<template>
  <div class="documents">
    <div class="documents-header">
      <h1>Документы</h1>
      <button>
        <i class="fas fa-plus"></i> Создать документ
      </button>
    </div>

    <div class="notification success">
      <i class="fas fa-info-circle"></i>
      Документы успешно загружены
    </div>

    <div class="documents-filters">
      <input type="text" placeholder="Поиск документов..." class="search-input">
      <select class="filter-select">
        <option value="">Все типы</option>
        <option value="contract">Договоры</option>
        <option value="invoice">Счета</option>
        <option value="report">Отчеты</option>
      </select>
      <select class="filter-select">
        <option value="">Все статусы</option>
        <option value="draft">Черновик</option>
        <option value="review">На рассмотрении</option>
        <option value="approved">Утверждено</option>
      </select>
    </div>

    <table>
      <thead>
        <tr>
          <th>Название</th>
          <th>Тип</th>
          <th>Статус</th>
          <th>Дата создания</th>
          <th>Действия</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="doc in documents" :key="doc.id">
          <td>{{ doc.name }}</td>
          <td>{{ doc.type }}</td>
          <td>
            <span :class="'status-badge ' + doc.status">{{ doc.status }}</span>
          </td>
          <td>{{ doc.created }}</td>
          <td class="actions">
            <button><i class="fas fa-eye"></i></button>
            <button><i class="fas fa-edit"></i></button>
            <button><i class="fas fa-trash"></i></button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  name: 'DocumentsList',
  data() {
    return {
      documents: [
        {
          id: 1,
          name: 'Договор поставки №123',
          type: 'Договор',
          status: 'review',
          created: '2024-03-20'
        },
        // Добавьте больше документов здесь
      ]
    }
  }
}
</script>

