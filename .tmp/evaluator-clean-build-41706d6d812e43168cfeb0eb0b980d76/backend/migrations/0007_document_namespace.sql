ALTER TABLE release_document_uses DROP CONSTRAINT pk_release_document_uses;
ALTER TABLE release_document_uses ADD CONSTRAINT pk_release_document_uses PRIMARY KEY(run_id,byte_sha256);
