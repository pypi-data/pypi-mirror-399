# PyPM - Python Package Manager

**True version isolation with zero duplication** - Multiple package versions coexist, environments use specific versions!

## 🚀 Quick Start

```bash
# Install PyPM
pip install pypm-manager

# Create environment  
pypm create myproject

# Activate it
pypm activate myproject  # Shows activation command
# Run the activation command shown

# Install packages with version isolation
pypm install pandas numpy scikit-learn

# Deactivate when done
deactivate
```

## ✨ The Problem PyPM Solves

**Problem 1 - Duplication:**
```
project1/venv/ → pandas 1.5.0 (100 MB)
project2/venv/ → pandas 1.5.0 (100 MB)  [DUPLICATE!]
project3/venv/ → pandas 1.5.0 (100 MB)  [DUPLICATE!]
Total: 300 MB wasted
```

**Problem 2 - Version Conflicts:**
```
project1 needs requests 2.28.0
project2 needs requests 2.31.0
❌ Can't have both with venv/conda!
```

**With PyPM v2.1:**
```
~/.pypm_central/packages/
  ├── requests/2.28.0/  [Version 1]
  ├── requests/2.31.0/  [Version 2]
  └── pandas/1.5.0/     [Shared dependency - stored once!]

✅ Both versions coexist
✅ Environments use specific versions
✅ Shared dependencies stored once
Total: Zero duplication + True isolation!
```

## 🎯 How It Works

1. **Create**: `pypm create myenv` - Creates lightweight environment
2. **Activate**: `pypm activate myenv` - Shows activation command
3. **Install**: `pypm install pandas==1.5.0` - Stores in version-specific directory
4. **Isolation**: Each environment's PYTHONPATH points to its specific package versions

## 📦 Installation

```bash
pip install pypm-manager
```

## 🔧 Commands

```bash
# Environment Management
pypm create <name>         # Create environment
pypm activate <name>       # Show activation command
pypm install <package>     # Install with version isolation
deactivate                 # Deactivate current environment
pypm delete <name>         # Delete environment
pypm list                  # List all environments
pypm info <name>           # Show environment details

# Central Store
pypm store-info            # View central store stats
```

## 💡 Complete Example

```bash
# Create data science environment
pypm create datascience
pypm activate datascience
# Run activation command shown (e.g., C:\...\datascience\Scripts\Activate.ps1)

# Install packages with specific versions
pypm install pandas==2.1.0 numpy scikit-learn

# Work on your project...
python my_analysis.py

# Deactivate
deactivate

# Create another project with different pandas version
pypm create ml-project
pypm activate ml-project
# Activate...

pypm install pandas==2.3.0 tensorflow
# ✅ Both pandas 2.1.0 and 2.3.0 coexist!
# ✅ numpy/scikit-learn shared between projects
```

## 🌟 Features

- ✅ **True version isolation** - Multiple package versions coexist
- ✅ **Environment-specific versions** - Each env uses its own package versions
- ✅ **Zero duplication** - Shared dependencies stored once
- ✅ **Familiar workflow** - Similar to venv activation
- ✅ **Cross-platform** - Windows, macOS, Linux
- ✅ **No dependencies** - Pure Python stdlib

## 🆚 vs Other Tools

| | venv | conda | PyPM v2.1 |
|---|---|---|---|
| **Multiple versions** | No | Limited | Yes |
| **Duplication** | Yes | Yes | No |
| **Workflow** | activate + pip | activate + conda | activate + pypm |
| **Version Isolation** | No | Yes | Yes |
| **Storage Efficiency** | Low | Low | High |

## 📁 Storage Locations

- Environments: `~/.pypm_envs/`
- Versioned packages: `~/.pypm_central/packages/{name}/{version}/`
- Environment configs: `{env}/.pypm_requirements.json`

## 🤝 Contributing

https://github.com/Avishek8136/pypm

## 📜 License

MIT License

---

**PyPM v2.1 - True version isolation with zero duplication!** 🎉
