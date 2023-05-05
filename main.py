import os
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import requests
from colorama import init, Fore, Style
import cgi

init()

def download_file(session, url, directory):
    response = session.get(url)
    response.raise_for_status()

    if 'Content-Disposition' in response.headers:
        _, params = cgi.parse_header(response.headers['Content-Disposition'])
        file_name = params.get('filename')
    else:
        file_name = os.path.basename(urlparse(url).path)

    file_path = os.path.join(directory, file_name)

    with open(file_path, 'wb') as f:
        f.write(response.content)

    print(Fore.GREEN + '[+] Downloading file:', file_name + Style.RESET_ALL)

def download_files(url, download_directory):
    if not os.path.exists(download_directory):
        try:
            os.makedirs(download_directory)
        except OSError as e:
            print(Fore.RED + f'[+] Failed to create folder {download_directory}: {e}' + Style.RESET_ALL)
            return

    with requests.Session() as session:
        response = session.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        links = soup.find_all('a')

        count = 0

        for link in links:
            link_url = link.get('href')
            if link_url and not link_url.endswith(('/', '#')) and os.path.splitext(link_url)[1]:
                try:
                    download_file(session, urljoin(url, link_url), download_directory)
                    count += 1
                except requests.exceptions.RequestException as e:
                    print(Fore.RED + f'[-] Failed to download {link_url}' + Style.RESET_ALL)
                except OSError as e:
                    print(Fore.RED + f'[-] Failed to save {link_url}' + Style.RESET_ALL)

        print(Fore.GREEN + f'[{count}] files downloaded successfully.' + Style.RESET_ALL)

url = input(Fore.GREEN + 'Web $> ' + Style.RESET_ALL)
download_directory = input(Fore.GREEN + 'Directory $> ' + Style.RESET_ALL)

download_files(url, download_directory)
