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
  console.log('API Request - Token found:', !!token);
  console.log('API Request - Method:', config.method?.toUpperCase());
  console.log('API Request - URL:', config.url);
  console.log('API Request - Data:', config.data);
  
  if (token) {
    config.headers.Authorization = `JWT ${token}`;
    console.log('API Request - Authorization header set:', config.headers.Authorization);
  } else {
    console.log('API Request - No token found in storage');
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

// Интерцептор для обработки ответов и ошибок
apiClient.interceptors.response.use(
  response => response,
  error => {
    console.log('API Response Error - Status:', error.response?.status);
    console.log('API Response Error - Data:', error.response?.data);
    console.log('API Response Error - Headers:', error.response?.headers);
    console.log('API Response Error - Config:', error.config);
    
    // Если получили 401, возможно токен истек
    if (error.response?.status === 401) {
      console.log('401 Unauthorized - Token may be expired');
      
      // Очищаем токены
      localStorage.removeItem('token');
      sessionStorage.removeItem('token');
      
      // Перенаправляем на страницу логина, если не находимся на ней
      if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
        console.log('Redirecting to login page');
        window.location.href = '/login';
      }
    }
    
    // Если получили 400, выводим подробности ошибки валидации
    if (error.response?.status === 400) {
      console.log('400 Bad Request - Validation errors:', error.response.data);
    }
    
    return Promise.reject(error);
  }
);

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
  },

  // Методы для работы с доступом к документам
  
  // Получение пользователей с доступом к документу
  getDocumentAccess: async (documentId) => {
    try {
      const response = await apiClient.get(`/document-access/document/${documentId}/`);
      return response.data;
    } catch (error) {
      return handleApiError(error, { owner: null, shared_users: [] }, 'Ошибка при получении списка доступа');
    }
  },

  // Предоставление доступа пользователю
  grantAccess: async (documentId, userId, accessLevel = 'read') => {
    try {
      const response = await apiClient.post('/document-access/', {
        document: documentId,
        user: userId,
        access_level: accessLevel
      });
      return response.data;
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при предоставлении доступа');
    }
  },

  // Обновление уровня доступа
  updateAccess: async (accessId, accessLevel) => {
    try {
      const response = await apiClient.patch(`/document-access/${accessId}/`, {
        access_level: accessLevel
      });
      return response.data;
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при обновлении уровня доступа');
    }
  },

  // Отзыв доступа
  revokeAccess: async (accessId) => {
    try {
      await apiClient.delete(`/document-access/${accessId}/`);
      return { success: true };
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при отзыве доступа');
    }
  },
  
  // Добавление подписи к документу
  addSignature: async (documentId, signatureData) => {
    try {
      const response = await apiClient.post(`/documents/${documentId}/add_signature/`, {
        signature: signatureData
      });
      return response.data;
    } catch (error) {
      return handleApiError(error, {
        success: false,
        message: 'Ошибка при добавлении подписи'
      });
    }
  },
  
  // Добавление электронной печати к документу
  addStamp: async (documentId, stampData, stampInfo) => {
    try {
      const response = await apiClient.post(`/documents/${documentId}/add_stamp/`, {
        stamp: stampData,
        stamp_info: stampInfo
      });
      return response.data;
    } catch (error) {
      return handleApiError(error, {
        success: false,
        message: 'Ошибка при добавлении печати'
      });
    }
  },
  
  // Получение информации о подписи документа
  getSignatureInfo: async (documentId) => {
    try {
      const response = await apiClient.get(`/documents/${documentId}/signature_info/`);
      return response.data;
    } catch (error) {
      return handleApiError(error, {
        has_signature: false
      });
    }
  },
  
  // Получение информации о печати документа
  getStampInfo: async (documentId) => {
    try {
      const response = await apiClient.get(`/documents/${documentId}/stamp_info/`);
      return response.data;
    } catch (error) {
      return handleApiError(error, {
        has_stamp: false
      });
    }
  },
  
  // Получение статуса утверждения документа
  getApprovalStatus: async (documentId) => {
    try {
      const response = await apiClient.get(`/documents/${documentId}/approval_status/`);
      return response.data;
    } catch (error) {
      return handleApiError(error, {
        is_signed: false,
        is_stamped: false,
        is_approved: false,
        status: 'draft'
      });
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

// Сервис для работы с пользователями
export const UserService = {
  // Поиск пользователей
  search: async (query) => {
    try {
      // Если query пустой или undefined, отправляем запрос без параметра для получения случайных пользователей
      const searchQuery = query ? query.trim() : '';
      const response = await apiClient.get(`/users/search/?q=${encodeURIComponent(searchQuery)}`);
      return response.data;
    } catch (error) {
      return handleApiError(error, [], 'Ошибка при поиске пользователей');
    }
  },

  // Получение текущего пользователя
  getCurrentUser: async () => {
    try {
      const response = await apiClient.get('/users/me/');
      return response.data;
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при получении данных пользователя');
    }
  },

  // Статистика профиля
  getProfileStats: async () => {
    try {
      const response = await apiClient.get('/users/profile_stats/');
      return response;
    } catch (error) {
      return handleApiError(error, {}, 'Ошибка при получении статистики профиля');
    }
  },

  // Последняя активность
  getRecentActivity: async () => {
    try {
      const response = await apiClient.get('/users/recent_activity/');
      return response;
    } catch (error) {
      return handleApiError(error, [], 'Ошибка при получении активности');
    }
  },

  // Загрузка аватара
  uploadAvatar: async (formData) => {
    try {
      const response = await apiClient.post('/users/upload_avatar/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      return response;
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при загрузке аватара');
    }
  },

  // Назначение роли пользователю
  assignRole: async (userId, roleId) => {
    try {
      const response = await apiClient.post(`/users/${userId}/assign_role/`, {
        role_id: roleId
      });
      return response;
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при назначении роли');
    }
  },

  // Снятие роли с пользователя
  removeRole: async (userId) => {
    try {
      const response = await apiClient.post(`/users/${userId}/remove_role/`);
      return response;
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при снятии роли');
    }
  },

  // Получение пользователя по ID
  getById: async (userId) => {
    try {
      const response = await apiClient.get(`/users/${userId}/`);
      return response;
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при получении пользователя');
    }
  }
};

// Сервис для работы с ролями
export const RoleService = {
  // Получение всех ролей
  getAll: async () => {
    try {
      const response = await apiClient.get('/roles/');
      return response;
    } catch (error) {
      return handleApiError(error, [], 'Ошибка при получении ролей');
    }
  },

  // Получение роли по ID
  getById: async (id) => {
    try {
      const response = await apiClient.get(`/roles/${id}/`);
      return response;
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при получении роли');
    }
  },

  // Создание новой роли
  create: async (roleData) => {
    try {
      const response = await apiClient.post('/roles/', roleData);
      return response;
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при создании роли');
    }
  },

  // Обновление роли
  update: async (id, roleData) => {
    try {
      const response = await apiClient.patch(`/roles/${id}/`, roleData);
      return response;
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при обновлении роли');
    }
  },

  // Удаление роли
  delete: async (id) => {
    try {
      const response = await apiClient.delete(`/roles/${id}/`);
      return response;
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при удалении роли');
    }
  },

  // Получение доступных ролей для назначения
  getAvailableRoles: async () => {
    try {
      const response = await apiClient.get('/roles/available_roles/');
      return response;
    } catch (error) {
      return handleApiError(error, [], 'Ошибка при получении доступных ролей');
    }
  },

  // Получение пользователей с определенной ролью
  getUsersByRole: async (roleId) => {
    try {
      const response = await apiClient.get(`/roles/${roleId}/users/`);
      return response;
    } catch (error) {
      return handleApiError(error, [], 'Ошибка при получении пользователей роли');
    }
  },

  // Назначение роли пользователю
  assignToUser: async (roleId, userId) => {
    try {
      const response = await apiClient.post(`/roles/${roleId}/assign_to_user/`, {
        user_id: userId
      });
      return response;
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при назначении роли');
    }
  },

  // Получение списка всех разрешений
  getPermissionsList: async () => {
    try {
      const response = await apiClient.get('/roles/permissions_list/');
      return response;
    } catch (error) {
      return handleApiError(error, [], 'Ошибка при получении разрешений');
    }
  },

  // Снятие роли с пользователя
  removeUserFromRole: async (roleId, userId) => {
    try {
      const response = await apiClient.post(`/roles/${roleId}/remove_user/`, {
        user_id: userId
      });
      return response;
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при снятии роли');
    }
  }
};

// Сервис для работы с BPMN диаграммами
export const BpmnService = {
  // Получение всех BPMN диаграмм
  getAll: async () => {
    try {
      const response = await apiClient.get('/bpmn-diagrams/');
      return response.data;
    } catch (error) {
      return handleApiError(error, [], 'Ошибка при получении BPMN диаграмм');
    }
  },

  // Получение конкретной BPMN диаграммы
  getById: async (id) => {
    try {
      const response = await apiClient.get(`/bpmn-diagrams/${id}/`);
      return response.data;
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при получении BPMN диаграммы');
    }
  },

  // Получение BPMN диаграммы по ID процесса
  getByProcessId: async (processId) => {
    try {
      const response = await apiClient.get(`/bpmn-diagrams/by-process/${processId}/`);
      return response.data;
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при получении BPMN диаграммы по процессу');
    }
  },

  // Создание новой BPMN диаграммы
  createDiagram: async (diagramData) => {
    try {
      const response = await apiClient.post('/bpmn-diagrams/', diagramData);
      return response.data;
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при создании BPMN диаграммы');
    }
  },

  // Обновление существующей BPMN диаграммы
  updateDiagram: async (id, diagramData) => {
    try {
      const response = await apiClient.put(`/bpmn-diagrams/${id}/`, diagramData);
      return response.data;
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при обновлении BPMN диаграммы');
    }
  },

  // Удаление BPMN диаграммы
  deleteDiagram: async (id) => {
    try {
      await apiClient.delete(`/bpmn-diagrams/${id}/`);
      return true;
    } catch (error) {
      return handleApiError(error, false, 'Ошибка при удалении BPMN диаграммы');
    }
  },

  // Методы для работы с доступом к BPMN диаграммам
  
  // Получение пользователей с доступом к BPMN диаграмме
  getBpmnAccess: async (diagramId) => {
    try {
      const response = await apiClient.get(`/bpmn-access/diagram/${diagramId}/`);
      return response.data;
    } catch (error) {
      return handleApiError(error, { owner: null, shared_users: [] }, 'Ошибка при получении списка доступа к BPMN диаграмме');
    }
  },

  // Предоставление доступа к BPMN диаграмме
  grantBpmnAccess: async (diagramId, userId, accessLevel = 'view') => {
    try {
      const response = await apiClient.post('/bpmn-access/', {
        diagram: diagramId,
        user: userId,
        access_level: accessLevel
      });
      return response.data;
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при предоставлении доступа к BPMN диаграмме');
    }
  },

  // Обновление уровня доступа к BPMN диаграмме
  updateBpmnAccess: async (accessId, accessLevel) => {
    try {
      const response = await apiClient.patch(`/bpmn-access/${accessId}/`, {
        access_level: accessLevel
      });
      return response.data;
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при обновлении уровня доступа к BPMN диаграмме');
    }
  },

  // Отзыв доступа к BPMN диаграмме
  revokeBpmnAccess: async (accessId) => {
    try {
      await apiClient.delete(`/bpmn-access/${accessId}/`);
      return { success: true };
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при отзыве доступа к BPMN диаграмме');
    }
  },

  // Получение пользователей с доступом к BPMN диаграмме (для совместимости)
  getDiagramAccess: async (diagramId) => {
    try {
      const response = await apiClient.get(`/bpmn-access/diagram/${diagramId}/`);
      return response.data;
    } catch (error) {
      return handleApiError(error, { owner: null, shared_users: [] }, 'Ошибка при получении списка доступа к BPMN диаграмме');
    }
  },

  // Предоставление доступа к BPMN диаграмме (для совместимости)
  grantAccess: async (diagramId, userId, accessLevel = 'view') => {
    try {
      const response = await apiClient.post('/bpmn-access/', {
        diagram: diagramId,
        user: userId,
        access_level: accessLevel
      });
      return response.data;
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при предоставлении доступа к BPMN диаграмме');
    }
  }
};