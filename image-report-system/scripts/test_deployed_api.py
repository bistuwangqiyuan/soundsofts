#!/usr/bin/env python3
"""Test deployed Vercel API. Usage: python scripts/test_deployed_api.py [BASE_URL]"""

import json
import sys

import requests

BASE_URL = (sys.argv[1] if len(sys.argv) > 1 else "").rstrip("/")
if not BASE_URL:
    print("Usage: python scripts/test_deployed_api.py https://your-app.vercel.app")
    sys.exit(1)


def test(name, fn):
    try:
        fn()
        print(f"  ✓ {name}")
    except Exception as e:
        print(f"  ✗ {name}: {e}")
        return False
    return True


ok = True
print("Testing API at", BASE_URL)

# Health
def _health():
    r = requests.get(f"{BASE_URL}/api/health", timeout=10)
    r.raise_for_status()
    assert r.json().get("status") == "healthy"


ok &= test("GET /api/health", _health)

# Analyze
def _analyze():
    r = requests.post(
        f"{BASE_URL}/api/analyze",
        json={"force": 85.0, "defect_area": 100, "total_area": 10000},
        timeout=10,
    )
    r.raise_for_status()
    d = r.json()
    assert "checks" in d and "all_passed" in d


ok &= test("POST /api/analyze", _analyze)

# Fuse
def _fuse():
    r = requests.post(
        f"{BASE_URL}/api/fuse",
        json={"predicted_force": 85.0, "defect_ratio": 0.01, "visual_confidence": 0.9},
        timeout=10,
    )
    r.raise_for_status()
    d = r.json()
    assert "quality" in d and d["quality"] in ("合格", "不合格", "待复核")


ok &= test("POST /api/fuse", _fuse)

# Terminology
def _term():
    r = requests.get(f"{BASE_URL}/api/terminology", timeout=10)
    r.raise_for_status()
    assert "terms" in r.json()


ok &= test("GET /api/terminology", _term)

print("\n" + ("All passed" if ok else "Some failed"))
sys.exit(0 if ok else 1)
