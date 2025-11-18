🌟 Secure Task Manager

A simple and secure task management web application built using Django and Django REST Framework.
Users can register, log in, update their profile, upload profile pictures with cropping, and manage tasks with filters, search, sorting, and favorites.

📛 Badges

📘 Secure Task Manager (Django + REST API)

A fully functional task management system where users can:

✔ Create tasks
✔ Edit tasks
✔ Delete tasks
✔ Mark tasks as favorite
✔ Filter, search, and sort tasks
✔ Manage their profile
✔ Upload and crop profile pictures
✔ Reset password via OTP email

Everything is built with clear code, clean UI, and a beginner-friendly approach.

📌 Features
🔐 1. User Authentication

Signup with email

Login using email + password

Logout

Forgot password

OTP verification

Reset password

👤 2. User Profile

View profile

Edit profile details

Upload profile photo

Modern drag & zoom image cropper (similar to Email/Gmail style)

Circular avatar preview

Fully responsive on mobile

📝 3. Task Management

Add new tasks

Edit existing tasks

Delete tasks

Read-only View Task mode

Mark/unmark favorite

Auto timestamps

Rich cards-based UI

🔍 4. Search, Filter & Sort

Search tasks by title

Filters:

All

Pending

Completed

Favorites

Sorting:

Newest

Oldest

A → Z

Z → A

📡 5. REST API (Django REST Framework)

Tasks API Endpoints:

GET    /api/tasks/
POST   /api/tasks/
GET    /api/tasks/<id>/
PUT    /api/tasks/<id>/
DELETE /api/tasks/<id>/
POST   /api/tasks/<id>/toggle-favorite/


Each user can access only their own tasks.

🧰 6. Responsive UI

Bootstrap 5

Mobile navigation bar

Smooth modals

Clean task grid layout

Optimized for all screen sizes

🛠️ Technologies Used
Backend

Python

Django

Django REST Framework

MySQL

Frontend

HTML

CSS

Bootstrap

JavaScript

Others

Pillow (image processing)

Canvas-based image cropper

📁 Project Structure
project/
│
├── accounts/         # Authentication, profile, OTP
├── tasks/            # Tasks app + REST API
├── static/           # JS, CSS, images
├── templates/        # HTML templates
├── media/            # User uploaded profile photos
└── task_manager/     # Main project settings, URLs

🚀 How to Run Locally
1. Install dependencies
pip install -r requirements.txt

2. Run migrations
python manage.py migrate

3. Start development server
python manage.py runserver

Visit:
http://127.0.0.1:8000/

🧪 API Testing (Postman)
Login (Session Auth)
POST /accounts/login/

Create Task
POST /api/tasks/

List Tasks
GET /api/tasks/

Edit Task
PUT /api/tasks/<id>/

Delete Task
DELETE /api/tasks/<id>/

📸 Screenshots (You can add later)

Dashboard

Tasks Page

Profile Page

Image Cropper

Login / Signup

OTP Screen

🎯 What I Learned

Custom user model

Handling authentication in Django

Building REST APIs

Working with JavaScript fetch requests

Image processing with canvas

Pagination and filtering

Building responsive layouts

🧭 Future Improvements

Dark mode

Task reminders

Subtasks

Export tasks as CSV/PDF

Activity logs


📄 License

This project is open-source under the MIT License.

