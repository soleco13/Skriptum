<template>
  <div class="profile-page">
    <div class="page-header">
      <h1>Профиль пользователя</h1>
      <div class="header-actions">
        <button class="btn-edit" @click="editMode = !editMode">
          <i class="fas" :class="editMode ? 'fa-times' : 'fa-edit'"></i>
          {{ editMode ? 'Отменить' : 'Редактировать' }}
        </button>
      </div>
    </div>

    <div class="profile-container">
      <div class="profile-sidebar">
        <div class="profile-avatar">
          <img :src="user.avatar || require('@/assets/avatar.png')" alt="Аватар пользователя">
          <div v-if="editMode" class="avatar-upload">
            <label for="avatar-input">
              <i class="fas fa-camera"></i>
              <span>Изменить фото</span>
            </label>
            <input id="avatar-input" type="file" accept="image/*" @change="handleAvatarChange">
          </div>
        </div>
        <div class="profile-stats">
          <div class="stat-item">
            <i class="fas fa-file-alt"></i>
            <div class="stat-info">
              <span class="stat-value">{{ user.documentsCount }}</span>
              <span class="stat-label">Документов</span>
            </div>
          </div>
          <div class="stat-item">
            <i class="fas fa-tasks"></i>
            <div class="stat-info">
              <span class="stat-value">{{ user.tasksCount }}</span>
              <span class="stat-label">Задач</span>
            </div>
          </div>
          <div class="stat-item">
            <i class="fas fa-project-diagram"></i>
            <div class="stat-info">
              <span class="stat-value">{{ user.processesCount }}</span>
              <span class="stat-label">Процессов</span>
            </div>
          </div>
        </div>
      </div>

      <div class="profile-content">
        <form @submit.prevent="saveProfile" v-if="editMode">
          <div class="form-section">
            <h2>Основная информация</h2>
            <div class="form-row">
              <div class="form-group">
                <label for="firstName">Имя</label>
                <input type="text" id="firstName" v-model="editedUser.firstName" required>
              </div>
              <div class="form-group">
                <label for="lastName">Фамилия</label>
                <input type="text" id="lastName" v-model="editedUser.lastName" required>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" v-model="editedUser.email" required>
              </div>
              <div class="form-group">
                <label for="phone">Телефон</label>
                <input type="tel" id="phone" v-model="editedUser.phone">
              </div>
            </div>
            <div class="form-group">
              <label for="position">Должность</label>
              <input type="text" id="position" v-model="editedUser.position">
            </div>
            <div class="form-group">
              <label for="department">Отдел</label>
              <input type="text" id="department" v-model="editedUser.department">
            </div>
          </div>

          <div class="form-section">
            <h2>Безопасность</h2>
            <div class="form-group">
              <label for="currentPassword">Текущий пароль</label>
              <input type="password" id="currentPassword" v-model="passwords.current">
            </div>
            <div class="form-row">
              <div class="form-group">
                <label for="newPassword">Новый пароль</label>
                <input type="password" id="newPassword" v-model="passwords.new">
              </div>
              <div class="form-group">
                <label for="confirmPassword">Подтверждение пароля</label>
                <input type="password" id="confirmPassword" v-model="passwords.confirm">
              </div>
            </div>
          </div>

          <div class="form-section">
            <h2>Настройки</h2>
            <div class="form-group checkbox-group">
              <label class="checkbox-container">
                <input type="checkbox" v-model="editedUser.settings.emailNotifications">
                <span class="checkmark"></span>
                Получать уведомления по email
              </label>
            </div>
            <div class="form-group checkbox-group">
              <label class="checkbox-container">
                <input type="checkbox" v-model="editedUser.settings.darkMode">
                <span class="checkmark"></span>
                Темная тема
              </label>
            </div>
          </div>

          <div class="form-actions">
            <button type="button" class="btn-cancel" @click="cancelEdit">Отменить</button>
            <button type="submit" class="btn-save" :disabled="isLoading">
              <span v-if="isLoading"><i class="fas fa-spinner fa-spin"></i> Сохранение...</span>
              <span v-else>Сохранить изменения</span>
            </button>
          </div>
        </form>

        <div class="profile-info" v-else>
          <div class="info-section">
            <h2>Основная информация</h2>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">Имя</span>
                <span class="info-value">{{ user.firstName }} {{ user.lastName }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Email</span>
                <span class="info-value">{{ user.email }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Телефон</span>
                <span class="info-value">{{ user.phone || 'Не указан' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Должность</span>
                <span class="info-value">{{ user.position || 'Не указана' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Отдел</span>
                <span class="info-value">{{ user.department || 'Не указан' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Дата регистрации</span>
                <span class="info-value">{{ user.registrationDate }}</span>
              </div>
            </div>
          </div>

          <div class="info-section">
            <h2>Настройки</h2>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">Уведомления по email</span>
                <span class="info-value">{{ user.settings.emailNotifications ? 'Включены' : 'Отключены' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Темная тема</span>
                <span class="info-value">{{ user.settings.darkMode ? 'Включена' : 'Отключена' }}</span>
              </div>
            </div>
          </div>

          <div class="info-section">
            <h2>Последняя активность</h2>
            <div class="activity-list">
              <div class="activity-item" v-for="(activity, index) in user.recentActivity" :key="index">
                <div class="activity-icon">
                  <i :class="getActivityIcon(activity.type)"></i>
                </div>
                <div class="activity-details">
                  <div class="activity-description">{{ activity.description }}</div>
                  <div class="activity-time">{{ activity.time }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UserProfile',
  data() {
    return {
      editMode: false,
      isLoading: false,
      user: {
        firstName: 'Александр',
        lastName: 'Смирнов',
        email: 'alex.smirnov@example.com',
        phone: '+7 (999) 123-45-67',
        position: 'Менеджер проектов',
        department: 'Отдел разработки',
        registrationDate: '15.03.2024',
        avatar: null,
        documentsCount: 24,
        tasksCount: 12,
        processesCount: 5,
        settings: {
          emailNotifications: true,
          darkMode: false
        },
        recentActivity: [
          {
            type: 'document',
            description: 'Создан документ "Договор поставки №123"',
            time: '2 часа назад'
          },
          {
            type: 'task',
            description: 'Выполнена задача "Подготовить отчет"',
            time: '5 часов назад'
          },
          {
            type: 'process',
            description: 'Запущен процесс "Согласование договора"',
            time: '1 день назад'
          },
          {
            type: 'login',
            description: 'Вход в систему',
            time: '1 день назад'
          }
        ]
      },
      editedUser: null,
      passwords: {
        current: '',
        new: '',
        confirm: ''
      }
    }
  },
  created() {
    // Клонируем объект пользователя для редактирования
    this.editedUser = JSON.parse(JSON.stringify(this.user));
  },
  methods: {
    getActivityIcon(type) {
      const icons = {
        document: 'fas fa-file-alt',
        task: 'fas fa-tasks',
        process: 'fas fa-project-diagram',
        login: 'fas fa-sign-in-alt'
      };
      return icons[type] || 'fas fa-info-circle';
    },
    handleAvatarChange(event) {
      const file = event.target.files[0];
      if (!file) return;
      
      // Здесь будет загрузка файла на сервер
      // Пока просто создаем URL для предпросмотра
      const reader = new FileReader();
      reader.onload = (e) => {
        this.editedUser.avatar = e.target.result;
      };
      reader.readAsDataURL(file);
    },
    cancelEdit() {
      this.editMode = false;
      this.editedUser = JSON.parse(JSON.stringify(this.user));
      this.passwords = { current: '', new: '', confirm: '' };
    },
    async saveProfile() {
      // Проверка паролей, если пользователь хочет изменить пароль
      if (this.passwords.new) {
        if (!this.passwords.current) {
          alert('Введите текущий пароль');
          return;
        }
        if (this.passwords.new !== this.passwords.confirm) {
          alert('Новый пароль и подтверждение не совпадают');
          return;
        }
      }
      
      this.isLoading = true;
      
      try {
        // Здесь будет запрос к API для обновления профиля
        // const response = await this.$http.put('/api/users/profile', {
        //   ...this.editedUser,
        //   password: this.passwords.new || undefined
        // });
        
        // Имитация задержки запроса
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Обновляем данные пользователя
        this.user = { ...this.editedUser };
        this.editMode = false;
        this.passwords = { current: '', new: '', confirm: '' };
        
        // Показываем уведомление об успешном сохранении
        alert('Профиль успешно обновлен');
      } catch (err) {
        console.error('Error updating profile:', err);
        alert('Ошибка при обновлении профиля');
      } finally {
        this.isLoading = false;
      }
    }
  }
}
</script>

<style src="@/assets/profile.css"></style>