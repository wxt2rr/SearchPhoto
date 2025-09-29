<script setup lang="ts">
import { 
  DialogRoot as DialogPrimitive
} from 'radix-vue'

interface DialogProps {
  open?: boolean
}

const props = defineProps<DialogProps>()

interface DialogEmits {
  'update:open': [open: boolean]
}

const emit = defineEmits<DialogEmits>()

const onOpenChange = (open: boolean) => {
  emit('update:open', open)
}
</script>

<template>
  <DialogPrimitive :open="open" @update:open="onOpenChange">
    <slot />
  </DialogPrimitive>
</template>