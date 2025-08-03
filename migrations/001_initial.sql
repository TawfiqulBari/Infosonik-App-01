CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    permissions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    google_id VARCHAR(255) UNIQUE,
    profile_picture VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    role_id INTEGER REFERENCES roles (id),
    preferences TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    title VARCHAR(255),
    content TEXT,
    language VARCHAR(10),
    theme VARCHAR(255) DEFAULT 'light',
    attachments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    title VARCHAR(255),
    description TEXT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    google_event_id VARCHAR(255),
    attachments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE file_attachments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    filename VARCHAR(255),
    original_filename VARCHAR(255),
    file_type VARCHAR(255),
    file_size INTEGER,
    file_path VARCHAR(255),
    google_drive_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    access_token TEXT,
    refresh_token TEXT,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE leave_applications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    leave_type VARCHAR(255),
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    days_requested INTEGER,
    reason TEXT,
    status VARCHAR(255) DEFAULT 'pending',
    approved_by INTEGER,
    approval_date TIMESTAMP,
    approval_comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE convenience_bills (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    week_start_date TIMESTAMP,
    week_end_date TIMESTAMP,
    total_amount INTEGER,
    description TEXT,
    receipt_file_id INTEGER,
    status VARCHAR(255) DEFAULT 'pending',
    approved_by INTEGER,
    approval_date TIMESTAMP,
    approval_comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE group_memberships (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    group_id INTEGER,
    role VARCHAR(255) DEFAULT 'member',
    added_by INTEGER,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE meddpicc (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    client_name VARCHAR(255),
    opportunity_name VARCHAR(255),
    metrics TEXT,
    economic_buyer TEXT,
    decision_criteria TEXT,
    decision_process TEXT,
    paper_process TEXT,
    identify_pain TEXT,
    champion TEXT,
    competition TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sales_funnel (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    opportunity_name VARCHAR(255),
    client_name VARCHAR(255),
    stage VARCHAR(255),
    probability INTEGER,
    amount INTEGER,
    closing_date TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
