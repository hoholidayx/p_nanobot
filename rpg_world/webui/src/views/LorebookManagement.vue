<template>
  <div class="lorebook-mgmt">
    <!-- Header bar -->
    <div class="page-header">
      <h2>世界书管理</h2>
      <a-button type="primary" @click="openCreate">
        <template #icon><PlusOutlined /></template>
        新增条目
      </a-button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-container">
      <a-spin size="large" />
    </div>

    <!-- Table -->
    <a-table
      v-else
      :data-source="entries"
      :columns="columns"
      :pagination="{ pageSize: 20, showSizeChanger: true, showTotal: (t) => `共 ${t} 条` }"
      row-key="name"
      :scroll="{ x: 700 }"
    >
      <template #bodyCell="{ column, record }">
        <!-- Enable switch -->
        <template v-if="column.key === 'enable'">
          <a-switch
            :checked="!!record.enable"
            @change="(v) => toggleEnable(record, v)"
          />
        </template>

        <!-- Tags -->
        <template v-if="column.key === 'tags'">
          <a-tag
            v-for="tag in record.tags || []"
            :key="tag"
            color="blue"
          >
            {{ tag }}
          </a-tag>
          <span v-if="!record.tags?.length" class="no-tags">-</span>
        </template>

        <!-- Actions -->
        <template v-if="column.key === 'actions'">
          <a-space>
            <a-button type="link" size="small" @click="openEdit(record)">
              编辑
            </a-button>
            <a-popconfirm
              title="确定删除此条目？"
              @confirm="handleDelete(record)"
            >
              <a-button type="link" danger size="small">删除</a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </template>

      <template #emptyText>
        <a-empty description="暂无条目，点击「新增条目」创建" />
      </template>
    </a-table>

    <!-- Create / Edit Modal -->
    <a-modal
      v-model:open="modalVisible"
      :title="editing ? '编辑条目' : '新增条目'"
      :confirm-loading="saving"
      @ok="handleSave"
      @cancel="resetForm"
      :destroy-on-close="true"
      :width="560"
    >
      <a-form ref="formRef" :model="form" :rules="rules" layout="vertical">
        <a-form-item label="名称" name="name">
          <a-input
            v-model:value="form.name"
            placeholder="条目名称"
            :disabled="!!editing"
          />
        </a-form-item>

        <a-form-item label="启用状态" name="enable">
          <a-switch v-model:checked="form.enable" />
          <span class="form-hint">
            {{ form.enable ? '已启用（参与上下文渲染）' : '已禁用' }}
          </span>
        </a-form-item>

        <!-- Tags -->
        <a-form-item label="标签">
          <a-space wrap>
            <a-tag
              v-for="(tag, i) in form.tags"
              :key="i"
              closable
              @close="removeTag(i)"
            >
              {{ tag }}
            </a-tag>
            <a-input
              v-if="tagInputVisible"
              ref="tagInputRef"
              v-model:value="tagInput"
              type="text"
              size="small"
              style="width: 90px"
              @press-enter="addTag"
              @blur="addTag"
            />
            <a-button
              v-else
              size="small"
              type="dashed"
              @click="showTagInput"
            >
              <PlusOutlined /> 添加标签
            </a-button>
          </a-space>
        </a-form-item>

        <!-- Dynamic fields -->
        <a-form-item
          v-for="(val, key) in dynamicFields"
          :key="key"
          :label="key"
        >
          <a-input
            :value="val"
            @change="(e) => (dynamicFields[key] = e.target.value)"
            :placeholder="key"
          />
          <a-button
            type="link"
            danger
            size="small"
            class="field-remove"
            @click="removeField(key)"
          >
            移除
          </a-button>
        </a-form-item>

        <a-form-item>
          <a-button type="dashed" block @click="addField">
            <PlusOutlined /> 添加自定义字段
          </a-button>
        </a-form-item>

        <a-form-item label="内容" name="content">
          <a-textarea
            v-model:value="form.content"
            :rows="4"
            placeholder="条目内容"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { message } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import {
  listEntries,
  createEntry,
  updateEntry,
  deleteEntry,
} from '@/api/lorebook'

const columns = [
  { title: '名称', dataIndex: 'name', key: 'name', width: 180 },
  { title: '启用', key: 'enable', width: 80, align: 'center' },
  { title: '标签', key: 'tags', width: 200 },
  {
    title: '内容',
    dataIndex: 'content',
    key: 'content',
    ellipsis: true,
  },
  { title: '操作', key: 'actions', width: 140, fixed: 'right' },
]

const entries = ref([])
const loading = ref(true)
const modalVisible = ref(false)
const saving = ref(false)
const editing = ref(null)

// Form
const formRef = ref(null)
const form = reactive({
  name: '',
  enable: false,
  content: '',
  tags: [],
})
const dynamicFields = reactive({})

// Tag input
const tagInputVisible = ref(false)
const tagInput = ref('')
const tagInputRef = ref(null)

const rules = {
  name: [{ required: true, message: '请输入条目名称' }],
}

// --- Data ---
async function loadData() {
  loading.value = true
  try {
    entries.value = await listEntries()
  } catch (e) {
    message.error('加载世界书失败: ' + e.message)
  } finally {
    loading.value = false
  }
}

// --- CRUD ---
function openCreate() {
  editing.value = null
  form.name = ''
  form.enable = false
  form.content = ''
  form.tags = []
  Object.keys(dynamicFields).forEach((k) => delete dynamicFields[k])
  modalVisible.value = true
}

function openEdit(record) {
  editing.value = record.name
  form.name = record.name
  form.enable = !!record.enable
  form.content = record.content || ''
  form.tags = [...(record.tags || [])]

  const fixed = new Set(['name', 'enable', 'content', 'tags'])
  Object.keys(dynamicFields).forEach((k) => delete dynamicFields[k])
  for (const [k, v] of Object.entries(record)) {
    if (!fixed.has(k)) {
      dynamicFields[k] = String(v ?? '')
    }
  }
  modalVisible.value = true
}

async function handleSave() {
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  saving.value = true
  try {
    const payload = {
      name: form.name,
      enable: form.enable,
      content: form.content,
      tags: form.tags,
    }
    for (const [k, v] of Object.entries(dynamicFields)) {
      payload[k] = v
    }
    if (editing.value) {
      await updateEntry(editing.value, payload)
      message.success('已更新')
    } else {
      await createEntry(payload)
      message.success('已创建')
    }
    modalVisible.value = false
    await loadData()
  } catch (e) {
    message.error('操作失败: ' + e.message)
  } finally {
    saving.value = false
  }
}

async function handleDelete(record) {
  try {
    await deleteEntry(record.name)
    message.success('已删除')
    await loadData()
  } catch (e) {
    message.error('删除失败: ' + e.message)
  }
}

function resetForm() {
  editing.value = null
  form.name = ''
  form.enable = false
  form.content = ''
  form.tags = []
  Object.keys(dynamicFields).forEach((k) => delete dynamicFields[k])
}

// --- Toggle enable ---
async function toggleEnable(record, val) {
  try {
    const payload = { ...record, enable: val }
    await updateEntry(record.name, payload)
    record.enable = val
    message.success(val ? '已启用' : '已禁用')
  } catch (e) {
    message.error('操作失败: ' + e.message)
  }
}

// --- Tags ---
function showTagInput() {
  tagInputVisible.value = true
  nextTick(() => {
    tagInputRef.value?.focus()
  })
}

function addTag() {
  const t = tagInput.value.trim()
  if (t && !form.tags.includes(t)) {
    form.tags.push(t)
  }
  tagInput.value = ''
  tagInputVisible.value = false
}

function removeTag(i) {
  form.tags.splice(i, 1)
}

// --- Dynamic fields ---
function addField() {
  dynamicFields[`field_${Date.now()}`] = ''
}

function removeField(key) {
  delete dynamicFields[key]
}

onMounted(loadData)
</script>

<style scoped>
.lorebook-mgmt {
  background: var(--card-bg);
  border-radius: 8px;
  padding: 24px;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 8px;
}
.page-header h2 {
  margin: 0;
  font-size: 20px;
}
.loading-container {
  text-align: center;
  padding: 48px 0;
}
.form-hint {
  margin-left: 8px;
  color: var(--text-secondary, #999);
  font-size: 12px;
}
.field-remove {
  margin-left: 8px;
}
.no-tags {
  color: var(--text-tertiary, #bbb);
}
</style>
