"""
Brand configuration - the single source of truth for all user-visible branding.

White-label seam:
    - To rebrand, edit DEFAULTS below, OR
    - Drop a `brand.json` next to this file to override any field WITHOUT editing
      code. The (future) GUI installer writes this file when a customer supplies
      their own brand.

The Python import namespace stays `gTools` on purpose - renaming the package is a
heavier, scripted operation. Everything a *user sees* (menus, window titles, the
.mod name, log tags) is driven from here instead.
"""

import os
import json
import logging

log = logging.getLogger(__name__)

# Default brand. Edit here to change the built-in brand.
# `name` is also used to derive the .mod filename and menu object name, so keep it
# a simple identifier (letters/digits/underscore, no spaces).
DEFAULTS = {
    "name": "gTools",                  # internal short id -> .mod filename, menu object name
    "display_name": "gTools",          # human-facing name
    "menu_label": "gTools",            # Maya menu label
    "window_title_prefix": "gTools",   # prefix for tool window titles
    "logger_tag": "gTools",            # logging.getLogger() name
    "author": "Gaige Hallman",
    "studio": "",
    "version": "1.0.0",
}

_BRAND_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brand.json")


def _load():
    """Merge DEFAULTS with an optional sibling brand.json override."""
    data = dict(DEFAULTS)
    if os.path.isfile(_BRAND_JSON):
        try:
            with open(_BRAND_JSON, "r") as f:
                override = json.load(f)
            if isinstance(override, dict):
                data.update(override)
            else:
                log.warning("brand.json is not a JSON object; ignoring it.")
        except Exception as exc:
            log.warning("Failed to read brand.json (%s); using defaults.", exc)
    return data


# Resolved brand dict. Import this (or use get()) from anywhere in the pipeline.
BRAND = _load()


def get(key, default=None):
    """Return a brand field, falling back to `default`."""
    return BRAND.get(key, default)


def mod_filename():
    """Filename of the Maya module file for this brand, e.g. 'gTools.mod'."""
    return "{0}.mod".format(BRAND["name"])
