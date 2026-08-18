
A full-stack **Django-based Blood Donation Management System** designed to connect blood donors with patients and simplify the management of blood donation requests.

The system provides features such as **donor search, blood requests, request approvals, notifications, dashboards, and donation tracking** through a centralized web application.

## 📌 Features

* 👤 **User Registration & Login**

  * Secure user authentication
  * Separate user information and profiles

* 🩸 **Donor Management**

  * Store donor information
  * Manage blood groups and donor details
  * Search for suitable donors

* 🔎 **Donor Search**

  * Find donors based on blood group and availability
  * Quickly identify potential blood donors

* 📋 **Blood Requests**

  * Patients can submit blood requests
  * Track submitted requests
  * Manage request status

* ✅ **Request Approval**

  * Donors can respond to blood requests
  * Requests can be approved or rejected
  * Track the current status of requests

* 🔔 **Notifications**

  * Notify users about blood requests
  * Provide updates about request status and approvals

* 📊 **Dashboard**

  * View important blood donation information
  * Track donors, requests, and activities

* 🩸 **Donation Tracking**

  * Keep track of blood donation activities
  * Maintain donation-related records

## 🛠️ Technologies Used

| Technology           | Purpose                   |
| -------------------- | ------------------------- |
| **Python**           | Backend programming       |
| **Django**           | Web framework             |
| **SQLite**           | Database                  |
| **HTML5**            | Frontend structure        |
| **CSS3**             | Styling                   |
| **JavaScript**       | Client-side functionality |
| **Django Templates** | Dynamic web pages         |

## 📂 Project Structure

```text
Blood-Donation-Management-System/
│
├── blooddonation/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   ├── asgi.py
│   └── wsgi.py
│
├── system/
│   ├── migrations/
│   ├── static/
│   │   ├── css/
│   │   └── images/
│   ├── templates/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── manage.py
├── requirements.txt
└── README.md
```

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/susmita-del/Online-Blood-Donation-Management-System.git
```

### 2. Navigate to the project

```bash
cd Online-Blood-Donation-Management-System
```

### 3. Create a virtual environment

Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is not available, install Django:

```bash
pip install django
```

### 5. Apply database migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an administrator account.

### 7. Start the development server

```bash
python manage.py runserver
```

Open your browser and visit:

```text
http://127.0.0.1:8000/
```

## 🔐 Django Admin

The Django administration panel can be accessed at:

```text
http://127.0.0.1:8000/admin/
```

Use the superuser credentials created during setup.

## 🔄 Application Workflow

```text
User Registration
       ↓
User Login
       ↓
Create / Complete Profile
       ↓
Search for Blood Donors
       ↓
Submit Blood Request
       ↓
Donor Receives Request
       ↓
Request Approval / Rejection
       ↓
Notification & Status Update
       ↓
Donation Tracking
```

## 🎯 Project Objectives

The main objectives of this project are:

* To provide a centralized platform for blood donation management.
* To make it easier to find potential blood donors.
* To simplify the process of requesting blood.
* To improve communication between donors and recipients.
* To track blood donation activities and requests.
* To provide an organized dashboard for managing the system.

## 🚀 Future Improvements

Possible future enhancements include:

* 📱 Responsive mobile-first UI
* 📍 Location-based donor search
* 📧 Email notifications
* 📱 SMS notifications
* 🔔 Real-time notifications
* 🗺️ Google Maps integration
* 📊 Advanced analytics and reports
* 🔐 Role-based access control
* ☁️ Cloud deployment
* 🩸 Blood inventory management
* 📅 Donation appointment scheduling

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository.
2. Create a new branch:

```bash
git checkout -b feature/your-feature
```

3. Make your changes.
4. Commit your changes:

```bash
git commit -m "Add your feature"
```

5. Push the branch:

```bash
git push origin feature/your-feature
```

6. Open a Pull Request.

## 📄 License

This project is intended for educational and development purposes.

## 👩‍💻 Authors

**Susmita Del**

Online Blood Donation Management System — built with **Python & Django**.

---

⭐ If you find this project useful, consider giving the repository a **star**!
