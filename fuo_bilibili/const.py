from pathlib import Path

# Define data root directory
FEELUOWN_DIRECTORY = Path.home() / '.FeelUOwn'
PLUGIN_DATA_DIRECTORY = FEELUOWN_DIRECTORY / 'fuo_bilibili'

# Cookiejar file
PLUGIN_API_COOKIEJAR_FILE = PLUGIN_DATA_DIRECTORY / 'bilibili_api.cookie'

# Ensure directories
PLUGIN_DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
