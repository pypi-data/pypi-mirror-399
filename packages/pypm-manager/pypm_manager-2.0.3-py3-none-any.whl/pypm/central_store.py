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
        self.versioned_packages_dir = self.store_path / 'packages'
        self.temp_install_dir = self.store_path / 'temp_install'
        self.metadata_file = self.store_path / 'packages.json'
        
        self._initialize_store()
    
    def _initialize_store(self):
        """Create store directory structure if it doesn't exist"""
        self.store_path.mkdir(parents=True, exist_ok=True)
        self.packages_dir.mkdir(parents=True, exist_ok=True)
        self.versioned_packages_dir.mkdir(parents=True, exist_ok=True)
        self.temp_install_dir.mkdir(parents=True, exist_ok=True)
        
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
    
    def install_packages(self, env_name: str, package_specs: List[str], env_manager) -> bool:
        """
        Install packages with version isolation
        
        Args:
            env_name: Name of the environment
            package_specs: List of package specifications (e.g., ['requests==2.28.0'])
            env_manager: EnvironmentManager instance
            
        Returns:
            True if installation successful
        """
        try:
            # Clear temp install directory
            if self.temp_install_dir.exists():
                shutil.rmtree(self.temp_install_dir)
            self.temp_install_dir.mkdir(parents=True, exist_ok=True)
            
            # Install to temp directory
            print("\nInstalling packages to temporary location...")
            cmd = [
                sys.executable, '-m', 'pip', 'install',
                '--target', str(self.temp_install_dir),
                '--no-warn-script-location'
            ] + package_specs
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"✗ pip install failed:")
                print(result.stderr)
                return False
            
            print(result.stdout)
            
            # Get list of what was installed
            installed_packages = self._get_installed_packages_from_temp()
            
            if not installed_packages:
                print("✗ No packages detected after installation")
                return False
            
            # Move packages to version-specific directories
            print("\nOrganizing packages into version-specific storage...")
            requirements = env_manager.load_env_requirements(env_name)
            
            for pkg_name, pkg_version in installed_packages.items():
                # Create version-specific directory
                version_dir = self.versioned_packages_dir / pkg_name / pkg_version
                version_dir.mkdir(parents=True, exist_ok=True)
                
                # Move package files from temp to version-specific directory
                self._move_package_to_versioned_storage(pkg_name, pkg_version, version_dir)
                
                # Update environment requirements
                requirements.setdefault('packages', {})[pkg_name] = pkg_version
                print(f"  ✓ {pkg_name} {pkg_version} → {version_dir}")
            
            # Save updated requirements
            env_manager.save_env_requirements(env_name, requirements)
            
            # Clean up temp directory
            shutil.rmtree(self.temp_install_dir)
            
            print(f"\n✓ Successfully installed {len(installed_packages)} package(s)")
            print(f"  Environment '{env_name}' now has access to these packages")
            print(f"\n  NOTE: Reactivate the environment to update PYTHONPATH:")
            print(f"    deactivate && pypm activate {env_name}")
            
            return True
            
        except Exception as e:
            print(f"✗ Error during installation: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _get_installed_packages_from_temp(self) -> Dict[str, str]:
        """Get packages and versions from temp install directory"""
        packages = {}
        
        # Scan for .dist-info directories
        for item in self.temp_install_dir.iterdir():
            if item.is_dir() and item.name.endswith('.dist-info'):
                # Parse package name and version from directory name
                # Format: package_name-version.dist-info
                dist_info_name = item.name[:-len('.dist-info')]
                
                # Find last dash to split name and version
                parts = dist_info_name.rsplit('-', 1)
                if len(parts) == 2:
                    pkg_name, pkg_version = parts
                    # Normalize package name
                    pkg_name = pkg_name.lower().replace('_', '-')
                    packages[pkg_name] = pkg_version
        
        return packages
    
    def _move_package_to_versioned_storage(self, pkg_name: str, pkg_version: str, version_dir: Path):
        """Move package files from temp to version-specific directory"""
        # Normalize package name for directory matching
        pkg_normalized = pkg_name.replace('-', '_')
        
        # Move all related files (package dir, .dist-info, etc.)
        for item in list(self.temp_install_dir.iterdir()):
            item_name_lower = item.name.lower()
            pkg_name_lower = pkg_name.lower()
            
            # Check if this item belongs to the package
            should_move = (
                item_name_lower == pkg_name_lower or
                item_name_lower == pkg_normalized.lower() or
                item_name_lower.startswith(pkg_name_lower + '-') or
                item_name_lower.startswith(pkg_normalized.lower() + '-') or
                (item_name_lower.replace('_', '-').startswith(pkg_name_lower + '-') and 
                 item.is_dir() and item_name_lower.endswith('.dist-info'))
            )
            
            if should_move:
                dest = version_dir / item.name
                if dest.exists():
                    if dest.is_dir():
                        shutil.rmtree(dest)
                    else:
                        dest.unlink()
                shutil.move(str(item), str(dest))
