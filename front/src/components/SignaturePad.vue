<template>
  <div class="signature-pad-container">
    <div class="signature-header">
      <h3>
        <i class="fas fa-signature"></i>
        Ручная подпись
      </h3>
      <div class="signature-actions">
        <button class="btn-clear" @click="clearSignature" :disabled="isEmpty">
          <i class="fas fa-eraser"></i>
          Очистить
        </button>
        <button class="btn-undo" @click="undoLastStroke" :disabled="isEmpty">
          <i class="fas fa-undo"></i>
          Отменить последний штрих
        </button>
        <button class="btn-save" @click="saveSignature" :disabled="isEmpty">
          <i class="fas fa-save"></i>
          Сохранить подпись
        </button>
      </div>
    </div>
    
    <div class="signature-canvas-container">
      <canvas 
        ref="signatureCanvas"
        class="signature-canvas"
      ></canvas>
    </div>
    
    <div class="signature-info">
      <p class="signature-hint">
        <i class="fas fa-info-circle"></i>
        Нарисуйте вашу подпись в области выше. Используйте мышь или касание на мобильном устройстве.
      </p>
    </div>
    
    <!-- Предпросмотр сохраненной подписи -->
    <div v-if="savedSignature" class="signature-preview">
      <h4>
        <i class="fas fa-eye"></i>
        Предпросмотр подписи
      </h4>
      <div class="preview-image">
        <img :src="savedSignature" alt="Сохраненная подпись" />
      </div>
    </div>
  </div>
</template>

<script>
import SignaturePad from 'signature_pad';

export default {
  name: 'SignaturePad',
  props: {
    documentId: {
      type: [String, Number],
      required: true
    },
    initialSignature: {
      type: String,
      default: null
    }
  },
  data() {
    return {
      signaturePad: null,
      isEmpty: true,
      savedSignature: null,
      isDrawing: false
    };
  },
  mounted() {
    this.initializeSignaturePad();
    if (this.initialSignature) {
      this.savedSignature = this.initialSignature;
    }
  },
  beforeUnmount() {
    if (this.signaturePad) {
      this.signaturePad.off();
    }
  },
  methods: {
    initializeSignaturePad() {
      const canvas = this.$refs.signatureCanvas;
      if (!canvas) return;
      
      // Устанавливаем размеры canvas
      const rect = canvas.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      
      const ctx = canvas.getContext('2d');
      ctx.scale(dpr, dpr);
      
      // Инициализируем SignaturePad
      this.signaturePad = new SignaturePad(canvas, {
        backgroundColor: 'rgba(255, 255, 255, 0)',
        penColor: 'rgb(0, 0, 0)',
        minWidth: 1,
        maxWidth: 3,
        throttle: 16,
        minDistance: 5
      });
      
      // Обработчики событий SignaturePad
      this.signaturePad.addEventListener('beginStroke', () => {
        this.isEmpty = false;
        this.isDrawing = true;
      });
      
      this.signaturePad.addEventListener('endStroke', () => {
        this.isDrawing = false;
        this.isEmpty = this.signaturePad.isEmpty();
      });
      
      // Отслеживаем изменения подписи
      this.signaturePad.addEventListener('afterUpdateStroke', () => {
        this.isEmpty = this.signaturePad.isEmpty();
      });
      
      // Обработчик изменения размера окна
      window.addEventListener('resize', this.resizeCanvas);
    },
    
    resizeCanvas() {
      const canvas = this.$refs.signatureCanvas;
      if (!canvas || !this.signaturePad) return;
      
      const rect = canvas.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      
      const ctx = canvas.getContext('2d');
      ctx.scale(dpr, dpr);
      
      this.signaturePad.clear();
    },
    
    clearSignature() {
      if (this.signaturePad) {
        this.signaturePad.clear();
        this.isEmpty = true;
      }
    },
    
    undoLastStroke() {
      if (this.signaturePad && !this.signaturePad.isEmpty()) {
        const data = this.signaturePad.toData();
        if (data.length > 0) {
          data.pop(); // Удаляем последний штрих
          this.signaturePad.fromData(data);
          this.isEmpty = this.signaturePad.isEmpty();
        }
      }
    },
    
    async saveSignature() {
      if (!this.signaturePad || this.signaturePad.isEmpty()) {
        this.$emit('error', 'Подпись не может быть пустой');
        return;
      }
      
      try {
        // Получаем подпись в формате base64
        const signatureData = this.signaturePad.toDataURL('image/png');
        
        // Отправляем на сервер
        const response = await this.saveSignatureToServer(signatureData);
        
        if (response.success) {
          this.savedSignature = signatureData;
          this.$emit('signature-saved', {
            signature: signatureData,
            documentId: this.documentId
          });
          
          // Показываем уведомление об успехе
          this.showSuccessMessage('Подпись успешно сохранена');
        } else {
          throw new Error(response.message || 'Ошибка при сохранении подписи');
        }
      } catch (error) {
        console.error('Ошибка при сохранении подписи:', error);
        this.$emit('error', error.message || 'Ошибка при сохранении подписи');
      }
    },
    
    async saveSignatureToServer(signatureData) {
      // Импортируем DocumentService
      const { DocumentService } = await import('../api/services');
      
      try {
        const response = await DocumentService.addSignature(this.documentId, signatureData);
        return response;
      } catch (error) {
        console.error('Ошибка при сохранении подписи:', error);
        throw error;
      }
    },
    
    showSuccessMessage(message) {
      // Простое уведомление об успехе
      const notification = document.createElement('div');
      notification.className = 'signature-success-notification';
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
    
    // Метод для загрузки существующей подписи
    loadSignature(signatureData) {
      if (signatureData && this.signaturePad) {
        // Создаем изображение из base64 данных
        const img = new Image();
        img.onload = () => {
          const canvas = this.$refs.signatureCanvas;
          const ctx = canvas.getContext('2d');
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          ctx.drawImage(img, 0, 0);
          this.isEmpty = false;
        };
        img.src = signatureData;
      }
    }
  }
};
</script>

<style scoped>
.signature-pad-container {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  margin-bottom: 1.5rem;
}

.signature-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-bottom: 1px solid #e5e7eb;
}

.signature-header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.signature-header h3 i {
  color: #6b7280;
}

.signature-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.btn-clear,
.btn-undo,
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

.btn-clear {
  background: #f3f4f6;
  color: #6b7280;
}

.btn-clear:hover:not(:disabled) {
  background: #e5e7eb;
  color: #374151;
}

.btn-undo {
  background: #fef3c7;
  color: #d97706;
}

.btn-undo:hover:not(:disabled) {
  background: #fde68a;
  color: #b45309;
}

.btn-save {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
}

.btn-save:hover:not(:disabled) {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
}

.btn-clear:disabled,
.btn-undo:disabled,
.btn-save:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.signature-canvas-container {
  padding: 1rem 1.5rem;
  background: #ffffff;
}

.signature-canvas {
  width: 100%;
  height: 200px;
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  cursor: crosshair;
  background: #fafafa;
  transition: all 0.2s ease;
}

.signature-canvas:hover {
  border-color: #9ca3af;
  background: #f9fafb;
}

.signature-canvas:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.signature-info {
  padding: 0.75rem 1.5rem;
  background: #f8f9fa;
  border-top: 1px solid #e5e7eb;
}

.signature-hint {
  margin: 0;
  font-size: 0.875rem;
  color: #6b7280;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.signature-hint i {
  color: #3b82f6;
}

.signature-preview {
  padding: 1rem 1.5rem;
  background: #f0f9ff;
  border-top: 1px solid #e0f2fe;
}

.signature-preview h4 {
  margin: 0 0 0.75rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #0c4a6e;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.signature-preview h4 i {
  color: #0284c7;
}

.preview-image {
  text-align: center;
  padding: 1rem;
  background: #ffffff;
  border-radius: 8px;
  border: 1px solid #e0f2fe;
}

.preview-image img {
  max-width: 100%;
  max-height: 150px;
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
  .signature-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
    padding: 1rem;
  }
  
  .signature-actions {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .btn-clear,
  .btn-undo,
  .btn-save {
    flex: 1;
    min-width: 120px;
    justify-content: center;
  }
  
  .signature-canvas-container {
    padding: 0.75rem 1rem;
  }
  
  .signature-canvas {
    height: 150px;
  }
  
  .signature-info,
  .signature-preview {
    padding: 0.75rem 1rem;
  }
}

@media (max-width: 480px) {
  .signature-actions {
    flex-direction: column;
  }
  
  .btn-clear,
  .btn-undo,
  .btn-save {
    width: 100%;
  }
  
  .signature-canvas {
    height: 120px;
  }
}
</style>
