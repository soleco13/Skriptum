-- SQL-запрос для добавления пользователя с id=1 в таблицу auth_user

INSERT INTO auth_user (
    id,
    password,
    last_login,
    is_superuser,
    username,
    first_name,
    last_name,
    email,
    is_staff,
    is_active,
    date_joined
) VALUES (
    1,
    'pbkdf2_sha256$600000$5FmABh9nGzBXHQvPNYeQDH$ZQpXCxXQaUKLXmIJgPUGsJL8ooLvYYR4QaKwvUJYYKQ=', -- хешированный пароль 'admin123'
    NULL, -- last_login может быть NULL
    FALSE, -- не суперпользователь
    'user1', -- имя пользователя
    'Имя', -- имя
    'Фамилия', -- фамилия
    'user1@example.com', -- email
    FALSE, -- не сотрудник администрации
    TRUE, -- активный пользователь
    CURRENT_TIMESTAMP -- текущая дата и время для date_joined
);

-- Примечание: Этот запрос добавляет пользователя с id=1, который используется
-- как значение по умолчанию для внешних ключей в таблицах documents, tasks и processes.
-- Пароль хеширован с использованием алгоритма PBKDF2 с SHA256, который используется в Django по умолчанию.
-- Пароль в открытом виде: 'admin123'