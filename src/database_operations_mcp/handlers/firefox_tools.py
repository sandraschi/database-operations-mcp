import os
import sqlite3
import json
import shutil
import tempfile
import psutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import fastmcp as mcp
from fastmcp import tool

# Firefox profile locations for Windows
FIREFOX_PROFILES = {
    'windows': {
        'base': Path(os.path.expanduser('~')) / 'AppData' / 'Roaming' / 'Mozilla' / 'Firefox' / 'Profiles',
        'profiles_ini': Path(os.path.expanduser('~')) / 'AppData' / 'Roaming' / 'Mozilla' / 'Firefox' / 'profiles.ini'
    },
    'linux': {
        'base': Path.home() / '.mozilla' / 'firefox',
        'profiles_ini': Path.home() / '.mozilla' / 'firefox' / 'profiles.ini'
    },
    'darwin': {
        'base': Path.home() / 'Library' / 'Application Support' / 'Firefox' / 'Profiles',
        'profiles_ini': Path.home() / 'Library' / 'Application Support' / 'Firefox' / 'profiles.ini'
    }
}

PLACES_DB = 'places.sqlite'
