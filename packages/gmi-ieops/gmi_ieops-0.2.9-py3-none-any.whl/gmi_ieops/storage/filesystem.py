"""
FileSystem SDK - User-isolated Distributed File System Access

Supports multiple backends:
- NFS (via libnfs) - High performance, requires libnfs-dev
- WebDAV (via webdavclient3) - No special deps, works in unprivileged containers

Auto-selects backend based on environment variables:
- IEOPS_WEBDAV_URL -> WebDAV
- IEOPS_NFS_SERVER -> NFS

Usage:
    # Auto-select backend based on env vars
    fs = FileSystem()
    
    # Or explicitly specify backend
    fs = FileSystem(backend="webdav", hostname="http://10.0.0.1:5000")
    fs = FileSystem(backend="nfs", server="10.0.0.1", port=32049)
"""

import os
from typing import Optional, Generator, List, TYPE_CHECKING, Union, Literal
from contextlib import contextmanager

# Lazy import to avoid crash when libnfs is not installed
_nfs_module = None
_nfs_available = None
_webdav_module = None
_webdav_available = None

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

def _ensure_webdav_module():
    """Lazy load webdav module, returns True if available"""
    global _webdav_module, _webdav_available
    if _webdav_available is not None:
        return _webdav_available
    try:
        from . import webdav as _webdav
        _webdav_module = _webdav
        _webdav_available = True
        return True
    except ImportError:
        _webdav_available = False
        return False

def _get_webdav_class(name: str):
    """Get class from webdav module"""
    if not _ensure_webdav_module():
        raise ImportError("WebDAV module not available. Please install: pip install webdavclient3")
    return getattr(_webdav_module, name)

# Type hints for IDE
if TYPE_CHECKING:
    from .nfs import NFSFileSystem as BaseNFSFileSystem, NFSFile, NFSError, NFSLockError, FileStat, DirEntry
    from .webdav import WebDAVFileSystem, WebDAVFile

from ..config import env


# ============================================================================
# Path Configuration (from config)
# ============================================================================

def _get_base_path() -> str:
    """Get user base path: /{pid}/{fs_name}/{oid}/{uid}"""
    return f"/{env.storage.pid}/{env.storage.fs_name}/{env.storage.oid}/{env.storage.uid}"

# Alias for backward compatibility
_get_base_nfs_path = _get_base_path


def _create_path(path: str) -> str:
    """Create full path: /{pid}/{fs_name}/{oid}/{uid}/{path}"""
    path = path.strip('/')
    base = _get_base_path()
    return f"{base}/{path}" if path else base

# Alias for backward compatibility
_create_nfs_path = _create_path


def _is_path_allowed(full_path: str) -> bool:
    """Check if path is within user directory (prevent path traversal attacks)"""
    base = os.path.normpath(_get_base_path())
    normalized = os.path.normpath(full_path)
    return normalized == base or normalized.startswith(base + '/')


def _create_safe_path(path: str) -> str:
    """Create and validate path, prevent path traversal attacks"""
    full_path = _create_path(path)
    if not _is_path_allowed(full_path):
        raise PermissionError(f"Path not allowed (outside user directory): {path}")
    return full_path

# Alias for backward compatibility
_create_safe_nfs_path = _create_safe_path


# ============================================================================
# FileSystem Class - Unified API with Multiple Backends
# ============================================================================

class FileSystem:
    """
    User-isolated FileSystem with multiple backend support
    
    All paths are prefixed with: /{pid}/{fs_name}/{oid}/{uid}/
    
    Backends:
    - "nfs": NFS via libnfs (high performance, requires libnfs-dev)
    - "webdav": WebDAV via HTTP (no special deps, works in unprivileged containers)
    - "auto": Auto-select based on env vars (IEOPS_WEBDAV_URL or IEOPS_NFS_SERVER)
    
    Usage:
        # Auto-select backend
        fs = FileSystem()
        
        # Explicit NFS
        fs = FileSystem(backend="nfs", server="10.0.0.1", port=32049)
        
        # Explicit WebDAV
        fs = FileSystem(backend="webdav", hostname="http://10.0.0.1:5000", 
                       username="user", password="pass")
    """
    
    def __init__(
        self,
        backend: Literal["auto", "nfs", "webdav"] = "auto",
        # NFS options
        server: Optional[str] = None,
        export: str = "/",
        port: Optional[int] = None,
        # WebDAV options
        hostname: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        # Common options
        auto_mkdir: bool = True,
        timeout: Optional[int] = None,
    ):
        """
        Initialize FileSystem
        
        Args:
            backend: "auto", "nfs", or "webdav"
            
            # NFS options (when backend="nfs")
            server: NFS server address (IP or hostname), or use IEOPS_NFS_SERVER env
            export: NFS export path (default "/")
            port: NFS port (optional, default 2049)
            
            # WebDAV options (when backend="webdav")
            hostname: WebDAV URL (e.g., "http://10.0.0.1:5000"), or use IEOPS_WEBDAV_URL env
            username: WebDAV username, or use IEOPS_WEBDAV_USER env
            password: WebDAV password, or use IEOPS_WEBDAV_PASS env
            
            # Common options
            auto_mkdir: Auto create user directory (default True)
            timeout: Connection timeout
        """
        self._backend_type: str = ""
        self._backend: Union["BaseNFSFileSystem", "WebDAVFileSystem", None] = None
        
        # Auto-detect backend
        if backend == "auto":
            # Priority: NFS > WebDAV (NFS has better performance)
            if server or env.storage.nfs_server:
                backend = "nfs"
            elif hostname or env.storage.webdav_url:
                backend = "webdav"
            else:
                raise ValueError(
                    "No storage backend configured. Set IEOPS_WEBDAV_URL or IEOPS_NFS_SERVER, "
                    "or specify backend='webdav'/'nfs' with connection parameters."
                )
        
        # Initialize backend
        if backend == "webdav":
            self._init_webdav(hostname, username, password, timeout, auto_mkdir)
        elif backend == "nfs":
            self._init_nfs(server, export, port, auto_mkdir)
        else:
            raise ValueError(f"Unknown backend: {backend}")
    
    def _init_nfs(self, server: Optional[str], export: str, port: Optional[int], auto_mkdir: bool):
        """Initialize NFS backend"""
        server = server or env.storage.nfs_server
        if not server:
            raise ValueError("NFS server not specified. Set IEOPS_NFS_SERVER or pass server parameter.")
        
        # Parse server:port format
        if ':' in server and port is None:
            parts = server.rsplit(':', 1)
            try:
                port = int(parts[1])
                server = parts[0]
            except ValueError:
                pass
        
        BaseNFSFileSystem = _get_nfs_class('NFSFileSystem')
        self._backend = BaseNFSFileSystem(server, export, port=port)
        self._backend_type = "nfs"
        
        if auto_mkdir:
            self._ensure_user_dir()
    
    def _init_webdav(self, hostname: Optional[str], username: Optional[str], 
                     password: Optional[str], timeout: Optional[int], auto_mkdir: bool):
        """Initialize WebDAV backend"""
        hostname = hostname or env.storage.webdav_url
        if not hostname:
            raise ValueError("WebDAV hostname not specified. Set IEOPS_WEBDAV_URL or pass hostname parameter.")
        
        username = username or env.storage.webdav_user or None
        password = password or env.storage.webdav_pass or None
        timeout = timeout or env.storage.webdav_timeout
        
        WebDAVClient = _get_webdav_class('WebDAVClient')
        self._backend = WebDAVClient(hostname, username, password, timeout)
        self._backend_type = "webdav"
        
        if auto_mkdir:
            self._ensure_user_dir()
    
    def _ensure_user_dir(self):
        """Ensure user directory exists"""
        try:
            self._backend.mkdir(_get_base_path(), parents=True)
        except Exception:
            pass
    
    @property
    def backend_type(self) -> str:
        """Get current backend type: 'nfs' or 'webdav'"""
        return self._backend_type
    
    @property
    def base_path(self) -> str:
        """User base path"""
        return _get_base_path()
    
    # ============ File Operations ============
    
    def open(self, path: str, mode: str = 'r', 
             encoding: Optional[str] = None, errors: Optional[str] = None):
        """Open file"""
        full_path = _create_safe_path(path)
        
        # Auto-create parent directories for write modes
        if any(c in mode for c in 'wax'):
            parent_dir = os.path.dirname(full_path)
            if parent_dir:
                try:
                    self._backend.mkdir(parent_dir, parents=True)
                except Exception:
                    pass
        
        if self._backend_type == "nfs":
            return self._backend.open(full_path, mode, encoding, errors)
        else:  # webdav
            WebDAVFile = _get_webdav_class('WebDAVFile')
            return WebDAVFile(self._backend, full_path, mode, encoding)
    
    @contextmanager
    def locked_open(self, path: str, mode: str = 'r', exclusive: bool = True, 
                    blocking: bool = True, timeout: int = 3600):
        """Open file with lock (context manager)"""
        full_path = _create_safe_path(path)
        
        if self._backend_type == "nfs":
            with self._backend.locked_open(full_path, mode, exclusive, blocking) as f:
                yield f
        else:  # webdav
            WebDAVFile = _get_webdav_class('WebDAVFile')
            WebDAVLockError = _get_webdav_class('WebDAVLockError')
            token = None
            try:
                token = self._backend.lock(full_path, timeout)
                f = WebDAVFile(self._backend, full_path, mode)
                yield f
                f.close()
            except Exception as e:
                raise WebDAVLockError(f"Failed to lock file: {e}")
            finally:
                if token:
                    try:
                        self._backend.unlock(full_path, token)
                    except Exception:
                        pass
    
    # ============ Directory Operations ============
    
    def mkdir(self, path: str, parents: bool = False, exist_ok: bool = False):
        """Create directory"""
        try:
            self._backend.mkdir(_create_safe_path(path), parents=parents)
        except Exception as e:
            if not exist_ok:
                raise
    
    def rmdir(self, path: str):
        """Remove empty directory"""
        self._backend.rmdir(_create_safe_path(path))
    
    def listdir(self, path: str = "") -> List[str]:
        """List directory contents"""
        return self._backend.listdir(_create_safe_path(path))
    
    def scandir(self, path: str = "") -> List:
        """List directory contents (with detailed info)"""
        return self._backend.scandir(_create_safe_path(path))
    
    def walk(self, path: str = "") -> Generator:
        """Recursively traverse directory"""
        full_path = _create_safe_path(path)
        base_len = len(_get_base_path())
        
        if self._backend_type == "nfs":
            for dirpath, dirnames, filenames in self._backend.walk(full_path):
                rel_path = dirpath[base_len:].lstrip('/')
                yield (rel_path, dirnames, filenames)
        else:  # webdav - implement walk
            def _walk_webdav(current_path):
                entries = self._backend.scandir(current_path)
                dirs = []
                files = []
                for entry in entries:
                    if entry.is_dir:
                        dirs.append(entry.name)
                    else:
                        files.append(entry.name)
                
                rel_path = current_path[base_len:].lstrip('/')
                yield (rel_path, dirs, files)
                
                for d in dirs:
                    yield from _walk_webdav(current_path.rstrip('/') + '/' + d)
            
            yield from _walk_webdav(full_path)
    
    # ============ File Info ============
    
    def exists(self, path: str) -> bool:
        return self._backend.exists(_create_safe_path(path))
    
    def isfile(self, path: str) -> bool:
        return self._backend.isfile(_create_safe_path(path))
    
    def isdir(self, path: str) -> bool:
        return self._backend.isdir(_create_safe_path(path))
    
    def stat(self, path: str):
        """Get file status"""
        return self._backend.stat(_create_safe_path(path))
    
    def getsize(self, path: str) -> int:
        return self._backend.getsize(_create_safe_path(path))
    
    # ============ File Management ============
    
    def remove(self, path: str):
        """Remove file"""
        self._backend.remove(_create_safe_path(path))
    
    unlink = remove
    
    def rename(self, src: str, dst: str):
        """Rename/move file"""
        self._backend.rename(_create_safe_path(src), _create_safe_path(dst))
    
    def copy(self, src: str, dst: str):
        """Copy file"""
        self._backend.copy(_create_safe_path(src), _create_safe_path(dst))
    
    def chmod(self, path: str, mode: int):
        """Change file permissions (NFS only, no-op for WebDAV)"""
        if self._backend_type == "nfs":
            self._backend.chmod(_create_safe_path(path), mode)
        # WebDAV doesn't support chmod, silently ignore
    
    # ============ Context Manager ============
    
    def close(self):
        if hasattr(self._backend, 'close'):
            self._backend.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

