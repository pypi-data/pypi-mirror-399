import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import ipaddress
import os
import sys
import json
import re
import csv
import time
import tempfile

# --- PATH CONFIGURATION ---
# 1. Get the directory where this script is installed (for read-only config)
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_DATA_DIR = os.path.join(PACKAGE_DIR, "data")

# 2. Define the Writable Data Directory (User's Home Directory)
# We use the user's home folder to avoid "Permission Denied" errors in site-packages
USER_HOME = os.path.expanduser("~")
USER_DATA_DIR = os.path.join(USER_HOME, ".kavachnet")

# Ensure user data directory exists
os.makedirs(USER_DATA_DIR, exist_ok=True)

# --- FILE PATHS ---
# Read-only source config (shipped with package)
SOURCE_FILE = os.path.join(PACKAGE_DATA_DIR, "vpn_sources.json")

# Writable data files (downloaded at runtime)
CACHE_FILE = os.path.join(USER_DATA_DIR, "vpn_ip_list.txt")
ASN_FILE_V4 = os.path.join(USER_DATA_DIR, "asn_ipv4.csv")
ASN_FILE_V6 = os.path.join(USER_DATA_DIR, "asn_ipv6.csv")

TIMEOUT = 15  # seconds for HTTP requests
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

# --- RISK CLASSIFICATION CONSTANTS ---
HIGH_RISK_ASNs = [
    'AS136787', 'AS141039','AS147049', 'AS207137', # NordVPN
    'AS209854', # Surfshark
    'AS49981',  # WorldStream
    'AS53667',  # FranTech / BuyVM    
    'AS14061',  # DigitalOcean
    'AS16276',  # OVH
    'AS24940',  # Hetzner
    'AS16509',  # AWS
    'AS63949',  # Linode
    'AS62240',  # Clouvider
    'AS9009',   # M247 
    'AS20473',  # Choopa
    'AS12876',  # Contabo 
    'NORDVPN', 'TEFINCOM', 'SURFSHARK', 'CYBERZONE',
    'DIGITALOCEAN', 'OVH', 'HETZNER', 'AMAZON',     
    'AWS', 'LINODE', 'AKAMAI', 'GOOGLE', 'MICROSOFT',
    'ORACLE', 'ALIBABA', 'TENCENT', 'VULTR', 
    'CHOOPA', 'DATACAMP', 'M247', 'CONTABO', 
    'HOSTINGER', 'WORLDSTREAM', 'FRANTECH', 
    'BUYVM', 'LEASEWEB'
]

SUSPICIOUS_ASNs = [
    'AS60626',  # Leaseweb
    'CLOUVIDER', 'CLOUDFLARE', 'FASTLY', 'CDN77'
]

DEFAULT_VPN_PROVIDER_ASN_MAP = {
    '9009': 'NordVPN, AirVPN, Others',
    '136787': 'NordVPN, AirVPN',
    '212238': 'NordVPN', 
    '212239': 'NordVPN',
    '209854': 'Surfshark',
    '137409': 'ExpressVPN', '206092': 'ExpressVPN', '396356': 'ExpressVPN',
    '401152': 'ExpressVPN', '8851': 'ExpressVPN', '7040': 'ExpressVPN',
    '209103': 'ProtonVPN',
}

DEFAULT_VPN_PROVIDER_KEYWORDS = {
    'NORDVPN': 'NordVPN',
    'TEFINCOM': 'NordVPN',
    'SURFSHARK': 'Surfshark',
    'CYBERZONE': 'Surfshark',
    'EXPRESSVPN': 'ExpressVPN',
    'PROTONVPN': 'ProtonVPN',
    'MULLVAD': 'Mullvad',
}

def _load_asn_csv(path):
    out = {}
    try:
        with open(path, newline='', encoding='utf-8') as fh:
            reader = csv.reader(fh)
            header = next(reader, None)
            if header is None: return out
            cols = [c.strip().lower() for c in header]
            asn_idx = next((i for i, c in enumerate(cols) if 'asn' in c), None)
            prov_idx = next((i for i, c in enumerate(cols) if 'provider' in c or 'vpn' in c), None)
            
            if asn_idx is not None and prov_idx is not None:
                for row in reader:
                    if len(row) > max(asn_idx, prov_idx):
                        asn_key = str(row[asn_idx]).upper().replace('AS', '').strip()
                        out[asn_key] = row[prov_idx].strip()
    except Exception: pass
    return out

def load_vpn_provider_asn_map():
    netify_csv = os.path.join(PACKAGE_DATA_DIR, "netify_vpn_asns.csv")
    if os.path.exists(netify_csv):
        return _load_asn_csv(netify_csv)
    return dict(DEFAULT_VPN_PROVIDER_ASN_MAP)

def load_vpn_provider_keywords():
    return dict(DEFAULT_VPN_PROVIDER_KEYWORDS)

VPN_PROVIDER_ASN_MAP = load_vpn_provider_asn_map()
VPN_PROVIDER_KEYWORDS = load_vpn_provider_keywords()

def get_vpn_provider(asn_str, org_name):
    if asn_str:
        clean_asn = asn_str.upper().replace('AS', '').strip()
        if clean_asn in VPN_PROVIDER_ASN_MAP:
            return VPN_PROVIDER_ASN_MAP[clean_asn]
    if org_name:
        org_upper = org_name.upper()
        for kw, prov in VPN_PROVIDER_KEYWORDS.items():
            if kw in org_upper:
                return prov
    return "Unknown"

def _normalize_ip_for_lookup(ip_str: str) -> str:
    """
    Normalize an IP/CIDR or IP:port string for ASN/network lookups.
    - Strip port from IPv4 like '1.2.3.4:80' -> '1.2.3.4'
    - Handle IPv6 with brackets like '[::1]:80' -> '::1'
    - Leave plain CIDR or IPv6 address unchanged.
    """
    if not isinstance(ip_str, str):
        return ip_str
    s = ip_str.strip()
    # IPv6 with brackets and port: [::1]:80
    if s.startswith('[') and ']:' in s:
        return s.split(']:', 1)[0].lstrip('[')

    # IPv4 with port (very common)
    if ':' in s and s.count('.') == 3:
        return s.rsplit(':', 1)[0]

    return s

# --- ASN / HOSTING LOGIC ---
ASN_INDEX = {'v4': [], 'v6': []}

def get_session():
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def download_asn_db():
    """Downloads the optimized ASN CSV databases (IPv4 and IPv6) from sapics/ip-location-db."""
    urls = {
        "v4": ("https://raw.githubusercontent.com/sapics/ip-location-db/main/asn/asn-ipv4.csv", ASN_FILE_V4),
        "v6": ("https://raw.githubusercontent.com/sapics/ip-location-db/refs/heads/main/asn/asn-ipv6.csv", ASN_FILE_V6)
    }
    
    success = True
    for ver, (url, filepath) in urls.items():
        print(f"[i] Fetching ASN {ver.upper()} Database from {url}...")
        try:
            session = get_session()
            r = session.get(url, headers=HEADERS, timeout=30)
            r.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(r.content)
            print(f"[✓] ASN {ver.upper()} Database updated.")
        except Exception as e:
            print(f"[WARN] Could not fetch ASN {ver.upper()} DB: {e}")
            success = False
            
    return success

def load_asn_db():
    """
    Loads ASN CSVs into memory.
    Returns a dict: {'v4': [(start, end, asn, org), ...], 'v6': [(start, end, asn, org), ...]}
    """
    asn_data = {'v4': [], 'v6': []}
    files = {'v4': ASN_FILE_V4, 'v6': ASN_FILE_V6}
    
    for ver, filepath in files.items():
        if not os.path.exists(filepath):
            continue
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) < 4: continue
                    try:
                        if ver == 'v4':
                            start_int = int(ipaddress.IPv4Address(row[0]))
                            end_int = int(ipaddress.IPv4Address(row[1]))
                        else:
                            start_int = int(ipaddress.IPv6Address(row[0]))
                            end_int = int(ipaddress.IPv6Address(row[1]))
                        asn_num = row[2]
                        org_name = row[3]
                        asn_data[ver].append((start_int, end_int, asn_num, org_name))
                    except ValueError: continue
        except Exception: continue
    
    for ver in ('v4', 'v6'):
        asn_data[ver].sort(key=lambda x: x[0])
        ASN_INDEX[ver] = [r[0] for r in asn_data[ver]]
    
    return asn_data

def check_asn_hosting(ip_str, asn_db):
    """
    Checks if an IP belongs to a hosting provider using the ASN DB.
    """
    try:
        ip_obj = ipaddress.ip_address(ip_str)
        ip_int = int(ip_obj)
    except ValueError:
        return None 

    ver = 'v4' if ip_obj.version == 4 else 'v6'
    db_list = asn_db.get(ver, [])
    starts = ASN_INDEX.get(ver, [])
    
    if not db_list or not starts:
        return None

    import bisect
    idx = bisect.bisect_right(starts, ip_int) - 1
    if idx >= 0 and idx < len(db_list):
        start, end, asn, org = db_list[idx]
        if start <= ip_int <= end:
            return f"AS{asn} {org}"
    return None

def check_organization_risk(asn_org):
    if not asn_org: return False, "LOW", None
    org_upper = asn_org.upper()
    for kw in HIGH_RISK_ASNs:
        if kw in org_upper:
            return True, "HIGH", f"High Risk ASN (Cloud/VPN): {asn_org}"
    for kw in SUSPICIOUS_ASNs:
        if kw in org_upper:
            return True, "MEDIUM", f"Suspicious ASN (Mixed Usage): {asn_org}"
    return False, "LOW", f"Organization: {asn_org}"

# --- DOWNLOADER / PARSER LOGIC ---

def load_sources():
    if not os.path.exists(SOURCE_FILE):
        return {}
    with open(SOURCE_FILE, 'r') as f:
        data = json.load(f)
    return data

def extract_ips_from_text(text):
    lines = text.splitlines()
    cleaned = set()
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "," in line and "{" not in line:
            line = line.split(",")[0].strip()
        if len(line) < 3: continue 
        cleaned.add(line)
    return cleaned

def extract_ips_from_json(data):
    ips = set()
    if isinstance(data, dict):
        if "prefixes" in data:
            for p in data["prefixes"]:
                for key in ["ip_prefix", "ipv4Prefix", "ipv6Prefix"]:
                    if key in p:
                        ips.add(p[key])
        if "vultr" in data:
            for p in data["vultr"]:
                ips.add(p)
        if "LogicalServers" in data:
            for p in data["LogicalServers"]:
                if "EntryIP" in p:
                    ips.add(p["EntryIP"])
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                ips.add(item)
            elif isinstance(item, dict):
                for key in ["ip", "ipv4", "ipv6", "ip_prefix", "ipv4Prefix", "ipv6Prefix", "ip_address", "EntryIP", "station"]:
                    if key in item:
                        ips.add(item[key])
    return ips

def download_list(url):
    try:
        session = get_session()
        resp = session.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        text = resp.text.strip()
        
        if "application/json" in resp.headers.get("Content-Type", "") or text.startswith("{") or text.startswith("["):
            try:
                data = json.loads(text)
                return extract_ips_from_json(data)
            except Exception:
                return extract_ips_from_text(text)
        else:
            return extract_ips_from_text(text)
    except Exception as e:
        print(f"[WARN] Could not fetch {url}: {e}")
        return set()

def load_cached_ips():
    if not os.path.exists(CACHE_FILE):
        return {}

    cached = {}
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                parts = line.split("|")
                if len(parts) >= 2:
                    ip = parts[0]
                    val_part = "|".join(parts[1:])
                    cached[ip] = val_part
                else:
                    cached[line] = "UNKNOWN"
    except Exception: pass
    return cached

def write_atomic(filepath, lines):
    """Writes lines to a temporary file then atomically replaces the target."""
    fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(filepath), prefix=os.path.basename(filepath) + '.', text=True)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as tf:
            for line in lines:
                tf.write(line + '\n')
        os.replace(tmp_path, filepath)
    finally:
        if os.path.exists(tmp_path):
            try: os.remove(tmp_path)
            except Exception: pass

def append_to_cache(entries, cache_path=None, asn_db=None):
    if not entries: return
    target_file = cache_path or CACHE_FILE
    
    # Load existing to merge
    existing = {}
    if os.path.exists(target_file):
        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line: continue
                    parts = line.split('|')
                    # format: ip|src|asn|org|provider
                    # we store parts as a list after the IP
                    existing[parts[0]] = parts[1:]
        except Exception: pass

    # Add new and resolve metadata
    for ip, t in entries.items():
        try:
            if not (isinstance(ip, str) and ('.' in ip or ':' in ip)):
                continue
            src = (t.split('|', 1)[0] if isinstance(t, str) else str(t)).replace('|', '').strip()
            
            # If already exists with full metadata, don't overwrite unless source changed
            if ip in existing and len(existing[ip]) >= 4:
                existing[ip][0] = src
                continue
                
            asn_label, org_name, provider = "", "", "Unknown"
            if asn_db:
                try:
                    rep_ip = _normalize_ip_for_lookup(ip)
                    if '/' in rep_ip:
                        rep_ip = str(ipaddress.ip_network(rep_ip, strict=False).network_address)
                    
                    asn_org = check_asn_hosting(rep_ip, asn_db)
                    if asn_org:
                        m = re.match(r"AS(\d+)\s*(.*)", asn_org)
                        if m:
                            asn_label = f"AS{m.group(1)}"
                            org_name = m.group(2).strip()
                        else:
                            org_name = asn_org
                        provider = get_vpn_provider(asn_label, org_name)
                except Exception: pass
            
            existing[ip] = [src, asn_label, org_name, provider]
        except Exception: continue

    lines = [f"{ip}|{'|'.join(parts)}" for ip, parts in existing.items()]
    write_atomic(target_file, lines)

def refresh_cache(cache_path=None):
    """Downloads both blocklists and the ASN DB with file-based locking."""
    target_cache = cache_path or CACHE_FILE
    lockfile = target_cache + '.lock'
    lockfd = None
    lock_token = str(int(time.time()))
    lock_acquired = False
    
    try:
        lockfd = os.open(lockfile, os.O_CREAT | os.O_EXCL | os.O_RDWR)
        os.write(lockfd, lock_token.encode('utf-8'))
        lock_acquired = True
    except Exception:
        lock_acquired = False

    if not lock_acquired:
        print('[WARN] Another update appears to be running (lock held). Exiting refresh.')
        return {}, 0

    try:
        download_asn_db()
        asn_db = load_asn_db()
        typed_sources = load_sources()
        cached = load_cached_ips() if not cache_path else {}
        total_new = {}
        
        print(f"[i] Starting Blocklist Update...")
        for t, urls in typed_sources.items():
            if t == "ASN": continue 
            for url in urls:
                print(f"    - Fetching {t}: {url[:50]}...")
                fetched = download_list(url)
                new_entries = {ip: t for ip in fetched if ip not in cached}
                if new_entries:
                    print(f"      + {len(new_entries)} new entries.")
                    total_new.update(new_entries)
                    cached.update(new_entries)

        append_to_cache(total_new, cache_path=cache_path, asn_db=asn_db)
        print(f"[OK] Blocklists updated with {len(total_new)} new entries.")
        return cached, len(total_new)
    finally:
        if lockfd is not None:
            try: os.close(lockfd)
            except Exception: pass
            try:
                if os.path.exists(lockfile):
                    os.remove(lockfile)
            except Exception: pass

def load_networks_from_cache(cached_data):
    all_networks = []
    if isinstance(cached_data, dict):
        iterator = cached_data.items()
    else:
        return []

    for ip_str, ip_type in iterator:
        try:
            net = ipaddress.ip_network(ip_str, strict=False)
            all_networks.append((net, ip_type))
        except ValueError:
            continue
    return all_networks

# --- MAIN DECISION LOGIC ---

def is_vpn_ip(ip, networks, asn_db=None):
    """
    Detects if an IP is a VPN/Proxy.
    Returns a tuple: (is_threat, info_string, asn_org)
    """
    asn_org = None
    clean_ip = ip.strip()

    # Support both single IPs and CIDR/network inputs.
    is_network = False
    ip_obj = None
    ip_net = None

    # Normalization (strip port)
    norm_ip = _normalize_ip_for_lookup(clean_ip)

    # First try to parse as a network (CIDR).
    try:
        ip_net = ipaddress.ip_network(norm_ip, strict=False)
        is_network = True
    except ValueError:
        # Not a network; try parsing as an IP address
        try:
            ip_obj = ipaddress.ip_address(norm_ip)
        except ValueError:
            return (None, "Invalid IP Format", None)

    # 0. Always fetch ASN if DB is available (use representative IP)
    if asn_db:
        if is_network:
            asn_org = check_asn_hosting(str(ip_net.network_address), asn_db)
        else:
            asn_org = check_asn_hosting(norm_ip, asn_db)

    # 1. Check Blocklists (Specific Lists)
    matched_types = []
    for net, info in networks:
        try:
            # handle 'source|asn|org|provider' format
            t = info.split('|')[0]
            if is_network:
                if ip_net.overlaps(net):
                    matched_types.append(t)
            else:
                if ip_obj in net:
                    matched_types.append(t)
        except Exception: continue

    if matched_types:
        unique = sorted(list(set(matched_types)))
        reason = f"Matched Blocklist: {', '.join(unique)}"
        return (True, reason, asn_org)

    # 2. Check ASN / Hosting (Broad Ownership Check)
    if asn_org:
        is_risk, level, msg = check_organization_risk(asn_org)
        if is_risk:
            return (True, msg, asn_org)
        return (False, msg, asn_org)

    return (False, "Unknown Organization", None)

def get_org_ranges(keyword, asn_db):
    keyword = keyword.lower()
    org_ranges = []
    for ver in ['v4', 'v6']:
        for start, end, asn, org in asn_db.get(ver, []):
            if keyword in org.lower() or keyword == str(asn) or keyword == f"as{asn}":
                org_ranges.append((start, end, asn, org, ver))
    return org_ranges

def format_org_ranges(org_ranges):
    return [{"Start IP": str(ipaddress.ip_address(s)), "End IP": str(ipaddress.ip_address(e)), "ASN": f"AS{a}", "Organization": o, "Version": v} for s, e, a, o, v in org_ranges]

def calculate_ip_count(start, end):
    return int(ipaddress.ip_address(end)) - int(ipaddress.ip_address(start)) + 1

def check_vpns_in_ranges(org_ranges, vpn_networks):
    matches = []
    for net, info in vpn_networks:
        try:
            ns, ne, nv = int(net.network_address), int(net.broadcast_address), net.version
            for os, oe, oa, on, ov in org_ranges:
                if (nv==4 and ov=='v4' or nv==6 and ov=='v6') and os <= ns and ne <= oe:
                    matches.append({'VPN IP / CIDR': str(net), 'Source': info.split('|')[0], 'Organization Range': f"{ipaddress.ip_address(os)} - {ipaddress.ip_address(oe)}", 'Organization': f"AS{oa} {on}"})
                    break
        except Exception: continue
    return matches

def get_vpn_provider_networks(provider_name, networks):
    pn = provider_name.lower()
    matches = []
    for net, info in networks:
        if pn in info.lower():
            parts = info.split('|')
            matches.append({"VPN IP / CIDR": str(net), "Source": parts[0] if len(parts)>0 else "Unknown", "ASN": parts[1] if len(parts)>1 else "Unknown", "Organization": parts[2] if len(parts)>2 else "Unknown", "Provider": parts[3] if len(parts)>3 else "Unknown"})
    return matches

def get_clean_blocks(org_ranges, vpn_results):
    """Identifies which organization ranges do NOT contain any detected VPNs."""
    ranges_with_vpns = set(r['Organization Range'] for r in vpn_results)
    clean_blocks = []
    for start, end, asn, org, ver in org_ranges:
        range_str = f"{ipaddress.ip_address(start)} - {ipaddress.ip_address(end)}"
        if range_str not in ranges_with_vpns:
            clean_blocks.append({"Start IP": str(ipaddress.ip_address(start)), "End IP": str(ipaddress.ip_address(end)), "ASN": f"AS{asn}", "Organization": org, "Version": ver})
    return clean_blocks

def add_ranges_to_blocklist(ranges, label, is_org_tuples=False):
    """Adds a list of ranges to the blocklist."""
    new_entries = {}
    count = 0
    if is_org_tuples:
        for item in ranges:
            try:
                start, end = item[0], item[1]
                cidrs = ipaddress.summarize_address_range(ipaddress.ip_address(start), ipaddress.ip_address(end))
                for cidr in cidrs:
                    new_entries[str(cidr)] = f"ASN-BLOCK|{label}"
                    count += 1
            except Exception: continue
    else:
        for item in ranges:
            item = item.strip()
            if not item: continue
            try:
                if '-' in item:
                    parts = item.split('-')
                    cidrs = ipaddress.summarize_address_range(ipaddress.ip_address(parts[0].strip()), ipaddress.ip_address(parts[1].strip()))
                    for cidr in cidrs:
                        new_entries[str(cidr)] = f"MANUAL-BLOCK|{label}"
                        count += 1
                else:
                    net = ipaddress.ip_network(item, strict=False)
                    new_entries[str(net)] = f"MANUAL-BLOCK|{label}"
                    count += 1
            except Exception: continue
    if new_entries:
        append_to_cache(new_entries)
    return count

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python vpn_checker.py <IP_Address> [refresh]")
        print("Add 'refresh' to update databases manually.")
        sys.exit(1)

    # Simple CLI argument parsing
    target = None
    should_refresh = False
    
    # Check if cache file exists; if not, force refresh
    if not os.path.exists(CACHE_FILE):
        print(f"[!] Cache file not found at {CACHE_FILE}.")
        print("[!] Auto-triggering data refresh to populate lists...")
        should_refresh = True
    
    # Check args for manual refresh override
    for arg in sys.argv[1:]:
        if arg.lower() == "refresh":
            should_refresh = True
        else:
            target = arg

    if should_refresh:
        refresh_cache()
        # Reload after refresh
        cached_data = load_cached_ips()
        nets = load_networks_from_cache(cached_data)
        asn_data = load_asn_db()
    else:
        # Quietly load data
        cached_data = load_cached_ips()
        nets = load_networks_from_cache(cached_data)
        asn_data = load_asn_db()

    if target:
        # Perform Check
        is_threat, info, asn_org = is_vpn_ip(target, nets, asn_db=asn_data)
        
        # --- FINAL OUTPUT FORMAT ---
        print("-" * 50)
        print(f"Target IP: {target}")
        print("-" * 50)
        
        if is_threat:
            print(f"🚨 STATUS: THREAT DETECTED")
            print(f"ℹ️  INFO:   {info}")
        elif is_threat is None:
            print(f"⚠️ STATUS: INVALID INPUT")
            print(f"ℹ️  INFO:   {info}")
        else:
            print(f"✅ STATUS: CLEAN")
            print(f"ℹ️  INFO:   {info}")
        
        if asn_org:
            print(f"🏢 ASN:    {asn_org}")
            
        print("-" * 50)
    else:
        if not should_refresh:
            print("[!] Please provide an IP address to check.")
