"""
Codebase scanning utilities for AI-powered project initialization.
"""
import os
from pathlib import Path


def scan_codebase(max_files: int = 10, max_size: int = 50000) -> dict[str, str]:
    """
    Scan current directory for important code files.

    Args:
        max_files: Maximum number of files to include
        max_size: Maximum file size in bytes (default 50KB)

    Returns:
        Dictionary of filename -> content for AI analysis
    """
    code_snippets = {}

    # Priority files to scan (in order)
    important_files = [
        # Python entry points
        'main.py', 'app.py', 'wsgi.py', 'asgi.py', 'manage.py',
        # Configuration files
        'requirements.txt', 'pyproject.toml', 'Pipfile', 'setup.py',
        # Django/Flask specific
        'settings.py', 'config.py',
        # Docker
        'Dockerfile', 'docker-compose.yml',
        # Xenfra config
        'xenfra.yaml', 'xenfra.yml',
    ]

    # Scan for important files in current directory
    for filename in important_files:
        if len(code_snippets) >= max_files:
            break

        if os.path.exists(filename) and os.path.isfile(filename):
            try:
                file_size = os.path.getsize(filename)
                if file_size > max_size:
                    continue

                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read(max_size)
                    code_snippets[filename] = content
            except (IOError, UnicodeDecodeError):
                # Skip files that can't be read
                continue

    # If we haven't found enough files, look for Python files in common locations
    if len(code_snippets) < 3:
        search_patterns = [
            'src/**/*.py',
            'app/**/*.py',
            '*.py',
        ]

        for pattern in search_patterns:
            if len(code_snippets) >= max_files:
                break

            for filepath in Path('.').glob(pattern):
                if len(code_snippets) >= max_files:
                    break

                if filepath.is_file() and filepath.name not in code_snippets:
                    try:
                        file_size = filepath.stat().st_size
                        if file_size > max_size:
                            continue

                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read(max_size)
                            code_snippets[str(filepath)] = content
                    except (IOError, UnicodeDecodeError):
                        continue

    return code_snippets


def has_xenfra_config() -> bool:
    """Check if xenfra.yaml already exists."""
    return os.path.exists('xenfra.yaml') or os.path.exists('xenfra.yml')
