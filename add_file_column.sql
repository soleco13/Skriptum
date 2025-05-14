-- SQL-запрос для добавления столбца file в таблицу documents
ALTER TABLE documents
ADD COLUMN file VARCHAR(255) NULL;

-- Добавление столбцов file_type и content, которые есть в модели Django
-- но отсутствуют в базе данных

ALTER TABLE documents
ADD COLUMN file_type VARCHAR(10) NULL;

ALTER TABLE documents
ADD COLUMN content TEXT NULL;