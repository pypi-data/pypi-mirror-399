# PyPM Quick Reference

## Installation
```bash
pip install pypm-manager
```

## Workflow
```bash
1. pypm create myproject          # Create environment
2. pypm activate myproject         # Shows activation command
3. [Run activation command shown]  # Activate environment
4. pypm install pandas numpy       # Install packages
5. python myapp.py                 # Use environment
6. deactivate                      # Deactivate when done
```

## CLI Commands

### Environment Management
```bash
pypm create <name>         # Create new environment
pypm activate <name>       # Show activation command
pypm delete <name>         # Delete environment
pypm list                  # List all environments
pypm info <name>           # Show environment details
```

### Package Installation (in activated environment)
```bash
pypm install <package>                    # Install latest version
pypm install <package>==<version>         # Install specific version
pypm install pkg1 pkg2 pkg3               # Install multiple packages

# Examples
pypm install requests==2.28.0
pypm install pandas==2.1.0 numpy scikit-learn
```

### Central Store
```bash
pypm store-info            # View central store statistics
```

## Typical Workflow Examples

### Data Science Project
```bash
pypm create datascience
pypm activate datascience
# Run: C:\Users\...\datascience\Scripts\Activate.ps1
pypm install pandas numpy matplotlib seaborn jupyter
python analysis.py
deactivate
```

### Web Development
```bash
pypm create webapp
pypm activate webapp
# Activate...
pypm install flask sqlalchemy requests
python app.py
deactivate
```

### Multiple Versions
```bash
# Project 1 with requests 2.28.0
pypm create project1
pypm activate project1
# Activate...
pypm install requests==2.28.0
deactivate

# Project 2 with requests 2.31.0
pypm create project2
pypm activate project2
# Activate...
pypm install requests==2.31.0
# ✅ Both versions coexist!
deactivate
```

## Storage Locations

- **Environments**: `~/.pypm_envs/{env_name}/`
- **Versioned Packages**: `~/.pypm_central/packages/{package}/{version}/`
- **Environment Config**: `{env}/.pypm_requirements.json`

## Key Features

✅ **Version Isolation** - Multiple package versions coexist  
✅ **Zero Duplication** - Shared dependencies stored once  
✅ **Environment-Specific** - Each env uses its own versions  
✅ **Cross-Platform** - Windows, macOS, Linux  

## Version 2.1.0 Highlights

- True version isolation with per-environment PYTHONPATH
- Multiple package versions can coexist (e.g., requests 2.28.0 AND 2.31.0)
- Shared dependencies are deduplicated (certifi, idna stored once)
- Environment-specific package tracking via pypm_requirements.json
