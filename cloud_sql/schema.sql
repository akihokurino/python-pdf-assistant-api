CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE IF NOT EXISTS documents (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(255) NOT NULL,
    gs_file_url VARCHAR(255) NOT NULL,
    status INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
ALTER TABLE documents
    ADD CONSTRAINT fk_documents_users
    FOREIGN KEY (user_id)
    REFERENCES users (id)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;
CREATE INDEX IF NOT EXISTS idx_user_id ON documents (user_id);

CREATE TABLE IF NOT EXISTS openai_assistants (
    document_id VARCHAR(255) NOT NULL,
    assistant_id VARCHAR(255) NOT NULL,
    thread_id VARCHAR(255) NOT NULL,
    used_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    PRIMARY KEY (document_id)
);
ALTER TABLE openai_assistants
    ADD CONSTRAINT fk_openai_assistants_documents
    FOREIGN KEY (document_id)
    REFERENCES documents (id)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;