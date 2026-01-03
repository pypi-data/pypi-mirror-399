import os


def is_binary_file(file_path: str) -> bool:
    """
    Determine if a file should be treated as binary based on its extension or path pattern.

    Args:
        file_path: The path to the file

    Returns:
        True if the file should be treated as binary, False otherwise
    """
    # Binary file extensions
    binary_extensions = {".so", ".dll", ".exe", ".bin", ".pyc", ".pyd"}

    # Check file extension
    _, ext = os.path.splitext(file_path)
    if ext.lower() in binary_extensions:
        return True

    # Check for pyarmor runtime files
    if "pyarmor_runtime" in file_path:
        return True

    return False
