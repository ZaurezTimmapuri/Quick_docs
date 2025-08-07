# 📂 Quick Docs - Document Management System

A **Flask-based Document Management System** with intelligent form handling, secure file uploads, real-time progress tracking, and **natural language query capabilities** powered by Gemini AI (optional).

---

## 🚀 Features

- 📄 **Document Submission** – Upload documents with intelligent form validation.
- 👥 **Customer Management** – Register and manage customers with process assignments.
- 📊 **Progress Tracking** – Real-time completion percentage calculations.
- 🔍 **Smart Search** – Natural language queries with Gemini AI integration.
- ✅ **Document Validation** – Automatic field checks based on document type.
- 📈 **Dashboard** – View process completion and document status in one place.
- 🎯 **Dynamic Forms** – Auto-populated JSON forms based on selected document types.

---

## 📦 Prerequisites

- Python **3.8+**
- SQLite3
- **Google Gemini API Key** *(optional for AI-powered queries)*

---

## 🛠 Installation

1️⃣ **Clone the Repository**
git clone https://github.com/zaureztimmapuri/quickdocs.git
cd quickdocs

2️⃣ Install Dependencies
pip install -r requirements.txt

3️⃣ Set Environment Variables
Create a .env file in the project root:
GOOGLE_API_KEY=your_gemini_api_key_here

4️⃣ Initialize Database
On first run, the database will be auto-created and populated with sample data.

			quickdocs/
			├── app.py                 # Main Flask application
			├── requirements.txt       # Python dependencies
			├── .env                  # Environment variables (create this)
			├── database/
			│   ├── schema.sql        # Database schema
			│   └── sample_data.sql   # Sample data
			└── templates/
			    ├── base.html         # Base template
			    ├── index.html        # Home page
			    ├── customers.html    # Customer management
			    ├── documents.html    # Document submission (updated)
			    ├── dashboard.html    # Progress dashboard
			    └── query.html        # Natural language queries
			
▶ Running the Application
	python app.py

Then open your browser and visit:
	http://localhost:5000

📖 Usage Guide
	
 1. Customer Registration
	Go to "Customers" page
	Fill in customer details and assign to a process
	Save the record

2. Document Submission
	Select Customer + Process
	Choose document type (fields load automatically)
	fill required fields
	Validate and submit

3. Document Review
	View recent submissions
	Filter by Pending / Approved / Rejected
	Approve/reject with confirmation
	View uploaded files directly

4. Progress Tracking
	Go to "Dashboard"
	Monitor completion % and document counts

5. Natural Language Queries
	Example queries:
	Show all customers
	List pending processes
	How many documents has John submitted?
	Which customers are assigned to loan application?

🗄 Database Schema
Main tables:

customers – Customer information

processes – Available workflows

document_types – Document definitions & required fields

process_assignments – Customer-process links

document_submissions – Uploaded documents & metadata

process_document_requirements – Required docs per process

🔑 Environment Variables

GOOGLE_API_KEY	(Optional) :Gemini API key for natural language queries
