from urllib.parse import quote_plus

# from bs4 import BeautifulSoup
import requests

REPL_URL = "https://replit.com/@{name}/{project}"
LOCATION_URL = "https://replit.com/data/repls/signed_urls/{repl_id}/{file_name}"
FILE_LIST_URL = "https://replit.com/data/repls/@{user}/{slug}"
ACCESS_HEADERS = {"origin": "https://replit.com", "Referer": None}


def get_details(name: str, project: str):
    file_list_request = requests.get(
        FILE_LIST_URL.format(
            user=name,
            slug=project   
        ))

    if file_list_request.status_code != 200:
        raise ValueError("Invalid name or project name provided")

    file_list_json = file_list_request.json()

    file_list = file_list_json['fileNames']

    repl_id = file_list_json['id'];

    return {'repl_id':repl_id, 'file_list':file_list}

def get_file_urls(data: dict):
    repl_id = data['repl_id']
    file_list = data['file_list']
    if 'setup.py' not in file_list:
        raise FileNotFoundError("Repl doesn't contain setup.py file")

    for file_path in file_list:
        yield file_path, LOCATION_URL.format(
            repl_id=repl_id,
            file_name=quote_plus(file_path)
        )

def get_file_contents(file_url: str, name: str, project: str):
    repl_url = REPL_URL.format(
        name=name,
        project=project
    )
    file_meta = requests.get(file_url).json()
    header_copy = ACCESS_HEADERS.copy()
    header_copy['Referer'] = repl_url
    file_content = requests.get(file_meta["urls_by_action"]["read"], headers=header_copy)
    return file_content.content

def collect_files(name: str, project: str):
    repl_meta = get_details(name, project)
    for file_path, file_url in get_file_urls(repl_meta):
        yield file_path, get_file_contents(file_url, name, project)
