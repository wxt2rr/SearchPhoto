// /Users/wangxt/myspace/SearchPhoto/frontend/src/api/index.ts
import axios from 'axios'

const API_BASE_URL = 'http://127.0.0.1:5000/api'

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30秒超时
})

// 提取图像特征
export const extractFeatures = async (imagePath: string) => {
  try {
    const response = await apiClient.post('/extract-features', { imagePath })
    return response.data
  } catch (error) {
    console.error('提取图像特征失败:', error)
    throw error
  }
}

// 文本搜索
export const searchByText = async (query: string, topK: number = 10) => {
  try {
    const response = await apiClient.post('/search-by-text', { 
      query,
      topK 
    })
    return response.data
  } catch (error) {
    console.error('文本搜索失败:', error)
    throw error
  }
}

// 以图搜图 - 支持文件上传
export const searchByImage = async (imageFile: File | string, topK: number = 10) => {
  try {
    if (imageFile instanceof File) {
      // 使用FormData上传文件
      const formData = new FormData()
      formData.append('image', imageFile)
      formData.append('topK', topK.toString())
      
      // 发送multipart/form-data请求
      const response = await axios.post(`${API_BASE_URL}/search-by-image`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      return response.data
    } else {
      // 传入的是文件路径
      const response = await apiClient.post('/search-by-image', { 
        imagePath: imageFile,
        topK 
      })
      return response.data
    }
  } catch (error) {
    console.error('以图搜图失败:', error)
    throw error
  }
}

// 处理文件夹
export const processFolder = async (folderPath: string) => {
  try {
    const response = await apiClient.post('/process-folder', { folderPath })
    return response.data
  } catch (error) {
    console.error('处理文件夹失败:', error)
    throw error
  }
}

// 获取处理状态
export const getProcessingStatus = async (taskId: string) => {
  try {
    const response = await apiClient.get(`/processing-status/${taskId}`)
    return response.data
  } catch (error) {
    console.error('获取处理状态失败:', error)
    throw error
  }
}

// 获取缩略图
export const getThumbnail = (imagePath: string) => {
  try {
    // 使用新的图片代理接口
    const encodedPath = encodeURIComponent(imagePath)
    return `${API_BASE_URL}/image-proxy?path=${encodedPath}`
  } catch (error) {
    console.error('获取缩略图失败:', error)
    throw error
  }
}