<template>
  <a-dropdown :trigger="['click']">
    <a-button type="text" size="small" class="theme-btn">
      <template #icon>
        <BulbOutlined v-if="themeStore.effective === 'light'" />
        <BulbFilled v-else />
      </template>
    </a-button>
    <template #overlay>
      <a-menu :selected-keys="[themeStore.mode]" @click="onSelect">
        <a-menu-item key="light">
          <BulbOutlined /> 亮色模式
        </a-menu-item>
        <a-menu-item key="dark">
          <BulbFilled /> 暗色模式
        </a-menu-item>
        <a-menu-item key="system">
          <DesktopOutlined /> 跟随系统
        </a-menu-item>
      </a-menu>
    </template>
  </a-dropdown>
</template>

<script setup>
import { BulbOutlined, BulbFilled, DesktopOutlined } from '@ant-design/icons-vue'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()

function onSelect({ key }) {
  themeStore.setMode(key)
}
</script>

<style scoped>
.theme-btn {
  color: inherit;
  font-size: 16px;
}
</style>
