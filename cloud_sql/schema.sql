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
CREATE INDEX IF NOT EXISTS idx_pager ON documents (created_at DESC, id DESC);

CREATE TABLE IF NOT EXISTS document_summaries (
    id VARCHAR(255) PRIMARY KEY,
    document_id VARCHAR(255) NOT NULL,
    text TEXT NOT NULL,
    index INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
ALTER TABLE document_summaries
    ADD CONSTRAINT fk_document_summaries_documents
    FOREIGN KEY (document_id)
    REFERENCES documents (id)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;
CREATE INDEX IF NOT EXISTS idx_document_id ON document_summaries (document_id);

CREATE TABLE IF NOT EXISTS assistants (
    document_id VARCHAR(255) PRIMARY KEY,
    assistant_id VARCHAR(255) NOT NULL,
    thread_id VARCHAR(255) NOT NULL,
    used_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
ALTER TABLE assistants
    ADD CONSTRAINT fk_assistants_documents
    FOREIGN KEY (document_id)
    REFERENCES documents (id)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;