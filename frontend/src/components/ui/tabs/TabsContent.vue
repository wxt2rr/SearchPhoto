<script setup lang="ts">
import { inject, computed } from 'vue'
import type { HTMLAttributes } from 'vue'
import { cn } from '@/lib/utils'

interface Props {
  value: string
  class?: HTMLAttributes['class']
}

const props = defineProps<Props>()

const tabs = inject('tabs') as any
const isActive = computed(() => tabs.activeTab.value === props.value)
</script>

<template>
  <div
    v-show="isActive"
    :class="cn('mt-2 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2', props.class)"
  >
    <slot />
  </div>
</template>