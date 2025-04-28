import logging
import os

DATA_DIR = './data/'
TMP_DIR = './tmp/'
LIST_OUTPUT_FILE = os.path.join(DATA_DIR, 'extensions.txt')
DOWNLOAD_DIR = os.path.join(DATA_DIR, 'extension/')
SOURCE_DIR = os.path.join(DATA_DIR, 'source/')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)


logging.basicConfig(
    filename=os.path.join(TMP_DIR, './collector.log'),
    filemode='a',
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)  # Only show ERROR in console to keep tqdm clean
formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%H:%M:%S')
console_handler.setFormatter(formatter)
logging.getLogger('').addHandler(console_handler)