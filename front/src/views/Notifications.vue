<template>
  <div class="notifications-page">
    <div class="notifications-header">
      <h1>Уведомления</h1>
      <div class="notifications-actions">
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
          Обновить
        </button>
      </div>
    </div>

    <div class="notifications-content">
      <!-- Фильтры -->
      <div class="filters">
        <div class="filter-group">
          <label>Тип:</label>
          <select v-model="selectedType" @change="applyFilters">
            <option value="">Все типы</option>
            <option value="info">Информационные</option>
            <option value="warning">Предупреждения</option>
            <option value="task">Задачи</option>
            <option value="document">Документы</option>
            <option value="process">Процессы</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Статус:</label>
          <select v-model="selectedStatus" @change="applyFilters">
            <option value="">Все</option>
            <option value="unread">Непрочитанные</option>
            <option value="read">Прочитанные</option>
          </select>
        </div>

        <div class="filter-group">
          <label>Поиск:</label>
          <input 
            v-model="searchQuery" 
            @input="applyFilters"
            type="text" 
            placeholder="Поиск по сообщению..."
            class="search-input"
          >
        </div>
      </div>

      <!-- Список уведомлений -->
      <div class="notifications-list">
        <div v-if="isLoading" class="loading">
          <i class="fas fa-spinner fa-spin"></i>
          <span>Загрузка уведомлений...</span>
        </div>
        
        <div v-else-if="filteredNotifications.length === 0" class="empty">
          <i class="fas fa-bell-slash"></i>
          <h3>Нет уведомлений</h3>
          <p>У вас пока нет уведомлений, соответствующих выбранным фильтрам</p>
        </div>

        <div v-else>
          <div 
            v-for="notification in paginatedNotifications" 
            :key="notification.id"
            class="notification-item"
            :class="{ 'unread': !notification.is_read }"
            @click="handleNotificationClick(notification)"
          >
            <div class="notification-icon">
              <i :class="notification.icon" :style="{ color: getNotificationColor(notification.type) }"></i>
            </div>
            <div class="notification-content">
              <div class="notification-message">{{ notification.message }}</div>
              <div class="notification-meta">
                <span class="notification-type">{{ notification.type_display }}</span>
                <span class="notification-time">{{ formatTime(notification.created_at) }}</span>
              </div>
            </div>
            <div class="notification-actions">
              <button 
                v-if="!notification.is_read" 
                @click.stop="markAsRead(notification.id)"
                class="btn-mark-read"
                title="Пометить как прочитанное"
              >
                <i class="fas fa-check"></i>
              </button>
              <button 
                @click.stop="deleteNotification(notification.id)"
                class="btn-delete"
                title="Удалить"
              >
                <i class="fas fa-trash"></i>
              </button>
            </div>
            <div v-if="!notification.is_read" class="notification-dot"></div>
          </div>
        </div>
      </div>

      <!-- Пагинация -->
      <div v-if="totalPages > 1" class="pagination">
        <button 
          @click="goToPage(currentPage - 1)"
          :disabled="currentPage === 1"
          class="btn btn-outline-secondary"
        >
          <i class="fas fa-chevron-left"></i>
        </button>
        
        <span class="page-info">
          Страница {{ currentPage }} из {{ totalPages }}
        </span>
        
        <button 
          @click="goToPage(currentPage + 1)"
          :disabled="currentPage === totalPages"
          class="btn btn-outline-secondary"
        >
          <i class="fas fa-chevron-right"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import notificationService from '@/api/notifications';
import { API_BASE_URL } from '@/api/config';

export default {
  name: 'NotificationsPage',
  data() {
    return {
      notifications: [],
      filteredNotifications: [],
      unreadCount: 0,
      isLoading: false,
      isMarkingAll: false,
      isClearing: false,
      selectedType: '',
      selectedStatus: '',
      searchQuery: '',
      currentPage: 1,
      itemsPerPage: 20,
      totalPages: 1
    };
  },
  computed: {
    paginatedNotifications() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.filteredNotifications.slice(start, end);
    }
  },
  mounted() {
    this.setupWebSocket();
    this.loadNotifications();
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
        notificationService.on('connected', this.handleConnected);
        notificationService.on('disconnected', this.handleDisconnected);
        notificationService.on('error', this.handleError);
      }
    },

    async loadNotifications() {
      this.isLoading = true;
      try {
        const token = localStorage.getItem('token') || sessionStorage.getItem('token');
        const response = await axios.get(`${API_BASE_URL}/notifications/`, {
          headers: {
            'Authorization': `JWT ${token}`
          },
          params: {
            page: this.currentPage,
            page_size: this.itemsPerPage,
            type: this.selectedType || undefined,
            is_read: this.selectedStatus === 'unread' ? false : this.selectedStatus === 'read' ? true : undefined,
            search: this.searchQuery || undefined
          }
        });
        
        this.notifications = response.data.results || response.data;
        this.totalPages = Math.ceil((response.data.count || this.notifications.length) / this.itemsPerPage);
        this.applyFilters();
        this.updateUnreadCount();
      } catch (error) {
        console.error('Ошибка загрузки уведомлений:', error);
        console.error('Ошибка загрузки уведомлений');
      } finally {
        this.isLoading = false;
      }
    },

    applyFilters() {
      let filtered = [...this.notifications];

      if (this.selectedType) {
        filtered = filtered.filter(n => n.type === this.selectedType);
      }

      if (this.selectedStatus === 'unread') {
        filtered = filtered.filter(n => !n.is_read);
      } else if (this.selectedStatus === 'read') {
        filtered = filtered.filter(n => n.is_read);
      }

      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        filtered = filtered.filter(n => 
          n.message.toLowerCase().includes(query)
        );
      }

      this.filteredNotifications = filtered;
      this.currentPage = 1; // Сбрасываем на первую страницу при фильтрации
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
        this.applyFilters();
        this.updateUnreadCount();
      } catch (error) {
        console.error('Ошибка пометки уведомления как прочитанного:', error);
        console.error('Ошибка пометки уведомления');
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
        this.applyFilters();
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
        this.filteredNotifications = [];
        this.unreadCount = 0;
        this.currentPage = 1;
        
        console.log('Все уведомления удалены');
      } catch (error) {
        console.error('Ошибка удаления всех уведомлений:', error);
        console.error('Ошибка удаления уведомлений');
      } finally {
        this.isClearing = false;
      }
    },

    async deleteNotification(notificationId) {
      if (!confirm('Вы уверены, что хотите удалить это уведомление?')) {
        return;
      }

      try {
        const token = localStorage.getItem('token') || sessionStorage.getItem('token');
        await axios.delete(`${API_BASE_URL}/notifications/${notificationId}/`, {
          headers: {
            'Authorization': `JWT ${token}`
          }
        });
        
        // Удаляем из локального состояния
        this.notifications = this.notifications.filter(n => n.id !== notificationId);
        this.applyFilters();
        this.updateUnreadCount();
        
        console.log('Уведомление удалено');
      } catch (error) {
        console.error('Ошибка удаления уведомления:', error);
        console.error('Ошибка удаления уведомления');
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
    },

    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page;
        this.loadNotifications();
      }
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
        return date.toLocaleDateString('ru-RU', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
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
      this.applyFilters();
      this.updateUnreadCount();
    },

    handleUnreadCount(count) {
      this.unreadCount = count;
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
      notificationService.disconnect();
    }
  }
};
</script>

<style scoped>
/* ======================================
 * СТИЛИ СТРАНИЦЫ УВЕДОМЛЕНИЙ В СТИЛЕ SKRIPTUM
 * ====================================== */

.notifications-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.notifications-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding: 1rem 0;
}

.notifications-header h1 {
  margin: 0;
  color: var(--text-color);
  font-size: 1.5rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.notifications-header h1::before {
  content: '🔔';
  font-size: 1.25rem;
}

.notifications-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.btn-mark-all,
.btn-clear-all,
.btn-refresh {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--card-background);
  border: 1px solid var(--border-color);
  padding: 0.75rem 1.25rem;
  border-radius: var(--border-radius);
  cursor: pointer;
  font-size: 0.875rem;
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

.filters {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 2rem;
  padding: 1.5rem 2rem;
  background: var(--bg-light);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-color);
  flex-wrap: wrap;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 180px;
}

.filter-group label {
  font-weight: 600;
  color: var(--text-color);
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.filter-group select,
.search-input {
  padding: 0.75rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: 0.875rem;
  background: var(--card-background);
  color: var(--text-color);
  transition: var(--transition);
}

.filter-group select:focus,
.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px var(--primary-color-light);
}

.search-input {
  min-width: 250px;
}

.notifications-list {
  background: var(--card-background);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.loading,
.empty {
  padding: 3rem;
  text-align: center;
  color: var(--text-muted);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.loading i,
.empty i {
  font-size: 2.5rem;
  color: var(--primary-color);
}

.empty i {
  color: var(--text-muted);
}

.loading span,
.empty h3,
.empty p {
  font-size: 1rem;
  font-weight: 500;
}

.empty h3 {
  margin: 0;
  color: var(--text-color);
}

.empty p {
  margin: 0;
  color: var(--text-light);
}

.empty h3 {
  margin: 0 0 10px 0;
  color: #495057;
}

.empty p {
  margin: 0;
  font-size: 0.9rem;
}

.notification-item {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: flex-start;
  gap: 1.25rem;
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
  border-left: 4px solid var(--primary-color);
}

.notification-item.unread::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: var(--primary-color);
}

.notification-icon {
  flex-shrink: 0;
  width: 3rem;
  height: 3rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  background: var(--bg-light);
  border-radius: 50%;
  color: var(--primary-color);
  box-shadow: var(--shadow-sm);
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-message {
  font-size: 1rem;
  color: var(--text-color);
  line-height: 1.5;
  margin-bottom: 0.75rem;
  font-weight: 500;
}

.notification-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
  color: var(--text-muted);
}

.notification-time {
  font-weight: 500;
}

.notification-type {
  background: var(--bg-light);
  padding: 0.25rem 0.75rem;
  border-radius: var(--border-radius-sm);
  font-weight: 500;
  text-transform: capitalize;
  color: var(--text-light);
}

.notification-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  flex-shrink: 0;
}

.btn-mark-read,
.btn-delete {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border: none;
  border-radius: var(--border-radius);
  cursor: pointer;
  font-size: 0.8rem;
  transition: var(--transition);
  color: var(--text-light);
}

.btn-mark-read {
  background-color: var(--status-completed);
  color: white;
}

.btn-mark-read:hover {
  background-color: var(--status-completed);
  opacity: 0.9;
  transform: translateY(-1px);
}

.btn-delete {
  background-color: var(--priority-high);
  color: white;
}

.btn-delete:hover {
  background-color: var(--priority-high);
  opacity: 0.9;
  transform: translateY(-1px);
}

.notification-dot {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 10px;
  height: 10px;
  background-color: #007bff;
  border-radius: 50%;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-top: 30px;
  padding: 20px;
}

.page-info {
  font-size: 0.9rem;
  color: #6c757d;
}

/* Анимации */
.notification-item {
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
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

@media (max-width: 768px) {
  .notifications-page {
    padding: 1rem;
  }
  
  .notifications-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
    padding: 0.5rem 0;
  }
  
  .notifications-actions {
    width: 100%;
    justify-content: flex-start;
    flex-wrap: wrap;
  }
  
  .filters {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }
  
  .filter-group {
    min-width: auto;
    width: 100%;
  }
  
  .search-input {
    min-width: auto;
    width: 100%;
  }
  
  .notification-item {
    padding: 1rem;
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .notification-actions {
    align-self: flex-end;
    margin-top: 0.5rem;
  }
}

@media (max-width: 480px) {
  .notifications-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .btn-mark-all,
  .btn-clear-all,
  .btn-refresh {
    width: 100%;
    justify-content: center;
  }
  
  .notification-item {
    padding: 0.75rem;
  }
  
  .notification-icon {
    width: 2.5rem;
    height: 2.5rem;
    font-size: 1rem;
  }
}
</style>
