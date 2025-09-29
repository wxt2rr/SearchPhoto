export { default as Dialog } from './Dialog.vue'
export { default as DialogContent } from './DialogContent.vue'

// 重新导出 radix-vue 的组件以保持一致性
export { 
  DialogTitle,
  DialogDescription
} from 'radix-vue'

// DialogHeader 是一个简单的容器组件
export const DialogHeader = { 
  template: '<div class="flex flex-col space-y-1.5 text-center sm:text-left"><slot /></div>' 
}