# Agent Hook 系统

Agent Hook 是 nanobot 的**生命周期钩子**机制，允许在不修改核心循环代码的前提下观察、拦截和定制 agent 的每次迭代行为。

## 核心概念

### 生命周期

一次 agent run = 多次 LLM **迭代**。每次迭代中：

```
before_iteration
       │
       ▼
  LLM call ──── on_stream (逐 token)
       │
       ▼
before_execute_tools
       │
       ▼
  tool execution
       │
       ▼
 after_iteration ──→ 继续下一轮迭代 or 结束
       │
       ▼
 finalize_content (最终输出后处理)
```

### AgentHookContext

```python
@dataclass
class AgentHookContext:
    iteration: int                     # 当前迭代轮次 (0-based)
    messages: list[dict]               # 当前完整消息列表
    response: LLMResponse | None       # LLM 原始响应
    usage: dict[str, int]              # token 用量
    tool_calls: list[ToolCallRequest]  # 本轮工具调用请求
    tool_results: list[Any]            # 工具执行结果
    tool_events: list[dict]            # 工具事件（用于进度展示）
    streamed_content: bool             # 是否已通过流式输出内容
    final_content: str | None          # 最终输出内容
    stop_reason: str | None            # 停止原因
    error: str | None                  # 错误信息
```

context 是**可变**的 —— hook 可以修改 `messages`、`tool_calls`、`tool_results` 等字段来影响后续行为。

## Hook 基类

`AgentHook` 定义在 `nanobot/agent/hook.py`，所有方法都是空的（no-op），子类只需按需覆盖：

```python
from nanobot.agent import AgentHook, AgentHookContext

class MyHook(AgentHook):
    ...
```

### 方法总览

| 方法 | 触发时机 | 同步/异步 | 修改 context 影响后续 |
|------|---------|-----------|---------------------|
| `wants_streaming()` | 初始化时 | 同步 | 决定是否启用流式模式 |
| `before_iteration(ctx)` | 每次 LLM 调用之前 | 异步 | 可修改 `messages` |
| `on_stream(ctx, delta)` | 流式模式下每收到 token 增量 | 异步 | 只读观察 |
| `on_stream_end(ctx, *, resuming)` | 流式结束 | 异步 | 只读观察 |
| `before_execute_tools(ctx)` | 执行工具之前 | 异步 | 可拦截/修改 `tool_calls` |
| `after_iteration(ctx)` | 每次迭代结束 | 异步 | 可记录状态 |
| `finalize_content(ctx, content)` | 返回最终内容前 | 同步 | 返回的内容将替代原内容 |

### 方法说明

#### `wants_streaming() -> bool`
返回 `True` 表示需要逐 token 流式输出。如果需要接收 `on_stream` 回调，必须返回 `True`。

#### `async before_iteration(context: AgentHookContext)`
LLM 调用前触发。可以在此：

- 注入/修改系统消息
- 记录迭代开始时间
- 修改上下文窗口

#### `async on_stream(context: AgentHookContext, delta: str)`
流式模式下每个 token 增量到达时触发。`delta` 是当前增量文本。

注意：此方法仅在 `wants_streaming()` 返回 `True` 时才会被调用。

`resuming=True` 表示流结束后仍有后续（如工具调用即将发生），`resuming=False` 表示这是最终回复。

#### `async before_execute_tools(context: AgentHookContext)`
LLM 返回工具调用请求后、实际执行工具前触发。可以在此：

- 日志记录所有工具调用
- 过滤/修改工具参数
- 发送工具进度通知

通过 `context.tool_calls` 读取工具列表：

```python
for tc in context.tool_calls:
    print(f"{tc.name}({tc.arguments})")
```

#### `async after_iteration(context: AgentHookContext)`
每次迭代（LLM 调用 + 工具执行）完成后触发。可以在此：
- 累加 token 用量
- 记录迭代耗时
- 检查是否需要提前停止

#### `finalize_content(context: AgentHookContext, content: str | None) -> str | None`
最终内容返回前调用。这是一个**同步管道**——所有 hook 的 `finalize_content` 会链式执行，前一个的输出作为后一个的输入。适合做内容后处理：

- 剔除 think 标签
- 内容审查/过滤
- 格式转换

## CompositeHook（组合钩子）

多个 hook 时自动包装为 `CompositeHook`。特性：

- **异步方法**：fan-out 并发执行各 hook，异常隔离（默认 catch 异常不中断循环）
- **`reraise=True`**：抛出异常不 catch，用于核心 hook
- **`finalize_content`**：管道模式（不隔离异常），结果依次传递

框架内部通过 `_LoopHook` + 用户自定义 hooks 组装：

```python
hook = CompositeHook([loop_hook] + user_hooks)
```

## 内置实现

### _LoopHook (`nanobot/agent/loop.py:67`)
框架核心 hook，必须执行。功能：
- 记录迭代状态到 `_current_iteration`
- 处理 `on_stream` / `on_stream_end` 回调
- `before_execute_tools`：发送工具进度、日志记录工具调用、设置工具上下文
- `after_iteration`：发送工具完成事件、记录 token 用量
- `finalize_content`：剔除 think 标签

### _SubagentHook (`nanobot/agent/subagent.py:44`)
子 agent 的 hook，功能：
- `before_execute_tools`：日志记录子 agent 的工具调用
- `after_iteration`：更新子 agent 状态（iteration、tool_events、usage、error）

## 完整示例

```python
from nanobot import Nanobot
from nanobot.agent import AgentHook, AgentHookContext


# 1. 审计 Hook：记录所有工具调用
class AuditHook(AgentHook):
    def __init__(self):
        super().__init__()
        self.calls: list[tuple[str, dict]] = []

    async def before_execute_tools(self, context: AgentHookContext) -> None:
        for tc in context.tool_calls:
            self.calls.append((tc.name, tc.arguments))


# 2. 流式 Hook：逐 token 输出
class StreamingHook(AgentHook):
    def wants_streaming(self) -> bool:
        return True

    async def on_stream(self, context: AgentHookContext, delta: str) -> None:
        print(delta, end="", flush=True)

    async def on_stream_end(self, context: AgentHookContext, *, resuming: bool) -> None:
        print()


# 3. 内容过滤 Hook：禁止敏感词
class CensorHook(AgentHook):
    BLOCKED = ["secret", "password"]

    def finalize_content(self, context: AgentHookContext, content: str | None) -> str | None:
        if content is None:
            return None
        for word in self.BLOCKED:
            content = content.replace(word, "***")
        return content


# 4. 性能统计 Hook
class TimingHook(AgentHook):
    def __init__(self):
        super().__init__()
        self._start: float | None = None
        self.iterations: list[float] = []

    async def before_iteration(self, context: AgentHookContext) -> None:
        self._start = time.monotonic()

    async def after_iteration(self, context: AgentHookContext) -> None:
        if self._start is not None:
            self.iterations.append(time.monotonic() - self._start)


# 使用
bot = Nanobot(...)
result = await bot.run("Hello", hooks=[AuditHook(), CensorHook()])
```

## 使用方式

### Python SDK

```python
result = await bot.run("Hello", hooks=[MyHook()])
```

### AgentLoop 直接调用

```python
hook = CompositeHook([_LoopHook(...), MyHook()])
await runner.run(AgentRunSpec(hook=hook, ...))
```

## 注意事项

1. **异常隔离**：自定义 hook 抛异常默认不会导致 agent 崩溃（catch 后只记日志）。核心 hook（`_LoopHook`）设置 `reraise=True` 例外。
2. **同步/异步区分**：`finalize_content` 是同步方法（性能敏感），其余生命周期方法均为异步。
3. **流式模式**：`on_stream` 仅在 `wants_streaming()` 返回 `True` 时启用。流式和非流式模式对 hook 体系透明。
4. **context 可变**：修改 `context.messages` 或 `context.tool_calls` 等字段会直接影响后续行为，使用需谨慎。
