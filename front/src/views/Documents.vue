<template>
  <div class="documents">
    <div class="documents-actions">
      <button class="btn-primary" @click="openCreateModal">
        <i class="fas fa-plus"></i>
        Создать документ
      </button>
      <div class="documents-filters">
        <div class="search-box">
          <i class="fas fa-search"></i>
          <input type="text" v-model="searchQuery" @input="applyFilters" placeholder="Поиск документов...">
        </div>
        <select class="filter-select" v-model="typeFilter" @change="applyFilters">
          <option value="">Тип документа</option>
          <option value="Договор">Договоры</option>
          <option value="Счет">Счета</option>
          <option value="Отчет">Отчеты</option>
        </select>
        <select class="filter-select" v-model="statusFilter" @change="applyFilters">
          <option value="">Статус</option>
          <option value="draft">Черновик</option>
          <option value="review">На рассмотрении</option>
          <option value="approved">Утверждено</option>
        </select>
      </div>
    </div>

    <div class="documents-grid">
      <div v-for="doc in documents" :key="doc.id" class="document-card">
        <div class="document-icon">
          <i class="fas fa-file-alt"></i>
        </div>
        <div class="document-info">
          <h3>{{ doc.name }}</h3>
          <p class="document-type">{{ doc.type }}</p>
          <span :class="'status-badge ' + doc.status">{{ doc.status }}</span>
        </div>
        <div class="document-meta">
          <span class="document-date">{{ doc.created }}</span>
          <div class="document-actions">
            <button class="btn-icon" title="Просмотр">
              <i class="fas fa-eye"></i>
            </button>
            <button class="btn-icon" title="Редактировать" @click="editDocument(doc)">
              <i class="fas fa-edit"></i>
            </button>
            <button class="btn-icon" title="Удалить" @click="deleteDocument(doc.id)">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Модальное окно для создания/редактирования документа -->
    <div v-if="showModal" class="modal">
      <div class="modal-content">
        <h2>{{ editingDocument ? 'Редактировать документ' : 'Создать документ' }}</h2>
        <form @submit.prevent="saveDocument">
          <div class="form-group">
            <label for="name">Название</label>
            <input type="text" id="name" v-model="newDocument.name" required>
          </div>
          
          <div class="form-group">
            <label for="type">Тип документа</label>
            <select id="type" v-model="newDocument.type" required>
              <option value="">Выберите тип</option>
              <option value="Договор">Договор</option>
              <option value="Счет">Счет</option>
              <option value="Отчет">Отчет</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="status">Статус</label>
            <select id="status" v-model="newDocument.status">
              <option value="draft">Черновик</option>
              <option value="review">На рассмотрении</option>
              <option value="approved">Утверждено</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="created">Дата создания</label>
            <input type="date" id="created" v-model="newDocument.created" required>
          </div>
          
          <div class="form-group">
            <label for="file">Файл документа (только DOCX)</label>
            <div class="file-upload-container">
              <input type="file" id="file" @change="handleFileUpload" accept=".docx" hidden>
              <label for="file" class="btn-upload">
                <i class="fas fa-file-upload"></i> Загрузить DOCX
              </label>
              <small v-if="newDocument.file" class="file-name">{{ getFileName(newDocument.file) }}</small>
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="showModal = false" class="btn-cancel">Отмена</button>
            <button type="submit" class="btn-primary">Сохранить</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { DocumentService } from '../api/services';
import mammoth from 'mammoth';

export default {
  name: 'DocumentsView',
  data() {
    return {
      documents: [],
      newDocument: {
        name: '',
        type: '',
        status: 'draft',
        created: '',
        file: null
      },
      editingDocument: null,
      showModal: false,
      searchQuery: '',
      typeFilter: '',
      statusFilter: ''
    }
  },
  mounted() {
    this.fetchDocuments();
  },
  methods: {
    async fetchDocuments() {
      try {
        // Используем сервис для получения документов
        this.documents = await DocumentService.getAll({
          search: this.searchQuery,
          type: this.typeFilter,
          status: this.statusFilter
        });
      } catch (error) {
        console.error('Ошибка при получении документов:', error);
        // Обработка ошибок уже реализована в сервисе
      }
    },
    
    openCreateModal() {
      this.editingDocument = null;
      const today = new Date();
      const formattedDate = today.toISOString().split('T')[0]; // YYYY-MM-DD формат
      
      this.newDocument = {
        name: '',
        type: '',
        status: 'draft',
        created: formattedDate,
        file: null
      };
      this.showModal = true;
    },
    
    openEditModal(document) {
      this.editingDocument = document.id;
      this.newDocument = {...document, file: null};
      this.showModal = true;
    },
    
    async saveDocument() {
      try {
        // Создаем FormData для отправки файла
        const formData = new FormData();
        formData.append('name', this.newDocument.name);
        formData.append('type', this.newDocument.type);
        formData.append('status', this.newDocument.status);
        formData.append('created', this.newDocument.created);
        
        // Добавляем файл, если он был выбран
        if (this.newDocument.file) {
          formData.append('file', this.newDocument.file);
        }
        
        // Добавляем содержимое документа, если оно было сконвертировано из DOCX
        if (this.newDocument.content) {
          formData.append('content', this.newDocument.content);
        }
        
        // Добавляем тип файла, если он был определен
        if (this.newDocument.file_type) {
          formData.append('file_type', this.newDocument.file_type);
        }
        
        
        if (this.editingDocument) {
          // Обновление существующего документа
          await DocumentService.updateWithFile(this.editingDocument, formData);
        } else {
          // Создание нового документа
          await DocumentService.createWithFile(formData);
        }
        this.fetchDocuments();
        this.showModal = false;
      } catch (error) {
        console.error('Ошибка при сохранении документа:', error);
        // Обработка ошибок уже реализована в сервисе
      }
    },
    
    async deleteDocument(id) {
      if (confirm('Вы уверены, что хотите удалить этот документ?')) {
        try {
          // Используем сервис для удаления документа
          await DocumentService.delete(id);
          this.fetchDocuments();
        } catch (error) {
          console.error('Ошибка при удалении документа:', error);
          // Обработка ошибок уже реализована в сервисе
        }
      }
    },


    applyFilters() {
      // Используем сервис для получения документов с фильтрами
      this.fetchDocuments();
      
      // Определяем переменные для фильтрации
      let params = [];
      let url = '/api/documents?';
      
      if (this.typeFilter) {
        params.push(`type=${encodeURIComponent(this.typeFilter)}`);
      }
      
      if (this.statusFilter) {
        params.push(`status=${encodeURIComponent(this.statusFilter)}`);
      }
      
      url += params.join('&');
      
      axios.get(url)
        .then(response => {
          this.documents = response.data;
        })
        .catch(error => {
          console.error('Ошибка при фильтрации документов:', error);
        });
    },
    
    // Обработка загрузки файла
    handleFileUpload(event) {
      const file = event.target.files[0];
      if (!file) return;
      
      // Проверяем тип файла
      const fileType = file.name.split('.').pop().toLowerCase();
      if (fileType === 'docx') {
        this.newDocument.file = file;
        
        // Всегда предлагаем конвертировать DOCX файл в HTML
        if (confirm('Хотите конвертировать DOCX файл в HTML для редактирования в редакторе?')) {
          this.convertDocxToHtml(file);
        }
      } else {
        alert('Пожалуйста, выберите файл формата DOCX');
        event.target.value = ''; // Сбрасываем выбор файла
      }
    },
    
    // Конвертация DOCX в HTML с помощью mammoth.js
    async convertDocxToHtml(file) {
      try {
        // Показываем индикатор загрузки или сообщение
        this.isLoading = true;
        
        // Читаем файл как ArrayBuffer
        const arrayBuffer = await this.readFileAsArrayBuffer(file);
        
        // Конвертируем DOCX в HTML с помощью mammoth.js
        const result = await mammoth.convertToHtml({ arrayBuffer });
        const html = result.value;
        
        // Сохраняем HTML для отправки на сервер
        this.newDocument.content = html;
        this.newDocument.file_type = 'docx';
        this.isLoading = false;
        
        // Показываем сообщение об успешной загрузке
        alert('Файл DOCX успешно загружен и конвертирован в HTML');
      } catch (error) {
        console.error('Ошибка при конвертации DOCX файла:', error);
        alert('Ошибка при конвертации DOCX файла');
        this.isLoading = false;
      }
    },
    
    // Вспомогательный метод для чтения файла как ArrayBuffer
    readFileAsArrayBuffer(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsArrayBuffer(file);
      });
    },
    
    // Получение имени файла для отображения
    getFileName(file) {
      return file ? file.name : '';
    },
    
    // Переход на страницу редактирования документа
    editDocument(doc) {
      this.$router.push({ name: 'DocumentEdit', params: { id: doc.id } });
    }
  }
}
</script>


<style src="@/assets/documents.css"></style>