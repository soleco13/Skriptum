from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Notification
from .notification_serializers import NotificationSerializer, NotificationListSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления уведомлениями
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'is_read']
    search_fields = ['message']
    ordering_fields = ['created_at', 'is_read']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Возвращаем только уведомления текущего пользователя"""
        return Notification.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Выбираем сериализатор в зависимости от действия"""
        if self.action == 'list':
            return NotificationListSerializer
        return NotificationSerializer
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Получение количества непрочитанных уведомлений"""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'count': count})
    
    @action(detail=True, methods=['patch'])
    def mark_as_read(self, request, pk=None):
        """Помечает уведомление как прочитанное"""
        notification = self.get_object()
        notification.mark_as_read()
        return Response({'status': 'marked as read'})
    
    @action(detail=False, methods=['patch'])
    def mark_all_as_read(self, request):
        """Помечает все уведомления как прочитанные"""
        updated = self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({'status': f'{updated} notifications marked as read'})
    
    @action(detail=False, methods=['delete'])
    def clear_all(self, request):
        """Удаляет все уведомления пользователя"""
        deleted = self.get_queryset().delete()
        return Response({'status': f'{deleted[0]} notifications deleted'})
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Получение последних уведомлений (для быстрого доступа)"""
        limit = int(request.query_params.get('limit', 5))
        notifications = self.get_queryset()[:limit]
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)
