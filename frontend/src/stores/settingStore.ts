import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useSettingStore = defineStore('setting', () => {
  // 当前选择的模型
  const selectedModel = ref<string>('clip-vit-base-patch32')
  
  // 模型选项
  const modelOptions = ref([
    {
      id: 'clip-vit-base-patch32',
      name: 'CLIP ViT-B/32',
      description: '平衡性能与速度的通用模型'
    },
    {
      id: 'clip-vit-large-patch14',
      name: 'CLIP ViT-L/14',
      description: '更高精度的大型模型'
    },
    {
      id: 'blip-base',
      name: 'BLIP Base',
      description: '结合视觉与语言理解的模型'
    }
  ])
  
  // 设置选择的模型
  const setSelectedModel = (modelId: string) => {
    selectedModel.value = modelId
    // 可以在这里添加保存到本地存储的逻辑
    localStorage.setItem('selectedModel', modelId)
  }
  
  // 获取当前模型信息
  const currentModel = computed(() => {
    return modelOptions.value.find(model => model.id === selectedModel.value)
  })
  
  // 从本地存储初始化
  const initialize = () => {
    const savedModel = localStorage.getItem('selectedModel')
    if (savedModel && modelOptions.value.some(model => model.id === savedModel)) {
      selectedModel.value = savedModel
    }
  }
  
  return {
    selectedModel,
    modelOptions,
    setSelectedModel,
    currentModel,
    initialize
  }
})