# 🎓 Student Management System (SMS)

A comprehensive, user-friendly **Student Management System** designed to streamline school and college administration. Built using **Python, Streamlit, and SQLite**, this application centralizes student records, attendance, academics, and reporting into a single platform.

---

## 🌟 Key Features

### 1️⃣ Student Management
- Student profiles with personal, academic, and guardian details
- Bulk import and export of student data using Excel/CSV
- Activate or deactivate student records
- Secure document upload and storage

---

### 2️⃣ Attendance Management
- Class-wise daily attendance marking
- Attendance status: Present / Absent / Late
- Attendance percentage calculation
- Export attendance reports to Excel/PDF

---

### 3️⃣ Academic Management
- Class and section creation
- Subject management
- Teacher–subject mapping
- Subject-wise performance tracking

---

### 4️⃣ User & Role Management
- Role-based access control:
  - Admin – Full access
  - Teacher – Assigned class access
  - Staff – View-only access
- User profile management

---

### 5️⃣ Dashboard & Analytics
- Student, teacher, and class overview
- Attendance analytics
- Academic performance insights

---

## 🛠️ Technical Stack

Frontend: Streamlit  
Backend: Python 3.8+  
Database: SQLite (SQLAlchemy ORM)  
Authentication: Role-based access  
Deployment: Docker-ready  

---
## 🎯 Why This Project Is Helpful

This Student Management System helps educational institutions digitize and centralize their administrative processes.

Reduces manual paperwork and errors

Saves time for administrators and teachers

Provides real-time access to student and attendance data

Improves data accuracy and consistency

Enables quick report generation and analytics

Scales easily as the number of students grows

The system is designed to be modular, secure, and easy to extend, making it suitable for schools, colleges, and training institutes.

---

## ⚙️ Setup Instructions

1. Clone the repository  
git clone https://github.com/Kashish-21/student-management-system.git  
cd student-management-system  

2. Create a virtual environment  
python -m venv .venv  

3. Activate the virtual environment  

Windows:  
.\.venv\Scripts\activate  

macOS / Linux:  
source .venv/bin/activate  

4. Install dependencies  
pip install -r requirements.txt  

5. Initialize the database  
python init_db.py  

6. Run the application  
streamlit run app.py  

7. Open the application in browser  
http://localhost:8501  

---

## 🚀 Usage

Admin  
- Manage students and academic structure  
- View dashboards and reports  
- Control user access  

Teacher  
- Mark attendance  
- View assigned class data  

Staff  
- View student information  
- Generate basic reports  

---

## 🔧 Configuration (Optional)

Create a `.env` file in the project root:

SECRET_KEY=your-secret-key  
DATABASE_URL=sqlite:///sms.db  
UPLOAD_FOLDER=uploads  

---

## 🧪 Testing

pytest tests/

---

## 🤝 Contributing

1. Fork the repository  
2. Create a feature branch  
3. Commit your changes  
4. Push to your branch  
5. Open a Pull Request  

---

## 📧 Contact

For queries or support, contact:  
your-kashishcoe021@gmail.com
