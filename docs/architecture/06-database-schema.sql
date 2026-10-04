-- PostgreSQL schema for the GIS platform.
-- UUID generation uses pgcrypto. No GIS extension is required by the base schema.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_subject VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(320),
    display_name VARCHAR(200),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE organization_members (
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (organization_id, user_id)
);

CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_projects_org ON projects(organization_id);

CREATE TABLE project_members (
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (project_id, user_id)
);

CREATE TABLE datasets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    project_id UUID NOT NULL REFERENCES projects(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    dataset_type VARCHAR(50) NOT NULL,
    source_format VARCHAR(100) NOT NULL,
    status VARCHAR(30) NOT NULL,
    current_version_id UUID,
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT datasets_status_chk CHECK (
        status IN ('UPLOADING','UPLOADED','VALIDATING','VALIDATED','PROCESSING','READY','FAILED','ARCHIVED')
    )
);

CREATE INDEX idx_datasets_project ON datasets(project_id);
CREATE INDEX idx_datasets_status ON datasets(status);
CREATE INDEX idx_datasets_format ON datasets(source_format);

CREATE TABLE dataset_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id UUID NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    source_object_key TEXT NOT NULL,
    source_sha256 CHAR(64) NOT NULL,
    source_size_bytes BIGINT NOT NULL,
    detected_format VARCHAR(100),
    crs VARCHAR(100),
    bbox_min_x DOUBLE PRECISION,
    bbox_min_y DOUBLE PRECISION,
    bbox_max_x DOUBLE PRECISION,
    bbox_max_y DOUBLE PRECISION,
    min_z DOUBLE PRECISION,
    max_z DOUBLE PRECISION,
    vertical_datum VARCHAR(100),
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    status VARCHAR(30) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(dataset_id, version_number)
);

CREATE INDEX idx_dataset_versions_dataset ON dataset_versions(dataset_id);
CREATE INDEX idx_dataset_versions_bbox
    ON dataset_versions(bbox_min_x, bbox_min_y, bbox_max_x, bbox_max_y);

ALTER TABLE datasets
    ADD CONSTRAINT datasets_current_version_fk
    FOREIGN KEY (current_version_id) REFERENCES dataset_versions(id);

CREATE TABLE dataset_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_version_id UUID NOT NULL REFERENCES dataset_versions(id) ON DELETE CASCADE,
    asset_type VARCHAR(50) NOT NULL,
    object_key TEXT NOT NULL,
    content_type VARCHAR(200),
    size_bytes BIGINT,
    sha256 CHAR(64),
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_dataset_assets_version ON dataset_assets(dataset_version_id);
CREATE INDEX idx_dataset_assets_type ON dataset_assets(asset_type);

CREATE TABLE layers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    dataset_version_id UUID NOT NULL REFERENCES dataset_versions(id),
    name VARCHAR(200) NOT NULL,
    layer_type VARCHAR(50) NOT NULL,
    visible BOOLEAN NOT NULL DEFAULT true,
    opacity DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    min_zoom DOUBLE PRECISION,
    max_zoom DOUBLE PRECISION,
    z_index INTEGER NOT NULL DEFAULT 0,
    style_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    source_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT layers_opacity_chk CHECK (opacity >= 0 AND opacity <= 1)
);

CREATE INDEX idx_layers_project ON layers(project_id);

CREATE TABLE processing_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    dataset_id UUID REFERENCES datasets(id),
    dataset_version_id UUID REFERENCES dataset_versions(id),
    job_type VARCHAR(80) NOT NULL,
    status VARCHAR(30) NOT NULL,
    progress DOUBLE PRECISION NOT NULL DEFAULT 0,
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    error_code VARCHAR(100),
    error_message TEXT,
    parameters_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    result_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    CONSTRAINT processing_jobs_progress_chk CHECK (progress >= 0 AND progress <= 100)
);

CREATE INDEX idx_processing_jobs_status ON processing_jobs(status);
CREATE INDEX idx_processing_jobs_dataset ON processing_jobs(dataset_id);

CREATE TABLE map_views (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    view_json JSONB NOT NULL,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE audit_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,
    request_id VARCHAR(100),
    trace_id VARCHAR(100),
    result VARCHAR(30) NOT NULL,
    details_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_audit_org_time ON audit_events(organization_id, created_at DESC);

CREATE TABLE outbox_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    aggregate_type VARCHAR(100) NOT NULL,
    aggregate_id UUID NOT NULL,
    event_type VARCHAR(150) NOT NULL,
    event_version INTEGER NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    published_at TIMESTAMPTZ
);

CREATE INDEX idx_outbox_unpublished ON outbox_events(published_at) WHERE published_at IS NULL;
