# PyPM Quick Reference

## Installation
No installation needed! Pure Python, no dependencies.

## CLI Commands Cheat Sheet

### Package Management
```bash
# Add package to central store
python pypm.py add <name> <version> <path>

# Remove package from store
python pypm.py remove <name> <version>

# List all packages
python pypm.py list

# Show store info
python pypm.py info
```

### Environment Management
```bash
# Create environment
python pypm.py create-env <name> [-d "description"]

# Delete environment
python pypm.py delete-env <name>

# List all environments
python pypm.py list-envs

# Show environment details
python pypm.py show-env <name>
```

### Package Installation
```bash
# Install package to environment
python pypm.py install <env> <package> <version>

# Uninstall package from environment
python pypm.py uninstall <env> <package>
```

### Verification & Activation
```bash
# Verify environment has all packages
python pypm.py verify <name>

# Create activation script
python pypm.py activate <name> [-o script.py]
```

## Python API Quick Reference

```python
# Import components
from central_store import CentralPackageStore
from environment_manager import EnvironmentManager
from package_loader import PackageLoader

# Initialize
store = CentralPackageStore()
env_mgr = EnvironmentManager()
loader = PackageLoader(store, env_mgr)

# Add package to store
store.add_package("mypackage", "1.0.0", "/path/to/package")

# Create environment
env_mgr.create_environment("myenv", "My environment")

# Add package to environment
env_mgr.add_package_to_env("myenv", "mypackage", "1.0.0")

# Activate environment
loader.activate_environment("myenv")

# Verify environment
result = loader.verify_environment("myenv")

# List packages
packages = store.list_packages()

# Get environment packages
env_packages = env_mgr.get_environment_packages("myenv")
```

## Examples

### Complete Workflow
```bash
# 1. Add packages to store
python pypm.py add numpy 1.24.0 C:/packages/numpy
python pypm.py add pandas 2.0.0 C:/packages/pandas

# 2. Create environment
python pypm.py create-env data_project -d "Data analysis"

# 3. Install packages
python pypm.py install data_project numpy 1.24.0
python pypm.py install data_project pandas 2.0.0

# 4. Verify and activate
python pypm.py verify data_project
python pypm.py activate data_project
```

### Multiple Environments with Shared Packages
```bash
# Add packages (stored once)
python pypm.py add scipy 1.11.0 C:/packages/scipy

# Create two projects
python pypm.py create-env project_a
python pypm.py create-env project_b

# Both use scipy (no duplication!)
python pypm.py install project_a scipy 1.11.0
python pypm.py install project_b scipy 1.11.0

# Only one copy in storage
python pypm.py info  # Shows 1 version of scipy
```

## Storage Locations

- **Central Store**: `~/.pypm_store/`
  - `packages/` - Package files
  - `metadata.json` - Package registry

- **Environments**: `~/.pypm_envs/`
  - `<env_name>.json` - Environment manifests

## Common Tasks

### Check what's in the store
```bash
python pypm.py list
python pypm.py info
```

### See all environments
```bash
python pypm.py list-envs
```

### Check environment configuration
```bash
python pypm.py show-env myproject
```

### Verify environment is ready
```bash
python pypm.py verify myproject
```

### Create activation script
```bash
python pypm.py activate myproject -o activate.py
python activate.py  # Activates the environment
```

## Tips

1. **Descriptive names**: Use clear environment names
2. **Add descriptions**: Helps remember purpose
3. **Verify first**: Always verify before activating
4. **Check store**: Monitor storage with `info`
5. **Share configs**: Environment JSON files are portable

## Troubleshooting

### Package not found
```bash
# Check what's in store
python pypm.py list

# Add if missing
python pypm.py add <name> <version> <path>
```

### Environment issues
```bash
# Check configuration
python pypm.py show-env <name>

# Verify packages
python pypm.py verify <name>
```

### Start fresh
```bash
# Delete environment
python pypm.py delete-env <name>

# Remove package
python pypm.py remove <name> <version>

# Recreate
python pypm.py create-env <name>
```

## Run Examples

```bash
# Interactive demo
python demo.py

# Basic example
python examples/example_basic.py

# Advanced example
python examples/example_advanced.py

# Show architecture
python architecture.py
```

## Key Benefits

✅ **No duplication** - Each package version stored once
✅ **Storage efficient** - 12-90% savings
✅ **Version flexible** - Different versions coexist
✅ **Fast setup** - No redundant downloads
✅ **Easy management** - Clear manifests

## File Structure

```
Packagemanager/
├── pypm.py                  # CLI interface
├── central_store.py         # Package storage
├── environment_manager.py   # Environment config
├── package_loader.py        # Package loading
├── demo.py                  # Interactive demo
├── README.md                # Full documentation
├── USAGE.md                 # Usage guide
└── examples/
    ├── example_basic.py
    └── example_advanced.py
```

---

**PyPM - Efficient Python Package Management** 🚀
