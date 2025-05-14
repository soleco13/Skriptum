// Конфигурация API

// Базовый URL для API запросов
export const API_BASE_URL = 'http://127.0.0.1:8000/api';

// Функция для формирования полного URL API
export const getApiUrl = (endpoint) => {
  // Убираем лишние слеши для корректного формирования URL
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.substring(1) : endpoint;
  return `${API_BASE_URL}/${cleanEndpoint}`;
};

// Обработчик ошибок API
export const handleApiError = (error, fallbackData = null, errorMessage = 'Ошибка при выполнении запроса') => {
  console.error(`${errorMessage}:`, error);
  
  // Проверяем наличие ответа от сервера
  if (error.response) {
    // Сервер ответил с кодом ошибки
    console.error('Статус ответа:', error.response.status);
    console.error('Данные ответа:', error.response.data);
  } else if (error.request) {
    // Запрос был сделан, но ответа не получено
    console.error('Нет ответа от сервера');
  } else {
    // Ошибка при настройке запроса
    console.error('Ошибка настройки запроса:', error.message);
  }
  
  // Возвращаем резервные данные, если они предоставлены
  return fallbackData;
};