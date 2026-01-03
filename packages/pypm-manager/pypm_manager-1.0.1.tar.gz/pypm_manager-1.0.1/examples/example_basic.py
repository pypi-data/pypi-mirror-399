"""
Basic Example - PyPM Usage
Demonstrates core functionality of the package manager
"""

from pypm import CentralPackageStore, EnvironmentManager, PackageLoader


def main():
    print("=== PyPM Basic Example ===\n")
    
    # Initialize PyPM components
    print("1. Initializing PyPM components...")
    store = CentralPackageStore()
    env_manager = EnvironmentManager()
    loader = PackageLoader(store, env_manager)
    
    # Show store info
    print("\n2. Central Store Information:")
    info = store.get_store_info()
    print(f"   Store Path: {info['store_path']}")
    print(f"   Total Package Versions: {info['total_versions']}")
    print(f"   Total Size: {info['total_size_mb']} MB")
    
    # Create an environment
    print("\n3. Creating environment 'demo_project'...")
    env_manager.create_environment("demo_project", "Example project for demonstration")
    
    # List environments
    print("\n4. Available Environments:")
    envs = env_manager.list_environments()
    for env in envs:
        print(f"   - {env['name']}: {env['package_count']} packages")
    
    # Show environment details
    print("\n5. Environment Details:")
    env_config = env_manager.show_environment("demo_project")
    if env_config:
        print(f"   Name: {env_config['name']}")
        print(f"   Description: {env_config['description']}")
        print(f"   Packages: {len(env_config['packages'])}")
    
    print("\n✅ Basic example completed!")
    print("\nNext steps:")
    print("  - Add packages to the central store using CLI")
    print("  - Install packages to environments")
    print("  - Activate environments in your scripts")


if __name__ == '__main__':
    main()
