// Сервис для работы с аутентификацией
import axios from 'axios';
import { API_BASE_URL } from './config';

// Создаем экземпляр axios с базовым URL
const authAPI = axios.create({
  baseURL: API_BASE_URL
});

// Интерцептор для добавления токена к запросам
authAPI.interceptors.request.use(config => {
  const token = localStorage.getItem('token') || sessionStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `JWT ${token}`;
  }
  return config;
});

// Функции для работы с аутентификацией
export const authService = {
  // Регистрация нового пользователя
  register: async (userData) => {
    try {
      // Исправленный URL для регистрации, без префикса /api/
      const response = await axios.post('http://127.0.0.1:8000/auth/users/', userData);
      return response.data;
    } catch (error) {
      // Улучшенная обработка ошибок
      if (error.response && error.response.data) {
        console.log('Server validation errors:', error.response.data);
        throw error.response.data;
      } else {
        console.error('Registration error:', error);
        throw { message: 'Ошибка соединения с сервером' };
      }
    }
  },

  // Вход в систему
  login: async (username, password) => {
    try {
      // Используем полный URL без префикса /api/, так как эндпоинт находится по пути /auth/
      const response = await axios.post('http://127.0.0.1:8000/auth/jwt/create/', { username, password });
      return response.data;
    } catch (error) {
      throw error.response ? error.response.data : error;
    }
  },

  // Получение данных текущего пользователя
  getMe: async () => {
    try {
      const response = await authAPI.get('/api/users/me/');
      return response.data;
    } catch (error) {
      throw error.response ? error.response.data : error;
    }
  },

  // Обновление профиля пользователя
  updateProfile: async (profileData) => {
    try {
      const response = await authAPI.patch('/api/users/update_profile/', profileData);
      return response.data;
    } catch (error) {
      throw error.response ? error.response.data : error;
    }
  },

  // Обновление данных пользователя
  updateUser: async (userData) => {
    try {
      const response = await authAPI.patch('/api/users/update_me/', userData);
      return response.data;
    } catch (error) {
      throw error.response ? error.response.data : error;
    }
  },

  // Выход из системы (удаление токена)
  logout: () => {
    localStorage.removeItem('token');
    sessionStorage.removeItem('token');
  },

  // Проверка, авторизован ли пользователь
  isAuthenticated: () => {
    return !!(localStorage.getItem('token') || sessionStorage.getItem('token'));
  }
};