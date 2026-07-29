import sys
import os

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.gui.app import SmartAlarmApp
from src.utils.logger import setup_logger

logger = setup_logger("Main")


def main():
    try:
        logger.info("Starting Smart Alarm Desktop Application...")
        app = SmartAlarmApp()
        app.mainloop()
        logger.info("Application exited cleanly.")
    except Exception as e:
        logger.critical(f"Unhandled application exception: {e}", exc_info=True)


if __name__ == "__main__":
    main()
