# Quick Start Guide - Exam Management System

## 📦 Installation

### Step 1: Clone & Setup Environment
```bash
cd "c:\Users\Vipul\Desktop\New folder"
python -m venv venv
venv\Scripts\activate  # Windows
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Initialize Database
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 4: Create Admin User
```bash
python manage.py createsuperuser
# Enter: username, email, password
```

### Step 5: Run Server
```bash
python manage.py runserver
```

**Access:**
- Main app: `http://localhost:8000`
- Admin panel: `http://localhost:8000/admin`
- Register page: `http://localhost:8000/accounts/register/`

---

## 🎯 Admin Quick Actions

1. **Go to Admin Panel**: `/admin/`
   - Login with superuser credentials

2. **Create Subject**:
   - Subjects → Add
   - Code: `CSC101`
   - Name: `Python Programming`
   - Credits: `3`

3. **Create Questions**:
   - Questions → Add
   - Subject: Select
   - Type: MCQ or Descriptive
   - For MCQ: Fill options A-D, mark correct answer
   - Marks: `5`

4. **Create Question Paper**:
   - Question Papers → Add
   - Title: `Midterm Exam`
   - Subject: Select
   - Questions: Check desired questions
   - Duration: `60` minutes
   - Passing Marks: `40`

5. **Schedule Exam**:
   - Exam Schedules → Add
   - Question Paper: Select
   - Date: Pick date
   - Start Time: `10:00`
   - End Time: `11:00`
   - Assigned Students: Select
   - Status: `Published`

---

## 👨‍🎓 Student Quick Actions

1. **Register**:
   - `/accounts/register/`
   - Role: Student
   - Fill: Email, Username, Name, Enrollment#, Department, Semester
   - Create Account

2. **Login**:
   - `/accounts/login/`
   - Use credentials

3. **Take Exam**:
   - Dashboard shows upcoming exams
   - Click exam name during scheduled time
   - Answer all questions
   - Submit

4. **View Results**:
   - After submission, see score and status
   - Can review answers

5. **Download Reports**:
   - Attendance Report: Shows exams attended
   - Performance Report: Overall statistics

---

## 🔧 Database Tables at a Glance

| App | Model | Purpose |
|-----|-------|---------|
| accounts | User | Authentication (admin/student role) |
| accounts | StudentProfile | Student details (enrollment, dept, semester) |
| exams | Subject | Course/Subject definition |
| exams | Question | Individual questions (MCQ/Descriptive) |
| exams | QuestionPaper | Collection of questions for an exam |
| exams | ExamSchedule | Exam scheduling + student assignment |
| exams | StudentExamResponse | Individual question answers by student |
| exams | StudentExamResult | Final score/result per exam |
| attendance | Attendance | Present/Absent tracking per exam |
| attendance | AttendanceReport | Aggregated attendance stats |
| reports | ProjectReport | Project submission tracking |
| reports | StudentReport | Overall performance metrics |

---

## 🎓 Example Workflow

### Day 1: Admin Sets Up Exam
```
1. Create Subject "Database Management"
2. Add 20 Questions (15 MCQ, 5 Descriptive)
3. Create Question Paper "Midterm" with 15 questions
4. Schedule for tomorrow 10:00-11:30 AM
5. Assign 50 students
```

### Day 2: Students Take Exam
```
1. Students login, see "Midterm" in dashboard
2. At 10:00 AM, click "Take Exam"
3. Answer 15 questions (20 min for MCQ, 40 min for descriptive)
4. Click Submit → see results immediately
5. View detailed answers
```

### Day 3: Admin Reviews
```
1. Check attendance report (who was present)
2. Grade descriptive questions if needed
3. View student reports (scores, performance)
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "No such table" error | Run `python manage.py migrate` |
| Student can't access exam | Check: (1) Is it scheduled time? (2) Is student assigned? (3) Is exam Published? |
| Can't create question paper | Make sure subject and questions exist first |
| Import errors | Verify all 4 apps in INSTALLED_APPS in settings.py |
| Template not found | Check templates/ folder structure matches app names |

---

## 📖 Key URLs Reference

### Authentication
- `GET/POST /accounts/register/` - Register page
- `GET/POST /accounts/login/` - Login page
- `GET /accounts/logout/` - Logout
- `GET /accounts/profile/` - View profile
- `GET/POST /accounts/profile/update/` - Edit profile

### Admin Dashboard
- `GET /exams/admin/dashboard/` - Admin home
- `GET /exams/admin/subjects/` - View subjects
- `GET/POST /exams/admin/subjects/create/` - Create subject
- `GET /exams/admin/questions/` - View questions (with filters)
- `GET/POST /exams/admin/questions/create/` - Create question
- `GET /exams/admin/papers/` - View papers
- `GET/POST /exams/admin/papers/create/` - Create paper
- `GET /exams/admin/schedules/` - View schedules
- `GET/POST /exams/admin/schedules/create/` - Schedule exam

### Student Dashboard
- `GET /exams/student/dashboard/` - Student home (shows exams)
- `GET/POST /exams/student/<id>/take/` - Take exam
- `GET /exams/student/<id>/result/` - View exam result
- `GET /exams/student/history/` - Exam history

### Attendance & Reports
- `GET/POST /attendance/mark/<id>/` - Mark attendance for exam
- `GET /attendance/report/<id>/` - View attendance report (admin)
- `GET /attendance/student-report/` - View attendance (student)
- `GET /reports/student/projects/` - View project assignments
- `GET /reports/student/performance/` - Overall performance report

---

## 🔐 Security Reminders

✅ Change `SECRET_KEY` in settings.py before production
✅ Set `DEBUG = False` in production
✅ Use strong superuser password
✅ Never commit `.env` files with secrets
✅ Use HTTPS in production

---

## 💡 Development Tips

**Add a new feature?**
1. Create model in `apps/<app>/models.py`
2. Add form in `apps/<app>/forms.py`
3. Add view in `apps/<app>/views.py`
4. Add URL in `apps/<app>/urls.py`
5. Run migrations: `python manage.py makemigrations && python manage.py migrate`
6. Register in admin.py if needed

**Debug queries?**
```python
from django.db import connection
from django.test.utils import CaptureQueriesContext

with CaptureQueriesContext(connection) as ctx:
    # Your code
print(f"Executed {len(ctx)} queries")
```

**Run tests?**
```bash
python manage.py test apps.exams  # Test specific app
```

---

## 📞 Support

Refer to `.github/copilot-instructions.md` for architecture details and best practices.
Refer to `README.md` for comprehensive documentation.
