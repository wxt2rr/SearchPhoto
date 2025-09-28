import { defineStore } from 'pinia'
import { ref } from 'vue'
import { searchByText, searchByImage, getThumbnail } from '@/api'

export const useSearchStore = defineStore('search', () => {
  const searchResults = ref<any[]>([])
  const isLoading = ref(false)
  const searchHistory = ref<string[]>([])
  
  // 文本搜索
  const textSearch = async (query: string) => {
    if (!query.trim()) return
    
    isLoading.value = true
    try {
      const results = await searchByText(query)
      searchResults.value = results.results || []
      
      // 添加到搜索历史
      if (!searchHistory.value.includes(query)) {
        searchHistory.value.unshift(query)
        if (searchHistory.value.length > 10) { // 只保留最近10个搜索
          searchHistory.value.pop()
        }
      }
      
      return searchResults.value
    } catch (error) {
      console.error('搜索失败:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }
  
  // 以图搜图
  const imageSearch = async (imageFile: File | string) => {
    isLoading.value = true
    try {
      const results = await searchByImage(imageFile)
      searchResults.value = results.results || []
      return searchResults.value
    } catch (error) {
      console.error('以图搜图失败:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }
  
  // 获取缩略图URL
  const getThumbnailUrl = (imagePath: string) => {
    return getThumbnail(imagePath)
  }
  
  // 清除搜索结果
  const clearResults = () => {
    searchResults.value = []
  }
  
  return {
    searchResults,
    isLoading,
    searchHistory,
    textSearch,
    imageSearch,
    getThumbnailUrl,
    clearResults
  }
})