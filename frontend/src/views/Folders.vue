<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { useImageStore } from '@/stores/imageStore'
import FolderSelector from '@/components/FolderSelector.vue'

const imageStore = useImageStore()

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

onMounted(() => {
  // 初始化
})
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
    <div class="max-w-7xl mx-auto px-4 py-8">
      <!-- 页面头部 -->
      <div class="mb-8">
        <div class="text-center mb-8">
          <h1 class="text-4xl font-bold tracking-tight mb-4">
            <span class="bg-clip-text text-transparent bg-gradient-to-r from-foreground via-primary to-secondary">
              文件夹管理
            </span>
          </h1>
          <p class="text-xl text-muted-foreground">管理和监控你的照片索引库</p>
        </div>

        <!-- 统计概览 -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card class="border-0 bg-gradient-to-br from-primary/10 to-primary/5 backdrop-blur-sm">
            <CardContent class="p-6 text-center">
              <div class="text-3xl font-bold text-primary mb-2">{{ stats.totalFolders }}</div>
              <div class="text-muted-foreground">总文件夹</div>
            </CardContent>
          </Card>
          <Card class="border-0 bg-gradient-to-br from-secondary/10 to-secondary/5 backdrop-blur-sm">
            <CardContent class="p-6 text-center">
              <div class="text-3xl font-bold text-secondary mb-2">{{ stats.totalImages }}</div>
              <div class="text-muted-foreground">已索引照片</div>
            </CardContent>
          </Card>
          <Card class="border-0 bg-gradient-to-br from-blue-500/10 to-blue-500/5 backdrop-blur-sm">
            <CardContent class="p-6 text-center">
              <div class="text-3xl font-bold text-blue-600 mb-2">{{ stats.processingFolders }}</div>
              <div class="text-muted-foreground">处理中</div>
            </CardContent>
          </Card>
          <Card class="border-0 bg-gradient-to-br from-green-500/10 to-green-500/5 backdrop-blur-sm">
            <CardContent class="p-6 text-center">
              <div class="text-3xl font-bold text-green-600 mb-2">{{ stats.completedFolders }}</div>
              <div class="text-muted-foreground">已完成</div>
            </CardContent>
          </Card>
        </div>
      </div>

      <!-- 添加文件夹区域 -->
      <Card class="mb-8 border-0 shadow-xl bg-card/80 backdrop-blur-xl">
        <CardHeader class="text-center">
          <CardTitle class="text-2xl flex items-center justify-center gap-3">
            <div class="bg-primary/10 p-2 rounded-lg">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            </div>
            添加新的照片文件夹
          </CardTitle>
          <CardDescription class="text-lg">选择包含照片的文件夹，AI将自动提取特征并建立索引</CardDescription>
        </CardHeader>
        <CardContent>
          <div class="flex flex-col items-center">
            <Button @click="handleSelectFolder" size="lg" class="px-12 py-6 text-lg">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
              </svg>
              选择文件夹
            </Button>
            <div class="mt-6 text-center">
              <p class="text-sm text-muted-foreground mb-2">支持的图片格式</p>
              <div class="flex flex-wrap justify-center gap-2">
                <Badge variant="outline">JPG</Badge>
                <Badge variant="outline">PNG</Badge>
                <Badge variant="outline">WebP</Badge>
                <Badge variant="outline">TIFF</Badge>
                <Badge variant="outline">BMP</Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- 文件夹列表 -->
      <div v-if="imageStore.processedFolders.length > 0" class="space-y-8">
        <!-- 处理中的文件夹 -->
        <div v-if="groupedFolders.processing.length > 0">
          <div class="flex items-center gap-3 mb-6">
            <div class="bg-blue-500/10 p-2 rounded-lg">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-600 animate-spin" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </div>
            <h2 class="text-2xl font-bold text-blue-600">正在处理</h2>
            <Badge variant="secondary">{{ groupedFolders.processing.length }}</Badge>
          </div>
          
          <div class="grid grid-cols-1 gap-6">
            <Card 
              v-for="folder in groupedFolders.processing" 
              :key="folder.id"
              class="border-0 bg-gradient-to-r from-blue-500/5 to-blue-500/10 backdrop-blur-sm"
            >
              <CardContent class="p-6">
                <div class="flex items-start justify-between">
                  <div class="flex items-start gap-4 flex-1">
                    <div class="bg-blue-500/10 p-3 rounded-xl">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-blue-600 animate-spin" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="getStatusIcon(folder.status)" />
                      </svg>
                    </div>
                    <div class="flex-1">
                      <h3 class="text-xl font-semibold mb-2">{{ folder.name }}</h3>
                      <p class="text-muted-foreground text-sm mb-4 font-mono break-all">{{ folder.path }}</p>
                      
                      <!-- 处理进度 -->
                      <div class="space-y-3">
                        <div class="flex justify-between text-sm">
                          <span class="text-muted-foreground">处理进度</span>
                          <span class="font-medium">
                            <span v-if="getTaskByPath(folder.path)">
                              {{ getTaskByPath(folder.path).processed || 0 }} / {{ getTaskByPath(folder.path).total || '扫描中...' }}
                            </span>
                          </span>
                        </div>
                        <Progress 
                          :value="getTaskByPath(folder.path)?.progress || 0" 
                          class="w-full h-2" 
                        />
                        <div class="flex items-center gap-4 text-sm text-muted-foreground">
                          <div class="flex items-center gap-1">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            开始时间: {{ formatTime(folder.lastProcessed) }}
                          </div>
                          <div class="flex items-center gap-1">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg>
                            预计剩余: {{ getTaskByPath(folder.path)?.estimatedTime || '计算中...' }}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        <!-- 已完成的文件夹 -->
        <div v-if="groupedFolders.completed.length > 0">
          <div class="flex items-center gap-3 mb-6">
            <div class="bg-green-500/10 p-2 rounded-lg">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 class="text-2xl font-bold text-green-600">已完成索引</h2>
            <Badge variant="secondary">{{ groupedFolders.completed.length }}</Badge>
          </div>
          
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card 
              v-for="folder in groupedFolders.completed" 
              :key="folder.id"
              class="border-0 bg-card/50 backdrop-blur-sm hover:shadow-xl transition-all duration-300 group"
            >
              <CardContent class="p-6">
                <div class="flex items-start justify-between">
                  <div class="flex items-start gap-4 flex-1">
                    <div class="bg-green-500/10 p-3 rounded-xl group-hover:bg-green-500/20 transition-colors">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="getStatusIcon(folder.status)" />
                      </svg>
                    </div>
                    <div class="flex-1">
                      <h3 class="text-lg font-semibold mb-2 group-hover:text-primary transition-colors">{{ folder.name }}</h3>
                      <p class="text-muted-foreground text-sm mb-4 font-mono break-all">{{ folder.path }}</p>
                      
                      <div class="grid grid-cols-2 gap-4 mb-4">
                        <div class="flex items-center gap-2 text-sm">
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          </svg>
                          <span class="font-medium">{{ folder.imageCount }}</span>
                          <span class="text-muted-foreground">张照片</span>
                        </div>
                        <div class="flex items-center gap-2 text-sm">
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <span class="text-muted-foreground">{{ formatTime(folder.lastProcessed) }}</span>
                        </div>
                      </div>
                      
                      <div class="flex items-center gap-2">
                        <Badge variant="outline" class="text-green-600 border-green-600/20">
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                          </svg>
                          已完成
                        </Badge>
                      </div>
                    </div>
                  </div>
                  
                  <div class="flex flex-col gap-2">
                    <Button 
                      variant="outline" 
                      size="sm"
                      @click="handleRefresh(folder.id)"
                      class="opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                      重新索引
                    </Button>
                    <Button 
                      variant="destructive" 
                      size="sm"
                      @click="confirmRemove(folder)"
                      class="opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                      移除
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        <!-- 失败的文件夹 -->
        <div v-if="groupedFolders.failed.length > 0">
          <div class="flex items-center gap-3 mb-6">
            <div class="bg-red-500/10 p-2 rounded-lg">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h2 class="text-2xl font-bold text-red-600">处理失败</h2>
            <Badge variant="destructive">{{ groupedFolders.failed.length }}</Badge>
          </div>
          
          <div class="grid grid-cols-1 gap-6">
            <Card 
              v-for="folder in groupedFolders.failed" 
              :key="folder.id"
              class="border-0 bg-gradient-to-r from-red-500/5 to-red-500/10 backdrop-blur-sm"
            >
              <CardContent class="p-6">
                <div class="flex items-start justify-between">
                  <div class="flex items-start gap-4 flex-1">
                    <div class="bg-red-500/10 p-3 rounded-xl">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="getStatusIcon(folder.status)" />
                      </svg>
                    </div>
                    <div class="flex-1">
                      <h3 class="text-xl font-semibold mb-2">{{ folder.name }}</h3>
                      <p class="text-muted-foreground text-sm mb-4 font-mono break-all">{{ folder.path }}</p>
                      <div class="bg-red-500/10 p-3 rounded-lg mb-4">
                        <p class="text-red-600 text-sm">处理失败，请检查文件夹路径是否正确或重新尝试</p>
                      </div>
                    </div>
                  </div>
                  
                  <div class="flex gap-2">
                    <Button 
                      variant="outline" 
                      size="sm"
                      @click="handleRefresh(folder.id)"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                      重试
                    </Button>
                    <Button 
                      variant="destructive" 
                      size="sm"
                      @click="confirmRemove(folder)"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                      移除
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="text-center py-16">
        <div class="max-w-md mx-auto">
          <div class="bg-muted/50 rounded-full w-32 h-32 flex items-center justify-center mx-auto mb-8">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
            </svg>
          </div>
          <h3 class="text-2xl font-semibold mb-4">还没有添加任何文件夹</h3>
          <p class="text-muted-foreground mb-8">添加包含照片的文件夹，开始构建你的智能相册索引</p>
          <Button @click="handleSelectFolder" size="lg" class="px-8">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
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
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
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