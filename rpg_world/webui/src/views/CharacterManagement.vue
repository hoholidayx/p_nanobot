<template>
  <div class="character-mgmt">
    <!-- Header bar -->
    <div class="page-header">
      <h2>角色卡管理</h2>
      <a-button type="primary" @click="openCreate">
        <template #icon><PlusOutlined /></template>
        新增角色
      </a-button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-container">
      <a-spin size="large" />
    </div>

    <!-- Table -->
    <a-table
      v-else
      :data-source="characters"
      :columns="columns"
      :pagination="false"
      row-key="name"
      :scroll="{ x: 600 }"
    >
      <!-- Enable switch -->
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'enable'">
          <a-switch
            :checked="!!record.enable"
            @change="(v) => toggleEnable(record, v)"
          />
        </template>

        <!-- Actions -->
        <template v-if="column.key === 'actions'">
          <a-space>
            <a-button type="link" size="small" @click="openEdit(record)">
              编辑
            </a-button>
            <a-popconfirm
              title="确定删除此角色卡？"
              @confirm="handleDelete(record)"
            >
              <a-button type="link" danger size="small">删除</a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </template>

      <!-- Empty state -->
      <template #emptyText>
        <a-empty description="暂无角色卡，点击「新增角色」创建" />
      </template>
    </a-table>

    <!-- Create / Edit Modal -->
    <a-modal
      v-model:open="modalVisible"
      :title="editing ? '编辑角色卡' : '新增角色卡'"
      :confirm-loading="saving"
      @ok="handleSave"
      @cancel="resetForm"
      :destroy-on-close="true"
      :width="560"
    >
      <a-form
        ref="formRef"
        :model="form"
        :rules="rules"
        layout="vertical"
      >
        <a-form-item label="名称" name="name">
          <a-input
            v-model:value="form.name"
            placeholder="角色名称"
            :disabled="!!editing"
          />
        </a-form-item>

        <a-form-item label="启用状态" name="enable">
          <a-switch v-model:checked="form.enable" />
          <span class="form-hint">
            {{ form.enable ? '已启用（参与上下文渲染）' : '已禁用' }}
          </span>
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
            placeholder="角色描述 / 背景故事"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import {
  listCharacters,
  createCharacter,
  updateCharacter,
  deleteCharacter,
} from '@/api/character'

const columns = [
  { title: '名称', dataIndex: 'name', key: 'name', width: 180 },
  {
    title: '启用',
    key: 'enable',
    width: 80,
    align: 'center',
  },
  {
    title: '内容',
    dataIndex: 'content',
    key: 'content',
    ellipsis: true,
  },
  { title: '操作', key: 'actions', width: 140, fixed: 'right' },
]

const characters = ref([])
const loading = ref(true)
const modalVisible = ref(false)
const saving = ref(false)
const editing = ref(null)

// Form state
const formRef = ref(null)
const form = reactive({
  name: '',
  enable: false,
  content: '',
})
const dynamicFields = reactive({})

const rules = {
  name: [{ required: true, message: '请输入角色名称' }],
}

// --- Data loading ---
async function loadData() {
  loading.value = true
  try {
    characters.value = await listCharacters()
  } catch (e) {
    message.error('加载角色列表失败: ' + e.message)
  } finally {
    loading.value = false
  }
}

// --- Create / Edit ---
function openCreate() {
  editing.value = null
  form.name = ''
  form.enable = false
  form.content = ''
  Object.keys(dynamicFields).forEach((k) => delete dynamicFields[k])
  modalVisible.value = true
}

function openEdit(record) {
  editing.value = record.name
  form.name = record.name
  form.enable = !!record.enable
  form.content = record.content || ''

  // Populate dynamic fields (everything except fixed fields)
  const fixed = new Set(['name', 'enable', 'content'])
  Object.keys(dynamicFields).forEach((k) => delete dynamicFields[k])
  for (const [k, v] of Object.entries(record)) {
    if (!fixed.has(k)) {
      dynamicFields[k] = String(v ?? '')
    }
  }

  modalVisible.value = true
}

function resetForm() {
  editing.value = null
  form.name = ''
  form.enable = false
  form.content = ''
  Object.keys(dynamicFields).forEach((k) => delete dynamicFields[k])
}

async function handleSave() {
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  saving.value = true
  try {
    // Merge fixed fields + dynamic fields
    const payload = {
      name: form.name,
      enable: form.enable,
      content: form.content,
    }
    for (const [k, v] of Object.entries(dynamicFields)) {
      payload[k] = v
    }

    if (editing.value) {
      await updateCharacter(editing.value, payload)
      message.success('已更新')
    } else {
      await createCharacter(payload)
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

// --- Delete ---
async function handleDelete(record) {
  try {
    await deleteCharacter(record.name)
    message.success('已删除')
    await loadData()
  } catch (e) {
    message.error('删除失败: ' + e.message)
  }
}

// --- Toggle enable ---
async function toggleEnable(record, val) {
  try {
    const payload = { ...record, enable: val }
    await updateCharacter(record.name, payload)
    record.enable = val
    message.success(val ? '已启用' : '已禁用')
  } catch (e) {
    message.error('操作失败: ' + e.message)
  }
}

// --- Dynamic fields ---
function addField() {
  const key = `field_${Date.now()}`
  dynamicFields[key] = ''
}

function removeField(key) {
  delete dynamicFields[key]
}

onMounted(loadData)
</script>

<style scoped>
.character-mgmt {
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
</style>
