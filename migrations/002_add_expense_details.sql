-- Migration to add enhanced expense fields to convenience_bills table
-- Date: 2025-08-04
-- Description: Add transportation details and additional cost breakdown fields

-- Add transportation detail fields
ALTER TABLE convenience_bills
    ADD COLUMN IF NOT EXISTS transport_to VARCHAR(255),
    ADD COLUMN IF NOT EXISTS transport_from VARCHAR(255),
    ADD COLUMN IF NOT EXISTS means_of_transportation VARCHAR(255);

-- Add additional cost breakdown fields (stored in BDT paisa)
ALTER TABLE convenience_bills
    ADD COLUMN IF NOT EXISTS fuel_cost INTEGER DEFAULT 0,
    ADD COLUMN IF NOT EXISTS rental_cost INTEGER DEFAULT 0;

-- Update existing records to have default values for new fields
UPDATE convenience_bills 
SET 
    transport_to = '',
    transport_from = '',
    means_of_transportation = '',
    fuel_cost = 0,
    rental_cost = 0
WHERE 
    transport_to IS NULL OR 
    transport_from IS NULL OR 
    means_of_transportation IS NULL OR
    fuel_cost IS NULL OR 
    rental_cost IS NULL;

-- Add indexes for better performance on the new fields
CREATE INDEX IF NOT EXISTS idx_convenience_bills_means_of_transportation 
    ON convenience_bills(means_of_transportation);

-- Add comment to document the enhanced schema
COMMENT ON TABLE convenience_bills IS 'Enhanced convenience bills table with detailed transportation and cost breakdown. All monetary amounts stored in BDT paisa (1 BDT = 100 paisa)';
COMMENT ON COLUMN convenience_bills.fuel_cost IS 'Fuel cost in BDT paisa';
COMMENT ON COLUMN convenience_bills.rental_cost IS 'Rental cost in BDT paisa';
COMMENT ON COLUMN convenience_bills.transport_to IS 'Destination location for transportation';
COMMENT ON COLUMN convenience_bills.transport_from IS 'Origin location for transportation';
COMMENT ON COLUMN convenience_bills.means_of_transportation IS 'Mode of transportation used';
