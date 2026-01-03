# 🎓 Student Management System

A secure, role-based Student Management System built with Streamlit that helps educational institutions manage users, student records, and academic processes efficiently.

![Dashboard Preview](https://img.shields.io/badge/Status-Active-success) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

### 🔐 Authentication & User Management
- **Role-Based Access Control**: Two distinct user roles - Admin and Teacher
- **Secure Login/Logout**: Protected routes and session management
- **User Management**: Admins can create and manage both Admin and Teacher accounts
- **Password Security**: Secure password hashing and validation

### 📚 Core Features
- **Student Management**: Add, view, edit, and delete student records
- **Attendance Tracking**: Record and monitor student attendance
- **Performance Analytics**: Track and analyze student performance
- **Role-Based Dashboard**: Customized interface based on user role
- **Responsive Design**: Works on desktop and tablet devices

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Edge, or Safari)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/student-management-system.git
   cd student-management-system
   ```

2. **Set up a virtual environment** (recommended):
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```
   The application will start and automatically open in your default web browser at `http://localhost:8501`

## 🔐 Authentication Guide

### Default Admin Account
On first run, the system automatically creates a default admin account:
- **Username**: `admin`
- **Password**: `admin123`

### User Roles

#### 👨‍💼 Admin
- Full access to all system features
- Can create and manage both Admin and Teacher accounts
- Access to user management dashboard
- Can view all student records and reports

#### 👩‍🏫 Teacher
- Limited access to attendance and reports
- Can view and update student records
- No access to user management

### Creating New Users
1. Log in as an Admin
2. Navigate to "User Management" in the sidebar
3. Fill in the new user details
4. Select the appropriate role (Admin or Teacher)
5. Click "Add User"

### Security Notes
- Always change the default admin password after first login
- Use strong, unique passwords for all accounts
- Log out after each session, especially on shared computers
- The system automatically hashes all passwords using SHA-256

## 📝 Usage Instructions

### For Admins
1. **User Management**:
   - Navigate to "User Management" in the sidebar
   - View all existing users
   - Add new users with appropriate roles
   - Monitor user activity

2. **Student Management**:
   - Access the "Manage Students" section
   - Add, edit, or remove student records
   - Generate and export reports

### For Teachers
1. **Dashboard**:
   - View quick stats and recent activities
   - Access frequently used features

2. **Attendance**:
   - Mark student attendance
   - View attendance reports
   - Export attendance data

## 📁 Project Structure
```
student-management-system/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── users.db            # SQLite database (created automatically)
└── README.md           # This file
```

## 🔧 Troubleshooting

### Common Issues
- **Database not updating**: Try restarting the application
- **Login issues**: Verify username/password and ensure Caps Lock is off
- **Page not loading**: Clear browser cache or try a different browser

### Resetting the Admin Password
If you lose admin access, you can reset the admin password by:
1. Delete the `users.db` file
2. Restart the application to recreate it with default credentials

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

5. **Access the application**:
   Open your web browser and go to `http://localhost:8501`

## 📋 Usage

### Dashboard
- View key metrics and statistics
- Monitor overall attendance and performance
- Get quick insights with visualizations

### Student Management
- Add new students with detailed information
- Edit existing student records
- Delete students when needed
- Search and filter students

### Attendance
- Record daily attendance
- View attendance trends
- Generate attendance reports

### Reports
- Generate class-wise reports
- Export data to Excel
- View performance analytics

## 📂 Project Structure

```
student-management-system/
├── .gitignore
├── README.md
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
└── instance/           # Instance folder for database and configs
    └── school.db       # SQLite database (created on first run)
```

## 📊 Screenshots

### Dashboard
![Dashboard](screenshots/dashboard.png)

### Student Management
![Student Management](screenshots/students.png)

### Attendance
![Attendance](screenshots/attendance.png)

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Icons by [Bootstrap Icons](https://icons.getbootstrap.com/)
- Data visualization with [Plotly](https://plotly.com/)

---

<div align="center">
  Made with ❤️ by Your Name
</div>
