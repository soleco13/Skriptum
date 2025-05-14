<template>
  <div class="processes">
    <!-- Заголовок с инструментами управления -->
    <div class="processes-header">
      <div class="header-title">
        <h1>Управление процессами</h1>
        <span class="process-counter" v-if="!showBpmnEditor">{{ filteredProcesses.length }} процессов</span>
        <span class="process-counter" v-else>{{ currentDiagramName || 'Редактор процессов' }}</span>
      </div>
      
      <div class="header-actions">
        <!-- Поиск и фильтры отображаются только в режиме списка -->
        <template v-if="!showBpmnEditor">
          <div class="search-container">
            <i class="fas fa-search search-icon"></i>
            <input 
              type="text" 
              v-model="searchQuery" 
              placeholder="Поиск процессов..." 
              class="search-input"
            />
            <button class="clear-search" v-if="searchQuery" @click="searchQuery = ''">
              <i class="fas fa-times"></i>
            </button>
          </div>
          
          <div class="filter-container">
            <button class="filter-button" @click="toggleFilterDropdown">
              <i class="fas fa-filter"></i>
              <span>Фильтр</span>
              <i class="fas fa-chevron-down"></i>
            </button>
            
            <div class="filter-dropdown" v-if="showFilterDropdown">
              <div class="filter-option">
                <label>Статус</label>
                <div class="checkbox-group">
                  <label class="checkbox-label">
                    <input type="checkbox" v-model="filters.active"> 
                    <span class="checkbox-text">Активные</span>
                  </label>
                  <label class="checkbox-label">
                    <input type="checkbox" v-model="filters.pending">
                    <span class="checkbox-text">Ожидающие</span>
                  </label>
                  <label class="checkbox-label">
                    <input type="checkbox" v-model="filters.completed">
                    <span class="checkbox-text">Завершенные</span>
                  </label>
                </div>
              </div>
              
              <div class="filter-option">
                <label>Прогресс</label>
                <div class="range-slider">
                  <input 
                    type="range" 
                    min="0" 
                    max="100" 
                    v-model="filters.progressMin" 
                    class="range-input"
                  >
                  <div class="range-values">
                    <span>{{ filters.progressMin }}%</span>
                    <span>100%</span>
                  </div>
                </div>
              </div>
              
              <div class="filter-actions">
                <button class="btn-text" @click="resetFilters">Сбросить</button>
                <button class="btn-primary" @click="showFilterDropdown = false">Применить</button>
              </div>
            </div>
          </div>
          
          <div class="view-toggle">
            <button 
              class="view-button" 
              :class="{ active: viewMode === 'grid' }" 
              @click="viewMode = 'grid'"
            >
              <i class="fas fa-th-large"></i>
            </button>
            <button 
              class="view-button" 
              :class="{ active: viewMode === 'list' }" 
              @click="viewMode = 'list'"
            >
              <i class="fas fa-list"></i>
            </button>
          </div>
          
          <button class="btn-primary create-btn" @click="openCreateModal">
            <i class="fas fa-plus"></i>
            <span>Создать процесс</span>
          </button>
          
          <!-- Кнопка для открытия редактора BPMN -->
          <button class="btn-primary bpmn-btn" @click="openBpmnEditor()">
            <i class="fas fa-project-diagram"></i>
            <span>Редактор процессов</span>
          </button>
        </template>
        
        <!-- Кнопки для режима редактора BPMN -->
        <template v-else>
          <button class="btn-secondary" @click="closeBpmnEditor">
            <i class="fas fa-arrow-left"></i>
            <span>Вернуться к списку</span>
          </button>
        </template>
      </div>
    </div>

    <!-- Основное содержимое страницы -->
    <div class="processes-content"> </div>
      <!-- Редактор BPMN-диаграмм -->
      <div v-if="showBpmnEditor" class="bpmn-editor-wrapper">
        <bpmn-editor 
          ref="bpmnEditor"
          :diagram-id="currentDiagramId"
          :initial-xml="currentDiagramXml"
          @saved="handleDiagramSaved"
          @diagram-created="handleDiagramCreated"
          @error="handleBpmnError"
        />
      </div>
      
      <!-- Список процессов -->
      <div v-else>
        <!-- Индикатор загрузки -->
        <div class="loader-container" v-if="loading">
          <div class="loader"></div>
          <p>Загрузка процессов...</p>
        </div>

        <!-- Пустое состояние -->
        <div class="empty-state" v-else-if="filteredProcesses.length === 0">
          <div class="empty-illustration">
            <i class="fas fa-tasks"></i>
          </div>
          <h3>Процессы не найдены</h3>
          <p v-if="searchQuery || isFiltered">Попробуйте изменить параметры поиска или фильтрации</p>
          <p v-else>Создайте свой первый процесс, чтобы начать работу</p>
          <button class="btn-primary" @click="openCreateModal">
            <i class="fas fa-plus"></i>
            Создать процесс
          </button>
        </div>

        <!-- Сетка процессов -->
        <transition-group 
          name="process-list" 
          tag="div" 
          :class="viewMode === 'grid' ? 'processes-grid' : 'processes-list'"
        >
      <div 
        v-for="process in filteredProcesses" 
        :key="process.id" 
        class="process-card"
        :class="[viewMode === 'list' ? 'list-view' : '', process.status]"
      >
        <div class="process-header">
          <div class="process-title">
            <h3>{{ process.name }}</h3>
            <div class="process-badge" :class="process.status">
              <i :class="getStatusIcon(process.status)"></i>
              <span>{{ getStatusText(process.status) }}</span>
            </div>
          </div>
          <div class="process-menu">
            <button class="btn-icon menu-trigger" @click="toggleCardMenu(process.id)">
              <i class="fas fa-ellipsis-v"></i>
            </button>
            <div class="card-menu" v-if="activeMenu === process.id">
              <button class="menu-item" @click="openEditModal(process)">
                <i class="fas fa-edit"></i> Редактировать
              </button>
              <button class="menu-item" @click="openBpmnEditor(process.id)">
                <i class="fas fa-project-diagram"></i> Редактировать диаграмму
              </button>
              <button class="menu-item" @click="duplicateProcess(process)">
                <i class="fas fa-copy"></i> Дублировать
              </button>
              <button class="menu-item danger" @click="confirmDelete(process.id)">
                <i class="fas fa-trash"></i> Удалить
              </button>
            </div>
          </div>
        </div>
        
        <div class="process-info">
          <div class="process-progress">
            <div class="progress-label">
              <span>Прогресс</span>
              <span class="progress-text">{{ process.progress }}%</span>
            </div>
            <div class="progress-bar">
              <div 
                class="progress" 
                :style="{ width: process.progress + '%' }"
                :class="{ 
                  'low': process.progress < 30, 
                  'medium': process.progress >= 30 && process.progress < 70,
                  'high': process.progress >= 70 
                }"
              ></div>
            </div>
          </div>
          
          <div class="process-meta">
            <div class="meta-item" :title="`${process.participants} участников`">
              <i class="fas fa-users"></i>
              <span>{{ process.participants }}</span>
            </div>
            
            <div class="meta-item deadline" :class="getDeadlineStatus(process.deadline)">
              <i class="fas fa-calendar-alt"></i>
              <span>{{ formatDeadline(process.deadline) }}</span>
            </div>
          </div>
        </div>
        
        <div class="process-actions">
          <button class="btn-secondary" @click="viewProcessDetails(process.id)">
            <i class="fas fa-eye"></i>
            <span>Детали</span>
          </button>
          <button class="action-button" @click="toggleStatus(process)">
            {{ process.status === 'completed' ? 'Возобновить' : 'Завершить' }}
          </button>
        </div>
      </div>
    </transition-group>
    
    <!-- Подтверждение удаления -->
    <div class="confirm-dialog" v-if="showDeleteConfirm">
      <div class="confirm-content">
        <div class="confirm-icon">
          <i class="fas fa-exclamation-triangle"></i>
        </div>
        <h3>Удаление процесса</h3>
        <p>Вы уверены, что хотите удалить этот процесс? Это действие нельзя отменить.</p>
        <div class="confirm-actions">
          <button class="btn-text" @click="showDeleteConfirm = false">Отмена</button>
          <button class="btn-danger" @click="deleteProcess()">Удалить</button>
        </div>
      </div>
    </div>
    
    <!-- Модальное окно для создания/редактирования -->
    <transition name="modal">
      <div v-if="showModal" class="modal" @click.self="closeModal">
        <div class="modal-content">
          <button class="modal-close" @click="closeModal">
            <i class="fas fa-times"></i>
          </button>
          
          <div class="modal-header">
            <h2>{{ editingProcess ? 'Редактировать процесс' : 'Создать процесс' }}</h2>
            <p class="modal-subtitle">{{ editingProcess ? 'Измените информацию о существующем процессе' : 'Заполните информацию о новом процессе' }}</p>
          </div>
          
          <form @submit.prevent="saveProcess" class="process-form">
            <div class="form-group">
              <label for="name">Название процесса</label>
              <input 
                type="text" 
                id="name" 
                v-model="newProcess.name" 
                required
                placeholder="Введите название процесса"
                :class="{ 'input-error': formErrors.name }"
              >
              <span class="error-message" v-if="formErrors.name">{{ formErrors.name }}</span>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label for="status">Статус</label>
                <div class="select-wrapper">
                  <select id="status" v-model="newProcess.status">
                    <option value="active">Активный</option>
                    <option value="pending">В ожидании</option>
                    <option value="completed">Завершен</option>
                  </select>
                  <i class="fas fa-chevron-down select-icon"></i>
                </div>
              </div>
              
              <div class="form-group">
                <label for="progress">Прогресс</label>
                <div class="progress-input-wrapper">
                  <input 
                    type="range" 
                    id="progress-slider" 
                    v-model.number="newProcess.progress" 
                    min="0" 
                    max="100"
                    step="5"
                    style="--value: 50"
                    @input="updateProgressStyle"
                  >
                  <div class="progress-value">
                    <input 
                      type="number" 
                      id="progress" 
                      v-model.number="newProcess.progress" 
                      min="0" 
                      max="100"
                      @input="updateProgressStyle"
                    >
                    <span class="unit">%</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label for="participants">Участники</label>
                <div class="number-input-wrapper">
                  <button 
                    type="button" 
                    class="number-btn" 
                    @click="adjustParticipants(-1)"
                    :disabled="newProcess.participants <= 0"
                  >
                    <i class="fas fa-minus"></i>
                  </button>
                  <input 
                    type="number" 
                    id="participants" 
                    v-model.number="newProcess.participants" 
                    min="0"
                    placeholder="0"
                  >
                  <button 
                    type="button" 
                    class="number-btn" 
                    @click="adjustParticipants(1)"
                  >
                    <i class="fas fa-plus"></i>
                  </button>
                </div>
              </div>
              
              <div class="form-group">
                <label for="deadline">Срок выполнения</label>
                <div class="date-input-wrapper">
                  <input 
                    type="date" 
                    id="deadline" 
                    v-model="newProcess.deadline"
                    :min="getCurrentDate()"
                    :class="{ 'input-error': formErrors.deadline }"
                  >
                  <i class="fas fa-calendar-alt date-icon"></i>
                </div>
                <span class="error-message" v-if="formErrors.deadline">{{ formErrors.deadline }}</span>
              </div>
            </div>
            
            <div class="form-group description-group">
              <label for="description">Описание</label>
              <textarea 
                id="description" 
                v-model="newProcess.description" 
                rows="4"
                placeholder="Опишите подробности процесса"
              ></textarea>
            </div>
            
            <div class="form-actions">
              <button type="button" @click="closeModal" class="btn-text">Отмена</button>
              <button 
                type="submit" 
                class="btn-primary"
                :disabled="isSaving"
              >
                <span v-if="isSaving">
                  <i class="fas fa-spinner fa-spin"></i>
                  Сохранение...
                </span>
                <span v-else>Сохранить</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </transition>
  </div>
</div>
</template>

<script>
import { ProcessService } from '../api/services';
import { BpmnService } from '../api/bpmn-service';
import BpmnEditor from '../components/BpmnEditor.vue';

export default {
  name: 'ProcessesView',
  components: {
    BpmnEditor
  },
  data() {
    return {
      processes: [],
      loading: true,
      isSaving: false,
      searchQuery: '',
      viewMode: 'grid',
      showFilterDropdown: false,
      filters: {
        active: true,
        pending: true,
        completed: true,
        progressMin: 0
      },
      newProcess: {
        name: '',
        status: 'pending',
        progress: 0,
        participants: 0,
        deadline: '',
        description: ''
      },
      formErrors: {
        name: '',
        deadline: ''
      },
      editingProcess: null,
      showModal: false,
      activeMenu: null,
      showDeleteConfirm: false,
      processToDelete: null,
      // Данные для BPMN-редактора
      showBpmnEditor: false,
      currentDiagramId: null,
      currentDiagramXml: null,
      currentDiagramName: ''
    }
  },
  computed: {
    filteredProcesses() {
      return this.processes.filter(process => {
        // Фильтр по поиску
        const matchesSearch = process.name.toLowerCase().includes(this.searchQuery.toLowerCase());
        
        // Фильтр по статусу
        const matchesStatus = 
          (process.status === 'active' && this.filters.active) ||
          (process.status === 'pending' && this.filters.pending) ||
          (process.status === 'completed' && this.filters.completed);
        
        // Фильтр по прогрессу
        const matchesProgress = process.progress >= this.filters.progressMin;
        
        return matchesSearch && matchesStatus && matchesProgress;
      });
    },
    isFiltered() {
      return !this.filters.active || !this.filters.pending || !this.filters.completed || this.filters.progressMin > 0;
    }
  },
  mounted() {
    this.fetchProcesses();
    // Регистрируем сервис BPMN в глобальном контексте компонента
    this.$bpmnService = BpmnService;
  },
  methods: {
    fetchProcesses() {
      this.loading = true;
      ProcessService.getAll()
        .then(data => {
          this.processes = data;
          // Добавляем небольшую задержку, чтобы показать анимацию загрузки
          setTimeout(() => {
            this.loading = false;
          }, 500);
        });
    },
    
    openCreateModal() {
      this.editingProcess = null;
      this.newProcess = {
        name: '',
        status: 'pending',
        progress: 0,
        participants: 0,
        deadline: this.getCurrentDate(),
        description: ''
      };
      this.formErrors = { name: '', deadline: '' };
      this.showModal = true;
      this.updateProgressStyle();
      
      // Закрыть выпадающее меню фильтров, если открыто
      this.showFilterDropdown = false;
    },
    
    openEditModal(process) {
      this.editingProcess = process.id;
      this.newProcess = {...process};
      this.formErrors = { name: '', deadline: '' };
      this.showModal = true;
      this.updateProgressStyle();
      this.activeMenu = null;
    },
    
    closeModal() {
      this.showModal = false;
    },
    
    validateForm() {
      let isValid = true;
      this.formErrors = { name: '', deadline: '' };
      
      if (!this.newProcess.name.trim()) {
        this.formErrors.name = 'Название процесса обязательно';
        isValid = false;
      }
      
      if (this.newProcess.deadline && new Date(this.newProcess.deadline) < new Date() && this.newProcess.status !== 'completed') {
        this.formErrors.deadline = 'Срок не может быть в прошлом';
        isValid = false;
      }
      
      return isValid;
    },
    
    saveProcess() {
      if (!this.validateForm()) return;
      
      this.isSaving = true;
      
      if (this.editingProcess) {
        // Обновление существующего процесса
        ProcessService.update(this.editingProcess, this.newProcess)
          .then(() => {
            this.fetchProcesses();
            setTimeout(() => {
              this.showModal = false;
              this.isSaving = false;
              this.showToast('Процесс успешно обновлен');
            }, 600);
          })
          .catch(error => {
            console.error('Ошибка при обновлении процесса:', error);
            this.isSaving = false;
            this.showToast('Ошибка при обновлении процесса', 'error');
          });
      } else {
        // Создание нового процесса
        ProcessService.create(this.newProcess)
          .then(() => {
            this.fetchProcesses();
            setTimeout(() => {
              this.showModal = false;
              this.isSaving = false;
              this.showToast('Процесс успешно создан');
            }, 600);
          })
          .catch(error => {
            console.error('Ошибка при создании процесса:', error);
            this.isSaving = false;
            this.showToast('Ошибка при создании процесса', 'error');
          });
      }
    },
    
    confirmDelete(processId) {
      this.processToDelete = processId;
      this.showDeleteConfirm = true;
      this.activeMenu = null;
    },
    
    deleteProcess() {
      if (!this.processToDelete) return;
      
      ProcessService.delete(this.processToDelete)
        .then(() => {
          this.fetchProcesses();
          this.showDeleteConfirm = false;
          this.processToDelete = null;
          this.showToast('Процесс успешно удален');
        })
        .catch(error => {
          console.error('Ошибка при удалении процесса:', error);
          this.showToast('Ошибка при удалении процесса', 'error');
        });
    },
    
    duplicateProcess(process) {
      const newProcess = {...process};
      delete newProcess.id;
      newProcess.name = `Копия ${newProcess.name}`;
      
      ProcessService.create(newProcess)
        .then(() => {
          this.fetchProcesses();
          this.activeMenu = null;
          this.showToast('Процесс успешно дублирован');
        })
        .catch(error => {
          console.error('Ошибка при дублировании процесса:', error);
          this.showToast('Ошибка при дублировании процесса', 'error');
        });
    },
    
    toggleStatus(process) {
      const updatedProcess = {...process};
      
      if (process.status === 'completed') {
        updatedProcess.status = 'active';
      } else {
        updatedProcess.status = 'completed';
        updatedProcess.progress = 100;
      }
      
      ProcessService.update(process.id, updatedProcess)
        .then(() => {
          this.fetchProcesses();
          this.showToast(`Процесс ${updatedProcess.status === 'completed' ? 'завершен' : 'возобновлен'}`);
        })
        .catch(error => {
          console.error('Ошибка при изменении статуса процесса:', error);
          this.showToast('Ошибка при изменении статуса', 'error');
        });
    },
    
    viewProcessDetails(id) {
      // В реальном приложении здесь был бы переход к детальной странице процесса
      this.showToast('Просмотр деталей процесса #' + id);
    },
    
    toggleFilterDropdown() {
      this.showFilterDropdown = !this.showFilterDropdown;
      this.activeMenu = null;
    },
    
    resetFilters() {
      this.filters = {
        active: true,
        pending: true,
        completed: true,
        progressMin: 0
      };
      this.searchQuery = '';
    },
    
    toggleCardMenu(processId) {
      if (this.activeMenu === processId) {
        this.activeMenu = null;
      } else {
        this.activeMenu = processId;
      }
      
      // Закрыть выпадающее меню фильтров, если открыто
      this.showFilterDropdown = false;
    },
    
    updateProgressStyle() {
      const sliderEl = document.getElementById('progress-slider');
      if (sliderEl) {
        sliderEl.style.setProperty('--value', this.newProcess.progress);
      }
    },
    
    adjustParticipants(change) {
      const newValue = this.newProcess.participants + change;
      if (newValue >= 0) {
        this.newProcess.participants = newValue;
      }
    },
    
    getCurrentDate() {
      const today = new Date();
      const year = today.getFullYear();
      const month = String(today.getMonth() + 1).padStart(2, '0');
      const day = String(today.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    },
    
    formatDeadline(date) {
      if (!date) return '—';
      
      const deadlineDate = new Date(date);
      const today = new Date();
      
      // Сбросить время для корректного сравнения дат
      today.setHours(0, 0, 0, 0);
      deadlineDate.setHours(0, 0, 0, 0);
      
      const diffTime = deadlineDate - today;
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      if (diffDays < 0) {
        return `Просрочено (${Math.abs(diffDays)} дн.)`;
      } else if (diffDays === 0) {
        return 'Сегодня';
      } else if (diffDays === 1) {
        return 'Завтра';
      } else if (diffDays <= 7) {
        return `${diffDays} дн.`;
      } else {
        const options = { day: 'numeric', month: 'short' };
        return deadlineDate.toLocaleDateString('ru-RU', options);
      }
    },
    
    getDeadlineStatus(date) {
      if (!date) return '';
      
      const deadlineDate = new Date(date);
      const today = new Date();
      
      // Сбросить время для корректного сравнения дат
      today.setHours(0, 0, 0, 0);
      deadlineDate.setHours(0, 0, 0, 0);
      
      const diffTime = deadlineDate - today;
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      if (diffDays < 0) {
        return 'overdue';
      } else if (diffDays <= 3) {
        return 'urgent';
      } else {
        return '';
      }
    },
    
    getStatusIcon(status) {
      switch(status) {
        case 'active':
          return 'fas fa-play-circle';
        case 'pending':
          return 'fas fa-pause-circle';
        case 'completed':
          return 'fas fa-check-circle';
        default:
          return 'fas fa-circle';
      }
    },
    
    getStatusText(status) {
      switch(status) {
        case 'active':
          return 'Активен';
        case 'pending':
          return 'Ожидание';
        case 'completed':
          return 'Завершен';
        default:
          return status;
      }
    },
    
    // Методы для работы с BPMN-редактором
    async openBpmnEditor(processId = null) {
      this.showBpmnEditor = true;
      this.currentDiagramId = processId;
      this.currentDiagramXml = null;
      this.currentDiagramName = '';
      
      if (processId) {
        try {
          // Загружаем диаграмму процесса, если указан ID
          const diagram = await BpmnService.getDiagram(processId);
          if (diagram) {
            this.currentDiagramXml = diagram.xml;
            this.currentDiagramName = diagram.name || `Процесс #${processId}`;
          }
        } catch (error) {
          console.error('Ошибка при загрузке диаграммы:', error);
          this.showToast('Не удалось загрузить диаграмму процесса', 'error');
        }
      }
    },
    
    closeBpmnEditor() {
      // Проверяем, есть ли несохраненные изменения
      if (this.$refs.bpmnEditor && this.$refs.bpmnEditor.isModified) {
        if (!confirm('У вас есть несохраненные изменения. Вы уверены, что хотите закрыть редактор?')) {
          return;
        }
      }
      
      this.showBpmnEditor = false;
      this.currentDiagramId = null;
      this.currentDiagramXml = null;
      this.currentDiagramName = '';
    },
    
    handleDiagramSaved(response) {
      if (response) {
        this.currentDiagramName = response.name || this.currentDiagramName;
        this.showToast('Диаграмма успешно сохранена');
        
        // Обновляем список процессов, если диаграмма связана с процессом
        if (this.currentDiagramId) {
          this.fetchProcesses();
        }
      }
    },
    
    handleDiagramCreated(diagramId) {
      if (diagramId) {
        this.currentDiagramId = diagramId;
        this.showToast('Создана новая диаграмма процесса');
      }
    },
    
    handleBpmnError(message) {
      this.showToast(message, 'error');
    },
    
    showToast(message, type = 'success') {
      // Простое уведомление (можно заменить на более красивое)
      alert(`${type.toUpperCase()}: ${message}`);
    }
  }
}
</script>

<style src="@/assets/processes.css"></style>