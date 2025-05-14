<template>
  <div class="document-edit">
    <div class="document-edit-header">
      <h1>{{ document.name }}</h1>
      <div class="document-actions">
        <button class="btn-primary" @click="saveDocument">
          <i class="fas fa-save"></i> Сохранить
        </button>
        <button class="btn-secondary" @click="togglePreview">
          <i class="fas" :class="showPreview ? 'fa-edit' : 'fa-eye'"></i> {{ showPreview ? 'Режим редактирования' : 'Режим предпросмотра' }}
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
      <div class="document-content">
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
          <div v-if="!showPreview" class="editor-container full-width">
            <ckeditor 
              ref="ckeditor" 
              :editor="editor" 
              v-model="document.content" 
              :config="editorConfig"
              @ready="onEditorReady"
              @change="updatePreview"
            ></ckeditor>
          </div>
          
          <!-- Предпросмотр документа -->
          <div v-else class="preview-container full-width">
            <div class="preview-header">
              <h3>Предпросмотр</h3>
            </div>
            <div class="preview-content" v-html="document.content"></div>
          </div>
        </div>
      </div>
      
      <!-- Панель истории документа -->
      <div class="document-history-panel">
        <div class="history-header">
          <h3>История изменений</h3>
          <button class="btn-refresh" @click="fetchDocumentHistory" title="Обновить историю">
            <i class="fas fa-sync-alt"></i>
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
  </div>
</template>

<script>
import { DocumentService } from '../api/services';
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
      versionName: ''
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
  }
};
</script>

<style>
.document-edit {
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.document-edit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e0e0e0;
}

.document-actions {
  display: flex;
  gap: 10px;
}

.btn-upload {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 8px 16px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.btn-upload:hover {
  background-color: #388e3c;
}

.document-info {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  padding: 15px;
  background-color: #fff;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.info-item {
  display: flex;
  flex-direction: column;
}

.label {
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.value {
  font-weight: 500;
}

.status-badge {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.draft {
  background-color: #e0e0e0;
  color: #616161;
}

.status-badge.review {
  background-color: #bbdefb;
  color: #1976d2;
}

.status-badge.approved {
  background-color: #c8e6c9;
  color: #388e3c;
}

.document-edit-container {
  display: flex;
  gap: 20px;
  margin-top: 20px;
}

.document-content {
  flex: 1;
}

.pdf-viewer {
  margin-bottom: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.doc-info {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #e3f2fd;
  border-radius: 4px;
  color: #0d47a1;
}

.btn-link {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  color: #1976d2;
  text-decoration: none;
  margin-top: 10px;
}

.btn-link:hover {
  text-decoration: underline;
}

.editor-preview-container {
  width: 100%;
}

.editor-container {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.editor-container.full-width,
.preview-container.full-width {
  width: 100%;
}

.preview-container {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background-color: #fff;
}

.preview-header {
  padding: 10px 15px;
  background-color: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.preview-content {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
  min-height: 400px;
  max-height: 600px;
}

/* Стили для CKEditor */
.ck-editor__editable {
  min-height: 400px;
  max-height: 600px;
}

/* Стили для панели истории */
.document-history-panel {
  width: 300px;
  background-color: #f5f5f5;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 15px;
  display: flex;
  flex-direction: column;
  max-height: 600px;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e0e0e0;
}

.history-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
}

.btn-refresh {
  background: none;
  border: none;
  color: #1976d2;
  cursor: pointer;
  font-size: 14px;
}

.btn-refresh:hover {
  color: #0d47a1;
}

.history-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px 0;
  color: #757575;
  font-size: 14px;
}

.history-loading i {
  margin-right: 8px;
}

.history-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px 0;
  color: #9e9e9e;
  text-align: center;
}

.history-empty i {
  font-size: 24px;
  margin-bottom: 10px;
}

.history-list {
  list-style: none;
  padding: 0;
  margin: 0;
  overflow-y: auto;
  flex: 1;
}

.history-item {
  background-color: #fff;
  border-radius: 4px;
  margin-bottom: 10px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  transition: all 0.2s ease;
}

.history-item.active {
  box-shadow: 0 2px 8px rgba(25, 118, 210, 0.2);
  border-left: 3px solid #1976d2;
}

.history-item-header {
  padding: 12px 15px;
  cursor: pointer;
}

.history-item-title {
  display: flex;
  flex-direction: column;
  margin-bottom: 5px;
}

.version-name {
  font-weight: 500;
  font-size: 14px;
  color: #333;
  margin-bottom: 3px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.version-date {
  font-size: 12px;
  color: #757575;
}

.history-item-user {
  font-size: 12px;
  color: #616161;
}

.history-item-actions {
  padding: 10px 15px;
  background-color: #f9f9f9;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
}

.btn-restore {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 6px 12px;
  background-color: #1976d2;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-restore:hover {
  background-color: #0d47a1;
}

.version-name-input {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: white;
  padding: 15px;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  z-index: 10;
  border-top: 1px solid #e0e0e0;
}

.version-name-input label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
}

.version-name-input input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  margin-bottom: 12px;
  font-size: 14px;
}

.version-name-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>