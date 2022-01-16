"""Configure pytest."""
import os

# Hack to prevent bleak from attempting to call bluetoothctl on import
os.environ["CI"] = "true"
