from datetime import datetime


def handle_new_latest_screenshot(logger):
    def _func(latest_utc_timestamp, latest_screenshot_filepath):
        logger.debug(
            f"{latest_utc_timestamp} ({datetime.utcfromtimestamp(latest_utc_timestamp).strftime('%Y-%m-%d %H-%M-%S')}) is now the most recent screenshot found! ({latest_screenshot_filepath.name})"
        )
    return _func
