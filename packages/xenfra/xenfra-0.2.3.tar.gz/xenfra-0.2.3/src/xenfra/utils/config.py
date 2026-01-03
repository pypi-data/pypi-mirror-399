"""
Configuration file generation utilities.
"""
import os
import shutil
from datetime import datetime
from pathlib import Path

import yaml
from rich.prompt import Confirm, IntPrompt, Prompt
from xenfra_sdk import CodebaseAnalysisResponse


def read_xenfra_yaml(filename: str = "xenfra.yaml") -> dict:
    """
    Read and parse xenfra.yaml configuration file.

    Args:
        filename: Path to the config file (default: xenfra.yaml)

    Returns:
        Dictionary containing the configuration

    Raises:
        FileNotFoundError: If the config file doesn't exist
    """
    if not Path(filename).exists():
        raise FileNotFoundError(f"Configuration file '{filename}' not found. Run 'xenfra init' first.")

    with open(filename, 'r') as f:
        return yaml.safe_load(f) or {}


def generate_xenfra_yaml(analysis: CodebaseAnalysisResponse, filename: str = "xenfra.yaml") -> str:
    """
    Generate xenfra.yaml from AI codebase analysis.

    Args:
        analysis: CodebaseAnalysisResponse from Intelligence Service
        filename: Output filename (default: xenfra.yaml)

    Returns:
        Path to the generated file
    """
    # Build configuration dictionary
    config = {
        'name': os.path.basename(os.getcwd()),
        'framework': analysis.framework,
        'port': analysis.port,
    }

    # Add database configuration if detected
    if analysis.database and analysis.database != 'none':
        config['database'] = {
            'type': analysis.database,
            'env_var': 'DATABASE_URL'
        }

    # Add cache configuration if detected
    if analysis.cache and analysis.cache != 'none':
        config['cache'] = {
            'type': analysis.cache,
            'env_var': f"{analysis.cache.upper()}_URL"
        }

    # Add worker configuration if detected
    if analysis.workers and len(analysis.workers) > 0:
        config['workers'] = analysis.workers

    # Add environment variables
    if analysis.env_vars and len(analysis.env_vars) > 0:
        config['env_vars'] = analysis.env_vars

    # Add instance size
    config['instance_size'] = analysis.instance_size

    # Add package manager info (for intelligent diagnosis)
    if analysis.package_manager:
        config['package_manager'] = analysis.package_manager
    if analysis.dependency_file:
        config['dependency_file'] = analysis.dependency_file

    # Write to file
    with open(filename, 'w') as f:
        yaml.dump(config, f, sort_keys=False, default_flow_style=False)

    return filename


def create_backup(file_path: str) -> str:
    """
    Create a timestamped backup of a file in .xenfra/backups/ directory.

    Args:
        file_path: Path to the file to backup

    Returns:
        Path to the backup file
    """
    # Create .xenfra/backups directory if it doesn't exist
    backup_dir = Path(".xenfra") / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Generate timestamped backup filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = Path(file_path).name
    backup_path = backup_dir / f"{file_name}.{timestamp}.backup"

    # Copy file to backup location
    shutil.copy2(file_path, backup_path)

    return str(backup_path)


def apply_patch(patch: dict, target_file: str = None, create_backup_file: bool = True):
    """
    Apply a JSON patch to a configuration file with automatic backup.

    Args:
        patch: Patch object with file, operation, path, value
        target_file: Optional override for the file to patch
        create_backup_file: Whether to create a backup before patching (default: True)

    Returns:
        Path to the backup file if created, None otherwise
    """
    file_to_patch = target_file or patch.get('file')

    if not file_to_patch:
        raise ValueError("No target file specified in patch")

    if not os.path.exists(file_to_patch):
        raise FileNotFoundError(f"File '{file_to_patch}' not found")

    # Create backup before modifying
    backup_path = None
    if create_backup_file:
        backup_path = create_backup(file_to_patch)

    # For YAML files
    if file_to_patch.endswith(('.yaml', '.yml')):
        with open(file_to_patch, 'r') as f:
            config_data = yaml.safe_load(f) or {}

        # Apply patch based on operation
        operation = patch.get('operation')
        path = patch.get('path', '').strip('/')
        value = patch.get('value')

        if operation == 'add':
            # For simple paths, add to root
            if path:
                path_parts = path.split('/')
                current = config_data
                for part in path_parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[path_parts[-1]] = value
            else:
                # Add to root level
                if isinstance(value, dict):
                    config_data.update(value)
                else:
                    config_data = value

        elif operation == 'replace':
            if path:
                path_parts = path.split('/')
                current = config_data
                for part in path_parts[:-1]:
                    current = current[part]
                current[path_parts[-1]] = value
            else:
                config_data = value

        # Write back
        with open(file_to_patch, 'w') as f:
            yaml.dump(config_data, f, sort_keys=False, default_flow_style=False)

    # For text files (like requirements.txt)
    elif file_to_patch.endswith('.txt'):
        operation = patch.get('operation')
        value = patch.get('value')

        if operation == 'add':
            # Append to file
            with open(file_to_patch, 'a') as f:
                f.write(f"\n{value}\n")
        elif operation == 'replace':
            # Replace entire file
            with open(file_to_patch, 'w') as f:
                f.write(str(value))
    else:
        raise NotImplementedError(f"Patching not supported for file type: {file_to_patch}")

    return backup_path


def manual_prompt_for_config(filename: str = "xenfra.yaml") -> str:
    """
    Prompt user interactively for configuration details and generate xenfra.yaml.

    Args:
        filename: Output filename (default: xenfra.yaml)

    Returns:
        Path to the generated file
    """
    config = {}

    # Project name (default to directory name)
    default_name = os.path.basename(os.getcwd())
    config['name'] = Prompt.ask("Project name", default=default_name)

    # Framework
    framework = Prompt.ask(
        "Framework",
        choices=["fastapi", "flask", "django", "other"],
        default="fastapi"
    )
    config['framework'] = framework

    # Port
    port = IntPrompt.ask("Application port", default=8000)
    config['port'] = port

    # Database
    use_database = Confirm.ask("Does your app use a database?", default=False)
    if use_database:
        db_type = Prompt.ask(
            "Database type",
            choices=["postgresql", "mysql", "sqlite", "mongodb"],
            default="postgresql"
        )
        config['database'] = {
            'type': db_type,
            'env_var': 'DATABASE_URL'
        }

    # Cache
    use_cache = Confirm.ask("Does your app use caching?", default=False)
    if use_cache:
        cache_type = Prompt.ask(
            "Cache type",
            choices=["redis", "memcached"],
            default="redis"
        )
        config['cache'] = {
            'type': cache_type,
            'env_var': f"{cache_type.upper()}_URL"
        }

    # Instance size
    instance_size = Prompt.ask(
        "Instance size",
        choices=["basic", "standard", "premium"],
        default="basic"
    )
    config['instance_size'] = instance_size

    # Environment variables
    add_env = Confirm.ask("Add environment variables?", default=False)
    if add_env:
        env_vars = []
        while True:
            env_var = Prompt.ask("Environment variable name (blank to finish)", default="")
            if not env_var:
                break
            env_vars.append(env_var)
        if env_vars:
            config['env_vars'] = env_vars

    # Write to file
    with open(filename, 'w') as f:
        yaml.dump(config, f, sort_keys=False, default_flow_style=False)

    return filename
