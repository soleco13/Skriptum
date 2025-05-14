// Сервис для работы с BPMN-диаграммами
import axios from 'axios';
import { handleApiError } from './config';
import { API_BASE_URL } from './config';

// Используем тот же экземпляр axios, что и для других сервисов
const apiClient = axios.create({
  baseURL: API_BASE_URL
});

// Интерцептор для добавления токена к запросам
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token') || sessionStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `JWT ${token}`;
  }
  return config;
});

// Сервис для работы с BPMN-диаграммами
export const BpmnService = {
  // Получение всех диаграмм
  getAll: async () => {
    try {
      const response = await apiClient.get('/bpmn-diagrams/');
      return response.data;
    } catch (error) {
      // Демо-данные при ошибке
      return handleApiError(error, [
        {
          id: 1,
          name: 'Процесс обработки заявки',
          description: 'Диаграмма процесса обработки заявки клиента',
          created_at: '2025-04-01T10:00:00Z',
          updated_at: '2025-04-05T15:30:00Z'
        },
        {
          id: 2,
          name: 'Процесс согласования документа',
          description: 'Диаграмма процесса согласования внутренних документов',
          created_at: '2025-03-20T09:15:00Z',
          updated_at: '2025-03-25T14:45:00Z'
        }
      ], 'Ошибка при получении BPMN-диаграмм');
    }
  },
  
  // Получение диаграммы по ID
  getDiagram: async (id) => {
    try {
      const response = await apiClient.get(`/bpmn-diagrams/${id}/`);
      return response.data;
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при получении BPMN-диаграммы');
    }
  },
  
  // Создание новой диаграммы
  createDiagram: async (diagram) => {
    try {
      const response = await apiClient.post('/bpmn-diagrams/', diagram);
      return response.data;
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при создании BPMN-диаграммы');
    }
  },
  
  // Обновление существующей диаграммы
  updateDiagram: async (id, xml) => {
    try {
      const response = await apiClient.put(`/bpmn-diagrams/${id}/`, { xml });
      return response.data;
    } catch (error) {
      return handleApiError(error, null, 'Ошибка при обновлении BPMN-диаграммы');
    }
  },
  
  // Удаление диаграммы
  deleteDiagram: async (id) => {
    try {
      await apiClient.delete(`/bpmn-diagrams/${id}/`);
      return true;
    } catch (error) {
      return handleApiError(error, false, 'Ошибка при удалении BPMN-диаграммы');
    }
  }
};