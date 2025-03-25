# Installation
```bash
git clone https://github.com/MaMad4Ever/Brutes.git
```
```bash
pip3 install -r requirements.txt
```

## Wordlist recommendations
- **n0kovo's** wordlists: [Can be downloaded from here](https://github.com/n0kovo/n0kovo_subdomains)
- **assetnote** wordlists: [Can be downloaded from here](https://wordlists.assetnote.io)
- **megalist** wordlists: [Can be downloaded from here](https://github.com/netsecurity-as/subfuz/blob/master/subdomain_megalist.txt)
- **SecLists** wordlists: [Can be downloaded from here](https://github.com/danielmiessler/SecLists)

## Usage
```bash
python3 brutes.py -d example.com
```
```bash
python3 brutes.py -d example.com -m http
```
```console
Switch:
   -d, --domain                       Enter the Domain Name
   -u, --show-unreachable             Show unreachable URLs
   -t, --threads                      Number of threads to use (default: 10)
   -w, --wordlist                     Path to the wordlist file (default: subdomain_names.txt)
   -m', --mode                        Protocol to use (default: https)

```
