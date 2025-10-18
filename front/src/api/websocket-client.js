/**
 * WebSocket клиент для совместного редактирования BPMN диаграмм
 */

class BpmnWebSocketClient {
  constructor(diagramId, onMessage, onError, token = null) {
    this.diagramId = diagramId;
    this.onMessage = onMessage;
    this.onError = onError;
    this.token = token || this.getTokenFromStorage();
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 1000;
    this.isConnected = false;
    this.cursorUpdateInterval = null;
    this.lastCursorPosition = { x: 0, y: 0 };
    this.activeUsers = new Map();
    this.operationQueue = [];
    this.isProcessingQueue = false;
  }

  /**
   * Получение токена из localStorage
   */
  getTokenFromStorage() {
    return localStorage.getItem('token') || sessionStorage.getItem('token');
  }

  /**
   * Подключение к WebSocket
   */
  connect() {
    try {
      // Проверяем наличие токена
      if (!this.token) {
        console.error('No token available for WebSocket connection');
        this.onError && this.onError(new Error('No authentication token'));
        return;
      }
      
      // Принудительно используем localhost:8000 для WebSocket (Django сервер)
      const wsUrl = `ws://localhost:8000/ws/bpmn/collaborate/${this.diagramId}/?token=${this.token}`;
      
      // Подключение к WebSocket
      this.ws = new WebSocket(wsUrl);
      
      this.ws.onopen = () => {
        console.log('🔌 WebSocket подключен');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.startCursorTracking();
        this.processOperationQueue();
      };
      
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
      
      this.ws.onclose = () => {
        this.isConnected = false;
        this.stopCursorTracking();
        this.cleanupActiveUsers();
        
        // Уведомляем о необходимости автосохранения
        this.onMessage('websocket_disconnected', {});
        
        // Попытка переподключения
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          setTimeout(() => {
            this.reconnectAttempts++;
            this.connect();
          }, this.reconnectInterval * this.reconnectAttempts);
        }
      };
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.onError && this.onError(error);
      };
      
    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
      this.onError && this.onError(error);
    }
  }

  /**
   * Отключение от WebSocket
   */
  disconnect() {
    this.stopCursorTracking();
    this.isConnected = false;
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * Обработка входящих сообщений
   */
  handleMessage(data) {
    console.log('📨 WebSocket сообщение получено:', data.type, data);
    switch (data.type) {
      case 'diagram_data':
        this.onMessage('diagram_data', data.data);
        break;
        
      case 'active_users':
        this.updateActiveUsers(data.users);
        this.onMessage('active_users', data.users);
        break;
        
      case 'user_joined':
        this.addActiveUser(data);
        this.onMessage('user_joined', data);
        break;
        
      case 'user_left':
        console.log('Пользователь покинул сессию:', data.username);
        this.removeActiveUser(data.user_id);
        this.onMessage('user_left', data);
        break;
        
      case 'cursor_update':
        this.updateUserCursor(data);
        this.onMessage('cursor_update', data);
        break;
        
      case 'operation':
        this.onMessage('operation_applied', data);
        break;
        
      case 'operation_applied':
        this.onMessage('operation_applied', data);
        break;
        
      case 'selection_update':
        this.onMessage('selection_update', data.selection);
        break;
        
      case 'pong':
        // Ответ на ping
        break;
        
      case 'error':
        console.error('Server error:', data.message);
        this.onError && this.onError(new Error(data.message));
        break;
        
      default:
        console.log('Unknown message type:', data.type);
    }
  }

  /**
   * Отправка сообщения
   */
  send(type, data = {}) {
    if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
      const message = {
        type,
        ...data,
        timestamp: Date.now()
      };
      
      try {
        this.ws.send(JSON.stringify(message));
      } catch (error) {
        console.error('Error sending WebSocket message:', error);
        this.onError && this.onError(error);
      }
    } else {
      console.warn('WebSocket not connected, queuing message');
      this.operationQueue.push({ type, data });
    }
  }

  /**
   * Отправка операции редактирования
   */
  sendOperation(operation) {
    this.send('operation', { operation });
  }

  /**
   * Отправка обновления курсора
   */
  sendCursorUpdate(x, y) {
    this.lastCursorPosition = { x, y };
    this.send('cursor_update', { x, y });
  }

  /**
   * Отправка обновления выделения
   */
  sendSelection(selectedElements) {
    this.send('selection', { selected_elements: selectedElements });
  }

  /**
   * Запуск отслеживания курсора
   */
  startCursorTracking() {
    if (this.cursorUpdateInterval) {
      clearInterval(this.cursorUpdateInterval);
    }
    
    this.cursorUpdateInterval = setInterval(() => {
      if (this.isConnected) {
        this.send('cursor_update', this.lastCursorPosition);
      }
    }, 50); // Обновляем каждые 50мс для более плавного движения
  }

  /**
   * Остановка отслеживания курсора
   */
  stopCursorTracking() {
    if (this.cursorUpdateInterval) {
      clearInterval(this.cursorUpdateInterval);
      this.cursorUpdateInterval = null;
    }
  }

  /**
   * Обработка очереди операций
   */
  async processOperationQueue() {
    if (this.isProcessingQueue || this.operationQueue.length === 0) {
      return;
    }
    
    this.isProcessingQueue = true;
    
    while (this.operationQueue.length > 0 && this.isConnected) {
      const { type, data } = this.operationQueue.shift();
      this.send(type, data);
      
      // Небольшая задержка между операциями
      await new Promise(resolve => setTimeout(resolve, 10));
    }
    
    this.isProcessingQueue = false;
  }

  /**
   * Обновление списка активных пользователей
   */
  updateActiveUsers(users) {
    this.activeUsers.clear();
    users.forEach(user => {
      this.activeUsers.set(user.user_id, user);
    });
  }

  /**
   * Добавление активного пользователя
   */
  addActiveUser(user) {
    this.activeUsers.set(user.user_id, user);
  }

  /**
   * Удаление активного пользователя
   */
  removeActiveUser(userId) {
    this.activeUsers.delete(userId);
  }

  /**
   * Получение активных пользователей
   */
  getActiveUsers() {
    return Array.from(this.activeUsers.values());
  }

  /**
   * Очистка данных активных пользователей
   */
  cleanupActiveUsers() {
    this.activeUsers.clear();
  }

  /**
   * Ping сервера для проверки соединения
   */
  ping() {
    this.send('ping');
  }

  /**
   * Обновление позиции курсора
   */
  updateUserCursor(cursorData) {
    if (cursorData && cursorData.user_id && this.activeUsers.has(cursorData.user_id)) {
      const user = this.activeUsers.get(cursorData.user_id);
      user.cursor = {
        x: cursorData.x,
        y: cursorData.y,
        username: cursorData.username
      };
      this.activeUsers.set(cursorData.user_id, user);
    }
  }
}

export default BpmnWebSocketClient;
