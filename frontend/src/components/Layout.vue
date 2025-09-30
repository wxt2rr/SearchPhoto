<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { Home, Search, Folder, Settings, Clock, BookOpen, Menu } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { ref } from 'vue'

// 定义导航项
const navItems = [
  { name: '首页', path: '/', icon: Home },
  { name: '搜索', path: '/search', icon: Search },
  { name: '文件夹', path: '/folders', icon: Folder },
  { name: '时间轴', path: '/timeline', icon: Clock },
  { name: 'AI故事', path: '/stories', icon: BookOpen },
  { name: '设置', path: '/settings', icon: Settings }
]
</script>

<template>
  <div class="flex flex-col min-h-screen bg-white">
    <!-- 顶部导航栏 -->
    <header class="sticky top-0 z-10 border-b border-gray-200 bg-white">
      <div class="container flex h-16 items-center px-6">
        <!-- 左侧：产品名称 -->
        <div class="flex-shrink-0">
          <RouterLink to="/" class="flex items-center gap-3">
            <div class="bg-gray-100 w-8 h-8 rounded-lg flex items-center justify-center">
              <Search class="text-gray-600 w-5 h-5" />
            </div>
            <h1 class="text-xl font-bold text-gray-900">
              智能相册搜索
            </h1>
          </RouterLink>
        </div>
        
        <!-- 中间：导航菜单居中 -->
        <div class="flex-1 flex justify-center">
          <nav class="hidden md:flex items-center gap-2">
            <RouterLink 
              v-for="item in navItems" 
              :key="item.path"
              :to="item.path"
              class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors hover:bg-gray-100"
              :class="$route.path === item.path ? 'bg-gray-100 text-gray-900' : 'text-gray-600'"
            >
              <component :is="item.icon" class="w-4 h-4" />
              {{ item.name }}
            </RouterLink>
          </nav>
        </div>
        
        <!-- 右侧：移动端菜单 -->
        <div class="flex-shrink-0">
          <Button variant="ghost" size="icon" class="lg:hidden text-gray-600 hover:bg-gray-100">
            <Menu class="h-5 w-5" />
          </Button>
        </div>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="flex-1">
      <RouterView />
    </main>

    <!-- 移动端底部导航栏 -->
    <nav class="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200">
      <div class="flex justify-around">
        <RouterLink 
          v-for="item in navItems.slice(0, 4)"
          :key="item.path"
          :to="item.path"
          class="flex flex-col items-center justify-center gap-1 py-3 px-3 text-xs"
          :class="$route.path === item.path ? 'text-gray-900' : 'text-gray-500'"
        >
          <component :is="item.icon" class="w-5 h-5" />
          <span>{{ item.name }}</span>
        </RouterLink>
        
        <!-- 为设置页添加特殊处理 -->
        <RouterLink 
          :to="navItems[5].path"
          class="flex flex-col items-center justify-center gap-1 py-3 px-3 text-xs"
          :class="$route.path === navItems[5].path ? 'text-gray-900' : 'text-gray-500'"
        >
          <component :is="navItems[5].icon" class="w-5 h-5" />
          <span>{{ navItems[5].name }}</span>
        </RouterLink>
      </div>
    </nav>

    <!-- 为移动端底部导航留出空间 -->
    <div class="md:hidden h-16"></div>
  </div>
</template>