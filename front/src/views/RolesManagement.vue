<template>
  <div class="roles-management-page">
    <!-- Заголовок страницы -->
    <div class="roles-header">
      <div class="header-content">
        <h1>
          <i class="fas fa-users-cog"></i>
          Управление ролями
        </h1>
        <p class="header-subtitle">Настройка ролей и разрешений пользователей системы</p>
      </div>
      <div class="header-actions">
        <router-link to="/profile" class="btn-secondary">
          <i class="fas fa-arrow-left"></i>
          Назад к профилю
        </router-link>
        <button 
          class="btn-primary" 
          @click="showCreateModal = true"
          v-if="hasPermission('manage_roles')"
        >
          <i class="fas fa-plus"></i>
          Создать роль
        </button>
      </div>
    </div>

    <!-- Статистика ролей -->
    <div class="roles-stats">
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-users"></i>
        </div>
        <div class="stat-content">
          <h3>{{ roles.length }}</h3>
          <p>Всего ролей</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon active">
          <i class="fas fa-check-circle"></i>
        </div>
        <div class="stat-content">
          <h3>{{ activeRolesCount }}</h3>
          <p>Активных ролей</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon users">
          <i class="fas fa-user-friends"></i>
        </div>
        <div class="stat-content">
          <h3>{{ totalUsersWithRoles }}</h3>
          <p>Пользователей с ролями</p>
        </div>
      </div>
    </div>

    <!-- Фильтры и поиск -->
    <div class="filters-section">
      <div class="filters-row">
        <div class="search-box">
          <i class="fas fa-search"></i>
          <input 
            type="text" 
            placeholder="Поиск ролей по названию или описанию..." 
            v-model="searchQuery"
            @input="filterRoles"
          >
        </div>
        <div class="filter-buttons">
          <button 
            class="btn-filter" 
            :class="{ active: activeFilter === 'all' }"
            @click="setFilter('all')"
          >
            <i class="fas fa-list"></i>
            Все роли
          </button>
          <button 
            class="btn-filter" 
            :class="{ active: activeFilter === 'active' }"
            @click="setFilter('active')"
          >
            <i class="fas fa-check-circle"></i>
            Активные
          </button>
          <button 
            class="btn-filter" 
            :class="{ active: activeFilter === 'inactive' }"
            @click="setFilter('inactive')"
          >
            <i class="fas fa-times-circle"></i>
            Неактивные
          </button>
        </div>
      </div>
    </div>

    <!-- Список ролей -->
    <div class="roles-container">
      <div v-if="isLoading" class="loading-container">
        <div class="loading-spinner">
          <i class="fas fa-spinner fa-spin"></i>
          <p>Загрузка ролей...</p>
        </div>
      </div>

      <div v-else-if="filteredRoles.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-users-cog"></i>
        </div>
        <h3>Роли не найдены</h3>
        <p>Попробуйте изменить параметры поиска или создать новую роль</p>
        <button class="btn-primary" @click="showCreateModal = true" v-if="hasPermission('manage_roles')">
          <i class="fas fa-plus"></i>
          Создать первую роль
        </button>
      </div>

      <div v-else class="roles-grid">
        <div 
          class="role-card" 
          v-for="role in filteredRoles" 
          :key="role.id"
          @click="selectRole(role)"
          :class="{ selected: selectedRole?.id === role.id }"
        >
          <div class="role-header">
            <div class="role-icon" :style="{ backgroundColor: role.color }">
              <i :class="role.icon"></i>
            </div>
            <div class="role-info">
              <h3>{{ role.display_name }}</h3>
              <p>{{ role.description }}</p>
            </div>
            <div class="role-status">
              <span 
                class="status-badge" 
                :class="{ active: role.is_active, inactive: !role.is_active }"
              >
                <i :class="role.is_active ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i>
                {{ role.is_active ? 'Активна' : 'Неактивна' }}
              </span>
            </div>
          </div>
          
          <div class="role-stats">
            <div class="stat-item">
              <i class="fas fa-users"></i>
              <span>{{ role.users_count }} пользователей</span>
            </div>
            <div class="stat-item">
              <i class="fas fa-key"></i>
              <span>{{ role.permissions?.length || 0 }} разрешений</span>
            </div>
          </div>

          <div class="role-permissions-preview" v-if="role.permissions?.length > 0">
            <div class="permissions-label">
              <i class="fas fa-key"></i>
              Разрешения:
            </div>
            <div class="permissions-tags">
              <span 
                class="permission-tag" 
                v-for="permission in role.permissions.slice(0, 3)" 
                :key="permission"
              >
                {{ getPermissionDisplayName(permission) }}
              </span>
              <span 
                v-if="role.permissions.length > 3" 
                class="permission-tag more"
              >
                +{{ role.permissions.length - 3 }} еще
              </span>
            </div>
          </div>

          <div class="role-actions" v-if="hasPermission('manage_roles')">
            <button 
              class="btn-action edit" 
              @click.stop="editRole(role)"
              title="Редактировать роль"
            >
              <i class="fas fa-edit"></i>
            </button>
            <button 
              class="btn-action danger" 
              @click.stop="deleteRole(role)"
              title="Удалить роль"
              :disabled="role.users_count > 0"
            >
              <i class="fas fa-trash"></i>
            </button>
            <button 
              class="btn-action info" 
              @click.stop="viewRoleDetails(role)"
              title="Подробная информация"
            >
              <i class="fas fa-info-circle"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Управление пользователями роли -->
    <div v-if="selectedRole" class="role-users-section">
      <div class="section-header">
        <h2>
          <i class="fas fa-users"></i>
          Пользователи с ролью "{{ selectedRole.display_name }}"
        </h2>
        <button class="btn-primary" @click="showAddUserModal = true">
          <i class="fas fa-user-plus"></i>
          Добавить пользователя
        </button>
      </div>
      
      <div v-if="roleUsers.length > 0" class="users-grid">
        <div 
          class="user-card" 
          v-for="user in roleUsers" 
          :key="user.id"
        >
          <div class="user-header">
            <div class="user-avatar">
              <i class="fas fa-user"></i>
            </div>
            <div class="user-info">
              <h3>{{ user.first_name }} {{ user.last_name }}</h3>
              <p>{{ user.email }}</p>
              <span class="user-username">@{{ user.username }}</span>
            </div>
          </div>
          <div class="user-actions">
            <button 
              class="btn-action danger" 
              @click="removeUserFromRole(user)"
              :disabled="user.id === currentUserId"
              title="Снять роль"
            >
              <i class="fas fa-user-minus"></i>
            </button>
          </div>
        </div>
      </div>
      
      <div v-else class="empty-users">
        <div class="empty-icon">
          <i class="fas fa-users"></i>
        </div>
        <h3>Нет пользователей с этой ролью</h3>
        <p>Добавьте пользователей, чтобы назначить им эту роль</p>
      </div>
    </div>

    <!-- Модальное окно добавления пользователя к роли -->
    <div v-if="showAddUserModal" class="modal-overlay" @click="closeAddUserModal">
      <div class="modal-content add-user-modal" @click.stop>
        <div class="modal-header">
          <h2>
            <i class="fas fa-user-plus"></i>
            Добавить пользователя к роли "{{ selectedRole?.display_name }}"
          </h2>
          <button class="close-btn" @click="closeAddUserModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="add-user-content">
          <div class="search-section">
            <div class="search-box">
              <i class="fas fa-search"></i>
              <input 
                type="text" 
                placeholder="Поиск пользователей по имени, email или username..." 
                v-model="userSearchQuery"
                @input="searchUsers"
              >
            </div>
          </div>

          <div v-if="isSearchingUsers" class="loading-container">
            <div class="loading-spinner">
              <i class="fas fa-spinner fa-spin"></i>
              <p>Поиск пользователей...</p>
            </div>
          </div>

          <div v-else-if="searchResults.length > 0" class="search-results">
            <div 
              class="user-search-item" 
              v-for="user in searchResults" 
              :key="user.id"
              @click="assignRoleToUser(user)"
            >
              <div class="user-avatar-small">
                <i class="fas fa-user"></i>
              </div>
              <div class="user-details">
                <h4>{{ user.first_name }} {{ user.last_name }}</h4>
                <p>{{ user.email }}</p>
                <span class="user-username">@{{ user.username }}</span>
              </div>
              <div class="user-role" v-if="user.role">
                <span class="role-badge" :style="{ backgroundColor: user.role.color }">
                  {{ user.role.display_name }}
                </span>
              </div>
              <div class="assign-icon">
                <i class="fas fa-plus"></i>
              </div>
            </div>
          </div>

          <div v-else-if="userSearchQuery" class="no-results">
            <i class="fas fa-search"></i>
            <p>Пользователи не найдены</p>
          </div>

          <div v-else class="search-prompt">
            <i class="fas fa-search"></i>
            <p>Введите имя пользователя для поиска</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно создания/редактирования роли -->
    <div v-if="showCreateModal || showEditModal" class="modal-overlay" @click="closeModals">
      <div class="modal-content role-modal" @click.stop>
        <div class="modal-header">
          <h2>
            <i class="fas fa-users-cog"></i>
            {{ showCreateModal ? 'Создание новой роли' : 'Редактирование роли' }}
          </h2>
          <button class="close-btn" @click="closeModals">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <form @submit.prevent="saveRole" class="role-form">
          <div class="form-section">
            <h3>
              <i class="fas fa-info-circle"></i>
              Основная информация
            </h3>
            <div class="form-grid">
              <div class="form-group">
                <label for="roleName">
                  <i class="fas fa-tag"></i>
                  Название роли *
                </label>
                <input 
                  type="text" 
                  id="roleName" 
                  v-model="roleForm.name" 
                  required
                  placeholder="manager"
                  :class="{ error: errors.name }"
                >
                <span v-if="errors.name" class="error-message">{{ errors.name }}</span>
              </div>
              <div class="form-group">
                <label for="displayName">
                  <i class="fas fa-eye"></i>
                  Отображаемое название *
                </label>
                <input 
                  type="text" 
                  id="displayName" 
                  v-model="roleForm.display_name" 
                  required
                  placeholder="Руководитель"
                  :class="{ error: errors.display_name }"
                >
                <span v-if="errors.display_name" class="error-message">{{ errors.display_name }}</span>
              </div>
              <div class="form-group">
                <label for="roleColor">
                  <i class="fas fa-palette"></i>
                  Цвет роли
                </label>
                <div class="color-input-group">
                  <input 
                    type="color" 
                    id="roleColor" 
                    v-model="roleForm.color"
                    class="color-picker"
                  >
                  <input 
                    type="text" 
                    v-model="roleForm.color"
                    class="color-text"
                    placeholder="#6c757d"
                  >
                </div>
              </div>
              <div class="form-group">
                <label for="roleIcon">
                  <i class="fas fa-icons"></i>
                  Иконка роли
                </label>
                <div class="icon-input-group">
                  <input 
                    type="text" 
                    id="roleIcon" 
                    v-model="roleForm.icon"
                    placeholder="fas fa-user-tie"
                    class="icon-input"
                  >
                  <div class="icon-preview">
                    <i :class="roleForm.icon || 'fas fa-user'"></i>
                  </div>
                </div>
              </div>
            </div>
            <div class="form-group">
              <label for="description">
                <i class="fas fa-align-left"></i>
                Описание роли
              </label>
              <textarea 
                id="description" 
                v-model="roleForm.description"
                rows="3"
                placeholder="Подробное описание роли и её функций в системе"
              ></textarea>
            </div>
            <div class="form-group">
              <label class="checkbox-label">
                <input 
                  type="checkbox" 
                  v-model="roleForm.is_active"
                >
                <span class="checkmark"></span>
                <span class="checkbox-text">
                  <i class="fas fa-toggle-on"></i>
                  Роль активна
                </span>
              </label>
            </div>
          </div>

          <div class="form-section">
            <h3>
              <i class="fas fa-key"></i>
              Настройка разрешений
            </h3>
            <div class="permissions-sections">
              <div class="permission-category" v-for="category in permissionCategories" :key="category.name">
                <div class="category-header">
                  <h4>{{ category.display_name }}</h4>
                  <button 
                    type="button" 
                    class="btn-toggle-all"
                    @click="toggleCategoryPermissions(category)"
                  >
                    {{ isCategoryFullySelected(category) ? 'Снять все' : 'Выбрать все' }}
                  </button>
                </div>
                <div class="permission-list">
                  <label 
                    class="permission-checkbox" 
                    v-for="permission in category.permissions" 
                    :key="permission.name"
                  >
                    <input 
                      type="checkbox" 
                      :value="permission.name"
                      v-model="roleForm.permissions"
                    >
                    <span class="checkmark"></span>
                    <div class="permission-info">
                      <span class="permission-name">{{ permission.display_name }}</span>
                      <span class="permission-desc">{{ permission.description }}</span>
                    </div>
                  </label>
                </div>
              </div>
            </div>
          </div>

          <div class="form-actions">
            <button type="button" class="btn-secondary" @click="closeModals">
              <i class="fas fa-times"></i>
              Отменить
            </button>
            <button type="submit" class="btn-primary" :disabled="isSaving">
              <i v-if="isSaving" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-save"></i>
              {{ isSaving ? 'Сохранение...' : 'Сохранить роль' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Модальное окно детальной информации о роли -->
    <div v-if="showDetailsModal" class="modal-overlay" @click="closeDetailsModal">
      <div class="modal-content details-modal" @click.stop>
        <div class="modal-header">
          <h2>
            <i :class="selectedRole?.icon" :style="{ color: selectedRole?.color }"></i>
            {{ selectedRole?.display_name }}
          </h2>
          <button class="close-btn" @click="closeDetailsModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="role-details-content" v-if="selectedRole">
          <div class="role-summary">
            <div class="role-icon-large" :style="{ backgroundColor: selectedRole.color }">
              <i :class="selectedRole.icon"></i>
            </div>
            <div class="role-summary-info">
              <h3>{{ selectedRole.display_name }}</h3>
              <p>{{ selectedRole.description }}</p>
              <div class="role-meta">
                <span class="meta-item">
                  <i class="fas fa-users"></i>
                  {{ selectedRole.users_count }} пользователей
                </span>
                <span class="meta-item">
                  <i class="fas fa-key"></i>
                  {{ selectedRole.permissions?.length || 0 }} разрешений
                </span>
                <span class="meta-item">
                  <i class="fas fa-toggle-on"></i>
                  {{ selectedRole.is_active ? 'Активна' : 'Неактивна' }}
                </span>
              </div>
            </div>
          </div>

          <div class="permissions-detailed" v-if="selectedRole.permissions?.length > 0">
            <h4>
              <i class="fas fa-key"></i>
              Все разрешения роли
            </h4>
            <div class="permissions-grid">
              <div 
                class="permission-item-detailed" 
                v-for="permission in selectedRole.permissions" 
                :key="permission"
              >
                <i class="fas fa-check-circle"></i>
                <span>{{ getPermissionDisplayName(permission) }}</span>
              </div>
            </div>
          </div>

          <div class="role-actions-detailed" v-if="hasPermission('manage_roles')">
            <button class="btn-primary" @click="editRole(selectedRole)">
              <i class="fas fa-edit"></i>
              Редактировать роль
            </button>
            <button 
              class="btn-danger" 
              @click="deleteRole(selectedRole)"
              :disabled="selectedRole.users_count > 0"
            >
              <i class="fas fa-trash"></i>
              Удалить роль
            </button>
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
  </div>
</template>

<script>
export default {
  name: 'RolesManagement',
  data() {
    return {
      isLoading: false,
      roles: [],
      filteredRoles: [],
      searchQuery: '',
      activeFilter: 'all',
      showCreateModal: false,
      showEditModal: false,
      showDetailsModal: false,
      showAddUserModal: false,
      isSaving: false,
      selectedRole: null,
      roleUsers: [],
      userSearchQuery: '',
      searchResults: [],
      isSearchingUsers: false,
      currentUserId: null,
      roleForm: {
        name: '',
        display_name: '',
        description: '',
        color: '#6c757d',
        icon: 'fas fa-user',
        permissions: [],
        is_active: true
      },
      permissionCategories: [],
      errors: {},
      notification: {
        show: false,
        type: 'success',
        message: '',
        icon: 'fas fa-check-circle'
      }
    }
  },
  computed: {
    activeRolesCount() {
      return this.roles.filter(role => role.is_active).length
    },
    totalUsersWithRoles() {
      return this.roles.reduce((total, role) => total + role.users_count, 0)
    }
  },
    async created() {
      await this.loadRoles()
      await this.loadPermissions()
      await this.loadCurrentUser()
    },
  methods: {
    async loadRoles() {
      try {
        this.isLoading = true
        const response = await this.$roleService.getAll()
        this.roles = response.data || []
        this.filteredRoles = [...this.roles]
      } catch (error) {
        console.error('Ошибка загрузки ролей:', error)
        this.showNotification('Ошибка загрузки ролей', 'error')
      } finally {
        this.isLoading = false
      }
    },

    async loadPermissions() {
      try {
        const response = await this.$roleService.getPermissionsList()
        const permissions = response.data || []
        
        // Группируем разрешения по категориям
        const categories = {}
        permissions.forEach(permission => {
          if (!categories[permission.category]) {
            categories[permission.category] = {
              name: permission.category,
              display_name: this.getCategoryDisplayName(permission.category),
              permissions: []
            }
          }
          categories[permission.category].permissions.push(permission)
        })
        
        this.permissionCategories = Object.values(categories)
      } catch (error) {
        console.error('Ошибка загрузки разрешений:', error)
      }
    },

    getCategoryDisplayName(category) {
      const names = {
        'documents': 'Документы',
        'processes': 'Процессы',
        'tasks': 'Задачи',
        'system': 'Система'
      }
      return names[category] || category
    },

    filterRoles() {
      let filtered = [...this.roles]

      // Фильтр по статусу
      if (this.activeFilter === 'active') {
        filtered = filtered.filter(role => role.is_active)
      } else if (this.activeFilter === 'inactive') {
        filtered = filtered.filter(role => !role.is_active)
      }

      // Поиск
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(role => 
          role.display_name.toLowerCase().includes(query) ||
          role.description.toLowerCase().includes(query) ||
          role.name.toLowerCase().includes(query)
        )
      }

      this.filteredRoles = filtered
    },

    setFilter(filter) {
      this.activeFilter = filter
      this.filterRoles()
    },

    selectRole(role) {
      this.selectedRole = role
      this.loadRoleUsers()
    },

    async loadCurrentUser() {
      try {
        const response = await this.$userService.getMe()
        this.currentUserId = response.data.id
      } catch (error) {
        console.error('Ошибка загрузки текущего пользователя:', error)
      }
    },

    async loadRoleUsers() {
      if (!this.selectedRole) return
      
      try {
        const response = await this.$roleService.getUsersByRole(this.selectedRole.id)
        this.roleUsers = response.data || []
      } catch (error) {
        console.error('Ошибка загрузки пользователей роли:', error)
        this.showNotification('Ошибка загрузки пользователей роли', 'error')
      }
    },

    async searchUsers() {
      if (!this.userSearchQuery.trim()) {
        this.searchResults = []
        return
      }

      try {
        this.isSearchingUsers = true
        const response = await this.$userService.search(this.userSearchQuery)
        this.searchResults = response.data || []
      } catch (error) {
        console.error('Ошибка поиска пользователей:', error)
        this.showNotification('Ошибка поиска пользователей', 'error')
      } finally {
        this.isSearchingUsers = false
      }
    },

    async assignRoleToUser(user) {
      try {
        await this.$userService.assignRole(user.id, this.selectedRole.id)
        this.showNotification(`Роль "${this.selectedRole.display_name}" назначена пользователю ${user.username}`, 'success')
        await this.loadRoleUsers()
        this.closeAddUserModal()
      } catch (error) {
        console.error('Ошибка назначения роли:', error)
        this.showNotification('Ошибка при назначении роли', 'error')
      }
    },

    async removeUserFromRole(user) {
      if (confirm(`Вы уверены, что хотите снять роль "${this.selectedRole.display_name}" с пользователя ${user.username}?`)) {
        try {
          await this.$roleService.removeUserFromRole(this.selectedRole.id, user.id)
          this.showNotification(`Роль снята с пользователя ${user.username}`, 'success')
          await this.loadRoleUsers()
        } catch (error) {
          console.error('Ошибка снятия роли:', error)
          this.showNotification('Ошибка при снятии роли', 'error')
        }
      }
    },

    closeAddUserModal() {
      this.showAddUserModal = false
      this.userSearchQuery = ''
      this.searchResults = []
    },

    editRole(role) {
      this.selectedRole = role
      this.roleForm = {
        name: role.name,
        display_name: role.display_name,
        description: role.description,
        color: role.color,
        icon: role.icon,
        permissions: [...(role.permissions || [])],
        is_active: role.is_active
      }
      this.showEditModal = true
      this.closeDetailsModal()
    },

    viewRoleDetails(role) {
      this.selectedRole = role
      this.showDetailsModal = true
    },

    async deleteRole(role) {
      if (role.users_count > 0) {
        this.showNotification('Нельзя удалить роль, которая назначена пользователям', 'error')
        return
      }

      if (confirm(`Вы уверены, что хотите удалить роль "${role.display_name}"?`)) {
        try {
          await this.$roleService.delete(role.id)
          this.showNotification('Роль успешно удалена', 'success')
          await this.loadRoles()
          this.selectedRole = null
        } catch (error) {
          console.error('Ошибка удаления роли:', error)
          this.showNotification('Ошибка при удалении роли', 'error')
        }
      }
    },

    async saveRole() {
      if (!this.validateForm()) {
        this.showNotification('Пожалуйста, исправьте ошибки в форме', 'error')
        return
      }

      try {
        this.isSaving = true
        
        if (this.showCreateModal) {
          await this.$roleService.create(this.roleForm)
          this.showNotification('Роль успешно создана', 'success')
        } else {
          await this.$roleService.update(this.selectedRole.id, this.roleForm)
          this.showNotification('Роль успешно обновлена', 'success')
        }
        
        this.closeModals()
        await this.loadRoles()
      } catch (error) {
        console.error('Ошибка сохранения роли:', error)
        this.showNotification('Ошибка при сохранении роли', 'error')
      } finally {
        this.isSaving = false
      }
    },

    validateForm() {
      this.errors = {}

      if (!this.roleForm.name?.trim()) {
        this.errors.name = 'Название роли обязательно'
      }

      if (!this.roleForm.display_name?.trim()) {
        this.errors.display_name = 'Отображаемое название обязательно'
      }

      return Object.keys(this.errors).length === 0
    },

    toggleCategoryPermissions(category) {
      const categoryPermissions = category.permissions.map(p => p.name)
      const isFullySelected = categoryPermissions.every(p => this.roleForm.permissions.includes(p))
      
      if (isFullySelected) {
        // Снимаем все разрешения категории
        this.roleForm.permissions = this.roleForm.permissions.filter(p => !categoryPermissions.includes(p))
      } else {
        // Добавляем все разрешения категории
        categoryPermissions.forEach(permission => {
          if (!this.roleForm.permissions.includes(permission)) {
            this.roleForm.permissions.push(permission)
          }
        })
      }
    },

    isCategoryFullySelected(category) {
      const categoryPermissions = category.permissions.map(p => p.name)
      return categoryPermissions.every(p => this.roleForm.permissions.includes(p))
    },

    closeModals() {
      this.showCreateModal = false
      this.showEditModal = false
      this.selectedRole = null
      this.roleForm = {
        name: '',
        display_name: '',
        description: '',
        color: '#6c757d',
        icon: 'fas fa-user',
        permissions: [],
        is_active: true
      }
      this.errors = {}
    },

    closeDetailsModal() {
      this.showDetailsModal = false
      this.selectedRole = null
    },

    hasPermission(permission) {
      // Проверяем разрешения текущего пользователя
      return this.$store?.state?.user?.profile?.permissions?.includes(permission) || false
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

    showNotification(message, type = 'success') {
      this.notification = {
        show: true,
        type,
        message,
        icon: type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle'
      }

      setTimeout(() => {
        this.hideNotification()
      }, 5000)
    },

    hideNotification() {
      this.notification.show = false
    }
  }
}
</script>

<style scoped>
.roles-management-page {
  padding: 2rem;
  background-color: var(--bg-page);
  min-height: 100vh;
}

.roles-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  padding: 0.5rem 0;
}

.header-content h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.5rem 0;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-content h1 i {
  color: var(--primary-color);
  font-size: 2.2rem;
}

.header-subtitle {
  color: var(--text-secondary);
  font-size: 1.1rem;
  margin: 0;
  font-weight: 400;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

/* Статистика ролей */
.roles-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-color);
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: var(--border-radius-lg);
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
}

.stat-icon.active {
  background: linear-gradient(135deg, var(--success-color), #28a745);
}

.stat-icon.users {
  background: linear-gradient(135deg, var(--warning-color), #ffc107);
}

.stat-content h3 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.25rem 0;
}

.stat-content p {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin: 0;
  font-weight: 500;
}

/* Фильтры */
.filters-section {
  background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-color);
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.filters-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1.5rem;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 500px;
}

.search-box i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
  font-size: 1rem;
}

.search-box input {
  width: 100%;
  padding: 1rem 1rem 1rem 3rem;
  border: 2px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  background-color: var(--bg-primary);
  color: var(--text-primary);
  font-size: 1rem;
  transition: all 0.3s ease;
}

.search-box input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
  background-color: white;
}

.filter-buttons {
  display: flex;
  gap: 0.75rem;
}

.btn-filter {
  padding: 0.75rem 1.25rem;
  border: 2px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  background-color: var(--bg-primary);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-filter:hover {
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  border-color: var(--primary-color);
  transform: translateY(-1px);
}

.btn-filter.active {
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
  color: white;
  border-color: var(--primary-color);
  box-shadow: var(--shadow-md);
}

/* Контейнер ролей */
.roles-container {
  min-height: 400px;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.loading-spinner {
  text-align: center;
  color: var(--text-secondary);
}

.loading-spinner i {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: var(--primary-color);
}

.loading-spinner p {
  font-size: 1.1rem;
  margin: 0;
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 4rem;
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
}

.empty-state h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 1rem 0;
}

.empty-state p {
  font-size: 1rem;
  margin: 0 0 2rem 0;
}

/* Сетка ролей */
.roles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
}

.role-card {
  background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-md);
  border: 2px solid var(--border-color);
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.role-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--primary-color), var(--primary-dark));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.role-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-xl);
  border-color: var(--primary-color);
}

.role-card:hover::before {
  opacity: 1;
}

.role-card.selected {
  border-color: var(--primary-color);
  box-shadow: var(--shadow-lg);
}

.role-card.selected::before {
  opacity: 1;
}

.role-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
}

.role-icon {
  width: 50px;
  height: 50px;
  border-radius: var(--border-radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.3rem;
  flex-shrink: 0;
  box-shadow: var(--shadow-sm);
}

.role-info {
  flex: 1;
}

.role-info h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.5rem 0;
}

.role-info p {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.4;
}

.role-status {
  flex-shrink: 0;
}

.status-badge {
  padding: 0.5rem 0.75rem;
  border-radius: var(--border-radius-md);
  font-size: 0.8rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.status-badge.active {
  background: linear-gradient(135deg, var(--success-color), #28a745);
  color: white;
}

.status-badge.inactive {
  background: linear-gradient(135deg, var(--danger-color), #dc3545);
  color: white;
}

.role-stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.stat-item i {
  color: var(--primary-color);
  font-size: 0.9rem;
}

.role-permissions-preview {
  margin-bottom: 1rem;
}

.permissions-label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-weight: 500;
}

.permissions-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.permission-tag {
  background-color: var(--primary-color);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: var(--border-radius-sm);
  font-size: 0.75rem;
  font-weight: 500;
}

.permission-tag.more {
  background-color: var(--text-secondary);
}

.role-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.btn-action {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: var(--border-radius-md);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
}

.btn-action.edit {
  background-color: var(--primary-color);
  color: white;
}

.btn-action.edit:hover {
  background-color: var(--primary-dark);
  transform: scale(1.1);
}

.btn-action.danger {
  background-color: var(--danger-color);
  color: white;
}

.btn-action.danger:hover {
  background-color: #dc3545;
  transform: scale(1.1);
}

.btn-action.danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.btn-action.info {
  background-color: var(--info-color);
  color: white;
}

.btn-action.info:hover {
  background-color: #17a2b8;
  transform: scale(1.1);
}

/* Модальные окна */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 2rem;
}

.modal-content {
  background-color: var(--bg-primary);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-xl);
  border: 1px solid var(--border-color);
  max-height: 90vh;
  overflow-y: auto;
  animation: modalSlideIn 0.3s ease;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-50px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-color);
  background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
}

.modal-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.close-btn {
  width: 40px;
  height: 40px;
  border: none;
  border-radius: var(--border-radius-md);
  background-color: var(--bg-secondary);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background-color: var(--danger-color);
  color: white;
  transform: scale(1.1);
}

.role-modal {
  max-width: 900px;
  width: 100%;
}

.details-modal {
  max-width: 700px;
  width: 100%;
}

.role-form {
  padding: 2rem;
}

.form-section {
  margin-bottom: 2.5rem;
}

.form-section h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 1.5rem 0;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid var(--border-color);
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-group input,
.form-group textarea {
  padding: 1rem;
  border: 2px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  background-color: var(--bg-primary);
  color: var(--text-primary);
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
  background-color: white;
}

.form-group input.error {
  border-color: var(--danger-color);
}

.error-message {
  color: var(--danger-color);
  font-size: 0.9rem;
  margin-top: 0.5rem;
  font-weight: 500;
}

.color-input-group {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.color-picker {
  width: 60px;
  height: 50px;
  border: none;
  border-radius: var(--border-radius-md);
  cursor: pointer;
}

.color-text {
  flex: 1;
}

.icon-input-group {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.icon-input {
  flex: 1;
}

.icon-preview {
  width: 50px;
  height: 50px;
  border: 2px solid var(--border-color);
  border-radius: var(--border-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 1.2rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  font-weight: 500;
}

.checkbox-label input {
  width: 20px;
  height: 20px;
}

.checkbox-text {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.permissions-sections {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.permission-category {
  background-color: var(--bg-secondary);
  border-radius: var(--border-radius-lg);
  padding: 1.5rem;
  border: 1px solid var(--border-color);
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.category-header h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.btn-toggle-all {
  padding: 0.5rem 1rem;
  border: 1px solid var(--primary-color);
  border-radius: var(--border-radius-md);
  background-color: transparent;
  color: var(--primary-color);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  font-weight: 500;
}

.btn-toggle-all:hover {
  background-color: var(--primary-color);
  color: white;
}

.permission-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.permission-checkbox {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  cursor: pointer;
  padding: 1rem;
  background-color: var(--bg-primary);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

.permission-checkbox:hover {
  background-color: var(--primary-color);
  color: white;
  transform: translateX(4px);
}

.permission-checkbox input {
  margin: 0;
  width: 18px;
  height: 18px;
}

.permission-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.permission-name {
  font-weight: 600;
  font-size: 0.95rem;
}

.permission-desc {
  font-size: 0.85rem;
  opacity: 0.8;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
}

/* Детальная информация о роли */
.role-details-content {
  padding: 2rem;
}

.role-summary {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background-color: var(--bg-secondary);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-color);
}

.role-icon-large {
  width: 80px;
  height: 80px;
  border-radius: var(--border-radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2rem;
  flex-shrink: 0;
  box-shadow: var(--shadow-md);
}

.role-summary-info {
  flex: 1;
}

.role-summary-info h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.5rem 0;
}

.role-summary-info p {
  font-size: 1rem;
  color: var(--text-secondary);
  margin: 0 0 1rem 0;
  line-height: 1.5;
}

.role-meta {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.meta-item i {
  color: var(--primary-color);
}

.permissions-detailed {
  margin-bottom: 2rem;
}

.permissions-detailed h4 {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 1rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.permissions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 0.75rem;
}

.permission-item-detailed {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background-color: var(--bg-secondary);
  border-radius: var(--border-radius-md);
  border: 1px solid var(--border-color);
}

.permission-item-detailed i {
  color: var(--success-color);
  font-size: 1rem;
}

.permission-item-detailed span {
  font-weight: 500;
  color: var(--text-primary);
}

.role-actions-detailed {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn-danger {
  background-color: var(--danger-color);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: var(--border-radius-lg);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-danger:hover {
  background-color: #dc3545;
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.btn-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* Уведомления */
.notification {
  position: fixed;
  top: 2rem;
  right: 2rem;
  background-color: var(--bg-primary);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-xl);
  border: 1px solid var(--border-color);
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  z-index: 1001;
  max-width: 400px;
  animation: slideInRight 0.3s ease;
}

.notification.success {
  border-left: 4px solid var(--success-color);
}

.notification.error {
  border-left: 4px solid var(--danger-color);
}

.notification i {
  font-size: 1.2rem;
}

.notification.success i {
  color: var(--success-color);
}

.notification.error i {
  color: var(--danger-color);
}

.notification span {
  flex: 1;
  color: var(--text-primary);
  font-weight: 500;
}

.notification-close {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: var(--border-radius-sm);
  transition: background-color 0.2s ease;
}

.notification-close:hover {
  background-color: var(--bg-secondary);
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Стили для управления пользователями */
.role-users-section {
  margin-top: 2rem;
  background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-color);
  padding: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid var(--border-color);
}

.section-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.users-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.user-card {
  background-color: var(--bg-primary);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-color);
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.user-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.user-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.user-avatar {
  width: 50px;
  height: 50px;
  border-radius: var(--border-radius-lg);
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
}

.user-info h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.25rem 0;
}

.user-info p {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin: 0 0 0.25rem 0;
}

.user-username {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.user-actions {
  display: flex;
  justify-content: flex-end;
}

.empty-users {
  text-align: center;
  padding: 3rem 2rem;
  color: var(--text-secondary);
}

.empty-users .empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: var(--text-secondary);
}

.empty-users h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.5rem 0;
}

.empty-users p {
  font-size: 1rem;
  margin: 0;
}

/* Модальное окно добавления пользователя */
.add-user-modal {
  max-width: 600px;
  width: 100%;
}

.add-user-content {
  padding: 2rem;
}

.search-section {
  margin-bottom: 2rem;
}

.search-results {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-lg);
}

.user-search-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.3s ease;
}

.user-search-item:hover {
  background-color: var(--bg-secondary);
}

.user-search-item:last-child {
  border-bottom: none;
}

.user-avatar-small {
  width: 40px;
  height: 40px;
  border-radius: var(--border-radius-md);
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1rem;
}

.user-details {
  flex: 1;
}

.user-details h4 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.25rem 0;
}

.user-details p {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin: 0 0 0.25rem 0;
}

.user-role {
  flex-shrink: 0;
}

.role-badge {
  padding: 0.25rem 0.75rem;
  border-radius: var(--border-radius-md);
  color: white;
  font-size: 0.8rem;
  font-weight: 500;
}

.assign-icon {
  width: 30px;
  height: 30px;
  border-radius: var(--border-radius-md);
  background-color: var(--success-color);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.9rem;
}

.no-results,
.search-prompt {
  text-align: center;
  padding: 3rem 2rem;
  color: var(--text-secondary);
}

.no-results i,
.search-prompt i {
  font-size: 2rem;
  margin-bottom: 1rem;
  color: var(--text-secondary);
}

.no-results p,
.search-prompt p {
  font-size: 1rem;
  margin: 0;
}

/* Адаптивность */
@media (max-width: 1200px) {
  .roles-grid {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  }
}

@media (max-width: 768px) {
  .roles-management-page {
    padding: 1rem;
  }
  
  .roles-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .header-content h1 {
    font-size: 2rem;
  }
  
  .roles-stats {
    grid-template-columns: 1fr;
  }
  
  .filters-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .roles-grid {
    grid-template-columns: 1fr;
  }
  
  .role-modal,
  .details-modal {
    max-width: 95vw;
    margin: 1rem;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .role-summary {
    flex-direction: column;
    text-align: center;
  }
  
  .role-meta {
    justify-content: center;
  }
  
  .permissions-grid {
    grid-template-columns: 1fr;
  }
  
  .role-actions-detailed {
    flex-direction: column;
  }
}

@media (max-width: 480px) {
  .role-card {
    padding: 1rem;
  }
  
  .role-header {
    flex-direction: column;
    text-align: center;
  }
  
  .role-actions {
    justify-content: center;
  }
  
  .modal-content {
    margin: 0.5rem;
  }
  
  .role-form {
    padding: 1rem;
  }
}
</style>
