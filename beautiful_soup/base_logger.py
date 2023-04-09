import logging
import os
import sys
dirname = os.path.dirname(__file__)
dataInfoPath = os.path.join(dirname, "..", "..", "logs")
if not os.path.exists(os.path.join(dataInfoPath)):
    os.mkdir(os.path.join(dataInfoPath))
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(dataInfoPath, "logs.log"))
    ],
    force=True)
logger = logging.getLogger("base_logger")
