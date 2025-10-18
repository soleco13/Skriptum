"""
Operational Transform для синхронизации изменений в BPMN диаграммах
"""

import json
import time
import redis
from typing import List, Dict, Any, Optional
from django.conf import settings


class Operation:
    """Класс для представления операции"""
    
    def __init__(self, op_type: str, data: Dict[str, Any], user_id: int, timestamp: float = None):
        self.type = op_type  # 'add', 'remove', 'modify', 'move'
        self.data = data
        self.user_id = user_id
        self.timestamp = timestamp or time.time()
        self.id = f"{user_id}_{int(timestamp * 1000)}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'data': self.data,
            'user_id': self.user_id,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            op_type=data['type'],
            data=data['data'],
            user_id=data['user_id'],
            timestamp=data['timestamp']
        )


class OperationalTransform:
    """
    Реализация Operational Transform для BPMN диаграмм
    """
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host='127.0.0.1',
            port=6379,
            db=0,
            decode_responses=True
        )
    
    async def transform_operation(self, operation: Dict[str, Any], diagram_id: str, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Трансформирует операцию с учетом других операций
        """
        try:
            # Получаем последние операции для диаграммы
            recent_operations = await self.get_recent_operations(diagram_id)
            
            # Создаем объект операции
            op = Operation(
                op_type=operation['type'],
                data=operation['data'],
                user_id=user_id
            )
            
            # Применяем трансформацию
            transformed_op = await self.apply_transformation(op, recent_operations)
            
            return transformed_op.to_dict() if transformed_op else None
            
        except Exception as e:
            print(f"Error in transform_operation: {e}")
            return None
    
    async def apply_transformation(self, operation: Operation, recent_operations: List[Operation]) -> Optional[Operation]:
        """
        Применяет трансформацию к операции
        """
        try:
            # Для BPMN диаграмм используем упрощенную логику трансформации
            # В реальном проекте здесь должна быть более сложная логика
            
            if operation.type == 'add_element':
                return await self.transform_add_element(operation, recent_operations)
            elif operation.type == 'remove_element':
                return await self.transform_remove_element(operation, recent_operations)
            elif operation.type == 'modify_element':
                return await self.transform_modify_element(operation, recent_operations)
            elif operation.type == 'move_element':
                return await self.transform_move_element(operation, recent_operations)
            else:
                # Для неизвестных операций возвращаем как есть
                return operation
                
        except Exception as e:
            print(f"Error in apply_transformation: {e}")
            return operation
    
    async def transform_add_element(self, operation: Operation, recent_operations: List[Operation]) -> Operation:
        """
        Трансформирует операцию добавления элемента
        """
        # Для добавления элементов обычно не нужна трансформация
        # Но можно проверить на конфликты ID
        element_id = operation.data.get('id')
        if element_id:
            # Проверяем, не был ли элемент уже добавлен
            for recent_op in recent_operations:
                if (recent_op.type == 'add_element' and 
                    recent_op.data.get('id') == element_id and
                    recent_op.user_id != operation.user_id):
                    # Генерируем новый ID
                    operation.data['id'] = f"{element_id}_{int(time.time() * 1000)}"
                    break
        
        return operation
    
    async def transform_remove_element(self, operation: Operation, recent_operations: List[Operation]) -> Operation:
        """
        Трансформирует операцию удаления элемента
        """
        element_id = operation.data.get('id')
        if element_id:
            # Проверяем, не был ли элемент уже удален
            for recent_op in recent_operations:
                if (recent_op.type == 'remove_element' and 
                    recent_op.data.get('id') == element_id and
                    recent_op.user_id != operation.user_id):
                    # Элемент уже удален, отменяем операцию
                    return None
        
        return operation
    
    async def transform_modify_element(self, operation: Operation, recent_operations: List[Operation]) -> Operation:
        """
        Трансформирует операцию изменения элемента
        """
        element_id = operation.data.get('id')
        if element_id:
            # Проверяем, не был ли элемент удален
            for recent_op in recent_operations:
                if (recent_op.type == 'remove_element' and 
                    recent_op.data.get('id') == element_id and
                    recent_op.user_id != operation.user_id):
                    # Элемент был удален, отменяем операцию
                    return None
        
        return operation
    
    async def transform_move_element(self, operation: Operation, recent_operations: List[Operation]) -> Operation:
        """
        Трансформирует операцию перемещения элемента
        """
        element_id = operation.data.get('id')
        if element_id:
            # Проверяем, не был ли элемент удален
            for recent_op in recent_operations:
                if (recent_op.type == 'remove_element' and 
                    recent_op.data.get('id') == element_id and
                    recent_op.user_id != operation.user_id):
                    # Элемент был удален, отменяем операцию
                    return None
        
        return operation
    
    async def get_recent_operations(self, diagram_id: str, limit: int = 10) -> List[Operation]:
        """
        Получает последние операции для диаграммы
        """
        try:
            key = f"{settings.COLLABORATIVE_EDITING['REDIS_PREFIX']}:operation:{diagram_id}"
            operations_data = self.redis_client.lrange(key, 0, limit - 1)
            
            operations = []
            for op_data in operations_data:
                try:
                    op_dict = json.loads(op_data)
                    operations.append(Operation.from_dict(op_dict))
                except (json.JSONDecodeError, KeyError):
                    continue
            
            return operations
            
        except Exception as e:
            print(f"Error getting recent operations: {e}")
            return []
    
    async def save_operation(self, operation: Operation, diagram_id: str):
        """
        Сохраняет операцию в Redis
        """
        try:
            key = f"{settings.COLLABORATIVE_EDITING['REDIS_PREFIX']}:operation:{diagram_id}"
            self.redis_client.lpush(key, json.dumps(operation.to_dict()))
            self.redis_client.ltrim(key, 0, 99)  # Храним только последние 100 операций
            
        except Exception as e:
            print(f"Error saving operation: {e}")
    
    def merge_operations(self, op1: Operation, op2: Operation) -> Optional[Operation]:
        """
        Объединяет две операции, если это возможно
        """
        # Простая реализация - в реальном проекте нужна более сложная логика
        if (op1.type == op2.type and 
            op1.data.get('id') == op2.data.get('id') and
            op1.user_id == op2.user_id):
            # Объединяем данные операций
            merged_data = {**op1.data, **op2.data}
            return Operation(
                op_type=op1.type,
                data=merged_data,
                user_id=op1.user_id,
                timestamp=max(op1.timestamp, op2.timestamp)
            )
        
        return None
    
    def is_operation_conflict(self, op1: Operation, op2: Operation) -> bool:
        """
        Проверяет, конфликтуют ли две операции
        """
        # Операции конфликтуют, если они работают с одним элементом
        # и одна из них - удаление
        if (op1.data.get('id') == op2.data.get('id') and
            (op1.type == 'remove_element' or op2.type == 'remove_element')):
            return True
        
        return False
