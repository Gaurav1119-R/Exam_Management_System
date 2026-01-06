# Template Quick Reference Guide

## Template File Structure

```
templates/
├── base.html                           # Master template (all pages extend this)
├── accounts/
│   ├── login.html                      # Login page
│   ├── register.html                   # Registration page
│   ├── profile.html                    # View user profile
│   └── profile_update.html             # Edit user profile
├── exams/
│   ├── admin/
│   │   ├── dashboard.html              # Admin dashboard
│   │   ├── subject_list.html           # List all subjects
│   │   ├── subject_form.html           # Create/Edit subject
│   │   ├── question_list.html          # List all questions
│   │   ├── question_form.html          # Create/Edit question
│   │   └── schedule_list.html          # Manage exam schedules
│   └── student/
│       ├── dashboard.html              # Student dashboard
│       ├── exam_take.html              # Take exam interface
│       ├── exam_result.html            # View exam results
│       └── exam_history.html           # View exam history
├── attendance/
│   ├── mark_attendance.html            # Mark attendance form
│   └── student_attendance_report.html  # View attendance records
└── reports/
    ├── student_project_reports.html    # View/Submit projects
    └── student_performance_report.html # Performance analytics
```

## Template Features by Page

### Authentication
| Page | Features |
|------|----------|
| login.html | Username/password form, error handling |
| register.html | Role selection, dynamic fields based on role, password validation |
| profile.html | Display user info, role badges, edit button |
| profile_update.html | Edit forms for user info and student details |

### Admin Exam Management
| Page | Features |
|------|----------|
| admin/dashboard.html | Statistics cards, quick action links |
| subject_list.html | Table with add/edit/delete buttons |
| subject_form.html | ModelForm with validation |
| question_list.html | Filterable table, question type badges |
| question_form.html | Dynamic MCQ/Descriptive fields |
| schedule_list.html | Status badges, assignment options |

### Student Exam Management
| Page | Features |
|------|----------|
| student/dashboard.html | Upcoming/past exams, quick links |
| exam_take.html | Timer, MCQ/Descriptive questions, submit button |
| exam_result.html | Score display, progress bar, performance analysis |
| exam_history.html | Past exam list with scores |

### Attendance & Reports
| Page | Features |
|------|----------|
| mark_attendance.html | Exam selection, student list, checkboxes |
| student_attendance_report.html | Statistics, attendance table, percentage |
| student_project_reports.html | Project list, status badges, submission button |
| student_performance_report.html | Component breakdown, subject-wise table |

## CSS Classes & Styling

### Color System
```html
<!-- Success (Green) -->
<span class="badge bg-success">PASSED</span>

<!-- Danger (Red) -->
<span class="badge bg-danger">FAILED</span>

<!-- Info (Blue) -->
<span class="badge bg-info">Submitted</span>

<!-- Warning (Orange) -->
<span class="badge bg-warning">Pending</span>
```

### Common Components
```html
<!-- Card with border highlight -->
<div class="card" style="border-left: 4px solid #3498db;">

<!-- Statistics card -->
<h5 class="text-muted">Label</h5>
<h2 style="color: #3498db;">Value</h2>

<!-- Button group -->
<div class="btn-group w-100" role="group">
  <a class="btn btn-primary">Option 1</a>
  <a class="btn btn-secondary">Option 2</a>
</div>

<!-- Progress bar -->
<div class="progress">
  <div class="progress-bar" style="width: 75%">75%</div>
</div>
```

## Form Handling

### Basic Form Structure
```html
<form method="post" novalidate>
    {% csrf_token %}
    
    <div class="mb-3">
        <label for="{{ form.field.id_for_label }}" class="form-label">
            Label
        </label>
        {{ form.field }}
        {% if form.field.errors %}
            <div class="invalid-feedback d-block">
                {{ form.field.errors }}
            </div>
        {% endif %}
    </div>
    
    <button type="submit" class="btn btn-primary">Submit</button>
</form>
```

### Messages Display
```html
{% if messages %}
    {% for message in messages %}
        <div class="alert alert-{{ message.tags }} alert-dismissible fade show">
            {{ message }}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    {% endfor %}
{% endif %}
```

## JavaScript Features

### Timer Functionality (exam_take.html)
- Auto-submit when time expires
- Updates every 1 second
- Formatted MM:SS display

### Dynamic Forms (register.html, question_form.html)
- Show/hide fields based on selection
- Toggle required attribute
- Real-time validation feedback

### Confirmation Dialogs
```html
<a href="#" onclick="return confirm('Are you sure?')">Delete</a>
```

## Responsive Design

All templates use Bootstrap 5 grid:
- `col-md-*`: Medium screens and up
- `col-lg-*`: Large screens and up
- `w-100`: Full width
- `h-100`: Full height

Mobile-first approach ensures templates work on all devices.

## Template Inheritance

All pages follow this structure:
```html
{% extends 'base.html' %}

{% block title %}Page Title{% endblock %}

{% block content %}
    <!-- Page specific content -->
{% endblock %}

{% block extra_js %}
    <!-- Optional: Page specific JavaScript -->
{% endblock %}
```

## Common URL Patterns

```python
# Admin URLs
{% url 'admin:dashboard' %}
{% url 'subject_list' %}
{% url 'subject_create' %}
{% url 'subject_update' pk %}
{% url 'question_list' %}
{% url 'question_create' %}

# Student URLs
{% url 'exams:student:dashboard' %}
{% url 'exams:student:exam_take' schedule_id %}
{% url 'exams:student:exam_result' schedule_id %}
{% url 'exams:student:exam_history' %}

# Attendance URLs
{% url 'attendance:mark' %}
{% url 'attendance:report' schedule_id %}
{% url 'attendance:student_report' %}

# Report URLs
{% url 'student_project_reports' %}
{% url 'student_performance_report' %}

# Account URLs
{% url 'login' %}
{% url 'register' %}
{% url 'logout' %}
{% url 'profile' %}
{% url 'profile_update' %}
{% url 'dashboard' %}
```

## Icons Used

All templates include Font Awesome 6.4.0 icons:
- `<i class="fas fa-book"></i>` - Book/Subject
- `<i class="fas fa-question"></i>` - Question
- `<i class="fas fa-calendar"></i>` - Calendar/Date
- `<i class="fas fa-clock"></i>` - Clock/Time
- `<i class="fas fa-star"></i>` - Star/Marks
- `<i class="fas fa-user"></i>` - User/Profile
- `<i class="fas fa-check"></i>` - Check/Correct
- `<i class="fas fa-times"></i>` - Cancel/Delete
- `<i class="fas fa-edit"></i>` - Edit
- `<i class="fas fa-trash"></i>` - Delete
- `<i class="fas fa-history"></i>` - History
- `<i class="fas fa-chart-bar"></i>` - Charts
- `<i class="fas fa-file-alt"></i>` - Documents

## Customization Tips

1. **Change Colors**: Update `:root` variables in base.html
2. **Add Custom CSS**: Create `static/css/custom.css` and link in base.html
3. **Modify Layouts**: Edit `templates/base.html` for global changes
4. **Add Static Files**: Store in `static/css/`, `static/js/`, `static/images/`
5. **Update Icons**: Replace Font Awesome with other icon libraries

## Testing Checklist

- [ ] All forms submit correctly
- [ ] Error messages display properly
- [ ] Links navigate to correct pages
- [ ] Mobile view is responsive
- [ ] Timer works on exam page
- [ ] Dynamic form fields toggle correctly
- [ ] Tables sort and filter properly
- [ ] Badges display with correct colors
- [ ] Progress bars show accurate percentages
- [ ] Navigation bar works on all pages
