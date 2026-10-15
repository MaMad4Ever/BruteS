# Brutes

A fast DNS brute-force subdomain scanner written in Python.

Brutes sends DNS queries (`A` / `AAAA` by default) for every word in a wordlist and prints the subdomains that resolve. It does **not** send HTTP requests, so it also finds hosts that have no web server (e.g. `mail`, `ns1`, `vpn`).

## Features

- Pure DNS resolution using `dnspython`
- Multi-threaded
- Wildcard DNS detection and filtering (avoids false positives)
- Custom resolvers: comma-separated list **or** a file (`resolvers.txt`)
- Selectable record types (`A`, `AAAA`, `CNAME`, ...)
- Optional display of resolved IP addresses
- Silent mode and file output for piping into other tools

## Installation

```bash
git clone https://github.com/MaMad4Ever/Brutes.git
cd Brutes
```

```bash
pip3 install -r requirements.txt
```

`requirements.txt`:

```
dnspython
```

## Wordlist recommendations

- **n0kovo's** wordlists: [Can be downloaded from here](https://github.com/n0kovo/n0kovo_subdomains)
- **assetnote** wordlists: [Can be downloaded from here](https://wordlists.assetnote.io)
- **megalist** wordlists: [Can be downloaded from here](https://github.com/netsecurity-as/subfuz/blob/master/subdomain_megalist.txt)
- **SecLists** wordlists: [Can be downloaded from here](https://github.com/danielmiessler/SecLists)

## Usage

Basic scan (system resolver, default wordlist `subdomain_names.txt`):

```bash
python3 brutes.py -d example.com
```

Custom wordlist and resolvers given inline:

```bash
python3 brutes.py -d example.com -w wordlist.txt -r 8.8.8.8,1.1.1.1
```

Resolvers loaded from a file:

```bash
python3 brutes.py -d example.com -w wordlist.txt -r resolvers.txt -t 100
```

Show IPs and save results:

```bash
python3 brutes.py -d example.com -w wordlist.txt -r resolvers.txt --show-ip -o out.txt
```

Silent mode (prints only resolved subdomains, good for piping):

```bash
python3 brutes.py -d example.com -s | httpx
```

### Options

```console
Switch:
  -h, --help                           show this help message and exit
  -d DOMAIN, --domain DOMAIN           Target domain
  -u, --show-unreachable               Show unresolved hosts
  -t THREADS, --threads THREADS        Number of threads (default: 50)
  -w WORDLIST, --wordlist WORDLIST     Path to the wordlist file (default: subdomain_names.txt)
  -s, --silent                         Print only resolved hosts
  -o OUTPUT, --output OUTPUT           Save resolved subdomains to a file
  --timeout TIMEOUT                    DNS timeout in seconds (default: 3)
  -r RESOLVERS, --resolvers RESOLVERS  DNS servers: comma-separated list or path to a file
                                       (one per line), e.g. 8.8.8.8,1.1.1.1 or resolvers.txt
  --types TYPES                        Record types to query (default: A,AAAA)
  --show-ip                            Show resolved IP addresses
```

### Resolvers file format

One DNS server per line. Empty lines and lines starting with `#` are ignored.

```
# Google
8.8.8.8
8.8.4.4
# Cloudflare
1.1.1.1
1.0.0.1
```

## Wildcard DNS

Some domains answer for **any** subdomain (e.g. `*.example.com`). Before scanning, Brutes resolves a few random non-existent names; if they resolve, the returned IPs are treated as wildcard IPs and any result that only matches them is filtered out.

## Tips

- Very high thread counts can trigger rate limiting on public resolvers (you will see `timeout` results). Use several resolvers and keep threads reasonable.
- A `--timeout` of 2-3 seconds is a good balance between speed and not missing slow but valid hosts.
- For multi-million-line wordlists, dedicated tools such as `puredns` or `massdns` will be faster.

## Disclaimer

Use this tool only on domains you own or have explicit permission to test. The author is not responsible for any misuse.
