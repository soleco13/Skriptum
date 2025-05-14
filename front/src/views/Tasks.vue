<template>
  <div class="tasks">
    <!-- Заголовок и инструменты управления -->
    <div class="tasks-header">
      <div class="header-left">
        <h1>Управление задачами</h1>
        <div class="task-statistics">
          <div class="stat-badge">
            <span class="count">{{ tasks.length }}</span>
            <span class="label">Всего</span>
          </div>
          <div class="stat-badge">
            <span class="count">{{ pendingCount }}</span>
            <span class="label">Ожидает</span>
          </div>
          <div class="stat-badge">
            <span class="count">{{ inProgressCount }}</span>
            <span class="label">В работе</span>
          </div>
          <div class="stat-badge">
            <span class="count">{{ completedCount }}</span>
            <span class="label">Завершено</span>
          </div>
        </div>
      </div>
      
      <div class="header-actions">
        <div class="search-wrapper">
          <i class="fas fa-search"></i>
          <input 
            type="text" 
            placeholder="Поиск задач..." 
            v-model="searchQuery"
            class="search-input"
          >
          <button 
            v-if="searchQuery" 
            @click="searchQuery = ''" 
            class="clear-search"
          >
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="filter-dropdown">
          <button class="filter-btn" @click="showFilters = !showFilters">
            <i class="fas fa-filter"></i>
            <span>Фильтр</span>
            <i class="fas fa-chevron-down" :class="{ 'rotated': showFilters }"></i>
          </button>
          
          <div class="filter-menu" v-if="showFilters">
            <div class="filter-section">
              <h4>Приоритет</h4>
              <label class="checkbox-label">
                <input type="checkbox" v-model="filters.priority.high">
                <span class="custom-checkbox high"></span>
                <span>Высокий</span>
              </label>
              <label class="checkbox-label">
                <input type="checkbox" v-model="filters.priority.medium">
                <span class="custom-checkbox medium"></span>
                <span>Средний</span>
              </label>
              <label class="checkbox-label">
                <input type="checkbox" v-model="filters.priority.low">
                <span class="custom-checkbox low"></span>
                <span>Низкий</span>
              </label>
            </div>
            
            <div class="filter-section">
              <h4>Статус</h4>
              <label class="checkbox-label">
                <input type="checkbox" v-model="filters.status.pending">
                <span class="custom-checkbox pending"></span>
                <span>В ожидании</span>
              </label>
              <label class="checkbox-label">
                <input type="checkbox" v-model="filters.status['in-progress']">
                <span class="custom-checkbox in-progress"></span>
                <span>В процессе</span>
              </label>
              <label class="checkbox-label">
                <input type="checkbox" v-model="filters.status.completed">
                <span class="custom-checkbox completed"></span>
                <span>Завершено</span>
              </label>
            </div>
            
            <div class="filter-section">
              <h4>Срок</h4>
              <label class="checkbox-label">
                <input type="checkbox" v-model="filters.deadline.overdue">
                <span>Просроченные</span>
              </label>
              <label class="checkbox-label">
                <input type="checkbox" v-model="filters.deadline.today">
                <span>На сегодня</span>
              </label>
              <label class="checkbox-label">
                <input type="checkbox" v-model="filters.deadline.upcoming">
                <span>Предстоящие</span>
              </label>
            </div>
            
            <div class="filter-actions">
              <button class="btn-text" @click="resetFilters">Сбросить</button>
              <button class="btn-primary" @click="showFilters = false">Применить</button>
            </div>
          </div>
        </div>
        
        <div class="view-toggle">
          <button 
            class="view-btn" 
            :class="{ active: viewMode === 'grid' }"
            @click="viewMode = 'grid'"
            title="Вид сеткой"
          >
            <i class="fas fa-th-large"></i>
          </button>
          <button 
            class="view-btn" 
            :class="{ active: viewMode === 'kanban' }"
            @click="viewMode = 'kanban'"
            title="Канбан"
          >
            <i class="fas fa-columns"></i>
          </button>
          <button 
            class="view-btn" 
            :class="{ active: viewMode === 'list' }"
            @click="viewMode = 'list'"
            title="Список"
          >
            <i class="fas fa-list"></i>
          </button>
        </div>
        
        <button class="btn-primary create-task-btn" @click="openCreateModal">
          <i class="fas fa-plus"></i>
          <span>Создать задачу</span>
        </button>
      </div>
    </div>

    <!-- Состояние загрузки -->
    <div class="loader-container" v-if="loading">
      <div class="loader"></div>
      <p>Загрузка задач...</p>
    </div>

    <!-- Пустое состояние -->
    <div class="empty-state" v-else-if="filteredTasks.length === 0">
      <div class="empty-icon">
        <i class="fas fa-clipboard-list"></i>
      </div>
      <h3>Задачи не найдены</h3>
      <p v-if="searchQuery || isFiltered">Попробуйте изменить параметры поиска или фильтрации</p>
      <p v-else>Создайте свою первую задачу для начала работы</p>
      <button class="btn-primary" @click="openCreateModal">
        <i class="fas fa-plus"></i>
        Создать задачу
      </button>
    </div>

    <!-- Представление сеткой -->
    <div class="tasks-grid" v-else-if="viewMode === 'grid'">
      <task-card 
        v-for="task in filteredTasks" 
        :key="task.id" 
        :task="task"
        @edit="openEditModal"
        @delete="confirmDelete"
        @status-change="changeTaskStatus"
      />
    </div>

    <!-- Представление списком -->
    <div class="tasks-list" v-else-if="viewMode === 'list'">
      <div class="list-header">
        <div class="col-title">Задача</div>
        <div class="col-assignee">Исполнитель</div>
        <div class="col-deadline">Срок</div>
        <div class="col-status">Статус</div>
        <div class="col-actions">Действия</div>
      </div>
      <div class="list-body">
        <div 
          class="list-item" 
          v-for="task in filteredTasks" 
          :key="task.id"
          :class="{ 'completed': task.status === 'completed' }"
        >
          <div class="col-title">
            <div class="priority-indicator" :class="task.priority"></div>
            <div class="task-title-desc">
              <h3>{{ task.title }}</h3>
              <p v-if="task.description">{{ truncateText(task.description, 60) }}</p>
            </div>
          </div>
          <div class="col-assignee">
            <div class="assignee-badge" :title="task.assignee || 'Не назначено'">
              <span v-if="task.assignee">{{ getInitials(task.assignee) }}</span>
              <i v-else class="fas fa-user-slash"></i>
            </div>
            <span class="assignee-name">{{ task.assignee || 'Не назначено' }}</span>
          </div>
          <div class="col-deadline">
            <div class="deadline-badge" :class="getDeadlineStatus(task.deadline)">
              <i class="fas fa-calendar-alt"></i>
              <span>{{ formatDeadline(task.deadline) }}</span>
            </div>
          </div>
          <div class="col-status">
            <div class="status-pill" :class="task.status">
              {{ getStatusLabel(task.status) }}
            </div>
          </div>
          <div class="col-actions">
            <div class="action-buttons">
              <button class="btn-icon" @click="openEditModal(task)" title="Редактировать">
                <i class="fas fa-edit"></i>
              </button>
              <button class="btn-icon" @click="confirmDelete(task.id)" title="Удалить">
                <i class="fas fa-trash"></i>
              </button>
              <div class="status-dropdown">
                <button class="btn-icon dropdown-toggle">
                  <i class="fas fa-ellipsis-v"></i>
                </button>
                <div class="status-menu">
                  <button 
                    v-for="status in availableStatuses(task)" 
                    :key="status.value"
                    class="status-option"
                    @click="changeTaskStatus(task, status.value)"
                  >
                    <i :class="status.icon"></i>
                    <span>{{ status.label }}</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Канбан представление -->
<div class="kanban-board" v-else-if="viewMode === 'kanban'">
  
  <!-- В ожидании -->
  <div class="kanban-column">
    <div class="column-header pending">
      <h3>В ожидании</h3>
      <span class="task-count">{{ pendingTasks.length }}</span>
    </div>
    <div class="column-body">
      <div 
        v-if="pendingTasks.length === 0" 
        class="empty-column"
      >
        <p>Нет задач в ожидании</p>
      </div>
      <task-card 
        v-for="task in pendingTasks" 
        :key="task.id" 
        :task="task"
        @edit="openEditModal"
        @delete="confirmDelete"
        @status-change="changeTaskStatus"
        kanban
      />
    </div>
  </div>

  <!-- В процессе -->
  <div class="kanban-column">
    <div class="column-header in-progress">
      <h3>В процессе</h3>
      <span class="task-count">{{ inProgressTasks.length }}</span>
    </div>
    <div class="column-body">
      <div 
        v-if="inProgressTasks.length === 0" 
        class="empty-column"
      >
        <p>Нет задач в процессе</p>
      </div>
      <task-card 
        v-for="task in inProgressTasks" 
        :key="task.id" 
        :task="task"
        @edit="openEditModal"
        @delete="confirmDelete"
        @status-change="changeTaskStatus"
        kanban
      />
    </div>
  </div>

  <!-- Завершено -->
  <div class="kanban-column">
    <div class="column-header completed">
      <h3>Завершено</h3>
      <span class="task-count">{{ completedTasks.length }}</span>
    </div>
    <div class="column-body">
      <div 
        v-if="completedTasks.length === 0" 
        class="empty-column"
      >
        <p>Нет завершенных задач</p>
      </div>
      <task-card 
        v-for="task in completedTasks" 
        :key="task.id" 
        :task="task"
        @edit="openEditModal"
        @delete="confirmDelete"
        @status-change="changeTaskStatus"
        kanban
      />
    </div>
  </div>

</div>

    <!-- Подтверждение удаления -->
    <div class="confirm-dialog" v-if="deleteConfirmation.show">
      <div class="confirm-content">
        <div class="confirm-icon">
          <i class="fas fa-exclamation-triangle"></i>
        </div>
        <h3>Удаление задачи</h3>
        <p>Вы уверены, что хотите удалить эту задачу? Это действие нельзя отменить.</p>
        <div class="confirm-actions">
          <button class="btn-text" @click="cancelDelete">Отмена</button>
          <button class="btn-danger" @click="deleteTask()">Удалить</button>
        </div>
      </div>
    </div>
    
    <!-- Модальное окно для создания/редактирования задачи -->
    <div v-if="showModal" class="modal" @click.self="closeModal">
      <div class="modal-content">
        <button class="close-btn" @click="closeModal">
          <i class="fas fa-times"></i>
        </button>
        
        <div class="modal-header">
          <h2>{{ editingTask ? 'Редактировать задачу' : 'Создать задачу' }}</h2>
          <p class="modal-subtitle">{{ editingTask ? 'Измените информацию о задаче' : 'Заполните информацию о новой задаче' }}</p>
        </div>
        
        <form @submit.prevent="saveTask" class="task-form">
          <div class="form-group">
            <label for="title">Название задачи</label>
            <input 
              type="text" 
              id="title" 
              v-model="newTask.title" 
              required
              placeholder="Введите название задачи"
              :class="{ 'error': formErrors.title }"
            >
            <span class="error-message" v-if="formErrors.title">{{ formErrors.title }}</span>
          </div>
          
          <div class="form-group">
            <label for="description">Описание</label>
            <textarea 
              id="description" 
              v-model="newTask.description" 
              rows="3"
              placeholder="Опишите задачу подробнее"
            ></textarea>
          </div>
          
          <div class="form-grid">
            <div class="form-group">
              <label for="priority">Приоритет</label>
              <div class="priority-selector">
                <button 
                  type="button"
                  class="priority-option" 
                  :class="{ active: newTask.priority === 'low' }"
                  @click="newTask.priority = 'low'"
                >
                  <span class="priority-color low"></span>
                  <span>Низкий</span>
                </button>
                <button 
                  type="button"
                  class="priority-option" 
                  :class="{ active: newTask.priority === 'medium' }"
                  @click="newTask.priority = 'medium'"
                >
                  <span class="priority-color medium"></span>
                  <span>Средний</span>
                </button>
                <button 
                  type="button"
                  class="priority-option" 
                  :class="{ active: newTask.priority === 'high' }"
                  @click="newTask.priority = 'high'"
                >
                  <span class="priority-color high"></span>
                  <span>Высокий</span>
                </button>
              </div>
            </div>
            
            <div class="form-group">
              <label for="status">Статус</label>
              <div class="custom-select">
                <select id="status" v-model="newTask.status">
                  <option value="pending">В ожидании</option>
                  <option value="in-progress">В процессе</option>
                  <option value="completed">Завершено</option>
                </select>
                <i class="fas fa-chevron-down select-arrow"></i>
              </div>
            </div>
          </div>
          
          <div class="form-grid">
            <div class="form-group">
              <label for="deadline">Срок выполнения</label>
              <div class="date-input">
                <input 
                  type="date" 
                  id="deadline" 
                  v-model="newTask.deadline" 
                  required
                  :class="{ 'error': formErrors.deadline }"
                >
                <i class="fas fa-calendar-alt date-icon"></i>
                <span class="error-message" v-if="formErrors.deadline">{{ formErrors.deadline }}</span>
              </div>
            </div>
            
            <div class="form-group">
              <label for="assignee">Исполнитель</label>
              <div class="assignee-input">
                <input 
                  type="text" 
                  id="assignee" 
                  v-model="newTask.assignee"
                  placeholder="Имя исполнителя"
                >
                <i class="fas fa-user assignee-icon"></i>
              </div>
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" class="btn-text" @click="closeModal">Отмена</button>
            <button 
              type="submit" 
              class="btn-primary"
              :disabled="isSaving"
            >
              <i class="fas fa-spinner fa-spin" v-if="isSaving"></i>
              <span v-else>Сохранить</span>
            </button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- Компонент для уведомлений -->
    <div class="toast-container" v-if="toast.show">
      <div class="toast" :class="toast.type">
        <i :class="getToastIcon()"></i>
        <span>{{ toast.message }}</span>
        <button class="close-toast" @click="toast.show = false">
          <i class="fas fa-times"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { TaskService } from '../api/services';
import TaskCard from '../components/TaskCard.vue';


export default {
  name: 'TasksView',
  components: {
    TaskCard
  },
  data() {
    
    return {
      tasks: [],
      loading: true,
      viewMode: 'grid', // grid, list, kanban
      showFilters: false,
      searchQuery: '',
      filters: {
        priority: {
          high: true,
          medium: true,
          low: true
        },
        status: {
          pending: true,
          'in-progress': true,
          completed: true
        },
        deadline: {
          overdue: true,
          today: true,
          upcoming: true
        }
      },
      newTask: {
        title: '',
        description: '',
        priority: 'medium',
        status: 'pending',
        deadline: '',
        assignee: ''
      },
      formErrors: {
        title: '',
        deadline: ''
      },
      editingTask: null,
      showModal: false,
      isSaving: false,
      deleteConfirmation: {
        show: false,
        taskId: null
      },
      toast: {
        show: false,
        message: '',
        type: 'success',
        timeout: null
      }
    }; 
  },
  
  computed: {
    pendingCount() {
      return this.tasks.filter(task => task.status === 'pending').length;
    },
    inProgressCount() {
      return this.tasks.filter(task => task.status === 'in-progress').length;
    },
    completedCount() {
      return this.tasks.filter(task => task.status === 'completed').length;
    },
    isFiltered() {
      // Проверяем, применены ли фильтры
      return (
        !this.filters.priority.high || 
        !this.filters.priority.medium || 
        !this.filters.priority.low ||
        !this.filters.status.pending ||
        !this.filters.status['in-progress'] ||
        !this.filters.status.completed ||
        !this.filters.deadline.overdue ||
        !this.filters.deadline.today ||
        !this.filters.deadline.upcoming
      );
    },
    // Фильтрованные задачи для канбан-доски
    pendingTasks() {
      return this.filteredTasks.filter(task => task.status === 'pending');
    },
    inProgressTasks() {
      return this.filteredTasks.filter(task => task.status === 'in-progress');
    },
    completedTasks() {
      return this.filteredTasks.filter(task => task.status === 'completed');
    },
    // Фильтрованные задачи
    filteredTasks() {
      return this.tasks.filter(task => {
        // Поиск по названию и описанию
        const matchesSearch = (
          task.title.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
          (task.description && task.description.toLowerCase().includes(this.searchQuery.toLowerCase()))
        );
        
        // Фильтрация по приоритету
        const matchesPriority = this.filters.priority[task.priority];
        
        // Фильтрация по статусу
        const matchesStatus = this.filters.status[task.status];
        
        // Фильтрация по сроку
        let matchesDeadline = true;
        if (task.deadline) {
          const deadlineDate = new Date(task.deadline);
          const today = new Date();
          today.setHours(0, 0, 0, 0);
          deadlineDate.setHours(0, 0, 0, 0);
          
          const diffTime = deadlineDate - today;
          const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
          
          if (diffDays < 0 && !this.filters.deadline.overdue) {
            matchesDeadline = false;
          } else if (diffDays === 0 && !this.filters.deadline.today) {
            matchesDeadline = false;
          } else if (diffDays > 0 && !this.filters.deadline.upcoming) {
            matchesDeadline = false;
          }
        }
        
        return matchesSearch && matchesPriority && matchesStatus && matchesDeadline;
      });
    }
  },
  mounted() {
    this.fetchTasks();
  },
  methods: {
    async fetchTasks() {
      this.loading = true;
      try {
        // Используем сервис для получения задач
        this.tasks = await TaskService.getAll();
        setTimeout(() => {
          this.loading = false;
        }, 500);
      } catch (error) {
        console.error('Ошибка при получении задач:', error);
        // Демо-данные уже обрабатываются в сервисе
        this.loading = false;
        // Если нужно, можно добавить дополнительную обработку ошибок здесь
      }
    },
    openCreateModal() {
      this.editingTask = null;
      const today = new Date();
      const formattedDate = today.toISOString().split('T')[0]; // YYYY-MM-DD формат
      
      this.newTask = {
        title: '',
        description: '',
        priority: 'medium',
        status: 'pending',
        deadline: formattedDate,
        assignee: ''
      };
      
      this.formErrors = { title: '', deadline: '' };
      this.showModal = true;
      this.showFilters = false;
    },
    
    openEditModal(task) {
      this.editingTask = task.id;
      this.newTask = {...task};
      this.formErrors = { title: '', deadline: '' };
      this.showModal = true;
    },
    
    closeModal() {
      this.showModal = false;
    },
    
    validateForm() {
      let isValid = true;
      this.formErrors = { title: '', deadline: '' };
      
      if (!this.newTask.title.trim()) {
        this.formErrors.title = 'Название задачи обязательно';
        isValid = false;
      }
      
      if (!this.newTask.deadline) {
        this.formErrors.deadline = 'Укажите срок выполнения';
        isValid = false;
      }
      
      return isValid;
    },
    
    saveTask() {
      if (!this.validateForm()) return;
      
      this.isSaving = true;
      
      if (this.editingTask) {
        // Обновление существующей задачи
        TaskService.update(this.editingTask, this.newTask)
          .then(() => {
            this.fetchTasks();
            setTimeout(() => {
              this.showModal = false;
              this.isSaving = false;
              this.showToast('Задача успешно обновлена', 'success');
            }, 600);
          })
          .catch(error => {
            console.error('Ошибка при обновлении задачи:', error);
            this.isSaving = false;
            this.showToast('Ошибка при обновлении задачи', 'error');
          });
      } else {
        // Создание новой задачи
        TaskService.create(this.newTask)
          .then(() => {
            this.fetchTasks();
            setTimeout(() => {
              this.showModal = false;
              this.isSaving = false;
              this.showToast('Задача успешно создана', 'success');
            }, 600);
          })
          .catch(error => {
            console.error('Ошибка при создании задачи:', error);
            this.isSaving = false;
            this.showToast('Ошибка при создании задачи', 'error');
          });
      }
    },
    
    confirmDelete(taskId) {
      this.deleteConfirmation = {
        show: true,
        taskId: taskId
      };
    },
    
    cancelDelete() {
      this.deleteConfirmation = {
        show: false,
        taskId: null
      };
    },
    
    deleteTask() {
      if (!this.deleteConfirmation.taskId) return;
      
      TaskService.delete(this.deleteConfirmation.taskId)
        .then(() => {
          this.fetchTasks();
          this.deleteConfirmation.show = false;
          this.showToast('Задача успешно удалена', 'success');
        })
        .catch(error => {
          console.error('Ошибка при удалении задачи:', error);
          this.showToast('Ошибка при удалении задачи', 'error');
        });
    },
    
    changeTaskStatus(task, newStatus) {
      const updatedTask = {...task, status: newStatus};
      
      axios.put(`http://127.0.0.1:8000/api/tasks/${task.id}/`, updatedTask)
        .then(() => {
          this.fetchTasks();
          this.showToast(`Статус задачи изменен на "${this.getStatusLabel(newStatus)}"`, 'success');
        })
        .catch(error => {
          console.error('Ошибка при изменении статуса задачи:', error);
          this.showToast('Ошибка при изменении статуса задачи', 'error');
        });
    },
    
    resetFilters() {
      this.filters = {
        priority: {
          high: true,
          medium: true,
          low: true
        },
        status: {
          pending: true,
          'in-progress': true,
          completed: true
        },
        deadline: {
          overdue: true,
          today: true,
          upcoming: true
        }
      };
      this.searchQuery = '';
    },
    
    showToast(message, type = 'success') {
      // Очищаем предыдущий таймер, если он существует
      if (this.toast.timeout) {
        clearTimeout(this.toast.timeout);
      }
      
      this.toast = {
        show: true,
        message: message,
        type: type,
        timeout: setTimeout(() => {
          this.toast.show = false;
        }, 3000)
      };
    },
    
    getStatusLabel(status) {
      switch(status) {
        case 'pending': return 'В ожидании';
        case 'in-progress': return 'В процессе';
        case 'completed': return 'Завершено';
        default: return status;
      }
    },
    
    formatDeadline(date) {
      if (!date) return '—';
      
      const deadlineDate = new Date(date);
      const today = new Date();
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
        return `Через ${diffDays} дн.`;
      } else {
        const options = { day: 'numeric', month: 'short' };
        return deadlineDate.toLocaleDateString('ru-RU', options);
      }
    },
    
    getDeadlineStatus(date) {
      if (!date) return '';
      
      const deadlineDate = new Date(date);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      deadlineDate.setHours(0, 0, 0, 0);
      
      const diffTime = deadlineDate - today;
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      if (diffDays < 0) {
        return 'overdue';
      } else if (diffDays <= 2) {
        return 'urgent';
      } else if (diffDays <= 7) {
        return 'upcoming';
      } else {
        return '';
      }
    },
    
    truncateText(text, length) {
      if (!text) return '';
      return text.length > length 
        ? text.substring(0, length) + '...' 
        : text;
    },
    
    getInitials(name) {
      if (!name) return '';
      return name.split(' ')
        .map(part => part.charAt(0).toUpperCase())
        .join('');
    },
    
    availableStatuses(task) {
      const statuses = [];
      
      if (task.status !== 'pending') {
        statuses.push({ 
          value: 'pending', 
          label: 'В ожидание', 
          icon: 'fas fa-pause-circle' 
        });
      }
      
      if (task.status !== 'in-progress') {
        statuses.push({ 
          value: 'in-progress', 
          label: 'В процесс', 
          icon: 'fas fa-play-circle' 
        });
      }
      
      if (task.status !== 'completed') {
        statuses.push({ 
          value: 'completed', 
          label: 'Завершить', 
          icon: 'fas fa-check-circle' 
        });
      }
      
      return statuses;
    },
    
    getToastIcon() {
      switch(this.toast.type) {
        case 'success': return 'fas fa-check-circle';
        case 'error': return 'fas fa-exclamation-circle';
        case 'warning': return 'fas fa-exclamation-triangle';
        case 'info': return 'fas fa-info-circle';
        default: return 'fas fa-bell';
      }
    }
  }
};
</script>

<style src="@/assets/tasks.css"></style>