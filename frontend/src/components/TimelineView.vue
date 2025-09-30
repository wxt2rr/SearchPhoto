<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useImageStore } from '@/stores/imageStore'
import { getPhotosByTimeline, getThumbnail } from '@/api'
import { 
  Clock, 
  MapPin, 
  Camera
} from 'lucide-vue-next'

const imageStore = useImageStore()

// 时间轴数据
const timelineData = ref<any[]>([])
const isLoading = ref(false)

// 时间轴视图模式
const viewMode = ref('timeline')

// 计算属性
const groupedByPeriod = computed(() => {
  // 这里应该根据selectedPeriod对数据进行分组
  return timelineData.value
})


// 格式化日期
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now.getTime() - date.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 1) return '昨天'
  if (diffDays < 7) return `${diffDays}天前`
  if (diffDays < 30) return `${Math.ceil(diffDays / 7)}周前`
  return date.toLocaleDateString('zh-CN', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}

// 加载时间线数据
const loadTimelineData = async () => {
  try {
    isLoading.value = true
    const response = await getPhotosByTimeline()
    
    // 检查响应数据是否存在且为数组
    if (response && Array.isArray(response)) {
      // 按日期分组图片
      const groupedData: { [key: string]: any } = {}
      
      response.forEach((item: any) => {
        const date = new Date(item.date).toDateString()
        
        if (!groupedData[date]) {
          groupedData[date] = {
            date: item.date,
            title: `照片回忆 - ${new Date(item.date).toLocaleDateString('zh-CN')}`,
            location: item.location || '未知位置',
            weather: '晴朗',
            tags: item.tags || [],
            images: []
          }
        }
        
        groupedData[date].images.push({
          ...item,
          thumbnail: getThumbnail(item.path)
        })
      })
      
      // 转换为数组并按日期排序
      timelineData.value = Object.values(groupedData)
        .sort((a: any, b: any) => new Date(b.date).getTime() - new Date(a.date).getTime())
    } else {
      console.warn('时间线数据格式不正确:', response)
      timelineData.value = []
    }
  } catch (error) {
    console.error('加载时间线数据失败:', error)
    // 如果API失败，使用空数据
    timelineData.value = []
  } finally {
    isLoading.value = false
  }
}

// 处理图片加载错误
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
  // 显示占位符
  const placeholder = img.nextElementSibling as HTMLElement
  if (placeholder) {
    placeholder.style.display = 'flex'
  }
}

onMounted(() => {
  loadTimelineData()
})
</script>

<template>
  <div class="max-w-6xl mx-auto px-4 py-8">
    <!-- 头部控制 -->
    <div class="mb-8">
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div>
          <h1 class="text-3xl font-bold mb-2">时间轴浏览</h1>
          <p class="text-muted-foreground">按时间顺序浏览你的照片回忆</p>
        </div>
        
      </div>

    </div>

    <!-- 加载状态 -->
    <div v-if="isLoading" class="flex justify-center items-center py-16">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="timelineData.length === 0" class="text-center py-16">
      <div class="bg-muted/50 rounded-full w-24 h-24 flex items-center justify-center mx-auto mb-6">
        <Camera class="h-12 w-12 text-muted-foreground" />
      </div>
      <h3 class="text-xl font-medium mb-2">暂无照片</h3>
      <p class="text-muted-foreground">请先添加一些照片到您的图库中</p>
    </div>

     <!-- 时间轴视图 -->
     <div v-else class="space-y-8">
      <div 
        v-for="(item, index) in groupedByPeriod" 
        :key="item.date"
        class="relative"
      >
        <!-- 时间轴线条 -->
        <div v-if="index < groupedByPeriod.length - 1" class="absolute left-6 top-16 w-0.5 h-full bg-gradient-to-b from-primary to-primary/20"></div>
        
        <div class="flex gap-6">
          <!-- 时间节点 -->
          <div class="flex flex-col items-center">
            <div class="w-12 h-12 bg-primary rounded-full flex items-center justify-center shadow-glow">
              <Camera class="h-6 w-6 text-primary-foreground" />
            </div>
            <div class="text-sm text-muted-foreground mt-2 text-center">
              {{ formatDate(item.date) }}
            </div>
          </div>
          
          <!-- 内容卡片 -->
          <div class="flex-1">
            <Card class="border-0 bg-card/50 backdrop-blur-sm hover:shadow-xl transition-all duration-300 group">
              <CardHeader>
                <div class="flex justify-between items-start">
                  <div>
                    <CardTitle class="text-xl group-hover:text-primary transition-colors">{{ item.title }}</CardTitle>
                    <CardDescription class="flex items-center gap-4 mt-2">
                      <span class="flex items-center gap-1">
                        <MapPin class="h-4 w-4" />
                        {{ item.location }}
                      </span>
                      <span class="flex items-center gap-1">
                        <Camera class="h-4 w-4" />
                        {{ item.images.length }} 张照片
                      </span>
                    </CardDescription>
                  </div>
                  <Badge variant="outline">{{ item.weather }}</Badge>
                </div>
              </CardHeader>
              <CardContent>
                <!-- 图片网格 -->
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
                  <div 
                    v-for="image in item.images.slice(0, 4)" 
                    :key="image.id"
                    class="aspect-square rounded-lg overflow-hidden bg-muted group-hover:scale-105 transition-transform cursor-pointer"
                  >
                    <img 
                      v-if="image.thumbnail" 
                      :src="image.thumbnail" 
                      :alt="image.title"
                      class="w-full h-full object-cover"
                      @error="handleImageError"
                    />
                    <div 
                      v-else
                      class="w-full h-full bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center"
                    >
                      <Camera class="h-8 w-8 text-muted-foreground" />
                    </div>
                  </div>
                  <div 
                    v-if="item.images.length > 4"
                    class="aspect-square rounded-lg bg-muted/50 flex items-center justify-center text-muted-foreground cursor-pointer hover:bg-muted transition-colors"
                  >
                    <span class="text-sm font-medium">+{{ item.images.length - 4 }}</span>
                  </div>
                </div>
                
                <!-- 标签 -->
                <div class="flex flex-wrap gap-2">
                  <Badge 
                    v-for="tag in item.tags" 
                    :key="tag"
                    variant="secondary"
                    class="text-xs"
                  >
                    {{ tag }}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.timeline-line {
  background: linear-gradient(to bottom, theme('colors.primary.500'), theme('colors.primary.200'));
}
</style>