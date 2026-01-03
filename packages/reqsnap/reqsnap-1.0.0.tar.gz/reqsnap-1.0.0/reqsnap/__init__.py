
"""
ReqSnap - Python Requirements Snapshot Tool
Lock exact installed versions of only the main libraries listed in requirements.txt
"""

__version__ = "1.0.0"
__author__ = "Ahmed2797"
__email__ = "tanvirahmed754575@gmail.com"

from .core import RequirementsLocker
from .cli import main
