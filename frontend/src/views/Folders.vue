<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { useImageStore } from '@/stores/imageStore'
import { useSettingStore } from '@/stores/settingStore'
import FolderSelector from '@/components/FolderSelector.vue'
import {
  Folder,
  FolderOpen,
  Loader,
  Check,
  X,
  Clock,
  MapPin,
  Users,
  Image as ImageIcon,
  AlertTriangle,
  Eye,
  Download,
  Upload,
  Settings,
  Home,
  Search,
  Plus,
  Zap,
  Trash,
  Brain
} from 'lucide-vue-next'

const imageStore = useImageStore()
const settingStore = useSettingStore()

// 状态管理
const showAddDialog = ref(false)
const folderPath = ref('')
const isProcessing = ref(false)
const showDeleteDialog = ref(false)
const folderToDelete = ref<any>(null)

// 统计信息
const stats = computed(() => {
  const totalFolders = imageStore.processedFolders.length
  const totalImages = imageStore.processedFolders.reduce((sum, folder) => sum + folder.imageCount, 0)
  const processingFolders = imageStore.processedFolders.filter(f => f.status === 'processing').length
  const completedFolders = imageStore.processedFolders.filter(f => f.status === 'completed').length
  
  return {
    totalFolders,
    totalImages,
    processingFolders,
    completedFolders
  }
})

// 按状态分组的文件夹
const groupedFolders = computed(() => {
  const processing = imageStore.processedFolders.filter(f => f.status === 'processing')
  const completed = imageStore.processedFolders.filter(f => f.status === 'completed')
  const failed = imageStore.processedFolders.filter(f => f.status === 'failed')
  
  return { processing, completed, failed }
})

// 方法
const handleSelectFolder = async () => {
  showAddDialog.value = true
}

const handleFolderSelected = async (path: string) => {
  folderPath.value = path
  await confirmAddFolder()
}

const confirmAddFolder = async () => {
  if (folderPath.value.trim()) {
    isProcessing.value = true
    try {
      await imageStore.addFolder(folderPath.value.trim())
      folderPath.value = ''
      showAddDialog.value = false
    } catch (error) {
      console.error('处理文件夹失败:', error)
      alert('处理文件夹失败: ' + (error as Error).message)
    } finally {
      isProcessing.value = false
    }
  }
}

const handleRefresh = async (folderId: number) => {
  try {
    await imageStore.refreshFolder(folderId)
  } catch (error) {
    console.error('刷新文件夹失败:', error)
    alert('刷新文件夹失败: ' + (error as Error).message)
  }
}

const confirmRemove = (folder: any) => {
  folderToDelete.value = folder
  showDeleteDialog.value = true
}

const handleRemove = async () => {
  if (folderToDelete.value) {
    try {
      await imageStore.removeFolder(folderToDelete.value.id)
      showDeleteDialog.value = false
      folderToDelete.value = null
    } catch (error) {
      console.error('移除文件夹失败:', error)
      alert('移除文件夹失败: ' + (error as Error).message)
    }
  }
}

// 根据文件夹路径获取处理任务信息
const getTaskByPath = (path: string) => {
  for (const taskId in imageStore.processingTasks) {
    if (imageStore.processingTasks[taskId].folderPath === path) {
      return imageStore.processingTasks[taskId]
    }
  }
  return null
}

// 获取状态颜色
const getStatusColor = (status: string) => {
  switch (status) {
    case 'processing': return 'text-blue-600'
    case 'completed': return 'text-green-600'
    case 'failed': return 'text-red-600'
    default: return 'text-gray-600'
  }
}

// 获取状态图标
const getStatusIcon = (status: string) => {
  switch (status) {
    case 'processing': return 'M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15'
    case 'completed': return 'M5 13l4 4L19 7'
    case 'failed': return 'M6 18L18 6M6 6l12 12'
    default: return 'M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z'
  }
}

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 格式化时间
const formatTime = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString('zh-CN')
}

// 将后端模型名称映射到显示名称
const getModelDisplayName = (modelName: string) => {
  const modelMapping = {
    'openai/clip-vit-base-patch32': 'CLIP ViT-B/32',
    'openai/clip-vit-large-patch14': 'CLIP ViT-L/14',
    'OFA-Sys/chinese-clip-vit-base-patch16': 'Chinese CLIP ViT-B/16',
    'sentence-transformers/clip-ViT-B-32-multilingual-v1': 'Multilingual CLIP ViT-B/32',
    'Salesforce/blip-image-captioning-base': 'BLIP Base'
  }
  return modelMapping[modelName] || modelName
}

onMounted(async () => {
  // 获取当前模型信息
  await settingStore.fetchCurrentModel()
})
</script>

<template>
  <div class="min-h-screen bg-white">
    <div class="max-w-6xl mx-auto px-6 py-12">
      <!-- 页面头部 -->
      <div class="mb-12">
        <div class="text-center mb-12">
          <h1 class="text-5xl font-bold text-gray-900 mb-4">
            文件夹管理
          </h1>
          <p class="text-xl text-gray-600">管理和监控你的照片索引库</p>
        </div>

        <!-- 统计概览 -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
          <div class="bg-white border border-gray-200 rounded-lg p-8 text-center">
            <div class="text-4xl font-bold text-gray-900 mb-2">{{ stats.totalFolders }}</div>
            <div class="text-gray-600">总文件夹</div>
          </div>
          <div class="bg-white border border-gray-200 rounded-lg p-8 text-center">
            <div class="text-4xl font-bold text-gray-900 mb-2">{{ stats.totalImages }}</div>
            <div class="text-gray-600">已索引照片</div>
          </div>
          <div class="bg-white border border-gray-200 rounded-lg p-8 text-center">
            <div class="text-4xl font-bold text-gray-900 mb-2">{{ stats.processingFolders }}</div>
            <div class="text-gray-600">处理中</div>
          </div>
          <div class="bg-white border border-gray-200 rounded-lg p-8 text-center">
            <div class="text-4xl font-bold text-gray-900 mb-2">{{ stats.completedFolders }}</div>
            <div class="text-gray-600">已完成</div>
          </div>
        </div>
      </div>

      <!-- 添加文件夹区域 -->
      <div class="mb-12 bg-white border border-gray-200 rounded-lg p-8">
        <div class="text-center">
          <div class="flex items-center justify-center gap-4 mb-6">
            <div class="bg-gray-100 p-3 rounded-lg">
              <Plus class="h-8 w-8 text-gray-600" />
            </div>
            <h2 class="text-3xl font-bold text-gray-900">添加新的照片文件夹</h2>
          </div>
          <p class="text-lg text-gray-600 mb-8">选择包含照片的文件夹，AI将自动提取特征并建立索引</p>
          
          <Button @click="handleSelectFolder" size="lg" class="px-12 py-6 text-lg bg-gray-900 text-white hover:bg-gray-800">
            <FolderOpen class="h-6 w-6 mr-3" />
            选择文件夹
          </Button>
          
          <div class="mt-8 text-center">
            <p class="text-sm text-gray-500 mb-4">支持的图片格式</p>
            <div class="flex flex-wrap justify-center gap-3">
              <Badge variant="outline" class="border-gray-200 text-gray-600">JPG</Badge>
              <Badge variant="outline" class="border-gray-200 text-gray-600">PNG</Badge>
              <Badge variant="outline" class="border-gray-200 text-gray-600">WebP</Badge>
              <Badge variant="outline" class="border-gray-200 text-gray-600">TIFF</Badge>
              <Badge variant="outline" class="border-gray-200 text-gray-600">BMP</Badge>
            </div>
          </div>
        </div>
      </div>

      <!-- 文件夹列表 -->
      <div v-if="imageStore.processedFolders.length > 0" class="space-y-12">
        <!-- 处理中的文件夹 -->
        <div v-if="groupedFolders.processing.length > 0">
          <div class="flex items-center gap-4 mb-8">
            <div class="bg-gray-100 p-3 rounded-lg">
              <Loader class="h-6 w-6 text-gray-600 animate-spin" />
            </div>
            <h2 class="text-3xl font-bold text-gray-900">正在处理</h2>
            <Badge variant="secondary" class="bg-gray-100 text-gray-600">{{ groupedFolders.processing.length }}</Badge>
          </div>
          
          <div class="grid grid-cols-1 gap-8">
            <div 
              v-for="folder in groupedFolders.processing" 
              :key="folder.id"
              class="bg-white border border-gray-200 rounded-lg p-8"
            >
              <div class="flex items-start justify-between">
                <div class="flex items-start gap-6 flex-1">
                  <div class="bg-gray-100 p-4 rounded-lg">
                    <Loader class="h-8 w-8 text-gray-600 animate-spin" />
                  </div>
                  <div class="flex-1">
                    <h3 class="text-2xl font-semibold text-gray-900 mb-3">{{ folder.name }}</h3>
                    <p class="text-gray-500 text-sm mb-6 font-mono break-all">{{ folder.path }}</p>
                    
                    <!-- 处理进度 -->
                    <div class="space-y-4">
                      <div class="flex justify-between text-sm">
                        <span class="text-gray-600">处理进度</span>
                        <span class="font-medium text-gray-900">
                          <span v-if="getTaskByPath(folder.path)">
                            {{ getTaskByPath(folder.path).processed || 0 }} / {{ getTaskByPath(folder.path).total || '扫描中...' }}
                          </span>
                        </span>
                      </div>
                      <Progress 
                        :value="getTaskByPath(folder.path)?.progress || 0" 
                        class="w-full h-2" 
                      />
                      <div class="flex items-center gap-6 text-sm text-gray-500">
                        <div class="flex items-center gap-2">
                          <Clock class="h-4 w-4" />
                          开始时间: {{ formatTime(folder.lastProcessed) }}
                        </div>
                        <div class="flex items-center gap-2">
                          <Zap class="h-4 w-4" />
                          预计剩余: {{ getTaskByPath(folder.path)?.estimatedTime || '计算中...' }}
                        </div>
                        <div class="flex items-center gap-2">
                          <Brain class="h-4 w-4" />
                          使用模型: {{ getModelDisplayName(getTaskByPath(folder.path)?.model || settingStore.currentModel?.name || '未知') }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 已完成的文件夹 -->
        <div v-if="groupedFolders.completed.length > 0">
          <div class="flex items-center gap-4 mb-8">
            <div class="bg-gray-100 p-3 rounded-lg">
              <Check class="h-6 w-6 text-gray-600" />
            </div>
            <h2 class="text-3xl font-bold text-gray-900">已完成索引</h2>
            <Badge variant="secondary" class="bg-gray-100 text-gray-600">{{ groupedFolders.completed.length }}</Badge>
          </div>
          
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div 
              v-for="folder in groupedFolders.completed" 
              :key="folder.id"
              class="bg-white border border-gray-200 rounded-lg p-8 hover:shadow-lg transition-all duration-300 group"
            >
              <div class="flex items-start justify-between">
                <div class="flex items-start gap-6 flex-1">
                  <div class="bg-gray-100 p-4 rounded-lg group-hover:bg-gray-200 transition-colors">
                    <Check class="h-8 w-8 text-gray-600" v-if="folder.status === 'completed'" />
                    <Loader class="h-8 w-8 text-gray-600 animate-spin" v-else-if="folder.status === 'processing'" />
                    <AlertTriangle class="h-8 w-8 text-gray-600" v-else-if="folder.status === 'failed'" />
                    <Folder class="h-8 w-8 text-gray-600" v-else />
                  </div>
                  <div class="flex-1">
                    <h3 class="text-2xl font-semibold text-gray-900 mb-3 group-hover:text-gray-700 transition-colors">{{ folder.name }}</h3>
                    <p class="text-gray-500 text-sm mb-6 font-mono break-all">{{ folder.path }}</p>
                    
                    <div class="grid grid-cols-2 gap-6 mb-6">
                      <div class="flex items-center gap-3 text-sm">
                        <ImageIcon class="h-5 w-5 text-gray-400" />
                        <span class="font-medium text-gray-900">{{ folder.imageCount }}</span>
                        <span class="text-gray-500">张照片</span>
                      </div>
                      <div class="flex items-center gap-3 text-sm">
                        <Clock class="h-5 w-5 text-gray-400" />
                        <span class="text-gray-500">{{ formatTime(folder.lastProcessed) }}</span>
                      </div>
                    </div>
                    
                    <div class="flex items-center gap-3">
                      <Badge variant="outline" class="text-gray-600 border-gray-300 bg-gray-50">
                        <Check class="h-3 w-3 mr-1" />
                        已完成
                      </Badge>
                    </div>
                  </div>
                </div>
                
                <div class="flex flex-col gap-3">
                  <Button 
                    variant="outline" 
                    size="sm"
                    @click="handleRefresh(folder.id)"
                    class="opacity-0 group-hover:opacity-100 transition-opacity border-gray-200 text-gray-700 hover:bg-gray-50"
                  >
                    <Loader class="h-4 w-4 mr-1" />
                    重新索引
                  </Button>
                  <Button 
                    variant="destructive" 
                    size="sm"
                    @click="confirmRemove(folder)"
                    class="opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <Trash class="h-4 w-4 mr-1" />
                    移除
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 失败的文件夹 -->
        <div v-if="groupedFolders.failed.length > 0">
          <div class="flex items-center gap-4 mb-8">
            <div class="bg-gray-100 p-3 rounded-lg">
              <X class="h-6 w-6 text-gray-600" />
            </div>
            <h2 class="text-3xl font-bold text-gray-900">处理失败</h2>
            <Badge variant="destructive" class="bg-red-100 text-red-600">{{ groupedFolders.failed.length }}</Badge>
          </div>
          
          <div class="grid grid-cols-1 gap-8">
            <div 
              v-for="folder in groupedFolders.failed" 
              :key="folder.id"
              class="bg-white border border-gray-200 rounded-lg p-8"
            >
              <div class="flex items-start justify-between">
                <div class="flex items-start gap-6 flex-1">
                  <div class="bg-gray-100 p-4 rounded-lg">
                    <X class="h-8 w-8 text-gray-600" v-if="folder.status === 'failed'" />
                    <Loader class="h-8 w-8 text-gray-600 animate-spin" v-else-if="folder.status === 'processing'" />
                    <Check class="h-8 w-8 text-gray-600" v-else-if="folder.status === 'completed'" />
                    <Folder class="h-8 w-8 text-gray-600" v-else />
                  </div>
                  <div class="flex-1">
                    <h3 class="text-2xl font-semibold text-gray-900 mb-3">{{ folder.name }}</h3>
                    <p class="text-gray-500 text-sm mb-6 font-mono break-all">{{ folder.path }}</p>
                    <div class="bg-red-50 border border-red-200 p-4 rounded-lg mb-6">
                      <p class="text-red-600 text-sm">处理失败，请检查文件夹路径是否正确或重新尝试</p>
                    </div>
                  </div>
                </div>
                
                <div class="flex gap-3">
                  <Button 
                    variant="outline" 
                    size="sm"
                    @click="handleRefresh(folder.id)"
                    class="border-gray-200 text-gray-700 hover:bg-gray-50"
                  >
                    <Loader class="h-4 w-4 mr-1" />
                    重试
                  </Button>
                  <Button 
                    variant="destructive" 
                    size="sm"
                    @click="confirmRemove(folder)"
                  >
                    <Trash class="h-4 w-4 mr-1" />
                    移除
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="text-center py-20">
        <div class="max-w-md mx-auto">
          <div class="bg-gray-100 rounded-full w-32 h-32 flex items-center justify-center mx-auto mb-8">
            <Folder class="h-16 w-16 text-gray-400" />
          </div>
          <h3 class="text-3xl font-semibold text-gray-900 mb-4">还没有添加任何文件夹</h3>
          <p class="text-gray-600 mb-8">添加包含照片的文件夹，开始构建你的智能相册索引</p>
          <Button @click="handleSelectFolder" size="lg" class="px-8 bg-gray-900 text-white hover:bg-gray-800">
            <Plus class="h-5 w-5 mr-2" />
            添加第一个文件夹
          </Button>
        </div>
      </div>
    </div>

    <!-- 新的文件夹选择器 -->
    <FolderSelector 
      v-model:open="showAddDialog"
      @folder-selected="handleFolderSelected"
    />

    <!-- 删除确认对话框 -->
    <Dialog v-model:open="showDeleteDialog">
      <DialogContent class="max-w-md">
        <DialogHeader>
          <DialogTitle class="flex items-center gap-2 text-red-600">
            <AlertTriangle class="h-5 w-5" />
            确认移除文件夹
          </DialogTitle>
        </DialogHeader>
        <div class="space-y-4">
          <div class="bg-red-500/10 p-4 rounded-lg">
            <p class="text-sm">
              确定要移除文件夹 <strong>{{ folderToDelete?.name }}</strong> 吗？
            </p>
            <p class="text-xs text-muted-foreground mt-2">
              这将删除该文件夹的所有索引数据，但不会删除原始照片文件。
            </p>
          </div>
          <div class="flex justify-end gap-2">
            <Button variant="outline" @click="showDeleteDialog = false">
              取消
            </Button>
            <Button variant="destructive" @click="handleRemove">
              确认移除
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  </div>
</template>