"""
Runtime configuration + data layer.

Resolves, at boot, *where things live* based on the active mode:

    dev    - the pipeline runs from a self-chosen clone folder (the repo itself).
             Data lives inside the clone under `_data/` (git-ignored).
    client - the pipeline was installed for an end user. Data lives in a per-user
             location under the profile so it survives reinstalls and needs no
             admin rights.

Mode is read from the GTOOLS_MODE environment variable, or a `pipeline.cfg`
(JSON) written by the installer at the install root. Defaults to `dev`.

This generalizes the old `setup/returnpath.py` path trick into a real config
object and reserves a stable home for the future asset-manager SQLite database
via get_data_dir() / get_db_path().
"""

import os
import json
import logging

log = logging.getLogger(__name__)

MODE_DEV = "dev"
MODE_CLIENT = "client"
_VALID_MODES = (MODE_DEV, MODE_CLIENT)

# Database filename for the future asset manager.
DB_FILENAME = "assets.db"


def get_install_root():
    """
    Absolute path to the pipeline root (the `gTools` folder).

    config.py lives at <root>/core/config.py, so two dirname() calls get us there.
    """
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read_pipeline_cfg():
    """Read optional <install_root>/pipeline.cfg (JSON). Returns {} if absent/bad."""
    cfg_path = os.path.join(get_install_root(), "pipeline.cfg")
    if os.path.isfile(cfg_path):
        try:
            with open(cfg_path, "r") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except Exception as exc:
            log.warning("Failed to read pipeline.cfg (%s); ignoring.", exc)
    return {}


def get_mode():
    """
    Resolve the active mode.

    Precedence: GTOOLS_MODE env var -> pipeline.cfg "mode" -> default 'dev'.
    """
    mode = os.environ.get("GTOOLS_MODE") or _read_pipeline_cfg().get("mode") or MODE_DEV
    mode = str(mode).strip().lower()
    if mode not in _VALID_MODES:
        log.warning("Unknown mode '%s'; falling back to '%s'.", mode, MODE_DEV)
        mode = MODE_DEV
    return mode


def _brand_name():
    """Brand short-name, used for the per-user data folder. Robust if brand is unavailable."""
    try:
        import brand
        return brand.get("name", "gTools")
    except Exception:
        return "gTools"


def get_data_dir():
    """
    Directory for pipeline-managed data (asset DB, caches, user state).

    dev    -> <install_root>/_data
    client -> %LOCALAPPDATA%\\<Brand>\\data  (falls back to ~/<Brand>/data)

    An explicit pipeline.cfg "data_dir" overrides both. The directory is created
    if missing.
    """
    override = _read_pipeline_cfg().get("data_dir")
    if override:
        data_dir = os.path.expanduser(os.path.expandvars(override))
    elif get_mode() == MODE_CLIENT:
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        data_dir = os.path.join(base, _brand_name(), "data")
    else:
        data_dir = os.path.join(get_install_root(), "_data")

    if not os.path.isdir(data_dir):
        try:
            os.makedirs(data_dir)
            log.info("Created data dir: %s", data_dir)
        except OSError as exc:
            log.error("Could not create data dir %s (%s)", data_dir, exc)
    return data_dir


def get_db_path():
    """Absolute path to the asset-manager SQLite database (Phase 2 contract)."""
    return os.path.join(get_data_dir(), DB_FILENAME)
