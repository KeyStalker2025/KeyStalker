import io
import json
import os

from collections import OrderedDict
from urllib.parse import urlencode
from typing import Optional, Tuple, Dict, Any, List

import requests
from tqdm import tqdm

from extracting.config import DATA_DIR, LIST_OUTPUT_FILE, TMP_DIR, logging

CONFIG = {
    'API_HOST': "https://chrome.google.com/webstore/ajax/item?",
    'DATA_DIR':  DATA_DIR,
    'OUTPUT_FILE': LIST_OUTPUT_FILE,
    'CHECKPOINT_FILE': os.path.join(TMP_DIR, 'checkpoint.json'),
    'MIN_USER_COUNT': 1,
    'STORE_VERSION': '20210820',
    'HTTP_HEADERS': {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}
}


def is_string_in_file(target_string: str, file_path: str) -> bool:
    """Check if a specific string exists in a file."""
    if not os.path.exists(file_path):
        return False
    with open(file_path, 'r', encoding='utf-8') as file:
        return target_string in file.read()

def append_dict_to_file(data: Dict[str, Any], file_path: str) -> None:
    """Append a dictionary as a JSON object into a file."""
    if data:
        ordered_data = OrderedDict(data)
        with io.open(file_path, 'a+', encoding='utf-8') as file:
            json.dump(ordered_data, file)
            file.write('\n')

def load_checkpoint(checkpoint_file: str) -> Optional[str]:
    """Load the checkpoint token if exists."""
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('token')
    return None

def save_checkpoint(token: str, checkpoint_file: str) -> None:
    """Save the current token to checkpoint file."""
    with open(checkpoint_file, 'w', encoding='utf-8') as f:
        json.dump({'token': token}, f)


class WebStoreCollector:
    """Collector for Chrome Web Store Extensions."""

    def __init__(self) -> None:
        self.page_limit: int = 200
        self.output_file_path: str = CONFIG['OUTPUT_FILE']
        self.checkpoint_file: str = CONFIG['CHECKPOINT_FILE']

        if not os.path.exists(self.output_file_path):
            with open(self.output_file_path, "w+", encoding='utf-8'):
                pass

    def run(self) -> None:
        """Main method to start collecting extensions."""
        next_page_token: Optional[str] = load_checkpoint(self.checkpoint_file)
        total_saved = 0

        with tqdm(desc="Collecting Extensions", unit="page") as pbar:
            while True:
                url = self.build_request_url(next_page_token)

                try:
                    response = self.make_request(url)
                    response_data = self.parse_response(response)
                except Exception as e:
                    logging.error(f"Failed to fetch data: {e}")
                    break

                extension_items = response_data[0][1][1]
                next_page_token = response_data[0][1][4] if response_data[0][1][4] != '#@' else None

                if not extension_items:
                    logging.info("No more extensions found. Exiting.")
                    break

                saved_this_page = self.process_extensions(extension_items)
                total_saved += saved_this_page

                if next_page_token:
                    save_checkpoint(next_page_token, self.checkpoint_file)

                if saved_this_page == 0 and next_page_token is None:
                    logging.info("No new extensions added. Exiting.")
                    break

                pbar.set_postfix(total_saved=total_saved)
                pbar.update(1)

    def build_request_url(self, token: Optional[str] = None) -> str:
        """Construct the request URL with query parameters."""
        query_params = {
            'hl': 'en',
            'pv': CONFIG['STORE_VERSION'],
            'mce': ('atf,pii,rtr,rlb,gtc,hcn,svp,wtd,hap,nma,dpb,utb,hbh,ebo,hqb,ifm,'
                    'ndd,ntd,oiw,uga,c3d,ncr,hns,ctm,ac,hot,hfi,dtp,mac,bga,pon,fcf,rai,hbs,rma,'
                    'ibg,pot,evt,hib'),
            'requestedCounts': f'infiniteWall:{self.page_limit}:0:false',
            'category': 'extensions',
            'rt': 'j'
        }
        if token:
            query_params['token'] = token

        return CONFIG['API_HOST'] + urlencode(query_params)

    def make_request(self, url: str) -> requests.Response:
        """Send HTTP POST request to the given URL."""
        response = requests.post(url, allow_redirects=False, timeout=10, headers=CONFIG['HTTP_HEADERS'])
        if response.status_code != 200:
            raise requests.RequestException(f"Request Error: {response.status_code}")
        return response

    def parse_response(self, response: requests.Response) -> List[Any]:
        """Parse the JSON response, stripping off anti-CSRF prefix."""
        cleaned_text = response.text.lstrip(")]}'\n")
        return json.loads(cleaned_text)

    def process_extensions(self, extensions: List[Any]) -> int:
        """Process a list of extensions and save new ones to file."""
        new_entries = 0

        for extension_data in extensions:
            ext_id, user_count, extension_info = self.parse_extension_info(extension_data)

            if is_string_in_file(ext_id, self.output_file_path):
                continue

            if user_count >= CONFIG['MIN_USER_COUNT']:
                append_dict_to_file(extension_info, self.output_file_path)
                logging.info(f"Saved extension: {ext_id} | Users: {user_count}")
                new_entries += 1

        return new_entries

    def parse_extension_info(self, data: List[Any]) -> Tuple[str, int, Dict[str, Any]]:
        """Extract useful fields from raw extension data."""
        try:
            extension_id = data[0]
            user_count = int(data[23].replace(',', '').replace('+', ''))
            extension_info = {
                "id": extension_id,
                "name": data[1],
                "developer": data[2],
                "description": data[6],
                "primary_category": data[9],
                "secondary_category": data[10],
                "rating_score": data[12],
                "star_count": data[22],
                "user_count": data[23],
                "url": data[11]
            }
            return extension_id, user_count, extension_info
        except (IndexError, ValueError) as error:
            raise ValueError(f"Error parsing extension data: {error}") from error


if __name__ == '__main__':
    collector = WebStoreCollector()
    collector.run()
