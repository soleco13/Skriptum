-- SQL-код для создания таблицы myapp_userprofile

CREATE TABLE myapp_userprofile (
    id SERIAL PRIMARY KEY,
    position VARCHAR(100) NULL,
    department VARCHAR(100) NULL,
    phone VARCHAR(20) NULL,
    avatar VARCHAR(255) NULL,
    user_id INTEGER NOT NULL UNIQUE,
    FOREIGN KEY (user_id) REFERENCES auth_user (id) ON DELETE CASCADE
);

-- Создание индекса для внешнего ключа
CREATE INDEX myapp_userprofile_user_id_idx ON myapp_userprofile (user_id);

-- Комментарий: эта таблица связана с моделью UserProfile в Django
-- и хранит дополнительную информацию о пользователях системы.
-- Поле user_id связывает профиль с пользователем из таблицы auth_user.