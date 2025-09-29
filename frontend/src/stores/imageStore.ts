import { defineStore } from 'pinia'
import { ref } from 'vue'
import { processFolder, getProcessingStatus, reindexFolder } from '@/api'
import { useSettingStore } from '@/stores/settingStore'

interface Folder {
  id: number
  name: string
  path: string
  imageCount: number
  lastProcessed: string
  status: 'completed' | 'processing'
}

export const useImageStore = defineStore('image', () => {
  // 已处理的文件夹列表
  const processedFolders = ref<Folder[]>([])
  
  // 处理任务状态
  const processingTasks = ref<Record<string, any>>({})
  
  // 添加新文件夹
  const addFolder = async (folderPath: string) => {
    try {
      const result = await processFolder(folderPath)
      
      // 创建一个临时的处理中文件夹对象
      const newFolder: Folder = {
        id: Date.now(), // 使用时间戳作为临时ID，后端处理完成后可能会有真正的ID
        name: folderPath.split('/').pop() || folderPath,
        path: folderPath,
        imageCount: 0,
        lastProcessed: new Date().toLocaleString(),
        status: 'processing'
      }
      
      // 将处理中的文件夹添加到列表
      processedFolders.value.push(newFolder)
      
      // 添加到处理任务列表
      processingTasks.value[result.taskId] = {
        taskId: result.taskId,
        folderPath: folderPath,
        progress: 0,
        status: 'processing',
        processed: 0,
        total: 0
      }
      
      // 开始轮询处理状态
      pollProcessingStatus(result.taskId)
      
      return result.taskId
    } catch (error) {
      console.error('添加文件夹失败:', error)
      throw error
    }
  }
  
  // 轮询处理状态
  const pollProcessingStatus = async (taskId: string) => {
    try {
      const status = await getProcessingStatus(taskId)
      processingTasks.value[taskId] = status
      
      // 查找对应的文件夹进行更新
      // 首先尝试使用status返回的folderPath进行匹配
      let folderIndex = -1
      if (status.folderPath) {
        folderIndex = processedFolders.value.findIndex(
          folder => folder.path === status.folderPath
        )
      } else {
        // 如果status中没有folderPath，则使用任务ID关联的路径
        const taskInfo = processingTasks.value[taskId]
        if (taskInfo && taskInfo.folderPath) {
          folderIndex = processedFolders.value.findIndex(
            folder => folder.path === taskInfo.folderPath
          )
        }
      }
      
      if (folderIndex !== -1) {
        // 更新文件夹信息
        processedFolders.value[folderIndex] = {
          ...processedFolders.value[folderIndex],
          status: status.status === 'completed' ? 'completed' : 'processing',
          imageCount: status.processed || 0
        }
      }
      
      // 如果处理未完成，继续轮询
      if (status.status === 'processing') {
        setTimeout(() => pollProcessingStatus(taskId), 1000) // 每秒轮询一次
      } else {
        // 处理完成或失败，从处理任务列表中移除
        delete processingTasks.value[taskId]
        
        if (status.status === 'completed') {
          console.log('文件夹处理完成:', status.folderPath || 'unknown path')
        } else if (status.status === 'failed') {
          console.error('文件夹处理失败:', status.error)
          // 可以在UI上显示错误信息
        }
      }
    } catch (error) {
      console.error('获取处理状态失败:', error)
      processingTasks.value[taskId] = { status: 'failed', error: (error as Error).message }
      
      // 尝试更新文件夹状态为失败
      const taskInfo = processingTasks.value[taskId]
      if (taskInfo && taskInfo.folderPath) {
        const folderIndex = processedFolders.value.findIndex(
          folder => folder.path === taskInfo.folderPath
        )
        
        if (folderIndex !== -1) {
          processedFolders.value[folderIndex] = {
            ...processedFolders.value[folderIndex],
            status: 'processing', // 保持处理中状态但显示错误
          }
        }
      }
      
      // 无论成功或失败，都从处理任务列表中移除
      delete processingTasks.value[taskId]
    }
  }
  
  // 移除文件夹
  const removeFolder = (folderId: number) => {
    processedFolders.value = processedFolders.value.filter(folder => folder.id !== folderId)
  }
  
  // 刷新文件夹
  const refreshFolder = async (folderId: number) => {
    console.log(`刷新文件夹 ${folderId}`)
    // 查找文件夹路径
    const folder = processedFolders.value.find(f => f.id === folderId)
    if (!folder) {
      throw new Error(`未找到ID为 ${folderId} 的文件夹`)
    }
    
    // 获取当前选择的模型
    const settingStore = useSettingStore()
    const selectedModel = settingStore.selectedModel
    
    // 这里会调用后端API重新处理文件夹
    try {
      const result = await reindexFolder(folder.path, selectedModel)
      
      // 更新文件夹状态为处理中
      const folderIndex = processedFolders.value.findIndex(f => f.id === folderId)
      if (folderIndex !== -1) {
        processedFolders.value[folderIndex] = {
          ...processedFolders.value[folderIndex],
          status: 'processing'
        }
      }
      
      // 添加到处理任务列表
      processingTasks.value[result.taskId] = {
        taskId: result.taskId,
        folderPath: folder.path,
        progress: 0,
        status: 'processing',
        processed: 0,
        total: 0
      }
      
      // 开始轮询处理状态
      pollProcessingStatus(result.taskId)
      
      return result.taskId
    } catch (error) {
      console.error('重新索引文件夹失败:', error)
      throw error
    }
  }
  
  return {
    processedFolders,
    processingTasks,
    addFolder,
    removeFolder,
    refreshFolder
  }
})