<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { getPhotosByPeople, getThumbnail } from '@/api'
import { Search as SearchIcon, Plus, Zap, Camera } from 'lucide-vue-next'

// 人物识别数据
const peopleData = ref<any[]>([])
const isLoading = ref(false)

// 原来的模拟数据，现在作为备用
const mockPeopleData = ref([
  {
    id: 1,
    name: '张三',
    avatar: '/api/avatar1.jpg',
    imageCount: 156,
    firstAppearance: '2023-01-15',
    lastSeen: '2024-03-20',
    relationship: '家人',
    confidence: 0.95,
    ageRange: '25-35',
    gender: '男',
    images: [
      { id: 1, path: '/api/image1.jpg', thumbnail: '/api/thumb1.jpg', date: '2024-03-20' },
      { id: 2, path: '/api/image2.jpg', thumbnail: '/api/thumb2.jpg', date: '2024-03-18' },
      { id: 3, path: '/api/image3.jpg', thumbnail: '/api/thumb3.jpg', date: '2024-03-15' },
    ]
  },
  {
    id: 2,
    name: '李四',
    avatar: '/api/avatar2.jpg',
    imageCount: 89,
    firstAppearance: '2023-03-22',
    lastSeen: '2024-03-19',
    relationship: '朋友',
    confidence: 0.92,
    ageRange: '20-30',
    gender: '女',
    images: [
      { id: 4, path: '/api/image4.jpg', thumbnail: '/api/thumb4.jpg', date: '2024-03-19' },
      { id: 5, path: '/api/image5.jpg', thumbnail: '/api/thumb5.jpg', date: '2024-03-17' },
    ]
  },
  {
    id: 3,
    name: '王五',
    avatar: '/api/avatar3.jpg',
    imageCount: 67,
    firstAppearance: '2023-06-10',
    lastSeen: '2024-03-16',
    relationship: '同事',
    confidence: 0.88,
    ageRange: '30-40',
    gender: '男',
    images: [
      { id: 6, path: '/api/image6.jpg', thumbnail: '/api/thumb6.jpg', date: '2024-03-16' },
      { id: 7, path: '/api/image7.jpg', thumbnail: '/api/thumb7.jpg', date: '2024-03-14' },
      { id: 8, path: '/api/image8.jpg', thumbnail: '/api/thumb8.jpg', date: '2024-03-12' },
    ]
  },
  {
    id: 4,
    name: '未知人物 #1',
    avatar: null,
    imageCount: 23,
    firstAppearance: '2024-02-28',
    lastSeen: '2024-03-10',
    relationship: '未知',
    confidence: 0.76,
    ageRange: '20-30',
    gender: '女',
    images: [
      { id: 9, path: '/api/image9.jpg', thumbnail: '/api/thumb9.jpg', date: '2024-03-10' },
    ]
  }
])

// 状态管理
const searchQuery = ref('')
const selectedRelationship = ref<string>('all')
const sortBy = ref<'name' | 'imageCount' | 'lastSeen' | 'confidence'>('imageCount')
const showPersonDialog = ref(false)
const selectedPerson = ref<any>(null)
const showAddPersonDialog = ref(false)
const newPersonName = ref('')

// 关系类型
const relationships = ref([
  { key: 'all', label: '全部', icon: '👥', count: 0 },
  { key: '家人', label: '家人', icon: '👨‍👩‍👧‍👦', count: 0 },
  { key: '朋友', label: '朋友', icon: '👫', count: 0 },
  { key: '同事', label: '同事', icon: '💼', count: 0 },
  { key: '未知', label: '未知', icon: '❓', count: 0 }
])

// 计算属性
const filteredPeople = computed(() => {
  let filtered = peopleData.value

  // 按搜索关键词筛选
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(person => 
      person.name.toLowerCase().includes(query) ||
      person.relationship.toLowerCase().includes(query)
    )
  }

  // 按关系筛选
  if (selectedRelationship.value !== 'all') {
    filtered = filtered.filter(person => person.relationship === selectedRelationship.value)
  }

  // 排序
  filtered.sort((a, b) => {
    switch (sortBy.value) {
      case 'name':
        return a.name.localeCompare(b.name)
      case 'imageCount':
        return b.imageCount - a.imageCount
      case 'lastSeen':
        return new Date(b.lastSeen).getTime() - new Date(a.lastSeen).getTime()
      case 'confidence':
        return b.confidence - a.confidence
      default:
        return 0
    }
  })

  return filtered
})

const totalImages = computed(() => {
  return filteredPeople.value.reduce((sum, person) => sum + person.imageCount, 0)
})

const averageConfidence = computed(() => {
  if (filteredPeople.value.length === 0) return 0
  const sum = filteredPeople.value.reduce((sum, person) => sum + person.confidence, 0)
  return (sum / filteredPeople.value.length * 100).toFixed(1)
})

const topPeople = computed(() => {
  return [...peopleData.value]
    .sort((a, b) => b.imageCount - a.imageCount)
    .slice(0, 6)
})

// 方法
const getRelationshipIcon = (relationship: string) => {
  const iconMap: { [key: string]: string } = {
    '家人': '👨‍👩‍👧‍👦',
    '朋友': '👫',
    '同事': '💼',
    '未知': '❓'
  }
  return iconMap[relationship] || '👤'
}

const getConfidenceColor = (confidence: number) => {
  if (confidence >= 0.9) return 'text-green-600'
  if (confidence >= 0.8) return 'text-blue-600'
  if (confidence >= 0.7) return 'text-yellow-600'
  return 'text-red-600'
}

const getConfidenceLabel = (confidence: number) => {
  if (confidence >= 0.9) return '高置信度'
  if (confidence >= 0.8) return '中等置信度'
  if (confidence >= 0.7) return '低置信度'
  return '极低置信度'
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now.getTime() - date.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 1) return '昨天'
  if (diffDays < 7) return `${diffDays}天前`
  if (diffDays < 30) return `${Math.ceil(diffDays / 7)}周前`
  return date.toLocaleDateString('zh-CN')
}

const showPersonDetails = (person: any) => {
  selectedPerson.value = person
  showPersonDialog.value = true
}

const addNewPerson = () => {
  showAddPersonDialog.value = true
}

const confirmAddPerson = () => {
  if (newPersonName.value.trim()) {
    // 这里应该调用API添加新人物
    console.log('添加新人物:', newPersonName.value)
    newPersonName.value = ''
    showAddPersonDialog.value = false
  }
}

// 更新关系计数
const updateRelationshipCounts = () => {
  relationships.value.forEach(relationship => {
    if (relationship.key === 'all') {
      relationship.count = peopleData.value.length
    } else {
      relationship.count = peopleData.value.filter(person => person.relationship === relationship.key).length
    }
  })
}

// 加载人物识别数据
const loadPeopleData = async () => {
  try {
    isLoading.value = true
    const response = await getPhotosByPeople()
    peopleData.value = response.map((item: any) => ({
      ...item,
      images: item.images.map((image: any) => ({
        ...image,
        thumbnail: getThumbnail(image.path)
      }))
    }))
    updateRelationshipCounts()
  } catch (error) {
    console.error('加载人物识别数据失败:', error)
    // 如果API失败，使用模拟数据
    peopleData.value = mockPeopleData.value
    updateRelationshipCounts()
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadPeopleData()
})
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 py-8">
    <!-- 头部 -->
    <div class="mb-8">
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold mb-4">
          <span class="bg-clip-text text-transparent bg-gradient-to-r from-foreground via-primary to-secondary">
            人物识别
          </span>
        </h1>
        <p class="text-xl text-muted-foreground">AI智能识别照片中的人物，管理你的回忆</p>
      </div>

      <!-- 统计概览 -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card class="border-0 bg-gradient-to-br from-primary/10 to-primary/5 backdrop-blur-sm">
          <CardContent class="p-6 text-center">
            <div class="text-3xl font-bold text-primary mb-2">{{ peopleData.length }}</div>
            <div class="text-muted-foreground">识别人物</div>
          </CardContent>
        </Card>
        <Card class="border-0 bg-gradient-to-br from-secondary/10 to-secondary/5 backdrop-blur-sm">
          <CardContent class="p-6 text-center">
            <div class="text-3xl font-bold text-secondary mb-2">{{ totalImages }}</div>
            <div class="text-muted-foreground">人物照片</div>
          </CardContent>
        </Card>
        <Card class="border-0 bg-gradient-to-br from-green-500/10 to-green-500/5 backdrop-blur-sm">
          <CardContent class="p-6 text-center">
            <div class="text-3xl font-bold text-green-600 mb-2">{{ averageConfidence }}%</div>
            <div class="text-muted-foreground">平均置信度</div>
          </CardContent>
        </Card>
        <Card class="border-0 bg-gradient-to-br from-purple-500/10 to-purple-500/5 backdrop-blur-sm">
          <CardContent class="p-6 text-center">
            <div class="text-3xl font-bold text-purple-600 mb-2">{{ relationships.length - 1 }}</div>
            <div class="text-muted-foreground">关系类型</div>
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
                  <SearchIcon class="h-5 w-5 text-muted-foreground" />
                </div>
                <Input 
                  v-model="searchQuery" 
                  placeholder="搜索人物姓名..."
                  class="pl-10"
                />
              </div>
            </div>

            <!-- 排序选择 -->
            <div class="flex items-center gap-4">
              <label class="text-sm font-medium">排序:</label>
              <select v-model="sortBy" class="px-3 py-2 border rounded-md bg-background text-sm">
                <option value="imageCount">照片数量</option>
                <option value="name">姓名</option>
                <option value="lastSeen">最近出现</option>
                <option value="confidence">置信度</option>
              </select>
            </div>

            <!-- 添加人物按钮 -->
            <Button @click="addNewPerson" class="flex items-center gap-2">
              <Plus class="h-4 w-4" />
              添加人物
            </Button>
          </div>

          <!-- 关系筛选 -->
          <div class="flex flex-wrap gap-2 mt-6">
            <Button
              v-for="relationship in relationships"
              :key="relationship.key"
              :variant="selectedRelationship === relationship.key ? 'default' : 'outline'"
              size="sm"
              @click="selectedRelationship = relationship.key"
              class="flex items-center gap-2"
            >
              <span>{{ relationship.icon }}</span>
              <span>{{ relationship.label }}</span>
              <Badge variant="secondary" class="ml-1">{{ relationship.count }}</Badge>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- 热门人物 -->
    <div class="mb-8">
      <h2 class="text-2xl font-bold mb-6 flex items-center gap-2">
          <Zap class="h-6 w-6 text-primary" />
          出现最多的人物
        </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card 
          v-for="person in topPeople.slice(0, 6)" 
          :key="person.id"
          class="border-0 bg-gradient-to-br from-card/80 to-card/40 backdrop-blur-sm hover:shadow-xl transition-all duration-300 group cursor-pointer"
          @click="showPersonDetails(person)"
        >
          <CardContent class="p-6">
            <div class="flex items-center gap-4 mb-4">
              <!-- 头像 -->
              <div class="w-16 h-16 rounded-full overflow-hidden bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center">
                <div v-if="!person.avatar" class="text-2xl">
                  {{ person.name.includes('未知') ? '❓' : person.name.charAt(0) }}
                </div>
                <img v-else :src="person.avatar" :alt="person.name" class="w-full h-full object-cover" />
              </div>
              
              <div class="flex-1">
                <h3 class="font-semibold text-lg group-hover:text-primary transition-colors">{{ person.name }}</h3>
                <div class="flex items-center gap-2 text-sm text-muted-foreground">
                  <span>{{ getRelationshipIcon(person.relationship) }}</span>
                  <span>{{ person.relationship }}</span>
                </div>
                <div class="flex items-center gap-2 mt-1">
                  <Badge :class="getConfidenceColor(person.confidence)" variant="outline">
                    {{ getConfidenceLabel(person.confidence) }}
                  </Badge>
                </div>
              </div>
            </div>
            
            <!-- 照片预览 -->
            <div class="grid grid-cols-3 gap-2 mb-4">
              <div 
                v-for="image in person.images.slice(0, 3)" 
                :key="image.id"
                class="aspect-square rounded-lg overflow-hidden bg-gradient-to-br from-primary/20 to-secondary/20 group-hover:scale-105 transition-transform"
              >
                <div class="w-full h-full flex items-center justify-center">
                  <Camera class="h-6 w-6 text-muted-foreground" />
                </div>
              </div>
            </div>
            
            <div class="flex justify-between items-center text-sm text-muted-foreground">
              <span class="flex items-center gap-1">
                <Camera class="h-4 w-4" />
                {{ person.imageCount }} 张照片
              </span>
              <span>{{ formatDate(person.lastSeen) }}</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>

    <!-- 所有人物列表 -->
    <div>
      <h2 class="text-2xl font-bold mb-6">所有人物 ({{ filteredPeople.length }})</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <Card 
          v-for="person in filteredPeople" 
          :key="person.id"
          class="border-0 bg-card/50 backdrop-blur-sm hover:shadow-lg transition-all duration-300 group cursor-pointer"
          @click="showPersonDetails(person)"
        >
          <CardContent class="p-6">
            <div class="text-center">
              <!-- 头像 -->
              <div class="w-20 h-20 rounded-full overflow-hidden bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                <div v-if="!person.avatar" class="text-3xl">
                  {{ person.name.includes('未知') ? '❓' : person.name.charAt(0) }}
                </div>
                <img v-else :src="person.avatar" :alt="person.name" class="w-full h-full object-cover" />
              </div>
              
              <h3 class="font-semibold text-lg mb-2 group-hover:text-primary transition-colors">{{ person.name }}</h3>
              
              <div class="space-y-2 mb-4">
                <div class="flex items-center justify-center gap-2 text-sm text-muted-foreground">
                  <span>{{ getRelationshipIcon(person.relationship) }}</span>
                  <span>{{ person.relationship }}</span>
                </div>
                <div class="flex items-center justify-center gap-2 text-sm text-muted-foreground">
                  <span>{{ person.gender }}</span>
                  <span>•</span>
                  <span>{{ person.ageRange }}岁</span>
                </div>
                <Badge :class="getConfidenceColor(person.confidence)" variant="outline" class="text-xs">
                  {{ (person.confidence * 100).toFixed(1) }}% 置信度
                </Badge>
              </div>
              
              <div class="text-sm text-muted-foreground space-y-1">
                <div class="flex items-center justify-center gap-1">
                  <Camera class="h-4 w-4" />
                  {{ person.imageCount }} 张照片
                </div>
                <div>最近出现: {{ formatDate(person.lastSeen) }}</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>

    <!-- 人物详情对话框 -->
    <Dialog v-model:open="showPersonDialog">
      <DialogContent class="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-full overflow-hidden bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center">
              <div v-if="!selectedPerson?.avatar" class="text-xl">
                {{ selectedPerson?.name.includes('未知') ? '❓' : selectedPerson?.name.charAt(0) }}
              </div>
              <img v-else :src="selectedPerson?.avatar" :alt="selectedPerson?.name" class="w-full h-full object-cover" />
            </div>
            {{ selectedPerson?.name }}
          </DialogTitle>
        </DialogHeader>
        
        <div v-if="selectedPerson" class="space-y-6">
          <!-- 基本信息 -->
          <Card>
            <CardHeader>
              <CardTitle class="text-lg">基本信息</CardTitle>
            </CardHeader>
            <CardContent>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <strong class="text-muted-foreground">关系:</strong>
                  <div class="flex items-center gap-2 mt-1">
                    <span>{{ getRelationshipIcon(selectedPerson.relationship) }}</span>
                    <span>{{ selectedPerson.relationship }}</span>
                  </div>
                </div>
                <div>
                  <strong class="text-muted-foreground">性别年龄:</strong>
                  <p class="mt-1">{{ selectedPerson.gender }}，{{ selectedPerson.ageRange }}岁</p>
                </div>
                <div>
                  <strong class="text-muted-foreground">识别置信度:</strong>
                  <div class="mt-1">
                    <Badge :class="getConfidenceColor(selectedPerson.confidence)" variant="outline">
                      {{ (selectedPerson.confidence * 100).toFixed(1) }}% - {{ getConfidenceLabel(selectedPerson.confidence) }}
                    </Badge>
                  </div>
                </div>
                <div>
                  <strong class="text-muted-foreground">照片数量:</strong>
                  <p class="mt-1">{{ selectedPerson.imageCount }} 张</p>
                </div>
                <div>
                  <strong class="text-muted-foreground">首次出现:</strong>
                  <p class="mt-1">{{ formatDate(selectedPerson.firstAppearance) }}</p>
                </div>
                <div>
                  <strong class="text-muted-foreground">最近出现:</strong>
                  <p class="mt-1">{{ formatDate(selectedPerson.lastSeen) }}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- 最近照片 -->
          <Card>
            <CardHeader>
              <CardTitle class="text-lg">最近照片</CardTitle>
            </CardHeader>
            <CardContent>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div 
                  v-for="image in selectedPerson.images" 
                  :key="image.id"
                  class="aspect-square rounded-lg overflow-hidden bg-gradient-to-br from-primary/20 to-secondary/20 hover:scale-105 transition-transform cursor-pointer"
                >
                  <div class="w-full h-full flex items-center justify-center">
                    <Camera class="h-8 w-8 text-muted-foreground" />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </DialogContent>
    </Dialog>

    <!-- 添加人物对话框 -->
    <Dialog v-model:open="showAddPersonDialog">
      <DialogContent class="max-w-md">
        <DialogHeader>
          <DialogTitle class="flex items-center gap-2">
            <Plus class="h-5 w-5" />
            添加新人物
          </DialogTitle>
        </DialogHeader>
        <div class="space-y-4">
          <div>
            <label class="text-sm font-medium mb-2 block">人物姓名</label>
            <Input 
              v-model="newPersonName" 
              placeholder="输入人物姓名"
              @keyup.enter="confirmAddPerson"
            />
          </div>
          <div class="flex justify-end gap-2">
            <Button variant="outline" @click="showAddPersonDialog = false">
              取消
            </Button>
            <Button @click="confirmAddPerson" :disabled="!newPersonName.trim()">
              确认添加
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  </div>
</template>