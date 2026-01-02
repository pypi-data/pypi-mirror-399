# built in
import re
from pathlib import Path


SCREENSHOT_FILENAME_VALIDATION_REGEX_WINDOWS = r"Screenshot .*\.png"


def get_screenshot_capture_date(filepath):
    # if the screenshot filename matches the validation regex
    if re.fullmatch(
        SCREENSHOT_FILENAME_VALIDATION_REGEX_WINDOWS, filepath.name
    ):
        # HACK: There isn't really a reliable way to get the date a screenshot was taken on Windows, but the last modified date is the best option I've found thus far
        # HACK: doesn't actually use a filename extracted date because by default Windows doesn't add timestamps to screenshot filenames
        return Path.stat(filepath).st_mtime
    else:
        return None
