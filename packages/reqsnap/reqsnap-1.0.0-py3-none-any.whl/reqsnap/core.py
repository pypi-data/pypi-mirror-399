
"""
Core functionality for ReqSnap
"""

import json
import sys
import datetime
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import subprocess

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    import toml
    TOML_AVAILABLE = True
except ImportError:
    TOML_AVAILABLE = False

try:
    from importlib.metadata import version as get_version, PackageNotFoundError
except ImportError:
    from importlib_metadata import version as get_version, PackageNotFoundError

#from .exception import RequirementsFileError, LockFileError, PackageNotFoundError as ReqSnapPackageNotFoundError
import sys
from reqsnap.exception import CustomException
from reqsnap.logger import logging


class RequirementsLocker:
    """
    Main class for locking requirements
    - Reads only main libraries from requirements.txt
    - Detects installed versions
    - Creates clean lock files
    """
    
    def __init__(self, requirements_file: str = "requirements.txt"):
        """
        Initialize RequirementsLocker
        
        Args:
            requirements_file: Path to requirements.txt file
        """
        self.requirements_file = Path(requirements_file)
        self.lock_file = Path("requirements.lock")
    
    def _extract_package_name(self, line: str) -> Optional[str]:
        """
        Extract clean package name from a requirements line
        
        Args:
            line: A line from requirements.txt
        
        Returns:
            Package name or None if invalid
        """
        # Remove comments
        line = line.split('#')[0].strip()
        if not line:
            return None
        
        # Remove extras like [security,dev]
        if '[' in line and ']' in line:
            line = line.split('[')[0].strip()
        
        # Remove version specifiers
        operators = ['==', '!=', '<=', '>=', '<', '>', '~=', '===']
        for op in operators:
            if op in line:
                line = line.split(op)[0].strip()
        
        # Remove whitespace and validate
        line = line.strip()
        
        # Validate package name pattern
        if re.match(r'^[a-zA-Z][a-zA-Z0-9._-]*$', line):
            return line
        
        return None
    
    def read_requirements(self) -> List[Tuple[str, str]]:
        """
        Read and parse requirements file
        
        Returns:
            List of tuples (package_name, original_line)
        
        Raises:
            RequirementsFileError: If file not found or invalid
        """
        if not self.requirements_file.exists():
            logging.info(
                f"Requirements file not found: {self.requirements_file}"
            )
        
        packages = []
        
        try:
            with open(self.requirements_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    original_line = line.strip()
                    
                    # Skip empty lines and comments
                    if not original_line or original_line.startswith('#'):
                        continue
                    
                    package_name = self._extract_package_name(original_line)
                    
                    if package_name:
                        packages.append((package_name, original_line))
                    else:
                        print(f"⚠️  Warning: Line {line_num} ignored: {original_line}")
            
            return packages
            
        except Exception as e:
            raise CustomException(f"Error reading requirements file: {e}",sys)
    
    def get_installed_version(self, package_name: str) -> Optional[str]:
        """
        Get installed version of a package
        
        Args:
            package_name: Name of the package
        
        Returns:
            Version string or None if not installed
        """
        try:
            return get_version(package_name)
        except Exception as e:
            return None
    
    def check_packages(self) -> Dict[str, Dict[str, Any]]:
        """
        Check all packages in requirements file
        
        Returns:
            Dictionary with package information
        """
        packages = self.read_requirements()
        results = {}
        
        print(f"🔍 Checking {len(packages)} packages...")
        
        for package_name, original_line in packages:
            version = self.get_installed_version(package_name)
            
            results[package_name] = {
                "name": package_name,
                "original_spec": original_line,
                "installed": version is not None,
                "version": version,
                "status": "installed" if version else "not_installed"
            }
        
        return results
    
    def generate_lock_data(self, format: str = "lock") -> Dict[str, Any]:
        """
        Generate lock data from requirements
        
        Args:
            format: Output format (lock, json, yaml, toml)
        
        Returns:
            Lock data dictionary
        """
        packages_info = self.check_packages()
        
        # Prepare metadata
        metadata = {
            "generated": datetime.datetime.now().isoformat(),
            "python_version": sys.version.split()[0],
            "platform": sys.platform,
            "requirements_file": str(self.requirements_file),
            "tool": f"ReqSnap v{__import__('reqsnap').__version__}"
        }
        
        # Prepare packages data
        packages_data = {}
        installed_count = 0
        
        for pkg_name, info in packages_info.items():
            packages_data[pkg_name] = {
                "name": pkg_name,
                "original_spec": info["original_spec"],
                "locked_version": info["version"] or "NOT_INSTALLED",
                "installed": info["installed"],
                "status": info["status"]
            }
            
            if info["installed"]:
                installed_count += 1
        
        # Prepare summary
        summary = {
            "total_packages": len(packages_info),
            "installed": installed_count,
            "not_installed": len(packages_info) - installed_count,
            "lock_format": format
        }
        
        # Combine all data
        lock_data = {
            "metadata": metadata,
            "packages": packages_data,
            "summary": summary
        }
        
        return lock_data
    
    def save_lock_file(self, lock_data: Dict[str, Any], 
                      output_file: str = "requirements.lock",
                      format: str = "lock") -> Path:
        """
        Save lock data to file
        
        Args:
            lock_data: Lock data dictionary
            output_file: Output file path
            format: Output format
        
        Returns:
            Path to saved file
        
        Raises:
            LockFileError: If there's an error saving the file
        """
        output_path = Path(output_file)
        
        try:
            if format == "json":
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(lock_data, f, indent=2, ensure_ascii=False)
            
            elif format == "yaml":
                if not YAML_AVAILABLE:
                    raise ImportError(
                        "PyYAML is required for YAML format. "
                        "Install with: pip install pyyaml"
                    )
                with open(output_path, 'w', encoding='utf-8') as f:
                    yaml.dump(lock_data, f, default_flow_style=False)
            
            elif format == "toml":
                if not TOML_AVAILABLE:
                    raise ImportError(
                        "toml is required for TOML format. "
                        "Install with: pip install toml"
                    )
                with open(output_path, 'w', encoding='utf-8') as f:
                    toml.dump(lock_data, f)
            
            elif format == "lock":
                # Traditional requirements.lock format
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write("# Generated by ReqSnap\n")
                    f.write(f"# Date: {lock_data['metadata']['generated']}\n")
                    f.write(f"# Python: {lock_data['metadata']['python_version']}\n")
                    f.write(f"# Source: {lock_data['metadata']['requirements_file']}\n\n")
                    
                    for pkg_name, info in sorted(lock_data["packages"].items()):
                        if info["installed"]:
                            f.write(f"{pkg_name}=={info['locked_version']}\n")
                        else:
                            f.write(f"# {pkg_name} (not installed)\n")
            
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            return output_path
            
        except Exception as e:
            raise CustomException(f"Error saving lock file: {e}",sys)
    
    def compare_with_previous(self) -> Dict[str, List[str]]:
        """
        Compare current requirements with previous lock file
        
        Returns:
            Dictionary with added, removed, and changed packages
        """
        if not self.lock_file.exists():
            return {"added": [], "removed": [], "changed": []}
        
        current_packages = set([pkg for pkg, _ in self.read_requirements()])
        
        try:
            with open(self.lock_file, 'r', encoding='utf-8') as f:
                previous_lines = f.readlines()
            
            previous_packages = {}
            for line in previous_lines:
                line = line.strip()
                if line and not line.startswith('#') and '==' in line:
                    parts = line.split('==')
                    if len(parts) == 2:
                        previous_packages[parts[0].strip()] = parts[1].strip()
            
            previous_set = set(previous_packages.keys())
            
            # Find differences
            added = sorted(current_packages - previous_set)
            removed = sorted(previous_set - current_packages)
            
            # Find changed versions
            changed = []
            for pkg in sorted(current_packages & previous_set):
                current_version = self.get_installed_version(pkg)
                if current_version and current_version != previous_packages[pkg]:
                    changed.append(f"{pkg}: {previous_packages[pkg]} -> {current_version}")
            
            return {
                "added": added,
                "removed": removed,
                "changed": changed
            }
            
        except Exception:
            return {"added": [], "removed": [], "changed": []}
    
    def validate_requirements(self) -> Tuple[bool, List[str]]:
        """
        Validate requirements file
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        if not self.requirements_file.exists():
            issues.append(f"File not found: {self.requirements_file}")
            return False, issues
        
        try:
            packages = self.read_requirements()
            
            if len(packages) == 0:
                issues.append("No valid packages found in requirements file")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            issues.append(f"Error reading file: {e}")
            return False, issues
