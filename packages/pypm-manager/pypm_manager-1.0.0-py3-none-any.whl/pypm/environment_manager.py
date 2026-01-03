"""
Environment Manager - Handles environment-specific package manifests
Uses dictionary-based configuration to specify package versions per environment
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Optional


class EnvironmentManager:
    """Manages environment manifests and package dependencies"""
    
    def __init__(self, environments_path: Optional[str] = None):
        """
        Initialize the environment manager
        
        Args:
            environments_path: Path to store environment configs. Defaults to ~/.pypm_envs
        """
        if environments_path is None:
            self.envs_path = Path.home() / '.pypm_envs'
        else:
            self.envs_path = Path(environments_path)
        
        self.envs_path.mkdir(parents=True, exist_ok=True)
    
    def create_environment(self, env_name: str, description: str = "") -> bool:
        """
        Create a new environment
        
        Args:
            env_name: Name of the environment
            description: Optional description
        
        Returns:
            True if created, False if already exists
        """
        env_file = self.envs_path / f"{env_name}.json"
        
        if env_file.exists():
            print(f"Environment '{env_name}' already exists")
            return False
        
        env_config = {
            'name': env_name,
            'description': description,
            'packages': {},
            'metadata': {
                'created': True
            }
        }
        
        with open(env_file, 'w') as f:
            json.dump(env_config, f, indent=2)
        
        print(f"Created environment '{env_name}'")
        return True
    
    def add_package_to_env(self, env_name: str, package_name: str, version: str) -> bool:
        """
        Add or update a package in an environment
        
        Args:
            env_name: Name of the environment
            package_name: Name of the package
            version: Version string
        
        Returns:
            True if successful, False otherwise
        """
        env_file = self.envs_path / f"{env_name}.json"
        
        if not env_file.exists():
            print(f"Environment '{env_name}' does not exist")
            return False
        
        with open(env_file, 'r') as f:
            env_config = json.load(f)
        
        env_config['packages'][package_name] = version
        
        with open(env_file, 'w') as f:
            json.dump(env_config, f, indent=2)
        
        print(f"Added {package_name}@{version} to environment '{env_name}'")
        return True
    
    def remove_package_from_env(self, env_name: str, package_name: str) -> bool:
        """
        Remove a package from an environment
        
        Args:
            env_name: Name of the environment
            package_name: Name of the package
        
        Returns:
            True if successful, False otherwise
        """
        env_file = self.envs_path / f"{env_name}.json"
        
        if not env_file.exists():
            print(f"Environment '{env_name}' does not exist")
            return False
        
        with open(env_file, 'r') as f:
            env_config = json.load(f)
        
        if package_name not in env_config['packages']:
            print(f"Package '{package_name}' not found in environment '{env_name}'")
            return False
        
        del env_config['packages'][package_name]
        
        with open(env_file, 'w') as f:
            json.dump(env_config, f, indent=2)
        
        print(f"Removed {package_name} from environment '{env_name}'")
        return True
    
    def get_environment_packages(self, env_name: str) -> Optional[Dict[str, str]]:
        """
        Get all packages defined in an environment
        
        Args:
            env_name: Name of the environment
        
        Returns:
            Dictionary mapping package names to versions, or None if env doesn't exist
        """
        env_file = self.envs_path / f"{env_name}.json"
        
        if not env_file.exists():
            return None
        
        with open(env_file, 'r') as f:
            env_config = json.load(f)
        
        return env_config['packages']
    
    def list_environments(self) -> List[Dict]:
        """List all available environments"""
        environments = []
        
        for env_file in self.envs_path.glob('*.json'):
            with open(env_file, 'r') as f:
                env_config = json.load(f)
                environments.append({
                    'name': env_config['name'],
                    'description': env_config.get('description', ''),
                    'package_count': len(env_config['packages'])
                })
        
        return environments
    
    def delete_environment(self, env_name: str) -> bool:
        """
        Delete an environment
        
        Args:
            env_name: Name of the environment
        
        Returns:
            True if deleted, False if not found
        """
        env_file = self.envs_path / f"{env_name}.json"
        
        if not env_file.exists():
            print(f"Environment '{env_name}' does not exist")
            return False
        
        env_file.unlink()
        print(f"Deleted environment '{env_name}'")
        return True
    
    def show_environment(self, env_name: str) -> Optional[Dict]:
        """
        Show detailed information about an environment
        
        Args:
            env_name: Name of the environment
        
        Returns:
            Environment configuration or None if not found
        """
        env_file = self.envs_path / f"{env_name}.json"
        
        if not env_file.exists():
            return None
        
        with open(env_file, 'r') as f:
            return json.load(f)
