from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import json
import re
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Database configuration
DATABASE = 'quickdocs.db'

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize database with schema and sample data"""
    conn = get_db_connection()
    
    # Read and execute schema
    with open('database/schema.sql', 'r') as f:
        conn.executescript(f.read())
    
    # Read and execute sample data
    with open('database/sample_data.sql', 'r') as f:
        conn.executescript(f.read())
    
    conn.commit()
    conn.close()

def calculate_completion_percentage(customer_id, process_id):
    """Calculate completion percentage for a process assignment"""
    conn = get_db_connection()
    
    # Get required documents for the process
    required_docs = conn.execute('''
        SELECT COUNT(*) as total
        FROM process_document_requirements pdr
        WHERE pdr.process_id = ? AND pdr.is_required = 1
    ''', (process_id,)).fetchone()
    
    # Get submitted and approved documents
    submitted_docs = conn.execute('''
        SELECT COUNT(*) as submitted
        FROM document_submissions ds
        WHERE ds.customer_id = ? AND ds.process_id = ? AND ds.validation_status = 'approved'
    ''', (customer_id, process_id)).fetchone()
    
    conn.close()
    
    if required_docs['total'] == 0:
        return 0
    
    percentage = (submitted_docs['submitted'] / required_docs['total']) * 100
    return min(100, int(percentage))

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/customers')
def customers():
    """Customer Registration Page"""
    conn = get_db_connection()
    customers = conn.execute('SELECT * FROM customers ORDER BY registration_date DESC').fetchall()
    processes = conn.execute('SELECT * FROM processes WHERE status = "active"').fetchall()
    conn.close()
    return render_template('customers.html', customers=customers, processes=processes)

@app.route('/add_customer', methods=['POST'])
def add_customer():
    """Add new customer"""
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    process_id = request.form.get('process_id')
    
    conn = get_db_connection()
    try:
        # Insert customer
        cursor = conn.execute(
            'INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)',
            (name, email, phone)
        )
        customer_id = cursor.lastrowid
        
        # Assign to process if selected
        if process_id:
            conn.execute(
                'INSERT INTO process_assignments (customer_id, process_id) VALUES (?, ?)',
                (customer_id, process_id)
            )
        
        conn.commit()
        flash('Customer added successfully!', 'success')
    except sqlite3.IntegrityError:
        flash('Email already exists!', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('customers'))

@app.route('/documents')
def documents():
    """Document Submission Page"""
    conn = get_db_connection()
    
    # Get customers with their process assignments
    customers_data = conn.execute('''
        SELECT c.id, c.name, p.id as process_id, p.name as process_name
        FROM customers c
        JOIN process_assignments pa ON c.id = pa.customer_id
        JOIN processes p ON pa.process_id = p.id
        WHERE pa.status = 'pending'
        ORDER BY c.name
    ''').fetchall()
    
    # Get document types
    document_types = conn.execute('SELECT * FROM document_types ORDER BY name').fetchall()
    
    # Get recent submissions
    recent_submissions = conn.execute('''
        SELECT ds.*, c.name as customer_name, p.name as process_name, dt.name as document_type_name
        FROM document_submissions ds
        JOIN customers c ON ds.customer_id = c.id
        JOIN processes p ON ds.process_id = p.id
        JOIN document_types dt ON ds.document_type_id = dt.id
        ORDER BY ds.upload_date DESC
        LIMIT 10
    ''').fetchall()
    
    conn.close()
    return render_template('documents.html', 
                         customers_data=customers_data, 
                         document_types=document_types,
                         recent_submissions=recent_submissions)

@app.route('/get_required_documents')
def get_required_documents():
    """Get required documents for a process"""
    process_id = request.args.get('process_id')
    
    conn = get_db_connection()
    required_docs = conn.execute('''
        SELECT dt.id, dt.name, dt.description, dt.required_fields
        FROM document_types dt
        JOIN process_document_requirements pdr ON dt.id = pdr.document_type_id
        WHERE pdr.process_id = ? AND pdr.is_required = 1
    ''', (process_id,)).fetchall()
    conn.close()
    
    return jsonify([dict(doc) for doc in required_docs])

@app.route('/submit_document', methods=['POST'])
def submit_document():
    """Submit document"""
    customer_id = request.form['customer_id']
    process_id = request.form['process_id']
    document_type_id = request.form['document_type_id']
    file_url = request.form['file_url']
    extracted_data = request.form['extracted_data']
    
    conn = get_db_connection()
    try:
        # Parse extracted data as JSON
        ocr_data = json.loads(extracted_data) if extracted_data else {}
        
        # Insert or update document submission
        conn.execute('''
            INSERT OR REPLACE INTO document_submissions 
            (customer_id, process_id, document_type_id, file_url, ocr_extracted_data, validation_status)
            VALUES (?, ?, ?, ?, ?, 'pending')
        ''', (customer_id, process_id, document_type_id, file_url, json.dumps(ocr_data)))
        
        # Update completion percentage
        completion = calculate_completion_percentage(customer_id, process_id)
        status = 'completed' if completion == 100 else 'pending'
        
        conn.execute('''
            UPDATE process_assignments 
            SET completion_percentage = ?, status = ?
            WHERE customer_id = ? AND process_id = ?
        ''', (completion, status, customer_id, process_id))
        
        conn.commit()
        flash('Document submitted successfully!', 'success')
    except json.JSONDecodeError:
        flash('Invalid JSON data in extracted fields!', 'error')
    except Exception as e:
        flash(f'Error submitting document: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('documents'))

@app.route('/dashboard')
def dashboard():
    """Status Dashboard"""
    conn = get_db_connection()
    
    # Get all process assignments with customer and process details
    assignments = conn.execute('''
        SELECT 
            pa.id,
            c.name as customer_name,
            p.name as process_name,
            pa.assignment_date,
            pa.status,
            pa.completion_percentage,
            COUNT(ds.id) as documents_submitted,
            COUNT(pdr.id) as documents_required
        FROM process_assignments pa
        JOIN customers c ON pa.customer_id = c.id
        JOIN processes p ON pa.process_id = p.id
        LEFT JOIN document_submissions ds ON pa.customer_id = ds.customer_id AND pa.process_id = ds.process_id
        LEFT JOIN process_document_requirements pdr ON pa.process_id = pdr.process_id AND pdr.is_required = 1
        GROUP BY pa.id, c.name, p.name, pa.assignment_date, pa.status, pa.completion_percentage
        ORDER BY pa.assignment_date DESC
    ''').fetchall()
    
    conn.close()
    return render_template('dashboard.html', assignments=assignments)

@app.route('/query')
def query_interface():
    """Natural Language Query Interface"""
    return render_template('query.html')

@app.route('/execute_query', methods=['POST'])
def execute_query():
    """Execute natural language query"""
    nl_query = request.form['query'].strip()
    
    try:
        sql_query = natural_language_to_sql(nl_query)
        if not sql_query:
            return jsonify({
                'error': 'Could not understand the query. Please try rephrasing.',
                'sql': '',
                'results': []
            })
        
        conn = get_db_connection()
        cursor = conn.execute(sql_query)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'sql': sql_query,
            'results': results,
            'error': None
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'sql': sql_query if 'sql_query' in locals() else '',
            'results': []
        })


# Natural Language to SQL Conversion

def natural_language_to_sql(query):
    """Convert natural language query to SQL"""
    query_lower = query.lower().strip()
    
    # Query patterns and their corresponding SQL
    patterns = [
        # Pattern 1: Show all customers
        (r'show all customers?|list all customers?|get all customers?', 
        'SELECT id, name, email, phone, registration_date FROM customers ORDER BY registration_date DESC'),
        
        # Pattern 2: List all pending processes
        (r'list all pending processes?|show pending processes?|get pending processes?',
         '''SELECT pa.id, c.name as customer_name, p.name as process_name, 
            pa.assignment_date, pa.completion_percentage 
            FROM process_assignments pa 
            JOIN customers c ON pa.customer_id = c.id 
            JOIN processes p ON pa.process_id = p.id 
            WHERE pa.status = 'pending' 
            ORDER BY pa.assignment_date'''),
        
        # Pattern 3: How many documents has [customer] submitted
        (r'how many documents has (.+?) submitted\??|documents submitted by (.+?)\??',
         lambda match: f'''SELECT c.name as customer_name, COUNT(ds.id) as documents_submitted
            FROM customers c 
            LEFT JOIN document_submissions ds ON c.id = ds.customer_id 
            WHERE LOWER(c.name) LIKE '%{match.group(1).lower()}%' 
            GROUP BY c.id, c.name'''),
        
        # Pattern 4: Which process has the most documents
        (r'which process has the most documents\??|process with most documents\??',
         '''SELECT p.name as process_name, COUNT(ds.id) as document_count
            FROM processes p 
            LEFT JOIN document_submissions ds ON p.id = ds.process_id 
            GROUP BY p.id, p.name 
            ORDER BY document_count DESC 
            LIMIT 1'''),
        
        # Pattern 5: Which customers are assigned to [process]
        (r'which customers are assigned to (.+?)\??|customers in (.+?)\??|customers for (.+?)\??',
         lambda match: f'''SELECT c.name as customer_name, pa.assignment_date, pa.status, pa.completion_percentage
            FROM customers c 
            JOIN process_assignments pa ON c.id = pa.customer_id 
            JOIN processes p ON pa.process_id = p.id 
            WHERE LOWER(p.name) LIKE '%{match.group(1).lower()}%' 
            ORDER BY pa.assignment_date'''),
        
        # Additional useful patterns
        (r'show completed processes?|list completed processes?',
         '''SELECT c.name as customer_name, p.name as process_name, pa.completion_percentage
            FROM process_assignments pa 
            JOIN customers c ON pa.customer_id = c.id 
            JOIN processes p ON pa.process_id = p.id 
            WHERE pa.status = 'completed' 
            ORDER BY pa.assignment_date'''),
        
        (r'show all processes?|list all processes?',
         'SELECT id, name, description, status, created_at FROM processes ORDER BY name'),
        
        (r'show all document types?|list document types?',
         'SELECT id, name, description FROM document_types ORDER BY name'),
        
        (r'show recent submissions?|recent documents?',
         '''SELECT c.name as customer_name, p.name as process_name, dt.name as document_type, 
            ds.upload_date, ds.validation_status
            FROM document_submissions ds 
            JOIN customers c ON ds.customer_id = c.id 
            JOIN processes p ON ds.process_id = p.id 
            JOIN document_types dt ON ds.document_type_id = dt.id 
            ORDER BY ds.upload_date DESC 
            LIMIT 10''')
    ]
    
    # Try to match patterns
    for pattern, sql_template in patterns:
        if callable(sql_template):
            # Pattern with capture groups
            match = re.search(pattern, query_lower)
            if match:
                return sql_template(match)
        else:
            # Simple pattern matching
            if re.search(pattern, query_lower):
                return sql_template
    
    return None

if __name__ == '__main__':
    # Initialize database if it doesn't exist
    if not os.path.exists(DATABASE):
        init_database()
    
    app.run(debug=True)