CREATE SCHEMA IF NOT EXISTS `app` DEFAULT CHARACTER SET utf8mb4;
USE `app`;

CREATE TABLE IF NOT EXISTS `users` (
    `id` VARCHAR(255) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `created_at` DATETIME NOT NULL,
    `updated_at` DATETIME NOT NULL,
    PRIMARY KEY (`id`)
)
ENGINE = InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `documents` (
    `id` VARCHAR(255) NOT NULL,
    `user_id` VARCHAR(255) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `description` VARCHAR(255) NOT NULL,
    `gs_file_url` VARCHAR(255) NOT NULL,
    `status` int(11) NOT NULL,
    `created_at` DATETIME NOT NULL,
    `updated_at` DATETIME NOT NULL,
    PRIMARY KEY (`id`),
    INDEX `idx_user_id` (`user_id` ASC),
    CONSTRAINT `fk_documents_users`
        FOREIGN KEY (`user_id`)
        REFERENCES `users` (`id`)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION
)
ENGINE = InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `openai_assistants` (
    `document_id` VARCHAR(255) NOT NULL,
    `assistant_id` VARCHAR(255) NOT NULL,
    `thread_id` VARCHAR(255) NOT NULL,
    `used_at` DATETIME NOT NULL,
    `created_at` DATETIME NOT NULL,
    `updated_at` DATETIME NOT NULL,
    PRIMARY KEY (`document_id`),
    CONSTRAINT `fk_openai_assistants_documents`
        FOREIGN KEY (`document_id`)
        REFERENCES `documents` (`id`)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION
)
ENGINE = InnoDB DEFAULT CHARSET=utf8mb4;