<script setup lang="ts">
import { ref } from 'vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { useImageStore } from '@/stores/imageStore'

const imageStore = useImageStore()

const handleSelectFolder = async () => {
  // 在实际的桌面应用中，这里会打开系统文件夹选择对话框
  // 现在我们模拟一个路径输入功能
  const folderPath = prompt('请输入文件夹路径 (在桌面应用中会打开系统对话框):')
  
  if (folderPath) {
    try {
      await imageStore.addFolder(folderPath)
    } catch (error) {
      console.error('处理文件夹失败:', error)
      alert('处理文件夹失败: ' + (error as Error).message)
    }
  }
}

const handleRefresh = (folderId: number) => {
  console.log(`刷新文件夹 ${folderId}`)
  imageStore.refreshFolder(folderId)
  alert(`刷新功能将在后续实现，文件夹ID: ${folderId}`)
}

const handleRemove = (folderId: number) => {
  console.log(`移除文件夹 ${folderId}`)
  imageStore.removeFolder(folderId)
  alert(`移除功能将在后续实现，文件夹ID: ${folderId}`)
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
</script>

<template>
  <div class="max-w-4xl mx-auto px-4">
    <!-- 添加文件夹卡片 -->
    <Card class="mb-8 border-0 bg-gradient-to-r from-primary/5 to-secondary/5 backdrop-blur-sm">
      <CardHeader class="text-center">
        <CardTitle class="text-2xl">添加照片文件夹</CardTitle>
        <CardDescription>选择包含照片的文件夹进行索引处理</CardDescription>
      </CardHeader>
      <CardContent>
        <div class="flex flex-col items-center">
          <Button @click="handleSelectFolder" class="w-full max-w-sm py-6 text-lg">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
            </svg>
            选择文件夹
          </Button>
          <p class="text-sm text-muted-foreground mt-4 text-center">
            选择文件夹后，系统将自动扫描并索引照片
          </p>
        </div>
      </CardContent>
    </Card>

    <!-- 文件夹列表（包含处理中的和已完成的） -->
    <Card class="border-0 bg-card/30 backdrop-blur-sm">
      <CardHeader>
        <CardTitle class="text-2xl">文件夹管理</CardTitle>
        <CardDescription>管理已索引的照片文件夹</CardDescription>
      </CardHeader>
      <CardContent>
        <div v-if="imageStore.processedFolders.length > 0" class="space-y-6">
          <div 
            v-for="folder in imageStore.processedFolders" 
            :key="folder.id" 
            class="flex flex-col sm:flex-row sm:items-center justify-between p-5 border rounded-xl bg-accent/30 backdrop-blur-sm transition-all hover:shadow-md"
          >
            <div class="flex items-start gap-4 mb-4 sm:mb-0">
              <div class="bg-primary/10 p-3 rounded-lg">
                <svg 
                  v-if="folder.status === 'processing'" 
                  xmlns="http://www.w3.org/2000/svg" 
                  class="h-6 w-6 text-primary animate-spin" 
                  fill="none" 
                  viewBox="0 0 24 24" 
                  stroke="currentColor"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <svg 
                  v-else 
                  xmlns="http://www.w3.org/2000/svg" 
                  class="h-6 w-6 text-primary" 
                  fill="none" 
                  viewBox="0 0 24 24" 
                  stroke="currentColor"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                </svg>
              </div>
              <div class="flex-1">
                <h3 class="font-semibold text-lg">{{ folder.name }}</h3>
                <p class="text-sm text-muted-foreground break-all mt-1">{{ folder.path }}</p>
                
                <!-- 处理进度显示 -->
                <div v-if="folder.status === 'processing'" class="mt-3">
                  <div class="flex justify-between text-sm mb-1">
                    <span class="text-muted-foreground">处理进度</span>
                    <span class="font-medium">
                      <span v-if="getTaskByPath(folder.path)">
                        {{ getTaskByPath(folder.path).processed || 0 }} / {{ getTaskByPath(folder.path).total || '未知' }}
                      </span>
                    </span>
                  </div>
                  <Progress 
                    :value="getTaskByPath(folder.path)?.progress || 0" 
                    class="w-full" 
                  />
                </div>
                
                <div class="flex flex-wrap items-center gap-4 mt-3">
                  <div class="flex items-center text-sm text-muted-foreground">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    {{ folder.imageCount }} 张照片
                  </div>
                  <div class="flex items-center text-sm text-muted-foreground">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    最后处理: {{ folder.lastProcessed }}
                  </div>
                  <Badge :variant="folder.status === 'processing' ? 'default' : 'secondary'" class="capitalize">
                    {{ folder.status === 'processing' ? '处理中' : '已完成' }}
                  </Badge>
                </div>
              </div>
            </div>
            <div class="flex gap-2">
              <Button 
                variant="outline" 
                size="sm"
                :disabled="folder.status === 'processing'"
                @click="handleRefresh(folder.id)"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                刷新
              </Button>
              <Button 
                variant="destructive" 
                size="sm"
                :disabled="folder.status === 'processing'"
                @click="handleRemove(folder.id)"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                移除
              </Button>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-12">
          <div class="mx-auto bg-muted w-16 h-16 rounded-full flex items-center justify-center mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
            </svg>
          </div>
          <h3 class="text-lg font-medium">还没有处理任何文件夹</h3>
          <p class="text-muted-foreground mt-1">点击上方按钮选择一个包含照片的文件夹开始索引</p>
        </div>
      </CardContent>
    </Card>
  </div>
</template>