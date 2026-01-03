# Getting Started with PyPM

Welcome to PyPM - the Python Package Manager that eliminates duplication!

## 🎬 First Time? Start Here!

### 1. Run the Interactive Demo (Recommended)
```bash
python demo.py
```
This will guide you through all features step-by-step.

### 2. Try the Examples
```bash
# Basic usage
python examples/example_basic.py

# Advanced workflow with dummy packages
python examples/example_advanced.py
```

### 3. View the Architecture
```bash
python architecture.py
```

## 📚 Documentation

- **[README.md](README.md)** - Complete overview and features
- **[USAGE.md](USAGE.md)** - Detailed usage guide with workflows
- **[QUICKREF.md](QUICKREF.md)** - Quick command reference
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Project completion summary

## 🎯 What Problem Does This Solve?

**Before PyPM:**
- Multiple environments = Multiple copies of same packages
- Wastes 50-90% of storage space
- Slow environment creation
- Difficult to manage versions

**With PyPM:**
- One central store = Zero duplication
- Each package version stored only once
- Lightning-fast environment creation
- Easy version management with JSON manifests

## 💡 Key Concepts

### 1. Central Store
All packages stored in one place: `~/.pypm_store/`
- No duplication
- Content-addressable (hash-based)
- Single source of truth

### 2. Environment Manifests
Lightweight JSON files in `~/.pypm_envs/`
- Dictionary mapping: package → version
- Typically < 1KB
- Easy to share and version control

### 3. Package Loading
Load only what you need:
- Read manifest
- Locate in central store
- Add to Python path
- Ready to use!

## 🚀 Quick Start (5 Minutes)

### Option A: Run the Demo
```bash
python demo.py
# Press Enter to walk through each step
```

### Option B: Manual Workflow
```bash
# See what's available (from demo)
python pypm.py list
python pypm.py list-envs

# Check an environment
python pypm.py show-env web_app

# Verify it
python pypm.py verify web_app

# View store statistics
python pypm.py info
```

## 📊 See the Benefits

The demo shows:
- ✅ 5 package versions in central store
- ✅ 3 environments created
- ✅ 8 total package references
- ✅ 37.5% storage savings (no duplication)
- ✅ All packages verified and working

## 🎓 Learning Path

1. **Understand the Problem**
   - Read: [README.md](README.md) "Problem Solved" section

2. **See It In Action**
   - Run: `python demo.py`

3. **Learn the Workflow**
   - Run: `python architecture.py`
   - Read: [USAGE.md](USAGE.md)

4. **Try It Yourself**
   - Create your own environment
   - Add some test packages
   - Experiment with versions

5. **Use Programmatically**
   - Check: `examples/example_basic.py`
   - Study: `examples/example_advanced.py`

## 💻 CLI Help

```bash
# See all commands
python pypm.py --help

# Command categories:
# - Package: add, remove, list, info
# - Environment: create-env, delete-env, list-envs, show-env
# - Install: install, uninstall
# - Activation: verify, activate
```

## 🔧 System Requirements

- Python 3.7+
- No external dependencies
- Works on Windows, Linux, macOS

## 📁 What Gets Created?

### On Your System
- `~/.pypm_store/` - Central package repository
- `~/.pypm_envs/` - Environment configurations

### In This Directory
- Python cache files (`__pycache__/`)
- Activation scripts (if you generate them)

## ❓ Common Questions

**Q: How is this different from venv/virtualenv?**
A: Traditional tools duplicate packages. PyPM stores each version once and uses manifests to specify what each environment uses.

**Q: Do I need to install anything?**
A: No! Pure Python, no dependencies. Just run the scripts.

**Q: Can I use real packages?**
A: Yes! Add any Python package directory to the central store.

**Q: What if I have existing environments?**
A: PyPM is standalone. It won't interfere with your existing setups.

**Q: Is this production-ready?**
A: It's a proof-of-concept showing the approach. You can extend it for production use.

## 🎉 Success Indicators

After running the demo, you should see:
- ✅ Packages listed in central store
- ✅ Environments created and configured
- ✅ Verification showing all packages available
- ✅ Storage statistics showing efficiency
- ✅ Clear understanding of how it works

## 🤝 Next Steps

1. **Explore**: Run all examples and demos
2. **Experiment**: Create your own environments
3. **Customize**: Modify for your specific needs
4. **Extend**: Add features like PyPI integration
5. **Share**: Use the JSON manifests across teams

## 📞 Need Help?

1. Check [USAGE.md](USAGE.md) for detailed guides
2. Look at [QUICKREF.md](QUICKREF.md) for command reference
3. Review examples in `examples/` directory
4. Run `python pypm.py --help` for CLI help

---

**Ready to get started? Run:** `python demo.py`

**Questions? Read:** [README.md](README.md)

**Quick reference?** [QUICKREF.md](QUICKREF.md)

---

*PyPM - Making environment management efficient!* 🚀
