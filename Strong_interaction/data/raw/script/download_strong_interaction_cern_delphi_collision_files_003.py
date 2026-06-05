#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import csv
import datetime as dt
import pathlib
import re
import shutil
import subprocess
import sys
from typing import Any, Iterable

RAW_BATCH = "03"
SCRIPT_VERSION = "003"


def utc_now() -> str:
