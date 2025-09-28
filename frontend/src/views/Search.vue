<script setup lang="ts">
import { ref, computed } from 'vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { useSearchStore } from '@/stores/searchStore'

const searchStore = useSearchStore()
const searchQuery = ref('')
const selectedImageForSearch = ref<File | null>(null)
const imagePreviewUrl = ref<string | null>(null)

// 图像信息对话框相关状态
const showImageInfoDialog = ref(false)
const currentImageInfo = ref<any>(null)
const loadingImageInfo = ref(false)

// 从搜索历史中选择
const selectFromHistory = (query: string) => {
  searchQuery.value = query
  handleSearch()
}

const handleSearch = async () => {
  if (searchQuery.value.trim()) {
    await searchStore.textSearch(searchQuery.value)
  }
}

// 处理图片上传
const handleImageUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (file) {
    selectedImageForSearch.value = file
    imagePreviewUrl.value = URL.createObjectURL(file)
    
    try {
      // 使用上传的图片进行搜索
      await searchStore.imageSearch(file)
    } catch (error) {
      console.error('以图搜图失败:', error)
      alert('以图搜图失败: ' + (error as Error).message)
    }
  }
}

// 处理拖拽上传
const handleDrop = async (event: DragEvent) => {
  event.preventDefault()
  
  if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
    const file = event.dataTransfer.files[0]
    
    // 检查是否为图片文件
    if (file.type.startsWith('image/')) {
      selectedImageForSearch.value = file
      imagePreviewUrl.value = URL.createObjectURL(file)
      
      try {
        // 使用上传的图片进行搜索
        await searchStore.imageSearch(file)
      } catch (error) {
        console.error('以图搜图失败:', error)
        alert('以图搜图失败: ' + (error as Error).message)
      }
    }
  }
}

// 清除图片搜索
const clearImageSearch = () => {
  selectedImageForSearch.value = null
  imagePreviewUrl.value = null
  searchStore.clearResults()
}

      async fetchImageInfo(imagePath: string) {
        this.loadingImageInfo = true;
        try {
          // 使用绝对URL确保请求发送到正确的后端端口
          const response = await fetch('http://localhost:5001/api/image-info', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              imagePath: imagePath
            })
          });
          
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          
          const data = await response.json();
          this.currentImageInfo = data;
        } catch (error) {
          console.error('获取图像信息失败:', error);
          this.currentImageInfo = null; // 确保在错误情况下重置
        } finally {
          this.loadingImageInfo = false;
        }
      },

// 计算搜索历史显示（只显示前5个）
const displayHistory = computed(() => {
  return searchStore.searchHistory.slice(0, 5)
})
</script>

<template>
  <div class="max-w-6xl mx-auto px-4">
    <!-- 搜索框区域 -->
    <div class="mb-12">
      <div class="bg-gradient-to-r from-primary/5 to-secondary/5 p-8 rounded-2xl">
        <div class="max-w-2xl mx-auto">
          <div class="relative">
            <div class="absolute left-4 top-1/2 -translate-y-1/2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <Input 
              v-model="searchQuery" 
              placeholder="输入搜索关键词，例如：海边日落、家庭聚会、猫咪玩耍..."
              class="pl-10 pr-24 py-6 text-lg h-auto shadow-sm"
              @keyup.enter="handleSearch"
            />
            <Button 
              @click="handleSearch" 
              :disabled="searchStore.isLoading"
              class="absolute right-2 top-1/2 -translate-y-1/2 py-5 px-6 text-lg"
            >
              <span v-if="searchStore.isLoading">
                <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                搜索中...
              </span>
              <span v-else>搜索</span>
            </Button>
          </div>
        </div>
        
        <!-- 搜索历史 -->
        <div v-if="searchStore.searchHistory.length > 0" class="mt-6">
          <p class="text-sm text-muted-foreground mb-2 text-center">搜索历史:</p>
          <div class="flex flex-wrap justify-center gap-2">
            <Button
              v-for="query in displayHistory"
              :key="query"
              variant="secondary"
              size="sm"
              @click="selectFromHistory(query)"
            >
              {{ query }}
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- 以图搜图部分 -->
    <div class="mb-12">
      <Card class="border-0 bg-muted/20 backdrop-blur-sm">
        <CardHeader class="text-center">
          <CardTitle>以图搜图</CardTitle>
          <CardDescription>上传图片搜索相似的照片</CardDescription>
        </CardHeader>
        <CardContent>
          <div class="flex flex-col items-center">
            <div class="w-full max-w-md">
              <!-- 拖拽上传区域 -->
              <div 
                class="border-2 border-dashed border-muted-foreground/30 rounded-xl p-8 text-center cursor-pointer hover:bg-accent/20 transition-colors"
                @dragover.prevent
                @drop="handleDrop"
              >
                <div class="flex flex-col items-center justify-center gap-4">
                  <div class="bg-primary/10 p-3 rounded-full">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                    </svg>
                  </div>
                  <div>
                    <p class="font-medium">拖拽图片到这里</p>
                    <p class="text-sm text-muted-foreground mt-1">或点击上传</p>
                  </div>
                  <Input 
                    type="file" 
                    accept="image/*"
                    @change="handleImageUpload"
                    class="hidden"
                    id="image-upload"
                  />
                  <label for="image-upload">
                    <Button variant="secondary" class="mt-2">选择图片</Button>
                  </label>
                </div>
              </div>
              
              <!-- 上传的图片预览 -->
              <div v-if="imagePreviewUrl" class="mt-6 flex flex-col items-center">
                <div class="flex items-center gap-4 mb-4">
                  <p class="text-muted-foreground">上传的图片：</p>
                  <Button 
                    variant="outline" 
                    size="sm"
                    @click="clearImageSearch"
                  >
                    清除
                  </Button>
                </div>
                <div class="border rounded-lg overflow-hidden">
                  <img 
                    :src="imagePreviewUrl" 
                    alt="上传图片预览" 
                    class="max-h-60 object-contain"
                  />
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- 搜索结果区域 -->
    <div v-if="searchStore.searchResults.length > 0" class="mb-8">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold">搜索结果</h2>
        <div class="text-muted-foreground">
          找到 {{ searchStore.searchResults.length }} 张照片
        </div>
      </div>
      
      <!-- 图片网格 -->
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
        <div 
          v-for="result in searchStore.searchResults" 
          :key="result.id" 
          class="group relative rounded-xl overflow-hidden border bg-card/50 backdrop-blur-sm transition-all hover:shadow-lg"
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
          <div class="p-3">
            <div class="text-sm truncate">{{ result.path.split('/').pop() }}</div>
            <div class="flex justify-between items-center mt-1">
              <div class="text-xs text-muted-foreground">
                相似度: {{ (result.similarity * 100).toFixed(1) }}%
              </div>
              <Button 
                variant="outline" 
                size="sm" 
                @click="showImageInfo(result.path)"
                class="text-xs px-2 py-1 h-6"
              >
                向量信息
              </Button>
            </div>
          </div>
          <div class="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-all duration-300 flex items-center justify-center opacity-0 group-hover:opacity-100">
            <Button size="sm" variant="secondary" @click="showImageInfo(result.path)">
              查看
            </Button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div v-else-if="searchStore.isLoading" class="text-center py-16">
      <div class="flex flex-col items-center">
        <div class="animate-pulse mb-4">
          <div class="bg-primary/10 p-4 rounded-full">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
        <h3 class="text-xl font-medium">正在搜索您的照片</h3>
        <p class="text-muted-foreground mt-2">AI正在分析您的请求...</p>
      </div>
    </div>
    
    <!-- 空状态 -->
    <div v-else class="text-center py-16">
      <div class="mb-6">
        <div class="bg-primary/10 p-4 rounded-full w-24 h-24 flex items-center justify-center mx-auto">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>
      <h3 class="text-xl font-medium">输入搜索关键词或上传图片开始搜索</h3>
      <p class="text-muted-foreground mt-2">我们正在等待您的指令</p>
      
      <div class="mt-8">
        <h4 class="font-medium mb-4">快速搜索示例</h4>
        <div class="flex flex-wrap justify-center gap-3">
          <Button 
            variant="outline" 
            @click="searchQuery = '海边日落'; handleSearch()"
          >
            海边日落
          </Button>
          <Button 
            variant="outline" 
            @click="searchQuery = '家庭聚会'; handleSearch()"
          >
            家庭聚会
          </Button>
          <Button 
            variant="outline" 
            @click="searchQuery = '猫咪玩耍'; handleSearch()"
          >
            猫咪玩耍
          </Button>
          <Button 
            variant="outline" 
            @click="searchQuery = '城市夜景'; handleSearch()"
          >
            城市夜景
          </Button>
        </div>
      </div>
    </div>

    <!-- 图像信息对话框 -->
    <Dialog v-model:open="showImageInfoDialog">
      <DialogContent class="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>图像向量信息</DialogTitle>
        </DialogHeader>
        
        <div v-if="loadingImageInfo" class="flex justify-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
        
        <div v-else-if="currentImageInfo && Object.keys(currentImageInfo).length > 0" class="space-y-6">
          <!-- 基本信息 -->
          <div>
            <h3 class="text-lg font-semibold mb-3">基本信息</h3>
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div v-if="currentImageInfo.path"><strong>文件路径:</strong> {{ currentImageInfo.path }}</div>
              <div v-if="currentImageInfo.metadata?.width && currentImageInfo.metadata?.height">
                <strong>尺寸:</strong> {{ currentImageInfo.metadata.width }} × {{ currentImageInfo.metadata.height }}
              </div>
              <div v-if="currentImageInfo.metadata?.format"><strong>格式:</strong> {{ currentImageInfo.metadata.format }}</div>
              <div v-if="currentImageInfo.metadata?.size_bytes">
                <strong>文件大小:</strong> {{ (currentImageInfo.metadata.size_bytes / 1024).toFixed(1) }} KB
              </div>
            </div>
          </div>

          <!-- 特征向量信息 -->
          <div>
            <h3 class="text-lg font-semibold mb-3">特征向量信息</h3>
            <div class="bg-muted/50 p-4 rounded-lg space-y-2 text-sm">
              <div v-if="currentImageInfo.feature_vector_info?.model">
                <strong>模型:</strong> {{ currentImageInfo.feature_vector_info.model }}
              </div>
              <div v-if="currentImageInfo.feature_vector_info?.dimension">
                <strong>向量维度:</strong> {{ currentImageInfo.feature_vector_info.dimension }}
              </div>
              <div v-if="currentImageInfo.feature_vector_info?.vector_norm">
                <strong>向量范数:</strong> {{ currentImageInfo.feature_vector_info.vector_norm.toFixed(6) }}
              </div>
              <div v-if="currentImageInfo.feature_vector_info?.first_10_values && currentImageInfo.feature_vector_info.first_10_values.length > 0">
                <strong>前10个特征值:</strong>
                <div class="mt-2 font-mono text-xs bg-background p-2 rounded border">
                  [{{ currentImageInfo.feature_vector_info.first_10_values.map((v: number) => v.toFixed(4)).join(', ') }}...]
                </div>
              </div>
            </div>
          </div>

          <!-- 可能的文本描述 -->
          <div>
            <h3 class="text-lg font-semibold mb-3">AI识别的可能内容</h3>
            <div class="space-y-2">
              <div v-if="!currentImageInfo.possible_descriptions || currentImageInfo.possible_descriptions.length === 0" class="text-muted-foreground">
                未找到高相似度的描述
              </div>
              <div v-else class="flex flex-wrap gap-2">
                <Badge 
                  v-for="desc in currentImageInfo.possible_descriptions" 
                  :key="desc.description"
                  variant="secondary"
                  class="text-sm"
                >
                  {{ desc.description }} ({{ (desc.similarity * 100).toFixed(1) }}%)
                </Badge>
              </div>
            </div>
          </div>

          <!-- 说明 -->
          <div class="text-xs text-muted-foreground bg-muted/30 p-3 rounded-lg">
            <p><strong>说明:</strong></p>
            <ul class="mt-1 space-y-1 list-disc list-inside">
              <li>特征向量是AI模型将图像转换为数字表示的结果</li>
              <li>向量维度为512，每个数值代表图像的某个特征</li>
              <li>相似的图像会有相似的特征向量</li>
              <li>AI识别内容基于与预定义词汇的相似度计算</li>
            </ul>
          </div>
        </div>
        
        <div v-else class="py-8 text-center text-muted-foreground">
          <p>未能获取图像信息</p>
          <p class="text-sm mt-2">可能的原因：</p>
          <ul class="text-sm list-disc list-inside mt-1 space-y-1">
            <li>图像文件不存在或路径错误</li>
            <li>后端服务未正确响应</li>
            <li>图像格式不受支持</li>
          </ul>
        </div>
      </DialogContent>
    </Dialog>
  </div>
</template>