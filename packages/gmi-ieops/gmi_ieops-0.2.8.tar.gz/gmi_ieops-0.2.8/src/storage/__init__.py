"""
Storage Module - User-isolated Distributed File System Access

Use gmifs:// protocol prefix to write to NFS storage:

    from gmi_ieops.storage import enable_nfs_intercept
    enable_nfs_intercept()  # Enable gmifs:// support
    
    # Write to NFS (explicit)
    with open("gmifs://output/image.png", "wb") as f:
        f.write(image_data)
    
    # Write to local (default, no prefix)
    with open("/data/local/file.txt", "w") as f:
        f.write("local data")

Or use FileSystem API directly:
    
    from gmi_ieops.storage import FileSystem
    
    fs = FileSystem(server="nfs.local", port=32049)
    with fs.open("data.txt", "w") as f:
        f.write("Hello NFS")
"""

from .filesystem import (
    # High-level API
    FileSystem,
    # Protocol constant
    GMIFS_PROTOCOL,
    # Interception control
    enable_nfs_intercept,
    disable_nfs_intercept,
    # NFS availability check
    _ensure_nfs_module,
)


def __getattr__(name):
    """Lazy load NFS classes to avoid crash when libnfs is not installed"""
    if name in ('NFSFile', 'FileStat', 'DirEntry', 'NFSError', 'NFSLockError'):
        from .filesystem import _get_nfs_class
        return _get_nfs_class(name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # High-level API
    'FileSystem',
    # Protocol constant
    'GMIFS_PROTOCOL',
    # Data types (lazy loaded)
    'NFSFile',
    'FileStat',
    'DirEntry',
    # Exception classes (lazy loaded)
    'NFSError',
    'NFSLockError',
    # Interception control
    'enable_nfs_intercept',
    'disable_nfs_intercept',
]
