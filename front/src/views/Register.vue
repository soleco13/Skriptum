<template>
  <div class="auth-page">
    <!-- Декоративные элементы фона -->
    <div class="bg-decoration">
      <div class="floating-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
        <div class="shape shape-4"></div>
      </div>
    </div>

    <div class="auth-container">
      <!-- Логотип и название -->
      <div class="auth-logo">
        <div class="logo-wrapper">
          <img src="@/assets/logo.png" alt="Skriptum" class="logo-img">
          <div class="logo-glow"></div>
        </div>
        <h1 class="brand-name">Skriptum</h1>
        <p class="brand-subtitle">Система управления документами</p>
      </div>
      
      <!-- Форма регистрации -->
      <div class="auth-form">
        <div class="form-header">
          <h2>Создайте аккаунт</h2>
          <p>Заполните форму для создания нового аккаунта</p>
        </div>

        <!-- Сообщение об ошибке -->
        <div v-if="error" class="error-message">
          <i class="fas fa-exclamation-triangle"></i>
          {{ error }}
        </div>
        
        <form @submit.prevent="register" class="register-form">
          <!-- Поле имени пользователя -->
          <div class="form-group">
            <div class="input-wrapper">
              <i class="fas fa-user input-icon"></i>
              <input 
                type="text" 
                id="username" 
                v-model="username" 
                required
                placeholder="Имя пользователя"
                class="form-input"
                :class="{ 'has-value': username }"
              >
              <label for="username" class="floating-label">Имя пользователя</label>
            </div>
          </div>
          
          <!-- Поле email -->
          <div class="form-group">
            <div class="input-wrapper">
              <i class="fas fa-envelope input-icon"></i>
              <input 
                type="email" 
                id="email" 
                v-model="email" 
                required
                placeholder="Email адрес"
                class="form-input"
                :class="{ 'has-value': email }"
              >
              <label for="email" class="floating-label">Email адрес</label>
            </div>
          </div>
          
          <!-- Поле пароля -->
          <div class="form-group">
            <div class="input-wrapper">
              <i class="fas fa-lock input-icon"></i>
              <input 
                :type="showPassword ? 'text' : 'password'" 
                id="password" 
                v-model="password" 
                required
                placeholder="Пароль"
                class="form-input"
                :class="{ 'has-value': password }"
              >
              <label for="password" class="floating-label">Пароль</label>
              <button 
                type="button" 
                class="toggle-password" 
                @click="showPassword = !showPassword"
                tabindex="-1"
              >
                <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
            <!-- Требования к паролю -->
            <div v-if="password" class="password-requirements">
              <div class="requirements-header">
                <i class="fas fa-info-circle"></i>
                Требования к паролю:
              </div>
              <div class="requirements-list">
                <div class="requirement" :class="{ 'met': password.length >= 8 }">
                  <i :class="password.length >= 8 ? 'fas fa-check' : 'fas fa-times'"></i>
                  Минимум 8 символов
                </div>
                <div class="requirement" :class="{ 'met': !/^\d+$/.test(password) }">
                  <i :class="!/^\d+$/.test(password) ? 'fas fa-check' : 'fas fa-times'"></i>
                  Не только цифры
                </div>
                <div class="requirement" :class="{ 'met': /(?=.*[A-Za-z])(?=.*\d)/.test(password) }">
                  <i :class="/(?=.*[A-Za-z])(?=.*\d)/.test(password) ? 'fas fa-check' : 'fas fa-times'"></i>
                  Буквы и цифры
                </div>
              </div>
            </div>
          </div>
          
          <!-- Поле подтверждения пароля -->
          <div class="form-group">
            <div class="input-wrapper">
              <i class="fas fa-shield-alt input-icon"></i>
              <input 
                :type="showConfirmPassword ? 'text' : 'password'" 
                id="confirmPassword" 
                v-model="confirmPassword" 
                required
                placeholder="Подтвердите пароль"
                class="form-input"
                :class="{ 'has-value': confirmPassword, 'error': confirmPassword && password !== confirmPassword }"
              >
              <label for="confirmPassword" class="floating-label">Подтвердите пароль</label>
              <button 
                type="button" 
                class="toggle-password" 
                @click="showConfirmPassword = !showConfirmPassword"
                tabindex="-1"
              >
                <i :class="showConfirmPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
            <div v-if="confirmPassword && password !== confirmPassword" class="password-mismatch">
              <i class="fas fa-exclamation-triangle"></i>
              Пароли не совпадают
            </div>
          </div>
          
          <!-- Согласие с условиями -->
          <div class="form-group">
            <label class="checkbox-container">
              <input type="checkbox" v-model="agreeTerms" class="checkbox-input" required>
              <span class="checkmark">
                <i class="fas fa-check"></i>
              </span>
              <span class="checkbox-text">
                Я согласен с 
                <a href="#" class="terms-link">
                  <i class="fas fa-external-link-alt"></i>
                  условиями использования
                </a>
              </span>
            </label>
          </div>
          
          <!-- Кнопка регистрации -->
          <button type="submit" class="btn-submit" :disabled="isLoading || !agreeTerms || password !== confirmPassword">
            <span v-if="isLoading" class="loading-content">
              <i class="fas fa-spinner fa-spin"></i>
              Создание аккаунта...
            </span>
            <span v-else class="submit-content">
              <i class="fas fa-user-plus"></i>
              Создать аккаунт
            </span>
          </button>
        </form>
        
        <!-- Ссылки входа -->
        <div class="auth-links">
          <div class="divider">
            <span>или</span>
          </div>
          <p class="login-text">
            Уже есть аккаунт? 
            <router-link to="/login" class="login-link">
              <i class="fas fa-sign-in-alt"></i>
              Войти в систему
            </router-link>
          </p>
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
/* ======================================
 * ПЕРЕМЕННЫЕ SKRIPTUM
 * ====================================== */
:root {
  --primary-color: #0055b3;
  --primary-light: #1e88e5;
  --primary-dark: #003d82;
  --accent-color: #6c5ce7;
  --accent-light: #a29bfe;
  --error-color: #e6294d;
  --success-color: #00b894;
  --text-color: #2d3748;
  --text-light: #718096;
  --background-color: #ffffff;
  --background-alt: #f8fafc;
  --border-radius: 12px;
  --box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
  --transition: all 0.3s ease;
  --gradient-primary: linear-gradient(135deg, var(--primary-color), var(--primary-light));
  --gradient-accent: linear-gradient(135deg, var(--accent-color), var(--accent-light));
  --gradient-background: linear-gradient(135deg, #f5f7fa, #e6ebf5);
  --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 8px 30px rgba(0, 0, 0, 0.08);
  --shadow-lg: 0 20px 60px rgba(0, 0, 0, 0.1);
  --glass-effect: rgba(255, 255, 255, 0.25);
  --glass-blur: blur(12px);
}

/* ======================================
 * ОСНОВНАЯ СТРАНИЦА АВТОРИЗАЦИИ
 * ====================================== */
.auth-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  height: 100vh;
  background: var(--gradient-background);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  position: relative;
  overflow: hidden;
  padding: 1rem;
  box-sizing: border-box;
}

/* ======================================
 * ДЕКОРАТИВНЫЕ ЭЛЕМЕНТЫ ФОНА
 * ====================================== */
.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.floating-shapes {
  position: relative;
  width: 100%;
  height: 100%;
}

.shape {
  position: absolute;
  border-radius: 50%;
  background: var(--gradient-primary);
  opacity: 0.1;
  animation: float 6s ease-in-out infinite;
}

.shape-1 {
  width: 80px;
  height: 80px;
  top: 20%;
  left: 10%;
  animation-delay: 0s;
}

.shape-2 {
  width: 120px;
  height: 120px;
  top: 60%;
  right: 15%;
  animation-delay: 2s;
}

.shape-3 {
  width: 60px;
  height: 60px;
  bottom: 20%;
  left: 20%;
  animation-delay: 4s;
  background: var(--gradient-accent);
}

.shape-4 {
  width: 100px;
  height: 100px;
  top: 10%;
  right: 30%;
  animation-delay: 3s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
}

/* ======================================
 * КОНТЕЙНЕР АВТОРИЗАЦИИ
 * ====================================== */
.auth-container {
  width: 100%;
  max-width: 450px;
  max-height: calc(100vh - 2rem);
  padding: 2.5rem;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: var(--glass-blur);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-lg);
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  z-index: 2;
  transition: var(--transition);
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.auth-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
  border-radius: var(--border-radius);
  pointer-events: none;
}

.auth-container:hover {
  transform: translateY(-2px);
  box-shadow: 0 25px 70px rgba(0, 0, 0, 0.15);
}

/* ======================================
 * ЛОГОТИП И БРЕНДИНГ
 * ====================================== */
.auth-logo {
  text-align: center;
  margin-bottom: 2.5rem;
}

.logo-wrapper {
  position: relative;
  display: inline-block;
  margin-bottom: 1rem;
}

.logo-img {
  width: 80px;
  height: 80px;
  transition: var(--transition);
  position: relative;
  z-index: 2;
}

.logo-glow {
  position: absolute;
  top: -10px;
  left: -10px;
  right: -10px;
  bottom: -10px;
  background: var(--gradient-primary);
  border-radius: 50%;
  opacity: 0;
  filter: blur(20px);
  transition: var(--transition);
  z-index: 1;
}

.logo-wrapper:hover .logo-glow {
  opacity: 0.3;
}

.logo-wrapper:hover .logo-img {
  transform: scale(1.05);
}

.brand-name {
  font-size: 2.2rem;
  font-weight: 700;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0.5rem 0 0.25rem;
  letter-spacing: -0.02em;
}

.brand-subtitle {
  color: var(--text-light);
  font-size: 0.9rem;
  margin: 0;
  opacity: 0.8;
}

/* ======================================
 * ЗАГОЛОВОК ФОРМЫ
 * ====================================== */
.form-header {
  text-align: center;
  margin-bottom: 2rem;
}

.form-header h2 {
  font-size: 1.8rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.5rem;
}

.form-header p {
  color: var(--text-light);
  font-size: 0.95rem;
  margin: 0;
  opacity: 0.9;
}

/* ======================================
 * ФОРМА ВХОДА
 * ====================================== */
.login-form {
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.75rem;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 1rem;
  color: var(--text-light);
  font-size: 1rem;
  z-index: 3;
  transition: var(--transition);
}

.form-input {
  width: 100%;
  padding: 1rem 1rem 1rem 3rem;
  border: 2px solid transparent;
  border-radius: var(--border-radius);
  font-size: 1rem;
  background: var(--background-alt);
  color: var(--text-color);
  transition: var(--transition);
  position: relative;
  z-index: 2;
}

.form-input::placeholder {
  color: transparent;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-color);
  background: var(--background-color);
  box-shadow: 0 0 0 4px rgba(0, 85, 179, 0.1);
}

.form-input:focus + .floating-label,
.form-input.has-value + .floating-label {
  transform: translateY(-2.5rem) scale(0.85);
  color: var(--primary-color);
  font-weight: 500;
}

.form-input:focus ~ .input-icon {
  color: var(--primary-color);
}

.floating-label {
  position: absolute;
  left: 3rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-light);
  font-size: 1rem;
  transition: var(--transition);
  pointer-events: none;
  z-index: 3;
  background: linear-gradient(to bottom, transparent 0%, transparent 40%, var(--background-color) 40%, var(--background-color) 60%, transparent 60%);
  padding: 0 0.5rem;
}

.toggle-password {
  position: absolute;
  right: 1rem;
  background: none;
  border: none;
  color: var(--text-light);
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  transition: var(--transition);
  z-index: 3;
}

.toggle-password:hover {
  background: rgba(0, 85, 179, 0.1);
  color: var(--primary-color);
}

/* ======================================
 * ОПЦИИ ФОРМЫ
 * ====================================== */
.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  font-size: 0.9rem;
}

.checkbox-container {
  display: flex;
  align-items: center;
  cursor: pointer;
  user-select: none;
}

.checkbox-input {
  display: none;
}

.checkmark {
  width: 20px;
  height: 20px;
  border: 2px solid var(--text-light);
  border-radius: 4px;
  margin-right: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition);
  position: relative;
}

.checkmark i {
  font-size: 12px;
  color: white;
  opacity: 0;
  transition: var(--transition);
}

.checkbox-input:checked + .checkmark {
  background: var(--gradient-primary);
  border-color: var(--primary-color);
}

.checkbox-input:checked + .checkmark i {
  opacity: 1;
}

.checkbox-text {
  color: var(--text-color);
  font-weight: 500;
}

.forgot-password {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: var(--transition);
}

.forgot-password:hover {
  color: var(--primary-dark);
  text-decoration: underline;
}

/* ======================================
 * КНОПКА ВХОДА
 * ====================================== */
.btn-submit {
  width: 100%;
  padding: 1rem 2rem;
  background: var(--gradient-primary);
  color: white;
  border: none;
  border-radius: var(--border-radius);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
  box-shadow: var(--shadow-md);
  position: relative;
  overflow: hidden;
}

.btn-submit::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.btn-submit:hover::before {
  left: 100%;
}

.btn-submit:hover {
  transform: translateY(-2px);
  box-shadow: 0 15px 40px rgba(0, 85, 179, 0.4);
}

.btn-submit:active {
  transform: translateY(0);
}

.btn-submit:disabled {
  background: linear-gradient(135deg, #a0a0a0, #c0c0c0);
  cursor: not-allowed;
  transform: none;
  box-shadow: var(--shadow-sm);
}

.loading-content,
.submit-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
}

.loading-content i {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* ======================================
 * СООБЩЕНИЕ ОБ ОШИБКЕ
 * ====================================== */
.error-message {
  background: linear-gradient(135deg, rgba(230, 41, 77, 0.1), rgba(230, 41, 77, 0.05));
  color: var(--error-color);
  padding: 1rem;
  border-radius: var(--border-radius);
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
  border: 1px solid rgba(230, 41, 77, 0.2);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 500;
}

.error-message i {
  font-size: 1.1rem;
}

/* ======================================
 * ССЫЛКИ РЕГИСТРАЦИИ
 * ====================================== */
.auth-links {
  text-align: center;
  margin-top: 2rem;
}

.divider {
  position: relative;
  margin: 1.5rem 0;
  text-align: center;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(to right, transparent, var(--text-light), transparent);
  opacity: 0.3;
}

.divider span {
  background: var(--background-color);
  padding: 0 1rem;
  color: var(--text-light);
  font-size: 0.85rem;
  font-weight: 500;
}

.register-text {
  color: var(--text-color);
  font-size: 0.95rem;
  margin: 0;
}

.register-link {
  color: var(--accent-color);
  text-decoration: none;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: var(--transition);
  margin-left: 0.5rem;
}

.register-link:hover {
  color: var(--accent-light);
  text-decoration: underline;
  transform: translateX(2px);
}

/* ======================================
 * АДАПТИВНОСТЬ
 * ====================================== */
@media (max-width: 768px) {
  .auth-page {
    padding: 0.5rem;
  }

  .auth-container {
    max-width: 100%;
    max-height: calc(100vh - 1rem);
    padding: 2rem;
  }

  .brand-name {
    font-size: 1.8rem;
  }

  .form-header h2 {
    font-size: 1.5rem;
  }
}

@media (max-width: 480px) {
  .auth-page {
    padding: 0.25rem;
  }

  .auth-container {
    max-height: calc(100vh - 0.5rem);
    padding: 1.5rem;
    border-radius: 8px;
  }

  .auth-logo {
    margin-bottom: 1.5rem;
  }

  .logo-img {
    width: 60px;
    height: 60px;
  }

  .brand-name {
    font-size: 1.6rem;
  }

  .brand-subtitle {
    font-size: 0.8rem;
  }

  .form-header {
    margin-bottom: 1.5rem;
  }

  .form-header h2 {
    font-size: 1.4rem;
  }

  .form-group {
    margin-bottom: 1.5rem;
  }

  .form-options {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
    margin-bottom: 1.5rem;
  }

  .auth-links {
    margin-top: 1.5rem;
  }

  .shape {
    display: none;
  }
}

@media (max-width: 360px) {
  .auth-page {
    padding: 0.125rem;
  }

  .auth-container {
    max-height: calc(100vh - 0.25rem);
    padding: 1rem;
  }

  .auth-logo {
    margin-bottom: 1rem;
  }

  .logo-img {
    width: 50px;
    height: 50px;
  }

  .brand-name {
    font-size: 1.4rem;
  }

  .form-header h2 {
    font-size: 1.2rem;
  }

  .form-input {
    padding: 0.875rem 0.875rem 0.875rem 2.5rem;
  }

  .floating-label {
    left: 2.5rem;
  }

  .input-icon {
    left: 0.75rem;
  }

  .form-group {
    margin-bottom: 1.25rem;
  }
}

/* ======================================
 * ДОПОЛНИТЕЛЬНЫЕ ОГРАНИЧЕНИЯ ВЫСОТЫ
 * ====================================== */
@media (max-height: 600px) {
  .auth-page {
    align-items: flex-start;
    padding-top: 1rem;
  }

  .auth-container {
    margin-top: 0;
  }

  .auth-logo {
    margin-bottom: 1rem;
  }

  .logo-img {
    width: 50px;
    height: 50px;
  }

  .brand-name {
    font-size: 1.5rem;
  }

  .brand-subtitle {
    font-size: 0.8rem;
  }

  .form-header {
    margin-bottom: 1rem;
  }

  .form-header h2 {
    font-size: 1.3rem;
  }

  .form-group {
    margin-bottom: 1rem;
  }
}

@media (max-height: 500px) {
  .auth-container {
    padding: 1rem;
  }

  .auth-logo {
    margin-bottom: 0.5rem;
  }

  .logo-img {
    width: 40px;
    height: 40px;
  }

  .brand-name {
    font-size: 1.2rem;
    margin: 0.25rem 0;
  }

  .brand-subtitle {
    display: none;
  }

  .form-header {
    margin-bottom: 0.5rem;
  }

  .form-header h2 {
    font-size: 1.1rem;
    margin-bottom: 0.25rem;
  }

  .form-header p {
    font-size: 0.8rem;
  }

  .form-group {
    margin-bottom: 0.75rem;
  }

  .form-options {
    margin-bottom: 1rem;
  }

  .auth-links {
    margin-top: 1rem;
  }

  .divider {
    margin: 0.75rem 0;
  }
}
</style>