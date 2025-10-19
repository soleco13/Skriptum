"""
WebSocket Consumers для совместного редактирования BPMN диаграмм и уведомлений
"""

import json
import asyncio
import redis.asyncio as redis
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .models import BpmnDiagram, BpmnAccess, Notification


class BpmnCollaborationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket Consumer для совместного редактирования BPMN диаграмм
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.diagram_id = None
        self.room_group_name = None
        self.user = None
        self.redis_client = None
        
    @database_sync_to_async
    def authenticate_user(self, token):
        """Аутентификация пользователя по JWT токену"""
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = User.objects.get(id=user_id)
            # Для JWT токенов user.is_authenticated всегда True
            return user
        except (InvalidToken, TokenError, User.DoesNotExist):
            return None
        
    async def connect(self):
        """Подключение к WebSocket"""
        print(f"🔌 WebSocket подключение: {self.scope}")
        # Получаем diagram_id из URL параметров
        self.diagram_id = self.scope['url_route']['kwargs'].get('diagram_id')
        print(f"📊 Diagram ID: {self.diagram_id}")
        
        if not self.diagram_id:
            await self.close()
            return
            
        self.room_group_name = f'bpmn_collab_{self.diagram_id}'
        
        # Получаем токен из query параметров
        query_string = self.scope['query_string'].decode()
        
        # Парсим токен из query параметров
        token = None
        if query_string:
            params = dict(param.split('=') for param in query_string.split('&') if '=' in param)
            token = params.get('token')
        
        if not token:
            await self.close()
            return
            
        # Аутентифицируем пользователя по токену
        self.user = await self.authenticate_user(token)
        
        if not self.user:
            print(f"❌ Аутентификация не удалась для токена: {token[:20]}...")
            await self.close()
            return
        
        print(f"✅ Пользователь аутентифицирован: {self.user.username} (ID: {self.user.id})")
            
        # Проверяем права доступа к диаграмме
        has_access = await self.check_diagram_access()
        if not has_access:
            print(f"❌ Нет доступа к диаграмме {self.diagram_id} для пользователя {self.user.username}")
            await self.close()
            return
        
        print(f"✅ Доступ к диаграмме {self.diagram_id} подтвержден для пользователя {self.user.username}")
            
        # Подключаемся к Redis с обработкой ошибок
        try:
            self.redis_client = redis.Redis(
                host='127.0.0.1',
                port=6379,
                db=0,
                decode_responses=True
            )
            # Проверяем подключение
            await self.redis_client.ping()
        except Exception as e:
            # Продолжаем работу без Redis (fallback)
            self.redis_client = None
        
        # Присоединяемся к группе
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Добавляем пользователя в Redis (если подключение доступно)
        if self.redis_client:
            await self.add_user_to_redis()
        
        # Уведомляем всех пользователей о подключении (включая себя)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user_id': self.user.id,
                'username': self.user.username,
                'full_name': self.get_user_display_name()
            }
        )
        
        # Отправляем текущее состояние диаграммы
        await self.send_diagram_state()
        
        # Отправляем список активных пользователей
        active_users = await self.get_active_users()
        await self.send(text_data=json.dumps({
            'type': 'active_users',
            'users': active_users
        }))
    
    async def disconnect(self, close_code):
        """Отключение от WebSocket"""
        print(f"WebSocket disconnect: {close_code}")
        if self.room_group_name:
            # Уведомляем других пользователей об отключении
            if self.user:
                print(f"Отправляем user_left для пользователя: {self.user.username}")
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'user_left',
                        'user_id': self.user.id,
                        'username': self.user.username
                    }
                )
                
                # Автосохранение диаграммы при отключении пользователя
                await self.auto_save_diagram()
            
            # Удаляем из группы
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            
            # Очищаем данные пользователя в Redis
            if self.redis_client:
                await self.cleanup_user_data()
                # Закрываем Redis соединение
                try:
                    await self.redis_client.close()
                except Exception as e:
                    print(f"Error closing Redis connection: {e}")
    
    async def receive(self, text_data):
        """Получение сообщения от клиента"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'cursor_update':
                await self.handle_cursor_update(data)
            elif message_type == 'operation':
                await self.handle_operation(data)
            elif message_type == 'selection':
                await self.handle_selection(data)
            elif message_type == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            print(f"Error in receive: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Internal server error'
            }))
    
    async def handle_cursor_update(self, data):
        """Обработка обновления курсора"""
        cursor_data = {
            'user_id': self.user.id,
            'username': self.user.username,
            'full_name': self.get_user_display_name(),
            'x': data.get('x', 0),
            'y': data.get('y', 0),
            'timestamp': asyncio.get_event_loop().time()
        }
        
        # Сохраняем в Redis
        await self.save_cursor_data(cursor_data)
        
        # Отправляем всем пользователям (включая отправителя для синхронизации)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'cursor_update',
                'user_id': self.user.id,
                'username': self.user.username,
                'full_name': self.get_user_display_name(),
                'x': data.get('x', 0),
                'y': data.get('y', 0)
            }
        )
    
    async def handle_operation(self, data):
        """Обработка операции редактирования"""
        operation = data.get('operation')
        if not operation:
            return
            
        # Сохраняем операцию в Redis
        await self.save_operation(operation)
        
        # Применяем к диаграмме
        await self.apply_operation_to_diagram(operation)
        
        # Отправляем другим пользователям
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'operation',
                'user_id': self.user.id,
                'operation': operation
            }
        )
    
    async def handle_selection(self, data):
        """Обработка выделения элементов"""
        selection_data = {
            'user_id': self.user.id,
            'username': self.user.username,
            'elements': data.get('elements', []),
            'timestamp': asyncio.get_event_loop().time()
        }
        
        # Сохраняем в Redis
        await self.save_selection_data(selection_data)
        
        # Отправляем другим пользователям
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'selection',
                'user_id': self.user.id,
                'username': self.user.username,
                'elements': data.get('elements', [])
            }
        )
    
    # Обработчики групповых сообщений
    async def user_joined(self, event):
        """Пользователь присоединился"""
        # Отправляем информацию о присоединившемся пользователе всем
        user_data = {
            'type': 'user_joined',
            'user_id': event['user_id'],
            'username': event['username'],
            'full_name': event['full_name']
        }
        await self.send(text_data=json.dumps(user_data))
        
        # Обновляем список активных пользователей
        active_users = await self.get_active_users()
        await self.send(text_data=json.dumps({
            'type': 'active_users',
            'users': active_users
        }))
    
    async def user_left(self, event):
        """Пользователь покинул"""
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'user_id': event['user_id'],
            'username': event['username']
        }))
    
    async def cursor_update(self, event):
        """Обновление курсора от другого пользователя"""
        # Отправляем курсор всем пользователям для синхронизации
        cursor_data = {
            'type': 'cursor_update',
            'user_id': event['user_id'],
            'username': event['username'],
            'full_name': event.get('full_name', event['username']),
            'x': event['x'],
            'y': event['y']
        }
        await self.send(text_data=json.dumps(cursor_data))
    
    async def operation(self, event):
        """Операция от другого пользователя"""
        # Отправляем операцию всем пользователям (включая отправителя)
        await self.send(text_data=json.dumps({
            'type': 'operation',
            'user_id': event['user_id'],
            'operation': event['operation']
        }))
    
    async def selection(self, event):
        """Выделение от другого пользователя"""
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'selection',
                'user_id': event['user_id'],
                'username': event['username'],
                'elements': event['elements']
            }))
    
    # Вспомогательные методы
    @database_sync_to_async
    def check_diagram_access(self):
        """Проверка прав доступа к диаграмме"""
        try:
            print(f"🔍 Проверка доступа к диаграмме {self.diagram_id} для пользователя {self.user.username}")
            
            # Проверяем, является ли пользователь владельцем
            if BpmnDiagram.objects.filter(id=self.diagram_id, user=self.user).exists():
                print(f"✅ Пользователь {self.user.username} является владельцем диаграммы {self.diagram_id}")
                return True
            
            # Проверяем, есть ли у пользователя доступ
            access = BpmnAccess.objects.filter(
                diagram_id=self.diagram_id,
                user=self.user,
                access_level__in=['view', 'edit', 'admin']
            ).first()
            
            if access:
                print(f"✅ Пользователь {self.user.username} имеет доступ {access.access_level} к диаграмме {self.diagram_id}")
                return True
            else:
                print(f"❌ Пользователь {self.user.username} не имеет доступа к диаграмме {self.diagram_id}")
                return False
            
        except BpmnDiagram.DoesNotExist:
            print(f"❌ Диаграмма {self.diagram_id} не существует")
            return False
        except Exception as e:
            print(f"❌ Ошибка при проверке доступа: {e}")
            return False
    
    async def send_diagram_state(self):
        """Отправка текущего состояния диаграммы"""
        diagram_data = await self.get_diagram_data()
        await self.send(text_data=json.dumps({
            'type': 'diagram_data',
            'data': diagram_data
        }))
    
    @database_sync_to_async
    def get_diagram_data(self):
        """Получение данных диаграммы"""
        try:
            diagram = BpmnDiagram.objects.get(id=self.diagram_id)
            return {
                'id': diagram.id,
                'name': diagram.name,
                'xml': diagram.xml,
                'updated_at': diagram.updated_at.isoformat()
            }
        except BpmnDiagram.DoesNotExist:
            return None
    
    @database_sync_to_async
    def apply_operation_to_diagram(self, operation):
        """Применение операции к диаграмме в БД"""
        try:
            diagram = BpmnDiagram.objects.get(id=self.diagram_id)
            original_owner = diagram.user  # Сохраняем исходного владельца
            
            # Применяем операцию к XML диаграммы
            if operation.get('type') == 'xml_update':
                new_xml = operation.get('xml')
                if new_xml and new_xml != diagram.xml:
                    diagram.xml = new_xml
                    # Сохраняем с исходным владельцем
                    diagram.user = original_owner
                    diagram.save()
                    print(f"Диаграмма {self.diagram_id} обновлена, владелец сохранен: {original_owner}")
                    return True
            
            # Для других типов операций пока просто обновляем updated_at
            diagram.user = original_owner  # Убеждаемся, что владелец не изменился
            diagram.save()
            return True
        except BpmnDiagram.DoesNotExist:
            return False
    
    def get_user_display_name(self):
        """Получение отображаемого имени пользователя"""
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        return self.user.username
    
    async def save_cursor_data(self, cursor_data):
        """Сохранение данных курсора в Redis"""
        if not self.redis_client:
            return
            
        try:
            key = f"{settings.COLLABORATIVE_EDITING['REDIS_PREFIX']}:cursor:{self.diagram_id}:{self.user.id}"
            await self.redis_client.setex(key, 30, json.dumps(cursor_data))  # TTL 30 секунд
        except Exception as e:
            print(f"Error saving cursor data to Redis: {e}")
    
    async def save_operation(self, operation):
        """Сохранение операции в Redis"""
        if not self.redis_client:
            return
            
        try:
            key = f"{settings.COLLABORATIVE_EDITING['REDIS_PREFIX']}:operation:{self.diagram_id}"
            await self.redis_client.lpush(key, json.dumps(operation))
            await self.redis_client.ltrim(key, 0, 99)  # Храним только последние 100 операций
        except Exception as e:
            print(f"Error saving operation to Redis: {e}")
    
    async def save_selection_data(self, selection_data):
        """Сохранение данных выделения в Redis"""
        if not self.redis_client:
            return
            
        try:
            key = f"{settings.COLLABORATIVE_EDITING['REDIS_PREFIX']}:selection:{self.diagram_id}:{self.user.id}"
            await self.redis_client.setex(key, 60, json.dumps(selection_data))  # TTL 60 секунд
        except Exception as e:
            print(f"Error saving selection data to Redis: {e}")
    
    async def get_active_users(self):
        """Получение списка активных пользователей"""
        if not self.redis_client:
            return []
            
        try:
            # Используем SET для быстрого получения активных пользователей
            active_users_key = f"{settings.COLLABORATIVE_EDITING['REDIS_PREFIX']}:active_users:{self.diagram_id}"
            user_ids = await self.redis_client.smembers(active_users_key)
            
            if not user_ids:
                return []
            
            # Получаем данные пользователей через mget (оптимизированно)
            user_data_keys = [f"{settings.COLLABORATIVE_EDITING['REDIS_PREFIX']}:user_data:{self.diagram_id}:{user_id}" 
                            for user_id in user_ids]
            user_data_list = await self.redis_client.mget(user_data_keys)
            
            active_users = []
            for user_data in user_data_list:
                if user_data:
                    user = json.loads(user_data)
                    active_users.append({
                        'user_id': user['user_id'],
                        'username': user['username'],
                        'full_name': user['full_name']
                    })
            
            return active_users
        except Exception as e:
            print(f"Error getting active users from Redis: {e}")
            return []
    
    async def add_user_to_redis(self):
        """Добавление пользователя в Redis при подключении"""
        if not self.redis_client:
            return
            
        try:
            user_data = {
                'user_id': self.user.id,
                'username': self.user.username,
                'full_name': self.get_user_display_name(),
                'connected_at': asyncio.get_event_loop().time()
            }
            
            # Используем SET для активных пользователей (быстрее чем HASH)
            active_users_key = f"{settings.COLLABORATIVE_EDITING['REDIS_PREFIX']}:active_users:{self.diagram_id}"
            user_data_key = f"{settings.COLLABORATIVE_EDITING['REDIS_PREFIX']}:user_data:{self.diagram_id}:{self.user.id}"
            
            # Добавляем пользователя в SET активных пользователей
            await self.redis_client.sadd(active_users_key, self.user.id)
            # Сохраняем данные пользователя
            await self.redis_client.setex(user_data_key, 300, json.dumps(user_data))  # TTL 5 минут
            # Обновляем TTL для SET
            await self.redis_client.expire(active_users_key, 300)
        except Exception as e:
            print(f"Error adding user to Redis: {e}")
    
    async def remove_user_from_redis(self):
        """Удаление пользователя из Redis при отключении"""
        await self.cleanup_user_data()
    
    async def cleanup_user_data(self):
        """Очистка данных пользователя при отключении"""
        if not self.redis_client:
            return
            
        try:
            # Удаляем пользователя из SET активных пользователей
            active_users_key = f"{settings.COLLABORATIVE_EDITING['REDIS_PREFIX']}:active_users:{self.diagram_id}"
            await self.redis_client.srem(active_users_key, self.user.id)
            
            # Удаляем данные пользователя
            user_data_key = f"{settings.COLLABORATIVE_EDITING['REDIS_PREFIX']}:user_data:{self.diagram_id}:{self.user.id}"
            await self.redis_client.delete(user_data_key)
            
            # Удаляем данные курсора
            cursor_key = f"{settings.COLLABORATIVE_EDITING['REDIS_PREFIX']}:cursor:{self.diagram_id}:{self.user.id}"
            await self.redis_client.delete(cursor_key)
            
            # Удаляем данные выделения
            selection_key = f"{settings.COLLABORATIVE_EDITING['REDIS_PREFIX']}:selection:{self.diagram_id}:{self.user.id}"
            await self.redis_client.delete(selection_key)
        except Exception as e:
            print(f"Error cleaning up user data from Redis: {e}")
    
    @database_sync_to_async
    def auto_save_diagram(self):
        """Автосохранение диаграммы при отключении пользователя"""
        try:
            if self.diagram_id:
                # Получаем последнюю операцию из Redis
                if self.redis_client:
                    operation_key = f"{settings.COLLABORATIVE_EDITING['REDIS_PREFIX']}:operation:{self.diagram_id}"
                    # Здесь можно добавить логику получения последней операции
                    # и сохранения её в БД
                    print(f"Автосохранение диаграммы {self.diagram_id} при отключении пользователя {self.user.username}")
        except Exception as e:
            print(f"Error in auto_save_diagram: {e}")


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket Consumer для real-time уведомлений
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.group_name = None
        
    @database_sync_to_async
    def authenticate_user(self, token):
        """Аутентификация пользователя по JWT токену"""
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = User.objects.get(id=user_id)
            return user
        except (InvalidToken, TokenError, User.DoesNotExist):
            return None
    
    async def connect(self):
        """Подключение к WebSocket для уведомлений"""
        print(f"🔔 WebSocket подключение для уведомлений: {self.scope}")
        
        # Получаем токен из query параметров
        query_string = self.scope['query_string'].decode()
        token = None
        if query_string:
            params = dict(param.split('=') for param in query_string.split('&') if '=' in param)
            token = params.get('token')
        
        if not token:
            await self.close()
            return
            
        # Аутентифицируем пользователя по токену
        self.user = await self.authenticate_user(token)
        
        if not self.user:
            print(f"❌ Аутентификация не удалась для токена: {token[:20]}...")
            await self.close()
            return
        
        print(f"✅ Пользователь аутентифицирован для уведомлений: {self.user.username} (ID: {self.user.id})")
        
        # Создаем группу для пользователя
        self.group_name = f'notifications_{self.user.id}'
        
        # Присоединяемся к группе
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Отправляем количество непрочитанных уведомлений
        unread_count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'count': unread_count
        }))
    
    async def disconnect(self, close_code):
        """Отключение от WebSocket"""
        print(f"WebSocket disconnect для уведомлений: {close_code}")
        if self.group_name:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Получение сообщения от клиента"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'mark_as_read':
                notification_id = data.get('notification_id')
                if notification_id:
                    await self.mark_notification_as_read(notification_id)
            elif message_type == 'mark_all_as_read':
                await self.mark_all_as_read()
            elif message_type == 'get_notifications':
                limit = data.get('limit', 20)
                offset = data.get('offset', 0)
                notifications = await self.get_notifications(limit, offset)
                await self.send(text_data=json.dumps({
                    'type': 'notifications_list',
                    'notifications': notifications
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            print(f"Error in notification receive: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Internal server error'
            }))
    
    async def notification_message(self, event):
        """Получение уведомления от группы"""
        notification = event['notification']
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'notification': notification
        }))
        
        # Обновляем счетчик непрочитанных
        unread_count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'count': unread_count
        }))
    
    @database_sync_to_async
    def get_unread_count(self):
        """Получение количества непрочитанных уведомлений"""
        try:
            return Notification.objects.filter(user=self.user, is_read=False).count()
        except Exception as e:
            print(f"Error getting unread count: {e}")
            return 0
    
    @database_sync_to_async
    def get_notifications(self, limit=20, offset=0):
        """Получение списка уведомлений"""
        try:
            notifications = Notification.objects.filter(user=self.user).order_by('-created_at')[offset:offset+limit]
            return [
                {
                    'id': notification.id,
                    'message': notification.message,
                    'type': notification.type,
                    'is_read': notification.is_read,
                    'created_at': notification.created_at.isoformat(),
                    'link': notification.link,
                    'icon': notification.get_icon(),
                    'color': notification.get_color(),
                }
                for notification in notifications
            ]
        except Exception as e:
            print(f"Error getting notifications: {e}")
            return []
    
    @database_sync_to_async
    def mark_notification_as_read(self, notification_id):
        """Помечает уведомление как прочитанное"""
        try:
            notification = Notification.objects.get(id=notification_id, user=self.user)
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            return False
        except Exception as e:
            print(f"Error marking notification as read: {e}")
            return False
    
    @database_sync_to_async
    def mark_all_as_read(self):
        """Помечает все уведомления как прочитанные"""
        try:
            Notification.objects.filter(user=self.user, is_read=False).update(is_read=True)
            return True
        except Exception as e:
            print(f"Error marking all notifications as read: {e}")
            return False