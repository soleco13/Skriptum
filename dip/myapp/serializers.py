from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Document, Process, Task, UserProfile, DocumentHistory, BpmnDiagram, DocumentAccess, BpmnAccess, Role

class RoleSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()
    users_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = '__all__'
    
    def get_permissions(self, obj):
        return obj.get_permissions()
    
    def get_users_count(self, obj):
        return obj.users.count()

class RoleListSerializer(serializers.ModelSerializer):
    """
    Упрощенный сериализатор для списка ролей
    """
    users_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'display_name', 'description', 'color', 'icon', 'is_active', 'users_count']
    
    def get_users_count(self, obj):
        return obj.users.count()

class UserProfileSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    role_info = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = ('position', 'department', 'phone', 'avatar', 'avatar_url', 'role', 'role_info', 'permissions', 'is_active', 'created_at', 'updated_at')
    
    def get_avatar_url(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None
    
    def get_role_info(self, obj):
        if obj.role:
            return {
                'id': obj.role.id,
                'name': obj.role.name,
                'display_name': obj.role.display_name,
                'color': obj.role.color,
                'icon': obj.role.icon,
                'description': obj.role.description
            }
        return None
    
    def get_permissions(self, obj):
        if obj.role:
            return obj.role.get_permissions()
        return []

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'profile')
        read_only_fields = ('id',)

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'password2')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

class DocumentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=False, allow_null=True)
    is_owner = serializers.SerializerMethodField()
    owner_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ('user',)
    
    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.user == request.user
        return False
    
    def get_owner_name(self, obj):
        if obj.user.first_name and obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return obj.user.username
        
    def create(self, validated_data):
        # Автоматически устанавливаем текущего пользователя
        validated_data['user'] = self.context['request'].user
        
        # Определяем тип файла, если файл был загружен
        file = validated_data.get('file')
        if file:
            filename = file.name.lower()
            if filename.endswith('.doc'):
                validated_data['file_type'] = 'doc'
            elif filename.endswith('.docx'):
                validated_data['file_type'] = 'docx'
            elif filename.endswith('.pdf'):
                validated_data['file_type'] = 'pdf'
        
        return super().create(validated_data)

class ProcessSerializer(serializers.ModelSerializer):
    is_owner = serializers.SerializerMethodField()
    owner_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Process
        fields = '__all__'
        read_only_fields = ('user',)
        
    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.user == request.user
        return False
    
    def get_owner_name(self, obj):
        if obj.user.first_name and obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return obj.user.username
        
    def create(self, validated_data):
        # Автоматически устанавливаем текущего пользователя
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ('user', 'id')
        
    def create(self, validated_data):
        # Автоматически устанавливаем текущего пользователя
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class DocumentHistorySerializer(serializers.ModelSerializer):
    created_at_formatted = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentHistory
        fields = ('id', 'document', 'content', 'created_at', 'created_at_formatted', 'user', 'user_name', 'version_name')
        read_only_fields = ('id', 'created_at', 'created_at_formatted')
    
    def get_created_at_formatted(self, obj):
        return obj.created_at.strftime("%d.%m.%Y %H:%M")
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user.first_name else obj.user.username


class BpmnDiagramSerializer(serializers.ModelSerializer):
    created_at_formatted = serializers.SerializerMethodField()
    updated_at_formatted = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    owner_name = serializers.SerializerMethodField()
    process = serializers.PrimaryKeyRelatedField(required=False, allow_null=True, queryset=Process.objects.none())
    
    class Meta:
        model = BpmnDiagram
        fields = ('id', 'name', 'description', 'xml', 'process', 'created_at', 'created_at_formatted', 
                  'updated_at', 'updated_at_formatted', 'user', 'user_name', 'is_owner', 'owner_name')
        read_only_fields = ('id', 'created_at', 'updated_at', 'user')
    
    def get_created_at_formatted(self, obj):
        return obj.created_at.strftime("%d.%m.%Y %H:%M")
    
    def get_updated_at_formatted(self, obj):
        return obj.updated_at.strftime("%d.%m.%Y %H:%M")
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user.first_name else obj.user.username
    
    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.user == request.user
        return False
    
    def get_owner_name(self, obj):
        if obj.user.first_name and obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return obj.user.username
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            self.fields['process'].queryset = Process.objects.filter(user=request.user)
        else:
            self.fields['process'].queryset = Process.objects.none()
    
    def create(self, validated_data):
        # Автоматически устанавливаем текущего пользователя
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class UserSearchSerializer(serializers.ModelSerializer):
    """Сериализатор для поиска пользователей"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'full_name')
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() if obj.first_name or obj.last_name else obj.username


class DocumentAccessSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()
    granted_by_name = serializers.SerializerMethodField()
    granted_at_formatted = serializers.SerializerMethodField()
    access_level_display = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentAccess
        fields = ('id', 'document', 'user', 'user_name', 'user_email', 'access_level', 
                 'access_level_display', 'granted_by', 'granted_by_name', 'granted_at', 'granted_at_formatted')
        read_only_fields = ('id', 'granted_by', 'granted_at')
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() if obj.user.first_name or obj.user.last_name else obj.user.username
    
    def get_user_email(self, obj):
        return obj.user.email
    
    def get_granted_by_name(self, obj):
        return f"{obj.granted_by.first_name} {obj.granted_by.last_name}".strip() if obj.granted_by.first_name or obj.granted_by.last_name else obj.granted_by.username
    
    def get_granted_at_formatted(self, obj):
        return obj.granted_at.strftime("%d.%m.%Y %H:%M")
    
    def get_access_level_display(self, obj):
        return obj.get_access_level_display()
    
    def create(self, validated_data):
        # Автоматически устанавливаем кто выдал доступ
        validated_data['granted_by'] = self.context['request'].user
        return super().create(validated_data)


class BpmnAccessSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()
    granted_by_name = serializers.SerializerMethodField()
    granted_at_formatted = serializers.SerializerMethodField()
    access_level_display = serializers.SerializerMethodField()
    
    class Meta:
        model = BpmnAccess
        fields = ('id', 'diagram', 'user', 'user_name', 'user_email', 'access_level', 
                 'access_level_display', 'granted_by', 'granted_by_name', 'granted_at', 'granted_at_formatted')
        read_only_fields = ('id', 'granted_by', 'granted_at')
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() if obj.user.first_name or obj.user.last_name else obj.user.username
    
    def get_user_email(self, obj):
        return obj.user.email
    
    def get_granted_by_name(self, obj):
        return f"{obj.granted_by.first_name} {obj.granted_by.last_name}".strip() if obj.granted_by.first_name or obj.granted_by.last_name else obj.granted_by.username
    
    def get_granted_at_formatted(self, obj):
        return obj.granted_at.strftime("%d.%m.%Y %H:%M")
    
    def get_access_level_display(self, obj):
        return obj.get_access_level_display()
    
    def create(self, validated_data):
        # Автоматически устанавливаем кто выдал доступ
        validated_data['granted_by'] = self.context['request'].user
        return super().create(validated_data)

