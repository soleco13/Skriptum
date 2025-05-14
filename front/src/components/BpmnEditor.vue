<template>
  <div class="bpmn-editor-container">
    <div class="bpmn-toolbar">
      <button @click="saveDiagram">Сохранить</button>
      <button @click="exportDiagram">Экспорт</button>
      <label>
        Импорт
        <input type="file" @change="importDiagram" accept=".bpmn, .xml" style="display:none" />
      </label>
      <div>
        <button @click="zoomIn">+</button>
        <button @click="zoomOut">-</button>
        <button @click="resetZoom">⟲</button>
      </div>
    </div>
    
    <!-- Контейнер для BPMN-редактора с фиксированной высотой -->
    <div style="width: 100%; height: 600px; border: 1px solid #ccc;">
      <div ref="canvas" style="width: 100%; height: 100%;"></div>
    </div>
  </div>
</template>

<script>
import BpmnModeler from 'bpmn-js/lib/Modeler';
import { emptyBpmn } from '../utils/bpmn-templates';
import { BpmnService } from '../api/bpmn-service';

export default {
  name: 'BpmnEditor',
  props: {
    diagramId: {
      type: [String, Number],
      default: null
    },
    initialXml: {
      type: String,
      default: null
    }
  },
  data() {
    return {
      modeler: null,
      currentXml: null,
      isModified: false
    };
  },
  mounted() {
    // Инициализируем сервис BPMN
    this.$bpmnService = BpmnService;
    
    this.initModeler();
    
    // Загружаем диаграмму, если передан ID или XML
    if (this.initialXml) {
      this.loadXml(this.initialXml);
    } else if (this.diagramId) {
      this.loadDiagram(this.diagramId);
    } else {
      this.createNewDiagram();
    }
    
    // Обработчик изменений для отслеживания модификаций
    window.addEventListener('beforeunload', this.handleBeforeUnload);
  },
  beforeUnmount() {
    window.removeEventListener('beforeunload', this.handleBeforeUnload);
    if (this.modeler) {
      this.modeler.destroy();
    }
  },
  methods: {
    initModeler() {
      console.log('Инициализация BPMN-редактора');
      // Проверяем, что контейнер существует и имеет размеры перед инициализацией
      if (!this.$refs.canvas) {
        console.error('Контейнер для BPMN-редактора не существует');
        // Отложенная инициализация, чтобы дать контейнеру время на рендеринг
        setTimeout(() => this.initModeler(), 100);
        return;
      }
      
      try {
        // Инициализация модулера BPMN с минимальными опциями
        this.modeler = new BpmnModeler({
          container: this.$refs.canvas
        });
        
        // Подписываемся на события изменения диаграммы
        this.modeler.on('element.changed', () => {
          this.isModified = true;
        });
        
        this.modeler.on('shape.added', () => {
          this.isModified = true;
        });
      } catch (error) {
        console.error('Ошибка при инициализации BPMN-модулера:', error);
        this.$emit('error', 'Не удалось инициализировать редактор BPMN');
      }
      
      // Обработчики событий для отслеживания изменений
      try {
        this.modeler.on('shape.removed', () => {
          this.isModified = true;
        });
        
        this.modeler.on('connection.added', () => {
          this.isModified = true;
        });
        
        this.modeler.on('connection.removed', () => {
          this.isModified = true;
        });
      } catch (error) {
        console.error('Ошибка при установке обработчиков событий:', error);
      }
    },
    
    async loadDiagram(id) {
      try {
        // Загрузка диаграммы с сервера по ID
        const response = await this.$bpmnService.getDiagram(id);
        if (response && response.xml) {
          this.loadXml(response.xml);
          this.currentXml = response.xml;
          this.isModified = false;
        }
      } catch (error) {
        console.error('Ошибка при загрузке диаграммы:', error);
        this.$emit('error', 'Не удалось загрузить диаграмму');
      }
    },
    
    loadXml(xml) {
      // Проверяем, что модулер инициализирован
      if (!this.modeler) {
        console.error('BPMN-модулер не инициализирован');
        this.$emit('error', 'Редактор BPMN не инициализирован');
        return;
      }
      
      // Загрузка XML в редактор
      this.modeler.importXML(xml)
        .then(({ warnings }) => {
          if (warnings.length) {
            console.warn('Предупреждения при загрузке BPMN:', warnings);
          }
          
          try {
            // Безопасный вызов масштабирования с обработкой ошибок
            const canvas = this.modeler.get('canvas');
            if (canvas) {
              // Добавляем небольшую задержку для корректного рендеринга
              setTimeout(() => {
                try {
                  canvas.zoom('fit-viewport');
                } catch (e) {
                  console.error('Ошибка при масштабировании после загрузки:', e);
                }
              }, 50);
            }
            
            this.currentXml = xml;
            this.isModified = false;
          } catch (zoomError) {
            console.error('Ошибка при настройке масштаба:', zoomError);
            // Продолжаем работу даже при ошибке масштабирования
            this.currentXml = xml;
            this.isModified = false;
          }
        })
        .catch(error => {
          console.error('Ошибка при импорте BPMN:', error);
          this.$emit('error', 'Ошибка при загрузке диаграммы');
        });
    },
    
    createNewDiagram() {
      // Создание новой пустой диаграммы
      this.loadXml(emptyBpmn);
    },
    
    async saveDiagram() {
      try {
        // Получаем XML текущей диаграммы
        const { xml } = await this.modeler.saveXML({ format: true });
        
        // Если есть ID диаграммы, обновляем существующую, иначе создаем новую
        let response;
        if (this.diagramId) {
          response = await this.$bpmnService.updateDiagram(this.diagramId, xml);
        } else {
          response = await this.$bpmnService.createDiagram({
            name: 'Новая диаграмма',
            xml: xml
          });
          
          // Если создана новая диаграмма, обновляем ID
          if (response && response.id) {
            this.$emit('diagram-created', response.id);
          }
        }
        
        this.currentXml = xml;
        this.isModified = false;
        this.$emit('saved', response);
      } catch (error) {
        console.error('Ошибка при сохранении диаграммы:', error);
        this.$emit('error', 'Не удалось сохранить диаграмму');
      }
    },
    
    async exportDiagram() {
      try {
        // Экспорт диаграммы в XML
        const { xml } = await this.modeler.saveXML({ format: true });
        
        // Создаем файл для скачивания
        const blob = new Blob([xml], { type: 'application/xml' });
        const url = URL.createObjectURL(blob);
        
        // Создаем ссылку для скачивания и эмулируем клик
        const a = document.createElement('a');
        a.href = url;
        a.download = `bpmn-diagram-${new Date().toISOString().slice(0, 10)}.bpmn`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      } catch (error) {
        console.error('Ошибка при экспорте диаграммы:', error);
        this.$emit('error', 'Не удалось экспортировать диаграмму');
      }
    },
    
    importDiagram(event) {
      const file = event.target.files[0];
      if (!file) return;
      
      const reader = new FileReader();
      reader.onload = (e) => {
        const xml = e.target.result;
        this.loadXml(xml);
      };
      reader.readAsText(file);
      
      // Сбрасываем значение input, чтобы можно было загрузить тот же файл повторно
      event.target.value = '';
    },
    
    zoomIn() {
      try {
        const canvas = this.modeler.get('canvas');
        if (canvas) {
          canvas.zoom(1.1, { x: 'center', y: 'center' });
        }
      } catch (error) {
        console.error('Ошибка при увеличении масштаба:', error);
        this.$emit('error', 'Не удалось изменить масштаб');
      }
    },
    
    zoomOut() {
      try {
        const canvas = this.modeler.get('canvas');
        if (canvas) {
          canvas.zoom(0.9, { x: 'center', y: 'center' });
        }
      } catch (error) {
        console.error('Ошибка при уменьшении масштаба:', error);
        this.$emit('error', 'Не удалось изменить масштаб');
      }
    },
    
    resetZoom() {
      try {
        const canvas = this.modeler.get('canvas');
        if (canvas) {
          canvas.zoom('fit-viewport');
        }
      } catch (error) {
        console.error('Ошибка при сбросе масштаба:', error);
        this.$emit('error', 'Не удалось сбросить масштаб');
      }
    },
    
    handleBeforeUnload(event) {
      if (this.isModified) {
        const message = 'У вас есть несохраненные изменения. Вы уверены, что хотите покинуть страницу?';
        event.returnValue = message;
        return message;
      }
    }
  }
};
</script>

<style>
/* Только базовые стили BPMN.js */
@import 'bpmn-js/dist/assets/diagram-js.css';
@import 'bpmn-js/dist/assets/bpmn-font/css/bpmn.css';

/* Минимальные стили для работы редактора */
.bpmn-editor-container {
  width: 100%;
  height: 100%;
}

.bpmn-toolbar {
  padding: 5px;
  margin-bottom: 5px;
}

.bpmn-toolbar button,
.bpmn-toolbar label {
  margin-right: 5px;
  padding: 3px 8px;
  cursor: pointer;
}
</style>