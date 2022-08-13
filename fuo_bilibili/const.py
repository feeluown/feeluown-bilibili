from pathlib import Path

# Define data root directory
from time import time

FEELUOWN_DIRECTORY = Path.home() / '.FeelUOwn'
PLUGIN_DATA_DIRECTORY = FEELUOWN_DIRECTORY / 'fuo_bilibili'
DANMAKU_DIRECTORY = PLUGIN_DATA_DIRECTORY / 'subtitles'

# Cookiejar file
PLUGIN_API_COOKIEJAR_FILE = PLUGIN_DATA_DIRECTORY / 'bilibili_api.cookie'

# Ensure directories
PLUGIN_DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
DANMAKU_DIRECTORY.mkdir(parents=True, exist_ok=True)

# Clear old files
for f in DANMAKU_DIRECTORY.glob('*.ass'):
    if time() - f.stat().st_mtime > 7 * 24 * 60 * 60:
        f.unlink(missing_ok=True)

for f in DANMAKU_DIRECTORY.glob('*.xml'):
    if time() - f.stat().st_mtime > 7 * 24 * 60 * 60:
        f.unlink(missing_ok=True)
