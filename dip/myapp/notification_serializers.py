from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для уведомлений
    """
    icon = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()
    created_at_formatted = serializers.SerializerMethodField()
    type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = ('id', 'title', 'message', 'type', 'type_display', 'is_read', 'created_at', 'created_at_formatted', 
                 'link', 'document', 'task', 'process', 'icon', 'color')
        read_only_fields = ('id', 'created_at', 'user')
    
    def get_icon(self, obj):
        return obj.get_icon()
    
    def get_color(self, obj):
        return obj.get_color()
    
    def get_created_at_formatted(self, obj):
        return obj.created_at.strftime("%d.%m.%Y %H:%M")
    
    def get_type_display(self, obj):
        return obj.get_type_display()


class NotificationListSerializer(serializers.ModelSerializer):
    """
    Упрощенный сериализатор для списка уведомлений
    """
    icon = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()
    created_at_formatted = serializers.SerializerMethodField()
    type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = ('id', 'title', 'message', 'type', 'type_display', 'is_read', 'created_at', 'created_at_formatted', 
                 'link', 'icon', 'color')
    
    def get_icon(self, obj):
        return obj.get_icon()
    
    def get_color(self, obj):
        return obj.get_color()
    
    def get_created_at_formatted(self, obj):
        return obj.created_at.strftime("%d.%m.%Y %H:%M")
    
    def get_type_display(self, obj):
        return obj.get_type_display()
