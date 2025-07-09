#!/usr/bin/env python3
"""
Debug script to check and fix common setup issues
"""

import os
import sys
import subprocess

def check_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("   ✅ Python version is compatible")
        return True
    else:
        print("   ❌ Python 3.8+ required")
        return False

def check_virtual_environment():
    """Check if virtual environment exists"""
    print("\n🔧 Checking virtual environment...")
    venv_path = os.path.join(os.path.dirname(__file__), 'venv')
    
    if os.path.exists(venv_path):
        print("   ✅ Virtual environment exists")
        return True
    else:
        print("   ❌ Virtual environment not found")
        print("   Creating virtual environment...")
        try:
            subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
            print("   ✅ Virtual environment created")
            return True
        except subprocess.CalledProcessError:
            print("   ❌ Failed to create virtual environment")
            return False

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    # Determine the correct pip path
    if os.name == 'nt':  # Windows
        pip_path = os.path.join('venv', 'Scripts', 'pip')
    else:  # Unix/Linux/macOS
        pip_path = os.path.join('venv', 'bin', 'pip')
    
    try:
        subprocess.run([pip_path, 'install', '-r', 'requirements.txt'], check=True)
        print("   ✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("   ❌ Failed to install dependencies")
        print("   Try running manually: ./venv/bin/pip install -r requirements.txt")
        return False
    except FileNotFoundError:
        print("   ❌ Virtual environment activation failed")
        return False

def check_database():
    """Check if database file exists"""
    print("\n🗄️  Checking database...")
    db_path = 'greek_conjugator_dev.db'
    
    if os.path.exists(db_path):
        print("   ✅ Database file exists")
        return True
    else:
        print("   ⚠️  Database file not found - will be created on first run")
        return True

def test_flask_import():
    """Test if Flask can be imported"""
    print("\n🌶️  Testing Flask import...")
    try:
        import flask
        print(f"   ✅ Flask {flask.__version__} imported successfully")
        return True
    except ImportError:
        print("   ❌ Flask not found - check virtual environment activation")
        return False

def main():
    print("🔧 Greek Conjugator Backend Debug Script")
    print("=" * 50)
    
    checks = [
        check_python_version(),
        check_virtual_environment(),
        install_dependencies(),
        test_flask_import(),
        check_database(),
    ]
    
    print("\n" + "=" * 50)
    if all(checks):
        print("✅ All checks passed! Backend should be ready to run.")
        print("\nTo start the backend:")
        print("1. cd greek-conjugator/backend")
        print("2. source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
        print("3. python run_backend.py")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\nManual setup steps:")
        print("1. cd greek-conjugator/backend")
        print("2. python -m venv venv")
        print("3. source venv/bin/activate")
        print("4. pip install -r requirements.txt")
        print("5. python run_backend.py")

if __name__ == "__main__":
    main()