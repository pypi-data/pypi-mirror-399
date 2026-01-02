# built in
import sys
import subprocess
import logging
import copy
import argparse
from pathlib import Path
from typing import Union, Callable
from os.path import isdir

# package
from openlatestscreenshot import linux, windows
from openlatestscreenshot.util import handle_new_latest_screenshot

# __version__.py is generated in CI based on pyproject.toml, so we need to gracefully
# ... handle if the version hasn't been set, for covering scenarios like local development.
try:
    from openlatestscreenshot.__version__ import __version__
except Exception:
    __version__ = "UNKNOWN"

# -----------------
# --- constants ---
# -----------------
SUPPORTED_PLATFORMS = ["linux", "win32"]
OPEN_COMMANDS = {"linux": "xdg-open", "win32": "explorer"}
SCREENSHOTS_DIRS = {"linux": "~/Pictures/", "win32": "~/Pictures/Screenshots"}
REPOSITORY_BUG_REPORT_LINK = (
    "https://gitlab.com/DrTexx/open-latest-screenshot/-/issues"
)
IMAGE_FILE_EXTENSIONS = [".png"]
OWN_PACKAGE_NAME = 'openlatestscreenshot'

# ----------------------
# --- initialization ---
# ----------------------

parser = argparse.ArgumentParser(
    prog='open-latest-screenshot',
    description='Open the latest screenshot you took in your default image viewer'
)
parser.add_argument('--version', '-V', action='version', version='%(prog)s ' + __version__)
group = parser.add_mutually_exclusive_group()
group.add_argument('--verbose', '-v', action='count', default=0, help="verbose output (can be used multiple times for even higher verbosity - e.g. `-vv`)")
group.add_argument('--silent', '-s', action='store_true')
parser.add_argument('--override-screenshot-path', '-i', type=Path)
args = parser.parse_args()

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("open-latest-screenshot.log"),
        logging.StreamHandler(stream=sys.stderr)
    ]
)

logger = logging.getLogger(__name__)

if args.verbose >= 1:
    match args.verbose:
        case 1:
            logger.setLevel(logging.INFO)
        case 2:
            logger.setLevel(logging.DEBUG)
        case _:
            raise RuntimeError("Invalid logging level")
if args.silent:
    logger.setLevel(logging.CRITICAL)


# -----------------
# --- functions ---
# -----------------

def _critical_error(err_msg):
    native_notification(
        "open-latest-screenshot",
        err_msg,
        "dialog-error",
        _platform=sys.platform,
    )
    logger.critical(err_msg)


def native_notification(summary, body, icon, _platform):
    """Post an OS-native notification."""
    if _platform == "linux":
        linux.native_notification(logger, summary, body, icon)
    elif _platform == "win32":
        raise NotImplementedError("Windows native notifications aren't supported yet.")
    else:
        raise NotImplementedError("Unsupported platform")


def custom_global_error_handler(vanilla_error_handler):
    def _func(exctype, value, traceback):
        if exctype is not KeyboardInterrupt:
            native_notification(
                "open-latest-screenshot",
                f"Unhandled Exception: {exctype.__name__}: {value}",
                "dialog-error",
                _platform=sys.platform
            )
        vanilla_error_handler(exctype, value, traceback)
    return _func


vanilla_error_handler=copy.copy(sys.excepthook)
sys.excepthook = custom_global_error_handler(vanilla_error_handler)


def _ensure_environment_compatible(_platform):
    # ensure user is using a supported platform
    if _platform not in SUPPORTED_PLATFORMS:
        raise NotImplementedError(
            f"Incompatible platform: {_platform} (supported platforms: {','.join(SUPPORTED_PLATFORMS)})"
        )


def open_image_in_default_application(image_filepath):
    """Open image at specified filepath using the system's default image viewer."""
    # fetch open command based on platform
    open_command = OPEN_COMMANDS[sys.platform]

    # SEC: ensure we don't try opening any files that aren't images
    # FIXME: Double-check that on Linux that an executable file with a .png extension isn't treated as an executable by xdg-open (web search indicates it's safe, but want to test it myself on a Linux machine)
    if image_filepath.suffix not in IMAGE_FILE_EXTENSIONS:
        raise RuntimeError(
            f"Fatal: Tried opening a file that wasn't an image as though it were.\n\nPlease file a bug report at {REPOSITORY_BUG_REPORT_LINK}"
        )

    # attempt to open filepath with default image viewer
    try:
        pipes = subprocess.Popen(
            [open_command, image_filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = pipes.communicate()

        # if the process we called had a non-zero return code
        if pipes.returncode != 0:
            # HACK: Windows is stupid and returns an exit code of 1 whether it worked or not. Can look into an alternative universally available open command that respects exit codes in the future, but for now it's a low priority.
            if sys.platform == "win32" and pipes.returncode == 1:
                logger.warning(
                    "Warning: Opening image with default Windows app had a return code of 1, but explorer is dumb and does that even when nothing went wrong."
                )
            else:
                # convert stderr byte array to string and strip newline
                err_msg = stderr.decode()
                # raise specific exception with stderr and request user to open new issue
                raise RuntimeError(
                    f"Failed to open '{image_filepath}' with {open_command}, error received:\n  {err_msg}\n\nPlease file a bug report at {REPOSITORY_BUG_REPORT_LINK}"
                )

    # if 'FileNotFoundError' error is raised
    except FileNotFoundError as err:
        # if error is due to platform's open command not being available
        if err.errno == 2 and err.filename == open_command:
            # raise specific error re. platform's open command not being available
            raise NotImplementedError(
                f"Incompatible system: {open_command} is used to open files on your platform ({sys.platform}), however it is not available on your system."
            ) from err
        # if error is due to a different file not being found
        else:
            # raise error normally
            raise err


def get_screenshot_capture_date(
    filepath: Path, _platform: str = sys.platform
) -> Union[float, None]:
    """Return date a screenshot was taken as UTC POSIX timestamp."""
    if _platform == "linux":
        return linux.get_screenshot_capture_date(filepath)
    elif _platform == "win32":
        return windows.get_screenshot_capture_date(filepath)
    else:
        raise NotImplementedError("Unsupported platform")


def get_latest_screenshot_filepath(
    screenshots_dirpath,
    _platform=sys.platform,
    on_new_latest: Union[None, Callable[[float, str], None]] = None,
):
    """Get filepath to latest screenshot."""
    latest_utc_timestamp = 0.0
    latest_screenshot_filepath = None

    # for each path in screenshots dir
    for filepath in screenshots_dirpath.iterdir():
        # if the path isn't a filepath, skip it
        if not filepath.is_file():
            continue

        # try to get capture date from file
        utc_timestamp = get_screenshot_capture_date(
            filepath, _platform=_platform
        )

        # if a valid screenshot capture date could be retrieved, skip
        if utc_timestamp is None:
            continue

        # if this utc timestamp is more recent than the previously recorded most recent
        if utc_timestamp > latest_utc_timestamp:
            # record timestamp as the most recent found thus far
            latest_utc_timestamp = utc_timestamp
            # record filepath of most recent screenshot found thus far
            latest_screenshot_filepath = filepath
            if on_new_latest:
                on_new_latest(latest_utc_timestamp, latest_screenshot_filepath)

    return latest_screenshot_filepath


def guess_screenshot_dirpath(_platform: str = sys.platform) -> Path:
    if args.override_screenshot_path:
        return Path(args.override_screenshot_path).expanduser().absolute()
    return Path(SCREENSHOTS_DIRS[_platform]).expanduser().absolute()


def _ensure_dir_accessible(screenshots_dirpath):
    if not isdir(screenshots_dirpath):
        err_msg = (f"Unable to access screenshot directory: '{screenshots_dirpath}'."
            " You may want to explicitly set your screenshot directory by adding the"
            " parameter `--override-screenshot-path` to wherever you're currently"
            " calling the open-latest-screenshot command from.")
        _critical_error(err_msg)
        raise FileNotFoundError(err_msg)


def open_latest_screenshot():
    """Open the most recently taken screenshot with the system's default image viewer."""
    _ensure_environment_compatible(sys.platform)

    screenshots_dirpath = guess_screenshot_dirpath()

    _ensure_dir_accessible(screenshots_dirpath)
    
    latest_screenshot_filepath = get_latest_screenshot_filepath(
        screenshots_dirpath,
        on_new_latest=handle_new_latest_screenshot(logger),
    )
    if latest_screenshot_filepath is None:
        _warn_msg=f"Failed to find any screenshots in screenshots directory: '{screenshots_dirpath}'. You may want to explicitly set your screenshot directory by adding the `--override-screenshot-path </PATH/TO/YOUR/SCREENSHOTS>` option to wherever you call the open-latest-screenshot command."
        native_notification(
            "open-latest-screenshot",
            f"Warning: {_warn_msg}",
            "dialog-warning",
            _platform=sys.platform
        )
        logger.warning(_warn_msg)
        exit(1)

    logger.info(f"{latest_screenshot_filepath} is the most recent of all screenshots searched.")

    open_image_in_default_application(latest_screenshot_filepath)
