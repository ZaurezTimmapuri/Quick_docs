-- database: :quickdocs:
-- Sample data for QuickDocs Document Collection System

-- Insert Processes
INSERT INTO processes (name, description, status) VALUES
('Home Loan Application', 'Complete home loan application process including document verification', 'active'),
('KYC Verification', 'Know Your Customer verification process for account opening', 'active');

-- Insert Document Types
INSERT INTO document_types (name, description, required_fields) VALUES
('PAN Card', 'Permanent Account Number card for tax identification', '{"pan_number": "string", "name": "string", "father_name": "string", "date_of_birth": "date"}'),
('Salary Slip', 'Monthly salary certificate from employer', '{"employee_name": "string", "employee_id": "string", "gross_salary": "number", "month_year": "string", "employer_name": "string"}'),
('Bank Statement', 'Bank account statement for income verification', '{"account_holder_name": "string", "account_number": "string", "bank_name": "string", "statement_period": "string", "average_balance": "number"}'),
('Aadhaar Card', 'Unique identification authority of India card', '{"aadhaar_number": "string", "name": "string", "date_of_birth": "date", "address": "string"}'),
('Property Documents', 'Property ownership and valuation documents', '{"property_address": "string", "property_value": "number", "owner_name": "string", "survey_number": "string"}');

-- Insert Customers
INSERT INTO customers (name, email, phone) VALUES
('Rajesh Kumar', 'rajesh.kumar@email.com', '9876543210'),
('Priya Sharma', 'priya.sharma@email.com', '9876543211'),
('Amit Patel', 'amit.patel@email.com', '9876543212'),
('Sunita Reddy', 'sunita.reddy@email.com', '9876543213'),
('Vikram Singh', 'vikram.singh@email.com', '9876543214');

-- Define process document requirements
INSERT INTO process_document_requirements (process_id, document_type_id, is_required) VALUES
-- Home Loan Application requirements
(1, 1, TRUE),  -- PAN Card
(1, 2, TRUE),  -- Salary Slip
(1, 3, TRUE),  -- Bank Statement
(1, 5, TRUE),  -- Property Documents
-- KYC Verification requirements
(2, 1, TRUE),  -- PAN Card
(2, 4, TRUE);  -- Aadhaar Card

-- Insert Process Assignments
INSERT INTO process_assignments (customer_id, process_id, status, completion_percentage) VALUES
(1, 1, 'pending', 75),    -- Rajesh Kumar - Home Loan (75% complete)
(1, 2, 'completed', 100), -- Rajesh Kumar - KYC (completed)
(2, 1, 'pending', 25),    -- Priya Sharma - Home Loan (50% complete)
(3, 2, 'pending', 50),    -- Amit Patel - KYC (50% complete)
(4, 1, 'pending', 0),    -- Sunita Reddy - Home Loan (25% complete)
(5, 2, 'completed', 100); -- Vikram Singh - KYC (completed)

-- Insert Document Submissions
INSERT INTO document_submissions (customer_id, process_id, document_type_id, file_url, ocr_extracted_data, validation_status) VALUES
-- Rajesh Kumar submissions (Home Loan)
(1, 1, 1, '/uploads/rajesh_pan.pdf', '{"pan_number": "ABCDE1234F", "name": "Rajesh Kumar", "father_name": "Ram Kumar", "date_of_birth": "1985-06-15"}', 'approved'),
(1, 1, 2, '/uploads/rajesh_salary.pdf', '{"employee_name": "Rajesh Kumar", "employee_id": "EMP001", "gross_salary": 75000, "month_year": "2024-01", "employer_name": "Tech Solutions Ltd"}', 'approved'),
(1, 1, 3, '/uploads/rajesh_bank.pdf', '{"account_holder_name": "Rajesh Kumar", "account_number": "1234567890", "bank_name": "State Bank of India", "statement_period": "2024-01", "average_balance": 50000}', 'approved'),

-- Rajesh Kumar submissions (KYC)
(1, 2, 1, '/uploads/rajesh_pan.pdf', '{"pan_number": "ABCDE1234F", "name": "Rajesh Kumar", "father_name": "Ram Kumar", "date_of_birth": "1985-06-15"}', 'approved'),
(1, 2, 4, '/uploads/rajesh_aadhaar.pdf', '{"aadhaar_number": "1234-5678-9012", "name": "Rajesh Kumar", "date_of_birth": "1985-06-15", "address": "123 Main St, Mumbai"}', 'approved'),

-- Priya Sharma submissions (Home Loan - partial)
(2, 1, 1, '/uploads/priya_pan.pdf', '{"pan_number": "FGHIJ5678K", "name": "Priya Sharma", "father_name": "Mohan Sharma", "date_of_birth": "1990-03-22"}', 'approved'),
(2, 1, 2, '/uploads/priya_salary.pdf', '{"employee_name": "Priya Sharma", "employee_id": "EMP002", "gross_salary": 65000, "month_year": "2024-01", "employer_name": "Finance Corp"}', 'pending'),

-- Amit Patel submissions (KYC - partial)
(3, 2, 1, '/uploads/amit_pan.pdf', '{"pan_number": "KLMNO9012P", "name": "Amit Patel", "father_name": "Suresh Patel", "date_of_birth": "1988-12-10"}', 'approved'),

-- Sunita Reddy submissions (Home Loan - minimal)
(4, 1, 1, '/uploads/sunita_pan.pdf', '{"pan_number": "QRSTU3456V", "name": "Sunita Reddy", "father_name": "Venkat Reddy", "date_of_birth": "1992-08-05"}', 'pending'),

-- Vikram Singh submissions (KYC - complete)
(5, 2, 1, '/uploads/vikram_pan.pdf', '{"pan_number": "WXYZ7890A", "name": "Vikram Singh", "father_name": "Gurdev Singh", "date_of_birth": "1987-11-18"}', 'approved'),
(5, 2, 4, '/uploads/vikram_aadhaar.pdf', '{"aadhaar_number": "9876-5432-1098", "name": "Vikram Singh", "date_of_birth": "1987-11-18", "address": "456 Oak Road, Delhi"}', 'approved');