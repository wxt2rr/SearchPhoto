<script setup lang="ts">
import { 
  DialogRoot as DialogPrimitive,
  DialogContent as DialogContentPrimitive,
  DialogTrigger,
  DialogTitle,
  DialogDescription 
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
    <slot name="trigger" />
    <DialogContentPrimitive class="fixed left-[50%] top-[50%] z-50 grid w-full max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 border bg-background p-6 shadow-lg duration-200">
      <DialogTitle class="text-lg font-semibold leading-none tracking-tight">
        <slot name="title" />
      </DialogTitle>
      <DialogDescription class="text-sm text-muted-foreground">
        <slot name="description" />
      </DialogDescription>
      <div class="py-4">
        <slot name="content" />
      </div>
    </DialogContentPrimitive>
  </DialogPrimitive>
</template>