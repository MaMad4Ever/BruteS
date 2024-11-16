import requests
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

def check_subdomain(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return url, 'reachable'
        else:
            return url, 'unreachable'
    except requests.ConnectionError:
        return url, 'unreachable'
    except requests.Timeout:
        return url, 'timeout'
    except Exception as e:
        return url, f'error: {e}'

def domain_scanner(domain_name, sub_domain_names, show_unreachable, max_workers):
    print('----------- Scanner Started -----------')
    print('---- URL after scanning subdomains ----')

    reachable_urls = []
    unreachable_urls = []

    urls = [f"https://{subdomain}.{domain_name}" for subdomain in sub_domain_names]

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(check_subdomain, url): url for url in urls}
        
        for future in as_completed(future_to_url):
            url, status = future.result()
            if status == 'reachable':
                reachable_urls.append(url)
                print(f'[+] {url}')
            elif show_unreachable:
                unreachable_urls.append(url)
                print(f'[-] {url} - {status}')

    print('\nReachable URLs:')
    for url in reachable_urls:
        print(url)

    if show_unreachable:
        print('\nUnreachable URLs:')
        for url in unreachable_urls:
            print(url)

    print('\n---- Scanning Finished ----')
    print('----- Scanner Stopped -----')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Domain Scanner for Subdomains')
    parser.add_argument('-d', '--domain', required=True, help='Enter the Domain Name')
    parser.add_argument('-u', '--show-unreachable', action='store_true', help='Show unreachable URLs')
    parser.add_argument('-t', '--threads', type=int, default=10, help='Number of threads to use (default: 10)')
    parser.add_argument('-w', '--wordlist', type=str, default='subdomain_names.txt', help='Path to the wordlist file (default: subdomain_names.txt)')
    args = parser.parse_args()

    dom_name = args.domain.strip()
    show_unreachable = args.show_unreachable
    max_workers = args.threads
    wordlist_path = args.wordlist.strip()
    print('\n')

    if not os.path.isfile(wordlist_path):
        print(f"Error: The wordlist file '{wordlist_path}' does not exist.")
        exit(1)

    try:
        with open(wordlist_path, 'r') as file:
            sub_dom = [line.strip() for line in file if line.strip()]
        domain_scanner(dom_name, sub_dom, show_unreachable, max_workers)
    except FileNotFoundError:
        print("Error: 'subdomain_names.txt' file not found.")
