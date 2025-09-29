<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { Home, Search, Folder, Settings, Clock, MapPin, Users, BookOpen, ChevronDown } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { ref } from 'vue'

// 定义基础导航项
const navItems = [
  { name: '首页', path: '/', icon: Home },
  { name: '搜索', path: '/search', icon: Search },
  { name: '文件夹', path: '/folders', icon: Folder }
]

// 定义高级功能导航项
const advancedItems = [
  { name: '时间轴', path: '/timeline', icon: Clock },
  { name: '地理位置', path: '/location', icon: MapPin },
  { name: '人物识别', path: '/people', icon: Users },
  { name: 'AI故事', path: '/stories', icon: BookOpen }
]

const showAdvancedMenu = ref(false)
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
          
          <!-- 高级功能下拉菜单 -->
          <div class="relative" @mouseenter="showAdvancedMenu = true" @mouseleave="showAdvancedMenu = false">
            <button 
              class="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors hover:bg-accent"
              :class="advancedItems.some(item => $route.path === item.path) ? 'bg-accent text-accent-foreground' : 'text-muted-foreground'"
            >
              <Settings class="w-4 h-4" />
              高级功能
              <ChevronDown class="w-3 h-3 transition-transform" :class="{ 'rotate-180': showAdvancedMenu }" />
            </button>
            
            <div 
              v-show="showAdvancedMenu"
              class="absolute top-full left-0 mt-2 w-48 bg-background border border-border rounded-lg shadow-lg z-50"
            >
              <div class="py-2">
                <RouterLink 
                  v-for="item in advancedItems"
                  :key="item.path"
                  :to="item.path"
                  class="flex items-center gap-3 px-4 py-2 text-sm transition-colors hover:bg-accent"
                  :class="$route.path === item.path ? 'bg-accent text-accent-foreground' : 'text-muted-foreground'"
                >
                  <component :is="item.icon" class="w-4 h-4" />
                  {{ item.name }}
                </RouterLink>
              </div>
            </div>
          </div>
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
        
        <!-- 移动端高级功能入口 -->
        <RouterLink 
          to="/timeline"
          class="flex flex-col items-center justify-center gap-1 py-2 px-4 text-xs"
          :class="advancedItems.some(item => $route.path === item.path) ? 'text-primary' : 'text-muted-foreground'"
        >
          <Settings class="w-5 h-5" />
          <span>更多</span>
        </RouterLink>
      </div>
    </nav>

    <!-- 为移动端底部导航留出空间 -->
    <div class="md:hidden h-16"></div>
  </div>
</template>