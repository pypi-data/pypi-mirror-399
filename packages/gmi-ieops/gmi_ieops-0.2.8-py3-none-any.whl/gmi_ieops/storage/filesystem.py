"""
FileSystem SDK - User-isolated Distributed File System Access

Based on NFS userspace client, provides:
- User directory isolation (pid/fs_name/oid/uid)
- Distributed file locks
- Transparent open() interception (auto-enabled via IEOPS_NFS_SERVER env var)
"""

import os
import builtins
from typing import Optional, Generator, List, TYPE_CHECKING
from contextlib import contextmanager

# Lazy import to avoid crash when libnfs is not installed
_nfs_module = None
_nfs_available = None

def _ensure_nfs_module():
    """Lazy load nfs module, returns True if available"""
    global _nfs_module, _nfs_available
    if _nfs_available is not None:
        return _nfs_available
    try:
        from . import nfs as _nfs
        _nfs_module = _nfs
        _nfs_available = True
        return True
    except (ImportError, OSError) as e:
        _nfs_available = False
        return False

def _get_nfs_class(name: str):
    """Get class from nfs module"""
    if not _ensure_nfs_module():
        raise ImportError("NFS module not available. Please install libnfs: apt-get install libnfs-dev")
    return getattr(_nfs_module, name)

# Type hints for IDE
if TYPE_CHECKING:
    from .nfs import NFSFileSystem as BaseNFSFileSystem, NFSFile, NFSError, NFSLockError, FileStat, DirEntry

from ..config import env


# ============================================================================
# Path Configuration (from config)
# ============================================================================

def _get_base_nfs_path() -> str:
    """Get user base NFS path: /{pid}/{fs_name}/{oid}/{uid}"""
    return f"/{env.storage.pid}/{env.storage.fs_name}/{env.storage.oid}/{env.storage.uid}"


def _create_nfs_path(path: str) -> str:
    """Create NFS path: /{pid}/{fs_name}/{oid}/{uid}/{path}"""
    path = path.strip('/')
    base = _get_base_nfs_path()
    return f"{base}/{path}" if path else base


def _is_path_allowed(nfs_path: str) -> bool:
    """Check if path is within user directory (prevent path traversal attacks)"""
    base = os.path.normpath(_get_base_nfs_path())
    normalized = os.path.normpath(nfs_path)
    return normalized == base or normalized.startswith(base + '/')


def _create_safe_nfs_path(path: str) -> str:
    """Create and validate NFS path, prevent path traversal attacks"""
    nfs_path = _create_nfs_path(path)
    if not _is_path_allowed(nfs_path):
        raise PermissionError(f"Path not allowed (outside user directory): {path}")
    return nfs_path


# ============================================================================
# FileSystem Class
# ============================================================================

class FileSystem:
    """
    User-isolated FileSystem
    
    All paths are prefixed with: /{pid}/{fs_name}/{oid}/{uid}/
    """
    
    def __init__(self, server: str, export: str = "/", auto_mkdir: bool = True, port: Optional[int] = None):
        """
        Initialize FileSystem
        
        Args:
            server: NFS server address (IP or hostname)
            export: Export path
            auto_mkdir: Auto create user directory
            port: NFS port (optional, default 2049, requires libnfs 6.x+)
        """
        BaseNFSFileSystem = _get_nfs_class('NFSFileSystem')
        self._nfs = BaseNFSFileSystem(server, export, port=port)
        if auto_mkdir:
            self._ensure_user_dir()
    
    def _ensure_user_dir(self):
        """Ensure user directory exists"""
        try:
            NFSError = _get_nfs_class('NFSError')
            self._nfs.mkdir(_get_base_nfs_path(), parents=True, exist_ok=True)
        except Exception:
            pass
    
    @property
    def base_path(self) -> str:
        """User base path"""
        return _get_base_nfs_path()
    
    # ============ File Operations ============
    
    def open(self, path: str, mode: str = 'r', 
             encoding: Optional[str] = None, errors: Optional[str] = None) -> "NFSFile":
        """Open file"""
        return self._nfs.open(_create_safe_nfs_path(path), mode, encoding, errors)
    
    @contextmanager
    def locked_open(self, path: str, mode: str = 'r', exclusive: bool = True, blocking: bool = True):
        """Open file with lock (context manager)"""
        with self._nfs.locked_open(_create_safe_nfs_path(path), mode, exclusive, blocking) as f:
            yield f
    
    # ============ Directory Operations ============
    
    def mkdir(self, path: str, parents: bool = False, exist_ok: bool = False):
        """Create directory"""
        self._nfs.mkdir(_create_safe_nfs_path(path), parents, exist_ok)
    
    def rmdir(self, path: str):
        """Remove empty directory"""
        self._nfs.rmdir(_create_safe_nfs_path(path))
    
    def listdir(self, path: str = "") -> List[str]:
        """List directory contents"""
        return self._nfs.listdir(_create_safe_nfs_path(path))
    
    def scandir(self, path: str = "") -> List["DirEntry"]:
        """List directory contents (with detailed info)"""
        return self._nfs.scandir(_create_safe_nfs_path(path))
    
    def walk(self, path: str = "") -> Generator:
        """Recursively traverse directory"""
        full_path = _create_safe_nfs_path(path)
        base_len = len(_get_base_nfs_path())
        for dirpath, dirnames, filenames in self._nfs.walk(full_path):
            rel_path = dirpath[base_len:].lstrip('/')
            yield (rel_path, dirnames, filenames)
    
    # ============ File Info ============
    
    def exists(self, path: str) -> bool:
        return self._nfs.exists(_create_safe_nfs_path(path))
    
    def isfile(self, path: str) -> bool:
        return self._nfs.isfile(_create_safe_nfs_path(path))
    
    def isdir(self, path: str) -> bool:
        return self._nfs.isdir(_create_safe_nfs_path(path))
    
    def stat(self, path: str) -> "FileStat":
        return self._nfs.stat(_create_safe_nfs_path(path))
    
    def getsize(self, path: str) -> int:
        return self._nfs.getsize(_create_safe_nfs_path(path))
    
    # ============ File Management ============
    
    def remove(self, path: str):
        """Remove file"""
        self._nfs.remove(_create_safe_nfs_path(path))
    
    unlink = remove
    
    def rename(self, src: str, dst: str):
        """Rename/move file"""
        self._nfs.rename(_create_safe_nfs_path(src), _create_safe_nfs_path(dst))
    
    def copy(self, src: str, dst: str):
        """Copy file"""
        self._nfs.copy(_create_safe_nfs_path(src), _create_safe_nfs_path(dst))
    
    def chmod(self, path: str, mode: int):
        """Change file permissions"""
        self._nfs.chmod(_create_safe_nfs_path(path), mode)
    
    # ============ Context Manager ============
    
    def close(self):
        self._nfs.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False


# ============================================================================
# Open Interception - Auto-enabled via IEOPS_NFS_SERVER env var
# ============================================================================

_builtin_open = builtins.open
_global_nfs = None  # Will be NFSFileSystem instance when enabled
_nfs_init_error = None  # Store initialization error for better error messages


# ============================================================================
# gmifs:// Protocol - Explicit NFS Path Prefix
# ============================================================================
#
# Use gmifs:// prefix to explicitly route to NFS storage:
#   open("gmifs://output/image.png", "wb")  -> NFS: /{pid}/{fs}/{oid}/{uid}/output/image.png
#   open("/data/local/file.txt", "w")       -> Local filesystem (default)
#
# This is simpler and clearer than auto-interception rules!

GMIFS_PROTOCOL = "gmifs://"


def _intercepted_open(file, mode='r', buffering=-1, encoding=None, 
                      errors=None, newline=None, closefd=True, opener=None):
    """
    Intercepted open function - routes gmifs:// paths to NFS
    
    Use gmifs:// prefix to explicitly route to NFS storage:
        open("gmifs://output/image.png", "wb")  -> NFS
        open("/data/local/file.txt", "w")       -> Local (default)
    
    Examples:
        - "gmifs://output.png"      -> NFS: /{pid}/{fs}/{oid}/{uid}/output.png
        - "gmifs://data/result.json"-> NFS: /{pid}/{fs}/{oid}/{uid}/data/result.json
        - "/data/models/model.bin"  -> Local filesystem
        - "local_file.txt"          -> Local filesystem
    """
    global _global_nfs
    
    file_str = str(file)
    
    # Check for gmifs:// protocol prefix
    if file_str.startswith(GMIFS_PROTOCOL):
        # Extract path after gmifs://
        nfs_rel_path = file_str[len(GMIFS_PROTOCOL):]
        
        # NFS not configured or initialization failed
        if _global_nfs is None:
            if _nfs_init_error:
                raise IOError(f"Cannot open '{file_str}': NFS initialization failed - {_nfs_init_error}")
            else:
                raise IOError(f"Cannot open '{file_str}': NFS not configured (IEOPS_NFS_SERVER not set or storage module not imported)")
        
        # Create full NFS path with user isolation
        nfs_path = _create_safe_nfs_path(nfs_rel_path)
        nfs_mode = mode.replace('t', '')
        
        try:
            # Auto-create parent directories for write modes
            if any(c in mode for c in 'wax'):
                import os as _os
                parent_dir = _os.path.dirname(nfs_path)
                if parent_dir:
                    try:
                        _global_nfs.mkdir(parent_dir, parents=True, exist_ok=True)
                    except Exception:
                        pass  # Directory may already exist
            
            return _global_nfs.open(nfs_path, nfs_mode, encoding, errors)
        except Exception as e:
            raise IOError(f"Failed to open NFS file '{nfs_path}': {e}")
    
    # No gmifs:// prefix - use native open
    return _builtin_open(file, mode, buffering, encoding, errors, newline, closefd, opener)


def _parse_nfs_server(server_str: str) -> tuple:
    """Parse server:port format, returns (host, port)"""
    if ':' in server_str:
        parts = server_str.rsplit(':', 1)  # rsplit for IPv6 support
        try:
            port = int(parts[1])
            return parts[0], port
        except ValueError:
            pass
    return server_str, None


def enable_nfs_intercept() -> bool:
    """
    Enable gmifs:// protocol support for open()
    
    After calling this, you can use gmifs:// prefix to write to NFS:
        open("gmifs://output/image.png", "wb")  -> NFS: /{pid}/{fs}/{oid}/{uid}/output/image.png
        open("/local/file.txt", "w")            -> Local filesystem (unchanged)
    
    Requires IEOPS_NFS_SERVER environment variable.
    Supports server:port format (e.g., "10.0.0.1:32049", requires libnfs 6.x+)
        
    Returns:
        True if enabled successfully, False if IEOPS_NFS_SERVER is not configured
    """
    global _global_nfs
    
    server = env.storage.nfs_server
    if not server:
        return False
    
    if _global_nfs is not None:
        try:
            _global_nfs.close()
        except Exception:
            pass
    
    # Parse server:port
    host, port = _parse_nfs_server(server)
    
    # Get NFS classes (lazy loaded)
    NFSFileSystem = _get_nfs_class('NFSFileSystem')
    _global_nfs = NFSFileSystem(host, "/", port=port)
    
    # Ensure user directory exists
    try:
        _global_nfs.mkdir(_get_base_nfs_path(), parents=True, exist_ok=True)
    except Exception:
        pass
    
    builtins.open = _intercepted_open
    return True


def disable_nfs_intercept():
    """Disable NFS open() interception and release resources"""
    global _global_nfs
    
    builtins.open = _builtin_open
    
    if _global_nfs is not None:
        try:
            _global_nfs.close()
        except Exception:
            pass
        _global_nfs = None


# Auto-enable NFS interception if IEOPS_NFS_SERVER is configured
# This is safe because only gmifs:// prefixed paths are routed to NFS
# Normal file operations (torch, diffusers, etc.) are NOT affected
def _auto_enable_nfs():
    global _nfs_init_error
    if env.storage.nfs_server:
        try:
            enable_nfs_intercept()
        except Exception as e:
            # Store error for better error messages when gmifs:// is used
            _nfs_init_error = str(e)
            # Still register interceptor to provide clear error messages
            builtins.open = _intercepted_open

_auto_enable_nfs()

