<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { getPhotosByLocation, getThumbnail } from '@/api'

// 地理位置数据
const locationData = ref<any[]>([])
const isLoading = ref(false)

// 原来的模拟数据，现在作为备用
const mockLocationData = ref([
  {
    id: 1,
    name: '西湖公园',
    coordinates: { lat: 30.2741, lng: 120.1551 },
    address: '浙江省杭州市西湖区',
    imageCount: 45,
    lastVisit: '2024-03-15',
    category: '公园',
    images: [
      { id: 1, path: '/api/image1.jpg', thumbnail: '/api/thumb1.jpg' },
      { id: 2, path: '/api/image2.jpg', thumbnail: '/api/thumb2.jpg' },
      { id: 3, path: '/api/image3.jpg', thumbnail: '/api/thumb3.jpg' },
    ]
  },
  {
    id: 2,
    name: '家',
    coordinates: { lat: 30.2853, lng: 120.1564 },
    address: '浙江省杭州市上城区',
    imageCount: 128,
    lastVisit: '2024-03-20',
    category: '住宅',
    images: [
      { id: 4, path: '/api/image4.jpg', thumbnail: '/api/thumb4.jpg' },
      { id: 5, path: '/api/image5.jpg', thumbnail: '/api/thumb5.jpg' },
    ]
  },
  {
    id: 3,
    name: '咖啡厅',
    coordinates: { lat: 30.2792, lng: 120.1633 },
    address: '浙江省杭州市西湖区文三路',
    imageCount: 23,
    lastVisit: '2024-03-12',
    category: '餐饮',
    images: [
      { id: 6, path: '/api/image6.jpg', thumbnail: '/api/thumb6.jpg' },
    ]
  },
  {
    id: 4,
    name: '办公室',
    coordinates: { lat: 30.2728, lng: 120.1614 },
    address: '浙江省杭州市西湖区学院路',
    imageCount: 67,
    lastVisit: '2024-03-18',
    category: '工作',
    images: [
      { id: 7, path: '/api/image7.jpg', thumbnail: '/api/thumb7.jpg' },
      { id: 8, path: '/api/image8.jpg', thumbnail: '/api/thumb8.jpg' },
      { id: 9, path: '/api/image9.jpg', thumbnail: '/api/thumb9.jpg' },
    ]
  }
])

// 搜索和筛选
const searchQuery = ref('')
const selectedCategory = ref<string>('all')
const viewMode = ref<'list' | 'map' | 'heatmap'>('list')

// 分类选项
const categories = ref([
  { key: 'all', label: '全部', icon: '🌍', count: 0 },
  { key: '公园', label: '公园', icon: '🌳', count: 0 },
  { key: '住宅', label: '住宅', icon: '🏠', count: 0 },
  { key: '餐饮', label: '餐饮', icon: '☕', count: 0 },
  { key: '工作', label: '工作', icon: '💼', count: 0 },
  { key: '商场', label: '商场', icon: '🛍️', count: 0 },
  { key: '景点', label: '景点', icon: '🏛️', count: 0 }
])

// 计算属性
const filteredLocations = computed(() => {
  let filtered = locationData.value

  // 按搜索关键词筛选
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(location => 
      location.name.toLowerCase().includes(query) ||
      location.address.toLowerCase().includes(query) ||
      location.category.toLowerCase().includes(query)
    )
  }

  // 按分类筛选
  if (selectedCategory.value !== 'all') {
    filtered = filtered.filter(location => location.category === selectedCategory.value)
  }

  return filtered.sort((a, b) => b.imageCount - a.imageCount)
})

const totalImages = computed(() => {
  return filteredLocations.value.reduce((sum, location) => sum + location.imageCount, 0)
})

const topLocations = computed(() => {
  return [...locationData.value]
    .sort((a, b) => b.imageCount - a.imageCount)
    .slice(0, 5)
})

// 方法
const getCategoryIcon = (category: string) => {
  const iconMap: { [key: string]: string } = {
    '公园': '🌳',
    '住宅': '🏠',
    '餐饮': '☕',
    '工作': '💼',
    '商场': '🛍️',
    '景点': '🏛️'
  }
  return iconMap[category] || '📍'
}

const formatDistance = (coordinates: { lat: number, lng: number }) => {
  // 这里应该计算与当前位置的距离
  // 暂时返回模拟数据
  const distances = ['0.5km', '1.2km', '2.8km', '5.1km', '12.3km']
  return distances[Math.floor(Math.random() * distances.length)]
}

const formatLastVisit = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now.getTime() - date.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 1) return '昨天'
  if (diffDays < 7) return `${diffDays}天前`
  if (diffDays < 30) return `${Math.ceil(diffDays / 7)}周前`
  return date.toLocaleDateString('zh-CN')
}

// 更新分类计数
const updateCategoryCounts = () => {
  categories.value.forEach(category => {
    if (category.key === 'all') {
      category.count = locationData.value.length
    } else {
      category.count = locationData.value.filter(loc => loc.category === category.key).length
    }
  })
}

// 加载地理位置数据
const loadLocationData = async () => {
  try {
    isLoading.value = true
    const response = await getPhotosByLocation()
    locationData.value = response.map((item: any) => ({
      ...item,
      images: item.images.map((image: any) => ({
        ...image,
        thumbnail: getThumbnail(image.path)
      }))
    }))
    updateCategoryCounts()
  } catch (error) {
    console.error('加载地理位置数据失败:', error)
    // 如果API失败，使用模拟数据
    locationData.value = mockLocationData.value
    updateCategoryCounts()
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadLocationData()
})
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 py-8">
    <!-- 头部 -->
    <div class="mb-8">
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold mb-4">
          <span class="bg-clip-text text-transparent bg-gradient-to-r from-foreground via-primary to-secondary">
            地理位置浏览
          </span>
        </h1>
        <p class="text-xl text-muted-foreground">探索你的照片足迹，重温美好回忆</p>
      </div>

      <!-- 统计概览 -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card class="border-0 bg-gradient-to-br from-primary/10 to-primary/5 backdrop-blur-sm">
          <CardContent class="p-6 text-center">
            <div class="text-3xl font-bold text-primary mb-2">{{ locationData.length }}</div>
            <div class="text-muted-foreground">拍摄地点</div>
          </CardContent>
        </Card>
        <Card class="border-0 bg-gradient-to-br from-secondary/10 to-secondary/5 backdrop-blur-sm">
          <CardContent class="p-6 text-center">
            <div class="text-3xl font-bold text-secondary mb-2">{{ totalImages }}</div>
            <div class="text-muted-foreground">地理标记照片</div>
          </CardContent>
        </Card>
        <Card class="border-0 bg-gradient-to-br from-green-500/10 to-green-500/5 backdrop-blur-sm">
          <CardContent class="p-6 text-center">
            <div class="text-3xl font-bold text-green-600 mb-2">{{ categories.length - 1 }}</div>
            <div class="text-muted-foreground">地点类别</div>
          </CardContent>
        </Card>
        <Card class="border-0 bg-gradient-to-br from-purple-500/10 to-purple-500/5 backdrop-blur-sm">
          <CardContent class="p-6 text-center">
            <div class="text-3xl font-bold text-purple-600 mb-2">15.6</div>
            <div class="text-muted-foreground">平均距离(km)</div>
          </CardContent>
        </Card>
      </div>

      <!-- 搜索和筛选 -->
      <Card class="border-0 bg-card/50 backdrop-blur-sm mb-8">
        <CardContent class="p-6">
          <div class="flex flex-col lg:flex-row gap-6">
            <!-- 搜索框 -->
            <div class="flex-1">
              <div class="relative">
                <div class="absolute left-3 top-1/2 -translate-y-1/2">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <Input 
                  v-model="searchQuery" 
                  placeholder="搜索地点名称或地址..."
                  class="pl-10"
                />
              </div>
            </div>

            <!-- 视图模式切换 -->
            <div class="flex items-center gap-2">
              <div class="inline-flex rounded-lg bg-muted p-1">
                <Button
                  :variant="viewMode === 'list' ? 'default' : 'ghost'"
                  size="sm"
                  @click="viewMode = 'list'"
                  class="rounded-md"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                  </svg>
                  列表
                </Button>
                <Button
                  :variant="viewMode === 'map' ? 'default' : 'ghost'"
                  size="sm"
                  @click="viewMode = 'map'"
                  class="rounded-md"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                  </svg>
                  地图
                </Button>
                <Button
                  :variant="viewMode === 'heatmap' ? 'default' : 'ghost'"
                  size="sm"
                  @click="viewMode = 'heatmap'"
                  class="rounded-md"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  热力图
                </Button>
              </div>
            </div>
          </div>

          <!-- 分类筛选 -->
          <div class="flex flex-wrap gap-2 mt-6">
            <Button
              v-for="category in categories"
              :key="category.key"
              :variant="selectedCategory === category.key ? 'default' : 'outline'"
              size="sm"
              @click="selectedCategory = category.key"
              class="flex items-center gap-2"
            >
              <span>{{ category.icon }}</span>
              <span>{{ category.label }}</span>
              <Badge variant="secondary" class="ml-1">{{ category.count }}</Badge>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- 列表视图 -->
    <div v-if="viewMode === 'list'">
      <!-- 热门地点 -->
      <div class="mb-8">
        <h2 class="text-2xl font-bold mb-6 flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          热门拍摄地点
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card 
            v-for="location in topLocations.slice(0, 3)" 
            :key="location.id"
            class="border-0 bg-gradient-to-br from-card/80 to-card/40 backdrop-blur-sm hover:shadow-xl transition-all duration-300 group cursor-pointer"
          >
            <CardContent class="p-6">
              <div class="flex items-start justify-between mb-4">
                <div class="flex items-center gap-3">
                  <div class="text-2xl">{{ getCategoryIcon(location.category) }}</div>
                  <div>
                    <h3 class="font-semibold text-lg group-hover:text-primary transition-colors">{{ location.name }}</h3>
                    <p class="text-sm text-muted-foreground">{{ location.address }}</p>
                  </div>
                </div>
                <Badge variant="outline">{{ location.category }}</Badge>
              </div>
              
              <!-- 照片预览 -->
              <div class="grid grid-cols-3 gap-2 mb-4">
                <div 
                  v-for="image in location.images.slice(0, 3)" 
                  :key="image.id"
                  class="aspect-square rounded-lg overflow-hidden bg-gradient-to-br from-primary/20 to-secondary/20 group-hover:scale-105 transition-transform"
                >
                  <div class="w-full h-full flex items-center justify-center">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                </div>
              </div>
              
              <div class="flex justify-between items-center text-sm text-muted-foreground">
                <span class="flex items-center gap-1">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  {{ location.imageCount }} 张照片
                </span>
                <span>{{ formatLastVisit(location.lastVisit) }}</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <!-- 所有地点 -->
      <div>
        <h2 class="text-2xl font-bold mb-6">所有地点 ({{ filteredLocations.length }})</h2>
        <div class="space-y-4">
          <Card 
            v-for="location in filteredLocations" 
            :key="location.id"
            class="border-0 bg-card/50 backdrop-blur-sm hover:shadow-lg transition-all duration-300 group cursor-pointer"
          >
            <CardContent class="p-6">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-4 flex-1">
                  <div class="text-3xl">{{ getCategoryIcon(location.category) }}</div>
                  <div class="flex-1">
                    <div class="flex items-center gap-3 mb-2">
                      <h3 class="font-semibold text-lg group-hover:text-primary transition-colors">{{ location.name }}</h3>
                      <Badge variant="outline">{{ location.category }}</Badge>
                    </div>
                    <p class="text-muted-foreground text-sm mb-3">{{ location.address }}</p>
                    <div class="flex items-center gap-6 text-sm text-muted-foreground">
                      <span class="flex items-center gap-1">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        {{ location.imageCount }} 张照片
                      </span>
                      <span class="flex items-center gap-1">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {{ formatLastVisit(location.lastVisit) }}
                      </span>
                      <span class="flex items-center gap-1">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        </svg>
                        {{ formatDistance(location.coordinates) }}
                      </span>
                    </div>
                  </div>
                </div>
                
                <!-- 照片预览 -->
                <div class="flex gap-2">
                  <div 
                    v-for="image in location.images.slice(0, 3)" 
                    :key="image.id"
                    class="w-16 h-16 rounded-lg overflow-hidden bg-gradient-to-br from-primary/20 to-secondary/20 group-hover:scale-105 transition-transform"
                  >
                    <div class="w-full h-full flex items-center justify-center">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </div>
                  </div>
                  <div 
                    v-if="location.images.length > 3"
                    class="w-16 h-16 rounded-lg bg-muted/50 flex items-center justify-center text-muted-foreground text-sm font-medium"
                  >
                    +{{ location.images.length - 3 }}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>

    <!-- 地图视图 -->
    <div v-else-if="viewMode === 'map'" class="text-center py-16">
      <div class="bg-muted/50 rounded-full w-24 h-24 flex items-center justify-center mx-auto mb-6">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
        </svg>
      </div>
      <h3 class="text-xl font-medium mb-2">地图视图</h3>
      <p class="text-muted-foreground">地图视图功能正在开发中...</p>
    </div>

    <!-- 热力图视图 -->
    <div v-else-if="viewMode === 'heatmap'" class="text-center py-16">
      <div class="bg-muted/50 rounded-full w-24 h-24 flex items-center justify-center mx-auto mb-6">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      </div>
      <h3 class="text-xl font-medium mb-2">热力图视图</h3>
      <p class="text-muted-foreground">热力图视图功能正在开发中...</p>
    </div>
  </div>
</template>