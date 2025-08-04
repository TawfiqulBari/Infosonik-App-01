-- Migration for Role-Based Access Control and Enhanced Reporting Features
-- Date: 2025-08-04
-- Description: Add RBAC permissions, expense modification, reporting, and receipt handling

-- Enhanced roles table with detailed permissions
ALTER TABLE roles 
    ADD COLUMN IF NOT EXISTS module_permissions JSONB DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS group_access JSONB DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS can_approve_expenses BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS can_view_all_expenses BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS can_generate_reports BOOLEAN DEFAULT FALSE;

-- User permissions override table (for individual user permissions)
CREATE TABLE IF NOT EXISTS user_permissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    module VARCHAR(255),
    permission VARCHAR(255), -- 'read', 'write', 'modify', 'delete', 'approve'
    granted_by INTEGER REFERENCES users(id),
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, module, permission)
);

-- Group permissions table
CREATE TABLE IF NOT EXISTS group_permissions (
    id SERIAL PRIMARY KEY,
    group_id INTEGER REFERENCES user_groups(id),
    module VARCHAR(255),
    permission VARCHAR(255),
    granted_by INTEGER REFERENCES users(id),
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(group_id, module, permission)
);

-- Expense modification tracking
CREATE TABLE IF NOT EXISTS expense_modifications (
    id SERIAL PRIMARY KEY,
    expense_id INTEGER REFERENCES convenience_bills(id),
    modified_by INTEGER REFERENCES users(id),
    modification_type VARCHAR(50), -- 'created', 'updated', 'approved', 'rejected'
    old_values JSONB,
    new_values JSONB,
    modification_reason TEXT,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Report generation tracking
CREATE TABLE IF NOT EXISTS generated_reports (
    id SERIAL PRIMARY KEY,
    report_type VARCHAR(100), -- 'user_monthly', 'group_monthly', 'admin_summary'
    report_period VARCHAR(50), -- 'daily', 'weekly', 'monthly', 'yearly'
    start_date DATE,
    end_date DATE,
    user_id INTEGER REFERENCES users(id),
    group_id INTEGER REFERENCES user_groups(id),
    generated_by INTEGER REFERENCES users(id),
    file_path VARCHAR(500),
    file_format VARCHAR(10), -- 'pdf', 'excel', 'csv', 'docx'
    share_link VARCHAR(500),
    drive_file_id VARCHAR(255),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

-- Receipt attachments table (enhanced file attachments for receipts)
CREATE TABLE IF NOT EXISTS receipt_attachments (
    id SERIAL PRIMARY KEY,
    expense_id INTEGER REFERENCES convenience_bills(id),
    file_attachment_id INTEGER REFERENCES file_attachments(id),
    receipt_type VARCHAR(50), -- 'transport', 'food', 'fuel', 'rental', 'other'
    uploaded_by INTEGER REFERENCES users(id),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add expense approval workflow fields
ALTER TABLE convenience_bills
    ADD COLUMN IF NOT EXISTS approval_required BOOLEAN DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS last_modified_by INTEGER REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS last_modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ADD COLUMN IF NOT EXISTS modification_reason TEXT,
    ADD COLUMN IF NOT EXISTS can_be_modified BOOLEAN DEFAULT TRUE;

-- Enhanced file attachments for image receipts
ALTER TABLE file_attachments
    ADD COLUMN IF NOT EXISTS is_image BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS image_width INTEGER,
    ADD COLUMN IF NOT EXISTS image_height INTEGER,
    ADD COLUMN IF NOT EXISTS thumbnail_path VARCHAR(500);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_permissions_user_id ON user_permissions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_permissions_module ON user_permissions(module);
CREATE INDEX IF NOT EXISTS idx_group_permissions_group_id ON group_permissions(group_id);
CREATE INDEX IF NOT EXISTS idx_expense_modifications_expense_id ON expense_modifications(expense_id);
CREATE INDEX IF NOT EXISTS idx_generated_reports_user_id ON generated_reports(user_id);
CREATE INDEX IF NOT EXISTS idx_generated_reports_group_id ON generated_reports(group_id);
CREATE INDEX IF NOT EXISTS idx_convenience_bills_last_modified ON convenience_bills(last_modified_at);
CREATE INDEX IF NOT EXISTS idx_receipt_attachments_expense_id ON receipt_attachments(expense_id);
CREATE INDEX IF NOT EXISTS idx_file_attachments_is_image ON file_attachments(is_image);

-- Update existing roles with enhanced permissions
UPDATE roles SET 
    module_permissions = '{
        "expenses": ["read", "write", "approve", "modify", "delete"],
        "users": ["read", "write", "modify", "delete"],
        "groups": ["read", "write", "modify", "delete"],
        "reports": ["read", "write", "generate", "export", "share"]
    }',
    can_approve_expenses = TRUE,
    can_view_all_expenses = TRUE,
    can_generate_reports = TRUE
WHERE name = 'Admin';

UPDATE roles SET 
    module_permissions = '{
        "expenses": ["read", "approve"],
        "users": ["read"],
        "groups": ["read"],
        "reports": ["read", "generate", "export"]
    }',
    can_approve_expenses = TRUE,
    can_view_all_expenses = TRUE,
    can_generate_reports = TRUE
WHERE name = 'HR';

UPDATE roles SET 
    module_permissions = '{
        "expenses": ["read", "approve"],
        "reports": ["read", "generate", "export", "share"]
    }',
    can_approve_expenses = TRUE,
    can_view_all_expenses = TRUE,
    can_generate_reports = TRUE
WHERE name = 'Accounts';

UPDATE roles SET 
    module_permissions = '{
        "expenses": ["read", "write", "modify"],
        "reports": ["read"]
    }',
    can_approve_expenses = FALSE,
    can_view_all_expenses = FALSE,
    can_generate_reports = FALSE
WHERE name IN ('Sales', 'Technical');

-- Create default admin permissions for existing admin users
INSERT INTO user_permissions (user_id, module, permission, granted_by)
SELECT u.id, 'all', 'admin', 1
FROM users u 
WHERE u.is_admin = TRUE
ON CONFLICT (user_id, module, permission) DO NOTHING;

COMMENT ON TABLE user_permissions IS 'Individual user permission overrides';
COMMENT ON TABLE group_permissions IS 'Group-based permissions for modules';
COMMENT ON TABLE expense_modifications IS 'Audit trail for expense changes';
COMMENT ON TABLE generated_reports IS 'Track generated reports and sharing';
COMMENT ON TABLE receipt_attachments IS 'Receipt images linked to expenses';
