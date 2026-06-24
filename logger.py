import logging

logger = logging.getLogger("barguesapp")

logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s")

# TERMINAl
stream_handle = logging.StreamHandler()
stream_handle.setFormatter(formatter)

# FILE
file_handle = logging.FileHandler("logs/app.log")
file_handle.setFormatter(formatter)

logger.addHandler(file_handle)
logger.addHandler(stream_handle)