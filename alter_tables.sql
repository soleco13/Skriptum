-- SQL-скрипт для добавления связи с пользователями в существующие таблицы

-- Добавление поля user_id в таблицу documents
ALTER TABLE documents
ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1;

-- Создание внешнего ключа для таблицы documents
ALTER TABLE documents
ADD CONSTRAINT fk_documents_user
FOREIGN KEY (user_id) REFERENCES auth_user (id);

-- Создание индекса для ускорения поиска по user_id в таблице documents
CREATE INDEX idx_documents_user_id ON documents (user_id);

-- Добавление поля user_id в таблицу tasks
ALTER TABLE tasks
ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1;

-- Создание внешнего ключа для таблицы tasks
ALTER TABLE tasks
ADD CONSTRAINT fk_tasks_user
FOREIGN KEY (user_id) REFERENCES auth_user (id);

-- Создание индекса для ускорения поиска по user_id в таблице tasks
CREATE INDEX idx_tasks_user_id ON tasks (user_id);

-- Добавление поля user_id в таблицу processes
ALTER TABLE processes
ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1;

-- Создание внешнего ключа для таблицы processes
ALTER TABLE processes
ADD CONSTRAINT fk_processes_user
FOREIGN KEY (user_id) REFERENCES auth_user (id);

-- Создание индекса для ускорения поиска по user_id в таблице processes
CREATE INDEX idx_processes_user_id ON processes (user_id);

-- Примечание: DEFAULT 1 установлен для существующих записей, чтобы они были
-- связаны с первым пользователем (обычно администратором). При необходимости
-- это значение можно изменить на ID нужного пользователя.