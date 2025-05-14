<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-logo">
        <img src="@/assets/logo.png" alt="Skriptum" class="logo-img">
        <h1>Skriptum</h1>
      </div>
      
      <div class="auth-form">
        <h2>Вход в систему</h2>
        <div v-if="error" class="error-message">{{ error }}</div>
        
        <form @submit.prevent="login">
          <div class="form-group">
            <label for="username">Имя пользователя</label>
            <input 
              type="text" 
              id="username" 
              v-model="username" 
              required
              placeholder="Введите имя пользователя"
            >
          </div>
          
          <div class="form-group">
            <label for="password">Пароль</label>
            <div class="password-input">
              <input 
                :type="showPassword ? 'text' : 'password'" 
                id="password" 
                v-model="password" 
                required
                placeholder="Введите пароль"
              >
              <button 
                type="button" 
                class="toggle-password" 
                @click="showPassword = !showPassword"
              >
                <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
          </div>
          
          <div class="form-options">
            <label class="checkbox-container">
              <input type="checkbox" v-model="rememberMe">
              <span class="checkmark"></span>
              Запомнить меня
            </label>
            <a href="#" class="forgot-password">Забыли пароль?</a>
          </div>
          
          <button type="submit" class="btn-submit" :disabled="isLoading">
            <span v-if="isLoading"><i class="fas fa-spinner fa-spin"></i> Вход...</span>
            <span v-else>Войти</span>
          </button>
        </form>
        
        <div class="auth-links">
          <p>Нет аккаунта? <router-link to="/register">Зарегистрироваться</router-link></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { authService } from '@/api/auth';

export default {
  name: 'LoginForm',
  data() {
    return {
      username: '',
      password: '',
      rememberMe: false,
      showPassword: false,
      isLoading: false,
      error: null
    }
  },
  methods: {
    async login() {
      this.isLoading = true;
      this.error = null;
      
      try {
        // Вызываем метод login из сервиса аутентификации
        const response = await authService.login(this.username, this.password);
        
        // Сохраняем токен в localStorage или sessionStorage в зависимости от rememberMe
        const storage = this.rememberMe ? localStorage : sessionStorage;
        storage.setItem('token', response.access); // Сохраняем токен доступа
        
        // Перенаправляем на дашборд
        this.$router.push('/dashboard');
      } catch (err) {
        this.error = 'Неверное имя пользователя или пароль';
        console.error('Login error:', err);
      } finally {
        this.isLoading = false;
      }
    }
  }
}
</script>

<style scoped>
.auth-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.auth-container {
  width: 100%;
  max-width: 420px;
  padding: 2rem;
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.auth-logo {
  text-align: center;
  margin-bottom: 2rem;
}

.auth-logo img {
  width: 60px;
  height: 60px;
}

.auth-logo h1 {
  margin-top: 0.5rem;
  font-size: 1.8rem;
  color: #333;
}

.auth-form h2 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #333;
  font-size: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #555;
}

input[type="text"],
input[type="password"] {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

input[type="text"]:focus,
input[type="password"]:focus {
  border-color: #4a90e2;
  outline: none;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
}

.password-input {
  position: relative;
}

.toggle-password {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #777;
  cursor: pointer;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
}

.checkbox-container {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.checkbox-container input {
  margin-right: 8px;
}

.forgot-password {
  color: #4a90e2;
  text-decoration: none;
}

.forgot-password:hover {
  text-decoration: underline;
}

.btn-submit {
  width: 100%;
  padding: 0.75rem;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-submit:hover {
  background-color: #3a7bc8;
}

.btn-submit:disabled {
  background-color: #a0c1e8;
  cursor: not-allowed;
}

.auth-links {
  text-align: center;
  margin-top: 1.5rem;
  font-size: 0.9rem;
}

.auth-links a {
  color: #4a90e2;
  text-decoration: none;
}

.auth-links a:hover {
  text-decoration: underline;
}

.error-message {
  background-color: #ffebee;
  color: #d32f2f;
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
}

/* Адаптивность для мобильных устройств */
@media (max-width: 480px) {
  .auth-container {
    padding: 1.5rem;
    max-width: 100%;
    border-radius: 0;
    box-shadow: none;
  }
}
</style>