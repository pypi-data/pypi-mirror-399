#!/usr/bin/env python3

import sys
import os

# 添加当前包路径到 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from main import main
except ImportError:
    from .main import main

if __name__ == "__main__":
    main()
