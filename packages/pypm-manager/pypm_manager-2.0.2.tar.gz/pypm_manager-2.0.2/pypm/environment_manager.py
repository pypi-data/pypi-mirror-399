"""
Environment Manager - Creates and manages isolated Python environments
Each environment links to packages in the central store (zero duplication)
"""
import os
import sys
import json
import shutil
import subprocess
import venv
from pathlib import Path
from typing import Dict, List, Optional


class EnvironmentManager:
    """Manages PyPM environments that link to central package store"""
    
    def __init__(self, envs_path: Optional[str] = None):
        """
        Initialize the environment manager
        
        Args:
            envs_path: Path to store environments. Defaults to ~/.pypm_envs
        """
        if envs_path is None:
            self.envs_path = Path.home() / '.pypm_envs'
        else:
            self.envs_path = Path(envs_path)
        
        self.metadata_file = self.envs_path / 'environments.json'
        self._initialize()
    
    def _initialize(self):
        """Create environments directory if it doesn't exist"""
        self.envs_path.mkdir(parents=True, exist_ok=True)
        
        if not self.metadata_file.exists():
            self._save_metadata({'environments': {}, 'version': '2.0.0'})
    
    def _load_metadata(self) -> Dict:
        """Load environment metadata"""
        try:
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {'environments': {}, 'version': '2.0.0'}
    
    def _save_metadata(self, metadata: Dict):
        """Save environment metadata"""
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def get_env_path(self, env_name: str) -> Path:
        """Get the path for an environment"""
        return self.envs_path / env_name
    
    def create_environment(self, env_name: str, python_exe: str = None) -> bool:
        """
        Create a new PyPM environment
        
        Args:
            env_name: Name of the environment
            python_exe: Python executable to use (default: current Python)
            
        Returns:
            True if creation successful
        """
        if self.environment_exists(env_name):
            print(f"✗ Environment '{env_name}' already exists")
            return False
        
        env_path = self.get_env_path(env_name)
        
        try:
            print(f"Creating environment '{env_name}'...")
            
            # Create base venv structure
            if python_exe is None:
                python_exe = sys.executable
            
            # Create virtual environment
            venv.create(env_path, with_pip=True, clear=False)
            
            # Create custom activation scripts
            self._create_activation_scripts(env_name, env_path)
            
            # Update metadata
            metadata = self._load_metadata()
            metadata['environments'][env_name] = {
                'path': str(env_path),
                'python': python_exe,
                'created': str(Path(env_path).stat().st_ctime),
                'packages': {}
            }
            self._save_metadata(metadata)
            
            print(f"✓ Environment '{env_name}' created successfully")
            print(f"  Location: {env_path}")
            print(f"\nActivate with: pypm activate {env_name}")
            
            return True
            
        except Exception as e:
            print(f"✗ Failed to create environment: {e}")
            if env_path.exists():
                shutil.rmtree(env_path)
            return False
    
    def _create_activation_scripts(self, env_name: str, env_path: Path):
        """Create custom activation scripts that integrate with central store"""
        
        # Get central store path
        central_store = Path.home() / '.pypm_central' / 'site-packages'
        
        # PowerShell activation script
        activate_ps1 = env_path / 'Scripts' / 'Activate.ps1'
        if activate_ps1.exists():
            # Read original
            with open(activate_ps1, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Add PyPM customizations BEFORE signature block
            pypm_additions = f'''
# PyPM Customizations
$env:PYPM_ENV = "{env_name}"
$env:PYPM_CENTRAL_STORE = "{central_store}"
$env:PYTHONPATH = "{central_store}" + [IO.Path]::PathSeparator + $env:PYTHONPATH

Write-Host "PyPM environment '{env_name}' activated" -ForegroundColor Green
Write-Host "Central store: {central_store}" -ForegroundColor Cyan
Write-Host "Use 'pip install <package>' to install packages" -ForegroundColor Yellow
Write-Host "Use 'deactivate' to exit" -ForegroundColor Yellow
'''
            
            # Find signature block (starts with "# SIG # Begin signature block")
            sig_marker = "# SIG # Begin signature block"
            if sig_marker in original_content:
                # Insert before signature
                parts = original_content.split(sig_marker)
                modified_content = parts[0] + pypm_additions + '\n' + sig_marker + parts[1]
            else:
                # No signature, append at end
                modified_content = original_content + '\n' + pypm_additions
            
            with open(activate_ps1, 'w', encoding='utf-8') as f:
                f.write(modified_content)
        
        # CMD/Batch activation script
        activate_bat = env_path / 'Scripts' / 'activate.bat'
        if activate_bat.exists():
            with open(activate_bat, 'r') as f:
                original_content = f.read()
            
            pypm_additions = f'''
@echo off
set PYPM_ENV={env_name}
set PYPM_CENTRAL_STORE={central_store}
set PYTHONPATH={central_store};%PYTHONPATH%
echo PyPM environment '{env_name}' activated
echo Use 'pip install <package>' to install packages
'''
            
            with open(activate_bat, 'w') as f:
                f.write(original_content + '\n' + pypm_additions)
        
        # Create deactivate.ps1
        deactivate_ps1 = env_path / 'Scripts' / 'deactivate.ps1'
        with open(deactivate_ps1, 'w') as f:
            f.write('''# PyPM Deactivation Script
if (Test-Path Function:deactivate) {
    deactivate
}
Remove-Item Env:PYPM_ENV -ErrorAction SilentlyContinue
Remove-Item Env:PYPM_CENTRAL_STORE -ErrorAction SilentlyContinue
Write-Host "PyPM environment deactivated" -ForegroundColor Yellow
''')
    
    def delete_environment(self, env_name: str) -> bool:
        """
        Delete an environment
        
        Args:
            env_name: Name of the environment to delete
            
        Returns:
            True if deletion successful
        """
        if not self.environment_exists(env_name):
            print(f"✗ Environment '{env_name}' does not exist")
            return False
        
        env_path = self.get_env_path(env_name)
        
        try:
            # Remove directory
            shutil.rmtree(env_path)
            
            # Update metadata
            metadata = self._load_metadata()
            if env_name in metadata['environments']:
                del metadata['environments'][env_name]
            self._save_metadata(metadata)
            
            print(f"✓ Environment '{env_name}' deleted")
            return True
            
        except Exception as e:
            print(f"✗ Failed to delete environment: {e}")
            return False
    
    def environment_exists(self, env_name: str) -> bool:
        """Check if an environment exists"""
        return self.get_env_path(env_name).exists()
    
    def list_environments(self) -> List[Dict]:
        """List all environments"""
        metadata = self._load_metadata()
        envs = []
        
        for name, info in metadata.get('environments', {}).items():
            env_path = Path(info['path'])
            if env_path.exists():
                envs.append({
                    'name': name,
                    'path': str(env_path),
                    'python': info.get('python', 'unknown'),
                    'exists': True
                })
            else:
                envs.append({
                    'name': name,
                    'path': str(env_path),
                    'python': info.get('python', 'unknown'),
                    'exists': False
                })
        
        return envs
    
    def get_env_info(self, env_name: str) -> Optional[Dict]:
        """Get detailed information about an environment"""
        if not self.environment_exists(env_name):
            return None
        
        metadata = self._load_metadata()
        env_info = metadata['environments'].get(env_name, {})
        env_path = self.get_env_path(env_name)
        
        # Get Python executable
        if sys.platform == 'win32':
            python_exe = env_path / 'Scripts' / 'python.exe'
        else:
            python_exe = env_path / 'bin' / 'python'
        
        # Get installed packages
        packages = []
        if python_exe.exists():
            try:
                result = subprocess.run(
                    [str(python_exe), '-m', 'pip', 'list', '--format=json'],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    packages = json.loads(result.stdout)
            except Exception:
                pass
        
        return {
            'name': env_name,
            'path': str(env_path),
            'python': str(python_exe),
            'packages': packages,
            'package_count': len(packages)
        }
    
    def get_activation_command(self, env_name: str) -> str:
        """Get the command to activate an environment"""
        if not self.environment_exists(env_name):
            return f"Environment '{env_name}' does not exist"
        
        env_path = self.get_env_path(env_name)
        
        if sys.platform == 'win32':
            # Windows
            return f"{env_path}\\Scripts\\Activate.ps1"
        else:
            # Unix-like
            return f"source {env_path}/bin/activate"
