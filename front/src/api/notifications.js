import { API_BASE_URL } from './config';

class NotificationService {
  constructor() {
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    this.listeners = new Map();
  }

  /**
   * Подключение к WebSocket для уведомлений
   */
  connect(token) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      return;
    }

    const wsUrl = `ws://${API_BASE_URL.replace('http://', '').replace('/api', '')}/ws/notifications/?token=${token}`;
    
    try {
      this.ws = new WebSocket(wsUrl);
      
      this.ws.onopen = () => {
        console.log('🔔 WebSocket для уведомлений подключен');
        this.reconnectAttempts = 0;
        this.emit('connected');
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (error) {
          console.error('Ошибка парсинга WebSocket сообщения:', error);
        }
      };

      this.ws.onclose = (event) => {
        console.log('🔔 WebSocket для уведомлений отключен:', event.code, event.reason);
        this.emit('disconnected', event);
        
        // Автоматическое переподключение
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          setTimeout(() => {
            this.reconnectAttempts++;
            console.log(`🔄 Попытка переподключения ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
            this.connect(token);
          }, this.reconnectDelay * this.reconnectAttempts);
        }
      };

      this.ws.onerror = (error) => {
        console.error('Ошибка WebSocket для уведомлений:', error);
        this.emit('error', error);
      };

    } catch (error) {
      console.error('Ошибка создания WebSocket соединения:', error);
    }
  }

  /**
   * Обработка входящих сообщений
   */
  handleMessage(data) {
    switch (data.type) {
      case 'new_notification':
        this.emit('new_notification', data.notification);
        break;
      case 'unread_count':
        this.emit('unread_count', data.count);
        break;
      case 'notifications_list':
        this.emit('notifications_list', data.notifications);
        break;
      case 'error':
        this.emit('error', data.message);
        break;
      default:
        console.log('Неизвестный тип сообщения:', data.type);
    }
  }

  /**
   * Отправка сообщения через WebSocket
   */
  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket не подключен');
    }
  }

  /**
   * Получение списка уведомлений
   */
  getNotifications(limit = 20, offset = 0) {
    this.send({
      type: 'get_notifications',
      limit,
      offset
    });
  }

  /**
   * Пометить уведомление как прочитанное
   */
  markAsRead(notificationId) {
    this.send({
      type: 'mark_as_read',
      notification_id: notificationId
    });
  }

  /**
   * Пометить все уведомления как прочитанные
   */
  markAllAsRead() {
    this.send({
      type: 'mark_all_as_read'
    });
  }

  /**
   * Подписка на события
   */
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  /**
   * Отписка от событий
   */
  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  /**
   * Генерация события
   */
  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error('Ошибка в обработчике события:', error);
        }
      });
    }
  }

  /**
   * Отключение от WebSocket
   */
  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.listeners.clear();
  }
}

// Создаем единственный экземпляр сервиса
const notificationService = new NotificationService();

export default notificationService;
