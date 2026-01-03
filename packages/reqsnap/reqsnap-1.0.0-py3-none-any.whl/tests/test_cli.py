
"""
CLI tests for ReqSnap
"""

import sys
import tempfile
from pathlib import Path
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from reqsnap.cli import main


def test_cli_version():
    """Test CLI version command"""
    # Capture output
    output = StringIO()
    
    # Temporarily replace sys.argv
    original_argv = sys.argv
    sys.argv = ['reqsnap', '--version']
    
    try:
        with redirect_stdout(output):
            main()
    except SystemExit:
        pass  # CLI正常退出
    finally:
        sys.argv = original_argv
    
    result = output.getvalue()
    assert "ReqSnap" in result or "1.0.0" in result
    print("✅ CLI version command works")


def test_cli_help():
    """Test CLI help command"""
    output = StringIO()
    original_argv = sys.argv
    sys.argv = ['reqsnap', '--help']
    
    try:
        with redirect_stdout(output):
            main()
    except SystemExit:
        pass
    finally:
        sys.argv = original_argv
    
    result = output.getvalue()
    assert "usage:" in result.lower() or "help" in result.lower()
    print("✅ CLI help command works")


def test_cli_lock_command():
    """Test CLI lock command"""
    # Create a test requirements file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("requests\n")
        temp_file = f.name
    
    output = StringIO()
    original_argv = sys.argv
    
    try:
        # Test lock command
        sys.argv = ['reqsnap', 'lock', '-f', temp_file, '--format', 'lock']
        
        with redirect_stdout(output):
            main()
    except SystemExit:
        pass
    finally:
        sys.argv = original_argv
        # Clean up
        lock_file = Path(temp_file).with_suffix('.lock')
        if lock_file.exists():
            lock_file.unlink()
        Path(temp_file).unlink()
    
    result = output.getvalue()
    assert "Lock file" in result or "saved" in result.lower()
    print("✅ CLI lock command works")


def test_cli_check_command():
    """Test CLI check command"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("requests\nflask\n")
        temp_file = f.name
    
    output = StringIO()
    original_argv = sys.argv
    
    try:
        sys.argv = ['reqsnap', 'check', '-f', temp_file]
        
        with redirect_stdout(output):
            main()
    except SystemExit:
        pass
    finally:
        sys.argv = original_argv
        Path(temp_file).unlink()
    
    result = output.getvalue()
    assert "Checking" in result or "packages" in result.lower()
    print("✅ CLI check command works")


def test_cli_validate_command():
    """Test CLI validate command"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("requests\nflask\n")
        temp_file = f.name
    
    output = StringIO()
    original_argv = sys.argv
    
    try:
        sys.argv = ['reqsnap', 'validate', '-f', temp_file]
        
        with redirect_stdout(output):
            main()
    except SystemExit:
        pass
    finally:
        sys.argv = original_argv
        Path(temp_file).unlink()
    
    result = output.getvalue()
    assert "valid" in result.lower() or "found" in result.lower()
    print("✅ CLI validate command works")


if __name__ == "__main__":
    test_cli_version()
    test_cli_help()
    test_cli_lock_command()
    test_cli_check_command()
    test_cli_validate_command()
    print("\n🎉 All CLI tests passed!")
