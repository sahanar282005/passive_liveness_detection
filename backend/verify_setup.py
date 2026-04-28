"""
Setup verification script for PassiveLiveness API
Checks all dependencies and configurations
"""

import sys
import importlib
from pathlib import Path


class VerificationReport:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
    
    def success(self, msg: str):
        self.passed.append(msg)
        print(f"✅ {msg}")
    
    def error(self, msg: str):
        self.failed.append(msg)
        print(f"❌ {msg}")
    
    def warning(self, msg: str):
        self.warnings.append(msg)
        print(f"⚠️  {msg}")
    
    def print_summary(self):
        print("\n" + "="*60)
        print("VERIFICATION SUMMARY")
        print("="*60)
        print(f"✅ Passed: {len(self.passed)}")
        print(f"❌ Failed: {len(self.failed)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        
        if self.failed:
            print("\nFailed checks:")
            for msg in self.failed:
                print(f"  - {msg}")
        
        if self.warnings:
            print("\nWarnings:")
            for msg in self.warnings:
                print(f"  - {msg}")
        
        print("="*60)
        
        if not self.failed:
            print("✅ All checks passed! Ready to run.")
            return True
        else:
            print("❌ Some checks failed. Please fix before running.")
            return False


def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        return f"Python {version.major}.{version.minor}.{version.micro}"
    else:
        return None


def check_module(module_name: str, package_name: str = None):
    """Check if module is installed"""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False


def check_file_exists(filepath: str) -> bool:
    """Check if file exists"""
    return Path(filepath).exists()


def main():
    report = VerificationReport()
    
    print("="*60)
    print("PASSIVE LIVENESS API - SETUP VERIFICATION")
    print("="*60)
    print()
    
    # Check Python version
    print("1. Checking Python version...")
    py_version = check_python_version()
    if py_version:
        report.success(f"Python {py_version}")
    else:
        report.error("Python 3.8+ required")
    
    # Check required files
    print("\n2. Checking project files...")
    required_files = [
        'main.py',
        'model.py',
        'image_processing.py',
        'feature_extractors.py',
        'test_api.py',
        'requirements.txt',
        'README.md'
    ]
    
    for filepath in required_files:
        if check_file_exists(filepath):
            report.success(f"Found {filepath}")
        else:
            report.error(f"Missing {filepath}")
    
    # Check Python dependencies
    print("\n3. Checking Python dependencies...")
    dependencies = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('torch', 'PyTorch'),
        ('torchvision', 'TorchVision'),
        ('cv2', 'OpenCV'),
        ('numpy', 'NumPy'),
        ('PIL', 'Pillow'),
        ('skimage', 'scikit-image'),
        ('sklearn', 'scikit-learn'),
        ('scipy', 'SciPy'),
    ]
    
    for module, name in dependencies:
        if check_module(module):
            report.success(f"{name} installed")
        else:
            report.error(f"{name} not installed - run: pip install -r requirements.txt")
    
    # Check configuration
    print("\n4. Checking configuration...")
    if check_file_exists('.env.example'):
        report.success("Configuration template found (.env.example)")
    else:
        report.warning("Configuration template not found")
    
    # Check port availability
    print("\n5. Checking system configuration...")
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 8000))
        sock.close()
        
        if result != 0:
            report.success("Port 8000 is available")
        else:
            report.warning("Port 8000 appears to be in use")
    except Exception as e:
        report.warning(f"Could not check port availability: {e}")
    
    # Check disk space
    print("\n6. Checking system resources...")
    try:
        import shutil
        stat = shutil.disk_usage('.')
        free_gb = stat.free / (1024**3)
        if free_gb > 1:
            report.success(f"Sufficient disk space ({free_gb:.1f} GB free)")
        else:
            report.warning(f"Low disk space ({free_gb:.1f} GB free)")
    except Exception as e:
        report.warning(f"Could not check disk space: {e}")
    
    # Final summary
    print()
    success = report.print_summary()
    
    if success:
        print("""
NEXT STEPS:
1. Start the server:
   python -m uvicorn main:app --reload

2. In another terminal, run tests:
   python test_api.py

3. View API docs:
   http://localhost:8000/docs
        """)
        sys.exit(0)
    else:
        print("""
INSTALLATION:
pip install -r requirements.txt

TROUBLESHOOTING:
- For PyTorch CPU: pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
- For OpenCV issues: pip install opencv-python
        """)
        sys.exit(1)


if __name__ == "__main__":
    main()
