<template>
  <div class="landing" :class="{ 'dark-mode': darkMode }">
    <!-- Индикатор прогресса скролла -->
    <div class="scroll-progress-bar" ref="scrollProgressBar"></div>
    
    <!-- Плавающие элементы декора (по всей странице) -->
    <div class="floating-elements">
      <div class="floating-element" v-for="n in 5" :key="n"></div>
    </div>

    <!-- Навигация с эффектом прозрачности -->
    <nav class="landing-nav" :class="{ 'scrolled': scrolled }">
      <div class="nav-logo">
        <div class="logo-animation">
          <img src="@/assets/logo.png" alt="Skriptum" class="logo-img">
        </div>
        <span class="logo-text">Skriptum</span>
      </div>
      <div class="nav-links desktop-nav">
        <a href="#features" class="nav-link">Возможности</a>
        <a href="#benefits" class="nav-link">Преимущества</a>
        <a href="#contact" class="nav-link">Контакты</a>
        <router-link to="/dashboard" class="btn-login">Войти в систему</router-link>
      </div>
      <div class="theme-toggle" @click="toggleDarkMode">
        <div class="toggle-icon">
          <i :class="darkMode ? 'fas fa-sun' : 'fas fa-moon'"></i>
        </div>
      </div>
      <div class="mobile-menu-toggle" @click="toggleMobileMenu">
        <div class="hamburger" :class="{ 'active': mobileMenuOpen }">
          <span></span><span></span><span></span>
        </div>
      </div>
    </nav>

    <!-- Мобильное меню -->
    <div class="mobile-menu" :class="{ 'open': mobileMenuOpen }">
      <a href="#features" class="mobile-link" @click="closeMobileMenu">Возможности</a>
      <a href="#benefits" class="mobile-link" @click="closeMobileMenu">Преимущества</a>
      <a href="#contact" class="mobile-link" @click="closeMobileMenu">Контакты</a>
      <router-link to="/dashboard" class="mobile-link highlight" @click="closeMobileMenu">Войти в систему</router-link>
    </div>

    <!-- Главный экран с 3D-элементами и параллаксом -->
    <section class="hero" ref="heroSection">
      <div class="hero-backdrop"></div>
      <div class="hero-particles" ref="particles"></div>
      <div class="hero-content" ref="heroContent">
        <h1 class="animated-heading">
          <span class="line">Документооборот</span>
          <span class="line accent">на новом уровне</span>
        </h1>
        <p class="hero-description">Автоматизируйте процессы, управляйте документами и 
           увеличивайте эффективность вашей компании на <span class="accent-text counter-inline" data-target="300">0</span>%</p>
        <div class="hero-cta">
          <router-link to="/dashboard" class="btn-primary pulse-effect">
            Начать бесплатно
            <span class="btn-shine"></span>
          </router-link>
          <a href="#how-it-works" class="btn-secondary">
            <i class="fas fa-play-circle"></i> Как это работает
          </a>
        </div>
        
        <!-- Плавающие статистические плашки -->
        <div class="stats-cards">
          <div class="stat-card" v-for="(stat, index) in stats" :key="index"
               :class="{ 'appear': true }" :style="{ animationDelay: (index*0.2)+'s' }">
            <div class="stat-icon"><i :class="stat.icon"></i></div>
            <div class="stat-number"><span class="counter" :data-target="stat.value">0</span>{{stat.suffix}}</div>
            <div class="stat-label">{{stat.label}}</div>
          </div>
        </div>
      </div>
      <div class="hero-visual" ref="heroVisual">
        <div class="mockup-container">
          <div class="mockup-screen">
            <div class="screen-content">
              <img src="@/assets/interface.png">
              <!-- Анимированная демонстрация интерфейса -->
              <div class="interface-demo">
                <div class="demo-header"></div>
                <div class="demo-sidebar"></div>
                <div class="demo-content">
                  <div class="demo-card"></div>
                  <div class="demo-card"></div>
                  <div class="demo-card"></div>
                </div>
              </div>
            </div>
            <div class="screen-glare"></div>
          </div>
          <div class="mockup-base"></div>
        </div>
        <div class="floating-elements mockup-decoration">
          <div class="floating-icon document"><i class="fas fa-file-alt"></i></div>
          <div class="floating-icon chart"><i class="fas fa-chart-line"></i></div>
          <div class="floating-icon task"><i class="fas fa-tasks"></i></div>
          <div class="floating-icon process"><i class="fas fa-project-diagram"></i></div>
        </div>
      </div>
      
      <!-- Подсказка для скролла -->
      <div class="scroll-down-indicator">
        <div class="mouse">
          <div class="wheel"></div>
        </div>
        <div class="arrows">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </section>

    <!-- Возможности с эффектом стекломорфизма -->
    <section id="features" class="features">
      <div class="section-heading-container">
        <h2 class="section-heading reveal-text">Ключевые возможности</h2>
        <p class="section-subheading">Всё необходимое для эффективной работы компании</p>
      </div>
      
      <!-- Интерактивные карточки с эффектами -->
      <div class="features-grid">
        <div class="feature-card interactive-card" 
             v-for="(feature, index) in features" 
             :key="index"
             @mousemove="handleCardMove"
             @mouseleave="resetCardPosition">
          <div class="card-content">
            <div class="feature-icon">
              <i :class="feature.icon"></i>
            </div>
            <h3>{{feature.title}}</h3>
            <p>{{feature.description}}</p>
            <a href="#" class="feature-link">Подробнее <i class="fas fa-arrow-right"></i></a>
          </div>
          <div class="card-highlight"></div>
        </div>
      </div>
      
      <!-- Выделенная особенность -->
      <div class="featured-highlight">
        <div class="highlight-content">
          <h3>Специальное предложение</h3>
          <p>Первый месяц использования системы бесплатно при регистрации до 15 апреля 2025</p>
          <div class="countdown">
            <div class="countdown-item">
              <span class="countdown-value">15</span>
              <span class="countdown-label">дней</span>
            </div>
            <div class="countdown-item">
              <span class="countdown-value">20</span>
              <span class="countdown-label">часов</span>
            </div>
            <div class="countdown-item">
              <span class="countdown-value">45</span>
              <span class="countdown-label">минут</span>
            </div>
          </div>
          <router-link to="/dashboard" class="btn-accent">Активировать</router-link>
        </div>
        <div class="highlight-decoration">
          <div class="orbit">
            <div class="planet"></div>
            <div class="satellite"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- Секция "Как это работает" с временной шкалой -->
    <section id="how-it-works" class="how-it-works">
      <div class="section-heading-container">
        <h2 class="section-heading reveal-text">Как это работает</h2>
        <p class="section-subheading">Всего 4 простых шага для старта</p>
      </div>
      
      <!-- Интерактивная временная шкала -->
      <div class="timeline">
        <div class="timeline-item" 
             v-for="(step, index) in howItWorks" 
             :key="index"
             @mouseenter="activateTimelineItem($event)"
             @mouseleave="deactivateTimelineItem($event)">
          <div class="timeline-number">{{index + 1}}</div>
          <div class="timeline-content">
            <h3>{{step.title}}</h3>
            <p>{{step.description}}</p>
            <div class="timeline-icon"><i :class="step.icon"></i></div>
          </div>
        </div>
      </div>
    </section>

    <!-- Преимущества с 3D-эффектами -->
    <section id="benefits" class="benefits">
      <div class="benefits-bg"></div>
      <div class="section-heading-container">
        <h2 class="section-heading reveal-text">Почему Skriptum?</h2>
        <p class="section-subheading">Преимущества, которые выделяют нас среди конкурентов</p>
      </div>
      
      <!-- 3D карточки с эффектами -->
      <div class="benefits-container">
        <div class="benefit-item morph-card" 
             v-for="(benefit, index) in benefits" 
             :key="index"
             @mousemove="handleMorphMove"
             @mouseleave="resetMorphCard">
          <div class="benefit-number">0{{index + 1}}</div>
          <div class="benefit-content">
            <h3>{{benefit.title}}</h3>
            <p>{{benefit.description}}</p>
          </div>
          <div class="benefit-icon">
            <i :class="benefit.icon"></i>
          </div>
          <div class="benefit-particles"></div>
        </div>
      </div>
      
      <!-- Интерактивная сравнительная таблица -->
      <div class="comparison-section">
        <h3 class="comparison-title">Сравнение с конкурентами</h3>
        <div class="comparison-table">
          <div class="comparison-header">
            <div class="comparison-cell header-product">Функциональность</div>
            <div class="comparison-cell header-highlight">Skriptum</div>
            <div class="comparison-cell">Конкурент А</div>
            <div class="comparison-cell">Конкурент Б</div>
          </div>
          <div class="comparison-row" v-for="(row, index) in comparisonData" :key="index">
            <div class="comparison-cell">{{row.feature}}</div>
            <div class="comparison-cell highlight-cell">
              <i class="fas fa-check-circle" v-if="row.skriptum"></i>
              <i class="fas fa-times-circle" v-else></i>
            </div>
            <div class="comparison-cell">
              <i class="fas fa-check-circle" v-if="row.competitorA"></i>
              <i class="fas fa-times-circle" v-else></i>
            </div>
            <div class="comparison-cell">
              <i class="fas fa-check-circle" v-if="row.competitorB"></i>
              <i class="fas fa-times-circle" v-else></i>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Призыв к действию (CTA) -->
    <section class="cta-section">
      <div class="cta-content">
        <h2>Готовы оптимизировать работу вашей компании?</h2>
        <p>Присоединяйтесь к 1500+ организаций, которые уже используют Skriptum</p>
        <div class="cta-buttons">
          <router-link to="/dashboard" class="btn-primary pulse-effect">
            Начать бесплатно
            <span class="btn-shine"></span>
          </router-link>
          <a href="#contact" class="btn-secondary">Связаться с нами</a>
        </div>
        
        <!-- Интерактивная подсказка -->
        <div class="cta-features">
          <div class="feature-tag" v-for="(tag, index) in ctaTags" :key="index">
            <i :class="tag.icon"></i> {{tag.text}}
          </div>
        </div>
      </div>
      <div class="cta-decoration"></div>
    </section>

    <!-- Контакты с неоморфной формой -->
    <section id="contact" class="contact">
      <div class="section-heading-container">
        <h2 class="section-heading reveal-text">Свяжитесь с нами</h2>
        <p class="section-subheading">Ответим на ваши вопросы и организуем демонстрацию</p>
      </div>
      <div class="contact-container">
        <div class="contact-info">
          <h3>Мы на связи</h3>
          <p>Наши консультанты готовы помочь вам выбрать оптимальное решение для вашего бизнеса</p>
          <div class="contact-methods">
            <div class="contact-method ripple-effect">
              <div class="method-icon"><i class="fas fa-envelope"></i></div>
              <div class="method-details">
                <h4>Email</h4>
                <p>info@skriptum.ru</p>
              </div>
            </div>
            <div class="contact-method ripple-effect">
              <div class="method-icon"><i class="fas fa-phone"></i></div>
              <div class="method-details">
                <h4>Телефон</h4>
                <p>+7 (XXX) XXX-XX-XX</p>
              </div>
            </div>
            <div class="contact-method ripple-effect">
              <div class="method-icon"><i class="fas fa-map-marker-alt"></i></div>
              <div class="method-details">
                <h4>Адрес</h4>
                <p>г. Москва, ул. Примерная, 123</p>
              </div>
            </div>
          </div>
          <div class="social-links">
            <a href="#" class="social-link hover-float"><i class="fab fa-facebook-f"></i></a>
            <a href="#" class="social-link hover-float"><i class="fab fa-twitter"></i></a>
            <a href="#" class="social-link hover-float"><i class="fab fa-linkedin-in"></i></a>
            <a href="#" class="social-link hover-float"><i class="fab fa-instagram"></i></a>
          </div>
        </div>
        <form class="contact-form" @submit.prevent="submitForm">
          <div class="form-group">
            <label for="name">Ваше имя</label>
            <input type="text" id="name" class="neomorphic-input" placeholder="Введите ваше имя" 
                  v-model="formData.name" :class="{ 'input-filled': formData.name }">
            <span class="input-status" v-if="formData.name"><i class="fas fa-check"></i></span>
          </div>
          <div class="form-group">
            <label for="email">Email</label>
            <input type="email" id="email" class="neomorphic-input" placeholder="Введите ваш email" 
                  v-model="formData.email" :class="{ 'input-filled': formData.email }">
            <span class="input-status" v-if="formData.email"><i class="fas fa-check"></i></span>
          </div>
          <div class="form-group">
            <label for="phone">Телефон</label>
            <input type="tel" id="phone" class="neomorphic-input" placeholder="Введите ваш телефон" 
                  v-model="formData.phone" :class="{ 'input-filled': formData.phone }">
            <span class="input-status" v-if="formData.phone"><i class="fas fa-check"></i></span>
          </div>
          <div class="form-group">
            <label for="message">Сообщение</label>
            <textarea id="message" class="neomorphic-input" placeholder="Ваше сообщение" 
                     v-model="formData.message" :class="{ 'input-filled': formData.message }"></textarea>
            <span class="input-status message-status" v-if="formData.message"><i class="fas fa-check"></i></span>
          </div>
          <button type="submit" class="btn-primary submit-btn" :class="{ 'button-ready': isFormValid }">
            <span class="btn-text">Отправить сообщение</span>
            <span class="btn-icon"><i class="fas fa-paper-plane"></i></span>
            <span class="btn-loader" v-if="isSubmitting">
              <i class="fas fa-circle-notch fa-spin"></i>
            </span>
          </button>
          <div class="form-success" v-if="formSubmitted">
            <i class="fas fa-check-circle"></i>
            <p>Ваше сообщение успешно отправлено! Мы свяжемся с вами в ближайшее время.</p>
          </div>
        </form>
      </div>
    </section>

    <!-- Футер с современным дизайном -->
    <footer class="landing-footer">
      <div class="footer-wave"></div>
      <div class="footer-content">
        <div class="footer-main">
          <div class="footer-logo">
            <img src="@/assets/logo.png" alt="Skriptum" class="logo-img">
            <span>Skriptum</span>
          </div>
          <p class="footer-description">Современная система документооборота для бизнеса любого масштаба</p>
          <div class="social-links">
            <a href="#" class="social-link hover-float"><i class="fab fa-facebook-f"></i></a>
            <a href="#" class="social-link hover-float"><i class="fab fa-twitter"></i></a>
            <a href="#" class="social-link hover-float"><i class="fab fa-linkedin-in"></i></a>
            <a href="#" class="social-link hover-float"><i class="fab fa-instagram"></i></a>
          </div>
        </div>
        <div class="footer-links">
          <div class="footer-column">
            <h4>Продукт</h4>
            <a href="#features" class="hover-effect">Возможности</a>
            <a href="#" class="hover-effect">Интеграции</a>
            <a href="#" class="hover-effect">Цены</a>
            <a href="#" class="hover-effect">Демо</a>
          </div>
          <div class="footer-column">
            <h4>Ресурсы</h4>
            <a href="#" class="hover-effect">Документация</a>
            <a href="#" class="hover-effect">Обучение</a>
            <a href="#" class="hover-effect">Блог</a>
            <a href="#" class="hover-effect">Кейсы</a>
          </div>
          <div class="footer-column">
            <h4>Компания</h4>
            <a href="#" class="hover-effect">О нас</a>
            <a href="#" class="hover-effect">Команда</a>
            <a href="#" class="hover-effect">Карьера</a>
            <a href="#contact" class="hover-effect">Контакты</a>
          </div>
          <div class="footer-column">
            <h4>Поддержка</h4>
            <a href="#" class="hover-effect">Центр помощи</a>
            <a href="#" class="hover-effect">FAQ</a>
            <a href="#" class="hover-effect">Сообщить о проблеме</a>
            <a href="#contact" class="hover-effect">Связаться с нами</a>
          </div>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; 2025 Skriptum. Все права защищены.</p>
        <div class="footer-legal">
          <a href="#" class="hover-effect">Условия использования</a>
          <a href="#" class="hover-effect">Политика конфиденциальности</a>
          <a href="#" class="hover-effect">Cookies</a>
        </div>
      </div>
      
      <!-- Кнопка "наверх" -->
      <div class="back-to-top" @click="scrollToTop" :class="{ 'visible': showBackToTop }">
        <i class="fas fa-chevron-up"></i>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'LandingPage',
  data() {
    return {
      darkMode: false,
      scrolled: false,
      mobileMenuOpen: false,
      showBackToTop: false,
      isSubmitting: false,
      formSubmitted: false,
      formData: {
        name: '',
        email: '',
        phone: '',
        message: ''
      },
      stats: [
        { icon: 'fas fa-rocket', value: 1500, suffix: '+', label: 'довольных клиентов' },
        { icon: 'fas fa-star', value: 98, suffix: '%', label: 'уровень удовлетворенности' },
        { icon: 'fas fa-bolt', value: 5, suffix: ' мин', label: 'скорость настройки' }
      ],
      features: [
        {
          icon: 'fas fa-file-alt',
          title: 'Управление документами',
          description: 'Создавайте, редактируйте и согласовывайте документы с контролем версий и защитой от ошибок'
        },
        {
          icon: 'fas fa-tasks',
          title: 'Управление задачами',
          description: 'Планируйте задачи, распределяйте ответственность и контролируйте исполнение в одной системе'
        },
        {
          icon: 'fas fa-project-diagram',
          title: 'Бизнес-процессы',
          description: 'Настраивайте и автоматизируйте любые рабочие процессы без программирования'
        },
        {
          icon: 'fas fa-chart-line',
          title: 'Аналитика и отчеты',
          description: 'Получайте наглядную аналитику по всем процессам компании в реальном времени'
        },
        {
          icon: 'fas fa-users',
          title: 'Коллаборация',
          description: 'Работайте над документами вместе с коллегами в режиме реального времени'
        }
      ],
      howItWorks: [
        {
          title: 'Регистрация',
          description: 'Создайте аккаунт за 30 секунд, укажите название компании и количество сотрудников',
          icon: 'fas fa-user-plus'
        },
        {
          title: 'Настройка',
          description: 'Импортируйте данные или начните с нуля, настройте структуру компании и основные процессы',
          icon: 'fas fa-cogs'
        },
        {
          title: 'Обучение',
          description: 'Пройдите короткое интерактивное обучение или получите персональную демонстрацию',
          icon: 'fas fa-graduation-cap'
        },
        {
          title: 'Внедрение',
          description: 'Пригласите коллег и начните работу. Наша поддержка доступна 24/7 при возникновении вопросов',
          icon: 'fas fa-rocket'
        }
      ],
      benefits: [
        {
          title: 'Простота использования',
          description: 'Интуитивно понятный интерфейс не требует специального обучения — сотрудники начинают работать сразу',
          icon: 'fas fa-hand-point-up'
        },
        {
          title: 'Безопасность',
          description: 'Надежная защита данных, шифрование и гибкое управление доступом к информации',
          icon: 'fas fa-shield-alt'
        },
        {
          title: 'Масштабируемость',
          description: 'Система растет вместе с вами — от небольшого стартапа до крупной корпорации',
          icon: 'fas fa-expand-arrows-alt'
        },
        {
          title: 'Поддержка 24/7',
          description: 'Персональный менеджер и быстрая техническая поддержка помогут решить любые вопросы',
          icon: 'fas fa-headset'
        }
      ],
      ctaTags: [
        { icon: 'fas fa-check', text: 'Бесплатная демонстрация' },
        { icon: 'fas fa-check', text: 'Персональный менеджер' },
        { icon: 'fas fa-check', text: 'Техническая поддержка 24/7' },
        { icon: 'fas fa-check', text: 'Регулярные обновления' },
      ],
      comparisonData: [
        { feature: 'Электронная подпись', skriptum: true, competitorA: true, competitorB: false },
        { feature: 'Контроль версий', skriptum: true, competitorA: true, competitorB: true },
        { feature: 'Автоматизация процессов', skriptum: true, competitorA: false, competitorB: false },
        { feature: 'Аналитика и отчеты', skriptum: true, competitorA: false, competitorB: true },
        { feature: 'Мобильное приложение', skriptum: true, competitorA: false, competitorB: false },
        { feature: 'API интеграция', skriptum: true, competitorA: true, competitorB: false },
      ],
    }
  },
  computed: {
    isFormValid() {
      return this.formData.name && this.formData.email && this.formData.phone && this.formData.message;
    }
  },
  mounted() {
    window.addEventListener('scroll', this.handleScroll);
    this.initAnimations();
    this.initParticles();
    
    // Добавляем эффект параллакса при движении мышью
    document.addEventListener('mousemove', this.parallaxEffect);
  },
  beforeUnmount() {
    window.removeEventListener('scroll', this.handleScroll);
    document.removeEventListener('mousemove', this.parallaxEffect);
  },
  methods: {
    toggleDarkMode() {
      this.darkMode = !this.darkMode;
    },
    handleScroll() {
      this.scrolled = window.scrollY > 50;
      this.showBackToTop = window.scrollY > 500;
      this.animateOnScroll();
      this.updateScrollProgress();
    },
    updateScrollProgress() {
      const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
      const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
      const scrolled = (winScroll / height) * 100;
      if (this.$refs.scrollProgressBar) {
        this.$refs.scrollProgressBar.style.width = scrolled + "%";
      }
    },
    toggleMobileMenu() {
      this.mobileMenuOpen = !this.mobileMenuOpen;
    },
    closeMobileMenu() {
      this.mobileMenuOpen = false;
    },
    scrollToTop() {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    },
    submitForm() {
      if (!this.isFormValid) return;
      
      this.isSubmitting = true;
      
      // Имитация отправки формы
      setTimeout(() => {
        this.isSubmitting = false;
        this.formSubmitted = true;
        
        // Сброс формы через некоторое время
        setTimeout(() => {
          this.formData = {
            name: '',
            email: '',
            phone: '',
            message: ''
          };
          this.formSubmitted = false;
        }, 5000);
      }, 1500);
    },
    initAnimations() {
      // Обработка счетчиков
      const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px'
      };
      
      const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            this.animateCounter(entry.target);
            counterObserver.unobserve(entry.target);
          }
        });
      }, observerOptions);
      
      // Наблюдаем за всеми счетчиками
      setTimeout(() => {
        document.querySelectorAll('.counter, .counter-inline').forEach(counter => {
          counterObserver.observe(counter);
        });
      }, 500);
      
      // Наблюдаем за элементами для анимации при скролле
      const animationObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
          }
        });
      }, { threshold: 0.1 });
      
      document.querySelectorAll('.reveal-text, .feature-card, .benefit-item, .timeline-item, .stat-card').forEach(el => {
        animationObserver.observe(el);
      });
    },
    animateCounter(counter) {
      const target = parseInt(counter.getAttribute('data-target'));
      const duration = 2000; // 2 секунды
      const increment = target / (duration / 16);
      let current = 0;
      
      const updateCounter = () => {
        current += increment;
        if (current >= target) {
          counter.textContent = target;
        } else {
          counter.textContent = Math.floor(current);
          requestAnimationFrame(updateCounter);
        }
      };
      
      updateCounter();
    },
    animateOnScroll() {
      // Анимация при скролле для различных элементов
      document.querySelectorAll('.feature-card, .benefit-item, .timeline-item').forEach(el => {
        const rect = el.getBoundingClientRect();
        const windowHeight = window.innerHeight;
        
        if (rect.top <= windowHeight * 0.8) {
          el.classList.add('animate-in');
        }
      });
    },
    parallaxEffect(e) {
      // Применяем параллакс-эффект для героя
      if (this.$refs.heroContent && this.$refs.heroVisual) {
        const moveX = (e.clientX - window.innerWidth / 2) / 50;
        const moveY = (e.clientY - window.innerHeight / 2) / 50;
        
        this.$refs.heroContent.style.transform = `translate(${moveX * -1}px, ${moveY * -1}px)`;
        this.$refs.heroVisual.style.transform = `translate(${moveX}px, ${moveY}px)`;
      }
    },
    initParticles() {
      // Инициализация частиц в фоне героя (упрощенная версия)
      if (!this.$refs.particles) return;
      
      for (let i = 0; i < 30; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = `${Math.random() * 100}%`;
        particle.style.top = `${Math.random() * 100}%`;
        particle.style.animationDelay = `${Math.random() * 5}s`;
        particle.style.width = particle.style.height = `${Math.random() * 10 + 5}px`;
        this.$refs.particles.appendChild(particle);
      }
    },
    handleCardMove(e) {
      const card = e.currentTarget;
      const cardRect = card.getBoundingClientRect();
      const x = e.clientX - cardRect.left;
      const y = e.clientY - cardRect.top;
      
      const centerX = cardRect.width / 2;
      const centerY = cardRect.height / 2;
      
      const rotateX = (y - centerY) / 10;
      const rotateY = (centerX - x) / 10;
      
      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
      
      // Перемещаем подсветку
      const highlight = card.querySelector('.card-highlight');
      highlight.style.opacity = 0.2;
      highlight.style.top = `${y}px`;
      highlight.style.left = `${x}px`;
    },
    resetCardPosition(e) {
      const card = e.currentTarget;
      card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0)';
      
      const highlight = card.querySelector('.card-highlight');
      highlight.style.opacity = 0;
    },
    handleMorphMove(e) {
      const card = e.currentTarget;
      const cardRect = card.getBoundingClientRect();
      const x = e.clientX - cardRect.left;
      const y = e.clientY - cardRect.top;
      
      const centerX = cardRect.width / 2;
      const centerY = cardRect.height / 2;
      
      // Применяем эффект "выдавливания" при наведении
      const moveX = (x - centerX) / 20;
      const moveY = (y - centerY) / 20;
      
      card.style.transform = `translateX(${moveX}px) translateY(${moveY}px)`;
      
      // Эффект с частицами
      const particles = card.querySelector('.benefit-particles');
      if (particles) {
        particles.style.backgroundPosition = `${x / 5}px ${y / 5}px`;
        particles.style.opacity = 0.2;
      }
    },
    resetMorphCard(e) {
      const card = e.currentTarget;
      card.style.transform = 'translateX(0) translateY(0)';
      
      const particles = card.querySelector('.benefit-particles');
      if (particles) {
        particles.style.opacity = 0;
      }
    },
    activateTimelineItem(e) {
      const item = e.currentTarget;
      item.classList.add('active');
    },
    deactivateTimelineItem(e) {
      const item = e.currentTarget;
      item.classList.remove('active');
    }
  }
}
</script>

<style src="@/assets/landing.css"></style>