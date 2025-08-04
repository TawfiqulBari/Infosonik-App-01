-- Initial database schema for Infosonik App
-- Updated to include group management and detailed expense tracking

-- Roles table for RBAC
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    permissions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users table
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

-- User Groups for team organization
CREATE TABLE user_groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Group memberships (many-to-many relationship)
CREATE TABLE group_memberships (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    group_id INTEGER REFERENCES user_groups(id),
    role VARCHAR(255) DEFAULT 'member', -- member, admin, moderator
    added_by INTEGER REFERENCES users(id),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, group_id)
);

-- Notes table
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(255),
    content TEXT,
    language VARCHAR(10),
    theme VARCHAR(255) DEFAULT 'light',
    attachments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Events table
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(255),
    description TEXT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    google_event_id VARCHAR(255),
    attachments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- File attachments
CREATE TABLE file_attachments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    filename VARCHAR(255),
    original_filename VARCHAR(255),
    file_type VARCHAR(255),
    file_size INTEGER,
    file_path VARCHAR(255),
    google_drive_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User sessions for OAuth
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    access_token TEXT,
    refresh_token TEXT,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Leave applications
CREATE TABLE leave_applications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    leave_type VARCHAR(255),
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    days_requested INTEGER,
    reason TEXT,
    status VARCHAR(255) DEFAULT 'pending',
    approved_by INTEGER REFERENCES users(id),
    approval_date TIMESTAMP,
    approval_comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Updated convenience bills with detailed breakdown
CREATE TABLE convenience_bills (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    bill_date TIMESTAMP NOT NULL,
    
    -- Transportation costs in BDT (stored in paisa - 1 BDT = 100 paisa)
    transport_amount INTEGER DEFAULT 0,
    transport_description TEXT,
    
    -- Transportation details
    transport_to VARCHAR(255),
    transport_from VARCHAR(255),
    means_of_transportation VARCHAR(255),
    
    -- Food costs in BDT (stored in paisa)
    food_amount INTEGER DEFAULT 0,
    food_description TEXT,
    
    -- Other costs in BDT (stored in paisa)
    other_amount INTEGER DEFAULT 0,
    other_description TEXT,
    
    -- Additional cost breakdown in BDT (stored in paisa)
    fuel_cost INTEGER DEFAULT 0,
    rental_cost INTEGER DEFAULT 0,
    
    -- Total amount (auto-computed)
    total_amount INTEGER GENERATED ALWAYS AS (transport_amount + food_amount + other_amount + fuel_cost + rental_cost) STORED,
    
    -- Additional fields
    general_description TEXT,
    receipt_file_id INTEGER REFERENCES file_attachments(id),
    status VARCHAR(255) DEFAULT 'pending',
    approved_by INTEGER REFERENCES users(id),
    approval_date TIMESTAMP,
    approval_comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sales management tables
CREATE TABLE meddpicc (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
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
    user_id INTEGER REFERENCES users(id),
    opportunity_name VARCHAR(255),
    client_name VARCHAR(255),
    stage VARCHAR(255),
    probability INTEGER,
    amount INTEGER, -- Amount in BDT paisa
    closing_date TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_google_id ON users(google_id);
CREATE INDEX idx_group_memberships_user_id ON group_memberships(user_id);
CREATE INDEX idx_group_memberships_group_id ON group_memberships(group_id);
CREATE INDEX idx_convenience_bills_user_id ON convenience_bills(user_id);
CREATE INDEX idx_convenience_bills_status ON convenience_bills(status);
CREATE INDEX idx_convenience_bills_bill_date ON convenience_bills(bill_date);
CREATE INDEX idx_leave_applications_user_id ON leave_applications(user_id);
CREATE INDEX idx_leave_applications_status ON leave_applications(status);
CREATE INDEX idx_notes_user_id ON notes(user_id);
CREATE INDEX idx_events_user_id ON events(user_id);

-- Insert default roles
INSERT INTO roles (name, description, permissions) VALUES 
('Admin', 'Full system administrator with all permissions', '["all"]'),
('HR', 'Human Resources - manage leave applications and user data', '["manage_leave", "view_users", "manage_bills", "manage_groups"]'),
('Accounts', 'Accounts department - manage convenience bills and financial data', '["manage_bills", "view_financial_reports"]'),
('Sales', 'Sales team members', '["view_sales_data", "manage_sales_data", "manage_client_notes"]'),
('Technical', 'Technical team members', '["view_technical_docs", "manage_project_notes"]');

-- Insert default groups
INSERT INTO user_groups (name, description, created_by) VALUES 
('Management', 'Senior management team', 1),
('Sales Team', 'Sales and business development team', 1),
('Technical Team', 'Software development and technical team', 1),
('HR Department', 'Human resources department', 1),
('Accounts Department', 'Finance and accounting department', 1);

-- Add indexes for clients table
CREATE INDEX IF NOT EXISTS idx_clients_company_name ON clients(company_name);
CREATE INDEX IF NOT EXISTS idx_clients_is_active ON clients(is_active);

