
"""
Utility functions for ReqSnap
"""

import re
import os
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any


def clean_package_name(package_name: str) -> str:
    """
    Clean package name by removing version specifiers and extras
    
    Args:
        package_name: Raw package name
    
    Returns:
        Cleaned package name
    """
    # Remove extras [security,dev]
    if '[' in package_name and ']' in package_name:
        package_name = package_name.split('[')[0]
    
    # Remove version specifiers
    operators = ['==', '!=', '<=', '>=', '<', '>', '~=', '===']
    for op in operators:
        if op in package_name:
            package_name = package_name.split(op)[0]
    
    return package_name.strip()


def is_valid_package_name(name: str) -> bool:
    """
    Check if a string is a valid Python package name
    
    Args:
        name: Package name to validate
    
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z][a-zA-Z0-9._-]*$'
    return bool(re.match(pattern, name))


def find_requirements_files(directory: str = ".") -> List[str]:
    """
    Find all requirements files in a directory
    
    Args:
        directory: Directory to search
    
    Returns:
        List of requirements file paths
    """
    directory_path = Path(directory)
    requirements_files = []
    
    patterns = [
        "requirements*.txt",
        "req*.txt",
        "*.requirements",
        "requirements/*.txt"
    ]
    
    for pattern in patterns:
        for file_path in directory_path.rglob(pattern):
            if file_path.is_file():
                requirements_files.append(str(file_path))
    
    return sorted(set(requirements_files))


def get_python_version() -> str:
    """
    Get current Python version
    
    Returns:
        Python version string
    """
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def format_file_size(file_path: str) -> str:
    """
    Format file size in human readable format
    
    Args:
        file_path: Path to file
    
    Returns:
        Formatted file size string
    """
    size = os.path.getsize(file_path)
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    
    return f"{size:.1f} TB"


def print_table(headers: List[str], rows: List[List[str]]) -> None:
    """
    Print a formatted table
    
    Args:
        headers: Table headers
        rows: Table rows
    """
    if not rows:
        return
    
    # Calculate column widths
    col_widths = []
    for i in range(len(headers)):
        max_width = len(headers[i])
        for row in rows:
            if i < len(row):
                max_width = max(max_width, len(str(row[i])))
        col_widths.append(max_width + 2)  # Add padding
    
    # Print headers
    header_row = " | ".join(
        headers[i].ljust(col_widths[i]) for i in range(len(headers))
    )
    print(header_row)
    print("-" * len(header_row))
    
    # Print rows
    for row in rows:
        row_str = " | ".join(
            str(row[i]).ljust(col_widths[i]) 
            for i in range(len(row)) if i < len(row)
        )
        print(row_str)
