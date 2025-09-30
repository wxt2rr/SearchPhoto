<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useSettingStore } from '@/stores/settingStore'

const settingStore = useSettingStore()
const message = ref('')
const messageType = ref<'success' | 'error' | 'warning'>('success')

onMounted(() => {
  settingStore.initialize()
})

const showMessage = (text: string, type: 'success' | 'error' | 'warning' = 'success') => {
  message.value = text
  messageType.value = type
  setTimeout(() => {
    message.value = ''
  }, 3000)
}

const handleModelChange = async (modelId: string) => {
  if (settingStore.isModelSwitching) {
    showMessage('模型正在切换中，请稍候...', 'warning')
    return
  }
  
  try {
    await settingStore.setSelectedModel(modelId)
    showMessage('模型切换成功', 'success')
  } catch (error) {
    showMessage('模型切换失败，请重试', 'error')
    console.error('模型切换错误:', error)
  }
}

// 模型选项
const modelOptions = [
  {
    id: 'clip-vit-base-patch32',
    name: 'CLIP ViT-B/32',
    description: '平衡性能与速度的通用模型',
    features: [
      '适合大多数图片类型',
      '处理速度快',
      '内存占用适中',
      '良好的通用性'
    ],
    useCases: [
      '日常照片搜索',
      '快速批量处理',
      '一般用途推荐'
    ]
  },
  {
    id: 'clip-vit-large-patch14',
    name: 'CLIP ViT-L/14',
    description: '更高精度的大型模型',
    features: [
      '更高的准确性',
      '更强的细节识别能力',
      '更大的模型容量',
      '更好的复杂场景理解'
    ],
    useCases: [
      '专业摄影分析',
      '高精度搜索需求',
      '复杂场景理解',
      '高质量内容生成'
    ]
  },
  {
    id: 'chinese-clip-vit-base-patch16',
    name: 'Chinese CLIP ViT-B/16',
    description: '专为中文优化的多模态模型',
    features: [
      '中文语义理解优化',
      '中文文本搜索增强',
      '本土化场景识别',
      '中文描述生成'
    ],
    useCases: [
      '中文描述搜索',
      '中文场景理解',
      '本地化内容识别',
      '中文智能标注'
    ]
  },
  {
    id: 'multilingual-clip-vit-base-patch32',
    name: 'Multilingual CLIP ViT-B/32',
    description: '支持多语言的跨语言视觉模型',
    features: [
      '多语言文本支持',
      '跨语言语义对齐',
      '国际化场景识别',
      '多语言描述理解'
    ],
    useCases: [
      '多语言搜索',
      '跨语言内容理解',
      '国际化应用场景',
      '多语言标注'
    ]
  },
  {
    id: 'blip-base',
    name: 'BLIP Base',
    description: '结合视觉与语言理解的模型',
    features: [
      '强大的图文理解能力',
      '优秀的描述生成',
      '多模态融合处理',
      '自然语言交互'
    ],
    useCases: [
      '图像内容深度分析',
      '自动生成图片描述',
      '故事创作辅助',
      '智能相册分类'
    ]
  }
]
</script>

<template>
  <div class="space-y-6">
    <!-- 消息提示 -->
    <div 
      v-if="message" 
      class="p-4 rounded-lg border"
      :class="{
        'bg-green-50 border-green-200 text-green-800': messageType === 'success',
        'bg-red-50 border-red-200 text-red-800': messageType === 'error',
        'bg-yellow-50 border-yellow-200 text-yellow-800': messageType === 'warning'
      }"
    >
      {{ message }}
    </div>

    <div>
      <h1 class="text-3xl font-bold">设置</h1>
      <p class="text-muted-foreground">配置系统偏好和模型选择</p>
    </div>

    <Card>
      <CardHeader>
        <CardTitle>AI模型选择</CardTitle>
        <CardDescription>选择用于图片分析和搜索的AI模型</CardDescription>
      </CardHeader>
      <CardContent class="space-y-6">
        <div class="space-y-4">
          <div 
            v-for="model in modelOptions" 
            :key="model.id"
            class="border rounded-lg p-4 hover:bg-accent transition-colors"
            :class="{ 'border-primary bg-primary/5': settingStore.selectedModel === model.id }"
          >
            <div class="flex items-start gap-4">
              <div class="flex-1">
                <div class="flex items-center gap-2">
                  <h3 class="font-semibold">{{ model.name }}</h3>
                  <span 
                    v-if="settingStore.selectedModel === model.id"
                    class="text-xs bg-primary text-primary-foreground px-2 py-1 rounded-full"
                  >
                    当前使用
                  </span>
                </div>
                <p class="text-sm text-muted-foreground mt-1">{{ model.description }}</p>
                
                <div class="mt-3 grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h4 class="text-sm font-medium mb-2">特点：</h4>
                    <ul class="text-sm space-y-1">
                      <li 
                        v-for="(feature, index) in model.features" 
                        :key="index"
                        class="flex items-start gap-2"
                      >
                        <div class="w-1.5 h-1.5 rounded-full bg-primary mt-1.5 flex-shrink-0"></div>
                        <span>{{ feature }}</span>
                      </li>
                    </ul>
                  </div>
                  
                  <div>
                    <h4 class="text-sm font-medium mb-2">适用场景：</h4>
                    <ul class="text-sm space-y-1">
                      <li 
                        v-for="(useCase, index) in model.useCases" 
                        :key="index"
                        class="flex items-start gap-2"
                      >
                        <div class="w-1.5 h-1.5 rounded-full bg-secondary mt-1.5 flex-shrink-0"></div>
                        <span>{{ useCase }}</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
              
              <Button 
                @click="handleModelChange(model.id)"
                variant="outline"
                :disabled="settingStore.isModelSwitching"
                :class="{ 'bg-primary text-primary-foreground hover:bg-primary/90': settingStore.selectedModel === model.id }"
              >
                <span v-if="settingStore.isModelSwitching && settingStore.selectedModel !== model.id" class="flex items-center gap-2">
                  <div class="w-4 h-4 border-2 border-gray-300 border-t-primary rounded-full animate-spin"></div>
                  切换中...
                </span>
                <span v-else>
                  {{ settingStore.selectedModel === model.id ? '使用中' : '选择' }}
                </span>
              </Button>
            </div>
          </div>
        </div>
        
        <div class="pt-4 border-t">
          <h3 class="font-medium mb-2">当前选择的模型：</h3>
          <div class="text-sm p-3 bg-muted rounded-lg">
            <div v-if="settingStore.isModelSwitching" class="flex items-center gap-2 text-primary">
              <div class="w-4 h-4 border-2 border-gray-300 border-t-primary rounded-full animate-spin"></div>
              <span>正在切换模型...</span>
              <div v-if="settingStore.rebuildProgress > 0" class="ml-2">
                (重建进度: {{ settingStore.rebuildProgress }}%)
              </div>
            </div>
            <span v-else-if="settingStore.selectedModel">
              {{
                modelOptions.find(m => m.id === settingStore.selectedModel)?.name || 
                settingStore.selectedModel
              }}
            </span>
            <span v-else class="text-muted-foreground">尚未选择模型</span>
          </div>
        </div>
      </CardContent>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle>其他设置</CardTitle>
        <CardDescription>系统其他配置选项</CardDescription>
      </CardHeader>
      <CardContent class="space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="font-medium">启用GPU加速</h3>
            <p class="text-sm text-muted-foreground">使用GPU提升处理速度（如果可用）</p>
          </div>
          <Button variant="outline">开启</Button>
        </div>
        
        <div class="flex items-center justify-between">
          <div>
            <h3 class="font-medium">自动备份索引</h3>
            <p class="text-sm text-muted-foreground">定期备份图片索引数据</p>
          </div>
          <Button variant="outline">开启</Button>
        </div>
      </CardContent>
    </Card>
  </div>
</template>