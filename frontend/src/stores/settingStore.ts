import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { setModel, getCurrentModel } from '@/api'

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
      id: 'chinese-clip-vit-base-patch16',
      name: 'Chinese CLIP ViT-B/16',
      description: '专为中文优化的多模态模型'
    },
    {
      id: 'multilingual-clip-vit-base-patch32',
      name: 'Multilingual CLIP ViT-B/32',
      description: '支持多语言的跨语言视觉模型'
    },
    {
      id: 'blip-base',
      name: 'BLIP Base',
      description: '结合视觉与语言理解的模型'
    }
  ])
  
  // 模型切换状态
  const isModelSwitching = ref(false)
  const rebuildProgress = ref(0)
  
  // 设置选择的模型
  const setSelectedModel = async (modelId: string) => {
    if (isModelSwitching.value) {
      console.warn('模型正在切换中，请稍候...')
      return
    }
    
    try {
      isModelSwitching.value = true
      rebuildProgress.value = 0
      
      console.log(`切换模型到: ${modelId}`)
      
      // 调用后端API切换模型
      const response = await setModel(modelId)
      
      // 更新本地状态
      selectedModel.value = modelId
      localStorage.setItem('selectedModel', modelId)
      
      console.log('模型切换成功:', response.message || '模型切换完成')
      return response
      
    } catch (error) {
      console.error('模型切换失败:', error)
      throw error
    } finally {
      isModelSwitching.value = false
    }
  }
  
  // 获取当前模型信息
  const currentModel = computed(() => {
    return modelOptions.value.find(model => model.id === selectedModel.value)
  })
  
  // 从后端获取当前模型信息
  const fetchCurrentModel = async () => {
    try {
      const modelInfo = await getCurrentModel()
      console.log('获取到当前模型信息:', modelInfo)
      
      // 根据后端返回的模型ID更新本地状态
      if (modelInfo.model_id) {
        // 将完整的模型路径映射到简化的ID
        const modelIdMapping = {
          'openai/clip-vit-base-patch32': 'clip-vit-base-patch32',
          'openai/clip-vit-large-patch14': 'clip-vit-large-patch14',
          'OFA-Sys/chinese-clip-vit-base-patch16': 'chinese-clip-vit-base-patch16',
          'sentence-transformers/clip-ViT-B-32-multilingual-v1': 'multilingual-clip-vit-base-patch32',
          'Salesforce/blip-image-captioning-base': 'blip-base'
        }
        
        const mappedId = modelIdMapping[modelInfo.model_id] || 'clip-vit-base-patch32'
        selectedModel.value = mappedId
        localStorage.setItem('selectedModel', mappedId)
      }
    } catch (error) {
      console.error('获取当前模型信息失败:', error)
      // 如果获取失败，使用本地存储的默认值
      const savedModel = localStorage.getItem('selectedModel')
      if (savedModel && modelOptions.value.some(model => model.id === savedModel)) {
        selectedModel.value = savedModel
      }
    }
  }

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
    initialize,
    fetchCurrentModel,
    isModelSwitching,
    rebuildProgress
  }
})