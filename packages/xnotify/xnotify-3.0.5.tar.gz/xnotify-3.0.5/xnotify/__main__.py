#!/usr/bin/env python3

# File: xnotify/xnotify/__main__.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-12-30
# Description: 
# License: MIT

"""Entry point for xnotify CLI."""

import sys
from .cli import main

if __name__ == '__main__':
    sys.exit(main())