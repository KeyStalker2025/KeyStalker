import json
import os
import random
import time
from typing import List, Dict

import requests
from tqdm import tqdm

from extracting.config import DOWNLOAD_DIR, LIST_OUTPUT_FILE

CONFIG = {
    'EXTENSION_LIST_FILE': LIST_OUTPUT_FILE,
    'DOWNLOAD_DIR': DOWNLOAD_DIR,
    'CHROME_VERSION': '121.0.6167',
    'NACL_ARCH': 'x86-64',
    'SLEEP_RANGE': (0, 3),
    'REQUEST_TIMEOUT': 30
}


def load_extension_list(file_path: str) -> List[Dict[str, str]]:
    """Load the list of extensions from a JSON lines file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Extension list file not found: {file_path}")

    extensions = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                extensions.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return extensions

def build_crx_download_url(extension_id: str) -> str:
    """Construct the CRX file download URL."""
    base_url = "https://clients2.google.com/service/update2/crx"
    params = (
        f"response=redirect&prodversion={CONFIG['CHROME_VERSION']}"
        f"&acceptformat=crx2,crx3&x=id%3D{extension_id}%26uc"
        f"&nacl_arch={CONFIG['NACL_ARCH']}"
    )
    return f"{base_url}?{params}"

def download_extension(extension_id: str, output_path: str) -> None:
    """Download a Chrome extension CRX file."""
    url = build_crx_download_url(extension_id)
    response = requests.get(url, timeout=CONFIG['REQUEST_TIMEOUT'])
    response.raise_for_status()

    with open(output_path, 'wb') as file:
        file.write(response.content)

def main():
    """Main function to download CRX files."""
    os.makedirs(CONFIG['DOWNLOAD_DIR'], exist_ok=True)

    extensions = load_extension_list(CONFIG['EXTENSION_LIST_FILE'])
    print(f"Total extensions to download: {len(extensions)}")

    with tqdm(extensions, desc="Downloading Extensions", ncols=100) as pbar:
        for ext in pbar:
            ext_id = ext.get('id')
            if not ext_id:
                continue

            output_file = os.path.join(CONFIG['DOWNLOAD_DIR'], f"{ext_id}.crx")

            if os.path.isfile(output_file):
                continue  # Skip already downloaded

            try:
                download_extension(ext_id, output_file)
                # Update progress bar with postfix info
                pbar.set_postfix({"Extension": ext_id, "Status": "Downloaded"})
                time.sleep(random.uniform(*CONFIG['SLEEP_RANGE']))
            except Exception as e:
                # Update progress bar with error info
                pbar.set_postfix({"Extension": ext_id, "Status": f"Failed: {e}"})

if __name__ == '__main__':
    main()
