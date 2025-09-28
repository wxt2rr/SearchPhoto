<script setup lang="ts">
import { ref } from 'vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'

const folderPath = ref('')
const isDialogOpen = ref(false)
const selectedFiles = ref<File[]>([])

// 模拟选择文件夹功能
const handleSelectFolder = () => {
  // 由于浏览器安全限制，我们无法直接访问文件系统
  // 这里我们使用输入框让用户粘贴路径，或者展示如何在桌面应用中实现
  alert('在桌面应用中，这里会打开系统文件夹选择对话框。目前我们使用输入框来模拟路径输入。')
  isDialogOpen.value = true
}

// 处理路径输入
const handlePathSubmit = () => {
  if (folderPath.value.trim()) {
    console.log('选择的文件夹路径:', folderPath.value)
    // 这里会调用后端API处理文件夹
    // processFolder(folderPath.value)
    isDialogOpen.value = false
  }
}
</script>

<template>
  <Dialog v-model:open="isDialogOpen">
    <DialogTrigger as-child>
      <Button variant="outline">选择文件夹</Button>
    </DialogTrigger>
    <DialogContent>
      <DialogHeader>
        <DialogTitle>选择照片文件夹</DialogTitle>
      </DialogHeader>
      <div class="py-4">
        <p class="text-sm text-muted-foreground mb-4">
          请输入包含照片的文件夹路径：
        </p>
        <Input 
          v-model="folderPath" 
          placeholder="/path/to/your/photos"
          @keyup.enter="handlePathSubmit"
        />
        <p class="text-xs text-muted-foreground mt-2">
          注意：在实际的桌面应用中，会直接打开系统文件夹选择器
        </p>
      </div>
      <div class="flex justify-end gap-2">
        <Button variant="outline" @click="isDialogOpen = false">取消</Button>
        <Button @click="handlePathSubmit">确定</Button>
      </div>
    </DialogContent>
  </Dialog>
</template>