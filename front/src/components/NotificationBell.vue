<template>
  <div class="notification-bell">
    <!-- Кнопка уведомлений -->
    <button 
      @click="toggleDropdown" 
      class="notification-button"
      :class="{ 'has-notifications': unreadCount > 0 }"
    >
      <i class="fas fa-bell"></i>
      <span v-if="unreadCount > 0" class="notification-badge">{{ unreadCount }}</span>
    </button>

    <!-- Выпадающий список уведомлений -->
    <div v-if="isDropdownOpen" class="notification-dropdown">
      <div class="notification-header">
        <h3>Уведомления</h3>
        <div class="notification-actions">
          <button 
            v-if="unreadCount > 0" 
            @click="markAllAsRead" 
            class="btn-mark-all"
            :disabled="isMarkingAll"
          >
            <i class="fas fa-check-double"></i>
            {{ isMarkingAll ? 'Помечаю...' : 'Прочитать все' }}
          </button>
          <button 
            v-if="notifications.length > 0" 
            @click="clearAllNotifications" 
            class="btn-clear-all"
            :disabled="isClearing"
          >
            <i class="fas fa-trash"></i>
            {{ isClearing ? 'Очищаю...' : 'Очистить все' }}
          </button>
          <button @click="refreshNotifications" class="btn-refresh">
            <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
          </button>
        </div>
      </div>

      <div class="notification-list">
        <div v-if="isLoading" class="loading">
          <i class="fas fa-spinner fa-spin"></i>
          <span>Загрузка...</span>
        </div>
        
        <div v-else-if="notifications.length === 0" class="empty">
          <i class="fas fa-bell-slash"></i>
          <span>Нет уведомлений</span>
        </div>

        <div v-else>
          <div 
            v-for="notification in notifications" 
            :key="notification.id"
            class="notification-item"
            :class="{ 'unread': !notification.is_read }"
            @click="handleNotificationClick(notification)"
          >
            <div class="notification-icon">
              <i :class="notification.icon" :style="{ color: getNotificationColor(notification.type) }"></i>
            </div>
            <div class="notification-content">
              <div v-if="notification.title" class="notification-title">{{ notification.title }}</div>
              <div class="notification-message">{{ notification.message }}</div>
              <div class="notification-meta">
                <span class="notification-time">{{ formatTime(notification.created_at) }}</span>
                <span class="notification-type">{{ notification.type_display }}</span>
              </div>
            </div>
            <div v-if="!notification.is_read" class="notification-dot"></div>
          </div>
        </div>
      </div>

      <div v-if="notifications.length > 0" class="notification-footer">
        <button @click="viewAllNotifications" class="btn-view-all">
          Показать все уведомления
        </button>
      </div>
    </div>

    <!-- Overlay для закрытия dropdown -->
    <div 
      v-if="isDropdownOpen" 
      @click="closeDropdown" 
      class="notification-overlay"
    ></div>
  </div>
</template>

<script>
import axios from 'axios';
import notificationService from '@/api/notifications';
import { API_BASE_URL } from '@/api/config';

export default {
  name: 'NotificationBell',
  data() {
    return {
      isDropdownOpen: false,
      notifications: [],
      unreadCount: 0,
      isLoading: false,
      isMarkingAll: false,
      isClearing: false,
      refreshInterval: null
    };
  },
  mounted() {
    this.setupWebSocket();
    this.loadNotifications();
    
    // Автообновление каждые 30 секунд
    this.refreshInterval = setInterval(() => {
      if (!this.isDropdownOpen) {
        this.loadNotifications();
      }
    }, 30000);
  },
  beforeUnmount() {
    this.cleanup();
  },
  methods: {
    setupWebSocket() {
      const token = localStorage.getItem('token') || sessionStorage.getItem('token');
      if (token) {
        notificationService.connect(token);
        
        // Подписываемся на события
        notificationService.on('new_notification', this.handleNewNotification);
        notificationService.on('unread_count', this.handleUnreadCount);
        notificationService.on('notifications_list', this.handleNotificationsList);
        notificationService.on('connected', this.handleConnected);
        notificationService.on('disconnected', this.handleDisconnected);
        notificationService.on('error', this.handleError);
      }
    },

    async loadNotifications() {
      this.isLoading = true;
      try {
        const token = localStorage.getItem('token') || sessionStorage.getItem('token');
        const response = await axios.get(`${API_BASE_URL}/notifications/recent/?limit=10`, {
          headers: {
            'Authorization': `JWT ${token}`
          }
        });
        this.notifications = response.data;
        this.updateUnreadCount();
      } catch (error) {
        console.error('Ошибка загрузки уведомлений:', error);
        console.error('Ошибка загрузки уведомлений');
      } finally {
        this.isLoading = false;
      }
    },

    async refreshNotifications() {
      await this.loadNotifications();
    },

    async markAsRead(notificationId) {
      try {
        const token = localStorage.getItem('token') || sessionStorage.getItem('token');
        await axios.patch(`${API_BASE_URL}/notifications/${notificationId}/mark_as_read/`, {}, {
          headers: {
            'Authorization': `JWT ${token}`
          }
        });
        
        // Обновляем локальное состояние
        const notification = this.notifications.find(n => n.id === notificationId);
        if (notification) {
          notification.is_read = true;
        }
        this.updateUnreadCount();
      } catch (error) {
        console.error('Ошибка пометки уведомления как прочитанного:', error);
      }
    },

    async markAllAsRead() {
      this.isMarkingAll = true;
      try {
        const token = localStorage.getItem('token') || sessionStorage.getItem('token');
        await axios.patch(`${API_BASE_URL}/notifications/mark_all_as_read/`, {}, {
          headers: {
            'Authorization': `JWT ${token}`
          }
        });
        
        // Обновляем локальное состояние
        this.notifications.forEach(notification => {
          notification.is_read = true;
        });
        this.unreadCount = 0;
        
        console.log('Все уведомления помечены как прочитанные');
      } catch (error) {
        console.error('Ошибка пометки всех уведомлений как прочитанных:', error);
        console.error('Ошибка пометки уведомлений');
      } finally {
        this.isMarkingAll = false;
      }
    },

    async clearAllNotifications() {
      this.isClearing = true;
      try {
        const token = localStorage.getItem('token') || sessionStorage.getItem('token');
        await axios.delete(`${API_BASE_URL}/notifications/clear_all/`, {
          headers: {
            'Authorization': `JWT ${token}`
          }
        });
        
        // Очищаем локальное состояние
        this.notifications = [];
        this.unreadCount = 0;
        
        console.log('Все уведомления удалены');
      } catch (error) {
        console.error('Ошибка удаления всех уведомлений:', error);
        console.error('Ошибка удаления уведомлений');
      } finally {
        this.isClearing = false;
      }
    },

    handleNotificationClick(notification) {
      // Помечаем как прочитанное
      if (!notification.is_read) {
        this.markAsRead(notification.id);
      }
      
      // Переходим по ссылке, если есть
      if (notification.link) {
        this.$router.push(notification.link);
      }
      
      this.closeDropdown();
    },

    viewAllNotifications() {
      this.$router.push('/notifications');
      this.closeDropdown();
    },

    toggleDropdown() {
      this.isDropdownOpen = !this.isDropdownOpen;
      if (this.isDropdownOpen) {
        this.loadNotifications();
      }
    },

    closeDropdown() {
      this.isDropdownOpen = false;
    },

    updateUnreadCount() {
      this.unreadCount = this.notifications.filter(n => !n.is_read).length;
    },

    formatTime(dateString) {
      const date = new Date(dateString);
      const now = new Date();
      const diff = now - date;
      
      if (diff < 60000) { // Меньше минуты
        return 'только что';
      } else if (diff < 3600000) { // Меньше часа
        const minutes = Math.floor(diff / 60000);
        return `${minutes} мин. назад`;
      } else if (diff < 86400000) { // Меньше дня
        const hours = Math.floor(diff / 3600000);
        return `${hours} ч. назад`;
      } else {
        return date.toLocaleDateString('ru-RU');
      }
    },

    getNotificationColor(type) {
      const colors = {
        'info': '#17a2b8',
        'warning': '#ffc107',
        'task': '#007bff',
        'document': '#28a745',
        'process': '#6c757d'
      };
      return colors[type] || '#6c757d';
    },

    // WebSocket обработчики
    handleNewNotification(notification) {
      this.notifications.unshift(notification);
      this.updateUnreadCount();
      
      // Показываем toast уведомление
      console.log('Новое уведомление:', notification.message);
    },

    handleUnreadCount(count) {
      this.unreadCount = count;
    },

    handleNotificationsList(notifications) {
      this.notifications = notifications;
      this.updateUnreadCount();
    },

    handleConnected() {
      console.log('WebSocket для уведомлений подключен');
    },

    handleDisconnected() {
      console.log('WebSocket для уведомлений отключен');
    },

    handleError(error) {
      console.error('Ошибка WebSocket уведомлений:', error);
    },

    cleanup() {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval);
      }
      notificationService.disconnect();
    }
  }
};
</script>

<style scoped>
/* ======================================
 * СТИЛИ УВЕДОМЛЕНИЙ В СТИЛЕ SKRIPTUM
 * ====================================== */

.notification-bell {
  position: relative;
  display: inline-block;
}

.notification-button {
  position: relative;
  background: none;
  border: none;
  font-size: 1.2rem;
  color: var(--text-light);
  cursor: pointer;
  padding: 0.75rem;
  border-radius: 50%;
  transition: var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
}

.notification-button:hover {
  background-color: var(--bg-light);
  color: var(--primary-color);
}

.notification-button.has-notifications {
  color: var(--primary-color);
  background-color: var(--primary-color-light);
}

.notification-badge {
  position: absolute;
  top: 0.25rem;
  right: 0.25rem;
  background-color: var(--priority-high);
  color: white;
  border-radius: 50%;
  width: 1.25rem;
  height: 1.25rem;
  font-size: 0.7rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  border: 2px solid var(--card-background);
  box-shadow: var(--shadow-sm);
}

.notification-dropdown {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  width: 380px;
  background: var(--card-background);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-lg);
  z-index: 1000;
  max-height: 500px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.notification-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, var(--primary-color-light) 0%, rgba(67, 97, 238, 0.05) 100%);
}

.notification-header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-color);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.notification-header h3::before {
  content: '🔔';
  font-size: 1rem;
}

.notification-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.btn-mark-all,
.btn-clear-all,
.btn-refresh {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  background: var(--card-background);
  border: 1px solid var(--border-color);
  padding: 0.5rem 0.75rem;
  border-radius: var(--border-radius);
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--text-light);
  transition: var(--transition);
  white-space: nowrap;
}

.btn-mark-all:hover {
  background-color: var(--primary-color-light);
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.btn-clear-all:hover {
  background-color: rgba(var(--priority-high-rgb), 0.1);
  border-color: var(--priority-high);
  color: var(--priority-high);
}

.btn-refresh:hover {
  background-color: var(--bg-light);
  color: var(--primary-color);
}

.btn-mark-all:disabled,
.btn-clear-all:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.notification-list {
  flex: 1;
  overflow-y: auto;
  max-height: 320px;
}

.loading,
.empty {
  padding: 2rem;
  text-align: center;
  color: var(--text-muted);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.loading i,
.empty i {
  font-size: 2rem;
  color: var(--primary-color);
}

.empty i {
  color: var(--text-muted);
}

.loading span,
.empty span {
  font-size: 0.9rem;
  font-weight: 500;
}

.notification-item {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  position: relative;
  background: var(--card-background);
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-item:hover {
  background-color: var(--bg-light);
}

.notification-item.unread {
  background: linear-gradient(90deg, var(--primary-color-light) 0%, var(--card-background) 10%);
  border-left: 3px solid var(--primary-color);
}

.notification-item.unread::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--primary-color);
}

.notification-icon {
  flex-shrink: 0;
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.125rem;
  background: var(--bg-light);
  border-radius: 50%;
  color: var(--primary-color);
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 0.25rem;
  line-height: 1.3;
}

.notification-message {
  font-size: 0.85rem;
  color: var(--text-light);
  line-height: 1.4;
  margin-bottom: 0.5rem;
}

.notification-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.notification-time {
  font-weight: 500;
}

.notification-type {
  background: var(--bg-light);
  padding: 0.125rem 0.5rem;
  border-radius: var(--border-radius-sm);
  font-weight: 500;
  text-transform: capitalize;
}

.notification-dot {
  position: absolute;
  top: 1.25rem;
  right: 1.5rem;
  width: 0.5rem;
  height: 0.5rem;
  background-color: var(--primary-color);
  border-radius: 50%;
  box-shadow: 0 0 0 2px var(--card-background);
}

.notification-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-color);
  text-align: center;
  background: var(--bg-light);
}

.btn-view-all {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--primary-color);
  border: none;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: var(--border-radius);
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: var(--transition);
}

.btn-view-all:hover {
  background: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.notification-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
  background: rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(2px);
}

/* ======================================
 * АНИМАЦИИ
 * ====================================== */

.notification-item {
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.notification-dropdown {
  animation: fadeInDown 0.2s ease;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fa-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* ======================================
 * АДАПТИВНОСТЬ
 * ====================================== */

@media (max-width: 480px) {
  .notification-dropdown {
    width: calc(100vw - 2rem);
    right: -1rem;
    left: -1rem;
  }
  
  .notification-header {
    padding: 1rem;
  }
  
  .notification-actions {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .btn-mark-all,
  .btn-clear-all,
  .btn-refresh {
    font-size: 0.75rem;
    padding: 0.375rem 0.5rem;
  }
  
  .notification-item {
    padding: 0.75rem 1rem;
  }
  
  .notification-icon {
    width: 2rem;
    height: 2rem;
    font-size: 1rem;
  }
}

/* ======================================
 * СКРОЛЛБАР
 * ====================================== */

.notification-list::-webkit-scrollbar {
  width: 4px;
}

.notification-list::-webkit-scrollbar-track {
  background: var(--bg-light);
}

.notification-list::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 2px;
}

.notification-list::-webkit-scrollbar-thumb:hover {
  background: var(--text-muted);
}
</style>
