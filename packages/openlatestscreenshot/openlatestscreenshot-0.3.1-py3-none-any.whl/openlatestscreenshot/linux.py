# built in
import re, os
import subprocess
import importlib.resources as pkg_res
from datetime import datetime, timezone


SCREENSHOT_FILENAME_DATE_CAPTURE_REGEX_LINUX = (
    r"Screenshot from (\d{4}-\d{2}-\d{2} \d{2}-\d{2}-\d{2})\.png"
)
GNOME_NOTIFICATION_SCRIPT = "gnome-notification.sh"


def get_screenshot_capture_date(filepath):
    # search for a date using the screenshot filename regex
    screenshot_filename = re.fullmatch(
        SCREENSHOT_FILENAME_DATE_CAPTURE_REGEX_LINUX, filepath.name
    )
    # if the filename matches the screenshot filename regex
    if screenshot_filename is not None:
        # get date from filename as a string
        date_str = screenshot_filename.group(1)
        # convert date string to datetime object
        date = datetime.strptime(date_str, "%Y-%m-%d %H-%M-%S")
        # get datetime as utc posix timestamp for simple comparison
        return date.replace(tzinfo=timezone.utc).timestamp()
    else:
        return None


def run_script(logger, rel_script_path, *args):
    script_path = pkg_res.files("openlatestscreenshot").joinpath(
        f"scripts/{rel_script_path}"
    )

    if not script_path.is_file():
        raise Exception(f"'{script_path}' not found in package")

    logger.info(f"Calling script '{script_path}' with args [{args}]...")

    subprocess.run(
        ["/bin/bash", str(script_path), *args],
        check=True,  # raise if the script exits non‑zero
        stdout=subprocess.DEVNULL,
    )


def native_notification(logger, summary, body, icon):
    desktop_env = os.getenv("XDG_CURRENT_DESKTOP").split(":")[1].lower()

    if desktop_env == "gnome":
        run_script(logger, GNOME_NOTIFICATION_SCRIPT, summary, body, icon)
        pass
    else:
        raise NotImplementedError("Unsupported desktop environment")
