<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { Home, Search, Folder, Settings } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'

// 定义导航项
const navItems = [
  { name: '首页', path: '/', icon: Home },
  { name: '搜索', path: '/search', icon: Search },
  { name: '文件夹', path: '/folders', icon: Folder },
  { name: '设置', path: '/settings', icon: Settings }
]
</script>

<template>
  <div class="flex flex-col min-h-screen bg-gradient-to-b from-background to-muted">
    <!-- 顶部导航栏 -->
    <header class="sticky top-0 z-10 border-b bg-background/80 backdrop-blur">
      <div class="container flex h-16 items-center justify-between px-4">
        <RouterLink to="/" class="flex items-center gap-2">
          <div class="bg-primary w-8 h-8 rounded-lg flex items-center justify-center">
            <Search class="text-primary-foreground w-5 h-5" />
          </div>
          <h1 class="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-primary/80">
            智能相册搜索
          </h1>
        </RouterLink>
        
        <!-- 桌面端导航 -->
        <nav class="hidden md:flex items-center gap-6">
          <RouterLink 
            v-for="item in navItems" 
            :key="item.path"
            :to="item.path"
            class="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors hover:bg-accent"
            :class="$route.path === item.path ? 'bg-accent text-accent-foreground' : 'text-muted-foreground'"
          >
            <component :is="item.icon" class="w-4 h-4" />
            {{ item.name }}
          </RouterLink>
        </nav>
        
        <!-- 移动端汉堡菜单 -->
        <div class="md:hidden">
          <Button variant="ghost" size="icon">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </Button>
        </div>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="flex-1 container mx-auto py-6 px-4">
      <RouterView />
    </main>

    <!-- 移动端底部导航栏 -->
    <nav class="md:hidden fixed bottom-0 left-0 right-0 bg-background border-t">
      <div class="flex justify-around">
        <RouterLink 
          v-for="item in navItems" 
          :key="item.path"
          :to="item.path"
          class="flex flex-col items-center justify-center gap-1 py-2 px-4 text-xs"
          :class="$route.path === item.path ? 'text-primary' : 'text-muted-foreground'"
        >
          <component :is="item.icon" class="w-5 h-5" />
          <span>{{ item.name }}</span>
        </RouterLink>
      </div>
    </nav>

    <!-- 为移动端底部导航留出空间 -->
    <div class="md:hidden h-16"></div>
  </div>
</template>