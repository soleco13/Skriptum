<template>
  <div class="dashboard">
    <!-- Статистика -->
    <div class="dashboard-grid">
      <div class="dashboard-card documents-card" @mouseenter="hoverCard('documents')" @mouseleave="leaveCard">
        <div class="card-header">
          <div class="card-icon">
            <i class="fas fa-file-alt"></i>
          </div>
          <h3>Документы</h3>
        </div>
        <div class="card-content">
          <div class="stat">
            <div class="counter-container">
              <span class="stat-number">{{ documentStats.total }}</span>
              <span class="trend-indicator positive">
                <i class="fas fa-arrow-up"></i>
                <span>5%</span>
              </span>
            </div>
            <span class="stat-label">Всего документов</span>
          </div>
          <div class="stat-chart">
            <div class="pie-chart">
              <svg viewBox="0 0 36 36">
                <path class="circle-bg"
                  d="M18 2.0845
                    a 15.9155 15.9155 0 0 1 0 31.831
                    a 15.9155 15.9155 0 0 1 0 -31.831" />
                <path class="circle circle-1"
                  :stroke-dasharray="`${getDocumentApprovedPercentage()}, 100`"
                  d="M18 2.0845
                    a 15.9155 15.9155 0 0 1 0 31.831
                    a 15.9155 15.9155 0 0 1 0 -31.831" />
                <text x="18" y="20.5" class="percentage">{{ getDocumentApprovedPercentage() }}%</text>
              </svg>
            </div>
          </div>
          <div class="stat-details">
            <div class="stat-item">
              <span class="stat-value">{{ documentStats.review }}</span>
              <span>На рассмотрении</span>
              <span class="status-indicator review"></span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ documentStats.approved }}</span>
              <span>Утверждено</span>
              <span class="status-indicator approved"></span>
            </div>
          </div>
        </div>
        <div class="card-footer">
          <router-link to="/documents" class="card-link">
    Просмотреть все <i class="fas fa-arrow-right"></i>
  </router-link>
        </div>
      </div>

      <div class="dashboard-card tasks-card" @mouseenter="hoverCard('tasks')" @mouseleave="leaveCard">
        <div class="card-header">
          <div class="card-icon">
            <i class="fas fa-tasks"></i>
          </div>
          <h3>Задачи</h3>
        </div>
        <div class="card-content">
          <div class="task-summary">
            <div class="task-summary-item">
              <div class="counter-container">
                <span class="stat-number">{{ taskStats.active }}</span>
                <span class="trend-indicator neutral">
                  <i class="fas fa-minus"></i>
                </span>
              </div>
              <span class="stat-label">Активных задач</span>
            </div>
            <div class="task-summary-item">
              <div class="counter-container">
                <span class="stat-number">{{ taskStats.completed }}</span>
                <span class="trend-indicator positive">
                  <i class="fas fa-arrow-up"></i>
                  <span>10%</span>
                </span>
              </div>
              <span class="stat-label">Завершено</span>
            </div>
          </div>
          <div class="progress-container">
            <div class="progress-bar">
              <div class="progress" :style="{ width: taskStats.completionRate + '%' }"></div>
            </div>
            <div class="progress-labels">
              <span>Прогресс</span>
              <span>{{ taskStats.completionRate }}%</span>
            </div>
          </div>
        </div>
        <div class="card-footer">
          <router-link to="/tasks" class="card-link">
    Просмотреть все <i class="fas fa-arrow-right"></i>
  </router-link>
        </div>
      </div>

      <div class="dashboard-card processes-card" @mouseenter="hoverCard('processes')" @mouseleave="leaveCard">
        <div class="card-header">
          <div class="card-icon">
            <i class="fas fa-project-diagram"></i>
          </div>
          <h3>Процессы</h3>
        </div>
        <div class="card-content">
          <div class="stat">
            <div class="counter-container">
              <span class="stat-number">{{ processStats.active }}</span>
              <span class="trend-indicator positive">
                <i class="fas fa-arrow-up"></i>
                <span>3%</span>
              </span>
            </div>
            <span class="stat-label">Активные процессы</span>
          </div>
          <div class="process-chart">
            <div class="vertical-bars">
              <div class="bar-item">
                <div class="bar-container">
                  <div class="bar" :style="{ height: getProcessBarHeight('active') }"></div>
                </div>
                <span>Активные</span>
              </div>
              <div class="bar-item">
                <div class="bar-container">
                  <div class="bar" :style="{ height: getProcessBarHeight('pending') }"></div>
                </div>
                <span>В ожидании</span>
              </div>
              <div class="bar-item">
                <div class="bar-container">
                  <div class="bar" :style="{ height: getProcessBarHeight('completed') }"></div>
                </div>
                <span>Завершено</span>
              </div>
            </div>
          </div>
        </div>
        <div class="card-footer">
          <router-link to="/processes" class="card-link">
    Просмотреть все <i class="fas fa-arrow-right"></i>
  </router-link>
        </div>
      </div>
    </div>

    <!-- Недавние действия -->
    <div class="recent-section">
      <div class="section-header">
        <h2>Последние действия</h2>
        <button class="refresh-btn" @click="fetchRecentActivities">
          <i class="fas fa-sync-alt"></i>
        </button>
      </div>
      <div class="recent-activity">
        <div class="activity-timeline" v-if="recentActivities.length > 0">
          <div class="timeline-divider" v-if="hasActivitiesToday">
            <span>Сегодня</span>
          </div>
          <div class="activity-item" 
               v-for="activity in recentActivities" 
               :key="activity.id"
               :class="{ 'highlight': hoveredActivity === activity.id }"
               @mouseenter="hoveredActivity = activity.id"
               @mouseleave="hoveredActivity = null">
            <div class="activity-icon" :class="activity.type">
              <i :class="getActivityIcon(activity.type)"></i>
            </div>
            <div class="activity-content">
              <p class="activity-description">{{ activity.description }}</p>
              <span class="activity-time">{{ formatDate(activity.timestamp) }}</span>
            </div>
            <div class="activity-actions">
              <button class="action-icon">
                <i class="fas fa-eye"></i>
              </button>
            </div>
          </div>
        </div>
        <div v-else class="no-activity">
          <div class="empty-state">
            <i class="fas fa-calendar-times"></i>
            <p>Нет недавних действий</p>
            <button class="btn-primary">Запустить новый процесс</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { DocumentService, TaskService, ProcessService, ActivityService } from '../api/services';

export default {
  name: 'DashboardView',
  data() {
    return {
      documentStats: {
        total: 0,
        review: 0,
        approved: 0
      },
      taskStats: {
        active: 0,
        completed: 0,
        total: 0,
        completionRate: 0
      },
      processStats: {
        active: 0,
        pending: 0,
        completed: 0
      },
      recentActivities: [],
      activeCard: null,
      hoveredActivity: null
    }
  },
  computed: {
    hasActivitiesToday() {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      
      return this.recentActivities.some(activity => {
        const activityDate = new Date(activity.timestamp);
        return activityDate >= today;
      });
    }
  },
  mounted() {
    this.fetchDocumentStats();
    this.fetchTaskStats();
    this.fetchProcessStats();
    this.fetchRecentActivities();
  },
  methods: {
    async fetchDocumentStats() {
      try {
        // Используем сервис для получения документов
        const documents = await DocumentService.getAll();
        this.documentStats.total = documents.length;
        this.documentStats.review = documents.filter(doc => doc.status === 'review').length;
        this.documentStats.approved = documents.filter(doc => doc.status === 'approved').length;
      } catch (error) {
        // Обработка ошибок уже реализована в сервисе
        console.error('Ошибка при получении статистики документов:', error);
        this.documentStats = {
          total: 47,
          review: 12,
          approved: 35
        };
      }
    },
    
    async fetchTaskStats() {
      try {
        // Используем сервис для получения задач
        const tasks = await TaskService.getAll();
        this.taskStats.total = tasks.length;
        this.taskStats.active = tasks.filter(task => 
          task.status === 'pending' || task.status === 'in-progress'
        ).length;
        this.taskStats.completed = tasks.filter(task => task.status === 'completed').length;
        
        // Расчет процента выполнения
          if (this.taskStats.total > 0) {
            this.taskStats.completionRate = Math.round((this.taskStats.completed / this.taskStats.total) * 100);
          }
        } catch (error) {
          console.error('Ошибка при получении статистики задач:', error);
          // Демо-данные при ошибке загрузки
          this.taskStats = {
            active: 23,
            completed: 18,
            total: 41,
            completionRate: 44
          };
        }
    },
    
    async fetchProcessStats() {
      try {
        // Используем сервис для получения процессов
        const processes = await ProcessService.getAll();
        this.processStats.active = processes.filter(proc => proc.status === 'active').length;
        this.processStats.pending = processes.filter(proc => proc.status === 'pending').length;
        this.processStats.completed = processes.filter(proc => proc.status === 'completed').length;
      } catch (error) {
        console.error('Ошибка при получении статистики процессов:', error);
        // Демо-данные при ошибке загрузки
        this.processStats = {
          active: 15,
          pending: 8,
          completed: 32
        };
      }
    },
    
    async fetchRecentActivities() {
      try {
        // Используем сервис для получения активностей
        // ActivityService автоматически создает имитацию активностей на основе данных из других сервисов
        this.recentActivities = await ActivityService.getRecent();
      } catch (error) {
        console.error('Ошибка при получении данных для активностей:', error);
        // Демо-данные при ошибке уже обрабатываются в сервисе
      }
    },
    
    getActivityIcon(type) {
      switch(type) {
        case 'document':
          return 'fas fa-file-signature';
        case 'task':
          return 'fas fa-tasks';
        case 'process':
          return 'fas fa-project-diagram';
        default:
          return 'fas fa-bell';
      }
    },
    
    formatDate(date) {
      const now = new Date();
      const activityDate = new Date(date);
      const diffMs = now - activityDate;
      const diffMins = Math.round(diffMs / 60000);
      const diffHours = Math.round(diffMs / 3600000);
      const diffDays = Math.round(diffMs / 86400000);
      
      if (diffMins < 60) {
        return `${diffMins} ${this.pluralize(diffMins, 'минута', 'минуты', 'минут')} назад`;
      } else if (diffHours < 24) {
        return `${diffHours} ${this.pluralize(diffHours, 'час', 'часа', 'часов')} назад`;
      } else {
        return `${diffDays} ${this.pluralize(diffDays, 'день', 'дня', 'дней')} назад`;
      }
    },
    
    pluralize(count, one, few, many) {
      if (count % 10 === 1 && count % 100 !== 11) {
        return one;
      } else if ([2, 3, 4].includes(count % 10) && ![12, 13, 14].includes(count % 100)) {
        return few;
      } else {
        return many;
      }
    },
    
    hoverCard(card) {
      this.activeCard = card;
    },
    
    leaveCard() {
      this.activeCard = null;
    },
    
    getDocumentApprovedPercentage() {
      if (this.documentStats.total === 0) return 0;
      return Math.round((this.documentStats.approved / this.documentStats.total) * 100);
    },
    
    getProcessBarHeight(type) {
      const total = this.processStats.active + this.processStats.pending + this.processStats.completed;
      if (total === 0) return '0%';
      
      const value = this.processStats[type];
      return `${(value / total) * 100}%`;
    }
  }
}
</script>

<style src="@/assets/board.css"></style>

