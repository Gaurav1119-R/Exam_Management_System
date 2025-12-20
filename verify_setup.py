#!/usr/bin/env python
"""
Setup Verification Script for Django Exam Management System

This script verifies that all project files and dependencies are correctly installed.
Run this after setup to ensure everything is ready.

Usage:
    python verify_setup.py
"""

import os
import sys
import django

def check_python_version():
    """Check Python version."""
    print("✓ Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"  ✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"  ❌ Python {version.major}.{version.minor} (Need 3.8+)")
        return False

def check_django_installation():
    """Check Django installation."""
    print("\n✓ Checking Django installation...")
    try:
        import django
        print(f"  ✅ Django {django.get_version()} installed")
        return True
    except ImportError:
        print("  ❌ Django not installed")
        print("  Run: pip install -r requirements.txt")
        return False

def check_required_packages():
    """Check required packages."""
    print("\n✓ Checking required packages...")
    required = [
        'django',
        'rest_framework',
        'django_filters',
        'PIL',  # Pillow
    ]
    
    all_ok = True
    for package in required:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} not found")
            all_ok = False
    
    if not all_ok:
        print("\n  Run: pip install -r requirements.txt")
    
    return all_ok

def check_project_structure():
    """Check project directory structure."""
    print("\n✓ Checking project structure...")
    
    required_dirs = [
        'apps',
        'apps/accounts',
        'apps/exams',
        'apps/attendance',
        'apps/reports',
        'exam_system',
        'templates',
        'static',
        '.github',
    ]
    
    all_ok = True
    for directory in required_dirs:
        if os.path.isdir(directory):
            print(f"  ✅ {directory}/")
        else:
            print(f"  ❌ {directory}/ (NOT FOUND)")
            all_ok = False
    
    return all_ok

def check_required_files():
    """Check required files."""
    print("\n✓ Checking required files...")
    
    required_files = [
        'manage.py',
        'requirements.txt',
        'exam_system/settings.py',
        'exam_system/urls.py',
        'apps/accounts/models.py',
        'apps/exams/models.py',
        'apps/attendance/models.py',
        'apps/reports/models.py',
        '.github/copilot-instructions.md',
        'README.md',
        'QUICKSTART.md',
        'ARCHITECTURE.md',
        'MODEL_REFERENCE.md',
        'DEVELOPMENT.md',
        'PROJECT_SUMMARY.md',
        'INDEX.md',
    ]
    
    all_ok = True
    for file in required_files:
        if os.path.isfile(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} (NOT FOUND)")
            all_ok = False
    
    return all_ok

def check_database():
    """Check database configuration."""
    print("\n✓ Checking database...")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_system.settings')
        django.setup()
        
        from django.db import connection
        connection.ensure_connection()
        print("  ✅ Database connection OK")
        
        # Check migrations
        from django.core.management import call_command
        from io import StringIO
        
        out = StringIO()
        try:
            call_command('showmigrations', stdout=out)
            output = out.getvalue()
            if '[X]' in output:
                print("  ✅ Migrations applied")
                return True
            else:
                print("  ⚠️  Migrations not applied yet")
                print("     Run: python manage.py migrate")
                return False
        except Exception as e:
            print(f"  ⚠️  Could not check migrations: {e}")
            return False
            
    except Exception as e:
        print(f"  ❌ Database error: {e}")
        return False

def check_apps_installed():
    """Check if all apps are installed."""
    print("\n✓ Checking installed apps...")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_system.settings')
        django.setup()
        
        from django.apps import apps
        
        required_apps = [
            'accounts',
            'exams',
            'attendance',
            'reports',
        ]
        
        installed = [app.name for app in apps.get_app_configs()]
        
        all_ok = True
        for app in required_apps:
            if any(app in name for name in installed):
                print(f"  ✅ {app}")
            else:
                print(f"  ❌ {app} (NOT INSTALLED)")
                all_ok = False
        
        return all_ok
    except Exception as e:
        print(f"  ❌ Error checking apps: {e}")
        return False

def print_summary(results):
    """Print summary of all checks."""
    print("\n" + "="*50)
    print("VERIFICATION SUMMARY")
    print("="*50)
    
    checks = [
        ("Python Version", results[0]),
        ("Django Installation", results[1]),
        ("Required Packages", results[2]),
        ("Project Structure", results[3]),
        ("Required Files", results[4]),
        ("Apps Installed", results[5]),
        ("Database", results[6]),
    ]
    
    for check_name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name:.<30} {status}")
    
    if all(results):
        print("\n🎉 All checks passed! Project is ready to use.")
        print("\nNext steps:")
        print("  1. Create superuser: python manage.py createsuperuser")
        print("  2. Run server: python manage.py runserver")
        print("  3. Visit: http://localhost:8000")
        print("  4. Admin: http://localhost:8000/admin")
        print("  5. Register: http://localhost:8000/accounts/register/")
        return True
    else:
        print("\n⚠️  Some checks failed. Please review the output above.")
        print("\nCommon fixes:")
        print("  - Missing packages: pip install -r requirements.txt")
        print("  - Missing migrations: python manage.py makemigrations && python manage.py migrate")
        print("  - Check settings.py for correct app registration")
        return False

def main():
    """Run all verification checks."""
    print("Django Exam Management System - Setup Verification")
    print("="*50)
    
    results = [
        check_python_version(),
        check_django_installation(),
        check_required_packages(),
        check_project_structure(),
        check_required_files(),
        check_apps_installed(),
        check_database(),
    ]
    
    success = print_summary(results)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
