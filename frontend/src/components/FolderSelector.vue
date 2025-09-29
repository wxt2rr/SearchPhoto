<script setup lang="ts">
import { ref, computed } from 'vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsItem } from '@/components/ui/tabs'

// Props
interface Props {
  open: boolean
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:open': [value: boolean]
  'folder-selected': [path: string]
}>()

// 状态管理
const folderPath = ref('')
const dragActive = ref(false)
const selectedMethod = ref<'browse' | 'drag' | 'input'>('browse')
const isValidating = ref(false)
const validationError = ref('')

// 计算属性
const isOpen = computed({
  get: () => props.open,
  set: (value) => emit('update:open', value)
})

const isValidPath = computed(() => {
  return folderPath.value.trim().length > 0 && !validationError.value
})

// 常见文件夹建议
const commonFolders = [
  { name: '图片文件夹', path: '/Users/用户名/Pictures', icon: '🖼️' },
  { name: '桌面', path: '/Users/用户名/Desktop', icon: '🖥️' },
  { name: '下载文件夹', path: '/Users/用户名/Downloads', icon: '📥' },
  { name: '文档', path: '/Users/用户名/Documents', icon: '📁' }
]

// 方法
const handleBrowseFolder = async () => {
  try {
    // 在实际应用中，这里会调用系统文件选择器
    // 目前模拟文件选择器的行为
    const mockPath = '/Users/username/Pictures/MyPhotos'
    folderPath.value = mockPath
    selectedMethod.value = 'browse'
    await validatePath(mockPath)
  } catch (error) {
    console.error('选择文件夹失败:', error)
  }
}

const handleDragOver = (e: DragEvent) => {
  e.preventDefault()
  dragActive.value = true
}

const handleDragLeave = (e: DragEvent) => {
  e.preventDefault()
  dragActive.value = false
}

const handleDrop = async (e: DragEvent) => {
  e.preventDefault()
  dragActive.value = false
  
  const items = e.dataTransfer?.items
  if (items) {
    for (let i = 0; i < items.length; i++) {
      const item = items[i]
      if (item.kind === 'file') {
        const entry = item.webkitGetAsEntry()
        if (entry?.isDirectory) {
          folderPath.value = entry.fullPath
          selectedMethod.value = 'drag'
          await validatePath(entry.fullPath)
          break
        }
      }
    }
  }
}

const handlePathInput = async (value: string) => {
  folderPath.value = value
  selectedMethod.value = 'input'
  if (value.trim()) {
    await validatePath(value)
  } else {
    validationError.value = ''
  }
}

const validatePath = async (path: string) => {
  isValidating.value = true
  validationError.value = ''
  
  try {
    // 模拟路径验证
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 简单的路径格式验证
    if (!path.includes('/') && !path.includes('\\')) {
      validationError.value = '请输入有效的文件夹路径'
      return
    }
    
    // 模拟检查文件夹是否存在和包含图片
    const hasImages = Math.random() > 0.3 // 70% 概率包含图片
    if (!hasImages) {
      validationError.value = '该文件夹中未找到支持的图片文件'
      return
    }
    
  } catch (error) {
    validationError.value = '无法访问该文件夹，请检查路径是否正确'
  } finally {
    isValidating.value = false
  }
}

const handleConfirm = () => {
  if (isValidPath.value) {
    emit('folder-selected', folderPath.value.trim())
    handleClose()
  }
}

const handleClose = () => {
  isOpen.value = false
  // 重置状态
  setTimeout(() => {
    folderPath.value = ''
    validationError.value = ''
    selectedMethod.value = 'browse'
  }, 300)
}

const selectCommonFolder = async (folder: typeof commonFolders[0]) => {
  folderPath.value = folder.path
  selectedMethod.value = 'browse'
  await validatePath(folder.path)
}
</script>

<template>
  <Dialog v-model:open="isOpen">
    <DialogContent class="max-w-2xl max-h-[90vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle class="flex items-center gap-3 text-2xl">
          <div class="bg-primary/10 p-2 rounded-lg">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
            </svg>
          </div>
          选择照片文件夹
        </DialogTitle>
      </DialogHeader>

      <div class="space-y-6">
        <!-- 选择方式标签页 -->
        <Tabs v-model:modelValue="selectedMethod" :defaultValue="selectedMethod" class="w-full">
          <TabsList class="grid w-full grid-cols-3">
            <TabsItem value="browse" class="flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
              </svg>
              浏览选择
            </TabsItem>
            <TabsItem value="drag" class="flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
              </svg>
              拖拽上传
            </TabsItem>
            <TabsItem value="input" class="flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              手动输入
            </TabsItem>
          </TabsList>

          <!-- 浏览选择 -->
          <TabsContent value="browse" class="space-y-4">
            <Card class="border-dashed border-2 border-primary/20 bg-primary/5">
              <CardContent class="p-8 text-center">
                <div class="mb-4">
                  <div class="bg-primary/10 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                    </svg>
                  </div>
                  <h3 class="text-lg font-semibold mb-2">选择包含照片的文件夹</h3>
                  <p class="text-muted-foreground mb-6">点击下方按钮打开系统文件夹选择器</p>
                </div>
                
                <Button @click="handleBrowseFolder" size="lg" class="px-8">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                  </svg>
                  浏览文件夹
                </Button>
              </CardContent>
            </Card>

            <!-- 常用文件夹快捷选择 -->
            <div>
              <h4 class="text-sm font-medium mb-3 text-muted-foreground">常用位置</h4>
              <div class="grid grid-cols-2 gap-3">
                <Button
                  v-for="folder in commonFolders"
                  :key="folder.path"
                  variant="outline"
                  class="justify-start h-auto p-4"
                  @click="selectCommonFolder(folder)"
                >
                  <div class="flex items-center gap-3">
                    <span class="text-xl">{{ folder.icon }}</span>
                    <div class="text-left">
                      <div class="font-medium">{{ folder.name }}</div>
                      <div class="text-xs text-muted-foreground">{{ folder.path }}</div>
                    </div>
                  </div>
                </Button>
              </div>
            </div>
          </TabsContent>

          <!-- 拖拽上传 -->
          <TabsContent value="drag" class="space-y-4">
            <div
              class="border-2 border-dashed rounded-lg p-12 text-center transition-all duration-200"
              :class="dragActive 
                ? 'border-primary bg-primary/10 scale-105' 
                : 'border-muted-foreground/25 hover:border-primary/50 hover:bg-primary/5'"
              @dragover="handleDragOver"
              @dragleave="handleDragLeave"
              @drop="handleDrop"
            >
              <div class="mb-4">
                <div 
                  class="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 transition-all duration-200"
                  :class="dragActive ? 'bg-primary/20' : 'bg-muted/50'"
                >
                  <svg 
                    xmlns="http://www.w3.org/2000/svg" 
                    class="h-8 w-8 transition-all duration-200" 
                    :class="dragActive ? 'text-primary' : 'text-muted-foreground'"
                    fill="none" 
                    viewBox="0 0 24 24" 
                    stroke="currentColor"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
                  </svg>
                </div>
                <h3 class="text-lg font-semibold mb-2">
                  {{ dragActive ? '松开鼠标完成选择' : '拖拽文件夹到这里' }}
                </h3>
                <p class="text-muted-foreground">
                  {{ dragActive ? '即将添加文件夹到索引库' : '从文件管理器中拖拽包含照片的文件夹' }}
                </p>
              </div>
            </div>
          </TabsContent>

          <!-- 手动输入 -->
          <TabsContent value="input" class="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle class="text-lg">输入文件夹路径</CardTitle>
                <CardDescription>
                  如果你知道确切的文件夹路径，可以直接输入
                </CardDescription>
              </CardHeader>
              <CardContent class="space-y-4">
                <div>
                  <Input
                    :value="folderPath"
                    @input="handlePathInput($event.target.value)"
                    placeholder="例如: /Users/username/Pictures/MyPhotos"
                    class="font-mono"
                  />
                  <div class="flex items-center gap-2 mt-2">
                    <div v-if="isValidating" class="flex items-center gap-2 text-sm text-muted-foreground">
                      <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      验证路径中...
                    </div>
                    <div v-else-if="folderPath && !validationError" class="flex items-center gap-2 text-sm text-green-600">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                      </svg>
                      路径有效
                    </div>
                  </div>
                </div>

                <!-- 路径格式提示 -->
                <Alert>
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <AlertDescription>
                    <strong>路径格式示例:</strong><br/>
                    • macOS: <code>/Users/用户名/Pictures</code><br/>
                    • Windows: <code>C:\Users\用户名\Pictures</code><br/>
                    • Linux: <code>/home/用户名/Pictures</code>
                  </AlertDescription>
                </Alert>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        <!-- 错误提示 -->
        <Alert v-if="validationError" variant="destructive">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <AlertDescription>{{ validationError }}</AlertDescription>
        </Alert>

        <!-- 选中的路径显示 -->
        <Card v-if="folderPath && !validationError" class="bg-green-50 border-green-200">
          <CardContent class="p-4">
            <div class="flex items-start gap-3">
              <div class="bg-green-100 p-2 rounded-lg">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                </svg>
              </div>
              <div class="flex-1">
                <h4 class="font-medium text-green-800 mb-1">已选择文件夹</h4>
                <p class="text-sm font-mono text-green-700 break-all">{{ folderPath }}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- 支持的文件格式 -->
        <div class="text-center">
          <p class="text-sm text-muted-foreground mb-3">支持的图片格式</p>
          <div class="flex flex-wrap justify-center gap-2">
            <Badge variant="outline">JPG</Badge>
            <Badge variant="outline">JPEG</Badge>
            <Badge variant="outline">PNG</Badge>
            <Badge variant="outline">WebP</Badge>
            <Badge variant="outline">TIFF</Badge>
            <Badge variant="outline">BMP</Badge>
            <Badge variant="outline">GIF</Badge>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="flex justify-end gap-3 pt-4 border-t">
          <Button variant="outline" @click="handleClose">
            取消
          </Button>
          <Button 
            @click="handleConfirm" 
            :disabled="!isValidPath || isValidating"
            class="px-8"
          >
            <span v-if="isValidating" class="flex items-center">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              验证中...
            </span>
            <span v-else class="flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              确认添加
            </span>
          </Button>
        </div>
      </div>
    </DialogContent>
  </Dialog>
</template>