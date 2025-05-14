from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Document, Process, Task, UserProfile, DocumentHistory, BpmnDiagram

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('position', 'department', 'phone', 'avatar')

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
    
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ('user',)
        
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
    class Meta:
        model = Process
        fields = '__all__'
        read_only_fields = ('user',)
        
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
    
    class Meta:
        model = BpmnDiagram
        fields = ('id', 'name', 'description', 'xml', 'created_at', 'created_at_formatted', 
                  'updated_at', 'updated_at_formatted', 'user', 'user_name')
        read_only_fields = ('id', 'created_at', 'updated_at', 'user')
    
    def get_created_at_formatted(self, obj):
        return obj.created_at.strftime("%d.%m.%Y %H:%M")
    
    def get_updated_at_formatted(self, obj):
        return obj.updated_at.strftime("%d.%m.%Y %H:%M")
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user.first_name else obj.user.username
    
    def create(self, validated_data):
        # Автоматически устанавливаем текущего пользователя
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

