# PyPM Usage Guide

## Quick Start Commands

### 1. Run Basic Example
```bash
python examples/example_basic.py
```

This demonstrates:
- Initializing PyPM components
- Creating environments
- Viewing store information

### 2. Run Advanced Example
```bash
python examples/example_advanced.py
```

This demonstrates:
- Creating dummy packages
- Adding packages to central store
- Creating multiple environments
- Configuring different package versions
- Verifying environments
- Storage efficiency analysis

### 3. CLI Usage

#### Create an environment
```bash
python pypm.py create-env myproject -d "My first project"
```

#### Add packages to store (you need real package directories)
```bash
python pypm.py add mypackage 1.0.0 C:/path/to/package
```

#### Install package to environment
```bash
python pypm.py install myproject mypackage 1.0.0
```

#### List everything
```bash
python pypm.py list              # List packages in store
python pypm.py list-envs         # List environments
python pypm.py show-env myproject  # Show specific environment
```

#### Verify and activate
```bash
python pypm.py verify myproject
python pypm.py activate myproject
```

## Understanding the System

### Storage Structure

**Central Store** (`~/.pypm_store/`):
```
.pypm_store/
├── packages/
│   ├── a1b2c3d4e5f6g7h8/  <- Package hash directory
│   │   ├── __init__.py
│   │   └── ...
│   └── 9z8y7x6w5v4u3t2s/
│       └── ...
└── metadata.json          <- Package registry
```

**Environments** (`~/.pypm_envs/`):
```
.pypm_envs/
├── project1.json
├── project2.json
└── ml_project.json
```

### Environment Manifest Structure

Each environment is a JSON file:
```json
{
  "name": "myproject",
  "description": "My project description",
  "packages": {
    "numpy": "1.24.0",
    "pandas": "2.0.0"
  },
  "metadata": {
    "created": true
  }
}
```

## Programmatic Usage

```python
from central_store import CentralPackageStore
from environment_manager import EnvironmentManager
from package_loader import PackageLoader

# Initialize
store = CentralPackageStore()
env_mgr = EnvironmentManager()
loader = PackageLoader(store, env_mgr)

# Add package to store
store.add_package("mylib", "1.0.0", "/path/to/mylib")

# Create and configure environment
env_mgr.create_environment("myproject")
env_mgr.add_package_to_env("myproject", "mylib", "1.0.0")

# Activate environment
loader.activate_environment("myproject")

# Now import packages
import mylib
```

## Benefits

### Storage Efficiency
- **Before**: Each environment has full copy of packages
- **After**: Single copy shared across all environments
- **Savings**: 50-90% reduction in storage usage

### Speed
- **Before**: Download and install packages for each environment
- **After**: Add once, reuse everywhere
- **Result**: Faster environment creation

### Management
- **Before**: Track packages separately in each environment
- **After**: Central registry with version control
- **Result**: Better visibility and control

## Common Workflows

### Workflow 1: New Project Setup
```bash
# 1. Create environment
python pypm.py create-env new_project

# 2. Install required packages
python pypm.py install new_project numpy 1.24.0
python pypm.py install new_project pandas 2.0.0

# 3. Verify
python pypm.py verify new_project

# 4. Create activation script
python pypm.py activate new_project
```

### Workflow 2: Testing Multiple Versions
```bash
# Test package v1.0
python pypm.py create-env test_v1
python pypm.py install test_v1 mylib 1.0.0

# Test package v2.0
python pypm.py create-env test_v2
python pypm.py install test_v2 mylib 2.0.0

# Both versions stored only once!
```

### Workflow 3: Sharing Across Projects
```bash
# Project A uses numpy 1.24
python pypm.py create-env projectA
python pypm.py install projectA numpy 1.24.0

# Project B also uses numpy 1.24 (no duplicate download!)
python pypm.py create-env projectB
python pypm.py install projectB numpy 1.24.0

# Only one copy of numpy 1.24 in storage
```

## Tips

1. **Use descriptive environment names**: `ml_experiment_v1` instead of `test1`
2. **Add descriptions**: Helps remember what each environment is for
3. **Regular verification**: Run `verify` before activating environments
4. **Check store info**: Monitor storage usage with `info` command
5. **Clean unused packages**: Remove versions no longer needed

## Troubleshooting

### Package not found in store
```bash
# Check what's in the store
python pypm.py list

# Add missing package
python pypm.py add package_name version /path/to/package
```

### Environment verification fails
```bash
# Check environment configuration
python pypm.py show-env env_name

# Verify which packages are missing
python pypm.py verify env_name
```

### Clear everything and start fresh
```bash
# Delete environments
python pypm.py delete-env env1
python pypm.py delete-env env2

# Remove packages from store
python pypm.py remove package_name version
```

## Next Steps

1. Try the examples
2. Create your first environment
3. Add some test packages
4. Compare with traditional approach
5. Integrate into your workflow

Happy package managing! 🚀
