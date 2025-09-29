import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useSettingStore } from './stores/settingStore'
import './assets/css/input.css'

const app = createApp(App)

const pinia = createPinia()
app.use(pinia)

// 初始化设置Store
const settingStore = useSettingStore(pinia)
settingStore.initialize()

app.use(router)

app.mount('#app')