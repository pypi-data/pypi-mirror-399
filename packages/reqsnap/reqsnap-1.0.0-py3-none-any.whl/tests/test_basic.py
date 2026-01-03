
"""
Basic tests for ReqSnap
"""

import sys
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from reqsnap import __version__
from reqsnap.core import RequirementsLocker


def test_version():
    """Test that version is defined"""
    assert __version__ == "1.0.0"
    print(f"✅ Version: {__version__}")


def test_import():
    """Test that core modules can be imported"""
    from reqsnap.core import RequirementsLocker
    from reqsnap.cli import main
    
    locker = RequirementsLocker()
    assert locker is not None
    print("✅ Imports successful")


def test_requirements_locker_initialization():
    """Test RequirementsLocker initialization"""
    locker = RequirementsLocker("requirements.txt")
    assert locker.requirements_file.name == "requirements.txt"
    print("✅ Locker initialized")


def test_read_empty_requirements():
    """Test reading empty requirements file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("# This is a comment\n\n  \n")
        temp_file = f.name
    
    try:
        locker = RequirementsLocker(temp_file)
        packages = locker.read_requirements()
        assert len(packages) == 0  # Should be empty
        print("✅ Empty requirements handled correctly")
    finally:
        Path(temp_file).unlink()


def test_read_requirements_with_packages():
    """Test reading requirements with packages"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("requests>=2.25.0\nflask==2.3.2\ndjango\n# Comment\n")
        temp_file = f.name
    
    try:
        locker = RequirementsLocker(temp_file)
        packages = locker.read_requirements()
        assert len(packages) == 3
        assert packages[0][0] == 'requests'
        assert packages[1][0] == 'flask'
        assert packages[2][0] == 'django'
        print("✅ Requirements parsing correct")
    finally:
        Path(temp_file).unlink()


def test_generate_lock_data():
    """Test lock data generation"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("requests\n")
        temp_file = f.name
    
    try:
        locker = RequirementsLocker(temp_file)
        lock_data = locker.generate_lock_data()
        
        # Check structure
        assert 'metadata' in lock_data
        assert 'packages' in lock_data
        assert 'summary' in lock_data
        assert isinstance(lock_data['summary']['total_packages'], int)
        print("✅ Lock data structure correct")
    finally:
        Path(temp_file).unlink()


if __name__ == "__main__":
    # Run tests manually
    test_version()
    test_import()
    test_requirements_locker_initialization()
    test_read_empty_requirements()
    test_read_requirements_with_packages()
    test_generate_lock_data()
    print("\n🎉 All basic tests passed!")
