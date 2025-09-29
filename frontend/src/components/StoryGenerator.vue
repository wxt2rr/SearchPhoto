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

// 原来的模拟数据，现在作为备用
const mockStories = ref([
  {
    id: 1,
    title: '春日踏青记',
    content: '阳光正好，微风不燥。在这个美好的春日午后，我们来到了西湖公园。樱花正盛，粉色的花瓣如雪花般飘洒，孩子们在草地上奔跑嬉戏，大人们悠闲地坐在湖边聊天。这一刻，时间仿佛静止了，只有快门声记录着这份美好。',
    date: '2024-03-15',
    location: '西湖公园',
    people: ['张三', '李四'],
    tags: ['春天', '踏青', '家庭', '樱花'],
    images: [
      { id: 1, path: '/api/image1.jpg', thumbnail: '/api/thumb1.jpg' },
      { id: 2, path: '/api/image2.jpg', thumbnail: '/api/thumb2.jpg' },
      { id: 3, path: '/api/image3.jpg', thumbnail: '/api/thumb3.jpg' },
    ],
    mood: '愉悦',
    weather: '晴朗',
    aiGenerated: true,
    likes: 12,
    views: 156
  },
  {
    id: 2,
    title: '温馨家庭聚餐',
    content: '今天是奶奶的生日，全家人聚在一起为她庆祝。餐桌上摆满了奶奶爱吃的菜，大家围坐在一起，有说有笑。当生日蛋糕端上来的那一刻，奶奶眼中闪烁着幸福的泪花。这样的时光，是最珍贵的回忆。',
    date: '2024-03-10',
    location: '家中',
    people: ['张三', '奶奶', '爸爸', '妈妈'],
    tags: ['家庭', '生日', '聚餐', '温馨'],
    images: [
      { id: 4, path: '/api/image4.jpg', thumbnail: '/api/thumb4.jpg' },
      { id: 5, path: '/api/image5.jpg', thumbnail: '/api/thumb5.jpg' },
    ],
    mood: '温馨',
    weather: '室内',
    aiGenerated: true,
    likes: 8,
    views: 89
  },
  {
    id: 3,
    title: '咖啡时光',
    content: '午后的咖啡厅，阳光透过百叶窗洒在桌面上，形成斑驳的光影。一杯拿铁，一本书，还有窗外匆忙的行人。这样的慢时光，在快节奏的生活中显得格外珍贵。',
    date: '2024-03-12',
    location: '咖啡厅',
    people: [],
    tags: ['咖啡', '阅读', '独处', '慢生活'],
    images: [
      { id: 6, path: '/api/image6.jpg', thumbnail: '/api/thumb6.jpg' },
    ],
    mood: '宁静',
    weather: '晴朗',
    aiGenerated: false,
    likes: 15,
    views: 203
  }
])

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
  <div class="max-w-6xl mx-auto px-4 py-8">
    <!-- 头部 -->
    <div class="mb-8">
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold mb-4">
          <span class="bg-clip-text text-transparent bg-gradient-to-r from-foreground via-primary to-secondary">
            AI故事生成
          </span>
        </h1>
        <p class="text-xl text-muted-foreground">让AI为你的照片创作美好的故事</p>
      </div>

      <!-- 统计概览 -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card class="border-0 bg-gradient-to-br from-primary/10 to-primary/5 backdrop-blur-sm">
          <CardContent class="p-6 text-center">
            <div class="text-3xl font-bold text-primary mb-2">{{ stories.length }}</div>
            <div class="text-muted-foreground">生成故事</div>
          </CardContent>
        </Card>
        <Card class="border-0 bg-gradient-to-br from-secondary/10 to-secondary/5 backdrop-blur-sm">
          <CardContent class="p-6 text-center">
            <div class="text-3xl font-bold text-secondary mb-2">{{ aiGeneratedCount }}</div>
            <div class="text-muted-foreground">AI创作</div>
          </CardContent>
        </Card>
        <Card class="border-0 bg-gradient-to-br from-green-500/10 to-green-500/5 backdrop-blur-sm">
          <CardContent class="p-6 text-center">
            <div class="text-3xl font-bold text-green-600 mb-2">{{ totalViews }}</div>
            <div class="text-muted-foreground">总浏览量</div>
          </CardContent>
        </Card>
        <Card class="border-0 bg-gradient-to-br from-pink-500/10 to-pink-500/5 backdrop-blur-sm">
          <CardContent class="p-6 text-center">
            <div class="text-3xl font-bold text-pink-600 mb-2">{{ totalLikes }}</div>
            <div class="text-muted-foreground">总点赞数</div>
          </CardContent>
        </Card>
      </div>

      <!-- 生成按钮 -->
      <div class="text-center mb-8">
        <Button 
          @click="startGeneration" 
          size="lg"
          class="bg-gradient-to-r from-primary to-secondary hover:from-primary/90 hover:to-secondary/90 text-white px-8 py-3 text-lg"
        >
          <Sparkles class="h-6 w-6 mr-2" />
          创作新故事
        </Button>
      </div>
    </div>

    <!-- 故事列表 -->
    <div class="space-y-8">
      <div 
        v-for="story in sortedStories" 
        :key="story.id"
        class="group"
      >
        <Card class="border-0 bg-gradient-to-br from-card/80 to-card/40 backdrop-blur-sm hover:shadow-2xl transition-all duration-500 cursor-pointer overflow-hidden">
          <div class="relative">
            <!-- 背景装饰 -->
            <div class="absolute inset-0 bg-gradient-to-r from-primary/5 via-transparent to-secondary/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            
            <CardContent class="p-8 relative">
              <!-- 故事头部 -->
              <div class="flex justify-between items-start mb-6">
                <div class="flex-1">
                  <div class="flex items-center gap-3 mb-3">
                    <h2 class="text-2xl font-bold group-hover:text-primary transition-colors">{{ story.title }}</h2>
                    <Badge v-if="story.aiGenerated" variant="secondary" class="bg-gradient-to-r from-ai-500/20 to-neural-500/20 text-ai-700">
                      <Sparkles class="h-3 w-3 mr-1" />
                      AI生成
                    </Badge>
                  </div>
                  
                  <div class="flex flex-wrap items-center gap-4 text-sm text-muted-foreground mb-4">
                    <span class="flex items-center gap-1">
                      <Calendar class="h-4 w-4" />
                      {{ formatDate(story.date) }}
                    </span>
                    <span class="flex items-center gap-1">
                      <MapPin class="h-4 w-4" />
                      {{ story.location }}
                    </span>
                    <span class="flex items-center gap-1" :class="getMoodColor(story.mood)">
                      <span>{{ getMoodIcon(story.mood) }}</span>
                      {{ story.mood }}
                    </span>
                    <span class="flex items-center gap-1">
                      <ImageIcon class="h-4 w-4" />
                      {{ story.views }}
                    </span>
                  </div>
                </div>
                
                <!-- 操作按钮 -->
                <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <Button variant="ghost" size="sm" @click.stop="likeStory(story)">
                    <Heart class="h-4 w-4 mr-1" />
                    {{ story.likes }}
                  </Button>
                  <Button variant="ghost" size="sm" @click.stop="shareStory(story)">
                    <Share2 class="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm" @click.stop="exportStory(story)">
                    <Download class="h-4 w-4" />
                  </Button>
                </div>
              </div>

              <!-- 故事内容 -->
              <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <!-- 文本内容 -->
                <div class="lg:col-span-2">
                  <p class="text-lg leading-relaxed text-foreground/90 mb-6 line-clamp-4">
                    {{ story.content }}
                  </p>
                  
                  <!-- 人物和标签 -->
                  <div class="space-y-3">
                    <div v-if="story.people.length > 0" class="flex items-center gap-2">
                      <span class="text-sm font-medium text-muted-foreground">出现人物:</span>
                      <div class="flex flex-wrap gap-2">
                        <Badge v-for="person in story.people" :key="person" variant="outline" class="text-xs">
                          👤 {{ person }}
                        </Badge>
                      </div>
                    </div>
                    
                    <div class="flex items-center gap-2">
                      <span class="text-sm font-medium text-muted-foreground">标签:</span>
                      <div class="flex flex-wrap gap-2">
                        <Badge v-for="tag in story.tags" :key="tag" variant="secondary" class="text-xs">
                          {{ tag }}
                        </Badge>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- 图片预览 -->
                <div class="space-y-4">
                  <div class="grid grid-cols-2 gap-3">
                    <div 
                      v-for="(image, index) in story.images.slice(0, 4)" 
                      :key="image.id"
                      class="aspect-square rounded-xl overflow-hidden bg-gradient-to-br from-primary/20 to-secondary/20 group-hover:scale-105 transition-transform"
                      :class="{ 'col-span-2': index === 0 && story.images.length > 1 }"
                    >
                      <div class="w-full h-full flex items-center justify-center">
                        <Camera class="h-8 w-8 text-muted-foreground" />
                      </div>
                    </div>
                    <div 
                      v-if="story.images.length > 4"
                      class="aspect-square rounded-xl bg-muted/50 flex items-center justify-center text-muted-foreground cursor-pointer hover:bg-muted transition-colors"
                    >
                      <span class="text-sm font-medium">+{{ story.images.length - 4 }}</span>
                    </div>
                  </div>
                  
                  <Button 
                    variant="outline" 
                    class="w-full"
                    @click="showStoryDetails(story)"
                  >
                    阅读完整故事
                  </Button>
                </div>
              </div>
            </CardContent>
          </div>
        </Card>
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
</template>

<style scoped>
.line-clamp-4 {
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>