<template>
  <div class="task-card" :class="[task.status, {'kanban-card': kanban}]">
    <div class="task-priority" :class="task.priority"></div>
    <div class="task-content">
      <div class="task-header">
        <h3 class="task-title">{{ task.title }}</h3>
        <div class="task-menu">
          <button class="btn-icon menu-trigger">
            <i class="fas fa-ellipsis-v"></i>
          </button>
          <div class="card-menu">
            <button class="menu-item" @click="$emit('edit', task)">
              <i class="fas fa-edit"></i> Редактировать
            </button>
            <button class="menu-item status-action" @click="nextStatus">
              <i :class="getStatusActionIcon()"></i> {{ getStatusActionText() }}
            </button>
            <button class="menu-item delete" @click="$emit('delete', task.id)">
              <i class="fas fa-trash"></i> Удалить
            </button>
          </div>
        </div>
      </div>
      
      <p v-if="task.description" class="task-description">{{ truncateText(task.description, 150) }}</p>
      
      <div class="task-meta">
        <div class="meta-item deadline" :class="getDeadlineStatus(task.deadline)">
          <i class="fas fa-calendar-alt"></i>
          <span>{{ formatDeadline(task.deadline) }}</span>
        </div>
        
        <div class="meta-item assignee" v-if="task.assignee">
          <i class="fas fa-user"></i>
          <span>{{ task.assignee }}</span>
        </div>
      </div>
      
      <div class="task-actions">
        <div class="status-badge" :class="task.status">
          {{ getStatusLabel(task.status) }}
        </div>
        
        <button class="status-action-btn" @click="nextStatus">
          <i :class="getStatusActionIcon()"></i>
          <span>{{ getStatusActionText() }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TaskCard',
  props: {
    task: {
      type: Object,
      required: true
    },
    kanban: {
      type: Boolean,
      default: false
    }
  },
  methods: {
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
    getStatusLabel(status) {
      switch(status) {
        case 'pending': return 'В ожидании';
        case 'in-progress': return 'В процессе';
        case 'completed': return 'Завершено';
        default: return status;
      }
    },
    nextStatus() {
      let newStatus;
      switch(this.task.status) {
        case 'pending':
          newStatus = 'in-progress';
          break;
        case 'in-progress':
          newStatus = 'completed';
          break;
        case 'completed':
          newStatus = 'pending';
          break;
        default:
          newStatus = 'pending';
      }
      this.$emit('status-change', this.task, newStatus);
    },
    getStatusActionText() {
      switch(this.task.status) {
        case 'pending': return 'Начать';
        case 'in-progress': return 'Завершить';
        case 'completed': return 'Возобновить';
        default: return 'Изменить';
      }
    },
    getStatusActionIcon() {
      switch(this.task.status) {
        case 'pending': return 'fas fa-play';
        case 'in-progress': return 'fas fa-check';
        case 'completed': return 'fas fa-redo';
        default: return 'fas fa-sync';
      }
    },
    truncateText(text, length) {
      if (!text) return '';
      return text.length > length 
        ? text.substring(0, length) + '...' 
        : text;
    }
  }
};
</script>

<!-- Стили перенесены в main.css -->