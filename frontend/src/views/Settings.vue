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
  <div class="min-h-screen bg-white">
    <div class="max-w-4xl mx-auto px-6 py-12">
      <!-- 消息提示 -->
      <div 
        v-if="message" 
        class="p-4 rounded-lg border mb-8"
        :class="{
          'bg-green-50 border-green-200 text-green-800': messageType === 'success',
          'bg-red-50 border-red-200 text-red-800': messageType === 'error',
          'bg-yellow-50 border-yellow-200 text-yellow-800': messageType === 'warning'
        }"
      >
        {{ message }}
      </div>

      <div class="mb-12">
        <h1 class="text-5xl font-bold text-gray-900 mb-4">设置</h1>
        <p class="text-xl text-gray-600">配置系统偏好和模型选择</p>
      </div>

      <div class="bg-white border border-gray-200 rounded-lg p-8 mb-12">
        <div class="mb-8">
          <h2 class="text-3xl font-bold text-gray-900 mb-3">AI模型选择</h2>
          <p class="text-lg text-gray-600">选择用于图片分析和搜索的AI模型</p>
        </div>
        
        <div class="space-y-8">
          <div 
            v-for="model in modelOptions" 
            :key="model.id"
            class="border border-gray-200 rounded-lg p-8 hover:bg-gray-50 transition-colors"
            :class="{ 'border-gray-400 bg-gray-50': settingStore.selectedModel === model.id }"
          >
            <div class="flex items-start gap-6">
              <div class="flex-1">
                <div class="flex items-center gap-3 mb-4">
                  <h3 class="text-2xl font-semibold text-gray-900">{{ model.name }}</h3>
                  <span 
                    v-if="settingStore.selectedModel === model.id"
                    class="text-sm bg-gray-200 text-gray-700 px-3 py-1 rounded-full"
                  >
                    当前使用
                  </span>
                </div>
                <p class="text-gray-600 mb-6">{{ model.description }}</p>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div>
                    <h4 class="text-lg font-medium text-gray-900 mb-4">特点：</h4>
                    <ul class="space-y-3">
                      <li 
                        v-for="(feature, index) in model.features" 
                        :key="index"
                        class="flex items-start gap-3"
                      >
                        <div class="w-2 h-2 rounded-full bg-gray-400 mt-2 flex-shrink-0"></div>
                        <span class="text-gray-700">{{ feature }}</span>
                      </li>
                    </ul>
                  </div>
                  
                  <div>
                    <h4 class="text-lg font-medium text-gray-900 mb-4">适用场景：</h4>
                    <ul class="space-y-3">
                      <li 
                        v-for="(useCase, index) in model.useCases" 
                        :key="index"
                        class="flex items-start gap-3"
                      >
                        <div class="w-2 h-2 rounded-full bg-gray-400 mt-2 flex-shrink-0"></div>
                        <span class="text-gray-700">{{ useCase }}</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
              
              <Button 
                @click="handleModelChange(model.id)"
                variant="outline"
                :disabled="settingStore.isModelSwitching"
                class="border-gray-200 text-gray-700 hover:bg-gray-50"
                :class="{ 'bg-gray-200 text-gray-900 hover:bg-gray-300': settingStore.selectedModel === model.id }"
              >
                <span v-if="settingStore.isModelSwitching && settingStore.switchingToModel === model.id" class="flex items-center gap-2">
                  <div class="w-4 h-4 border-2 border-gray-300 border-t-gray-600 rounded-full animate-spin"></div>
                  切换中...
                </span>
                <span v-else>
                  {{ settingStore.selectedModel === model.id ? '使用中' : '选择' }}
                </span>
              </Button>
            </div>
          </div>
        </div>
        
        <div class="pt-8 border-t border-gray-200">
          <h3 class="text-lg font-medium text-gray-900 mb-4">当前选择的模型：</h3>
          <div class="text-sm p-4 bg-gray-50 rounded-lg">
            <div v-if="settingStore.isModelSwitching" class="flex items-center gap-3 text-gray-600">
              <div class="w-4 h-4 border-2 border-gray-300 border-t-gray-600 rounded-full animate-spin"></div>
              <span>正在切换模型...</span>
              <div v-if="settingStore.rebuildProgress > 0" class="ml-2">
                (重建进度: {{ settingStore.rebuildProgress }}%)
              </div>
            </div>
            <span v-else-if="settingStore.selectedModel" class="text-gray-900">
              {{
                modelOptions.find(m => m.id === settingStore.selectedModel)?.name || 
                settingStore.selectedModel
              }}
            </span>
            <span v-else class="text-gray-500">尚未选择模型</span>
          </div>
        </div>
      </div>

      <div class="bg-white border border-gray-200 rounded-lg p-8">
        <div class="mb-8">
          <h2 class="text-3xl font-bold text-gray-900 mb-3">其他设置</h2>
          <p class="text-lg text-gray-600">系统其他配置选项</p>
        </div>
        
        <div class="space-y-8">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-xl font-medium text-gray-900">启用GPU加速</h3>
              <p class="text-gray-600 mt-1">使用GPU提升处理速度（如果可用）</p>
            </div>
            <Button variant="outline" class="border-gray-200 text-gray-700 hover:bg-gray-50">开启</Button>
          </div>
          
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-xl font-medium text-gray-900">自动备份索引</h3>
              <p class="text-gray-600 mt-1">定期备份图片索引数据</p>
            </div>
            <Button variant="outline" class="border-gray-200 text-gray-700 hover:bg-gray-50">开启</Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>