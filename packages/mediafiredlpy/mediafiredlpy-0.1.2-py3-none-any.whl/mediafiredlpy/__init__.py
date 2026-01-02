import requests
from bs4 import BeautifulSoup
import re

def mf(url):
    if not url.startswith('https://www.mediafire.com'):
        return {
            'status': 'false',
            'Error': 'You Input Wrong Url'
        }

    response = requests.get(url)
    if response.status_code != 200:
        return {
            'status': 'false',
            'Error': f'HTTP Error: {response.status_code}'
        }

    soup = BeautifulSoup(response.text, 'html.parser')

    download_button = soup.select_one('a#downloadButton')
    dl = download_button['href'] if download_button else 'undefined'
    file_text = download_button.text.strip() if download_button else ''
    upload_info_raw = soup.select_one('div.DLExtraInfo-sectionDetails p')
    upload = upload_info_raw.text.strip().split('\n')[0] if upload_info_raw else 'undefined'

    match = re.search(r'\d+(\.\d+)?\s?(KB|MB|GB)', file_text)
    date = re.search(r'\w+\s\d{1,2},\s\d{4}',upload)
    date = date.group(0) if date else 'undefined'
    file_size = match.group(0) if match else 'undefined'

    return {
        'status': 'true',
        'data': {
            'download': dl,
            'fileSize': file_size,
            'uploadInfo': upload,
            'date':date
        }
    }




