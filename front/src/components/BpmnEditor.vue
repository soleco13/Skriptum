<template>
  <div class="bpmn-editor-page">
    <!-- Упрощенный Header только с основными кнопками -->
    <div class="bpmn-header">
      <div class="header-actions">
        <button 
          class="btn-secondary" 
          @click="closeDiagram"
          title="Закрыть редактор">
          <i class="fas fa-times"></i>
          Закрыть
        </button>
        
        <button 
          class="btn-primary" 
          @click="saveDiagram" 
          :disabled="!isModified"
          title="Сохранить изменения">
          <i class="fas fa-save"></i>
          Сохранить
        </button>
        
        <button 
          class="btn-secondary" 
          @click="openShareModal"
          title="Поделиться диаграммой">
          <i class="fas fa-share-alt"></i>
          Поделиться
        </button>
        
        <!-- Индикатор совместного редактирования -->
        <div v-if="isCollaborativeMode" class="collaboration-indicator">
          <i class="fas fa-users"></i>
          <span>{{ activeUsers.length }} пользователей</span>
        </div>
        
        <!-- Список активных пользователей -->
        <active-users 
          v-if="isCollaborativeMode" 
          :users="activeUsers" 
          :current-user-id="getCurrentUserId()"
          class="active-users-widget"
        />
        
        <div class="btn-group">
          <button 
            class="btn-secondary" 
            @click="exportDiagram"
            title="Экспортировать диаграмму">
            <i class="fas fa-download"></i>
            Экспорт
          </button>
          
          <label class="btn-secondary import-btn" title="Импортировать диаграмму">
            <i class="fas fa-upload"></i>
            Импорт
            <input type="file" @change="importDiagram" accept=".bpmn, .xml" />
          </label>
        </div>
        
        <!-- Перенесенные инструменты масштабирования -->
        <div class="zoom-controls">
          <button 
            class="zoom-btn" 
            @click="zoomOut"
            title="Уменьшить">
            <i class="fas fa-search-minus"></i>
          </button>
          <button 
            class="zoom-btn" 
            @click="resetZoom"
            title="По размеру">
            <i class="fas fa-expand-arrows-alt"></i>
          </button>
          <button 
            class="zoom-btn" 
            @click="zoomIn"
            title="Увеличить">
            <i class="fas fa-search-plus"></i>
          </button>
        </div>
        
        <!-- Индикатор изменений -->
        <div class="modification-indicator" v-if="isModified">
          <i class="fas fa-circle"></i>
          Несохранено
        </div>
      </div>
    </div>
    
    <!-- Основная область редактора -->
    <div class="bpmn-editor-main">
      <div class="bpmn-canvas-container">
        <div ref="canvas" class="bpmn-canvas" @mousemove="handleMouseMove">
          <!-- Курсоры других пользователей -->
          <user-cursors :cursors="Array.from(userCursors.values())" />
        </div>
        
        <!-- Индикатор загрузки -->
        <div v-if="!modeler" class="loading-overlay">
          <div class="loading-spinner">
            <i class="fas fa-spinner fa-spin"></i>
            <span>Инициализация редактора...</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно управления доступом -->
    <div v-if="showShareModal" class="modal" @click="handleShareModalBackdrop">
      <div class="modal-content share-modal" @click.stop>
        <button class="close-btn" @click="closeShareModal">
          <i class="fas fa-times"></i>
        </button>
        
        <div class="modal-header">
          <h2>Управление доступом к диаграмме</h2>
          <p class="modal-subtitle">Предоставьте доступ к BPMN-диаграмме другим пользователям</p>
        </div>
        
        <div class="share-content">
          <!-- Поиск пользователей -->
          <div class="user-search-section">
            <h3>
              <i class="fas fa-user-plus"></i>
              Добавить пользователей
            </h3>
            <div class="search-wrapper">
              <i class="fas fa-search"></i>
              <input 
                type="text" 
                v-model="userSearchQuery" 
                placeholder="Поиск пользователей по имени или username..."
                @input="searchUsers"
                @focus="onSearchFocus"
                class="user-search-input"
              >
            </div>
            
            <!-- Список найденных пользователей -->
            <div v-if="searchResults.length > 0" class="user-search-results">
              <div 
                v-for="user in searchResults" 
                :key="user.id"
                class="user-search-item"
                @click="addUserAccess(user)"
              >
                <div class="user-avatar">
                  <i class="fas fa-user"></i>
                </div>
                <div class="user-info">
                  <div class="user-name">{{ user.full_name || user.username }}</div>
                  <div class="user-username">@{{ user.username }}</div>
                </div>
                <button class="btn-add-user">
                  <i class="fas fa-plus"></i>
                </button>
              </div>
            </div>
            
            <!-- Сообщение, если пользователи не найдены -->
            <div v-else-if="userSearchQuery && !isSearchingUsers" class="no-users-found">
              <i class="fas fa-user-slash"></i>
              <p>Пользователи не найдены</p>
            </div>
            
            <!-- Индикатор загрузки поиска -->
            <div v-if="isSearchingUsers" class="search-loading">
              <i class="fas fa-spinner fa-spin"></i>
              <p>Поиск пользователей...</p>
            </div>
          </div>
          
          <!-- Пользователи с доступом -->
          <div class="users-with-access-section">
            <h3>
              <i class="fas fa-users"></i>
              Пользователи с доступом
            </h3>
            
            <!-- Владелец диаграммы -->
            <div class="access-user-item owner">
              <div class="user-avatar">
                <i class="fas fa-crown"></i>
              </div>
              <div class="user-info">
                <div class="user-name">{{ diagramOwner ? diagramOwner.user_name : 'Вы' }}</div>
                <div class="user-role">Владелец диаграммы</div>
              </div>
              <div class="access-level">
                <span class="access-badge owner">Полный доступ</span>
              </div>
            </div>
            
            <!-- Пользователи с предоставленным доступом -->
            <div 
              v-for="access in usersWithAccess" 
              :key="access.id"
              class="access-user-item"
            >
              <div class="user-avatar">
                <i class="fas fa-user"></i>
              </div>
              <div class="user-info">
                <div class="user-name">{{ access.user_name }}</div>
                <div class="user-email">{{ access.user_email }}</div>
              </div>
              <div class="access-level">
                <select 
                  v-model="access.access_level"
                  @change="updateUserAccess(access)"
                  class="access-select"
                >
                  <option value="view">Просмотр</option>
                  <option value="edit">Редактирование</option>
                  <option value="admin">Администратор</option>
                </select>
              </div>
              <button 
                @click="removeUserAccess(access.id)"
                class="btn-remove-user"
                title="Удалить доступ"
              >
                <i class="fas fa-trash"></i>
              </button>
            </div>
            
            <!-- Сообщение, если нет пользователей с доступом -->
            <div v-if="usersWithAccess.length === 0" class="no-shared-users">
              <i class="fas fa-users-slash"></i>
              <p>Диаграмма пока не была предоставлена другим пользователям</p>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn-secondary" @click="closeShareModal">
            Закрыть
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import BpmnModeler from 'bpmn-js/lib/Modeler';
import { emptyBpmn } from '../utils/bpmn-templates';
import { BpmnService } from '../api/services';
import { UserService } from '../api/services';
import BpmnWebSocketClient from '../api/websocket-client';
import UserCursors from './UserCursors.vue';
import ActiveUsers from './ActiveUsers.vue';

export default {
  name: 'BpmnEditor',
  components: {
    UserCursors,
    ActiveUsers
  },
  props: {
    diagramId: {
      type: [String, Number],
      default: null
    },
    initialXml: {
      type: String,
      default: null
    }
  },
  data() {
    return {
      modeler: null,
      currentXml: null,
      isModified: false,
      diagramCreated: false, // Флаг для отслеживания создания диаграммы
      actualDiagramId: null, // ID созданной диаграммы (отличается от diagramId, который может быть ID процесса)
      // Данные для управления доступом
      showShareModal: false,
      userSearchQuery: '',
      searchResults: [],
      isSearchingUsers: false,
      usersWithAccess: [],
      diagramOwner: null,
      searchTimeout: null,
      // Данные для совместного редактирования
      wsClient: null,
      isCollaborativeMode: false,
      activeUsers: [],
      userCursors: new Map(),
      cursorLastUpdate: new Map(), // Для дебаунса курсоров
      isConnected: false,
      diagramChangeTimeout: null
    };
  },
  mounted() {
    console.log('BpmnEditor mounted. Props:', {
      diagramId: this.diagramId,
      initialXml: !!this.initialXml
    });
    
    // Инициализируем сервис BPMN
    this.$bpmnService = BpmnService;
    
    this.initModeler();
    
    // Загружаем диаграмму, если передан ID или XML
    if (this.initialXml) {
      console.log('Загрузка с initialXml, diagramId:', this.diagramId);
      this.diagramCreated = true; // Диаграмма уже существует
      this.actualDiagramId = this.diagramId; // При передаче XML, diagramId уже содержит ID диаграммы
      this.loadXml(this.initialXml);
    } else if (this.diagramId) {
      console.log('Загрузка по diagramId:', this.diagramId);
      this.loadDiagram(this.diagramId);
    } else {
      console.log('Создание новой диаграммы');
      this.createNewDiagram();
    }
    
    // Обработчик изменений для отслеживания модификаций
    window.addEventListener('beforeunload', this.handleBeforeUnload);
    
    // Инициализация совместного редактирования будет выполнена после создания диаграммы
    // this.initCollaborativeEditing();
  },
  async beforeUnmount() {
    window.removeEventListener('beforeunload', this.handleBeforeUnload);
    
    // Автосохранение перед уничтожением компонента
    if (this.isModified && this.actualDiagramId) {
      try {
        console.log('Автосохранение перед уничтожением компонента...');
        await this.saveDiagram();
        console.log('Автосохранение завершено');
      } catch (error) {
        console.error('Ошибка автосохранения:', error);
      }
    }
    
    if (this.modeler) {
      this.modeler.destroy();
    }
    // Очищаем таймер поиска при уничтожении компонента
    if (this.searchTimeout) {
      clearTimeout(this.searchTimeout);
    }
    // Отключаемся от WebSocket
    if (this.wsClient) {
      this.wsClient.disconnect();
    }
    
    // Очищаем таймер изменений диаграммы
    if (this.diagramChangeTimeout) {
      clearTimeout(this.diagramChangeTimeout);
    }
    
    // Останавливаем очистку курсоров
    this.stopCursorCleanup();
    
    // Останавливаем автосохранение
    this.stopAutoSave();
  },
  methods: {
    initModeler() {
      console.log('Инициализация BPMN-редактора');
      // Проверяем, что контейнер существует и имеет размеры перед инициализацией
      if (!this.$refs.canvas) {
        console.error('Контейнер для BPMN-редактора не существует');
        // Отложенная инициализация, чтобы дать контейнеру время на рендеринг
        setTimeout(() => this.initModeler(), 100);
        return;
      }
      
      try {
        // Инициализация модулера BPMN с минимальными опциями
        this.modeler = new BpmnModeler({
          container: this.$refs.canvas
        });
        
        // Обработчики событий устанавливаются в setupDiagramEventHandlers()
      } catch (error) {
        console.error('Ошибка при инициализации BPMN-модулера:', error);
        this.$emit('error', 'Не удалось инициализировать редактор BPMN');
      }
      
        // Устанавливаем обработчики событий
        this.setupDiagramEventHandlers();
    },
    
    /**
     * Установка обработчиков событий диаграммы
     */
    setupDiagramEventHandlers() {
      if (!this.modeler) return;
      
      // Подписываемся на события изменения диаграммы
      this.modeler.on('element.changed', () => {
        this.isModified = true;
        this.handleDiagramChange();
      });
      
      this.modeler.on('shape.added', () => {
        this.isModified = true;
        this.handleDiagramChange();
      });
      
      this.modeler.on('shape.removed', () => {
        this.isModified = true;
        this.handleDiagramChange();
      });
      
      this.modeler.on('connection.added', () => {
        this.isModified = true;
        this.handleDiagramChange();
      });
      
      this.modeler.on('connection.removed', () => {
        this.isModified = true;
        this.handleDiagramChange();
      });
      
      // Дополнительные события для полной синхронизации
      this.modeler.on('commandStack.shape.create.postExecute', () => {
        this.handleDiagramChange();
      });
      
      this.modeler.on('commandStack.shape.delete.postExecute', () => {
        this.handleDiagramChange();
      });
      
      this.modeler.on('commandStack.connection.create.postExecute', () => {
        this.handleDiagramChange();
      });
      
      this.modeler.on('commandStack.connection.delete.postExecute', () => {
        this.handleDiagramChange();
      });
      
      // Обработка изменений масштаба для курсоров
      this.modeler.on('canvas.zoom', () => {
        // Принудительно обновляем курсоры при изменении масштаба
        this.$nextTick(() => {
          // Курсоры обновятся автоматически через реактивность Vue
        });
      });
    },
    
    async loadDiagram(id) {
      try {
        console.log('Попытка загрузить диаграмму с ID/процессом:', id);
        // Загрузка диаграммы с сервера по ID процесса
        const response = await this.$bpmnService.getByProcessId(id);
        console.log('Ответ от сервера:', response);
        
        if (response && response.xml) {
          this.diagramCreated = true; // Диаграмма уже существует
          this.actualDiagramId = response.id; // Сохраняем реальный ID диаграммы
          this.loadXml(response.xml);
          this.currentXml = response.xml;
          this.isModified = false;
          console.log('Загружена существующая диаграмма с ID:', response.id);
          console.log('Установлен actualDiagramId:', this.actualDiagramId);
          
          // Инициализируем совместное редактирование после загрузки диаграммы
          this.$nextTick(() => {
            this.initCollaborativeEditing();
          });
        } else {
          // Если диаграмма не найдена, создаем новую пустую диаграмму
          console.log('Диаграмма не найдена, создаем новую для процесса:', id);
          this.createNewDiagram();
        }
      } catch (error) {
        console.error('Ошибка при загрузке диаграммы, создаем новую:', error);
        // Если произошла ошибка 404, создаем новую пустую диаграмму
        if (error.response && error.response.status === 404) {
          console.log('Диаграмма не найдена (404), создаем новую для процесса:', id);
          this.createNewDiagram();
        } else {
          // Для других ошибок также создаем новую диаграмму
          this.createNewDiagram();
        }
      }
    },
    
    loadXml(xml) {
      // Проверяем, что модулер инициализирован
      if (!this.modeler) {
        console.error('BPMN-модулер не инициализирован');
        this.$emit('error', 'Редактор BPMN не инициализирован');
        return;
      }
      
      // Загрузка XML в редактор
      this.modeler.importXML(xml)
        .then(({ warnings }) => {
          if (warnings.length) {
            console.warn('Предупреждения при загрузке BPMN:', warnings);
          }
          
          try {
            // Безопасный вызов масштабирования с обработкой ошибок
            const canvas = this.modeler.get('canvas');
            if (canvas) {
              // Добавляем небольшую задержку для корректного рендеринга
              setTimeout(() => {
                try {
                  canvas.zoom('fit-viewport');
                } catch (e) {
                  console.error('Ошибка при масштабировании после загрузки:', e);
                }
              }, 50);
            }
            
            this.currentXml = xml;
            this.isModified = false;
          } catch (zoomError) {
            console.error('Ошибка при настройке масштаба:', zoomError);
            // Продолжаем работу даже при ошибке масштабирования
            this.currentXml = xml;
            this.isModified = false;
          }
        })
        .catch(error => {
          console.error('Ошибка при импорте BPMN:', error);
          this.$emit('error', 'Ошибка при загрузке диаграммы');
        });
    },
    
    async createNewDiagram() {
      // Создание новой пустой диаграммы
      this.loadXml(emptyBpmn);
      
      // Создаем диаграмму в базе данных
      try {
        console.log('Создаем новую диаграмму в БД для процесса:', this.diagramId);
        const response = await this.$bpmnService.createDiagram({
          name: 'Новая диаграмма',
          xml: emptyBpmn,
          process: this.diagramId // Привязываем к процессу
        });
        
        if (response && response.id) {
          this.actualDiagramId = response.id;
          this.diagramCreated = true;
          this.$emit('diagram-created', response.id);
          console.log('Новая диаграмма создана в БД с ID:', response.id);
          
          // Загружаем пользователей с доступом после создания диаграммы
          this.fetchUsersWithAccess();
        }
      } catch (error) {
        console.error('Ошибка при создании диаграммы в БД:', error);
        this.$emit('error', 'Не удалось создать диаграмму в базе данных');
      }
      
      // Инициализируем совместное редактирование после создания диаграммы
      this.$nextTick(() => {
        this.initCollaborativeEditing();
      });
    },
    
    async saveDiagram() {
      try {
        // Получаем XML текущей диаграммы
        const { xml } = await this.modeler.saveXML({ format: true });
        
        let response;
        console.log('Состояние перед сохранением:', {
          actualDiagramId: this.actualDiagramId,
          diagramId: this.diagramId,
          diagramCreated: this.diagramCreated,
          initialXml: !!this.initialXml
        });
        
        if (this.actualDiagramId) {
          // Обновляем существующую диаграмму по её реальному ID
          console.log('Обновляем существующую диаграмму с ID:', this.actualDiagramId);
          response = await this.$bpmnService.updateDiagram(this.actualDiagramId, {
            name: 'Новая диаграмма', // Добавляем обязательное поле name
            xml: xml
          });
        } else {
          // Создаем новую диаграмму для процесса
          console.log('Создаем новую диаграмму для процесса:', this.diagramId);
          response = await this.$bpmnService.createDiagram({
            name: 'Новая диаграмма',
            xml: xml,
            process: this.diagramId // Привязываем к процессу
          });
          
          // Если создана новая диаграмма, сохраняем её ID
          if (response && response.id) {
            this.actualDiagramId = response.id;
            this.diagramCreated = true;
            this.$emit('diagram-created', response.id);
            console.log('Новая диаграмма создана с ID:', response.id);
            
            // Загружаем пользователей с доступом после создания диаграммы
            this.fetchUsersWithAccess();
          }
        }
        
        this.currentXml = xml;
        this.isModified = false;
        this.$emit('saved', response);
      } catch (error) {
        console.error('Ошибка при сохранении диаграммы:', error);
        this.$emit('error', 'Не удалось сохранить диаграмму');
      }
    },
    
    async exportDiagram() {
      try {
        // Экспорт диаграммы в XML
        const { xml } = await this.modeler.saveXML({ format: true });
        
        // Создаем файл для скачивания
        const blob = new Blob([xml], { type: 'application/xml' });
        const url = URL.createObjectURL(blob);
        
        // Создаем ссылку для скачивания и эмулируем клик
        const a = document.createElement('a');
        a.href = url;
        a.download = `bpmn-diagram-${new Date().toISOString().slice(0, 10)}.bpmn`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      } catch (error) {
        console.error('Ошибка при экспорте диаграммы:', error);
        this.$emit('error', 'Не удалось экспортировать диаграмму');
      }
    },
    
    importDiagram(event) {
      const file = event.target.files[0];
      if (!file) return;
      
      const reader = new FileReader();
      reader.onload = (e) => {
        const xml = e.target.result;
        this.loadXml(xml);
      };
      reader.readAsText(file);
      
      // Сбрасываем значение input, чтобы можно было загрузить тот же файл повторно
      event.target.value = '';
    },
    
    zoomIn() {
      try {
        const canvas = this.modeler.get('canvas');
        if (canvas) {
          canvas.zoom(1.1, { x: 'center', y: 'center' });
        }
      } catch (error) {
        console.error('Ошибка при увеличении масштаба:', error);
        this.$emit('error', 'Не удалось изменить масштаб');
      }
    },
    
    zoomOut() {
      try {
        const canvas = this.modeler.get('canvas');
        if (canvas) {
          canvas.zoom(0.9, { x: 'center', y: 'center' });
        }
      } catch (error) {
        console.error('Ошибка при уменьшении масштаба:', error);
        this.$emit('error', 'Не удалось изменить масштаб');
      }
    },
    
    resetZoom() {
      try {
        const canvas = this.modeler.get('canvas');
        if (canvas) {
          canvas.zoom('fit-viewport');
        }
      } catch (error) {
        console.error('Ошибка при сбросе масштаба:', error);
        this.$emit('error', 'Не удалось сбросить масштаб');
      }
    },
    
    handleBeforeUnload(event) {
      if (this.isModified) {
        // Автосохранение при закрытии браузера (синхронно)
        try {
          // Синхронное сохранение для beforeunload
          const { xml } = this.modeler.saveXML({ format: true });
          if (this.actualDiagramId) {
            // Отправляем запрос на сохранение синхронно
            const xhr = new XMLHttpRequest();
            xhr.open('PUT', `/api/bpmn-diagrams/${this.actualDiagramId}/`, false); // false = синхронно
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.setRequestHeader('Authorization', `Bearer ${localStorage.getItem('token') || sessionStorage.getItem('token')}`);
            xhr.send(JSON.stringify({
              name: 'Новая диаграмма',
              xml: xml
            }));
          }
        } catch (error) {
          console.error('Ошибка автосохранения:', error);
        }
        const message = 'У вас есть несохраненные изменения. Вы уверены, что хотите покинуть страницу?';
        event.returnValue = message;
        return message;
      }
    },
    
    closeDiagram() {
      if (this.isModified) {
        if (!confirm('У вас есть несохраненные изменения. Вы уверены, что хотите закрыть редактор?')) {
          return;
        }
      }
      this.$emit('close');
    },

    // Методы для управления доступом
    openShareModal() {
      this.showShareModal = true;
      this.fetchUsersWithAccess();
    },
    
    closeShareModal() {
      this.showShareModal = false;
      this.userSearchQuery = '';
      this.searchResults = [];
    },
    
    handleShareModalBackdrop(event) {
      if (event.target === event.currentTarget) {
        this.closeShareModal();
      }
    },
    
    // Обработчик фокуса на поле поиска
    async onSearchFocus() {
      if (!this.userSearchQuery.trim()) {
        await this.loadRandomUsers();
      }
    },

    // Загрузка случайных пользователей
    async loadRandomUsers() {
      this.isSearchingUsers = true;
      try {
        const users = await UserService.search('');
        this.searchResults = users.filter(user => 
          !this.usersWithAccess.some(access => access.user === user.id) &&
          user.id !== this.getCurrentUserId()
        );
      } catch (error) {
        console.error('Ошибка при загрузке случайных пользователей:', error);
        this.searchResults = [];
      } finally {
        this.isSearchingUsers = false;
      }
    },

    // Поиск пользователей с задержкой
    searchUsers() {
      if (this.searchTimeout) {
        clearTimeout(this.searchTimeout);
      }
      
      if (!this.userSearchQuery.trim()) {
        this.loadRandomUsers();
        return;
      }
      
      this.searchTimeout = setTimeout(async () => {
        this.isSearchingUsers = true;
        try {
          const users = await UserService.search(this.userSearchQuery);
          this.searchResults = users.filter(user => 
            !this.usersWithAccess.some(access => access.user === user.id) &&
            user.id !== this.getCurrentUserId()
          );
        } catch (error) {
          console.error('Ошибка при поиске пользователей:', error);
          this.searchResults = [];
        } finally {
          this.isSearchingUsers = false;
        }
      }, 300);
    },
    
    // Получение текущего ID пользователя
    getCurrentUserId() {
      try {
        const token = localStorage.getItem('token') || sessionStorage.getItem('token');
        if (token) {
          const payload = JSON.parse(atob(token.split('.')[1]));
          return payload.user_id;
        }
      } catch (error) {
        console.error('Ошибка при получении ID пользователя:', error);
      }
      return null;
    },
    
    // Получение пользователей с доступом к диаграмме
    async fetchUsersWithAccess() {
      try {
        const diagramId = this.actualDiagramId || this.diagramId;
        if (!diagramId) {
          console.log('Нет ID диаграммы для загрузки доступа');
          return;
        }
        
        // Проверяем, что диаграмма создана (не новая)
        if (!this.diagramCreated) {
          console.log('Диаграмма еще не создана, доступ будет доступен после сохранения');
          return;
        }
        
        const data = await BpmnService.getDiagramAccess(diagramId);
        this.usersWithAccess = data.shared_users || [];
        this.diagramOwner = data.owner || null;
      } catch (error) {
        console.error('Ошибка при получении пользователей с доступом:', error);
        this.usersWithAccess = [];
        // Если ошибка 404, это нормально для новой диаграммы
        if (error.response && error.response.status === 404) {
          console.log('Диаграмма еще не создана, доступ будет доступен после сохранения');
        }
      }
    },
    
    // Добавление доступа пользователю
    async addUserAccess(user) {
      try {
        const diagramId = this.actualDiagramId || this.diagramId;
        if (!diagramId) {
          console.error('ID диаграммы не определен');
          return;
        }
        
        const newAccess = await BpmnService.grantAccess(diagramId, user.id, 'edit');
        
        if (newAccess) {
          await this.fetchUsersWithAccess();
          this.searchResults = this.searchResults.filter(u => u.id !== user.id);
          console.log(`Доступ к диаграмме предоставлен пользователю: ${user.full_name || user.username}`);
        }
      } catch (error) {
        console.error('Ошибка при добавлении доступа:', error);
      }
    },
    
    // Обновление уровня доступа пользователя
    async updateUserAccess(access) {
      try {
        const updatedAccess = await BpmnService.updateAccess(access.id, access.access_level);
        if (updatedAccess) {
          console.log(`Уровень доступа для ${access.user_name} изменен на: ${access.access_level}`);
        }
      } catch (error) {
        console.error('Ошибка при обновлении доступа:', error);
      }
    },
    
    // Удаление доступа пользователя
    async removeUserAccess(accessId) {
      try {
        const result = await BpmnService.revokeAccess(accessId);
        if (result && result.success) {
          await this.fetchUsersWithAccess();
          console.log('Доступ пользователя удален');
        }
      } catch (error) {
        console.error('Ошибка при удалении доступа:', error);
      }
    },

    // ======================================
    // МЕТОДЫ СОВМЕСТНОГО РЕДАКТИРОВАНИЯ
    // ======================================
    
    /**
     * Инициализация совместного редактирования
     */
    initCollaborativeEditing() {
      console.log('🚀 Инициализация совместного редактирования');
      const diagramId = this.actualDiagramId || this.diagramId;
      if (!diagramId) {
        console.log('❌ Нет ID диаграммы для совместного редактирования');
        return;
      }
      
      console.log('📊 ID диаграммы:', diagramId);
      
      // Получаем токен из localStorage
      const token = localStorage.getItem('token') || sessionStorage.getItem('token');
      console.log('🔑 Токен:', token ? 'найден' : 'не найден');
      
      this.wsClient = new BpmnWebSocketClient(
        diagramId,
        this.handleWebSocketMessage,
        this.handleWebSocketError,
        token
      );
      
      this.wsClient.connect();
      
      // Обновляем состояние соединения
      this.isConnected = true;
      console.log('✅ WebSocket соединение установлено');
      
      // Запускаем периодическую очистку неактивных курсоров
      this.startCursorCleanup();
      
      // Запускаем периодическое автосохранение
      this.startAutoSave();
    },
    
    /**
     * Запуск периодической очистки неактивных курсоров
     */
    startCursorCleanup() {
      if (this.cursorCleanupInterval) {
        clearInterval(this.cursorCleanupInterval);
      }
      
      this.cursorCleanupInterval = setInterval(() => {
        const now = Date.now();
        for (const [userId, cursorData] of this.userCursors.entries()) {
          if (cursorData.lastUpdate && (now - cursorData.lastUpdate) > 5000) {
            this.userCursors.delete(userId);
            this.cursorLastUpdate.delete(userId);
            console.log('Удален неактивный курсор пользователя:', userId);
          }
        }
      }, 2000); // Проверяем каждые 2 секунды
    },
    
    /**
     * Остановка очистки курсоров
     */
    stopCursorCleanup() {
      if (this.cursorCleanupInterval) {
        clearInterval(this.cursorCleanupInterval);
        this.cursorCleanupInterval = null;
      }
    },
    
    /**
     * Запуск периодического автосохранения
     */
    startAutoSave() {
      if (this.autoSaveInterval) {
        clearInterval(this.autoSaveInterval);
      }
      
      this.autoSaveInterval = setInterval(() => {
        if (this.isModified && this.actualDiagramId && this.isConnected) {
          console.log('Периодическое автосохранение...');
          this.saveDiagram();
        }
      }, 30000); // Каждые 30 секунд
    },
    
    /**
     * Остановка периодического автосохранения
     */
    stopAutoSave() {
      if (this.autoSaveInterval) {
        clearInterval(this.autoSaveInterval);
        this.autoSaveInterval = null;
      }
    },
    
    /**
     * Обработка сообщений WebSocket
     */
    handleWebSocketMessage(type, data) {
      console.log('🔌 WebSocket сообщение:', type, data);
      switch (type) {
        case 'diagram_data':
          this.handleDiagramData(data);
          break;
        case 'active_users':
          this.activeUsers = data || [];
          this.isCollaborativeMode = this.activeUsers.length > 1;
          console.log('Обновлен список активных пользователей:', this.activeUsers);
          break;
        case 'user_joined':
          this.handleUserJoined(data);
          break;
        case 'user_left':
          this.handleUserLeft(data);
          break;
        case 'cursor_update':
          this.handleCursorUpdate(data);
          break;
        case 'operation_applied':
          this.handleOperationApplied(data);
          break;
        case 'selection_update':
          this.handleSelectionUpdate(data);
          break;
        case 'websocket_disconnected':
          this.handleWebSocketDisconnected();
          break;
      }
    },
    
    /**
     * Обработка ошибок WebSocket
     */
    handleWebSocketError(error) {
      console.error('WebSocket error:', error);
      this.isConnected = false;
    },
    
    /**
     * Обработка отключения WebSocket
     */
    async handleWebSocketDisconnected() {
      console.log('WebSocket отключен, выполняем автосохранение...');
      this.isConnected = false;
      
      // Автосохранение при отключении WebSocket
      if (this.isModified && this.actualDiagramId) {
        try {
          console.log('Автосохранение при отключении WebSocket...');
          await this.saveDiagram();
          console.log('Автосохранение завершено');
        } catch (error) {
          console.error('Ошибка автосохранения при отключении WebSocket:', error);
        }
      }
    },
    
    /**
     * Обработка данных диаграммы
     */
    handleDiagramData(data) {
      if (data && data.xml && data.xml !== this.currentXml) {
        console.log('Получены обновленные данные диаграммы');
        this.loadXml(data.xml);
        this.currentXml = data.xml;
        this.isModified = false;
      }
    },
    
    /**
     * Обработка присоединения пользователя
     */
    handleUserJoined(data) {
      console.log('👤 Пользователь присоединился:', data);
      // Проверяем, что пользователь еще не в списке
      const existingUser = this.activeUsers.find(user => user.user_id === data.user_id);
      if (!existingUser) {
        this.activeUsers.push({
          user_id: data.user_id,
          username: data.username,
          full_name: data.full_name || data.username
        });
        this.isCollaborativeMode = this.activeUsers.length > 1;
        console.log('✅ Активные пользователи:', this.activeUsers);
      }
    },
    
    /**
     * Обработка отключения пользователя
     */
    async handleUserLeft(data) {
      console.log('Пользователь покинул сессию:', data.username);
      this.activeUsers = this.activeUsers.filter(user => user.user_id !== data.user_id);
      this.userCursors.delete(data.user_id);
      this.cursorLastUpdate.delete(data.user_id);
      this.isCollaborativeMode = this.activeUsers.length > 1;
      console.log('Обновлен список активных пользователей после выхода:', this.activeUsers);
      
      // Автосохранение при выходе пользователя (синхронно)
      if (this.isModified) {
        try {
          console.log('Автосохранение при выходе пользователя...');
          await this.saveDiagram();
          console.log('Автосохранение завершено');
        } catch (error) {
          console.error('Ошибка автосохранения:', error);
        }
      }
      
      // Принудительно обновляем отображение курсоров
      this.$nextTick(() => {
        this.updateCursorDisplay();
      });
    },
    
    /**
     * Обработка обновления курсора
     */
    handleCursorUpdate(cursor) {
      console.log('🖱️ Обновление курсора:', cursor);
      if (cursor && cursor.user_id) {
        // Не показываем свой собственный курсор
        const currentUserId = this.getCurrentUserId();
        if (cursor.user_id != currentUserId) {
          this.userCursors.set(cursor.user_id, {
            user_id: cursor.user_id,
            username: cursor.username,
            full_name: cursor.full_name || cursor.username,
            x: cursor.x,
            y: cursor.y,
            lastUpdate: Date.now()
          });
          
          console.log('✅ Курсор добавлен:', cursor.user_id, this.userCursors.size);
          this.updateCursorDisplay();
        }
      }
    },
    
    /**
     * Обработка применения операции
     */
    handleOperationApplied(data) {
      console.log('🔄 Операция получена:', data);
      // Применяем операцию только если она не от текущего пользователя
      const currentUserId = this.getCurrentUserId();
      if (data.user_id && data.user_id != currentUserId) {
        this.applyOperationToModeler(data.operation || data);
        console.log('✅ Применена операция от пользователя:', data.user_id);
      }
    },
    
    /**
     * Обработка обновления выделения
     */
    handleSelectionUpdate(selection) {
      console.log('Обновлено выделение от пользователя:', selection.username);
      // Здесь должна быть логика отображения выделения других пользователей
    },
    
    /**
     * Отправка операции редактирования
     */
    sendOperation(operation) {
      if (this.wsClient && this.isConnected) {
        this.wsClient.sendOperation(operation);
      }
    },
    
    /**
     * Отправка обновления курсора
     */
    sendCursorUpdate(x, y) {
      if (this.wsClient && this.isConnected) {
        this.wsClient.sendCursorUpdate(x, y);
      }
    },
    
    /**
     * Отправка обновления выделения
     */
    sendSelection(selectedElements) {
      if (this.wsClient && this.isConnected) {
        this.wsClient.sendSelection(selectedElements);
      }
    },
    
    /**
     * Применение операции к BPMN модели
     */
    async applyOperationToModeler(operation) {
      try {
        if (operation.type === 'xml_update' && operation.xml) {
          console.log('Применяем XML обновление от другого пользователя');
          
          // Временно отключаем обработчики изменений
          const wasCollaborativeMode = this.isCollaborativeMode;
          this.isCollaborativeMode = false;
          
          // Пытаемся очистить диаграмму перед импортом нового XML
          try {
            this.modeler.clear();
            // Применяем обновленный XML к диаграмме
            await this.modeler.importXML(operation.xml);
            console.log('XML успешно применен через clear()');
          } catch (clearError) {
            console.log('Очистка не удалась, пробуем пересоздать диаграмму');
            // Если очистка не удалась, пересоздаем диаграмму
            const container = this.$refs.canvas;
            container.innerHTML = '';
            this.modeler = new BpmnModeler({ container });
            await this.modeler.importXML(operation.xml);
            
            // Переустанавливаем обработчики событий
            this.setupDiagramEventHandlers();
            console.log('XML успешно применен через пересоздание');
          }
          
          this.currentXml = operation.xml;
          this.isModified = false;
          
          // Восстанавливаем режим совместного редактирования
          this.isCollaborativeMode = wasCollaborativeMode;
          console.log('Операция применена успешно');
        }
      } catch (error) {
        console.error('Ошибка при применении операции к модели:', error);
        // Восстанавливаем режим совместного редактирования даже при ошибке
        this.isCollaborativeMode = true;
      }
    },
    
    /**
     * Обновление отображения курсоров
     */
    updateCursorDisplay() {
      // Обновление курсоров происходит автоматически через реактивность Vue
      // При изменении масштаба позиции курсоров пересчитываются автоматически
    },
    
    /**
     * Обработка событий мыши для отслеживания курсора
     */
    handleMouseMove(event) {
      if (this.isCollaborativeMode && this.wsClient && this.modeler) {
        const rect = this.$refs.canvas.getBoundingClientRect();
        const canvas = this.modeler.get('canvas');
        const zoom = canvas ? canvas.zoom() : 1;
        
        // Учитываем масштаб диаграммы
        const x = (event.clientX - rect.left) / zoom;
        const y = (event.clientY - rect.top) / zoom;
        
        this.sendCursorUpdate(x, y);
      }
    },
    
    /**
     * Обработка изменений диаграммы для совместного редактирования
     */
    async handleDiagramChange() {
      if (this.isCollaborativeMode && this.wsClient && this.isConnected) {
        // Очищаем предыдущий таймер
        if (this.diagramChangeTimeout) {
          clearTimeout(this.diagramChangeTimeout);
        }
        
        // Устанавливаем новый таймер с задержкой 300мс
        this.diagramChangeTimeout = setTimeout(async () => {
          try {
            // Получаем текущий XML диаграммы
            const { xml } = await this.modeler.saveXML({ format: true });
            
            // Проверяем, что XML действительно изменился
            if (xml !== this.currentXml) {
              this.currentXml = xml;
              
              // Отправляем операцию обновления XML
              this.sendOperation({
                type: 'xml_update',
                xml: xml,
                timestamp: Date.now()
              });
              
              console.log('Отправлено обновление диаграммы');
              
              // Автосохранение при изменении диаграммы (с задержкой)
              if (this.actualDiagramId) {
                setTimeout(async () => {
                  try {
                    await this.saveDiagram();
                    console.log('Автосохранение после изменения диаграммы');
                  } catch (error) {
                    console.error('Ошибка автосохранения после изменения:', error);
                  }
                }, 2000); // Сохраняем через 2 секунды после изменения
              }
            }
          } catch (error) {
            console.error('Ошибка при получении XML диаграммы:', error);
          }
        }, 300);
      }
    }
  }
};
</script>

<style>
/* Только базовые стили BPMN.js */
@import 'bpmn-js/dist/assets/diagram-js.css';
@import 'bpmn-js/dist/assets/bpmn-font/css/bpmn.css';
</style>

<style scoped>
/* ======================================
 * BPMN РЕДАКТОР - СТИЛИ В СТИЛЕ SCRIPTUM
 * ====================================== */

.bpmn-editor-page {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: white;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1000;
}

/* ======================================
 * HEADER - Упрощенный
 * ====================================== */
.bpmn-header {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0.75rem 1rem;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  z-index: 101;
  height: 60px;
  flex-shrink: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  justify-content: center;
  height: 100%;
}

.btn-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  height: 100%;
}

/* ======================================
 * КНОПКИ - Стандартизированные
 * ====================================== */
.btn-primary, .btn-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  height: 40px;
  padding: 0 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  min-width: 100px;
}

.btn-primary {
  background: #3b82f6;
  color: white;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #9ca3af;
}

.btn-secondary {
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.btn-secondary:hover {
  background: #f9fafb;
  border-color: #9ca3af;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.import-btn {
  position: relative;
  overflow: hidden;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  height: 40px !important;
}

.import-btn input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
  margin: 0;
  padding: 0;
  border: none;
}

/* ======================================
 * ИНСТРУМЕНТЫ В HEADER
 * ====================================== */

.zoom-controls {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  background: #f3f4f6;
  border-radius: 6px;
  padding: 0.25rem;
  border: 1px solid #e5e7eb;
  height: 40px;
}

.zoom-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: 4px;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s ease;
}

.zoom-btn:hover {
  background: white;
  color: #3b82f6;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.modification-indicator {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0 0.75rem;
  background: rgba(251, 191, 36, 0.1);
  color: #d97706;
  border: 1px solid rgba(251, 191, 36, 0.2);
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 500;
  height: 40px;
}

.modification-indicator i {
  font-size: 0.5rem;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* ======================================
 * ОСНОВНАЯ ОБЛАСТЬ РЕДАКТОРА - На всю страницу
 * ====================================== */
.bpmn-editor-main {
  flex: 1;
  display: flex;
  overflow: hidden;
  position: relative;
  background: white;
  height: calc(100vh - 60px);
}

.bpmn-canvas-container {
  flex: 1;
  position: relative;
  background: white;
  overflow: hidden;
  width: 100%;
  height: 100%;
}

.bpmn-canvas {
  width: 100%;
  height: 100%;
  position: relative;
}

/* ======================================
 * ИНДИКАТОР ЗАГРУЗКИ
 * ====================================== */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.95);
  z-index: 1000;
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  color: var(--text-light);
}

.loading-spinner i {
  font-size: 2rem;
  color: var(--primary-color);
}

.loading-spinner span {
  font-size: 0.875rem;
  font-weight: 500;
}

/* ======================================
 * КАСТОМИЗАЦИЯ BPMN.JS
 * ====================================== */

/* Панель инструментов - Адаптивная (+10% размер) */
:deep(.djs-palette) {
  background: white !important;
  border: 1px solid #e5e7eb !important;
  border-radius: 8px !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
  max-height: calc(100vh - 120px) !important;
  overflow-y: auto !important;
  width: 53px !important;
  position: fixed !important;
  top: 80px !important;
  left: 10px !important;
  z-index: 100 !important;
}

/* Адаптивная ширина панели инструментов (+10%) */
@media (max-width: 1400px) and (min-width: 1024px) {
  :deep(.djs-palette) {
    width: 50px !important;
    top: 85px !important;
  }
}

@media (max-width: 1024px) and (min-width: 768px) {
  :deep(.djs-palette) {
    width: 48px !important;
    top: 85px !important;
  }
}

@media (max-width: 768px) and (min-width: 600px) {
  :deep(.djs-palette) {
    width: 44px !important;
    top: 90px !important;
    left: 5px !important;
  }
}

@media (max-width: 600px) and (min-width: 480px) {
  :deep(.djs-palette) {
    width: 42px !important;
    top: 95px !important;
    left: 5px !important;
    max-height: calc(100vh - 135px) !important;
  }
}

@media (max-width: 480px) and (min-width: 360px) {
  :deep(.djs-palette) {
    width: 40px !important;
    top: 105px !important;
    left: 5px !important;
    max-height: calc(100vh - 145px) !important;
  }
}

@media (max-width: 360px) {
  :deep(.djs-palette) {
    width: 38px !important;
    top: 110px !important;
    left: 3px !important;
    max-height: calc(100vh - 150px) !important;
  }
}

:deep(.djs-palette .entry) {
  border-radius: 4px !important;
  margin: 1px !important;
  transition: all 0.2s ease !important;
  width: calc(100% - 4px) !important;
  height: 40px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  font-size: 18px !important;
}

:deep(.djs-palette .entry:hover) {
  background: rgba(59, 130, 246, 0.1) !important;
  color: #3b82f6 !important;
}

/* Адаптивные размеры элементов палитры (+10%) */
@media (max-width: 1400px) and (min-width: 1024px) {
  :deep(.djs-palette .entry) {
    height: 39px !important;
    font-size: 17px !important;
  }
}

@media (max-width: 1024px) and (min-width: 768px) {
  :deep(.djs-palette .entry) {
    height: 37px !important;
    font-size: 16px !important;
  }
}

@media (max-width: 768px) and (min-width: 600px) {
  :deep(.djs-palette .entry) {
    height: 35px !important;
    font-size: 15px !important;
  }
}

@media (max-width: 600px) and (min-width: 480px) {
  :deep(.djs-palette .entry) {
    height: 34px !important;
    font-size: 14px !important;
  }
}

@media (max-width: 480px) and (min-width: 360px) {
  :deep(.djs-palette .entry) {
    height: 33px !important;
    font-size: 13px !important;
  }
}

@media (max-width: 360px) {
  :deep(.djs-palette .entry) {
    height: 31px !important;
    font-size: 12px !important;
  }
}

/* Кастомный скроллбар для палитры */
:deep(.djs-palette::-webkit-scrollbar) {
  width: 4px !important;
}

:deep(.djs-palette::-webkit-scrollbar-track) {
  background: #f1f5f9 !important;
  border-radius: 2px !important;
}

:deep(.djs-palette::-webkit-scrollbar-thumb) {
  background: #cbd5e1 !important;
  border-radius: 2px !important;
}

:deep(.djs-palette::-webkit-scrollbar-thumb:hover) {
  background: #94a3b8 !important;
}

/* Контекстное меню */
:deep(.djs-context-pad) {
  background: white !important;
  border: 1px solid var(--border-color) !important;
  border-radius: 0.5rem !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}

:deep(.djs-context-pad .entry) {
  border-radius: 0.375rem !important;
  transition: all 0.2s ease !important;
}

:deep(.djs-context-pad .entry:hover) {
  background: var(--primary-color-light) !important;
  color: var(--primary-color) !important;
}

/* Выделение элементов */
:deep(.djs-shape.selected) {
  outline: 2px solid var(--primary-color) !important;
  outline-offset: 2px !important;
}

/* Панель свойств справа */
:deep(.bio-properties-panel) {
  background: white !important;
  border-left: 1px solid var(--border-color) !important;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.05) !important;
}

/* ======================================
 * ПОЛНАЯ АДАПТИВНОСТЬ
 * ====================================== */

/* Большие экраны (>1400px) */
@media (min-width: 1400px) {
  .bpmn-header {
    padding: 1rem 2rem;
  }
  
  .header-actions {
    gap: 1rem;
  }
  
  .btn-primary, .btn-secondary {
    min-width: 120px;
    font-size: 0.9rem;
  }
}

/* Средние экраны (1024px - 1400px) */
@media (max-width: 1400px) and (min-width: 1024px) {
  .bpmn-header {
    padding: 0.75rem 1.5rem;
  }
  
  .header-actions {
    gap: 0.875rem;
  }
  
  .btn-primary, .btn-secondary {
    min-width: 110px;
  }
}

/* Планшеты (768px - 1024px) */
@media (max-width: 1024px) and (min-width: 768px) {
  .bpmn-header {
    padding: 0.5rem 1rem;
    height: 65px;
  }
  
  .header-actions {
    gap: 0.75rem;
  }
  
  .btn-primary, .btn-secondary {
    min-width: 100px;
    font-size: 0.8rem;
  }
  
  .bpmn-editor-main {
    height: calc(100vh - 65px);
  }
}

/* Малые планшеты (600px - 768px) */
@media (max-width: 768px) and (min-width: 600px) {
  .bpmn-header {
    padding: 0.5rem;
    height: 70px;
  }
  
  .header-actions {
    flex-wrap: wrap;
    gap: 0.5rem;
    justify-content: center;
  }
  
  .btn-group {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .zoom-controls {
    order: -1;
    width: 100%;
    justify-content: center;
    margin-bottom: 0.5rem;
  }
  
  .btn-primary, .btn-secondary {
    min-width: 90px;
    font-size: 0.75rem;
  }
  
  .modification-indicator {
    font-size: 0.65rem;
    padding: 0 0.5rem;
    height: 36px;
  }
  
  .bpmn-editor-main {
    height: calc(100vh - 70px);
  }
}

/* Мобильные (480px - 600px) */
@media (max-width: 600px) and (min-width: 480px) {
  .bpmn-header {
    padding: 0.5rem;
    height: 75px;
  }
  
  .header-actions {
    flex-wrap: wrap;
    gap: 0.4rem;
    justify-content: center;
  }
  
  .btn-group {
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .btn-primary, .btn-secondary {
    min-width: 85px;
    height: 36px;
    font-size: 0.7rem;
    padding: 0 0.75rem;
  }
  
  .zoom-controls {
    height: 36px;
    order: -1;
    margin-bottom: 0.25rem;
  }
  
  .modification-indicator {
    height: 36px;
    font-size: 0.6rem;
  }
  
  .bpmn-editor-main {
    height: calc(100vh - 75px);
  }
}

/* Очень маленькие экраны (<480px) */
@media (max-width: 480px) {
  .bpmn-header {
    padding: 0.4rem;
    height: 85px;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 0.4rem;
    align-items: center;
  }
  
  .btn-group {
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
    gap: 0.3rem;
  }
  
  .btn-primary, .btn-secondary {
    min-width: 75px;
    height: 34px;
    font-size: 0.65rem;
    padding: 0 0.5rem;
  }
  
  .zoom-controls {
    height: 34px;
    order: -1;
    margin-bottom: 0.25rem;
  }
  
  .zoom-btn {
    width: 28px;
    height: 28px;
    font-size: 0.7rem;
  }
  
  .modification-indicator {
    height: 34px;
    font-size: 0.55rem;
    padding: 0 0.4rem;
  }
  
  .bpmn-editor-main {
    height: calc(100vh - 85px);
  }
}

/* Экстра маленькие экраны (<360px) */
@media (max-width: 360px) {
  .bpmn-header {
    height: 90px;
    padding: 0.3rem;
  }
  
  .btn-primary, .btn-secondary {
    min-width: 70px;
    height: 32px;
    font-size: 0.6rem;
  }
  
  .zoom-controls {
    height: 32px;
  }
  
  .zoom-btn {
    width: 26px;
    height: 26px;
  }
  
  .modification-indicator {
    height: 32px;
    font-size: 0.5rem;
  }
  
  .bpmn-editor-main {
    height: calc(100vh - 90px);
  }
}

/* ======================================
 * СТИЛИ ДЛЯ МОДАЛЬНОГО ОКНА УПРАВЛЕНИЯ ДОСТУПОМ
 * ====================================== */
.share-modal {
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: slideIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.share-content {
  padding: 1.5rem 2rem 0;
  flex: 1;
  overflow-y: auto;
}

.modal-footer {
  padding: 1.5rem 2rem 2rem;
  border-top: 1px solid #f3f4f6;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.modal-footer .btn-secondary {
  padding: 0.75rem 1.5rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: #ffffff;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.modal-footer .btn-secondary:hover {
  background: #f9fafb;
  border-color: #9ca3af;
  color: #374151;
}

.user-search-section,
.users-with-access-section {
  margin-bottom: 2rem;
}

.user-search-section h3,
.users-with-access-section h3 {
  margin: 0 0 1rem 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #f3f4f6;
}

.search-wrapper {
  position: relative;
  margin-bottom: 1rem;
}

.search-wrapper i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6b7280;
  font-size: 1rem;
  z-index: 1;
}

.user-search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  box-sizing: border-box;
  background: #ffffff;
  font-family: inherit;
}

.user-search-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.user-search-results {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  max-height: 200px;
  overflow-y: auto;
  background: #ffffff;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  margin-top: 0.5rem;
}

.user-search-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
  border-bottom: 1px solid #f3f4f6;
}

.user-search-item:last-child {
  border-bottom: none;
}

.user-search-item:hover {
  background-color: #f9fafb;
}

.user-avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #3B82F6, #1D4ED8);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1rem;
  flex-shrink: 0;
}

.user-info {
  flex: 1;
}

.user-name {
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

.user-email {
  color: #6B7280;
  font-size: 0.75rem;
  margin-top: 0.125rem;
}

.user-username {
  color: #3B82F6;
  font-size: 0.75rem;
  margin-top: 0.125rem;
  font-weight: 500;
}

.btn-add-user {
  background: #10B981;
  color: white;
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
  font-size: 0.875rem;
}

.btn-add-user:hover {
  background: #059669;
  transform: scale(1.05);
}

.access-user-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  margin-bottom: 0.5rem;
  background: white;
  transition: all 0.2s ease;
}

.access-user-item:hover {
  border-color: #d1d5db;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.access-user-item.owner {
  background: #fef3c7;
  border-color: #f59e0b;
}

.access-user-item.owner .user-avatar {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.access-level {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.access-select {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  font-size: 0.875rem;
  cursor: pointer;
  transition: border-color 0.2s ease;
}

.access-select:focus {
  outline: none;
  border-color: #3b82f6;
}

.access-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.access-badge.owner {
  background: #f59e0b;
  color: white;
}

.btn-remove-user {
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 50%;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
  font-size: 0.75rem;
}

  .btn-remove-user:hover {
    background: #dc2626;
    transform: scale(1.05);
  }

/* ======================================
 * ИНДИКАТОР СОВМЕСТНОГО РЕДАКТИРОВАНИЯ
 * ====================================== */
.collaboration-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #10B981, #059669);
  color: white;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
  animation: pulse 2s infinite;
}

.collaboration-indicator i {
  font-size: 0.75rem;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

/* ======================================
 * ВИДЖЕТ АКТИВНЫХ ПОЛЬЗОВАТЕЛЕЙ
 * ====================================== */
.active-users-widget {
  position: absolute;
  top: 80px;
  right: 20px;
  z-index: 100;
  max-width: 250px;
  animation: slideInRight 0.3s ease-out;
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Адаптивность для мобильных устройств */
@media (max-width: 768px) {
  .active-users-widget {
    position: fixed;
    top: 70px;
    right: 10px;
    left: 10px;
    max-width: none;
  }
}

.no-users-found,
.search-loading,
.no-shared-users {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
  font-style: italic;
  font-size: 0.875rem;
}

.no-users-found i,
.search-loading i,
.no-shared-users i {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  color: #d1d5db;
}

.search-loading i {
  color: #3b82f6;
}

/* Адаптивность для мобильных устройств */
@media (max-width: 768px) {
  .share-modal {
    max-width: 95vw;
    margin: 1rem;
  }
  
  .share-content {
    padding: 1rem 1.5rem 1.5rem;
  }
  
  .access-user-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .access-user-item .user-info {
    width: 100%;
  }
  
  .access-user-item .access-level {
    align-self: flex-start;
  }
  
  .btn-remove-user {
    position: absolute;
    top: 0.5rem;
    right: 0.5rem;
  }
}
</style>