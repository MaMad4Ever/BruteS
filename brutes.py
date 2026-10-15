import argparse
import os
import random
import string
from concurrent.futures import ThreadPoolExecutor, as_completed

import dns.exception
import dns.resolver


def make_resolver(nameservers, timeout):
    resolver = dns.resolver.Resolver(configure=not nameservers)
    if nameservers:
        resolver.nameservers = nameservers
    resolver.timeout = timeout
    resolver.lifetime = timeout
    return resolver


def resolve_host(host, resolver, record_types):
    """Returns (host, status, set_of_ips)"""
    ips = set()
    status = 'no-record'
    for rtype in record_types:
        try:
            answer = resolver.resolve(host, rtype)
            for rdata in answer:
                ips.add(rdata.to_text())
        except dns.resolver.NXDOMAIN:
            return host, 'nxdomain', set()
        except dns.resolver.NoAnswer:
            continue
        except dns.exception.Timeout:
            status = 'timeout'
        except dns.resolver.NoNameservers:
            status = 'error'
        except Exception as e:
            status = f'error: {e}'
    if ips:
        return host, 'resolved', ips
    return host, status, set()

def load_resolvers(value):
    """Accepts a file path or a comma-separated list of DNS servers."""
    if not value:
        return []
    if os.path.isfile(value):
        with open(value, 'r') as f:
            items = [line.strip() for line in f]
    else:
        items = value.split(',')
    return [x.strip() for x in items if x.strip() and not x.strip().startswith('#')]

def detect_wildcard(domain, resolver, record_types):
    """Resolve a random non-existent label to detect wildcard DNS."""
    wildcard_ips = set()
    for _ in range(3):
        label = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
        _, status, ips = resolve_host(f"{label}.{domain}", resolver, record_types)
        if status == 'resolved':
            wildcard_ips |= ips
    return wildcard_ips


def domain_scanner(domain, words, show_unreachable, max_workers, silent,
                   output_file, timeout, nameservers, record_types, show_ip):
    if not silent:
        print('----------- DNS Scanner Started -----------')

    resolver = make_resolver(nameservers, timeout)

    wildcard_ips = detect_wildcard(domain, resolver, record_types)
    if wildcard_ips and not silent:
        print(f'[!] Wildcard DNS detected ({", ".join(sorted(wildcard_ips))}), filtering matching results')

    hosts = [f"{w}.{domain}" for w in words]
    resolved, failed = [], []

    out = open(output_file, 'a') if output_file else None
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(resolve_host, h, resolver, record_types) for h in hosts]
            for future in as_completed(futures):
                host, status, ips = future.result()

                if status == 'resolved' and wildcard_ips and ips <= wildcard_ips:
                    status = 'wildcard'

                if status == 'resolved':
                    resolved.append((host, ips))
                    if out:
                        out.write(host + "\n")
                        out.flush()
                    if silent:
                        print(host)
                    else:
                        print(f'[+] {host} -> {", ".join(sorted(ips))}' if show_ip else f'[+] {host}')
                elif show_unreachable:
                    failed.append(host)
                    if not silent:
                        print(f'[-] {host} - {status}')
    finally:
        if out:
            out.close()

    if not silent:
        print(f'\nResolved: {len(resolved)} / {len(hosts)}')
        for host, _ in resolved:
            print(host)
        print('\n----- Scanner Stopped -----')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DNS Brute-force Subdomain Scanner')
    parser.add_argument('-d', '--domain', required=True, help='Target domain')
    parser.add_argument('-u', '--show-unreachable', action='store_true', help='Show unresolved hosts')
    parser.add_argument('-t', '--threads', type=int, default=50, help='Number of threads (default: 50)')
    parser.add_argument('-w', '--wordlist', default='subdomain_names.txt', help='Wordlist path')
    parser.add_argument('-s', '--silent', action='store_true', help='Print only resolved hosts')
    parser.add_argument('-o', '--output', help='Save resolved subdomains to a file')
    parser.add_argument('--timeout', type=float, default=3, help='DNS timeout in seconds (default: 3)')
    parser.add_argument('-r', '--resolvers', default='8.8.4.4', help='DNS servers: comma-separated list or path to a file, e.g. 8.8.8.8,1.1.1.1 or resolvers.txt')
    parser.add_argument('--types', default='A,AAAA', help='Record types to query (default: A,AAAA)')
    parser.add_argument('--show-ip', action='store_true', help='Show resolved IPs')
    args = parser.parse_args()

    if not os.path.isfile(args.wordlist):
        print(f"Error: The wordlist file '{args.wordlist}' does not exist.")
        raise SystemExit(1)

    with open(args.wordlist, 'r') as f:
        words = [line.strip() for line in f if line.strip()]

    nameservers = load_resolvers(args.resolvers.strip())
    record_types = [x.strip().upper() for x in args.types.split(',') if x.strip()]

    domain_scanner(args.domain.strip(), words, args.show_unreachable, args.threads,
                   args.silent, args.output, args.timeout, nameservers,
                   record_types, args.show_ip)
