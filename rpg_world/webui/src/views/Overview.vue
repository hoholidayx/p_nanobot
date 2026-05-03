<template>
  <div class="overview">
    <a-card>
      <template #title>
        <DashboardOutlined /> 概览
      </template>
      <a-result
        status="info"
        title="全局状态观测"
        sub-title="此页面用于展示 RPG World 的整体运行状态，后续实现。"
      >
        <template #icon>
          <DashboardOutlined />
        </template>
      </a-result>
    </a-card>
  </div>
</template>

<script setup>
import { DashboardOutlined } from '@ant-design/icons-vue'
</script>

<style scoped>
.overview {
  max-width: 800px;
  margin: 0 auto;
}
</style>
