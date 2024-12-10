-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Хост: 127.0.0.1:3306
-- Время создания: Ноя 29 2024 г., 05:39
-- Версия сервера: 8.0.30
-- Версия PHP: 7.2.34

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- База данных: `crypto_db-copy`
--

-- --------------------------------------------------------

--
-- Структура таблицы `decryption_log`
--

CREATE TABLE `decryption_log` (
  `id` int NOT NULL,
  `encrypted_text` text,
  `decrypted_text` text,
  `decryption_key` blob,
  `user_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `encryption_log`
--

CREATE TABLE `encryption_log` (
  `id` int NOT NULL,
  `original_text` text,
  `encrypted_text` text,
  `encryption_key` blob,
  `user_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `users`
--

CREATE TABLE `users` (
  `id` int NOT NULL,
  `username` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `keyword_hash` varchar(255) NOT NULL,
  `user_type` enum('Admin','User') NOT NULL DEFAULT 'User'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Дамп данных таблицы `users`
--

INSERT INTO `users` (`id`, `username`, `password_hash`, `email`, `keyword_hash`, `user_type`) VALUES
(1, 'root', '$2b$12$XxJqhjIyXt7CUi84U1dmHObpY3sQIxGsX6kxTyz93OsEaIRFfCZl6', 'root@root.root', '$2b$12$feBry9JPrPS4iRxoIdKP2Ob9YKR1UhuPxswkwWfo.gHclKeUfXRLC', 'Admin');

-- --------------------------------------------------------

--
-- Структура таблицы `user_actions`
--

CREATE TABLE `user_actions` (
  `id` int NOT NULL,
  `user_id` int NOT NULL,
  `action_type` varchar(50) NOT NULL,
  `timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Дамп данных таблицы `user_actions`
--

INSERT INTO `user_actions` (`id`, `user_id`, `action_type`, `timestamp`) VALUES
(1, 1, 'Регистрация', '2024-11-29 02:39:18');

--
-- Индексы сохранённых таблиц
--

--
-- Индексы таблицы `decryption_log`
--
ALTER TABLE `decryption_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_decryption_log_user` (`user_id`);

--
-- Индексы таблицы `encryption_log`
--
ALTER TABLE `encryption_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_encryption_log_user` (`user_id`);

--
-- Индексы таблицы `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Индексы таблицы `user_actions`
--
ALTER TABLE `user_actions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- AUTO_INCREMENT для сохранённых таблиц
--

--
-- AUTO_INCREMENT для таблицы `decryption_log`
--
ALTER TABLE `decryption_log`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `encryption_log`
--
ALTER TABLE `encryption_log`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `users`
--
ALTER TABLE `users`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT для таблицы `user_actions`
--
ALTER TABLE `user_actions`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- Ограничения внешнего ключа сохраненных таблиц
--

--
-- Ограничения внешнего ключа таблицы `decryption_log`
--
ALTER TABLE `decryption_log`
  ADD CONSTRAINT `fk_decryption_log_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Ограничения внешнего ключа таблицы `encryption_log`
--
ALTER TABLE `encryption_log`
  ADD CONSTRAINT `fk_encryption_log_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Ограничения внешнего ключа таблицы `user_actions`
--
ALTER TABLE `user_actions`
  ADD CONSTRAINT `user_actions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
