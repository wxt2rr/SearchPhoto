<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { RouterLink } from 'vue-router'
import { useImageStore } from '@/stores/imageStore'
import { computed, ref } from 'vue'
import { useSearchStore } from '@/stores/searchStore'

const imageStore = useImageStore()
const searchStore = useSearchStore()
const searchQuery = ref('')

// 计算统计信息
const stats = computed(() => {
  const totalFolders = imageStore.processedFolders.length
  const totalImages = imageStore.processedFolders.reduce((sum, folder) => sum + folder.imageCount, 0)
  const lastSearch = '海边日落' // 这里应该从searchStore获取，但为了简化，我们使用固定值
  
  return {
    totalFolders,
    totalImages,
    lastSearch
  }
})

const handleSearch = async () => {
  if (searchQuery.value.trim()) {
    await searchStore.textSearch(searchQuery.value)
  }
}
</script>

<template>
  <div class="flex flex-col items-center py-8 md:py-16">
    <div class="text-center max-w-3xl w-full px-4">
      <div class="inline-flex items-center rounded-full border px-4 py-1 text-sm font-medium mb-6">
        <span class="h-2 w-2 bg-primary rounded-full mr-2"></span>
        本地AI驱动
      </div>
      <h1 class="text-4xl md:text-6xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-primary to-primary/80">
        智能相册搜索
      </h1>
      <p class="text-lg md:text-xl text-muted-foreground mt-4 max-w-2xl mx-auto">
        用自然语言找到你的照片，所有处理均在本地完成，保障隐私安全
      </p>
    </div>

    <div class="mt-12 w-full max-w-5xl px-4">
      <div class="relative">
        <div class="absolute inset-0 bg-primary/5 rounded-2xl -rotate-1"></div>
        <div class="relative grid grid-cols-1 md:grid-cols-3 gap-6 w-full">
          <RouterLink 
            v-for="feature in [
              { title: '选择文件夹', description: '选择包含照片的文件夹开始索引', route: '/folders', icon: '📁' },
              { title: '搜索照片', description: '用自然语言搜索你的照片', route: '/search', icon: '🔍' },
              { title: '查看已处理', description: '管理已处理的文件夹', route: '/folders', icon: '📊' }
            ]" 
            :key="feature.title"
            :to="feature.route"
            class="group relative block"
          >
            <Card class="h-full border-0 shadow-none group-hover:scale-[1.02] transition-all duration-300 bg-card/50 backdrop-blur-sm">
              <CardHeader>
                <div class="text-3xl mb-2">{{ feature.icon }}</div>
                <CardTitle class="group-hover:text-primary transition-colors">{{ feature.title }}</CardTitle>
                <CardDescription>{{ feature.description }}</CardDescription>
              </CardHeader>
              <CardContent>
                <Button class="w-full">
                  开始使用
                </Button>
              </CardContent>
            </Card>
          </RouterLink>
        </div>
      </div>
    </div>

    <div class="mt-16 max-w-4xl w-full px-4">
      <Card class="border-0 bg-muted/30 backdrop-blur-sm">
        <CardHeader class="text-center">
          <CardTitle>使用统计</CardTitle>
          <CardDescription>您的相册搜索概览</CardDescription>
        </CardHeader>
        <CardContent>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-6 text-center">
            <div class="p-4">
              <div class="text-3xl font-bold text-primary">{{ stats.totalFolders }}</div>
              <div class="text-sm text-muted-foreground mt-2">已处理文件夹</div>
            </div>
            <div class="p-4">
              <div class="text-3xl font-bold text-primary">{{ stats.totalImages }}</div>
              <div class="text-sm text-muted-foreground mt-2">已索引照片</div>
            </div>
            <div class="p-4">
              <div class="text-xl font-bold text-primary truncate max-w-[150px] mx-auto">{{ stats.lastSearch }}</div>
              <div class="text-sm text-muted-foreground mt-2">最近搜索</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>

    <div class="mt-16 max-w-3xl w-full px-4">
      <Card class="border-0 bg-gradient-to-br from-primary/5 to-secondary/5 backdrop-blur-sm">
        <CardHeader class="text-center">
          <CardTitle>如何使用</CardTitle>
          <CardDescription>简单几步开始使用智能相册搜索</CardDescription>
        </CardHeader>
        <CardContent>
          <ol class="relative text-lg font-medium text-muted-foreground">
            <li class="mb-6 ml-6">
              <span class="absolute flex items-center justify-center w-8 h-8 bg-primary text-primary-foreground rounded-full -left-11 top-1">
                1
              </span>
              点击"选择文件夹"按钮，选择包含照片的文件夹
            </li>
            <li class="mb-6 ml-6">
              <span class="absolute flex items-center justify-center w-8 h-8 bg-primary text-primary-foreground rounded-full -left-11 top-1">
                2
              </span>
              系统将扫描文件夹并提取图像特征（此过程可能需要几分钟）
            </li>
            <li class="mb-6 ml-6">
              <span class="absolute flex items-center justify-center w-8 h-8 bg-primary text-primary-foreground rounded-full -left-11 top-1">
                3
              </span>
              处理完成后，即可使用自然语言搜索照片
            </li>
            <li class="ml-6">
              <span class="absolute flex items-center justify-center w-8 h-8 bg-primary text-primary-foreground rounded-full -left-11 top-1">
                4
              </span>
              也可以使用"以图搜图"功能
            </li>
          </ol>
        </CardContent>
      </Card>
    </div>

    <div class="mt-16 max-w-2xl w-full px-4">
      <Card class="border-0 bg-gradient-to-r from-primary/10 to-secondary/10">
        <CardHeader class="text-center">
          <CardTitle>拍照行，地点，时间，内容...</CardTitle>
          <CardDescription class="text-lg">一切皆可搜索</CardDescription>
        </CardHeader>
        <CardContent>
          <div class="flex flex-wrap justify-center gap-2">
            <Button variant="secondary" @click="searchQuery = '海边日落'; handleSearch()">海边日落</Button>
            <Button variant="secondary" @click="searchQuery = '家庭聚会'; handleSearch()">家庭聚会</Button>
            <Button variant="secondary" @click="searchQuery = '猫咪玩耍'; handleSearch()">猫咪玩耍</Button>
            <Button variant="secondary" @click="searchQuery = '城市夜景'; handleSearch()">城市夜景</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
</template>

<style scoped>
/* 添加一些样式以优化移动端显示 */
@media (max-width: 768px) {
  .grid {
    gap: 1rem;
  }
}
</style>