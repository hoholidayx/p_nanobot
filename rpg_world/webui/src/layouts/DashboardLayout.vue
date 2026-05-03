<template>
  <a-layout class="dashboard-layout">
    <!-- Mobile header -->
    <a-layout-header class="mobile-header">
      <a-button type="text" class="menu-trigger" @click="drawerVisible = true">
        <MenuOutlined />
      </a-button>
      <span class="header-title">RPG World</span>
      <div class="header-actions">
        <ThemeToggle />
      </div>
    </a-layout-header>

    <!-- Desktop sidebar -->
    <a-layout-sider
      v-if="!isMobile"
      v-model:collapsed="collapsed"
      :trigger="null"
      collapsible
      class="desktop-sider"
      :width="220"
      :collapsed-width="64"
      :theme="siderTheme"
    >
      <div class="logo">{{ collapsed ? 'RPG' : 'RPG World' }}</div>
      <a-menu
        v-model:selectedKeys="selectedKeys"
        mode="inline"
        :theme="siderTheme"
        @click="onMenuClick"
      >
        <a-menu-item key="/overview">
          <DashboardOutlined />
          <span>概览</span>
        </a-menu-item>
        <a-menu-item key="/characters">
          <UserOutlined />
          <span>角色卡管理</span>
        </a-menu-item>
        <a-menu-item key="/lorebook">
          <BookOutlined />
          <span>世界书管理</span>
        </a-menu-item>
      </a-menu>
      <div class="sider-footer">
        <ThemeToggle />
        <a-button
          type="text"
          size="small"
          class="collapse-btn"
          @click="collapsed = !collapsed"
        >
          <LeftOutlined v-if="!collapsed" />
          <RightOutlined v-else />
        </a-button>
      </div>
    </a-layout-sider>

    <!-- Mobile drawer -->
    <a-drawer
      v-else
      v-model:open="drawerVisible"
      placement="left"
      :width="260"
      :closable="false"
      :body-style="{ padding: 0 }"
    >
      <div class="drawer-header">
        <span class="drawer-title">RPG World</span>
      </div>
      <a-menu
        v-model:selectedKeys="selectedKeys"
        mode="inline"
        @click="onMenuClick"
      >
        <a-menu-item key="/overview">
          <DashboardOutlined />
          <span>概览</span>
        </a-menu-item>
        <a-menu-item key="/characters">
          <UserOutlined />
          <span>角色卡管理</span>
        </a-menu-item>
        <a-menu-item key="/lorebook">
          <BookOutlined />
          <span>世界书管理</span>
        </a-menu-item>
      </a-menu>
      <div style="padding: 16px; border-top: 1px solid #f0f0f0; margin-top: 16px;">
        <ThemeToggle />
      </div>
    </a-drawer>

    <!-- Content -->
    <a-layout>
      <a-layout-content class="content-area">
        <router-view />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  MenuOutlined,
  LeftOutlined,
  RightOutlined,
  DashboardOutlined,
  UserOutlined,
  BookOutlined,
} from '@ant-design/icons-vue'
import ThemeToggle from '@/components/ThemeToggle.vue'
import { useThemeStore } from '@/stores/theme'

const router = useRouter()
const route = useRoute()
const themeStore = useThemeStore()

const collapsed = ref(false)
const drawerVisible = ref(false)
const selectedKeys = ref([route.path])
const isMobile = ref(false)

function checkMobile() {
  isMobile.value = window.innerWidth < 768
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})
onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})

const siderTheme = computed(() =>
  themeStore.effective === 'dark' ? 'dark' : 'dark',
)

watch(
  () => route.path,
  (p) => {
    selectedKeys.value = [p]
  },
)

function onMenuClick({ key }) {
  router.push(key)
  drawerVisible.value = false
}
</script>

<style scoped>
.dashboard-layout {
  min-height: 100vh;
}

/* ---- Mobile header ---- */
.mobile-header {
  display: none;
  align-items: center;
  padding: 0 16px;
  background: var(--sider-bg);
  height: 48px;
  position: sticky;
  top: 0;
  z-index: 100;
}
.menu-trigger {
  color: #fff;
  font-size: 18px;
  margin-right: 12px;
}
.header-title {
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  flex: 1;
}
.header-actions {
  display: flex;
  align-items: center;
}

/* ---- Desktop sidebar ---- */
.desktop-sider {
  position: sticky;
  top: 0;
  height: 100vh;
  overflow: auto;
  left: 0;
}
.logo {
  height: 48px;
  line-height: 48px;
  text-align: center;
  color: #fff;
  font-weight: 700;
  font-size: 16px;
  white-space: nowrap;
  overflow: hidden;
}
.sider-footer {
  position: absolute;
  bottom: 12px;
  width: 100%;
  display: flex;
  justify-content: center;
  gap: 8px;
  align-items: center;
}
.collapse-btn {
  color: rgba(255, 255, 255, 0.65);
}

/* ---- Drawer ---- */
.drawer-header {
  height: 48px;
  line-height: 48px;
  padding: 0 24px;
  background: var(--sider-bg);
  color: #fff;
  font-weight: 700;
  font-size: 16px;
}

/* ---- Content ---- */
.content-area {
  margin: 16px;
  min-height: calc(100vh - 32px);
}

/* ---- Responsive ---- */
@media (max-width: 767px) {
  .mobile-header {
    display: flex;
  }
  .desktop-sider {
    display: none !important;
  }
  .content-area {
    margin: 8px;
    min-height: calc(100vh - 64px);
  }
}
</style>
