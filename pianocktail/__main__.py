import logging
import time
from pianocktail.utils.logging import logger_config

main_logger = logging.getLogger("pianocktail")

event = logger_config()
main_logger.info("Hello")
time.sleep(10)
event.set()
