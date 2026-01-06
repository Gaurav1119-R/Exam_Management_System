"""
Script to populate Department and Subject data
Run with: python manage.py shell < setup_departments_subjects.py
Or: python setup_departments_subjects.py
"""

import os
import django

# Setup Django if running standalone
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_system.settings')
    django.setup()

from apps.exams.models import Department, Subject

# Department and Subject data
DEPARTMENTS_DATA = {
    'BCA': {
        'name': 'Bachelor of Computer Applications',
        'subjects': [
            {'code': 'BCA-AI-ML', 'name': 'AI & ML'},
            {'code': 'BCA-CC', 'name': 'Cloud Computing'},
            {'code': 'BCA-PYTHON', 'name': 'Python'},
            {'code': 'BCA-DWH', 'name': 'Data Warehouse'},
            {'code': 'BCA-NOSQL', 'name': 'NoSQL'},
            {'code': 'BCA-INT', 'name': 'Internship'},
        ]
    },
    'IT': {
        'name': 'Information Technology',
        'subjects': [
            {'code': 'IT-NET', 'name': '.NET'},
            {'code': 'IT-AI-ML', 'name': 'AI & ML'},
            {'code': 'IT-INT', 'name': 'Internship'},
            {'code': 'IT-DWH', 'name': 'Data Warehouse'},
            {'code': 'IT-VIRT', 'name': 'Virtualization'},
            {'code': 'IT-JAVA', 'name': 'Java'},
        ]
    }
}

def setup_departments_and_subjects():
    """
    Create departments and their associated subjects.
    """
    print("Starting Department and Subject Setup...")
    
    for dept_code, dept_info in DEPARTMENTS_DATA.items():
        # Create or update department
        department, created = Department.objects.get_or_create(
            code=dept_code,
            defaults={
                'name': dept_info['name'],
                'description': f'Department of {dept_info["name"]}'
            }
        )
        
        status = "Created" if created else "Already exists"
        print(f"\n{status}: Department '{dept_code}' - {department.name}")
        
        # Create subjects for this department
        for subject_data in dept_info['subjects']:
            subject, created = Subject.objects.get_or_create(
                code=subject_data['code'],
                defaults={
                    'name': subject_data['name'],
                    'department': department,
                    'description': f'{subject_data["name"]} for {department.name}',
                    'credits': 3  # Default credits
                }
            )
            
            # Update department if it was created without one
            if not created and subject.department != department:
                subject.department = department
                subject.save()
                print(f"  Updated: Subject '{subject.code}' - {subject.name}")
            else:
                status = "Created" if created else "Already exists"
                print(f"  {status}: Subject '{subject.code}' - {subject.name}")
    
    print("\n✓ Department and Subject setup completed successfully!")
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY:")
    print("="*60)
    for dept in Department.objects.all():
        subject_count = dept.subjects.count()
        print(f"\n{dept.code}: {subject_count} subjects")
        for subject in dept.subjects.all():
            print(f"  • {subject.code}: {subject.name}")

if __name__ == '__main__':
    setup_departments_and_subjects()
