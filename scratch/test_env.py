import sys

print("Python Executable:", sys.executable)
modules = ["pandas", "numpy", "sklearn", "xgboost", "joblib", "matplotlib", "shap"]
for mod in modules:
    try:
        m = __import__(mod)
        ver = getattr(m, "__version__", "installed")
        print(f"✅ {mod}: {ver}")
    except ImportError as e:
        print(f"❌ {mod}: NOT INSTALLED ({e})")
