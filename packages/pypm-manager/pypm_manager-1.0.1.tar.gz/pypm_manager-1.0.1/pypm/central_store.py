"""
Central Package Store - Manages all package versions in a single location
Avoids duplication by storing each package version only once
"""
import os
import json
import hashlib
import shutil
from pathlib import Path
from typing import Dict, List, Optional


class CentralPackageStore:
    """Manages centralized storage of all package versions"""
    
    def __init__(self, store_path: Optional[str] = None):
        """
        Initialize the central package store
        
        Args:
            store_path: Path to the central store. Defaults to ~/.pypm_store
        """
        if store_path is None:
            self.store_path = Path.home() / '.pypm_store'
        else:
            self.store_path = Path(store_path)
        
        self.packages_dir = self.store_path / 'packages'
        self.metadata_file = self.store_path / 'metadata.json'
        
        self._initialize_store()
    
    def _initialize_store(self):
        """Create store directory structure if it doesn't exist"""
        self.store_path.mkdir(parents=True, exist_ok=True)
        self.packages_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.metadata_file.exists():
            self._save_metadata({})
    
    def _load_metadata(self) -> Dict:
        """Load package metadata from store"""
        with open(self.metadata_file, 'r') as f:
            return json.load(f)
    
    def _save_metadata(self, metadata: Dict):
        """Save package metadata to store"""
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _get_package_hash(self, package_name: str, version: str) -> str:
        """Generate unique hash for package version"""
        unique_id = f"{package_name}@{version}"
        return hashlib.sha256(unique_id.encode()).hexdigest()[:16]
    
    def add_package(self, package_name: str, version: str, source_path: str) -> str:
        """
        Add a package version to the central store
        
        Args:
            package_name: Name of the package
            version: Version string
            source_path: Path to the package files
        
        Returns:
            Hash identifier of the stored package
        """
        metadata = self._load_metadata()
        
        # Generate unique identifier
        pkg_hash = self._get_package_hash(package_name, version)
        pkg_key = f"{package_name}@{version}"
        
        # Check if already exists
        if pkg_key in metadata:
            print(f"Package {pkg_key} already exists in store")
            return metadata[pkg_key]['hash']
        
        # Create package directory in store
        pkg_store_path = self.packages_dir / pkg_hash
        
        if pkg_store_path.exists():
            shutil.rmtree(pkg_store_path)
        
        # Copy package files to store
        shutil.copytree(source_path, pkg_store_path)
        
        # Update metadata
        metadata[pkg_key] = {
            'name': package_name,
            'version': version,
            'hash': pkg_hash,
            'path': str(pkg_store_path)
        }
        
        self._save_metadata(metadata)
        print(f"Added {pkg_key} to central store with hash {pkg_hash}")
        
        return pkg_hash
    
    def get_package_path(self, package_name: str, version: str) -> Optional[str]:
        """
        Get the path to a specific package version in the store
        
        Args:
            package_name: Name of the package
            version: Version string
        
        Returns:
            Path to the package or None if not found
        """
        metadata = self._load_metadata()
        pkg_key = f"{package_name}@{version}"
        
        if pkg_key in metadata:
            return metadata[pkg_key]['path']
        
        return None
    
    def list_packages(self) -> List[Dict]:
        """List all packages in the store"""
        metadata = self._load_metadata()
        return [
            {
                'name': info['name'],
                'version': info['version'],
                'hash': info['hash']
            }
            for info in metadata.values()
        ]
    
    def remove_package(self, package_name: str, version: str) -> bool:
        """
        Remove a package version from the store
        
        Args:
            package_name: Name of the package
            version: Version string
        
        Returns:
            True if removed, False if not found
        """
        metadata = self._load_metadata()
        pkg_key = f"{package_name}@{version}"
        
        if pkg_key not in metadata:
            return False
        
        # Remove directory
        pkg_path = Path(metadata[pkg_key]['path'])
        if pkg_path.exists():
            shutil.rmtree(pkg_path)
        
        # Remove from metadata
        del metadata[pkg_key]
        self._save_metadata(metadata)
        
        print(f"Removed {pkg_key} from central store")
        return True
    
    def get_store_info(self) -> Dict:
        """Get information about the store"""
        metadata = self._load_metadata()
        
        total_packages = len(metadata)
        unique_packages = len(set(info['name'] for info in metadata.values()))
        
        # Calculate total size
        total_size = 0
        for pkg_info in metadata.values():
            pkg_path = Path(pkg_info['path'])
            if pkg_path.exists():
                for file in pkg_path.rglob('*'):
                    if file.is_file():
                        total_size += file.stat().st_size
        
        return {
            'store_path': str(self.store_path),
            'total_versions': total_packages,
            'unique_packages': unique_packages,
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        }
