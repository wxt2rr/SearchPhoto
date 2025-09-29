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
        <nav class="hidden md:flex items-center gap-1"> <!-- 缩小gap -->
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
        <Button variant="ghost" size="icon" class="lg:hidden">
          <Menu class="h-5 w-5" />
        </Button>
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
          v-for="item in navItems.slice(0, 4)"  <!-- 只显示前4个导航项 -->
          :key="item.path"
          :to="item.path"
          class="flex flex-col items-center justify-center gap-1 py-2 px-3 text-xs"
          :class="$route.path === item.path ? 'text-primary' : 'text-muted-foreground'"
        >
          <component :is="item.icon" class="w-5 h-5" />
          <span>{{ item.name }}</span>
        </RouterLink>
        
        <!-- 为设置页添加特殊处理 -->
        <RouterLink 
          :to="navItems[5].path"
          class="flex flex-col items-center justify-center gap-1 py-2 px-3 text-xs"
          :class="$route.path === navItems[5].path ? 'text-primary' : 'text-muted-foreground'"
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