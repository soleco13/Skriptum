<template>
  <div class="active-users" v-if="users.length > 0">
    <div class="users-header">
      <i class="fas fa-users"></i>
      <span>Активные пользователи ({{ users.length }})</span>
    </div>
    
    <div class="users-list">
      <div 
        v-for="user in users" 
        :key="user.user_id"
        class="user-item"
        :class="{ 'current-user': isCurrentUser(user.user_id) }"
      >
        <div class="user-avatar" :style="{ backgroundColor: getUserColor(user.user_id) }">
          <i class="fas fa-user"></i>
        </div>
        <div class="user-info">
          <div class="user-name">{{ user.full_name || user.username }}</div>
          <div class="user-status">
            <div class="status-indicator online"></div>
            <span>Онлайн</span>
          </div>
        </div>
        <div v-if="isCurrentUser(user.user_id)" class="current-user-badge">
          <i class="fas fa-crown"></i>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ActiveUsers',
  props: {
    users: {
      type: Array,
      default: () => []
    },
    currentUserId: {
      type: [String, Number],
      default: null
    }
  },
  methods: {
    isCurrentUser(userId) {
      return this.currentUserId && userId == this.currentUserId;
    },
    
    getUserColor(userId) {
      const colors = [
        '#3B82F6', '#10B981', '#F59E0B', '#EF4444', 
        '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'
      ];
      const index = userId % colors.length;
      return colors[index];
    }
  }
}
</script>

<style scoped>
.active-users {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 1rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.users-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
}

.users-header i {
  color: #10B981;
  font-size: 0.75rem;
}

.users-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.user-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  border-radius: 8px;
  transition: all 0.2s ease;
  position: relative;
}

.user-item:hover {
  background: rgba(59, 130, 246, 0.05);
}

.user-item.current-user {
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.75rem;
  flex-shrink: 0;
}

.user-info {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-status {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: #6B7280;
  margin-top: 0.125rem;
}

.status-indicator {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-indicator.online {
  background: #10B981;
  box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
}

.current-user-badge {
  color: #F59E0B;
  font-size: 0.75rem;
  flex-shrink: 0;
}

/* Анимация для новых пользователей */
.user-item {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Адаптивность */
@media (max-width: 768px) {
  .active-users {
    padding: 0.75rem;
  }
  
  .user-item {
    padding: 0.375rem;
  }
  
  .user-avatar {
    width: 28px;
    height: 28px;
    font-size: 0.625rem;
  }
  
  .user-name {
    font-size: 0.8125rem;
  }
  
  .user-status {
    font-size: 0.6875rem;
  }
}
</style>
