"""Lightweight smoke test for core imports.

Run with:
    env/bin/python test.py
"""

from app import main as assistant_main


def smoke_test():
    assert callable(assistant_main), "app.main should be callable"
    print("Smoke test passed: app.main is importable.")


if __name__ == "__main__":
    smoke_test()
