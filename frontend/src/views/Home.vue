<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { RouterLink, useRouter } from 'vue-router'
import { useImageStore } from '@/stores/imageStore'
import { useSearchStore } from '@/stores/searchStore'
import { computed, ref, onMounted } from 'vue'

const router = useRouter()
const imageStore = useImageStore()
const searchStore = useSearchStore()
const searchQuery = ref('')

// 计算统计信息
const stats = computed(() => {
  const totalFolders = imageStore.processedFolders.length
  const totalImages = imageStore.processedFolders.reduce((sum, folder) => sum + folder.imageCount, 0)
  const recentSearches = searchStore.searchHistory.slice(0, 3)
  
  return {
    totalFolders,
    totalImages,
    recentSearches,
    hasData: totalFolders > 0 && totalImages > 0
  }
})

// 快速搜索
const handleQuickSearch = async (query: string) => {
  searchQuery.value = query
  await handleSearch()
}

const handleSearch = async () => {
  if (searchQuery.value.trim()) {
    await searchStore.textSearch(searchQuery.value)
    router.push('/search')
  }
}

// 智能搜索建议
const searchSuggestions = ref([
  { text: '海边日落', icon: '🌅', category: '风景' },
  { text: '家庭聚会', icon: '👨‍👩‍👧‍👦', category: '人物' },
  { text: '猫咪玩耍', icon: '🐱', category: '动物' },
  { text: '城市夜景', icon: '🌃', category: '建筑' },
  { text: '美食料理', icon: '🍽️', category: '生活' },
  { text: '旅行风光', icon: '✈️', category: '旅游' }
])

// 时间轴快捷入口
const timelineQuickAccess = ref([
  { label: '今天', value: 'today', count: 12 },
  { label: '本周', value: 'week', count: 89 },
  { label: '本月', value: 'month', count: 234 },
  { label: '今年', value: 'year', count: 1567 }
])

onMounted(() => {
  // 初始化数据
})
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
    <!-- Hero Section with Search -->
    <div class="relative overflow-hidden">
      <!-- Background Elements -->
      <div class="absolute inset-0 bg-grid-pattern opacity-5"></div>
      <div class="absolute top-20 left-10 w-72 h-72 bg-primary/10 rounded-full blur-3xl"></div>
      <div class="absolute bottom-20 right-10 w-96 h-96 bg-secondary/10 rounded-full blur-3xl"></div>
      
      <div class="relative max-w-7xl mx-auto px-4 py-16 md:py-24">
        <!-- Status Badge -->
        <div class="flex justify-center mb-8">
          <div class="inline-flex items-center rounded-full border border-primary/20 bg-primary/5 px-6 py-2 text-sm font-medium backdrop-blur-sm">
            <div class="flex items-center gap-2">
              <div class="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
              <span>本地AI驱动 · 隐私安全</span>
              <Badge v-if="stats.hasData" variant="secondary" class="ml-2">
                {{ stats.totalImages }} 张照片已索引
              </Badge>
            </div>
          </div>
        </div>

        <!-- Main Title -->
        <div class="text-center mb-12">
          <h1 class="text-5xl md:text-7xl font-bold tracking-tight mb-6">
            <span class="bg-clip-text text-transparent bg-gradient-to-r from-foreground via-primary to-secondary">
              智能相册搜索
            </span>
          </h1>
          <p class="text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
            用自然语言描述，瞬间找到你想要的照片
          </p>
        </div>

        <!-- Main Search Interface -->
        <div class="max-w-4xl mx-auto mb-16">
          <Card class="border-0 shadow-2xl bg-card/80 backdrop-blur-xl">
            <CardContent class="p-8">
              <!-- Search Input -->
              <div class="relative mb-6">
                <div class="absolute left-6 top-1/2 -translate-y-1/2 z-10">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <Input 
                  v-model="searchQuery" 
                  placeholder="描述你想找的照片：海边日落、家庭聚会、猫咪玩耍..."
                  class="pl-14 pr-32 py-6 text-lg border-0 bg-muted/50 focus:bg-background transition-colors"
                  @keyup.enter="handleSearch"
                />
                <Button 
                  @click="handleSearch" 
                  :disabled="!searchQuery.trim() || !stats.hasData"
                  class="absolute right-2 top-1/2 -translate-y-1/2 px-8 py-4 text-base"
                >
                  <span v-if="searchStore.isLoading" class="flex items-center">
                    <svg class="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    搜索中
                  </span>
                  <span v-else>搜索</span>
                </Button>
              </div>

              <!-- Quick Actions -->
              <div class="flex flex-wrap justify-center gap-3 mb-6">
                <Button 
                  v-for="suggestion in searchSuggestions.slice(0, 6)" 
                  :key="suggestion.text"
                  variant="outline" 
                  size="sm"
                  class="text-sm"
                  :disabled="!stats.hasData"
                  @click="handleQuickSearch(suggestion.text)"
                >
                  <span class="mr-2">{{ suggestion.icon }}</span>
                  {{ suggestion.text }}
                </Button>
              </div>

              <!-- Recent Searches -->
              <div v-if="stats.recentSearches.length > 0" class="text-center">
                <p class="text-sm text-muted-foreground mb-3">最近搜索:</p>
                <div class="flex flex-wrap justify-center gap-2">
                  <Badge 
                    v-for="search in stats.recentSearches" 
                    :key="search"
                    variant="secondary"
                    class="cursor-pointer hover:bg-primary hover:text-primary-foreground transition-colors"
                    @click="handleQuickSearch(search)"
                  >
                    {{ search }}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <!-- No Data State -->
        <div v-if="!stats.hasData" class="text-center mb-16">
          <div class="max-w-md mx-auto">
            <div class="bg-muted/50 rounded-full w-24 h-24 flex items-center justify-center mx-auto mb-6">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
              </svg>
            </div>
            <h3 class="text-2xl font-semibold mb-4">开始使用智能搜索</h3>
            <p class="text-muted-foreground mb-6">首先需要添加包含照片的文件夹</p>
            <RouterLink to="/folders">
              <Button size="lg" class="px-8">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                添加文件夹
              </Button>
            </RouterLink>
          </div>
        </div>
      </div>
    </div>

    <!-- Features Section -->
    <div v-if="stats.hasData" class="max-w-7xl mx-auto px-4 py-16">
      <!-- Timeline Quick Access -->
      <div class="mb-16">
        <Card class="border-0 bg-gradient-to-r from-primary/5 to-secondary/5 backdrop-blur-sm">
          <CardHeader class="text-center">
            <CardTitle class="text-2xl">时间轴浏览</CardTitle>
            <CardDescription>按时间快速浏览你的照片</CardDescription>
          </CardHeader>
          <CardContent>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div 
                v-for="period in timelineQuickAccess" 
                :key="period.value"
                class="text-center p-4 rounded-xl bg-background/50 hover:bg-background transition-colors cursor-pointer group"
              >
                <div class="text-3xl font-bold text-primary group-hover:scale-110 transition-transform">
                  {{ period.count }}
                </div>
                <div class="text-sm text-muted-foreground mt-1">{{ period.label }}</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Smart Categories -->
      <div class="mb-16">
        <Card class="border-0 bg-card/50 backdrop-blur-sm">
          <CardHeader class="text-center">
            <CardTitle class="text-2xl">智能分类</CardTitle>
            <CardDescription>AI自动识别的照片类别</CardDescription>
          </CardHeader>
          <CardContent>
            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              <div 
                v-for="suggestion in searchSuggestions" 
                :key="suggestion.text"
                class="text-center p-4 rounded-xl bg-muted/30 hover:bg-primary/10 transition-colors cursor-pointer group"
                @click="handleQuickSearch(suggestion.text)"
              >
                <div class="text-3xl mb-2 group-hover:scale-110 transition-transform">
                  {{ suggestion.icon }}
                </div>
                <div class="font-medium text-sm">{{ suggestion.text }}</div>
                <div class="text-xs text-muted-foreground mt-1">{{ suggestion.category }}</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Statistics -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
        <Card class="border-0 bg-gradient-to-br from-primary/10 to-primary/5 backdrop-blur-sm">
          <CardContent class="p-6 text-center">
            <div class="text-4xl font-bold text-primary mb-2">{{ stats.totalFolders }}</div>
            <div class="text-muted-foreground">已索引文件夹</div>
          </CardContent>
        </Card>
        <Card class="border-0 bg-gradient-to-br from-secondary/10 to-secondary/5 backdrop-blur-sm">
          <CardContent class="p-6 text-center">
            <div class="text-4xl font-bold text-secondary mb-2">{{ stats.totalImages }}</div>
            <div class="text-muted-foreground">可搜索照片</div>
          </CardContent>
        </Card>
        <Card class="border-0 bg-gradient-to-br from-green-500/10 to-green-500/5 backdrop-blur-sm">
          <CardContent class="p-6 text-center">
            <div class="text-4xl font-bold text-green-600 mb-2">{{ searchStore.searchHistory.length }}</div>
            <div class="text-muted-foreground">搜索历史</div>
          </CardContent>
        </Card>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="max-w-4xl mx-auto px-4 pb-16">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <RouterLink to="/search" class="group">
          <Card class="border-0 bg-card/50 backdrop-blur-sm group-hover:shadow-xl transition-all duration-300 group-hover:scale-[1.02]">
            <CardContent class="p-8 text-center">
              <div class="bg-primary/10 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4 group-hover:bg-primary/20 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <h3 class="text-xl font-semibold mb-2 group-hover:text-primary transition-colors">高级搜索</h3>
              <p class="text-muted-foreground">使用以图搜图和更多搜索选项</p>
            </CardContent>
          </Card>
        </RouterLink>
        
        <RouterLink to="/folders" class="group">
          <Card class="border-0 bg-card/50 backdrop-blur-sm group-hover:shadow-xl transition-all duration-300 group-hover:scale-[1.02]">
            <CardContent class="p-8 text-center">
              <div class="bg-secondary/10 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4 group-hover:bg-secondary/20 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-secondary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                </svg>
              </div>
              <h3 class="text-xl font-semibold mb-2 group-hover:text-secondary transition-colors">文件夹管理</h3>
              <p class="text-muted-foreground">添加和管理照片文件夹</p>
            </CardContent>
          </Card>
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
.bg-grid-pattern {
  background-image: 
    linear-gradient(rgba(0,0,0,0.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,0,0,0.1) 1px, transparent 1px);
  background-size: 20px 20px;
}

@media (max-width: 768px) {
  .grid {
    gap: 1rem;
  }
}
</style>