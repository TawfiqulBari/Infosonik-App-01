-- Migration to add client/company information to expenses
-- Date: 2025-08-04
-- Description: Add client tracking fields to convenience_bills and create clients table

-- Create clients/companies table for better data management
CREATE TABLE IF NOT EXISTS clients (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(255),
    contact_number VARCHAR(50),
    email VARCHAR(255),
    address TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Add client information fields to convenience_bills
ALTER TABLE convenience_bills
    ADD COLUMN IF NOT EXISTS client_id INTEGER REFERENCES clients(id),
    ADD COLUMN IF NOT EXISTS client_company_name VARCHAR(255),
    ADD COLUMN IF NOT EXISTS client_contact_number VARCHAR(50),
    ADD COLUMN IF NOT EXISTS expense_purpose TEXT,
    ADD COLUMN IF NOT EXISTS project_reference VARCHAR(255),
    ADD COLUMN IF NOT EXISTS is_billable BOOLEAN DEFAULT FALSE;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_clients_company_name ON clients(company_name);
CREATE INDEX IF NOT EXISTS idx_clients_is_active ON clients(is_active);
CREATE INDEX IF NOT EXISTS idx_convenience_bills_client_id ON convenience_bills(client_id);
CREATE INDEX IF NOT EXISTS idx_convenience_bills_is_billable ON convenience_bills(is_billable);
CREATE INDEX IF NOT EXISTS idx_convenience_bills_expense_purpose ON convenience_bills USING gin(to_tsvector('english', expense_purpose));

-- Insert some default clients for testing
INSERT INTO clients (company_name, contact_person, contact_number, email, created_by) VALUES 
('Internal Projects', 'Admin', 'N/A', 'admin@company.com', 1),
('Client A - Tech Solutions', 'John Smith', '+8801700000001', 'john@techsolutions.com', 1),
('Client B - Digital Marketing', 'Sarah Johnson', '+8801700000002', 'sarah@digitalmarketing.com', 1),
('Client C - E-commerce Platform', 'Mike Wilson', '+8801700000003', 'mike@ecommerce.com', 1)
ON CONFLICT DO NOTHING;

-- Update existing records to have default values
UPDATE convenience_bills 
SET 
    client_id = 1, -- Internal Projects
    client_company_name = 'Internal Projects',
    client_contact_number = 'N/A',
    expense_purpose = 'General business expense',
    is_billable = FALSE
WHERE 
    client_id IS NULL;

-- Add comments for documentation
COMMENT ON TABLE clients IS 'Client/Company information for expense tracking and billing';
COMMENT ON COLUMN convenience_bills.client_id IS 'Reference to clients table for structured data';
COMMENT ON COLUMN convenience_bills.client_company_name IS 'Direct company name entry (alternative to client_id)';
COMMENT ON COLUMN convenience_bills.client_contact_number IS 'Client contact number for this expense';
COMMENT ON COLUMN convenience_bills.expense_purpose IS 'Purpose/reason for this expense';
COMMENT ON COLUMN convenience_bills.project_reference IS 'Project or reference code';
COMMENT ON COLUMN convenience_bills.is_billable IS 'Whether this expense can be billed to client';
