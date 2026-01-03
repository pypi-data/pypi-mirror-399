"""
Advanced Example - Complete Workflow
Demonstrates full package manager workflow with dummy packages
"""

import tempfile
from pathlib import Path

from pypm import CentralPackageStore, EnvironmentManager, PackageLoader


def create_dummy_package(name: str, version: str, base_dir: Path) -> Path:
    """Create a dummy package for demonstration"""
    pkg_dir = base_dir / f"{name}-{version}"
    pkg_dir.mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py
    init_file = pkg_dir / "__init__.py"
    init_file.write_text(f'''"""
{name} package version {version}
Dummy package for PyPM demonstration
"""

__version__ = "{version}"

def get_info():
    return f"{name} v{version}"
''')
    
    # Create a module file
    module_file = pkg_dir / "core.py"
    module_file.write_text(f'''"""Core module for {name}"""

class {name.capitalize()}:
    def __init__(self):
        self.name = "{name}"
        self.version = "{version}"
    
    def info(self):
        return f"{{self.name}} v{{self.version}}"
''')
    
    return pkg_dir


def main():
    print("=== PyPM Advanced Example ===\n")
    
    # Initialize components
    store = CentralPackageStore()
    env_manager = EnvironmentManager()
    loader = PackageLoader(store, env_manager)
    
    # Create temporary directory for dummy packages
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        print("1. Creating dummy packages...")
        pkg1 = create_dummy_package("mathlib", "1.0.0", temp_path)
        pkg2 = create_dummy_package("mathlib", "2.0.0", temp_path)
        pkg3 = create_dummy_package("datatools", "1.5.0", temp_path)
        pkg4 = create_dummy_package("plotlib", "3.0.0", temp_path)
        print("   ✓ Created 4 dummy packages")
        
        print("\n2. Adding packages to central store...")
        store.add_package("mathlib", "1.0.0", str(pkg1))
        store.add_package("mathlib", "2.0.0", str(pkg2))
        store.add_package("datatools", "1.5.0", str(pkg3))
        store.add_package("plotlib", "3.0.0", str(pkg4))
        
        print("\n3. Central Store Status:")
        info = store.get_store_info()
        print(f"   Total Versions: {info['total_versions']}")
        print(f"   Unique Packages: {info['unique_packages']}")
        print(f"   Storage Used: {info['total_size_mb']} MB")
        
        print("\n4. Listing all packages in store:")
        packages = store.list_packages()
        for pkg in packages:
            print(f"   - {pkg['name']} v{pkg['version']} ({pkg['hash']})")
        
        print("\n5. Creating environments...")
        env_manager.create_environment("data_project", "Project using data tools")
        env_manager.create_environment("analysis_project", "Analysis with different versions")
        print("   ✓ Created 2 environments")
        
        print("\n6. Configuring 'data_project' environment...")
        env_manager.add_package_to_env("data_project", "mathlib", "2.0.0")
        env_manager.add_package_to_env("data_project", "datatools", "1.5.0")
        env_manager.add_package_to_env("data_project", "plotlib", "3.0.0")
        
        print("\n7. Configuring 'analysis_project' environment...")
        env_manager.add_package_to_env("analysis_project", "mathlib", "1.0.0")
        env_manager.add_package_to_env("analysis_project", "datatools", "1.5.0")
        
        print("\n8. Environment Comparison:")
        print("\n   data_project:")
        packages = env_manager.get_environment_packages("data_project")
        for name, ver in packages.items():
            print(f"     - {name}: {ver}")
        
        print("\n   analysis_project:")
        packages = env_manager.get_environment_packages("analysis_project")
        for name, ver in packages.items():
            print(f"     - {name}: {ver}")
        
        print("\n9. Verifying environments...")
        for env_name in ["data_project", "analysis_project"]:
            result = loader.verify_environment(env_name)
            print(f"\n   {env_name}: {result['status'].upper()}")
            print(f"     Available: {len(result['available'])}")
            print(f"     Missing: {len(result['missing'])}")
        
        print("\n10. Creating activation script...")
        activation_script = Path("activate_data_project.py")
        loader.create_activation_script("data_project", str(activation_script))
        print(f"   ✓ Created {activation_script}")
        
        print("\n11. Storage Efficiency Analysis:")
        print(f"   Traditional approach (duplicate storage):")
        print(f"     - data_project: 3 packages")
        print(f"     - analysis_project: 2 packages")
        print(f"     - Total: 5 package copies")
        print(f"\n   PyPM approach (centralized storage):")
        print(f"     - Central store: 4 unique package versions")
        print(f"     - Environment manifests: 2 small JSON files")
        print(f"     - Savings: 1 package copy eliminated (20% reduction)")
        
        print("\n✅ Advanced example completed!")
        
        print("\n" + "="*60)
        print("Key Benefits Demonstrated:")
        print("  ✓ No package duplication (mathlib shared across environments)")
        print("  ✓ Multiple versions coexist (mathlib 1.0.0 and 2.0.0)")
        print("  ✓ Lightweight environment configs (JSON manifests)")
        print("  ✓ Easy verification and activation")
        print("="*60)


if __name__ == '__main__':
    main()
