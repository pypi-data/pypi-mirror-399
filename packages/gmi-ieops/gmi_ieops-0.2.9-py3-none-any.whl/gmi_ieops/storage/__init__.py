"""
Storage Module - User-isolated Distributed File System Access

Supports two storage backends:
1. NFS (via libnfs) - High performance, requires libnfs-dev
2. WebDAV (via webdavclient3) - No special dependencies, works in unprivileged containers

=== Unified FileSystem API (Recommended) ===

FileSystem auto-selects backend based on env vars:

    from gmi_ieops.storage import FileSystem
    
    # Auto-select backend (NFS if IEOPS_NFS_SERVER, else WebDAV if IEOPS_WEBDAV_URL)
    fs = FileSystem()
    
    # Or explicit backend
    fs = FileSystem(backend="webdav", hostname="http://10.0.0.1:5000")
    fs = FileSystem(backend="nfs", server="10.0.0.1", port=32049)
    
    with fs.open("data.txt", "w") as f:
        f.write("Hello Storage")

=== Protocol Prefix (for open() interception) ===

Use gmifs:// prefix with standard open(), backend auto-selected by env vars:

    from gmi_ieops.storage import enable_storage_intercept
    enable_storage_intercept()  # Auto-enable based on env vars
    
    # Write to remote storage (WebDAV or NFS, depends on env)
    with open("gmifs://output/image.png", "wb") as f:
        f.write(image_data)
    
    # Local files unchanged
    with open("/tmp/local.txt", "w") as f:
        f.write("local")
"""

import builtins
import os
from typing import Optional

from .filesystem import (
    # High-level API (unified, supports both NFS and WebDAV)
    FileSystem,
    # Module availability checks
    _ensure_nfs_module,
    _ensure_webdav_module,
    _get_nfs_class,
    _get_webdav_class,
    # Path utilities
    _get_base_path,
    _create_safe_path,
)

from ..config import env


# ============================================================================
# Protocol Interception - gmifs:// routes to WebDAV or NFS based on config
# ============================================================================

# Protocol constant
GMIFS_PROTOCOL = "gmifs://"

# Global state
_global_fs = None  # FileSystem instance (WebDAV or NFS)
_fs_init_error = None
_builtin_open = builtins.open
_current_backend = None  # 'webdav', 'nfs', or None


def _intercepted_open(file, mode='r', buffering=-1, encoding=None,
                      errors=None, newline=None, closefd=True, opener=None):
    """
    Intercepted open function - routes gmifs:// paths to storage backend
    
    Backend is auto-selected based on env vars:
    - IEOPS_WEBDAV_URL -> WebDAV
    - IEOPS_NFS_SERVER -> NFS
    
    Examples:
        open("gmifs://output/image.png", "wb")  -> Remote storage
        open("/data/local/file.txt", "w")       -> Local (default)
    """
    global _global_fs
    
    file_str = str(file)
    
    # Check for gmifs:// protocol prefix
    if file_str.startswith(GMIFS_PROTOCOL):
        # Extract path after gmifs://
        rel_path = file_str[len(GMIFS_PROTOCOL):]
        
        if _global_fs is None:
            if _fs_init_error:
                raise IOError(f"Cannot open '{file_str}': Storage initialization failed - {_fs_init_error}")
            else:
                raise IOError(f"Cannot open '{file_str}': Storage not configured (set IEOPS_WEBDAV_URL or IEOPS_NFS_SERVER)")
        
        try:
            return _global_fs.open(rel_path, mode, encoding)
        except Exception as e:
            raise IOError(f"Failed to open storage file '{rel_path}': {e}")
    
    # No gmifs:// prefix - use native open
    return _builtin_open(file, mode, buffering, encoding, errors, newline, closefd, opener)


def enable_storage_intercept(
    backend: str = "auto",
    # WebDAV options
    hostname: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    # NFS options
    server: Optional[str] = None,
    port: Optional[int] = None,
) -> str:
    """
    Enable gmifs:// protocol support for open()
    
    Auto-selects backend based on env vars or explicit parameters:
    - IEOPS_NFS_SERVER -> NFS (priority, better performance)
    - IEOPS_WEBDAV_URL -> WebDAV (fallback, works in unprivileged containers)
    
    After calling this, you can use gmifs:// prefix:
        open("gmifs://output/image.png", "wb")  -> Remote storage
        open("/local/file.txt", "w")            -> Local filesystem (unchanged)
    
    Args:
        backend: "auto", "webdav", or "nfs"
        hostname: WebDAV server URL (or use IEOPS_WEBDAV_URL env)
        username: WebDAV username (or use IEOPS_WEBDAV_USER env)
        password: WebDAV password (or use IEOPS_WEBDAV_PASS env)
        server: NFS server address (or use IEOPS_NFS_SERVER env)
        port: NFS port
        
    Returns:
        'webdav', 'nfs', or 'none'
    """
    global _global_fs, _fs_init_error, _current_backend
    
    # Clean up previous instance
    if _global_fs is not None:
        try:
            _global_fs.close()
        except Exception:
            pass
        _global_fs = None
    
    _fs_init_error = None
    _current_backend = None
    
    try:
        # Determine backend (NFS has priority for performance)
        if backend == "auto":
            if server or env.storage.nfs_server:
                backend = "nfs"
            elif hostname or env.storage.webdav_url:
                backend = "webdav"
            else:
                builtins.open = _intercepted_open  # Register for error messages
                return 'none'
        
        # Initialize FileSystem with specified backend
        if backend == "webdav":
            _global_fs = FileSystem(
                backend="webdav",
                hostname=hostname,
                username=username,
                password=password,
                auto_mkdir=True
            )
            _current_backend = 'webdav'
        elif backend == "nfs":
            _global_fs = FileSystem(
                backend="nfs",
                server=server,
                port=port,
                auto_mkdir=True
            )
            _current_backend = 'nfs'
        else:
            raise ValueError(f"Unknown backend: {backend}")
        
        builtins.open = _intercepted_open
        return _current_backend
        
    except Exception as e:
        _fs_init_error = str(e)
        builtins.open = _intercepted_open  # Register for error messages
        return 'none'


def disable_storage_intercept():
    """Disable gmifs:// open() interception"""
    global _global_fs, _current_backend
    
    builtins.open = _builtin_open
    
    if _global_fs is not None:
        try:
            _global_fs.close()
        except Exception:
            pass
        _global_fs = None
    
    _current_backend = None


def get_storage_backend() -> Optional[str]:
    """Get current storage backend type: 'webdav', 'nfs', or None"""
    return _current_backend


# Legacy aliases for backward compatibility
def enable_nfs_intercept() -> bool:
    """Legacy: Enable NFS backend. Use enable_storage_intercept() instead."""
    result = enable_storage_intercept(backend="nfs")
    return result == 'nfs'


def disable_nfs_intercept():
    """Legacy: Disable interception. Use disable_storage_intercept() instead."""
    disable_storage_intercept()


# ============================================================================
# Auto-enable if configured
# ============================================================================

def _auto_enable():
    """Auto-enable storage interception if env vars are configured"""
    if env.storage.webdav_url or env.storage.nfs_server:
        try:
            enable_storage_intercept()
        except Exception as e:
            global _fs_init_error
            _fs_init_error = str(e)
            builtins.open = _intercepted_open

_auto_enable()


# ============================================================================
# Lazy Loading for Optional Dependencies
# ============================================================================

def __getattr__(name):
    """Lazy load classes to avoid crashes when dependencies are not installed"""
    # NFS classes
    if name in ('NFSFile', 'FileStat', 'DirEntry', 'NFSError', 'NFSLockError'):
        return _get_nfs_class(name)
    
    # WebDAV classes
    if name in ('WebDAVFileSystem', 'WebDAVFile', 'WebDAVClient', 'WebDAVError', 'WebDAVLockError'):
        return _get_webdav_class(name)
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # High-level unified API
    'FileSystem',
    # WebDAV-specific classes (lazy loaded)
    'WebDAVFileSystem',
    'WebDAVFile',
    'WebDAVClient',
    # Protocol constant
    'GMIFS_PROTOCOL',
    # Data types (lazy loaded)
    'NFSFile',
    'FileStat',
    'DirEntry',
    # Exception classes (lazy loaded)
    'NFSError',
    'NFSLockError',
    'WebDAVError',
    'WebDAVLockError',
    # Interception control
    'enable_storage_intercept',
    'disable_storage_intercept',
    'get_storage_backend',
    # Legacy (backward compatibility)
    'enable_nfs_intercept',
    'disable_nfs_intercept',
]
