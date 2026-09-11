import joblib
import os

artifacts_dir = "backend/ml/artifacts"
for f in sorted(os.listdir(artifacts_dir)):
    if f.endswith(".joblib"):
        path = os.path.join(artifacts_dir, f)
        size = os.path.getsize(path)
        try:
            obj = joblib.load(path)
            print(f"✅ {f} ({size} bytes): Loaded as {type(obj)}")
        except Exception as e:
            print(f"❌ {f} ({size} bytes): ERROR {type(e).__name__}: {e}")
