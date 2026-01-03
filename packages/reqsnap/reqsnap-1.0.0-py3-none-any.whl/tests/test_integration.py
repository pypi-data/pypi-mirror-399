
"""
Integration tests for ReqSnap
"""

import sys
import tempfile
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_package_installation():
    """Test that package can be installed and imported"""
    # Try to import
    try:
        from reqsnap import __version__
        from reqsnap.core import RequirementsLocker
        from reqsnap.cli import main
        
        print(f"✅ Package imports work (v{__version__})")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_cli_from_command_line():
    """Test CLI from command line"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("requests\n")
        temp_file = f.name
    
    try:
        # Run reqsnap via python -m
        result = subprocess.run(
            [sys.executable, "-m", "reqsnap.cli", "--version"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and ("ReqSnap" in result.stdout or "1.0.0" in result.stdout):
            print("✅ CLI works via python -m")
        else:
            print(f"❌ CLI failed: {result.stderr}")
        
        # Clean up any generated files
        lock_file = Path(temp_file).with_suffix('.lock')
        if lock_file.exists():
            lock_file.unlink()
            
    finally:
        Path(temp_file).unlink()


def test_full_workflow():
    """Test full workflow: read -> lock -> save"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("requests\nflask\ndjango\nnumpy\n")
        temp_file = f.name
    
    try:
        from reqsnap.core import RequirementsLocker
        
        # Create locker
        locker = RequirementsLocker(temp_file)
        
        # Read requirements
        packages = locker.read_requirements()
        print(f"✅ Read {len(packages)} packages")
        
        # Generate lock data
        lock_data = locker.generate_lock_data()
        print(f"✅ Generated lock data: {lock_data['summary']}")
        
        # Save in all formats
        formats = ['lock', 'json', 'yaml', 'toml']
        for fmt in formats:
            if fmt == 'yaml':
                try:
                    import yaml
                except ImportError:
                    continue
            elif fmt == 'toml':
                try:
                    import toml
                except ImportError:
                    continue
            
            output_file = Path(temp_file).with_suffix(f'.{fmt}')
            try:
                locker.save_lock_file(lock_data, str(output_file), fmt)
                print(f"✅ Saved {fmt.upper()} format")
                output_file.unlink()  # Clean up
            except Exception as e:
                print(f"⚠️  Could not save {fmt}: {e}")
        
        print("✅ Full workflow completed")
        
    except Exception as e:
        print(f"❌ Workflow failed: {e}")
    finally:
        Path(temp_file).unlink()


def test_error_handling():
    """Test error handling"""
    from reqsnap.core import RequirementsLocker
    
    # Test non-existent file
    try:
        locker = RequirementsLocker("non_existent_file.txt")
        locker.read_requirements()
        print("❌ Should have raised an error for non-existent file")
    except Exception as e:
        print("✅ Correctly raised error for non-existent file")
    
    # Test empty file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("")  # Empty file
        temp_file = f.name
    
    try:
        locker = RequirementsLocker(temp_file)
        packages = locker.read_requirements()
        assert len(packages) == 0
        print("✅ Handled empty file correctly")
    finally:
        Path(temp_file).unlink()


if __name__ == "__main__":
    print("🧪 Running integration tests...")
    
    test_package_installation()
    test_cli_from_command_line()
    test_full_workflow()
    test_error_handling()
    
    print("\n🎉 All integration tests completed!")
