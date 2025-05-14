<template>
  <div id="app">
    <!-- Показываем хедер и сайдбар только если это не лендинг, не страница входа и не страница регистрации -->
    <template v-if="!isPublicPage">
      <header>
        <router-link to="/dashboard" class="logo">
  <img src="./assets/logo.png" alt="Skriptum logo" class="logo-img">
  <span class="logo-text">Skriptum</span>
</router-link>
        <div class="user-menu">
          <div class="search-global">
            <i class="fas fa-search"></i>
            <input type="text" placeholder="Глобальный поиск...">
          </div>
          <div class="notifications">
            <i class="fas fa-bell"></i>
            <span class="notification-badge">3</span>
          </div>
          <div class="user-profile" @click="toggleProfileMenu">
            <img src="./assets/avatar.png" alt="User" class="avatar">
            <span>{{ userName }}</span>
            <i class="fas fa-chevron-down"></i>
            
            <!-- Выпадающее меню профиля -->
            <div class="profile-dropdown" v-if="showProfileMenu">
              <router-link to="/profile" class="dropdown-item">
                <i class="fas fa-user"></i> Мой профиль
              </router-link>
              <div class="dropdown-divider"></div>
              <a href="#" class="dropdown-item" @click.prevent="logout">
                <i class="fas fa-sign-out-alt"></i> Выйти
              </a>
            </div>
          </div>
        </div>
      </header>

      <div class="container">
        <aside class="sidebar">
          <nav class="nav-menu">
            <router-link to="/dashboard" class="nav-item" active-class="active">
              <i class="fas fa-home"></i>
              <span>Главная</span>
            </router-link>
            
            <router-link to="/documents" class="nav-item" active-class="active">
              <i class="fas fa-file-alt"></i>
              <span>Документы</span>
            </router-link>
            
            <router-link to="/tasks" class="nav-item" active-class="active">
              <i class="fas fa-tasks"></i>
              <span>Задачи</span>
            </router-link>
            
            <router-link to="/processes" class="nav-item" active-class="active">
              <i class="fas fa-project-diagram"></i>
              <span>Бизнес-процессы</span>
            </router-link>
          </nav>

          <div class="sidebar-footer">
            <div class="quick-stats">
              <div class="stat-item">
                <i class="fas fa-clock"></i>
                <span>Активные задачи: 5</span>
              </div>
              <div class="stat-item">
                <i class="fas fa-file-signature"></i>
                <span>На подписи: 3</span>
              </div>
            </div>
          </div>
        </aside>

        <main class="main-content">
          <div class="page-header">
            <h1><router-view name="title"></router-view></h1>
            <div class="breadcrumbs">
              <router-view name="breadcrumbs"></router-view>
            </div>
          </div>
          <router-view></router-view>
        </main>
      </div>
    </template>

    <!-- Показываем только роутер-вью если это лендинг -->
    <template v-else>
      <router-view></router-view>
    </template>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      message: null,  // Изначально данных нет
      showProfileMenu: false,
      userName: 'Александр С.'
    };
  },
  computed: {
    isLanding() {
      // Проверяем, находимся ли мы на главной странице (лендинге)
      return this.$route.path === '/';
    },
    isPublicPage() {
      // Проверяем, находимся ли мы на публичной странице (лендинг, логин, регистрация)
      const publicRoutes = ['/', '/login', '/register'];
      return publicRoutes.includes(this.$route.path);
    }
  },
  methods: {
    toggleProfileMenu() {
      this.showProfileMenu = !this.showProfileMenu;
    },
    logout() {
      // Удаляем токен из хранилища
      localStorage.removeItem('token');
      sessionStorage.removeItem('token');
      
      // Перенаправляем на страницу входа
      this.$router.push('/login');
    }
  },
  mounted() {
    // Закрываем меню профиля при клике вне его
    document.addEventListener('click', (e) => {
      const profileElement = this.$el.querySelector('.user-profile');
      if (profileElement && !profileElement.contains(e.target) && this.showProfileMenu) {
        this.showProfileMenu = false;
      }
    });
    
    // Проверяем наличие токена перед запросом к API
    const token = localStorage.getItem('token') || sessionStorage.getItem('token');
    if (token) {
      // Запрос к Django API с использованием токена
      axios.get('http://127.0.0.1:8000/api/', {
        headers: {
          'Authorization': `JWT ${token}`
        }
      })
        .then(response => {
          this.message = response.data;  // Сохраняем полученные данные
        })
        .catch(error => {
          console.error('Произошла ошибка при запросе данных:', error);
          this.message = { error: "Не удалось загрузить данные" }; // Показываем ошибку пользователю
        });
    }
  }
};
</script>


<style src="@/assets/profile.css"></style>
<style src="@/assets/main.css"></style>