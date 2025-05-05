import logging
import json

from .const import PLUGIN_API_COOKIEDICT_FILE


logger = logging.getLogger(__name__)


def load_user_cookies():
    """
    Load cookies from a file in JSON format.
    """
    if PLUGIN_API_COOKIEDICT_FILE.exists():
        with PLUGIN_API_COOKIEDICT_FILE.open('r', encoding='utf-8') as f:
            try:
                cookie_dict = json.load(f)
            except Exception:
                logger.warning('parse cookies(json) failed')
                return None
        return cookie_dict


def dump_user_cookies(cookies):
    """
    Dump cookies to a file in JSON format.
    """
    with PLUGIN_API_COOKIEDICT_FILE.open('w', encoding='utf-8') as f:
        json.dump(cookies, f, indent=2)
