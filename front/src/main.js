import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import CKEditor from '@ckeditor/ckeditor5-vue'

// Подключаем единые стили для модальных окон
import '@/assets/modal.css'

// Импортируем сервисы
import { DocumentService, TaskService, ProcessService, ActivityService, UserService, BpmnService, RoleService } from './api/services'

const app = createApp(App)
app.use(router)
app.use(CKEditor)

// Добавляем сервисы в глобальные свойства
app.config.globalProperties.$documentService = DocumentService
app.config.globalProperties.$taskService = TaskService
app.config.globalProperties.$processService = ProcessService
app.config.globalProperties.$activityService = ActivityService
app.config.globalProperties.$userService = UserService
app.config.globalProperties.$bpmnService = BpmnService
app.config.globalProperties.$roleService = RoleService

app.mount('#app')
