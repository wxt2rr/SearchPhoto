<script setup lang="ts">
import { provide, ref, watch, onMounted } from 'vue'

interface Props {
  modelValue?: string
  defaultValue?: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const activeTab = ref(props.modelValue || props.defaultValue || '')

// 确保初始值正确设置
onMounted(() => {
  if (props.modelValue) {
    activeTab.value = props.modelValue
  }
})

watch(() => props.modelValue, (newValue) => {
  if (newValue !== undefined) {
    activeTab.value = newValue
  }
})

const setActiveTab = (value: string) => {
  activeTab.value = value
  emit('update:modelValue', value)
}

provide('tabs', {
  activeTab,
  setActiveTab
})
</script>

<template>
  <div class="w-full">
    <slot />
  </div>
</template>