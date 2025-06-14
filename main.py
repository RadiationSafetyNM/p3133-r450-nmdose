import platform
import os
from logger import get_logger

logger = get_logger(__name__)

def main():
    logger.info(
        "===== Starting MyProject (version: %s, env: %s) =====",
        "1.0.0", os.getenv('ENV', 'development')
    )
    logger.info("Python version: %s", platform.python_version())
    logger.info("Host: %s, User: %s", platform.node(), os.getenv("USER") or os.getenv("USERNAME"))
    logger.info("LOG_LEVEL: %s", os.getenv("LOG_LEVEL"))
    # 이하 main logic...

if __name__ == "__main__":
    main()
