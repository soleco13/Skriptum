<template>
  <div class="digital-stamp-container">
    <div class="stamp-header">
      <h3>
        <i class="fas fa-stamp"></i>
        Электронная печать
      </h3>
      <div class="stamp-actions">
        <button class="btn-preview" @click="generatePreview" :disabled="!isFormValid">
          <i class="fas fa-eye"></i>
          Предпросмотр
        </button>
        <button class="btn-save" @click="saveStamp" :disabled="!isFormValid || !stampPreview">
          <i class="fas fa-save"></i>
          Сохранить печать
        </button>
      </div>
    </div>
    
    <div class="stamp-form">
      <div class="form-row">
        <div class="form-group">
          <label for="organization">
            <i class="fas fa-building"></i>
            Организация *
          </label>
          <input 
            type="text" 
            id="organization"
            v-model="stampData.organization"
            placeholder="Введите название организации"
            class="form-input"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="certificate">
            <i class="fas fa-certificate"></i>
            Сертификат *
          </label>
          <div class="certificate-input-group">
            <input 
              type="text" 
              id="certificate"
              v-model="stampData.certificate"
              placeholder="Номер сертификата"
              class="form-input certificate-input"
              required
              readonly
            />
            <button type="button" class="btn-generate-cert" @click="generateNewCertificate">
              <i class="fas fa-sync-alt"></i>
              Новый
            </button>
          </div>
        </div>
      </div>
      
      <div class="form-row">
        <div class="form-group">
          <label for="publisher">
            <i class="fas fa-user-tie"></i>
            Издатель *
          </label>
          <input 
            type="text" 
            id="publisher"
            v-model="stampData.publisher"
            placeholder="ФИО издателя"
            class="form-input"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="validityFrom">
            <i class="fas fa-calendar"></i>
            Действителен с *
          </label>
          <input 
            type="date" 
            id="validityFrom"
            v-model="stampData.validityFrom"
            class="form-input"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="validityTo">
            <i class="fas fa-calendar"></i>
            Действителен по *
          </label>
          <input 
            type="date" 
            id="validityTo"
            v-model="stampData.validityTo"
            class="form-input"
            required
          />
        </div>
      </div>
      
      <div class="form-group">
        <label for="additionalInfo">
          <i class="fas fa-info-circle"></i>
          Дополнительная информация
        </label>
        <textarea 
          id="additionalInfo"
          v-model="stampData.additionalInfo"
          placeholder="Дополнительная информация (необязательно)"
          class="form-textarea"
          rows="3"
        ></textarea>
      </div>
    </div>
    
    <!-- Предпросмотр печати -->
    <div v-if="stampPreview || showPreview" class="stamp-preview">
      <h4>
        <i class="fas fa-eye"></i>
        Предпросмотр печати
      </h4>
      <div class="preview-canvas-container">
        <canvas 
          ref="previewCanvas"
          class="preview-canvas"
          :width="canvasWidth"
          :height="canvasHeight"
        ></canvas>
      </div>
      <div class="preview-actions">
        <button class="btn-regenerate" @click="generatePreview">
          <i class="fas fa-sync-alt"></i>
          Перегенерировать
        </button>
        <button class="btn-download" @click="downloadStamp">
          <i class="fas fa-download"></i>
          Скачать
        </button>
      </div>
    </div>
    
    <!-- Сохраненная печать -->
    <div v-if="savedStamp" class="saved-stamp">
      <h4>
        <i class="fas fa-check-circle"></i>
        Сохраненная печать
      </h4>
      <div class="saved-image">
        <img :src="savedStamp" alt="Сохраненная печать" />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DigitalStamp',
  props: {
    documentId: {
      type: [String, Number],
      required: true
    },
    initialStamp: {
      type: String,
      default: null
    }
  },
  data() {
    return {
      stampData: {
        organization: '',
        certificate: this.generateCertificate(),
        publisher: 'Skriptum — система автоматизированного документооборота и управления бизнес-процессами',
        validityFrom: '',
        validityTo: '',
        additionalInfo: ''
      },
      stampPreview: null,
      savedStamp: null,
      showPreview: false,
       canvasWidth: 600,
       canvasHeight: 200
    };
  },
  computed: {
    isFormValid() {
      const isValid = this.stampData.organization.trim() !== '' &&
             this.stampData.certificate.trim() !== '' &&
             this.stampData.publisher.trim() !== '' &&
             this.stampData.validityFrom.trim() !== '' &&
             this.stampData.validityTo.trim() !== '';
      
      console.log('DigitalStamp - Проверка валидности формы:', {
        organization: this.stampData.organization,
        certificate: this.stampData.certificate,
        publisher: this.stampData.publisher,
        validityFrom: this.stampData.validityFrom,
        validityTo: this.stampData.validityTo,
        isValid: isValid
      });
      
      return isValid;
    }
  },
  mounted() {
    if (this.initialStamp) {
      this.savedStamp = this.initialStamp;
    }
  },
  methods: {
    async generatePreview() {
      console.log('DigitalStamp - generatePreview вызван');
      console.log('DigitalStamp - isFormValid:', this.isFormValid);
      
      if (!this.isFormValid) {
        this.$emit('error', 'Пожалуйста, заполните все обязательные поля');
        return;
      }
      
      try {
        console.log('DigitalStamp - Создание предпросмотра печати');
        this.showPreview = true; // Показываем секцию предпросмотра
        await this.$nextTick(); // Ждем обновления DOM
        const canvas = this.$refs.previewCanvas;
        console.log('DigitalStamp - Canvas найден:', canvas);
        if (!canvas) {
          console.error('DigitalStamp - Canvas не найден!');
          return;
        }
        
        const ctx = canvas.getContext('2d');
        console.log('DigitalStamp - Context получен:', ctx);
        
        // Очищаем canvas
        ctx.clearRect(0, 0, this.canvasWidth, this.canvasHeight);
        
        // Рисуем синюю рамку
        ctx.strokeStyle = '#3b82f6';
        ctx.lineWidth = 3;
        ctx.strokeRect(5, 5, this.canvasWidth - 10, this.canvasHeight - 10);
        
         // Настраиваем шрифт и цвет текста
         ctx.fillStyle = '#3b82f6';
         ctx.textAlign = 'center';
         ctx.textBaseline = 'middle';
        
         // Заголовок - "Документ подписан усиленной квалифицированной электронной подписью."
         ctx.font = 'bold 16px Arial';
         ctx.fillText('Документ подписан', this.canvasWidth / 2, 35);
         ctx.fillText('усиленной квалифицированной электронной', this.canvasWidth / 2, 55);
         ctx.fillText('подписью.', this.canvasWidth / 2, 75);
         
         // Переключаемся на левое выравнивание для полей
         ctx.textAlign = 'left';
         ctx.font = '14px Arial';
         
         // Организация
         ctx.fillText(`Организация: ${this.stampData.organization}`, 20, 100);
         
         // Сертификат
         ctx.fillText(`Сертификат: ${this.stampData.certificate}`, 20, 120);
         
         // Издатель
         ctx.fillText(`Издатель: ${this.stampData.publisher}`, 20, 140);
         
         // Период действия
         const validityText = `с ${this.formatDate(this.stampData.validityFrom)} по ${this.formatDate(this.stampData.validityTo)}`;
         ctx.fillText(`Действителен: ${validityText}`, 20, 160);
        
        // Сохраняем предпросмотр
        this.stampPreview = canvas.toDataURL('image/png');
        console.log('DigitalStamp - Предпросмотр создан:', this.stampPreview ? 'Да' : 'Нет');
        console.log('DigitalStamp - Длина данных предпросмотра:', this.stampPreview ? this.stampPreview.length : 0);
        
        this.$emit('preview-generated', this.stampPreview);
        
      } catch (error) {
        console.error('Ошибка при генерации предпросмотра:', error);
        this.$emit('error', 'Ошибка при генерации предпросмотра печати');
      }
    },
    
    drawDecorativeElements(ctx) {
      // Рисуем декоративные звездочки по углам
      ctx.fillStyle = '#1e40af';
      ctx.font = '20px Arial';
      
      // Верхние углы
      ctx.fillText('★', 20, 25);
      ctx.fillText('★', this.canvasWidth - 20, 25);
      
      // Нижние углы
      ctx.fillText('★', 20, this.canvasHeight - 15);
      ctx.fillText('★', this.canvasWidth - 20, this.canvasHeight - 15);
      
      // Рисуем декоративную линию внизу
      ctx.strokeStyle = '#3b82f6';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(50, this.canvasHeight - 30);
      ctx.lineTo(this.canvasWidth - 50, this.canvasHeight - 30);
      ctx.stroke();
    },
    
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('ru-RU');
    },
    
    generateCertificate() {
      // Генерируем случайный сертификат из цифр и букв
      const chars = '0123456789abcdef';
      let result = '';
      for (let i = 0; i < 32; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
      }
      return result;
    },
    
    generateNewCertificate() {
      this.stampData.certificate = this.generateCertificate();
    },
    
    async saveStamp() {
      console.log('DigitalStamp - saveStamp вызван');
      console.log('DigitalStamp - stampPreview:', this.stampPreview);
      console.log('DigitalStamp - isFormValid:', this.isFormValid);
      
      if (!this.stampPreview) {
        this.$emit('error', 'Сначала создайте предпросмотр печати');
        return;
      }
      
      try {
        // Отправляем на сервер
        const response = await this.saveStampToServer(this.stampPreview);
        
        if (response.success) {
          this.savedStamp = this.stampPreview;
          this.$emit('stamp-saved', {
            stamp: this.stampPreview,
            stampData: { ...this.stampData },
            documentId: this.documentId
          });
          
          this.showSuccessMessage('Печать успешно сохранена');
        } else {
          throw new Error(response.message || 'Ошибка при сохранении печати');
        }
      } catch (error) {
        console.error('Ошибка при сохранении печати:', error);
        this.$emit('error', error.message || 'Ошибка при сохранении печати');
      }
    },
    
    async saveStampToServer(stampData) {
      // Импортируем DocumentService
      const { DocumentService } = await import('../api/services');
      
      try {
        const response = await DocumentService.addStamp(this.documentId, stampData, this.stampData);
        return response;
      } catch (error) {
        console.error('Ошибка при сохранении печати:', error);
        throw error;
      }
    },
    
    downloadStamp() {
      if (!this.stampPreview) return;
      
      const link = document.createElement('a');
      link.download = `stamp_${this.documentId}_${Date.now()}.png`;
      link.href = this.stampPreview;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    },
    
    showSuccessMessage(message) {
      // Простое уведомление об успехе
      const notification = document.createElement('div');
      notification.className = 'stamp-success-notification';
      notification.textContent = message;
      notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #10b981;
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        z-index: 1000;
        font-size: 14px;
        font-weight: 500;
        animation: slideInRight 0.3s ease;
      `;
      
      document.body.appendChild(notification);
      
      setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
          document.body.removeChild(notification);
        }, 300);
      }, 3000);
    },
    
    // Метод для загрузки существующей печати
    loadStamp(stampData) {
      if (stampData) {
        this.savedStamp = stampData;
      }
    },
    
    // Метод для сброса формы
    resetForm() {
      this.stampData = {
        organization: '',
        certificate: this.generateCertificate(),
        publisher: 'Skriptum — система автоматизированного документооборота и управления бизнес-процессами',
        validityFrom: '',
        validityTo: '',
        additionalInfo: ''
      };
      this.stampPreview = null;
      this.showPreview = false;
    }
  }
};
</script>

<style scoped>
.digital-stamp-container {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  margin-bottom: 1.5rem;
}

.stamp-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-bottom: 1px solid #bae6fd;
}

.stamp-header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #0c4a6e;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stamp-header h3 i {
  color: #0284c7;
}

.stamp-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.btn-preview,
.btn-save {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.875rem;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-preview {
  background: #dbeafe;
  color: #1e40af;
}

.btn-preview:hover:not(:disabled) {
  background: #bfdbfe;
  color: #1e3a8a;
}

.btn-save {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
}

.btn-save:hover:not(:disabled) {
  background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
}

.btn-preview:disabled,
.btn-save:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.stamp-form {
  padding: 1.5rem;
  background: #ffffff;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
}

.form-group label i {
  color: #6b7280;
  font-size: 0.875rem;
}

.form-input,
.form-textarea {
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.875rem;
  background: #ffffff;
  color: #374151;
  transition: all 0.2s ease;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.certificate-input-group {
  display: flex;
  gap: 0.5rem;
  align-items: stretch;
}

.certificate-input {
  flex: 1;
}

.btn-generate-cert {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.875rem;
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-generate-cert:hover {
  background: #e5e7eb;
  border-color: #9ca3af;
  transform: translateY(-1px);
}

.btn-generate-cert i {
  font-size: 0.75rem;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.stamp-preview {
  padding: 1rem 1.5rem;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
}

.stamp-preview h4 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #0c4a6e;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stamp-preview h4 i {
  color: #0284c7;
}

.preview-canvas-container {
  display: flex;
  justify-content: center;
  margin-bottom: 1rem;
}

.preview-canvas {
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.preview-actions {
  display: flex;
  justify-content: center;
  gap: 0.75rem;
}

.btn-regenerate,
.btn-download {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-regenerate {
  background: #fef3c7;
  color: #d97706;
}

.btn-regenerate:hover {
  background: #fde68a;
  color: #b45309;
}

.btn-download {
  background: #d1fae5;
  color: #059669;
}

.btn-download:hover {
  background: #a7f3d0;
  color: #047857;
}

.saved-stamp {
  padding: 1rem 1.5rem;
  background: #f0fdf4;
  border-top: 1px solid #bbf7d0;
}

.saved-stamp h4 {
  margin: 0 0 0.75rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #14532d;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.saved-stamp h4 i {
  color: #16a34a;
}

.saved-image {
  text-align: center;
  padding: 1rem;
  background: #ffffff;
  border-radius: 8px;
  border: 1px solid #bbf7d0;
}

.saved-image img {
  max-width: 100%;
  max-height: 200px;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Анимации для уведомлений */
@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes slideOutRight {
  from {
    transform: translateX(0);
    opacity: 1;
  }
  to {
    transform: translateX(100%);
    opacity: 0;
  }
}

/* Адаптивность */
@media (max-width: 768px) {
  .stamp-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
    padding: 1rem;
  }
  
  .stamp-actions {
    justify-content: center;
  }
  
  .form-row {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
  
  .stamp-form {
    padding: 1rem;
  }
  
  .stamp-preview,
  .saved-stamp {
    padding: 1rem;
  }
  
  .preview-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .btn-regenerate,
  .btn-download {
    width: 100%;
    max-width: 200px;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .stamp-actions {
    flex-direction: column;
  }
  
  .btn-preview,
  .btn-save {
    width: 100%;
    justify-content: center;
  }
  
  .preview-canvas {
    width: 100%;
    max-width: 280px;
    height: auto;
  }
}
</style>
