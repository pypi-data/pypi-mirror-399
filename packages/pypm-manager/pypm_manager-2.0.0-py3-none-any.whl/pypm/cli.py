"""
PyPM CLI - Command-line interface for PyPM package manager
Works like venv/conda but with centralized package storage
"""
import sys
import os
import subprocess
import argparse
from pathlib import Path
from .central_store import CentralPackageStore
from .environment_manager import EnvironmentManager


class PyPMCLI:
    """Command-line interface for PyPM"""
    
    def __init__(self):
        self.store = CentralPackageStore()
        self.env_manager = EnvironmentManager()
    
    def create(self, env_name: str):
        """Create a new PyPM environment"""
        return self.env_manager.create_environment(env_name)
    
    def activate(self, env_name: str):
        """Show activation command for an environment"""
        if not self.env_manager.environment_exists(env_name):
            print(f"✗ Environment '{env_name}' does not exist")
            print(f"\nCreate it with: pypm create {env_name}")
            return False
        
        activation_cmd = self.env_manager.get_activation_command(env_name)
        
        print(f"\n{'='*60}")
        print(f"  PyPM Environment: {env_name}")
        print(f"{'='*60}")
        print(f"\n📋 To activate this environment, run:\n")
        
        if sys.platform == 'win32':
            print(f"   {activation_cmd}")
            print(f"\n   Or simply:")
            print(f"   .\\{activation_cmd}")
        else:
            print(f"   {activation_cmd}")
        
        print(f"\n{'='*60}")
        print(f"💡 After activation:")
        print(f"   • Use 'pip install <package>' to install packages")
        print(f"   • Packages are stored centrally (no duplication!)")
        print(f"   • Use 'deactivate' to exit the environment")
        print(f"{'='*60}\n")
        
        # Try to activate automatically using subprocess
        if sys.platform == 'win32':
            env_path = self.env_manager.get_env_path(env_name)
            activate_script = env_path / 'Scripts' / 'Activate.ps1'
            
            print("🚀 Attempting to activate environment...\n")
            try:
                # Launch new PowerShell window with activation
                subprocess.Popen(
                    ['powershell', '-NoExit', '-ExecutionPolicy', 'Bypass', 
                     '-Command', f'& "{activate_script}"'],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
                print("✓ New PowerShell window opened with activated environment")
            except Exception as e:
                print(f"⚠ Could not auto-activate. Please run the command above manually.")
        
        return True
    
    def deactivate(self):
        """Deactivate current environment"""
        if 'PYPM_ENV' in os.environ:
            env_name = os.environ['PYPM_ENV']
            print(f"Deactivating PyPM environment '{env_name}'...")
            print("\nRun 'deactivate' in your shell to complete deactivation")
        else:
            print("No PyPM environment is currently active")
        return True
    
    def delete(self, env_name: str):
        """Delete an environment"""
        return self.env_manager.delete_environment(env_name)
    
    def list_envs(self):
        """List all environments"""
        envs = self.env_manager.list_environments()
        
        if not envs:
            print("\n📦 No PyPM environments found")
            print("   Create one with: pypm create <env-name>\n")
            return
        
        print(f"\n{'='*70}")
        print(f"  PyPM Environments")
        print(f"{'='*70}")
        
        for env in envs:
            status = "✓" if env['exists'] else "✗"
            print(f"\n  {status} {env['name']}")
            print(f"     Path: {env['path']}")
            if not env['exists']:
                print(f"     Status: Missing (directory not found)")
        
        print(f"\n{'='*70}")
        print(f"Total environments: {len(envs)}")
        print(f"{'='*70}\n")
    
    def env_info(self, env_name: str):
        """Show detailed information about an environment"""
        info = self.env_manager.get_env_info(env_name)
        
        if not info:
            print(f"✗ Environment '{env_name}' does not exist")
            return False
        
        print(f"\n{'='*70}")
        print(f"  Environment: {info['name']}")
        print(f"{'='*70}")
        print(f"\n  Path: {info['path']}")
        print(f"  Python: {info['python']}")
        print(f"  Packages: {info['package_count']} installed\n")
        
        if info['packages']:
            print(f"  Installed Packages:")
            for pkg in info['packages'][:10]:  # Show first 10
                print(f"    • {pkg['name']} ({pkg['version']})")
            
            if len(info['packages']) > 10:
                print(f"    ... and {len(info['packages']) - 10} more")
        
        print(f"\n{'='*70}\n")
        return True
    
    def store_info(self):
        """Show information about the central store"""
        info = self.store.get_store_info()
        
        print(f"\n{'='*70}")
        print(f"  PyPM Central Package Store")
        print(f"{'='*70}")
        print(f"\n  Location: {info['store_path']}")
        print(f"  Packages Directory: {info['packages_dir']}")
        print(f"  Total Packages: {info['total_packages']}")
        print(f"  Total Files: {info['total_files']}")
        print(f"  Storage Used: {info['total_size_mb']} MB")
        
        if info['packages']:
            print(f"\n  Stored Packages:")
            count = 0
            for pkg_name in sorted(info['packages'].keys())[:15]:
                print(f"    • {pkg_name}")
                count += 1
            
            if len(info['packages']) > 15:
                print(f"    ... and {len(info['packages']) - 15} more")
        
        print(f"\n{'='*70}\n")
    
    def install_central(self, package_spec: str):
        """Install a package to the central store"""
        return self.store.install_to_central(package_spec)
    
    def uninstall_central(self, package_name: str):
        """Uninstall a package from the central store"""
        return self.store.uninstall_from_central(package_name)
    
    def help(self):
        """Show help information"""
        help_text = """
╔══════════════════════════════════════════════════════════════╗
║                  PyPM - Python Package Manager                ║
║          Zero-duplication package management for Python       ║
╚══════════════════════════════════════════════════════════════╝

WORKFLOW (like venv + pip):
  1. pypm create myproject        # Create environment
  2. pypm activate myproject       # Activate environment
  3. pip install pandas numpy      # Install packages (stored centrally!)
  4. deactivate                    # Deactivate when done

ENVIRONMENT COMMANDS:
  create <name>         Create a new environment
  activate <name>       Activate an environment (shows activation command)
  deactivate            Deactivate current environment
  delete <name>         Delete an environment
  list                  List all environments
  info <name>           Show environment details

CENTRAL STORE COMMANDS:
  store-info            Show central store information
  store-install <pkg>   Install package to central store
  store-uninstall <pkg> Remove package from central store

EXAMPLES:
  pypm create datascience
  pypm activate datascience
  # In activated environment: pip install pandas scikit-learn
  pypm list
  pypm info datascience
  pypm store-info

FEATURES:
  ✓ Works with standard pip install
  ✓ Zero package duplication across environments
  ✓ Each environment references centrally stored packages
  ✓ Familiar venv-like workflow
  ✓ Cross-platform (Windows, macOS, Linux)

For more information: https://github.com/Avishek8136/pypm
"""
        print(help_text)


def main():
    """Main entry point for PyPM CLI"""
    parser = argparse.ArgumentParser(
        description='PyPM - Python Package Manager with centralized storage',
        add_help=False
    )
    
    parser.add_argument('command', nargs='?', help='Command to execute')
    parser.add_argument('args', nargs='*', help='Command arguments')
    parser.add_argument('-h', '--help', action='store_true', help='Show help')
    
    args = parser.parse_args()
    
    cli = PyPMCLI()
    
    # Handle help
    if args.help or not args.command or args.command in ['help', '--help', '-h']:
        cli.help()
        return
    
    # Route commands
    command = args.command.lower()
    
    try:
        if command == 'create':
            if not args.args:
                print("✗ Usage: pypm create <env-name>")
                sys.exit(1)
            cli.create(args.args[0])
        
        elif command == 'activate':
            if not args.args:
                print("✗ Usage: pypm activate <env-name>")
                sys.exit(1)
            cli.activate(args.args[0])
        
        elif command == 'deactivate':
            cli.deactivate()
        
        elif command == 'delete':
            if not args.args:
                print("✗ Usage: pypm delete <env-name>")
                sys.exit(1)
            cli.delete(args.args[0])
        
        elif command in ['list', 'ls']:
            cli.list_envs()
        
        elif command == 'info':
            if not args.args:
                print("✗ Usage: pypm info <env-name>")
                sys.exit(1)
            cli.env_info(args.args[0])
        
        elif command == 'store-info':
            cli.store_info()
        
        elif command == 'store-install':
            if not args.args:
                print("✗ Usage: pypm store-install <package-spec>")
                sys.exit(1)
            cli.install_central(' '.join(args.args))
        
        elif command == 'store-uninstall':
            if not args.args:
                print("✗ Usage: pypm store-uninstall <package-name>")
                sys.exit(1)
            cli.uninstall_central(args.args[0])
        
        else:
            print(f"✗ Unknown command: {command}")
            print("   Run 'pypm help' for usage information")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
