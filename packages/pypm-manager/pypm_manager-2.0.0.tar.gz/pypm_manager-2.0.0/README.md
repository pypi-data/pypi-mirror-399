# PyPM - Python Package Manager

**Zero-duplication package management for Python** - Works like `venv` + `pip` but stores packages centrally!

## 🚀 Quick Start

```bash
# Install PyPM
pip install pypm-manager

# Create environment  
pypm create myproject

# Activate it (opens new shell)
pypm activate myproject

# Use pip normally - packages stored centrally!
pip install pandas numpy scikit-learn

# Deactivate when done
deactivate
```

## ✨ The Problem PyPM Solves

**Before PyPM:**
```
project1/venv/ → pandas 1.5.0 (100 MB)
project2/venv/ → pandas 1.5.0 (100 MB)  [DUPLICATE!]
project3/venv/ → pandas 1.5.0 (100 MB)  [DUPLICATE!]
Total: 300 MB wasted
```

**With PyPM:**
```
~/.pypm_central/ → pandas 1.5.0 (100 MB)  [STORED ONCE!]
All projects reference the same files
Total: 100 MB  (66% savings!)
```

## 🎯 How It Works

1. **Create**: `pypm create myenv` - Creates environment
2. **Activate**: `pypm activate myenv` - Opens activated shell
3. **Install**: `pip install pandas` - Packages go to central store
4. **Use Anywhere**: Activate same environment from any directory!

## 📦 Installation

```bash
pip install pypm-manager
```

## 🔧 Commands

```bash
# Environment Management
pypm create <name>         # Create environment
pypm activate <name>       # Activate (opens new shell)
deactivate                 # Deactivate current environment
pypm delete <name>         # Delete environment
pypm list                  # List all environments
pypm info <name>           # Show environment details

# Central Store
pypm store-info            # View central store stats
pypm store-install <pkg>   # Install to central store
pypm store-uninstall <pkg> # Remove from central store
```

## 💡 Complete Example

```bash
# Create data science environment
pypm create datascience
pypm activate datascience

# In activated shell - use pip normally:
pip install pandas numpy matplotlib seaborn scikit-learn jupyter

# Work on your project...
python my_analysis.py

# Deactivate
deactivate

# Later, from anywhere:
pypm activate datascience  # Same environment!
```

## 🌟 Features

- ✅ **Works like venv** - Same familiar workflow
- ✅ **Use standard `pip install`** - No new commands
- ✅ **Zero package duplication** - 12-90% storage savings
- ✅ **Machine-wide environments** - Activate from anywhere
- ✅ **Cross-platform** - Windows, macOS, Linux
- ✅ **No dependencies** - Pure Python stdlib

## 🆚 vs Other Tools

| | venv | conda | PyPM |
|---|---|---|---|
| **Duplication** | Yes | Yes | No |
| **Workflow** | activate + pip | activate + conda | activate + pip |
| **Learning Curve** | None | Moderate | None |
| **Storage Waste** | High | High | Zero |

## 📁 Storage Locations

- Environments: `~/.pypm_envs/`
- Central packages: `~/.pypm_central/site-packages/`

## 🤝 Contributing

https://github.com/Avishek8136/pypm

## 📜 License

MIT License

---

**PyPM v2.0 - No more duplicate packages!** 🎉
