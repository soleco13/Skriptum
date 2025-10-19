<template>
  <div class="profile-page">
    <!-- Заголовок страницы -->
    <div class="profile-header">
      <div class="header-content">
        <h1>
          <i class="fas fa-user-circle"></i>
          Мой профиль
        </h1>
        <p class="header-subtitle">Управление личной информацией и настройками</p>
      </div>
      <div class="header-actions">
        <button 
          class="btn-secondary" 
          @click="toggleEditMode"
          :disabled="isLoading || !user"
        >
          <i class="fas" :class="editMode ? 'fa-times' : 'fa-edit'"></i>
          {{ editMode ? 'Отменить' : 'Редактировать' }}
        </button>
      </div>
    </div>

    <!-- Индикатор загрузки -->
    <div v-if="isLoading && !user" class="loading-container">
      <div class="loading-spinner">
        <i class="fas fa-spinner fa-spin"></i>
        <p>Загрузка данных профиля...</p>
      </div>
    </div>

    <!-- Основной контент -->
    <div v-if="user" class="profile-container">
      <!-- Боковая панель с аватаром и статистикой -->
      <div class="profile-sidebar">
        <div class="profile-card">
        <div class="profile-avatar">
            <div class="avatar-container">
              <img 
                :src="getAvatarUrl()" 
                alt="Аватар пользователя"
                class="avatar-image"
                @error="handleAvatarError"
              >
              <div v-if="editMode" class="avatar-overlay">
                <label for="avatar-input" class="avatar-upload-btn">
              <i class="fas fa-camera"></i>
              <span>Изменить фото</span>
            </label>
                <input 
                  id="avatar-input" 
                  type="file" 
                  accept="image/*" 
                  @change="handleAvatarChange"
                  ref="avatarInput"
                >
              </div>
            </div>
            <div class="avatar-info">
              <h3>{{ getUserDisplayName() }}</h3>
              <p class="user-position">{{ user?.profile?.position || 'Пользователь' }}</p>
              <div class="user-role-badge" v-if="user?.profile?.role_info">
                <i :class="user.profile.role_info.icon" :style="{ color: user.profile.role_info.color }"></i>
                <span>{{ user.profile.role_info.display_name }}</span>
              </div>
            </div>
          </div>
          
          <!-- Статистика -->
        <div class="profile-stats">
            <h4>
              <i class="fas fa-chart-bar"></i>
              Статистика
            </h4>
            <div class="stats-grid">
          <div class="stat-item">
                <div class="stat-icon documents">
            <i class="fas fa-file-alt"></i>
                </div>
            <div class="stat-info">
                  <span class="stat-value">{{ stats.documents_count || 0 }}</span>
              <span class="stat-label">Документов</span>
            </div>
          </div>
          <div class="stat-item">
                <div class="stat-icon tasks">
            <i class="fas fa-tasks"></i>
                </div>
            <div class="stat-info">
                  <span class="stat-value">{{ stats.tasks_count || 0 }}</span>
              <span class="stat-label">Задач</span>
            </div>
          </div>
          <div class="stat-item">
                <div class="stat-icon processes">
            <i class="fas fa-project-diagram"></i>
                </div>
            <div class="stat-info">
                  <span class="stat-value">{{ stats.processes_count || 0 }}</span>
              <span class="stat-label">Процессов</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Основной контент профиля -->
      <div class="profile-content">
        <!-- Форма редактирования -->
        <form @submit.prevent="saveProfile" v-if="editMode" class="profile-form">
          <!-- Основная информация -->
          <div class="form-section">
            <div class="section-header">
              <h2>
                <i class="fas fa-user"></i>
                Основная информация
              </h2>
            </div>
            <div class="form-grid">
              <div class="form-group">
                <label for="firstName">Имя *</label>
                <input 
                  type="text" 
                  id="firstName" 
                  v-model="editedUser.first_name" 
                  required
                  :class="{ 'error': errors.first_name }"
                >
                <span v-if="errors.first_name" class="error-message">{{ errors.first_name }}</span>
              </div>
              <div class="form-group">
                <label for="lastName">Фамилия *</label>
                <input 
                  type="text" 
                  id="lastName" 
                  v-model="editedUser.last_name" 
                  required
                  :class="{ 'error': errors.last_name }"
                >
                <span v-if="errors.last_name" class="error-message">{{ errors.last_name }}</span>
              </div>
              <div class="form-group">
                <label for="email">Email *</label>
                <input 
                  type="email" 
                  id="email" 
                  v-model="editedUser.email" 
                  required
                  :class="{ 'error': errors.email }"
                >
                <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
              </div>
              <div class="form-group">
                <label for="phone">Телефон</label>
                <input 
                  type="tel" 
                  id="phone" 
                  v-model="editedProfile.phone"
                  placeholder="+7 (999) 123-45-67"
                >
            </div>
            <div class="form-group">
              <label for="position">Должность</label>
                <input 
                  type="text" 
                  id="position" 
                  v-model="editedProfile.position"
                  placeholder="Менеджер проектов"
                >
            </div>
            <div class="form-group">
              <label for="department">Отдел</label>
                <input 
                  type="text" 
                  id="department" 
                  v-model="editedProfile.department"
                  placeholder="Отдел разработки"
                >
              </div>
            </div>
          </div>

          <!-- Безопасность -->
          <div class="form-section">
            <div class="section-header">
              <h2>
                <i class="fas fa-shield-alt"></i>
                Безопасность
              </h2>
            </div>
            <div class="form-grid">
              <div class="form-group">
                <label for="currentPassword">Текущий пароль</label>
                <input 
                  type="password" 
                  id="currentPassword" 
                  v-model="passwords.current"
                  placeholder="Введите текущий пароль"
                >
              </div>
              <div class="form-group">
                <label for="newPassword">Новый пароль</label>
                <input 
                  type="password" 
                  id="newPassword" 
                  v-model="passwords.new"
                  placeholder="Введите новый пароль"
                  :class="{ 'error': errors.new_password }"
                >
                <span v-if="errors.new_password" class="error-message">{{ errors.new_password }}</span>
              </div>
              <div class="form-group">
                <label for="confirmPassword">Подтверждение пароля</label>
                <input 
                  type="password" 
                  id="confirmPassword" 
                  v-model="passwords.confirm"
                  placeholder="Подтвердите новый пароль"
                  :class="{ 'error': errors.confirm_password }"
                >
                <span v-if="errors.confirm_password" class="error-message">{{ errors.confirm_password }}</span>
              </div>
            </div>
          </div>

          <!-- Действия формы -->
          <div class="form-actions">
            <button type="button" class="btn-secondary" @click="cancelEdit" :disabled="isLoading">
              <i class="fas fa-times"></i>
              Отменить
            </button>
            <button type="submit" class="btn-primary" :disabled="isLoading">
              <i v-if="isLoading" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-save"></i>
              {{ isLoading ? 'Сохранение...' : 'Сохранить изменения' }}
            </button>
          </div>
        </form>

        <!-- Информация для просмотра -->
        <div class="profile-info" v-else>
          <!-- Основная информация -->
          <div class="info-section">
            <div class="section-header">
              <h2>
                <i class="fas fa-user"></i>
                Основная информация
              </h2>
            </div>
            <div class="info-grid">
              <div class="info-item">
                <div class="info-label">
                  <i class="fas fa-user"></i>
                  Полное имя
                </div>
                <div class="info-value">{{ getUserDisplayName() }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">
                  <i class="fas fa-envelope"></i>
                  Email
                </div>
                <div class="info-value">{{ user?.email || 'Не указан' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">
                  <i class="fas fa-phone"></i>
                  Телефон
                </div>
                <div class="info-value">{{ user?.profile?.phone || 'Не указан' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">
                  <i class="fas fa-briefcase"></i>
                  Должность
                </div>
                <div class="info-value">{{ user?.profile?.position || 'Не указана' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">
                  <i class="fas fa-building"></i>
                  Отдел
                </div>
                <div class="info-value">{{ user?.profile?.department || 'Не указан' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">
                  <i class="fas fa-calendar-plus"></i>
                  Дата регистрации
                </div>
                <div class="info-value">{{ formatDate(user?.date_joined) }}</div>
              </div>
            </div>
          </div>

          <!-- Роль и разрешения -->
          <div class="info-section" v-if="user?.profile?.role_info">
            <div class="section-header">
              <h2>
                <i :class="user.profile.role_info.icon" :style="{ color: user.profile.role_info.color }"></i>
                Роль и разрешения
              </h2>
              <div class="section-actions" v-if="hasPermission('manage_roles')">
                <router-link to="/roles" class="btn-secondary">
                  <i class="fas fa-users-cog"></i>
                  Управление ролями
                </router-link>
                <button class="btn-primary" @click="showRoleManagement = true; loadAvailableRoles()" v-if="isOtherUser">
                  <i class="fas fa-user-cog"></i>
                  Управление ролью
                </button>
              </div>
            </div>
            <div class="role-info">
              <div class="role-details">
                <div class="role-badge-large">
                  <i :class="user.profile.role_info.icon" :style="{ color: user.profile.role_info.color }"></i>
                  <div class="role-text">
                    <h3>{{ user.profile.role_info.display_name }}</h3>
                    <p>{{ user.profile.role_info.description }}</p>
                  </div>
                </div>
              </div>
              
              <div class="permissions-section" v-if="user?.profile?.permissions?.length > 0">
                <h4>
                  <i class="fas fa-key"></i>
                  Разрешения
                </h4>
                <div class="permissions-grid">
                  <div 
                    class="permission-item" 
                    v-for="permission in user.profile.permissions" 
                    :key="permission"
                  >
                    <i class="fas fa-check-circle"></i>
                    <span>{{ getPermissionDisplayName(permission) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Последняя активность -->
          <div class="info-section">
            <div class="section-header">
              <h2>
                <i class="fas fa-history"></i>
                Последняя активность
              </h2>
            </div>
            <div class="activity-list" v-if="recentActivity.length > 0">
              <div 
                class="activity-item" 
                v-for="(activity, index) in recentActivity" 
                :key="index"
              >
                <div class="activity-icon" :style="{ backgroundColor: activity.color }">
                  <i :class="activity.icon"></i>
                </div>
                <div class="activity-details">
                  <div class="activity-description">{{ activity.description }}</div>
                  <div class="activity-time">{{ activity.time }}</div>
                </div>
              </div>
            </div>
            <div v-else class="empty-state">
              <i class="fas fa-history"></i>
              <p>Активность не найдена</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Уведомления -->
    <div v-if="notification.show" class="notification" :class="notification.type">
      <i :class="notification.icon"></i>
      <span>{{ notification.message }}</span>
      <button @click="hideNotification" class="notification-close">
        <i class="fas fa-times"></i>
      </button>
    </div>

    <!-- Модальное окно управления ролью пользователя -->
    <div v-if="showRoleManagement" class="modal-overlay" @click="closeRoleManagement">
      <div class="modal-content role-management-modal" @click.stop>
        <div class="modal-header">
          <h2>
            <i class="fas fa-user-cog"></i>
            Управление ролью пользователя {{ user?.username }}
          </h2>
          <button class="close-btn" @click="closeRoleManagement">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="role-management-content">
          <div class="current-role-section" v-if="user?.profile?.role_info">
            <h3>Текущая роль</h3>
            <div class="current-role-card">
              <div class="role-icon" :style="{ backgroundColor: user.profile.role_info.color }">
                <i :class="user.profile.role_info.icon"></i>
              </div>
              <div class="role-details">
                <h4>{{ user.profile.role_info.display_name }}</h4>
                <p>{{ user.profile.role_info.description }}</p>
              </div>
              <div class="role-actions">
                <button class="btn-danger" @click="removeRole">
                  <i class="fas fa-user-minus"></i>
                  Снять роль
                </button>
              </div>
            </div>
          </div>

          <div class="assign-role-section">
            <h3>Назначить новую роль</h3>
            <div class="roles-grid">
              <div 
                class="role-card" 
                v-for="role in availableRoles" 
                :key="role.id"
                @click="assignRole(role.id)"
                :class="{ disabled: role.id === user?.profile?.role_info?.id }"
              >
                <div class="role-icon" :style="{ backgroundColor: role.color }">
                  <i :class="role.icon"></i>
                </div>
                <div class="role-info">
                  <h4>{{ role.display_name }}</h4>
                  <p>{{ role.description }}</p>
                </div>
                <div class="role-stats">
                  <span>{{ role.users_count }} пользователей</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { authService } from '@/api/auth'

export default {
  name: 'UserProfile',
  data() {
    return {
      editMode: false,
      isLoading: false,
      user: null,
      editedUser: null,
      editedProfile: null,
      stats: {},
      recentActivity: [],
      passwords: {
        current: '',
        new: '',
        confirm: ''
      },
      errors: {},
      notification: {
        show: false,
        type: 'success',
        message: '',
        icon: 'fas fa-check-circle'
      },
      // Данные для управления ролями
      showRoleManagement: false,
      availableRoles: [],
      isOtherUser: false,
      currentUserId: null
    }
  },
    async created() {
      await this.loadUserData()
      await this.loadStats()
      await this.loadRecentActivity()
      await this.loadCurrentUser()
      this.checkIfOtherUser()
    },
  methods: {
    async loadUserData() {
      try {
        this.isLoading = true
        const userData = await authService.getMe()
        this.user = userData
        this.resetEditData()
      } catch (error) {
        console.error('Ошибка загрузки данных пользователя:', error)
        this.showNotification('Ошибка загрузки данных пользователя', 'error')
      } finally {
        this.isLoading = false
      }
    },

    async loadStats() {
      try {
        const response = await this.$UserService.getProfileStats()
        this.stats = response.data
      } catch (error) {
        console.error('Ошибка загрузки статистики:', error)
      }
    },

    async loadRecentActivity() {
      try {
        const response = await this.$UserService.getRecentActivity()
        this.recentActivity = response.data
      } catch (error) {
        console.error('Ошибка загрузки активности:', error)
      }
    },

    resetEditData() {
      this.editedUser = {
        first_name: this.user.first_name || '',
        last_name: this.user.last_name || '',
        email: this.user.email || ''
      }
      this.editedProfile = {
        phone: this.user.profile?.phone || '',
        position: this.user.profile?.position || '',
        department: this.user.profile?.department || ''
      }
      this.passwords = { current: '', new: '', confirm: '' }
      this.errors = {}
    },

    toggleEditMode() {
      this.editMode = !this.editMode
      if (this.editMode) {
        this.resetEditData()
      }
    },

    cancelEdit() {
      this.editMode = false
      this.resetEditData()
    },

    getUserDisplayName() {
      if (!this.user) return 'Пользователь'
      const firstName = this.user.first_name || ''
      const lastName = this.user.last_name || ''
      return `${firstName} ${lastName}`.trim() || this.user.username || 'Пользователь'
    },

    getAvatarUrl() {
      if (this.user?.profile?.avatar_url) {
        return this.user.profile.avatar_url
      }
      return require('@/assets/avatar.png')
    },

    handleAvatarError() {
      // Если аватар не загрузился, используем дефолтный
      console.log('Ошибка загрузки аватара, используется дефолтный')
    },

    async handleAvatarChange(event) {
      const file = event.target.files[0]
      if (!file) return

      // Проверяем размер файла (максимум 5MB)
      if (file.size > 5 * 1024 * 1024) {
        this.showNotification('Размер файла не должен превышать 5MB', 'error')
        return
      }

      // Проверяем тип файла
      const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
      if (!allowedTypes.includes(file.type)) {
        this.showNotification('Неподдерживаемый тип файла. Разрешены: JPEG, PNG, GIF, WebP', 'error')
        return
      }

      try {
        this.isLoading = true
        
        const formData = new FormData()
        formData.append('avatar', file)
        
        const response = await this.$UserService.uploadAvatar(formData)
        
        if (response.data.success) {
          // Обновляем URL аватара
          this.user.profile.avatar_url = response.data.avatar_url
          this.showNotification('Аватар успешно загружен', 'success')
        }
      } catch (error) {
        console.error('Ошибка загрузки аватара:', error)
        this.showNotification('Ошибка при загрузке аватара', 'error')
      } finally {
        this.isLoading = false
        // Очищаем input
        if (this.$refs.avatarInput) {
          this.$refs.avatarInput.value = ''
        }
      }
    },

    validateForm() {
      this.errors = {}

      // Валидация имени
      if (!this.editedUser.first_name?.trim()) {
        this.errors.first_name = 'Имя обязательно для заполнения'
      }

      // Валидация фамилии
      if (!this.editedUser.last_name?.trim()) {
        this.errors.last_name = 'Фамилия обязательна для заполнения'
      }

      // Валидация email
      if (!this.editedUser.email?.trim()) {
        this.errors.email = 'Email обязателен для заполнения'
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.editedUser.email)) {
        this.errors.email = 'Некорректный формат email'
      }

      // Валидация паролей
      if (this.passwords.new) {
        if (!this.passwords.current) {
          this.errors.current_password = 'Введите текущий пароль'
        }
        if (this.passwords.new.length < 8) {
          this.errors.new_password = 'Пароль должен содержать минимум 8 символов'
        }
        if (this.passwords.new !== this.passwords.confirm) {
          this.errors.confirm_password = 'Пароли не совпадают'
        }
      }

      return Object.keys(this.errors).length === 0
    },

    async saveProfile() {
      if (!this.validateForm()) {
        this.showNotification('Пожалуйста, исправьте ошибки в форме', 'error')
        return
      }

      this.isLoading = true

      try {
        // Обновляем основную информацию пользователя
        const userUpdateData = {
          first_name: this.editedUser.first_name,
          last_name: this.editedUser.last_name,
          email: this.editedUser.email
        }

        // Если указан новый пароль, добавляем его
        if (this.passwords.new) {
          userUpdateData.password = this.passwords.new
          userUpdateData.current_password = this.passwords.current
        }

        await authService.updateUser(userUpdateData)

        // Обновляем профиль
        await authService.updateProfile(this.editedProfile)

        // Перезагружаем данные пользователя
        await this.loadUserData()
        
        this.editMode = false
        this.showNotification('Профиль успешно обновлен', 'success')
      } catch (error) {
        console.error('Ошибка обновления профиля:', error)
        
        if (error.response?.data) {
          const errorData = error.response.data
          if (errorData.password) {
            this.errors.current_password = 'Неверный текущий пароль'
          }
          if (errorData.email) {
            this.errors.email = 'Email уже используется'
          }
        }
        
        this.showNotification('Ошибка при обновлении профиля', 'error')
      } finally {
        this.isLoading = false
      }
    },

    formatDate(dateString) {
      if (!dateString) return 'Не указана'
      const date = new Date(dateString)
      return date.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    },

    showNotification(message, type = 'success') {
      this.notification = {
        show: true,
        type,
        message,
        icon: type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle'
      }

      // Автоматически скрываем уведомление через 5 секунд
      setTimeout(() => {
        this.hideNotification()
      }, 5000)
    },

    hideNotification() {
      this.notification.show = false
    },

    getPermissionDisplayName(permission) {
      const permissionNames = {
        'create_documents': 'Создание документов',
        'edit_documents': 'Редактирование документов',
        'delete_documents': 'Удаление документов',
        'share_documents': 'Обмен документами',
        'create_processes': 'Создание процессов',
        'edit_processes': 'Редактирование процессов',
        'delete_processes': 'Удаление процессов',
        'manage_processes': 'Управление процессами',
        'create_tasks': 'Создание задач',
        'edit_tasks': 'Редактирование задач',
        'delete_tasks': 'Удаление задач',
        'assign_tasks': 'Назначение задач',
        'manage_users': 'Управление пользователями',
        'view_analytics': 'Просмотр аналитики',
        'manage_roles': 'Управление ролями'
      }
      return permissionNames[permission] || permission
    },

    hasPermission(permission) {
      // Проверяем разрешения текущего пользователя
      return this.user?.profile?.permissions?.includes(permission) || false
    },

    // Методы для управления ролями
    async loadCurrentUser() {
      try {
        const response = await this.$userService.getMe()
        this.currentUserId = response.data.id
      } catch (error) {
        console.error('Ошибка загрузки текущего пользователя:', error)
      }
    },

    checkIfOtherUser() {
      // Проверяем, является ли просматриваемый профиль чужим
      this.isOtherUser = this.user && this.currentUserId && this.user.id !== this.currentUserId
    },

    async loadAvailableRoles() {
      try {
        const response = await this.$roleService.getAvailableRoles()
        this.availableRoles = response.data || []
      } catch (error) {
        console.error('Ошибка загрузки ролей:', error)
        this.showNotification('Ошибка загрузки ролей', 'error')
      }
    },

    async assignRole(roleId) {
      try {
        await this.$userService.assignRole(this.user.id, roleId)
        this.showNotification(`Роль назначена пользователю ${this.user.username}`, 'success')
        await this.loadUserData()
        this.closeRoleManagement()
      } catch (error) {
        console.error('Ошибка назначения роли:', error)
        this.showNotification('Ошибка при назначении роли', 'error')
      }
    },

    async removeRole() {
      if (confirm(`Вы уверены, что хотите снять роль с пользователя ${this.user.username}?`)) {
        try {
          await this.$userService.removeRole(this.user.id)
          this.showNotification(`Роль снята с пользователя ${this.user.username}`, 'success')
          await this.loadUserData()
          this.closeRoleManagement()
        } catch (error) {
          console.error('Ошибка снятия роли:', error)
          this.showNotification('Ошибка при снятии роли', 'error')
        }
      }
    },

    closeRoleManagement() {
      this.showRoleManagement = false
    }
  }
}
</script>

<style src="@/assets/profile.css"></style>