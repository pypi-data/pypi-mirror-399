"""
PyPM - Python Package Manager CLI
Command-line interface for managing packages and environments
"""
import argparse
import sys
from pathlib import Path
from .central_store import CentralPackageStore
from .environment_manager import EnvironmentManager
from .package_loader import PackageLoader


class PyPMCLI:
    """Command-line interface for PyPM"""
    
    def __init__(self):
        self.store = CentralPackageStore()
        self.env_manager = EnvironmentManager()
        self.loader = PackageLoader(self.store, self.env_manager)
    
    def cmd_add_package(self, args):
        """Add a package to the central store"""
        self.store.add_package(args.name, args.version, args.path)
    
    def cmd_remove_package(self, args):
        """Remove a package from the central store"""
        self.store.remove_package(args.name, args.version)
    
    def cmd_list_packages(self, args):
        """List all packages in the store"""
        packages = self.store.list_packages()
        
        if not packages:
            print("No packages in store")
            return
        
        print(f"\n{'Package':<30} {'Version':<15} {'Hash':<20}")
        print("-" * 65)
        
        for pkg in sorted(packages, key=lambda x: (x['name'], x['version'])):
            print(f"{pkg['name']:<30} {pkg['version']:<15} {pkg['hash']:<20}")
        
        print(f"\nTotal: {len(packages)} package versions")
    
    def cmd_store_info(self, args):
        """Show information about the central store"""
        info = self.store.get_store_info()
        
        print("\n=== Central Store Information ===")
        print(f"Store Path: {info['store_path']}")
        print(f"Total Package Versions: {info['total_versions']}")
        print(f"Unique Packages: {info['unique_packages']}")
        print(f"Total Size: {info['total_size_mb']} MB")
    
    def cmd_create_env(self, args):
        """Create a new environment"""
        self.env_manager.create_environment(args.name, args.description or "")
    
    def cmd_delete_env(self, args):
        """Delete an environment"""
        self.env_manager.delete_environment(args.name)
    
    def cmd_list_envs(self, args):
        """List all environments"""
        envs = self.env_manager.list_environments()
        
        if not envs:
            print("No environments found")
            return
        
        print(f"\n{'Environment':<25} {'Packages':<12} {'Description':<40}")
        print("-" * 77)
        
        for env in sorted(envs, key=lambda x: x['name']):
            desc = env['description'][:37] + "..." if len(env['description']) > 40 else env['description']
            print(f"{env['name']:<25} {env['package_count']:<12} {desc:<40}")
        
        print(f"\nTotal: {len(envs)} environments")
    
    def cmd_show_env(self, args):
        """Show detailed environment information"""
        env_config = self.env_manager.show_environment(args.name)
        
        if env_config is None:
            print(f"Environment '{args.name}' not found")
            return
        
        print(f"\n=== Environment: {env_config['name']} ===")
        print(f"Description: {env_config.get('description', 'N/A')}")
        print(f"\nPackages ({len(env_config['packages'])}):")
        
        if env_config['packages']:
            for pkg_name, version in sorted(env_config['packages'].items()):
                print(f"  - {pkg_name}: {version}")
        else:
            print("  No packages defined")
    
    def cmd_add_to_env(self, args):
        """Add a package to an environment"""
        self.env_manager.add_package_to_env(args.env, args.package, args.version)
    
    def cmd_remove_from_env(self, args):
        """Remove a package from an environment"""
        self.env_manager.remove_package_from_env(args.env, args.package)
    
    def cmd_verify_env(self, args):
        """Verify environment packages are available"""
        result = self.loader.verify_environment(args.name)
        
        if 'error' in result:
            print(f"Error: {result['error']}")
            return
        
        print(f"\n=== Verification: {result['environment']} ===")
        print(f"Total Packages: {result['total_packages']}")
        print(f"Status: {result['status'].upper()}")
        
        if result['available']:
            print(f"\nAvailable ({len(result['available'])}):")
            for pkg in result['available']:
                print(f"  ✓ {pkg}")
        
        if result['missing']:
            print(f"\nMissing ({len(result['missing'])}):")
            for pkg in result['missing']:
                print(f"  ✗ {pkg}")
    
    def cmd_activate(self, args):
        """Create activation script for an environment"""
        output = args.output or f"activate_{args.name}.py"
        self.loader.create_activation_script(args.name, output)
    
    def run(self):
        """Run the CLI"""
        parser = argparse.ArgumentParser(
            description='PyPM - Python Package Manager with centralized storage',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Package commands
        pkg_add = subparsers.add_parser('add', help='Add package to central store')
        pkg_add.add_argument('name', help='Package name')
        pkg_add.add_argument('version', help='Package version')
        pkg_add.add_argument('path', help='Path to package files')
        
        pkg_remove = subparsers.add_parser('remove', help='Remove package from store')
        pkg_remove.add_argument('name', help='Package name')
        pkg_remove.add_argument('version', help='Package version')
        
        subparsers.add_parser('list', help='List all packages in store')
        subparsers.add_parser('info', help='Show store information')
        
        # Environment commands
        env_create = subparsers.add_parser('create-env', help='Create new environment')
        env_create.add_argument('name', help='Environment name')
        env_create.add_argument('-d', '--description', help='Environment description')
        
        env_delete = subparsers.add_parser('delete-env', help='Delete environment')
        env_delete.add_argument('name', help='Environment name')
        
        subparsers.add_parser('list-envs', help='List all environments')
        
        env_show = subparsers.add_parser('show-env', help='Show environment details')
        env_show.add_argument('name', help='Environment name')
        
        env_add_pkg = subparsers.add_parser('install', help='Add package to environment')
        env_add_pkg.add_argument('env', help='Environment name')
        env_add_pkg.add_argument('package', help='Package name')
        env_add_pkg.add_argument('version', help='Package version')
        
        env_remove_pkg = subparsers.add_parser('uninstall', help='Remove package from environment')
        env_remove_pkg.add_argument('env', help='Environment name')
        env_remove_pkg.add_argument('package', help='Package name')
        
        env_verify = subparsers.add_parser('verify', help='Verify environment packages')
        env_verify.add_argument('name', help='Environment name')
        
        env_activate = subparsers.add_parser('activate', help='Create activation script')
        env_activate.add_argument('name', help='Environment name')
        env_activate.add_argument('-o', '--output', help='Output script path')
        
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            return
        
        # Execute command
        command_map = {
            'add': self.cmd_add_package,
            'remove': self.cmd_remove_package,
            'list': self.cmd_list_packages,
            'info': self.cmd_store_info,
            'create-env': self.cmd_create_env,
            'delete-env': self.cmd_delete_env,
            'list-envs': self.cmd_list_envs,
            'show-env': self.cmd_show_env,
            'install': self.cmd_add_to_env,
            'uninstall': self.cmd_remove_from_env,
            'verify': self.cmd_verify_env,
            'activate': self.cmd_activate,
        }
        
        handler = command_map.get(args.command)
        if handler:
            handler(args)
        else:
            parser.print_help()


def main():
    """Main entry point"""
    cli = PyPMCLI()
    cli.run()


if __name__ == '__main__':
    main()
