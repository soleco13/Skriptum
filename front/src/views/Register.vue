<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-logo">
        <img src="@/assets/logo.png" alt="Skriptum" class="logo-img">
        <h1>Skriptum</h1>
      </div>
      
      <div class="auth-form">
        <h2>Регистрация</h2>
        <div v-if="error" class="error-message">{{ error }}</div>
        
        <form @submit.prevent="register">
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
            <label for="email">Email</label>
            <input 
              type="email" 
              id="email" 
              v-model="email" 
              required
              placeholder="Введите email"
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
              <div class="password-requirements">
                <small>Требования к паролю:</small>
                <ul>
                  <li :class="{ 'requirement-met': password.length >= 8 }">Минимум 8 символов</li>
                  <li :class="{ 'requirement-met': !/^\d+$/.test(password) }">Не только цифры</li>
                  <li :class="{ 'requirement-met': /(?=.*[A-Za-z])(?=.*\d)/.test(password) }">Содержит буквы и цифры</li>
                </ul>
              </div>
              <button 
                type="button" 
                class="toggle-password" 
                @click="showPassword = !showPassword"
              >
                <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
          </div>
          
          <div class="form-group">
            <label for="confirmPassword">Подтверждение пароля</label>
            <div class="password-input">
              <input 
                :type="showConfirmPassword ? 'text' : 'password'" 
                id="confirmPassword" 
                v-model="confirmPassword" 
                required
                placeholder="Подтвердите пароль"
              >
              <button 
                type="button" 
                class="toggle-password" 
                @click="showConfirmPassword = !showConfirmPassword"
              >
                <i :class="showConfirmPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
          </div>
          
          <div class="form-group">
            <label class="checkbox-container">
              <input type="checkbox" v-model="agreeTerms" required>
              <span class="checkmark"></span>
              Я согласен с <a href="#" class="terms-link">условиями использования</a>
            </label>
          </div>
          
          <button type="submit" class="btn-submit" :disabled="isLoading || !agreeTerms || password !== confirmPassword">
            <span v-if="isLoading"><i class="fas fa-spinner fa-spin"></i> Регистрация...</span>
            <span v-else>Зарегистрироваться</span>
          </button>
        </form>
        
        <div class="auth-links">
          <p>Уже есть аккаунт? <router-link to="/login">Войти</router-link></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { authService } from '@/api/auth';

export default {
  name: 'RegisterForm',
  data() {
    return {
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      agreeTerms: false,
      showPassword: false,
      showConfirmPassword: false,
      isLoading: false,
      error: null
    }
  },
  methods: {
    // Валидация пароля
    validatePassword(password) {
      // Проверка на минимальную длину
      if (password.length < 8) {
        return 'Пароль должен содержать не менее 8 символов';
      }
      
      // Проверка на наличие только цифр
      if (/^\d+$/.test(password)) {
        return 'Пароль не должен состоять только из цифр';
      }
      
      // Проверка на наличие букв и цифр
      if (!/(?=.*[A-Za-z])(?=.*\d)/.test(password)) {
        return 'Пароль должен содержать как минимум одну букву и одну цифру';
      }
      
      return null; // Пароль валидный
    },
    
    async register() {
      if (this.password !== this.confirmPassword) {
        this.error = 'Пароли не совпадают';
        return;
      }
      
      // Валидация пароля перед отправкой
      const passwordError = this.validatePassword(this.password);
      if (passwordError) {
        this.error = passwordError;
        return;
      }
      
      this.isLoading = true;
      this.error = null;
      
      try {
        // Вызываем метод register из сервиса аутентификации
        const userData = {
          username: this.username,
          email: this.email,
          password: this.password
        };
        await authService.register(userData);
        
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // После успешной регистрации перенаправляем на страницу входа
        this.$router.push('/login');
      } catch (err) {
        // Более детальная обработка ошибок
        if (err.password) {
          this.error = `Ошибка пароля: ${err.password.join(', ')}`;
        } else if (err.username) {
          this.error = `Ошибка имени пользователя: ${err.username.join(', ')}`;
        } else if (err.email) {
          this.error = `Ошибка email: ${err.email.join(', ')}`;
        } else {
          this.error = 'Ошибка при регистрации. Пожалуйста, проверьте введенные данные.';
        }
        console.error('Registration error:', err);
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
input[type="email"],
input[type="password"] {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

input[type="text"]:focus,
input[type="email"]:focus,
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

.checkbox-container {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.checkbox-container input {
  margin-right: 8px;
}

.terms-link {
  color: #4a90e2;
  text-decoration: none;
}

.terms-link:hover {
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

.password-requirements {
  margin-top: 0.5rem;
  font-size: 0.8rem;
  color: #7f8c8d;
}

.password-requirements ul {
  padding-left: 1.2rem;
  margin-top: 0.3rem;
  margin-bottom: 0;
}

.password-requirements li {
  margin-bottom: 0.2rem;
  color: #e74c3c;
}

.requirement-met {
  color: #2ecc71;
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