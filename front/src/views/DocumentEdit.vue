<template>
  <div class="document-edit">
    <div class="document-edit-header">
      <h1>{{ document.name }}</h1>
      <div class="document-actions">
        <button class="btn-primary" @click="saveDocument">
          <i class="fas fa-save"></i> Сохранить
        </button>
        <button class="btn-secondary" @click="openShareModal">
          <i class="fas fa-share-alt"></i> Поделиться
        </button>
        <button class="btn-secondary" @click="togglePreview">
          <i class="fas" :class="showPreview ? 'fa-edit' : 'fa-eye'"></i> {{ showPreview ? 'Режим редактирования' : 'Режим предпросмотра' }}
        </button>
        <button class="btn-secondary" @click="openHistoryModal">
          <i class="fas fa-history"></i> История
        </button>
        <button class="btn-secondary" @click="goBack">
          <i class="fas fa-arrow-left"></i> Назад
        </button>
      </div>
    </div>
    
    <div class="document-info">
      <div class="info-item">
        <span class="label">Тип:</span>
        <span class="value">{{ document.type }}</span>
      </div>
      <div class="info-item">
        <span class="label">Статус:</span>
        <span class="value" :class="'status-badge ' + document.status">{{ document.status }}</span>
      </div>
      <div class="info-item">
        <span class="label">Дата создания:</span>
        <span class="value">{{ document.created }}</span>
      </div>
    </div>
    
    <div class="document-edit-container">
      <!-- Отображение документа в зависимости от типа файла -->
      <div v-if="document.file_type === 'pdf'" class="pdf-viewer">
        <iframe :src="document.file" width="100%" height="600" frameborder="0"></iframe>
      </div>
      
      <!-- Для doc/docx файлов показываем сообщение о необходимости редактирования в CKEditor -->
      <div v-else-if="document.file_type === 'doc' || document.file_type === 'docx'" class="doc-info">
        <p>Файл {{ document.file_type }} загружен. Используйте редактор ниже для внесения изменений.</p>
        <a href="#" @click.prevent="openOriginalFile" class="btn-link">
          <i class="fas fa-external-link-alt"></i> Открыть оригинальный файл
        </a>
      </div>
      
      <!-- Переключение между редактором и предпросмотром -->
      <div class="editor-preview-container">
        <!-- CKEditor для редактирования содержимого -->
        <div v-if="!showPreview" class="editor-container a4-paper">
          <ckeditor 
            ref="ckeditor" 
            :editor="editor" 
            v-model="document.content" 
            :config="editorConfig"
            @ready="onEditorReady"
            @input="updatePreview"
          ></ckeditor>
        </div>
        
        <!-- Предпросмотр документа -->
        <div v-else class="preview-container a4-paper">
          <div class="preview-header">
            <h3>Предпросмотр</h3>
          </div>
          <div class="preview-content" v-html="document.content"></div>
        </div>
      </div>
    </div>
    
    <!-- Модальное окно истории изменений -->
    <div v-if="showHistoryModal" class="modal" @click="handleHistoryModalBackdrop">
      <div class="modal-content history-modal" @click.stop>
        <button class="close-btn" @click="closeHistoryModal">
          <i class="fas fa-times"></i>
        </button>
        
        <div class="modal-header">
          <h2>История изменений</h2>
          <p class="modal-subtitle">Просмотр и восстановление предыдущих версий документа</p>
        </div>
        
        <div class="history-modal-content">
          <div class="history-actions">
            <button class="btn-refresh" @click="fetchDocumentHistory" title="Обновить историю">
              <i class="fas fa-sync-alt"></i>
              Обновить
            </button>
          </div>
          
          <div v-if="isLoadingHistory" class="history-loading">
            <i class="fas fa-spinner fa-spin"></i> Загрузка истории...
          </div>
          
          <div v-else-if="documentHistory.length === 0" class="history-empty">
            <i class="fas fa-history"></i>
            <p>История изменений пуста</p>
          </div>
          
          <ul v-else class="history-list">
            <li v-for="item in documentHistory" :key="item.id" class="history-item" :class="{ 'active': selectedHistoryItem === item.id }">
              <div class="history-item-header" @click="selectHistoryItem(item)">
                <div class="history-item-title">
                  <span class="version-name">{{ item.version_name }}</span>
                  <span class="version-date">{{ item.created_at_formatted }}</span>
                </div>
                <div class="history-item-user">{{ item.user_name }}</div>
              </div>
              
              <div v-if="selectedHistoryItem === item.id" class="history-item-actions">
                <button class="btn-restore" @click="restoreVersion(item.id)">
                  <i class="fas fa-undo"></i> Восстановить версию
                </button>
              </div>
            </li>
          </ul>
        </div>
        
        <div v-if="showVersionNameInput" class="version-name-input">
          <label for="versionName">Название версии:</label>
          <input type="text" id="versionName" v-model="versionName" placeholder="Введите название версии">
          <div class="version-name-actions">
            <button class="btn-primary" @click="saveWithVersionName">Сохранить</button>
            <button class="btn-secondary" @click="cancelVersionName">Отмена</button>
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
          <h2>Управление доступом</h2>
          <p class="modal-subtitle">Предоставьте доступ к документу другим пользователям</p>
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
                placeholder="Поиск пользователей по имени или email..."
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
              <i class="fas" :class="document.is_owner ? 'fa-users' : 'fa-info-circle'"></i>
              {{ document.is_owner ? 'Пользователи с доступом' : 'Информация о доступе' }}
            </h3>
            
            <!-- Владелец документа (показывается только владельцу) -->
            <div v-if="document.is_owner" class="access-user-item owner">
              <div class="user-avatar">
                <i class="fas fa-crown"></i>
              </div>
              <div class="user-info">
                <div class="user-name">{{ documentOwner ? documentOwner.user_name : 'Вы' }}</div>
                <div class="user-role">Владелец документа</div>
              </div>
              <div class="access-level">
                <span class="access-badge owner">Полный доступ</span>
              </div>
            </div>
            
            <!-- Информация о том, кто предоставил доступ (показывается только получателям) -->
            <div v-else class="access-user-item granted-by">
              <div class="user-avatar">
                <i class="fas fa-user-shield"></i>
              </div>
              <div class="user-info">
                <div class="user-name">{{ documentOwner ? documentOwner.user_name : 'Пользователь' }}</div>
                <div class="user-role">Предоставил вам доступ</div>
              </div>
              <div class="access-level">
                <span class="access-badge granted">Доступ предоставлен</span>
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
                <span class="access-badge">Доступ предоставлен</span>
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
              <p>Документ пока не был предоставлен другим пользователям</p>
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
import { DocumentService, UserService } from '../api/services';
import ClassicEditor from '@ckeditor/ckeditor5-build-classic';
import '@ckeditor/ckeditor5-build-classic/build/translations/ru';

export default {
  name: 'DocumentEdit',
  components: {
    // CKEditor регистрируется глобально в main.js через app.use(CKEditor)
  },
  data() {
    return {
      document: {
        id: null,
        name: '',
        type: '',
        status: '',
        created: '',
        content: '', // Инициализируем пустой строкой по умолчанию
        file: null,
        file_type: null
      },
      showPreview: true, // Показывать предпросмотр по умолчанию
      editor: ClassicEditor,
      editorInstance: null, // Ссылка на экземпляр редактора
      editorConfig: {
        language: 'ru',
        toolbar: [
          'heading', '|', 
          'bold', 'italic', 'link', 'bulletedList', 'numberedList', '|', 
          'indent', 'outdent', '|', 
          'blockQuote', 'insertTable', 'undo', 'redo'
        ]
      },
      // Данные для истории документа
      documentHistory: [],
      isLoadingHistory: false,
      selectedHistoryItem: null,
      showVersionNameInput: false,
      versionName: '',
      showHistoryModal: false,
      // Данные для управления доступом
      showShareModal: false,
      userSearchQuery: '',
      searchResults: [],
      isSearchingUsers: false,
      usersWithAccess: [],
      documentOwner: null,
      searchTimeout: null
    };
  },
  created() {
    // Получаем ID документа из параметров маршрута
    const documentId = this.$route.params.id;
    if (documentId) {
      this.fetchDocument(documentId);
      this.fetchDocumentHistory();
    }
  },
  methods: {
    async fetchDocument(id) {
      try {
        // Получаем содержимое документа для редактирования
        const documentData = await DocumentService.getContent(id);
        console.log('Полученные данные документа:', documentData); // Отладочный вывод
        
        // Проверяем, есть ли содержимое в полученных данных
        if (documentData && typeof documentData === 'object') {
          // Убедимся, что content всегда будет строкой и не undefined/null
          this.document = {
            ...documentData,
            id: id,
            content: documentData.content || ''
          };
          
          console.log('Установленное содержимое документа:', this.document.content); // Отладочный вывод
          console.log('Данные о документе:', this.document); // Отладка
          console.log('document.is_owner:', this.document.is_owner); // Отладка
          
          // Если поле is_owner отсутствует, определяем владельца по наличию прав на редактирование
          if (this.document.is_owner === undefined || this.document.is_owner === null) {
            // Если у пользователя есть доступ к редактированию документа, то он либо владелец, либо имеет доступ
            // Проверим через API информацию о доступе
            this.checkOwnership();
          }
        } else {
          console.error('Получены некорректные данные документа:', documentData);
          this.document.id = id;
        }
        
        // Принудительно обновляем содержимое редактора
        this.$nextTick(() => {
          if (this.$refs.ckeditor && this.editorInstance) {
            console.log('Устанавливаем содержимое в редактор через nextTick:', this.document.content);
            this.editorInstance.setData(this.document.content);
          }
        });
      } catch (error) {
        console.error('Ошибка при получении документа:', error);
        this.$router.push('/documents');
      }
    },
    
    // Проверка владения документом
    async checkOwnership() {
      try {
        const accessData = await DocumentService.getDocumentAccess(this.document.id);
        console.log('Данные о доступе:', accessData);
        
        if (accessData && accessData.owner) {
          // Получаем текущего пользователя
          const currentUserId = this.getCurrentUserId();
          console.log('Текущий пользователь ID:', currentUserId);
          console.log('Владелец документа ID:', accessData.owner.user_id);
          
          // Определяем, является ли текущий пользователь владельцем
          this.document.is_owner = currentUserId === accessData.owner.user_id;
          console.log('Обновленный is_owner:', this.document.is_owner);
        }
      } catch (error) {
        console.error('Ошибка при проверке владения:', error);
        // По умолчанию считаем, что пользователь не владелец
        this.document.is_owner = false;
      }
    },
    
    // Получение истории документа
    async fetchDocumentHistory() {
      if (!this.document.id) return;
      
      this.isLoadingHistory = true;
      try {
        const history = await DocumentService.getHistory(this.document.id);
        this.documentHistory = history;
        console.log('История документа:', history);
      } catch (error) {
        console.error('Ошибка при получении истории документа:', error);
      } finally {
        this.isLoadingHistory = false;
      }
    },
    
    // Выбор элемента истории для просмотра
    selectHistoryItem(item) {
      if (this.selectedHistoryItem === item.id) {
        // Если элемент уже выбран, снимаем выделение
        this.selectedHistoryItem = null;
      } else {
        // Иначе выбираем элемент
        this.selectedHistoryItem = item.id;
      }
    },
    
    // Восстановление версии документа из истории
    async restoreVersion(historyId) {
      if (!confirm('Вы уверены, что хотите восстановить эту версию документа? Текущие изменения будут сохранены в истории.')) {
        return;
      }
      
      try {
        const result = await DocumentService.restoreVersion(this.document.id, historyId);
        
        // Обновляем содержимое документа
        this.document.content = result.content;
        
        // Обновляем содержимое редактора
        if (this.editorInstance) {
          this.editorInstance.setData(this.document.content);
        }
        
        // Обновляем историю
        this.fetchDocumentHistory();
        
        // Сбрасываем выбранный элемент
        this.selectedHistoryItem = null;
        
        alert(result.message || 'Версия документа успешно восстановлена');
      } catch (error) {
        console.error('Ошибка при восстановлении версии документа:', error);
        alert('Ошибка при восстановлении версии документа');
      }
    },
    
    // Показать диалог для ввода названия версии
    showVersionNameDialog() {
      this.showVersionNameInput = true;
      this.versionName = '';
    },
    
    // Отмена ввода названия версии
    cancelVersionName() {
      this.showVersionNameInput = false;
      this.versionName = '';
    },
    
    // Сохранение документа с названием версии
    async saveWithVersionName() {
      if (!this.versionName.trim()) {
        alert('Пожалуйста, введите название версии');
        return;
      }
      
      try {
        await DocumentService.updateContent(this.document.id, this.document.content || '', this.versionName);
        this.showVersionNameInput = false;
        this.versionName = '';
        
        // Обновляем историю
        this.fetchDocumentHistory();
        
        alert('Документ успешно сохранен с названием версии');
      } catch (error) {
        console.error('Ошибка при сохранении документа с названием версии:', error);
        alert('Ошибка при сохранении документа');
      }
    },
    
    // Обычное сохранение документа
    async saveDocument() {
      // Предлагаем пользователю ввести название версии
      if (confirm('Хотите добавить название для этой версии документа?')) {
        this.showVersionNameDialog();
        return;
      }
      
      try {
        // Сохраняем только содержимое документа, убедившись, что content не null/undefined
        await DocumentService.updateContent(this.document.id, this.document.content || '');
        
        // Обновляем историю
        this.fetchDocumentHistory();
        
        alert('Документ успешно сохранен');
      } catch (error) {
        console.error('Ошибка при сохранении документа:', error);
        alert('Ошибка при сохранении документа');
      }
    },
    
    goBack() {
      this.$router.push('/documents');
    },
    
    // Методы для модального окна истории
    openHistoryModal() {
      this.showHistoryModal = true;
      this.fetchDocumentHistory();
    },
    
    closeHistoryModal() {
      this.showHistoryModal = false;
      this.selectedHistoryItem = null;
    },
    
    handleHistoryModalBackdrop(event) {
      if (event.target === event.currentTarget) {
        this.closeHistoryModal();
      }
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
      // Если поле пустое, показываем случайных пользователей
      if (!this.userSearchQuery.trim()) {
        await this.loadRandomUsers();
      }
    },

    // Загрузка случайных пользователей
    async loadRandomUsers() {
      this.isSearchingUsers = true;
      try {
        const users = await UserService.search(''); // Пустой запрос вернет случайных пользователей
        // Фильтруем пользователей, исключая тех, у кого уже есть доступ
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
      
      // Если поле очистили, показываем случайных пользователей
      if (!this.userSearchQuery.trim()) {
        this.loadRandomUsers();
        return;
      }
      
      this.searchTimeout = setTimeout(async () => {
        this.isSearchingUsers = true;
        try {
          const users = await this.fetchUsers(this.userSearchQuery);
          // Фильтруем пользователей, исключая тех, у кого уже есть доступ
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
    
    // Получение списка пользователей через API
    async fetchUsers(query) {
      try {
        const users = await UserService.search(query);
        return users;
      } catch (error) {
        console.error('Ошибка при поиске пользователей:', error);
        return [];
      }
    },
    
    // Получение текущего ID пользователя
    getCurrentUserId() {
      // Получаем ID из токена или другого источника
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
    
    // Получение пользователей с доступом к документу
    async fetchUsersWithAccess() {
      try {
        const data = await DocumentService.getDocumentAccess(this.document.id);
        this.usersWithAccess = data.shared_users || [];
        this.documentOwner = data.owner || null;
      } catch (error) {
        console.error('Ошибка при получении пользователей с доступом:', error);
        this.usersWithAccess = [];
      }
    },
    
    // Добавление доступа пользователю
    async addUserAccess(user) {
      try {
        const newAccess = await DocumentService.grantAccess(this.document.id, user.id);
        
        if (newAccess) {
          // Обновляем список пользователей с доступом
          await this.fetchUsersWithAccess();
          
          // Удаляем пользователя из результатов поиска
          this.searchResults = this.searchResults.filter(u => u.id !== user.id);
          
          console.log(`Доступ предоставлен пользователю: ${user.first_name} ${user.last_name}`);
        }
      } catch (error) {
        console.error('Ошибка при добавлении доступа:', error);
      }
    },
    
    // Обновление уровня доступа пользователя
    async updateUserAccess(access) {
      try {
        const updatedAccess = await DocumentService.updateAccess(access.id, access.access_level);
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
        const result = await DocumentService.revokeAccess(accessId);
        if (result && result.success) {
          // Обновляем список пользователей с доступом
          await this.fetchUsersWithAccess();
          console.log('Доступ пользователя удален');
        }
      } catch (error) {
        console.error('Ошибка при удалении доступа:', error);
      }
    },
    
    // Обработчик события готовности редактора
    onEditorReady(editor) {
      // Сохраняем ссылку на экземпляр редактора
      this.editorInstance = editor;
      
      // Если у нас уже есть содержимое документа, устанавливаем его в редактор
      if (this.document.content) {
        console.log('Устанавливаем содержимое в редактор при инициализации:', this.document.content);
        // Используем метод setData редактора для установки содержимого
        editor.setData(this.document.content);
      }
    },
    
    // Обновление предпросмотра при изменении содержимого
    updatePreview() {
      // Предпросмотр обновляется автоматически благодаря v-html и v-model
      console.log('Содержимое обновлено для предпросмотра');
      // Если мы в режиме предпросмотра, убедимся, что содержимое актуально
      if (this.showPreview && this.document.content) {
        this.$nextTick(() => {
          // Принудительное обновление DOM для предпросмотра
          this.$forceUpdate();
        });
      }
    },
    
    // Открытие оригинального файла
    openOriginalFile() {
      if (this.document.file) {
        // Открываем файл в новом окне
        window.open(this.document.file, '_blank');
      } else {
        alert('Оригинальный файл недоступен');
      }
    },
    
    // Переключение режима предпросмотра
    togglePreview() {
      this.showPreview = !this.showPreview;
      // Обновляем содержимое предпросмотра при переключении в режим предпросмотра
      if (this.showPreview && this.editorInstance) {
        this.updatePreview();
      }
    }
  },
  beforeUnmount() {
    // Очищаем таймер поиска при уничтожении компонента
    if (this.searchTimeout) {
      clearTimeout(this.searchTimeout);
    }
  }
};
</script>

<style scoped>
.document-edit {
  padding: 0;
  background-color: transparent;
  min-height: 100vh;
}

.document-edit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: var(--card-background);
  border-radius: var(--border-radius-lg);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color);
}

.document-edit-header h1 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-color);
}

.document-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

/* Современные кнопки */
.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: linear-gradient(135deg, var(--primary-color) 0%, #2563eb 100%);
  color: white;
  border: none;
  border-radius: var(--border-radius-lg);
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.btn-primary:hover {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: var(--card-background);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background: rgba(59, 130, 246, 0.05);
  border-color: var(--primary-color);
  color: var(--primary-color);
  transform: translateY(-1px);
}

.btn-upload {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  border-radius: var(--border-radius-lg);
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
}

.btn-upload:hover {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

.document-info {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: var(--card-background);
  border-radius: var(--border-radius-lg);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color);
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.value {
  font-weight: 500;
  color: var(--text-color);
  font-size: 0.875rem;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.875rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge::before {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.status-badge.draft {
  background: rgba(113, 128, 150, 0.15);
  color: #64748b;
}

.status-badge.draft::before {
  background: #64748b;
}

.status-badge.review {
  background: rgba(245, 158, 11, 0.15);
  color: #d97706;
}

.status-badge.review::before {
  background: #d97706;
}

.status-badge.approved {
  background: rgba(34, 197, 94, 0.15);
  color: #059669;
}

.status-badge.approved::before {
  background: #059669;
}

.document-edit-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: calc(100vh - 200px);
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 2rem;
}

.pdf-viewer {
  margin-bottom: 1.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.doc-info {
  margin-bottom: 1.5rem;
  padding: 1.25rem;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(59, 130, 246, 0.02) 100%);
  border-radius: var(--border-radius-lg);
  border: 1px solid rgba(59, 130, 246, 0.1);
  color: var(--primary-color);
}

.btn-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--primary-color);
  text-decoration: none;
  margin-top: 0.75rem;
  font-weight: 500;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.btn-link:hover {
  color: #2563eb;
  text-decoration: underline;
  transform: translateX(2px);
}

.editor-preview-container {
  width: 100%;
  display: flex;
  justify-content: center;
}

/* Стили для листа A4 */
.a4-paper {
  width: 210mm;
  min-height: 297mm;
  background: #ffffff;
  box-shadow: 
    0 0 0 1px rgba(0, 0, 0, 0.1),
    0 4px 8px rgba(0, 0, 0, 0.1),
    0 8px 16px rgba(0, 0, 0, 0.1),
    0 16px 32px rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  overflow: hidden;
  transition: all 0.3s ease;
  position: relative;
}

.a4-paper::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0) 100%);
  pointer-events: none;
  z-index: 1;
}

.a4-paper:focus-within {
  box-shadow: 
    0 0 0 2px var(--primary-color),
    0 4px 12px rgba(59, 130, 246, 0.2),
    0 8px 24px rgba(59, 130, 246, 0.15),
    0 16px 48px rgba(59, 130, 246, 0.1);
}

.editor-container {
  border: none;
  border-radius: 4px;
  overflow: hidden;
  transition: all 0.3s ease;
  background: #ffffff;
}

.editor-container.full-width,
.preview-container.full-width {
  width: 100%;
}

.preview-container {
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: var(--card-background);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.preview-header {
  padding: 1rem 1.25rem;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(59, 130, 246, 0.02) 100%);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-header h3 {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-color);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.preview-content {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
  min-height: 400px;
  max-height: 600px;
  color: var(--text-color);
  line-height: 1.6;
}

/* Стили для CKEditor в стиле A4 */
.a4-paper .ck-editor__editable {
  min-height: 297mm;
  max-height: none;
  border: none !important;
  border-radius: 0 !important;
  font-family: 'Times New Roman', Times, serif;
  font-size: 12pt;
  line-height: 1.5;
  color: #000000;
  padding: 25.4mm 20mm 25.4mm 20mm; /* A4 margins: 1 inch top/bottom, 0.8 inch left/right */
  background: #ffffff;
  position: relative;
  z-index: 2;
}

.a4-paper .ck-editor__editable:focus {
  box-shadow: none !important;
  outline: none !important;
}

.a4-paper .ck-toolbar {
  border: none !important;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1) !important;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%) !important;
  border-radius: 4px 4px 0 0 !important;
  padding: 8px 16px !important;
  position: relative;
  z-index: 3;
}

.a4-paper .ck-button {
  border-radius: 4px !important;
  margin: 0 2px !important;
  transition: all 0.2s ease !important;
}

.a4-paper .ck-button:hover {
  background: rgba(59, 130, 246, 0.1) !important;
  transform: translateY(-1px) !important;
}

.a4-paper .ck-button.ck-on {
  background: var(--primary-color) !important;
  color: white !important;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3) !important;
}

/* Стили для превью в формате A4 */
.preview-container.a4-paper {
  border: none;
}

.preview-container.a4-paper .preview-header {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 4px 4px 0 0;
  padding: 8px 16px;
  position: relative;
  z-index: 3;
}

.preview-container.a4-paper .preview-content {
  font-family: 'Times New Roman', Times, serif;
  font-size: 12pt;
  line-height: 1.5;
  color: #000000;
  padding: 25.4mm 20mm 25.4mm 20mm;
  background: #ffffff;
  min-height: 297mm;
  position: relative;
  z-index: 2;
}

/* Стили для модального окна истории */
.history-modal {
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
}

.history-modal-content {
  padding: 1.5rem 0;
  max-height: 60vh;
  overflow-y: auto;
}

.history-actions {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 1rem;
  padding: 0 1.5rem;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.history-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color);
}

.btn-refresh {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--primary-color);
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: var(--border-radius);
  transition: all 0.2s ease;
}

.btn-refresh:hover {
  background: rgba(59, 130, 246, 0.1);
  border-color: var(--primary-color);
  color: #2563eb;
  transform: translateY(-1px);
}

.btn-refresh i {
  transition: transform 0.3s ease;
}

.btn-refresh:hover i {
  transform: rotate(180deg);
}

.history-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 0;
  color: var(--text-muted);
  font-size: 0.875rem;
  gap: 0.5rem;
}

.history-loading i {
  color: var(--primary-color);
}

.history-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem 0;
  color: var(--text-muted);
  text-align: center;
}

.history-empty i {
  font-size: 2rem;
  margin-bottom: 0.75rem;
  color: var(--text-light);
}

.history-empty p {
  margin: 0;
  font-size: 0.875rem;
}

.history-list {
  list-style: none;
  padding: 0 1.5rem;
  margin: 0;
  overflow-y: auto;
  flex: 1;
}

.history-item {
  background: #ffffff;
  border-radius: var(--border-radius-lg);
  margin-bottom: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color);
  overflow: hidden;
  transition: all 0.3s ease;
}

.history-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
}

.history-item.active {
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2);
  border-color: var(--primary-color);
  transform: translateY(-1px);
}

.history-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--primary-color);
}

.history-item-header {
  padding: 1rem;
  cursor: pointer;
  position: relative;
}

.history-item-title {
  display: flex;
  flex-direction: column;
  margin-bottom: 0.5rem;
}

.version-name {
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--text-color);
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.version-date {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.history-item-user {
  font-size: 0.75rem;
  color: var(--text-light);
  font-weight: 500;
}

.history-item-actions {
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.02) 0%, rgba(59, 130, 246, 0.01) 100%);
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
}

.btn-restore {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.875rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--border-radius);
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-restore:hover {
  background: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4);
}

.version-name-input {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--card-background);
  padding: 1.25rem;
  box-shadow: 0 -4px 15px rgba(0, 0, 0, 0.1);
  z-index: 10;
  border-top: 1px solid var(--border-color);
  border-radius: 0 0 var(--border-radius-lg) var(--border-radius-lg);
}

.version-name-input label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-color);
}

.version-name-input input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  margin-bottom: 1rem;
  font-size: 0.875rem;
  background: var(--card-background);
  color: var(--text-color);
  transition: all 0.3s ease;
}

.version-name-input input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.version-name-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

/* Адаптивность */
@media (max-width: 1024px) {
  .document-edit-container {
    padding: 1rem;
  }
  
  .a4-paper {
    width: 100%;
    max-width: 210mm;
    min-height: auto;
  }
  
  .a4-paper .ck-editor__editable {
    min-height: 60vh;
    padding: 2rem 1.5rem;
  }
  
  .preview-container.a4-paper .preview-content {
    min-height: 60vh;
    padding: 2rem 1.5rem;
  }
}

@media (max-width: 768px) {
  .document-edit-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
    padding: 1rem;
  }
  
  .document-actions {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .btn-primary,
  .btn-secondary {
    flex: 1;
    justify-content: center;
    min-width: 140px;
  }
  
  .document-info {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }
  
  .info-item {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }
  
  .document-edit-container {
    padding: 0.5rem;
    min-height: calc(100vh - 150px);
  }
  
  .a4-paper {
    width: 100%;
    min-height: 50vh;
    box-shadow: 
      0 0 0 1px rgba(0, 0, 0, 0.1),
      0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .a4-paper .ck-editor__editable {
    min-height: 50vh;
    padding: 1rem;
    font-size: 14px;
  }
  
  .preview-container.a4-paper .preview-content {
    min-height: 50vh;
    padding: 1rem;
    font-size: 14px;
  }
  
  .history-modal {
    width: 95%;
    max-height: 90vh;
  }
}

@media (max-width: 480px) {
  .document-edit-header h1 {
    font-size: 1.25rem;
  }
  
  .document-actions {
    flex-direction: column;
  }
  
  .btn-primary,
  .btn-secondary {
    width: 100%;
  }
  
  .document-info {
    padding: 0.75rem;
  }
  
  .document-edit-container {
    padding: 0.25rem;
    background: #f5f5f5;
  }
  
  .a4-paper {
    border-radius: 8px;
    min-height: 40vh;
  }
  
  .a4-paper .ck-editor__editable {
    min-height: 40vh;
    padding: 0.75rem;
    font-size: 13px;
  }
  
  .preview-container.a4-paper .preview-content {
    min-height: 40vh;
    padding: 0.75rem;
    font-size: 13px;
  }
  
  .history-modal {
    width: 98%;
    max-height: 95vh;
  }
  
  .history-modal-content {
    max-height: 70vh;
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

.user-search-section h3 i,
.users-with-access-section h3 i {
  color: #6b7280;
  font-size: 1rem;
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

.user-role {
  color: #059669;
  font-size: 0.875rem;
  font-weight: 500;
  margin-top: 0.125rem;
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
  background: linear-gradient(135deg, #fef3c7 0%, #f59e0b 20%, #fde68a 100%);
  border: 3px solid #d97706;
  box-shadow: 
    0 8px 25px -5px rgba(245, 158, 11, 0.4),
    0 0 0 1px rgba(245, 158, 11, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  position: relative;
  overflow: hidden;
}

.access-user-item.owner::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #f59e0b, #d97706, #b45309);
}

.access-user-item.owner .user-avatar {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 50%, #b45309 100%);
  box-shadow: 
    0 4px 14px rgba(245, 158, 11, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.access-user-item.owner .user-name {
  color: #78350f;
  font-weight: 800;
  font-size: 1rem;
  text-shadow: 0 1px 2px rgba(245, 158, 11, 0.2);
}

.access-user-item.owner .user-role {
  color: #92400e;
  font-weight: 700;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.access-user-item.granted-by {
  background: linear-gradient(135deg, #dbeafe 0%, #93c5fd 20%, #bfdbfe 100%);
  border: 2px solid #2563eb;
  box-shadow: 
    0 6px 20px -5px rgba(59, 130, 246, 0.3),
    0 0 0 1px rgba(59, 130, 246, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  position: relative;
}

.access-user-item.granted-by .user-avatar {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 50%, #1e40af 100%);
  box-shadow: 
    0 3px 12px rgba(59, 130, 246, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.2);
}

.access-user-item.granted-by .user-name {
  color: #1e3a8a;
  font-weight: 700;
  font-size: 0.95rem;
}

.access-user-item.granted-by .user-role {
  color: #1d4ed8;
  font-weight: 600;
  font-size: 0.875rem;
}

.access-level {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.access-select {
  padding: 0.5rem;
  border: 1px solid #D1D5DB;
  border-radius: 6px;
  background: white;
  font-size: 0.875rem;
  cursor: pointer;
  transition: border-color 0.2s ease;
}

.access-select:focus {
  outline: none;
  border-color: #3B82F6;
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

.access-badge.granted {
  background: #3b82f6;
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

/* Адаптивность для мобильных устройств */
@media (max-width: 768px) {
  .share-modal {
    max-width: 95vw;
    margin: 1rem;
  }
  
  .share-content {
    padding: 1rem 1.5rem 1.5rem;
  }
  
  .user-search-section h3,
  .users-with-access-section h3 {
    font-size: 1.125rem;
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