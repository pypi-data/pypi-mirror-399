"""
Package Loader - Loads specific package versions based on environment manifest
Only loads packages specified in the environment dictionary
"""
import sys
import os
from pathlib import Path
from typing import List, Dict, Optional
from .central_store import CentralPackageStore
from .environment_manager import EnvironmentManager


class PackageLoader:
    """Loads packages according to environment specifications"""
    
    def __init__(self, store: CentralPackageStore, env_manager: EnvironmentManager):
        """
        Initialize the package loader
        
        Args:
            store: Central package store instance
            env_manager: Environment manager instance
        """
        self.store = store
        self.env_manager = env_manager
        self.loaded_packages = {}
    
    def load_environment(self, env_name: str) -> Dict[str, str]:
        """
        Load all packages for a specific environment
        
        Args:
            env_name: Name of the environment to load
        
        Returns:
            Dictionary of loaded packages and their paths
        """
        packages = self.env_manager.get_environment_packages(env_name)
        
        if packages is None:
            raise ValueError(f"Environment '{env_name}' not found")
        
        loaded = {}
        missing = []
        
        for package_name, version in packages.items():
            pkg_path = self.store.get_package_path(package_name, version)
            
            if pkg_path is None:
                missing.append(f"{package_name}@{version}")
            else:
                loaded[package_name] = pkg_path
                self.loaded_packages[package_name] = {
                    'version': version,
                    'path': pkg_path
                }
        
        if missing:
            print(f"Warning: Missing packages in store: {', '.join(missing)}")
        
        print(f"Loaded {len(loaded)} packages for environment '{env_name}'")
        return loaded
    
    def activate_environment(self, env_name: str) -> List[str]:
        """
        Activate an environment by adding package paths to sys.path
        
        Args:
            env_name: Name of the environment to activate
        
        Returns:
            List of added paths
        """
        loaded_packages = self.load_environment(env_name)
        
        added_paths = []
        for package_name, pkg_path in loaded_packages.items():
            if pkg_path not in sys.path:
                sys.path.insert(0, pkg_path)
                added_paths.append(pkg_path)
        
        print(f"Activated environment '{env_name}' with {len(added_paths)} package paths")
        return added_paths
    
    def deactivate_environment(self):
        """Remove loaded package paths from sys.path"""
        for package_info in self.loaded_packages.values():
            pkg_path = package_info['path']
            if pkg_path in sys.path:
                sys.path.remove(pkg_path)
        
        count = len(self.loaded_packages)
        self.loaded_packages.clear()
        print(f"Deactivated environment, removed {count} package paths")
    
    def get_loaded_packages(self) -> Dict[str, Dict]:
        """Get information about currently loaded packages"""
        return self.loaded_packages.copy()
    
    def verify_environment(self, env_name: str) -> Dict:
        """
        Verify that all packages for an environment are available
        
        Args:
            env_name: Name of the environment
        
        Returns:
            Dictionary with verification results
        """
        packages = self.env_manager.get_environment_packages(env_name)
        
        if packages is None:
            return {'error': f"Environment '{env_name}' not found"}
        
        available = []
        missing = []
        
        for package_name, version in packages.items():
            pkg_path = self.store.get_package_path(package_name, version)
            
            if pkg_path is None:
                missing.append(f"{package_name}@{version}")
            else:
                available.append(f"{package_name}@{version}")
        
        return {
            'environment': env_name,
            'total_packages': len(packages),
            'available': available,
            'missing': missing,
            'status': 'complete' if not missing else 'incomplete'
        }
    
    def create_activation_script(self, env_name: str, output_path: str):
        """
        Create a Python script to activate the environment
        
        Args:
            env_name: Name of the environment
            output_path: Path to save the activation script
        """
        loaded_packages = self.load_environment(env_name)
        
        script_content = f"""#!/usr/bin/env python3
\"\"\"
Auto-generated activation script for environment: {env_name}
Generated by PyPM - Python Package Manager
\"\"\"
import sys

# Add package paths to Python path
package_paths = [
"""
        
        for pkg_path in loaded_packages.values():
            script_content += f"    r'{pkg_path}',\n"
        
        script_content += """
]

for path in package_paths:
    if path not in sys.path:
        sys.path.insert(0, path)

print(f"Activated environment: """ + env_name + """ with {len(package_paths)} packages")
"""
        
        with open(output_path, 'w') as f:
            f.write(script_content)
        
        print(f"Created activation script at {output_path}")
