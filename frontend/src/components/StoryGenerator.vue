<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { generateStory as apiGenerateStory, getThumbnail } from '@/api'
import { 
  BookOpen, 
  Calendar, 
  MapPin, 
  Users, 
  Camera, 
  Clock,
  Copy,
  Download,
  Share2,
  Sparkles,
  Image as ImageIcon,
  Play,
  MoreHorizontal,
  Heart
} from 'lucide-vue-next'

// 故事数据
const stories = ref<any[]>([])
const isLoading = ref(false)

// 清空测试数据，使用空数组
const mockStories = ref([])

// 状态管理
const selectedStory = ref<any>(null)
const showStoryDialog = ref(false)
const isGenerating = ref(false)
const generationProgress = ref(0)
const showGenerateDialog = ref(false)
const selectedImages = ref<any[]>([])
const storyPrompt = ref('')
const storyStyle = ref<'narrative' | 'poetic' | 'casual' | 'formal'>('narrative')

// 故事风格选项
const storyStyles = [
  { key: 'narrative', label: '叙述风格', description: '详细描述事件经过，适合记录重要时刻', icon: '📖' },
  { key: 'poetic', label: '诗意风格', description: '优美的文字表达，充满诗意和情感', icon: '🌸' },
  { key: 'casual', label: '轻松风格', description: '轻松幽默的语调，适合日常生活记录', icon: '😊' },
  { key: 'formal', label: '正式风格', description: '正式严谨的表达，适合重要场合', icon: '🎩' }
]

// 计算属性
const sortedStories = computed(() => {
  return [...stories.value].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
})

const aiGeneratedCount = computed(() => {
  return stories.value.filter(story => story.aiGenerated).length
})

const totalViews = computed(() => {
  return stories.value.reduce((sum, story) => sum + story.views, 0)
})

const totalLikes = computed(() => {
  return stories.value.reduce((sum, story) => sum + story.likes, 0)
})

// 方法
const getMoodIcon = (mood: string) => {
  const moodMap: { [key: string]: string } = {
    '愉悦': '😊',
    '温馨': '🥰',
    '宁静': '😌',
    '兴奋': '🤩',
    '感动': '🥺',
    '怀念': '😌'
  }
  return moodMap[mood] || '😊'
}

const getMoodColor = (mood: string) => {
  const colorMap: { [key: string]: string } = {
    '愉悦': 'text-green-600',
    '温馨': 'text-pink-600',
    '宁静': 'text-blue-600',
    '兴奋': 'text-orange-600',
    '感动': 'text-purple-600',
    '怀念': 'text-gray-600'
  }
  return colorMap[mood] || 'text-gray-600'
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}

const showStoryDetails = (story: any) => {
  selectedStory.value = story
  showStoryDialog.value = true
}

const startGeneration = () => {
  showGenerateDialog.value = true
}

const generateStoryFromAPI = async () => {
  if (selectedImages.value.length === 0) {
    alert('请至少选择一张照片')
    return
  }

  isGenerating.value = true
  generationProgress.value = 0

  try {
    // 调用真实的API生成故事
    const photoIds = selectedImages.value.map(img => img.id)
    const response = await apiGenerateStory(photoIds)
    
    // 生成新故事
    const newStory = {
      ...response,
      images: response.images.map((image: any) => ({
        ...image,
        thumbnail: getThumbnail(image.path)
      }))
    }

    stories.value.unshift(newStory)
    
    // 显示新生成的故事
    showStoryDetails(newStory)
  } catch (error) {
    console.error('生成故事失败:', error)
    // 如果API失败，使用模拟生成
    await generateStoryFallback()
  } finally {
    isGenerating.value = false
    showGenerateDialog.value = false
    selectedImages.value = []
    storyPrompt.value = ''
  }
}

const generateStoryFallback = async () => {
  // 模拟AI生成过程
  const steps = [
    { progress: 20, message: '分析照片内容...' },
    { progress: 40, message: '识别人物和场景...' },
    { progress: 60, message: '提取情感和氛围...' },
    { progress: 80, message: '生成故事文本...' },
    { progress: 100, message: '完成生成！' }
  ]

  for (const step of steps) {
    await new Promise(resolve => setTimeout(resolve, 1000))
    generationProgress.value = step.progress
  }

  // 生成新故事
  const newStory = {
    id: stories.value.length + 1,
    title: `AI生成故事 #${stories.value.length + 1}`,
    content: generateStoryContent(),
    date: new Date().toISOString().split('T')[0],
    location: '未知位置',
    people: [],
    tags: ['AI生成'],
    images: selectedImages.value,
    mood: '愉悦',
    weather: '未知',
    aiGenerated: true,
    likes: 0,
    views: 1
  }

  stories.value.unshift(newStory)
  showStoryDetails(newStory)
}

const generateStoryContent = () => {
  const templates = [
    '这是一个美好的时刻，照片记录了生活中的点点滴滴。阳光洒在脸上，微笑定格在这一瞬间，成为了永恒的回忆。',
    '时光荏苒，但这些珍贵的瞬间永远不会褪色。每一张照片都诉说着一个故事，每一个故事都承载着满满的回忆。',
    '生活就像一本相册，每一页都记录着不同的精彩。这些照片见证了我们的成长，记录了我们的喜怒哀乐。'
  ]
  return templates[Math.floor(Math.random() * templates.length)]
}

const likeStory = (story: any) => {
  story.likes++
}

const shareStory = (story: any) => {
  // 分享功能
  console.log('分享故事:', story.title)
}

const exportStory = (story: any) => {
  // 导出功能
  console.log('导出故事:', story.title)
}

// 加载故事数据
const loadStoriesData = async () => {
  try {
    isLoading.value = true
    // 这里可以添加获取已生成故事的API调用
    // const response = await getGeneratedStories()
    // stories.value = response
    
    // 暂时使用模拟数据
    stories.value = mockStories.value
  } catch (error) {
    console.error('加载故事数据失败:', error)
    stories.value = mockStories.value
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadStoriesData()
})
</script>

<template>
  <div class="min-h-screen bg-white">
    <div class="max-w-6xl mx-auto px-6 py-12">
      <!-- 头部 -->
      <div class="mb-12">
        <div class="text-center mb-12">
          <h1 class="text-5xl font-bold text-gray-900 mb-4">
            AI故事生成
          </h1>
          <p class="text-xl text-gray-600">让AI为你的照片创作美好的故事</p>
        </div>

        <!-- 统计概览 -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
          <div class="bg-white border border-gray-200 rounded-lg p-8 text-center">
            <div class="text-4xl font-bold text-gray-900 mb-2">{{ stories.length }}</div>
            <div class="text-gray-600">生成故事</div>
          </div>
          <div class="bg-white border border-gray-200 rounded-lg p-8 text-center">
            <div class="text-4xl font-bold text-gray-900 mb-2">{{ aiGeneratedCount }}</div>
            <div class="text-gray-600">AI创作</div>
          </div>
          <div class="bg-white border border-gray-200 rounded-lg p-8 text-center">
            <div class="text-4xl font-bold text-gray-900 mb-2">{{ totalViews }}</div>
            <div class="text-gray-600">总浏览量</div>
          </div>
          <div class="bg-white border border-gray-200 rounded-lg p-8 text-center">
            <div class="text-4xl font-bold text-gray-900 mb-2">{{ totalLikes }}</div>
            <div class="text-gray-600">总点赞数</div>
          </div>
        </div>

        <!-- 生成按钮 -->
        <div class="text-center mb-12">
          <Button 
            @click="startGeneration" 
            size="lg"
            class="bg-gray-900 text-white hover:bg-gray-800 px-12 py-6 text-lg"
          >
            <Sparkles class="h-6 w-6 mr-3" />
            创作新故事
          </Button>
        </div>
      </div>

      <!-- 故事列表 -->
      <div class="space-y-12">
        <div 
          v-for="story in sortedStories" 
          :key="story.id"
          class="group"
        >
          <div class="bg-white border border-gray-200 rounded-lg hover:shadow-lg transition-all duration-300 cursor-pointer overflow-hidden">
            <div class="p-8">
              <!-- 故事头部 -->
              <div class="flex justify-between items-start mb-8">
                <div class="flex-1">
                  <div class="flex items-center gap-4 mb-4">
                    <h2 class="text-3xl font-bold text-gray-900 group-hover:text-gray-700 transition-colors">{{ story.title }}</h2>
                    <Badge v-if="story.aiGenerated" variant="secondary" class="bg-gray-100 text-gray-600">
                      <Sparkles class="h-3 w-3 mr-1" />
                      AI生成
                    </Badge>
                  </div>
                  
                  <div class="flex flex-wrap items-center gap-6 text-sm text-gray-500 mb-6">
                    <span class="flex items-center gap-2">
                      <Calendar class="h-4 w-4" />
                      {{ formatDate(story.date) }}
                    </span>
                    <span class="flex items-center gap-2">
                      <MapPin class="h-4 w-4" />
                      {{ story.location }}
                    </span>
                    <span class="flex items-center gap-2" :class="getMoodColor(story.mood)">
                      <span>{{ getMoodIcon(story.mood) }}</span>
                      {{ story.mood }}
                    </span>
                    <span class="flex items-center gap-2">
                      <ImageIcon class="h-4 w-4" />
                      {{ story.views }}
                    </span>
                  </div>
                </div>
                
                <!-- 操作按钮 -->
                <div class="flex items-center gap-3 opacity-0 group-hover:opacity-100 transition-opacity">
                  <Button variant="ghost" size="sm" @click.stop="likeStory(story)" class="text-gray-600 hover:bg-gray-100">
                    <Heart class="h-4 w-4 mr-1" />
                    {{ story.likes }}
                  </Button>
                  <Button variant="ghost" size="sm" @click.stop="shareStory(story)" class="text-gray-600 hover:bg-gray-100">
                    <Share2 class="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm" @click.stop="exportStory(story)" class="text-gray-600 hover:bg-gray-100">
                    <Download class="h-4 w-4" />
                  </Button>
                </div>
              </div>

              <!-- 故事内容 -->
              <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <!-- 文本内容 -->
                <div class="lg:col-span-2">
                  <p class="text-lg leading-relaxed text-gray-700 mb-8 line-clamp-4">
                    {{ story.content }}
                  </p>
                  
                  <!-- 人物和标签 -->
                  <div class="space-y-4">
                    <div v-if="story.people.length > 0" class="flex items-center gap-3">
                      <span class="text-sm font-medium text-gray-600">出现人物:</span>
                      <div class="flex flex-wrap gap-2">
                        <Badge v-for="person in story.people" :key="person" variant="outline" class="text-xs border-gray-200 text-gray-600">
                          👤 {{ person }}
                        </Badge>
                      </div>
                    </div>
                    
                    <div class="flex items-center gap-3">
                      <span class="text-sm font-medium text-gray-600">标签:</span>
                      <div class="flex flex-wrap gap-2">
                        <Badge v-for="tag in story.tags" :key="tag" variant="secondary" class="text-xs bg-gray-100 text-gray-600">
                          {{ tag }}
                        </Badge>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- 图片预览 -->
                <div class="space-y-6">
                  <div class="grid grid-cols-2 gap-4">
                    <div 
                      v-for="(image, index) in story.images.slice(0, 4)" 
                      :key="image.id"
                      class="aspect-square rounded-lg overflow-hidden bg-gray-100 group-hover:scale-105 transition-transform"
                      :class="{ 'col-span-2': index === 0 && story.images.length > 1 }"
                    >
                      <div class="w-full h-full flex items-center justify-center">
                        <Camera class="h-8 w-8 text-gray-400" />
                      </div>
                    </div>
                    <div 
                      v-if="story.images.length > 4"
                      class="aspect-square rounded-lg bg-gray-50 flex items-center justify-center text-gray-500 cursor-pointer hover:bg-gray-100 transition-colors"
                    >
                      <span class="text-sm font-medium">+{{ story.images.length - 4 }}</span>
                    </div>
                  </div>
                  
                  <Button 
                    variant="outline" 
                    class="w-full border-gray-200 text-gray-700 hover:bg-gray-50"
                    @click="showStoryDetails(story)"
                  >
                    阅读完整故事
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    <!-- 故事详情对话框 -->
    <Dialog v-model:open="showStoryDialog">
      <DialogContent class="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle class="flex items-center gap-3">
            <span>{{ selectedStory?.title }}</span>
            <Badge v-if="selectedStory?.aiGenerated" variant="secondary" class="bg-gradient-to-r from-ai-500/20 to-neural-500/20 text-ai-700">
              AI生成
            </Badge>
          </DialogTitle>
        </DialogHeader>
        
        <div v-if="selectedStory" class="space-y-6">
          <!-- 故事信息 -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-muted/50 rounded-lg">
            <div class="space-y-2">
              <div class="flex items-center gap-2 text-sm">
                <Calendar class="h-4 w-4" />
                <strong>日期:</strong> {{ formatDate(selectedStory.date) }}
              </div>
              <div class="flex items-center gap-2 text-sm">
                <MapPin class="h-4 w-4" />
                <strong>地点:</strong> {{ selectedStory.location }}
              </div>
            </div>
            <div class="space-y-2">
              <div class="flex items-center gap-2 text-sm" :class="getMoodColor(selectedStory.mood)">
                <span>{{ getMoodIcon(selectedStory.mood) }}</span>
                <strong>情绪:</strong> {{ selectedStory.mood }}
              </div>
              <div class="flex items-center gap-2 text-sm">
                <Camera class="h-4 w-4" />
                <strong>照片:</strong> {{ selectedStory.images.length }} 张
              </div>
            </div>
          </div>

          <!-- 故事内容 -->
          <div class="prose prose-lg max-w-none">
            <p class="text-lg leading-relaxed">{{ selectedStory.content }}</p>
          </div>

          <!-- 照片网格 -->
          <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div 
              v-for="image in selectedStory.images" 
              :key="image.id"
              class="aspect-square rounded-lg overflow-hidden bg-gradient-to-br from-primary/20 to-secondary/20 hover:scale-105 transition-transform cursor-pointer"
            >
              <div class="w-full h-full flex items-center justify-center">
                <Camera class="h-8 w-8 text-muted-foreground" />
              </div>
            </div>
          </div>

          <!-- 标签和人物 -->
          <div class="space-y-4">
            <div v-if="selectedStory.people.length > 0">
              <h4 class="font-medium mb-2">出现人物</h4>
              <div class="flex flex-wrap gap-2">
                <Badge v-for="person in selectedStory.people" :key="person" variant="outline">
                  👤 {{ person }}
                </Badge>
              </div>
            </div>
            
            <div>
              <h4 class="font-medium mb-2">标签</h4>
              <div class="flex flex-wrap gap-2">
                <Badge v-for="tag in selectedStory.tags" :key="tag" variant="secondary">
                  {{ tag }}
                </Badge>
              </div>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>

    <!-- 生成故事对话框 -->
    <Dialog v-model:open="showGenerateDialog">
      <DialogContent class="max-w-2xl">
        <DialogHeader>
          <DialogTitle class="flex items-center gap-2">
            <Sparkles class="h-5 w-5" />
            AI故事生成
          </DialogTitle>
        </DialogHeader>
        
        <div v-if="!isGenerating" class="space-y-6">
          <!-- 选择照片 -->
          <div>
            <label class="text-sm font-medium mb-3 block">选择照片 (最多10张)</label>
            <div class="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 text-center">
              <Camera class="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <p class="text-muted-foreground mb-2">点击选择照片或拖拽到此处</p>
              <p class="text-sm text-muted-foreground">支持 JPG、PNG 格式</p>
            </div>
          </div>

          <!-- 故事风格 -->
          <div>
            <label class="text-sm font-medium mb-3 block">选择故事风格</label>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div 
                v-for="style in storyStyles" 
                :key="style.key"
                class="p-4 border rounded-lg cursor-pointer transition-all hover:shadow-md"
                :class="storyStyle === style.key ? 'border-primary bg-primary/5' : 'border-muted'"
                @click="storyStyle = style.key"
              >
                <div class="flex items-center gap-3 mb-2">
                  <span class="text-2xl">{{ style.icon }}</span>
                  <h4 class="font-medium">{{ style.label }}</h4>
                </div>
                <p class="text-sm text-muted-foreground">{{ style.description }}</p>
              </div>
            </div>
          </div>

          <!-- 自定义提示 -->
          <div>
            <label class="text-sm font-medium mb-2 block">自定义提示 (可选)</label>
            <Input 
              v-model="storyPrompt" 
              placeholder="例如：重点描述人物的情感变化..."
              class="w-full"
            />
          </div>

          <div class="flex justify-end gap-2">
            <Button variant="outline" @click="showGenerateDialog = false">
              取消
            </Button>
            <Button @click="generateStoryFromAPI" :disabled="selectedImages.length === 0">
              开始生成
            </Button>
          </div>
        </div>

        <!-- 生成进度 -->
        <div v-else class="space-y-6 text-center py-8">
          <div class="w-16 h-16 mx-auto bg-gradient-to-r from-primary to-secondary rounded-full flex items-center justify-center animate-pulse">
            <Sparkles class="h-8 w-8 text-white" />
          </div>
          <div>
            <h3 class="text-lg font-medium mb-2">AI正在创作故事...</h3>
            <div class="w-full bg-muted rounded-full h-2 mb-2">
              <div 
                class="bg-gradient-to-r from-primary to-secondary h-2 rounded-full transition-all duration-500"
                :style="{ width: `${generationProgress}%` }"
              ></div>
            </div>
            <p class="text-sm text-muted-foreground">{{ generationProgress }}% 完成</p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
    </div>
  </div>
</template>

<style scoped>
.line-clamp-4 {
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>