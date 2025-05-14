// API сервисы для работы с данными
import axios from 'axios';
import { handleApiError } from './config';
import { API_BASE_URL } from './config';

// Создаем экземпляр axios с базовым URL и интерцептором для добавления токена
const apiClient = axios.create({
  baseURL: API_BASE_URL
});

// Интерцептор для добавления токена к запросам
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token') || sessionStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `JWT ${token}`;
  }
  
  // Добавляем CSRF-токен для запросов к CKEditor
  if (config.url && config.url.includes('ckeditor')) {
    // Получаем CSRF-токен из cookie, если он есть
    const csrfToken = document.cookie.split('; ')
      .find(row => row.startsWith('csrftoken='))
      ?.split('=')[1];
    
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken;
    }
  }
  
  return config;
});

// Сервис для работы с документами
export const DocumentService = {
  // Получение содержимого документа для редактирования
  getContent: async (id) => {
    try {
      const response = await apiClient.get(`/documents/${id}/content/`);
      return response.data;
    } catch (error) {
      return handleApiError(error, {
        id: id,
        name: 'Документ не найден',
        content: '',
        file: null,
        file_type: null
      }, 'Ошибка при получении содержимого документа');
    }
  },
  
  // Обновление содержимого документа
  updateContent: async (id, content, versionName = null) => {
    try {
      const data = { content };
      if (versionName) {
        data.version_name = versionName;
      }
      const response = await apiClient.put(`/documents/${id}/update_content/`, data);
      return response.data;
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при обновлении содержимого документа');
    }
  },
  
  // Получение истории изменений документа
  getHistory: async (id) => {
    try {
      const response = await apiClient.get(`/documents/${id}/history/`);
      return response.data;
    } catch (error) {
      return handleApiError(error, [], 'Ошибка при получении истории документа');
    }
  },
  
  // Восстановление документа из истории
  restoreVersion: async (documentId, historyId) => {
    try {
      const response = await apiClient.post(`/documents/${documentId}/restore/${historyId}/`);
      return response.data;
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при восстановлении версии документа');
    }
  },
  
  // Получение всех документов с опциональными параметрами фильтрации
  getAll: async (params = {}) => {
    try {
      // Формируем URL с параметрами запроса
      let url = '/documents/';
      const queryParams = new URLSearchParams();
      
      // Добавляем параметры фильтрации, если они есть
      if (params.search) queryParams.append('search', params.search);
      if (params.type) queryParams.append('type', params.type);
      if (params.status) queryParams.append('status', params.status);
      
      // Добавляем параметры к URL, если они есть
      const queryString = queryParams.toString();
      if (queryString) url = `${url}?${queryString}`;
      
      // Примечание: Фильтрация по пользователю происходит на стороне сервера
      // на основе токена аутентификации, который передается в заголовке
      
      const response = await apiClient.get(url);
      return response.data;
    } catch (error) {
      // Используем обработчик ошибок с демо-данными в качестве резервных
      return handleApiError(error, [
        {
          id: 1,
          name: 'Договор поставки №123',
          type: 'Договор',
          status: 'approved',
          created: '2025-03-15',
          file: null,
          file_type: null
        },
        {
          id: 2,
          name: 'Отчет за Q1 2025',
          type: 'Отчет',
          status: 'review',
          created: '2025-04-01',
          file: null,
          file_type: null
        },
        {
          id: 3,
          name: 'Счет №456',
          type: 'Счет',
          status: 'draft',
          created: '2025-04-05',
          file: null,
          file_type: null
        }
      ], 'Ошибка при получении документов');
    }
  },
  

  
  // Создание нового документа
  create: async (document) => {
    try {
      const response = await apiClient.post('/documents/', document);
      return response.data;
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при создании документа');
    }
  },
  
  // Создание нового документа с файлом
  createWithFile: async (formData) => {
    try {
      const response = await apiClient.post('/documents/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      return response.data;
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при создании документа с файлом');
    }
  },
  
  // Обновление существующего документа
  update: async (id, document) => {
    try {
      const response = await apiClient.put(`/documents/${id}/`, document);
      return response.data;
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при обновлении документа');
    }
  },
  
  // Обновление существующего документа с файлом
  updateWithFile: async (id, formData) => {
    try {
      const response = await apiClient.put(`/documents/${id}/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      return response.data;
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при обновлении документа с файлом');
    }
  },
  
  // Удаление документа
  delete: async (id) => {
    try {
      await apiClient.delete(`/documents/${id}/`);
      return true;
    } catch (error) {
      return handleApiError(error, false, 'Ошибка при удалении документа');
    }
  }
};

// Сервис для работы с задачами
export const TaskService = {
  // Получение всех задач
  getAll: async () => {
    try {
      const response = await apiClient.get('/tasks/');
      return response.data;
    } catch (error) {
      // Демо-данные при ошибке
      return handleApiError(error, [
        {
          id: 1,
          title: 'Подготовить отчет',
          description: 'Подготовить ежемесячный отчет о проделанной работе',
          priority: 'high',
          status: 'pending',
          deadline: '2025-04-15',
          assignee: 'Иван Петров'
        },
        {
          id: 2,
          title: 'Обновить документацию',
          description: 'Внести изменения в техническую документацию проекта',
          priority: 'medium',
          status: 'in-progress',
          deadline: '2025-04-20',
          assignee: 'Мария Сидорова'
        },
        {
          id: 3,
          title: 'Тестирование модуля',
          description: 'Провести тестирование нового функционала',
          priority: 'low',
          status: 'completed',
          deadline: '2025-04-10',
          assignee: 'Алексей Иванов'
        }
      ], 'Ошибка при получении задач');
    }
  },
  
  // Создание новой задачи
  create: async (task) => {
    try {
      const response = await apiClient.post('/tasks/', task);
      return response.data;
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при создании задачи');
    }
  },
  
  // Обновление существующей задачи
  update: async (id, task) => {
    try {
      const response = await apiClient.put(`/tasks/${id}/`, task);
      return response.data;
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при обновлении задачи');
    }
  },
  
  // Удаление задачи
  delete: async (id) => {
    try {
      await apiClient.delete(`/tasks/${id}/`);
      return true;
    } catch (error) {
      return handleApiError(error, false, 'Ошибка при удалении задачи');
    }
  }
};

// Сервис для работы с процессами
export const ProcessService = {
  // Получение всех процессов
  getAll: async () => {
    try {
      const response = await apiClient.get('/processes/');
      return response.data;
    } catch (error) {
      // Демо-данные при ошибке
      return handleApiError(error, [
        {
          id: 1,
          name: 'Разработка нового модуля',
          status: 'active',
          progress: 65,
          participants: 4,
          deadline: '2025-05-15',
          description: 'Разработка и тестирование нового функционала'
        },
        {
          id: 2,
          name: 'Обновление документации',
          status: 'pending',
          progress: 20,
          participants: 2,
          deadline: '2025-04-10',
          description: 'Доработка технической документации'
        },
        {
          id: 3,
          name: 'Интеграция с внешней системой',
          status: 'completed',
          progress: 100,
          participants: 3,
          deadline: '2025-03-20',
          description: 'Интеграция API с внешним сервисом'
        }
      ], 'Ошибка при получении процессов');
    }
  },
  
  // Создание нового процесса
  create: async (process) => {
    try {
      const response = await apiClient.post('/processes/', process);
      return response.data;
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при создании процесса');
    }
  },
  
  // Обновление существующего процесса
  update: async (id, process) => {
    try {
      const response = await apiClient.put(`/processes/${id}/`, process);
      return response.data;
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при обновлении процесса');
    }
  },
  
  // Удаление процесса
  delete: async (id) => {
    try {
      await apiClient.delete(`/processes/${id}/`);
      return true;
    } catch (error) {
      return handleApiError(error, false, 'Ошибка при удалении процесса');
    }
  }
};

// Сервис для работы с активностями (имитация, т.к. API не реализовано)
export const ActivityService = {
  // Получение недавних активностей на основе других данных
  getRecent: async () => {
    try {
      // Получаем данные из других сервисов для формирования активностей
      const [documents, tasks, processes] = await Promise.all([
        DocumentService.getAll(),
        TaskService.getAll(),
        ProcessService.getAll()
      ]);
      
      // Создаем имитацию активностей на основе полученных данных
      const activities = [];
      
      // Добавляем документы
      documents.slice(0, 2).forEach((doc, index) => {
        activities.push({
          id: `doc-${doc.id}`,
          type: 'document',
          description: `Документ "${doc.name}" ${doc.status === 'approved' ? 'утвержден' : 'на рассмотрении'}`,
          timestamp: new Date(new Date().setDate(new Date().getDate() - index)).toISOString(),
          user: 'Александр С.',
          icon: 'file-alt'
        });
      });
      
      // Добавляем задачи
      tasks.slice(0, 2).forEach((task, index) => {
        activities.push({
          id: `task-${task.id}`,
          type: 'task',
          description: `Задача "${task.title}" ${task.status === 'completed' ? 'завершена' : 'в работе'}`,
          timestamp: new Date(new Date().setDate(new Date().getDate() - index - 1)).toISOString(),
          user: task.assignee,
          icon: 'tasks'
        });
      });
      
      // Добавляем процессы
      processes.slice(0, 2).forEach((proc, index) => {
        activities.push({
          id: `proc-${proc.id}`,
          type: 'process',
          description: `Процесс "${proc.name}" ${proc.status === 'completed' ? 'завершен' : 'активен'}`,
          timestamp: new Date(new Date().setDate(new Date().getDate() - index - 2)).toISOString(),
          user: 'Система',
          icon: 'project-diagram'
        });
      });
      
      // Сортируем по времени (сначала новые)
      return activities.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    } catch (error) {
      // Демо-данные при ошибке
      return handleApiError(error, [
        {
          id: 'act-1',
          type: 'document',
          description: 'Документ "Договор поставки №123" утвержден',
          timestamp: new Date(new Date().setDate(new Date().getDate() - 0)).toISOString(),
          user: 'Александр С.',
          icon: 'file-alt'
        },
        {
          id: 'act-2',
          type: 'task',
          description: 'Задача "Подготовить отчет" в работе',
          timestamp: new Date(new Date().setDate(new Date().getDate() - 1)).toISOString(),
          user: 'Иван Петров',
          icon: 'tasks'
        },
        {
          id: 'act-3',
          type: 'process',
          description: 'Процесс "Разработка нового модуля" активен',
          timestamp: new Date(new Date().setDate(new Date().getDate() - 2)).toISOString(),
          user: 'Система',
          icon: 'project-diagram'
        }
      ], 'Ошибка при получении активностей');
    }
  }
};