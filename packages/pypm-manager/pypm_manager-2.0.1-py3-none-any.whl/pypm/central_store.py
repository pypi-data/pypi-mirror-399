"""
Central Package Store - Manages all pip-installed packages in a centralized location
Works with standard pip installations, avoiding duplication across environments
"""
import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set


class CentralPackageStore:
    """Manages centralized storage of all package versions installed via pip"""
    
    def __init__(self, store_path: Optional[str] = None):
        """
        Initialize the central package store
        
        Args:
            store_path: Path to the central store. Defaults to ~/.pypm_central
        """
        if store_path is None:
            self.store_path = Path.home() / '.pypm_central'
        else:
            self.store_path = Path(store_path)
        
        self.packages_dir = self.store_path / 'site-packages'
        self.metadata_file = self.store_path / 'packages.json'
        
        self._initialize_store()
    
    def _initialize_store(self):
        """Create store directory structure if it doesn't exist"""
        self.store_path.mkdir(parents=True, exist_ok=True)
        self.packages_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.metadata_file.exists():
            self._save_metadata({'packages': {}, 'version': '2.0.0'})
    
    def _load_metadata(self) -> Dict:
        """Load package metadata from store"""
        try:
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {'packages': {}, 'version': '2.0.0'}
    
    def _save_metadata(self, metadata: Dict):
        """Save package metadata to store"""
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def get_package_dir(self, package_name: str, version: str) -> Path:
        """Get the directory for a specific package version"""
        # Normalize package name (pip uses lowercase with underscores)
        normalized = package_name.lower().replace('-', '_')
        return self.packages_dir / f"{normalized}-{version}"
    
    def is_package_installed(self, package_name: str, version: str) -> bool:
        """Check if a package version exists in central store"""
        pkg_dir = self.get_package_dir(package_name, version)
        return pkg_dir.exists()
    
    def get_central_site_packages(self) -> Path:
        """Get the central site-packages directory"""
        return self.packages_dir
    
    def list_all_packages(self) -> Dict[str, List[str]]:
        """List all packages and their versions in the central store"""
        packages = {}
        
        if not self.packages_dir.exists():
            return packages
        
        # Scan site-packages directory
        for item in self.packages_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.') and not item.name.endswith('.dist-info'):
                # Try to extract package name
                if not any(item.name.endswith(ext) for ext in ['.dist-info', '.egg-info']):
                    pkg_name = item.name
                    if pkg_name not in packages:
                        packages[pkg_name] = []
                    packages[pkg_name].append('installed')
        
        return packages
    
    def get_installed_packages_from_pip(self, python_exe: str = None) -> List[Dict[str, str]]:
        """Get list of packages in central store using pip list"""
        if python_exe is None:
            python_exe = sys.executable
            
        try:
            env = os.environ.copy()
            env['PYTHONPATH'] = str(self.packages_dir)
            
            result = subprocess.run(
                [python_exe, '-m', 'pip', 'list', '--format=json'],
                capture_output=True,
                text=True,
                env=env
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            return []
        except Exception:
            return []
    
    def get_store_info(self) -> Dict:
        """Get information about the central store"""
        total_size = 0
        file_count = 0
        
        if self.packages_dir.exists():
            for item in self.packages_dir.rglob('*'):
                if item.is_file():
                    total_size += item.stat().st_size
                    file_count += 1
                    
        packages = self.list_all_packages()
        
        return {
            'store_path': str(self.store_path),
            'packages_dir': str(self.packages_dir),
            'total_packages': len(packages),
            'total_files': file_count,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'packages': packages
        }
    
    def install_to_central(self, package_spec: str, upgrade: bool = False) -> bool:
        """
        Install a package directly to the central store using pip
        
        Args:
            package_spec: Package specification (e.g., 'pandas==1.5.0' or 'numpy')
            upgrade: Whether to upgrade if already installed
            
        Returns:
            True if installation successful
        """
        try:
            cmd = [
                sys.executable, '-m', 'pip', 'install',
                '--target', str(self.packages_dir),
                '--no-warn-script-location'
            ]
            
            if upgrade:
                cmd.append('--upgrade')
            
            cmd.append(package_spec)
            
            print(f"Installing {package_spec} to central store...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✓ Installed {package_spec} to central store")
                return True
            else:
                print(f"✗ Failed to install {package_spec}")
                if result.stderr:
                    print(result.stderr)
                return False
                
        except Exception as e:
            print(f"✗ Error installing {package_spec}: {e}")
            return False
    
    def uninstall_from_central(self, package_name: str) -> bool:
        """
        Uninstall a package from the central store
        
        Args:
            package_name: Name of package to uninstall
            
        Returns:
            True if uninstallation successful
        """
        try:
            # Find and remove package directories
            pkg_pattern = package_name.lower().replace('-', '_')
            removed = False
            
            for item in self.packages_dir.iterdir():
                if (item.is_dir() and 
                    (item.name == pkg_pattern or 
                     item.name.startswith(pkg_pattern + '-') or
                     item.name.startswith(pkg_pattern + '.'))):
                    shutil.rmtree(item)
                    print(f"✓ Removed {item.name}")
                    removed = True
            
            if not removed:
                print(f"✗ Package {package_name} not found in central store")
            
            return removed
            
        except Exception as e:
            print(f"✗ Error uninstalling {package_name}: {e}")
            return False
