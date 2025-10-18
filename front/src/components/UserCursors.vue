<template>
  <div class="user-cursors">
    <div 
      v-for="cursor in cursors" 
      :key="cursor.user_id"
      class="user-cursor"
      :data-user-id="cursor.user_id"
      :style="getCursorStyle(cursor)"
    >
      <div class="cursor-pointer"></div>
      <div class="cursor-label">
        <div class="user-avatar">
          <i class="fas fa-user"></i>
        </div>
        <span class="username">{{ cursor.full_name || cursor.username }}</span>
      </div>
    </div>
  </div>
</template>

<script>
// Updated: 2024-01-20 - Fixed cursor positioning
export default {
  name: 'UserCursors',
  props: {
    cursors: {
      type: Array,
      default: () => []
    }
  },
  methods: {
    getCursorStyle(cursor) {
      // Получаем масштаб из родительского компонента
      const zoom = this.$parent.modeler ? this.$parent.modeler.get('canvas').zoom() : 1
      return {
        left: (cursor.x * zoom) + 'px',
        top: (cursor.y * zoom) + 'px'
      }
    }
  }
}
</script>

<style scoped>
.user-cursors {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1000;
}

.user-cursor {
  position: absolute;
  transform: translate(0, 0);
  transition: all 0.2s ease-out;
  pointer-events: none;
  will-change: transform;
}

.cursor-pointer {
  width: 20px;
  height: 20px;
  background: linear-gradient(135deg, #3B82F6, #1D4ED8);
  border-radius: 50% 50% 50% 0;
  transform: rotate(-45deg);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
  position: relative;
}

.cursor-pointer::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 6px;
  height: 6px;
  background: white;
  border-radius: 50%;
  transform: translate(-50%, -50%);
}

.cursor-label {
  position: absolute;
  top: 25px;
  left: 10px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  white-space: nowrap;
  backdrop-filter: blur(4px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.user-avatar {
  width: 16px;
  height: 16px;
  background: linear-gradient(135deg, #10B981, #059669);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.625rem;
  color: white;
}

.username {
  font-weight: 500;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Анимация пульсации для активных курсоров */
.user-cursor.active .cursor-pointer {
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: rotate(-45deg) scale(1);
    opacity: 1;
  }
  50% {
    transform: rotate(-45deg) scale(1.1);
    opacity: 0.8;
  }
}

/* Разные цвета для разных пользователей */
.user-cursor:nth-child(1) .cursor-pointer {
  background: linear-gradient(135deg, #3B82F6, #1D4ED8);
}

.user-cursor:nth-child(2) .cursor-pointer {
  background: linear-gradient(135deg, #10B981, #059669);
}

.user-cursor:nth-child(3) .cursor-pointer {
  background: linear-gradient(135deg, #F59E0B, #D97706);
}

.user-cursor:nth-child(4) .cursor-pointer {
  background: linear-gradient(135deg, #EF4444, #DC2626);
}

.user-cursor:nth-child(5) .cursor-pointer {
  background: linear-gradient(135deg, #8B5CF6, #7C3AED);
}

.user-cursor:nth-child(6) .cursor-pointer {
  background: linear-gradient(135deg, #EC4899, #DB2777);
}
</style>