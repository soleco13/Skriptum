# Система уведомлений Skriptum

## Обзор

Реализована полнофункциональная система уведомлений для системы управления документами Skriptum с поддержкой real-time уведомлений через WebSocket и in-app уведомлений.

## Архитектура

### Бэкенд (Django + Django Channels)
- **Модель Notification** - хранение уведомлений в БД
- **Django Signals** - автоматическое создание уведомлений при событиях
- **Django Channels** - real-time доставка через WebSocket
- **REST API** - CRUD операции с уведомлениями
- **Memurai** - Redis-совместимый брокер сообщений

### Фронтенд (Vue.js 3)
- **NotificationBell** - компонент колокольчика уведомлений
- **WebSocket Service** - подключение к real-time уведомлениям
- **Toast Notifications** - всплывающие уведомления
- **Notifications Page** - страница управления уведомлениями

## Установка и настройка

### 1. Бэкенд настройка

#### Установка зависимостей
```bash
pip install channels channels-redis redis
```

#### Настройка Django Channels
В `settings.py` уже настроено:
```python
INSTALLED_APPS = [
    'channels',
    # ... другие приложения
]

ASGI_APPLICATION = 'dip.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
            "capacity": 1000,
            "expiry": 60,
        },
    },
}
```

#### Применение миграций
```bash
python manage.py migrate
```

#### Запуск сервера
```bash
python manage.py runserver
# В отдельном терминале для WebSocket:
daphne -b 0.0.0.0 -p 8000 dip.asgi:application
```

### 2. Настройка Memurai (Redis)

1. Скачайте и установите Memurai с официального сайта
2. Запустите Memurai (по умолчанию работает на порту 6379)
3. Убедитесь, что Memurai запущен: `redis-cli ping` должен вернуть `PONG`

### 3. Фронтенд настройка

#### Установка зависимостей
```bash
cd front
npm install vue-toastification@next
```

#### Настройка WebSocket
В `src/api/notifications.js` проверьте URL:
```javascript
const wsUrl = `ws://${config.BASE_URL.replace('http://', '')}/ws/notifications/?token=${token}`;
```

#### Запуск фронтенда
```bash
npm run serve
```

## Использование

### 1. Автоматические уведомления

Система автоматически создает уведомления при:
- Создании/обновлении документов
- Создании/обновлении задач
- Создании/обновлении процессов
- Создании/обновлении BPMN диаграмм

### 2. API эндпоинты

#### Получение уведомлений
```http
GET /api/notifications/
Authorization: Bearer <token>
```

#### Пометка как прочитанное
```http
PATCH /api/notifications/{id}/mark_as_read/
Authorization: Bearer <token>
```

#### Пометка всех как прочитанных
```http
PATCH /api/notifications/mark_all_as_read/
Authorization: Bearer <token>
```

#### Количество непрочитанных
```http
GET /api/notifications/unread_count/
Authorization: Bearer <token>
```

### 3. WebSocket подключение

```javascript
import notificationService from '@/api/notifications';

// Подключение
const token = localStorage.getItem('access_token');
notificationService.connect(token);

// Подписка на события
notificationService.on('new_notification', (notification) => {
  console.log('Новое уведомление:', notification);
});

notificationService.on('unread_count', (count) => {
  console.log('Непрочитанных:', count);
});
```

### 4. Компоненты Vue

#### NotificationBell
```vue
<template>
  <NotificationBell />
</template>

<script>
import NotificationBell from '@/components/NotificationBell.vue';

export default {
  components: { NotificationBell }
}
</script>
```

#### Страница уведомлений
```vue
<template>
  <router-view name="Notifications" />
</template>
```

## Типы уведомлений

- **info** - Информационные (синий)
- **warning** - Предупреждения (желтый)
- **task** - Задачи (синий)
- **document** - Документы (зеленый)
- **process** - Процессы (серый)

## Настройка уведомлений

### Создание кастомного уведомления

```python
from myapp.models import create_notification

# Создание уведомления
create_notification(
    user=user,
    message="Кастомное сообщение",
    notification_type='info',
    link="/custom-page/",
    document=document  # опционально
)
```

### Настройка сигналов

В `models.py` можно добавить новые сигналы:

```python
@receiver(post_save, sender=YourModel)
def your_model_notification(sender, instance, created, **kwargs):
    # Логика создания уведомления
    pass
```

## Отладка

### Проверка WebSocket подключения
1. Откройте DevTools в браузере
2. Перейдите на вкладку Network → WS
3. Убедитесь, что есть активное WebSocket соединение

### Проверка Memurai
```bash
redis-cli
> KEYS *
> GET notifications_1
```

### Логи Django
```bash
# В логах должны быть сообщения:
# "WebSocket подключение для уведомлений"
# "Создано уведомление для пользователя"
```

## Производительность

### Оптимизации
- Индексы на поля `user`, `is_read`, `created_at`
- Пагинация уведомлений (20 на страницу)
- Автоочистка старых уведомлений (можно добавить задачу)
- Кэширование счетчика непрочитанных

### Мониторинг
- Количество активных WebSocket соединений
- Размер очереди уведомлений в Memurai
- Время отклика API уведомлений

## Безопасность

- Аутентификация через JWT токены
- Фильтрация уведомлений по пользователю
- Валидация WebSocket соединений
- Защита от спама уведомлений

## Расширение функциональности

### Возможные улучшения
1. Email уведомления
2. Push уведомления в браузере
3. Мобильные push уведомления
4. Группировка уведомлений
5. Настройки пользователя (отключение типов уведомлений)
6. Шаблоны уведомлений
7. Уведомления по расписанию

### Добавление новых типов уведомлений
1. Добавьте тип в `NOTIFICATION_TYPES` в модели
2. Обновите иконки и цвета в методах `get_icon()` и `get_color()`
3. Добавьте соответствующие сигналы
4. Обновите фронтенд компоненты

## Поддержка

При возникновении проблем проверьте:
1. Запущен ли Memurai
2. Корректность JWT токенов
3. Настройки CORS
4. Логи Django и браузера
5. Сетевое подключение между фронтендом и бэкендом
