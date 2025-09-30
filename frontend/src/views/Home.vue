<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { RouterLink, useRouter } from 'vue-router'
import { useImageStore } from '@/stores/imageStore'
import { useSearchStore } from '@/stores/searchStore'
import { computed, ref, onMounted } from 'vue'
import {
  Home as HomeIcon,
  Search as SearchIcon,
  Folder,
  Camera,
  MapPin,
  Users,
  Clock,
  BarChart3,
  Sparkles,
  Image as ImageIcon,
  Activity,
  Eye,
  Download,
  Share2,
  Settings,
  Calendar,
  Zap,
  Plus
} from 'lucide-vue-next'

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
  <div class="min-h-screen bg-white">
    <!-- Hero Section with Search -->
    <div class="relative">
      <div class="max-w-6xl mx-auto px-6 py-16 md:py-20">
        <!-- Status Badge -->
        <div class="flex justify-center mb-8">
          <div class="inline-flex items-center rounded-full bg-gray-100 px-4 py-2 text-sm text-gray-600">
            <div class="flex items-center gap-2">
              <div class="h-2 w-2 bg-green-500 rounded-full"></div>
              <span>本地AI驱动·隐私安全</span>
            </div>
          </div>
        </div>

        <!-- Main Title -->
        <div class="text-center mb-12">
          <h1 class="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            智能相册搜索
          </h1>
          <p class="text-lg md:text-xl text-gray-600 max-w-2xl mx-auto">
            用自然语言描述，瞬间找到你想要的照片
          </p>
        </div>

        <!-- Main Search Interface -->
        <div class="max-w-3xl mx-auto mb-16">
          <div class="bg-white border border-gray-200 rounded-lg p-8">
            <!-- Search Input -->
            <div class="relative mb-6">
              <div class="absolute left-4 top-1/2 -translate-y-1/2 z-10">
                <SearchIcon class="h-5 w-5 text-gray-400" />
              </div>
              <Input 
                v-model="searchQuery" 
                placeholder="描述你想找的照片：海边日落、家庭聚会、猫咪玩耍..."
                class="pl-12 pr-24 py-4 text-base border-gray-200 focus:border-gray-400 focus:ring-0"
                @keyup.enter="handleSearch"
              />
              <Button 
                @click="handleSearch" 
                :disabled="!searchQuery.trim() || !stats.hasData"
                class="absolute right-2 top-1/2 -translate-y-1/2 px-6 py-2 bg-gray-100 text-gray-700 hover:bg-gray-200 border-0"
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
            <div class="flex flex-wrap justify-center gap-2">
              <Button 
                v-for="suggestion in searchSuggestions.slice(0, 6)" 
                :key="suggestion.text"
                variant="outline" 
                size="sm"
                class="text-sm bg-gray-50 text-gray-700 hover:bg-gray-100 border-gray-200"
                :disabled="!stats.hasData"
                @click="handleQuickSearch(suggestion.text)"
              >
                <span class="mr-1">{{ suggestion.icon }}</span>
                {{ suggestion.text }}
              </Button>
            </div>
          </div>
        </div>

        <!-- No Data State -->
        <div v-if="!stats.hasData" class="text-center mb-16">
          <div class="max-w-md mx-auto">
            <div class="bg-muted/50 rounded-full w-24 h-24 flex items-center justify-center mx-auto mb-6">
              <Folder class="h-12 w-12 text-muted-foreground" />
            </div>
            <h3 class="text-2xl font-semibold mb-4">开始使用智能搜索</h3>
            <p class="text-muted-foreground mb-6">首先需要添加包含照片的文件夹</p>
            <RouterLink to="/folders">
              <Button size="lg" class="px-8">
                <Plus class="h-5 w-5 mr-2" />
                添加文件夹
              </Button>
            </RouterLink>
          </div>
        </div>
      </div>
    </div>

    <!-- Features Section -->
    <div v-if="stats.hasData" class="max-w-6xl mx-auto px-6 py-16">
      <!-- Statistics -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
        <div class="bg-white border border-gray-200 rounded-lg p-8 text-center">
          <div class="text-3xl font-bold text-gray-900 mb-2">{{ stats.totalFolders }}</div>
          <div class="text-gray-600">已索引文件夹</div>
        </div>
        <div class="bg-white border border-gray-200 rounded-lg p-8 text-center">
          <div class="text-3xl font-bold text-gray-900 mb-2">{{ stats.totalImages }}</div>
          <div class="text-gray-600">可搜索照片</div>
        </div>
        <div class="bg-white border border-gray-200 rounded-lg p-8 text-center">
          <div class="text-3xl font-bold text-gray-900 mb-2">{{ searchStore.searchHistory.length }}</div>
          <div class="text-gray-600">搜索历史</div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="max-w-4xl mx-auto px-6 pb-16">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <RouterLink to="/search" class="group">
          <div class="bg-white border border-gray-200 rounded-lg p-8 text-center hover:shadow-lg transition-all duration-300">
            <div class="bg-gray-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4 group-hover:bg-gray-200 transition-colors">
              <SearchIcon class="h-8 w-8 text-gray-600" />
            </div>
            <h3 class="text-xl font-semibold mb-2 text-gray-900">高级搜索</h3>
            <p class="text-gray-600">使用以图搜图和更多搜索选项</p>
          </div>
        </RouterLink>
        
        <RouterLink to="/folders" class="group">
          <div class="bg-white border border-gray-200 rounded-lg p-8 text-center hover:shadow-lg transition-all duration-300">
            <div class="bg-gray-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4 group-hover:bg-gray-200 transition-colors">
              <Folder class="h-8 w-8 text-gray-600" />
            </div>
            <h3 class="text-xl font-semibold mb-2 text-gray-900">文件夹管理</h3>
            <p class="text-gray-600">添加和管理照片文件夹</p>
          </div>
        </RouterLink>
      </div>
    </div>
  </div>
</template>
