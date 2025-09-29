<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { useSearchStore } from '@/stores/searchStore'
import { useImageStore } from '@/stores/imageStore'

const searchStore = useSearchStore()
const imageStore = useImageStore()

// 搜索状态
const searchQuery = ref('')
const selectedImageForSearch = ref<File | null>(null)
const imagePreviewUrl = ref<string | null>(null)
const searchMode = ref<'text' | 'image' | 'combined'>('text')

// 高级搜索选项
const showAdvancedOptions = ref(false)
const dateRange = ref({ start: '', end: '' })
const locationFilter = ref('')
const sizeFilter = ref<'all' | 'small' | 'medium' | 'large'>('all')
const sortBy = ref<'relevance' | 'date' | 'size'>('relevance')

// 图像信息对话框
const showImageInfoDialog = ref(false)
const currentImageInfo = ref<any>(null)
const loadingImageInfo = ref(false)

// 搜索结果视图模式
const viewMode = ref<'grid' | 'list' | 'timeline'>('grid')
const gridSize = ref<'small' | 'medium' | 'large'>('medium')

// 智能搜索建议
const searchSuggestions = ref([
  { text: '海边日落', category: '风景', icon: '🌅' },
  { text: '家庭聚会', category: '人物', icon: '👨‍👩‍👧‍👦' },
  { text: '猫咪玩耍', category: '动物', icon: '🐱' },
  { text: '城市夜景', category: '建筑', icon: '🌃' },
  { text: '美食料理', category: '生活', icon: '🍽️' },
  { text: '旅行风光', category: '旅游', icon: '✈️' },
  { text: '生日派对', category: '庆祝', icon: '🎂' },
  { text: '雪景冬日', category: '季节', icon: '❄️' }
])

// 计算属性
const hasResults = computed(() => searchStore.searchResults.length > 0)
const isSearching = computed(() => searchStore.isLoading)
const displayHistory = computed(() => searchStore.searchHistory.slice(0, 8))

// 搜索结果分组（按相似度）
const groupedResults = computed(() => {
  if (!hasResults.value) return []
  
  const results = [...searchStore.searchResults]
  const groups = [
    { label: '高度匹配', min: 0.8, max: 1.0, results: [], color: 'text-green-600' },
    { label: '较好匹配', min: 0.6, max: 0.8, results: [], color: 'text-blue-600' },
    { label: '一般匹配', min: 0.4, max: 0.6, results: [], color: 'text-yellow-600' },
    { label: '低匹配度', min: 0.0, max: 0.4, results: [], color: 'text-gray-600' }
  ]
  
  results.forEach(result => {
    const group = groups.find(g => result.similarity >= g.min && result.similarity < g.max)
    if (group) group.results.push(result)
  })
  
  return groups.filter(g => g.results.length > 0)
})

// 方法
const handleSearch = async () => {
  if (searchQuery.value.trim()) {
    await searchStore.textSearch(searchQuery.value)
  }
}

const handleQuickSearch = (query: string) => {
  searchQuery.value = query
  handleSearch()
}

const handleImageUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (file) {
    selectedImageForSearch.value = file
    imagePreviewUrl.value = URL.createObjectURL(file)
    searchMode.value = 'image'
    
    try {
      await searchStore.imageSearch(file)
    } catch (error) {
      console.error('以图搜图失败:', error)
      alert('以图搜图失败: ' + (error as Error).message)
    }
  }
}

const handleDrop = async (event: DragEvent) => {
  event.preventDefault()
  
  if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
    const file = event.dataTransfer.files[0]
    
    if (file.type.startsWith('image/')) {
      selectedImageForSearch.value = file
      imagePreviewUrl.value = URL.createObjectURL(file)
      searchMode.value = 'image'
      
      try {
        await searchStore.imageSearch(file)
      } catch (error) {
        console.error('以图搜图失败:', error)
        alert('以图搜图失败: ' + (error as Error).message)
      }
    }
  }
}

const clearImageSearch = () => {
  selectedImageForSearch.value = null
  imagePreviewUrl.value = null
  searchMode.value = 'text'
  searchStore.clearResults()
}

const fetchImageInfo = async (imagePath: string) => {
  loadingImageInfo.value = true
  try {
    const response = await fetch('http://localhost:5001/api/image-info', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        imagePath: imagePath
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    currentImageInfo.value = data
  } catch (error) {
    console.error('获取图像信息失败:', error)
    currentImageInfo.value = null
  } finally {
    loadingImageInfo.value = false
  }
}

const showImageInfo = async (imagePath: string) => {
  await fetchImageInfo(imagePath)
  showImageInfoDialog.value = true
}

const getGridClass = () => {
  const sizeMap = {
    small: 'grid-cols-3 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8',
    medium: 'grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6',
    large: 'grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4'
  }
  return sizeMap[gridSize.value]
}

onMounted(() => {
  // 初始化
})
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
    <div class="max-w-7xl mx-auto px-4 py-8">
      <!-- 搜索头部 -->
      <div class="mb-8">
        <Card class="border-0 shadow-xl bg-card/80 backdrop-blur-xl">
          <CardContent class="p-6">
            <!-- 搜索模式切换 -->
            <div class="flex justify-center mb-6">
              <div class="inline-flex rounded-lg bg-muted p-1">
                <Button
                  :variant="searchMode === 'text' ? 'default' : 'ghost'"
                  size="sm"
                  @click="searchMode = 'text'"
                  class="rounded-md"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                  </svg>
                  文本搜索
                </Button>
                <Button
                  :variant="searchMode === 'image' ? 'default' : 'ghost'"
                  size="sm"
                  @click="searchMode = 'image'"
                  class="rounded-md"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  以图搜图
                </Button>
                <Button
                  :variant="searchMode === 'combined' ? 'default' : 'ghost'"
                  size="sm"
                  @click="searchMode = 'combined'"
                  class="rounded-md"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  智能搜索
                </Button>
              </div>
            </div>

            <!-- 文本搜索界面 -->
            <div v-if="searchMode === 'text' || searchMode === 'combined'" class="mb-6">
              <div class="relative">
                <div class="absolute left-4 top-1/2 -translate-y-1/2 z-10">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <Input 
                  v-model="searchQuery" 
                  placeholder="描述你想找的照片：海边日落、家庭聚会、猫咪玩耍..."
                  class="pl-12 pr-32 py-4 text-base border-0 bg-muted/50 focus:bg-background transition-colors"
                  @keyup.enter="handleSearch"
                />
                <Button 
                  @click="handleSearch" 
                  :disabled="!searchQuery.trim() || isSearching"
                  class="absolute right-2 top-1/2 -translate-y-1/2 px-6"
                >
                  <span v-if="isSearching" class="flex items-center">
                    <svg class="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    搜索中
                  </span>
                  <span v-else>搜索</span>
                </Button>
              </div>
            </div>

            <!-- 图片搜索界面 -->
            <div v-if="searchMode === 'image' || searchMode === 'combined'" class="mb-6">
              <div 
                class="border-2 border-dashed border-muted-foreground/30 rounded-xl p-6 text-center cursor-pointer hover:bg-accent/20 transition-colors"
                @dragover.prevent
                @drop="handleDrop"
              >
                <div v-if="!imagePreviewUrl" class="flex flex-col items-center justify-center gap-4">
                  <div class="bg-primary/10 p-4 rounded-full">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                    </svg>
                  </div>
                  <div>
                    <p class="font-medium">拖拽图片到这里或点击上传</p>
                    <p class="text-sm text-muted-foreground mt-1">支持 JPG、PNG、WebP 格式</p>
                  </div>
                  <Input 
                    type="file" 
                    accept="image/*"
                    @change="handleImageUpload"
                    class="hidden"
                    id="image-upload"
                  />
                  <label for="image-upload">
                    <Button variant="secondary">选择图片</Button>
                  </label>
                </div>
                
                <div v-else class="flex flex-col items-center">
                  <div class="relative mb-4">
                    <img 
                      :src="imagePreviewUrl" 
                      alt="上传图片预览" 
                      class="max-h-40 rounded-lg object-contain"
                    />
                    <Button 
                      variant="destructive" 
                      size="sm"
                      class="absolute -top-2 -right-2 rounded-full w-8 h-8 p-0"
                      @click="clearImageSearch"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </Button>
                  </div>
                  <p class="text-sm text-muted-foreground">正在搜索相似图片...</p>
                </div>
              </div>
            </div>

            <!-- 高级选项 -->
            <div class="flex justify-between items-center">
              <Button
                variant="ghost"
                size="sm"
                @click="showAdvancedOptions = !showAdvancedOptions"
                class="text-muted-foreground"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
                </svg>
                高级选项
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-2 transition-transform" :class="{ 'rotate-180': showAdvancedOptions }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </Button>

              <!-- 搜索历史 -->
              <div v-if="displayHistory.length > 0" class="flex flex-wrap gap-2">
                <Badge 
                  v-for="query in displayHistory.slice(0, 4)" 
                  :key="query"
                  variant="outline"
                  class="cursor-pointer hover:bg-primary hover:text-primary-foreground transition-colors"
                  @click="handleQuickSearch(query)"
                >
                  {{ query }}
                </Badge>
              </div>
            </div>

            <!-- 高级选项面板 -->
            <div v-if="showAdvancedOptions" class="mt-6 p-4 bg-muted/30 rounded-lg">
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                  <label class="text-sm font-medium mb-2 block">日期范围</label>
                  <div class="space-y-2">
                    <Input type="date" v-model="dateRange.start" placeholder="开始日期" />
                    <Input type="date" v-model="dateRange.end" placeholder="结束日期" />
                  </div>
                </div>
                <div>
                  <label class="text-sm font-medium mb-2 block">位置</label>
                  <Input v-model="locationFilter" placeholder="地理位置" />
                </div>
                <div>
                  <label class="text-sm font-medium mb-2 block">图片大小</label>
                  <select v-model="sizeFilter" class="w-full p-2 border rounded-md bg-background">
                    <option value="all">全部大小</option>
                    <option value="small">小图片</option>
                    <option value="medium">中等大小</option>
                    <option value="large">大图片</option>
                  </select>
                </div>
                <div>
                  <label class="text-sm font-medium mb-2 block">排序方式</label>
                  <select v-model="sortBy" class="w-full p-2 border rounded-md bg-background">
                    <option value="relevance">相关性</option>
                    <option value="date">日期</option>
                    <option value="size">文件大小</option>
                  </select>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- 智能搜索建议 -->
      <div v-if="!hasResults && !isSearching" class="mb-8">
        <Card class="border-0 bg-card/50 backdrop-blur-sm">
          <CardHeader class="text-center">
            <CardTitle>智能搜索建议</CardTitle>
            <CardDescription>点击下方标签快速搜索</CardDescription>
          </CardHeader>
          <CardContent>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
              <Button
                v-for="suggestion in searchSuggestions"
                :key="suggestion.text"
                variant="outline"
                class="h-auto p-4 flex flex-col items-center gap-2"
                @click="handleQuickSearch(suggestion.text)"
              >
                <span class="text-2xl">{{ suggestion.icon }}</span>
                <span class="text-sm font-medium">{{ suggestion.text }}</span>
                <Badge variant="secondary" class="text-xs">{{ suggestion.category }}</Badge>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- 搜索结果 -->
      <div v-if="hasResults">
        <!-- 结果头部 -->
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
          <div>
            <h2 class="text-2xl font-bold">搜索结果</h2>
            <p class="text-muted-foreground">找到 {{ searchStore.searchResults.length }} 张相关照片</p>
          </div>
          
          <!-- 视图控制 -->
          <div class="flex items-center gap-4">
            <!-- 网格大小控制 -->
            <div class="flex items-center gap-2">
              <Button
                v-for="size in ['small', 'medium', 'large']"
                :key="size"
                :variant="gridSize === size ? 'default' : 'outline'"
                size="sm"
                @click="gridSize = size"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path v-if="size === 'small'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                  <path v-else-if="size === 'medium'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h12a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM4 14a2 2 0 012-2h12a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2z" />
                  <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                </svg>
              </Button>
            </div>
          </div>
        </div>

        <!-- 按相似度分组的结果 -->
        <div class="space-y-8">
          <div v-for="group in groupedResults" :key="group.label" class="space-y-4">
            <div class="flex items-center gap-3">
              <h3 class="text-lg font-semibold" :class="group.color">{{ group.label }}</h3>
              <Badge variant="secondary">{{ group.results.length }} 张</Badge>
              <div class="flex-1 h-px bg-border"></div>
            </div>
            
            <div class="grid gap-4" :class="getGridClass()">
              <div 
                v-for="result in group.results" 
                :key="result.id" 
                class="group relative rounded-xl overflow-hidden border bg-card/50 backdrop-blur-sm transition-all hover:shadow-lg hover:scale-[1.02]"
              >
                <div class="aspect-square overflow-hidden">
                  <img 
                    :src="searchStore.getThumbnailUrl(result.path)" 
                    :alt="result.path"
                    class="w-full h-full object-cover transition-transform group-hover:scale-105 cursor-pointer"
                    @click="showImageInfo(result.path)"
                    @error="console.error('Failed to load image:', result.path)"
                  />
                </div>
                
                <!-- 图片信息覆盖层 -->
                <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                  <div class="absolute bottom-0 left-0 right-0 p-3 text-white">
                    <div class="text-sm font-medium truncate">{{ result.path.split('/').pop() }}</div>
                    <div class="flex justify-between items-center mt-1">
                      <Badge variant="secondary" class="text-xs">
                        {{ (result.similarity * 100).toFixed(1) }}% 匹配
                      </Badge>
                      <Button 
                        variant="secondary" 
                        size="sm"
                        @click.stop="showImageInfo(result.path)"
                        class="text-xs px-2 py-1 h-6"
                      >
                        详情
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 加载状态 -->
      <div v-else-if="isSearching" class="text-center py-16">
        <div class="flex flex-col items-center">
          <div class="relative mb-6">
            <div class="animate-spin rounded-full h-16 w-16 border-4 border-primary/20 border-t-primary"></div>
            <div class="absolute inset-0 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>
          <h3 class="text-xl font-medium mb-2">AI正在分析您的搜索</h3>
          <p class="text-muted-foreground">请稍候，正在匹配最相关的照片...</p>
          <Progress value={33} class="w-64 mt-4" />
        </div>
      </div>
    </div>

    <!-- 图像详情对话框 -->
    <Dialog v-model:open="showImageInfoDialog">
      <DialogContent class="max-w-5xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle class="flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            图像智能分析
          </DialogTitle>
        </DialogHeader>
        
        <div v-if="loadingImageInfo" class="flex justify-center py-12">
          <div class="flex flex-col items-center">
            <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary/20 border-t-primary mb-4"></div>
            <p class="text-muted-foreground">正在分析图像信息...</p>
          </div>
        </div>
        
        <div v-else-if="currentImageInfo && Object.keys(currentImageInfo).length > 0" class="space-y-6">
          <!-- 图像预览 -->
          <div class="text-center">
            <img 
              :src="searchStore.getThumbnailUrl(currentImageInfo.path)" 
              :alt="currentImageInfo.path"
              class="max-h-64 mx-auto rounded-lg shadow-lg"
            />
          </div>

          <!-- 基本信息 -->
          <Card>
            <CardHeader>
              <CardTitle class="text-lg">基本信息</CardTitle>
            </CardHeader>
            <CardContent>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div v-if="currentImageInfo.path">
                  <strong class="text-muted-foreground">文件路径:</strong>
                  <p class="font-mono text-xs mt-1 break-all">{{ currentImageInfo.path }}</p>
                </div>
                <div v-if="currentImageInfo.metadata?.width && currentImageInfo.metadata?.height">
                  <strong class="text-muted-foreground">图像尺寸:</strong>
                  <p class="mt-1">{{ currentImageInfo.metadata.width }} × {{ currentImageInfo.metadata.height }} 像素</p>
                </div>
                <div v-if="currentImageInfo.metadata?.format">
                  <strong class="text-muted-foreground">文件格式:</strong>
                  <p class="mt-1">{{ currentImageInfo.metadata.format }}</p>
                </div>
                <div v-if="currentImageInfo.metadata?.size_bytes">
                  <strong class="text-muted-foreground">文件大小:</strong>
                  <p class="mt-1">{{ (currentImageInfo.metadata.size_bytes / 1024).toFixed(1) }} KB</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- AI特征分析 -->
          <Card>
            <CardHeader>
              <CardTitle class="text-lg">AI特征分析</CardTitle>
            </CardHeader>
            <CardContent>
              <div class="space-y-4">
                <div v-if="currentImageInfo.feature_vector_info?.model" class="flex justify-between">
                  <span class="text-muted-foreground">AI模型:</span>
                  <Badge variant="outline">{{ currentImageInfo.feature_vector_info.model }}</Badge>
                </div>
                <div v-if="currentImageInfo.feature_vector_info?.dimension" class="flex justify-between">
                  <span class="text-muted-foreground">特征维度:</span>
                  <Badge variant="secondary">{{ currentImageInfo.feature_vector_info.dimension }}D</Badge>
                </div>
                <div v-if="currentImageInfo.feature_vector_info?.vector_norm" class="flex justify-between">
                  <span class="text-muted-foreground">向量强度:</span>
                  <span class="font-mono text-sm">{{ currentImageInfo.feature_vector_info.vector_norm.toFixed(6) }}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- AI识别内容 -->
          <Card>
            <CardHeader>
              <CardTitle class="text-lg">AI识别内容</CardTitle>
            </CardHeader>
            <CardContent>
              <div v-if="!currentImageInfo.possible_descriptions || currentImageInfo.possible_descriptions.length === 0" class="text-center py-8 text-muted-foreground">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-4 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 20.5a7.962 7.962 0 01-5.657-2.343m11.314 0C19.763 16.05 21 14.137 21 12s-1.237-4.05-3.343-6.157M12 3.5a8.001 8.001 0 00-8 8c0 2.137 1.237 4.05 3.343 6.157" />
                </svg>
                <p>未找到高置信度的内容描述</p>
              </div>
              <div v-else class="flex flex-wrap gap-2">
                <Badge 
                  v-for="desc in currentImageInfo.possible_descriptions" 
                  :key="desc.description"
                  :variant="desc.similarity > 0.7 ? 'default' : 'secondary'"
                  class="text-sm px-3 py-1"
                >
                  {{ desc.description }}
                  <span class="ml-2 text-xs opacity-75">{{ (desc.similarity * 100).toFixed(1) }}%</span>
                </Badge>
              </div>
            </CardContent>
          </Card>

          <!-- 技术说明 -->
          <Card class="bg-muted/30">
            <CardContent class="p-4">
              <div class="text-xs text-muted-foreground space-y-2">
                <p><strong>技术说明:</strong></p>
                <ul class="space-y-1 list-disc list-inside ml-4">
                  <li>使用CLIP模型提取图像的512维特征向量</li>
                  <li>通过余弦相似度计算图像间的相关性</li>
                  <li>AI识别基于预训练模型的语义理解能力</li>
                  <li>匹配度越高，表示图像内容越相关</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </div>
        
        <div v-else class="py-12 text-center text-muted-foreground">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto mb-4 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          <h3 class="text-lg font-medium mb-2">无法获取图像信息</h3>
          <p class="text-sm">可能的原因：图像文件不存在、格式不支持或服务暂时不可用</p>
        </div>
      </DialogContent>
    </Dialog>
  </div>
</template>