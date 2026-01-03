from src.wztools.utils.logger import get_loguru, get_logger

logger = get_loguru(log_file="logs/t.log")
# logger = get_logger(log_file="logs/t.log")

logger.info("hi")