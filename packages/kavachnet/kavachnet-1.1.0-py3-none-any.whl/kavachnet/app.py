import streamlit as st
import json
import os
import sys
import time
from pathlib import Path
import ipaddress

# --- PATH & IMPORT CONFIGURATION ---
CURRENT_DIR = Path(__file__).parent

# Ensure the package directory is on sys.path for local imports
if str(CURRENT_DIR) not in sys.path:
    sys.path.append(str(CURRENT_DIR))

# Try importing the logic
try:
    from vpn_checker import (
        refresh_cache, load_networks_from_cache, is_vpn_ip, 
        load_cached_ips, CACHE_FILE, load_asn_db,
        get_org_ranges, check_vpns_in_ranges, format_org_ranges,
        calculate_ip_count, get_vpn_provider_networks,
        get_clean_blocks, add_ranges_to_blocklist
    )
except ImportError as e:
    st.error(f"Critical Error: Could not import vpn_checker. Details: {e}")
    st.stop()

# path to the read-only sources file for the sidebar
SOURCES_JSON = CURRENT_DIR / "data" / "vpn_sources.json"

# ────────────────────────────────────────────────────────────────
# Streamlit Page Config
st.set_page_config(
    page_title="KAVACHNET",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ────────────────────────────────────────────────────────────────
# Custom Styling
st.markdown("""
<style>
    .big-font {font-size:45px !important; font-weight: bold; text-align: center; color: #FF9933; margin-bottom: 0px;}
    .sub-font {font-size:20px !important; text-align: center; color: #666; margin-bottom: 30px;}
    .stButton>button {width: 100%; border-radius: 5px; height: 3em; background-color: #FF4B4B; color: white;}
    .reportview-container .main .block-container{ padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────
# Header
st.markdown('<p class="big-font">KAVACHNET</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-font">VPN & Proxy Detection System by Rishabh KRW</p>', unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────
# CACHING LOGIC
@st.cache_resource(show_spinner=False)
def load_data_into_memory():
    """Loads the processed networks AND the ASN database into memory efficiently."""
    cached_dict = load_cached_ips()
    networks = load_networks_from_cache(cached_dict)
    asn_db = load_asn_db()
    return networks, asn_db

# ────────────────────────────────────────────────────────────────
# Sidebar
with st.sidebar:
    st.header("🛡️ System Control")
    
    networks, asn_db = load_data_into_memory()
    
    # Status Metrics
    st.metric("Active Signatures", f"{len(networks):,}", help="Total unique IP/CIDR entries in your detection engine.")
    st.metric("ASN Database", "Active" if asn_db else "Inactive")
    
    st.divider()
    
    # Update Button
    if st.button("🔄 Update Database"):
        with st.spinner("Fetching latest VPN IP lists..."):
            try:
                _, new_count = refresh_cache()
                st.cache_resource.clear()
                st.success(f"Updated! {new_count} new entries.")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Update failed: {e}")

    # Instructional Panel
    st.warning("⚠️ **FIRST TIME USAGE**: You must update the database below to download the latest threat intelligence before the system can detect VPNs.")
    st.info("🗓️ **Weekly Update**: Keep your detection engine current by updating the database weekly.")
    
    st.divider()
    st.markdown("### 🌍 Active Sources")
    if SOURCES_JSON.exists():
        try:
            with open(SOURCES_JSON, 'r') as f:
                data = json.load(f)
            for category, urls in data.items():
                with st.expander(f"{category} ({len(urls)})"):
                    for url in urls:
                        display_url = url.split('/')[2] if '//' in url else url
                        st.markdown(f"• [{display_url}]({url})")
        except Exception: pass
    
    st.divider()
    st.caption(f"Cache Path: {CACHE_FILE}")
    st.caption("Developed by Rishabh KRW")

# ────────────────────────────────────────────────────────────────
# Main Interface
tab1, tab2, tab3 = st.tabs(["🔍 IP Inspector", "🏢 Infrastructure Analyzer", "🛡️ VPN Provider Search"])

with tab1:
    st.subheader("🔍 Real-time IP Inspection")
    ip_input = st.text_input("Enter IP Address (v4/v6)", placeholder="e.g., 185.156.174.19", help="Supports CIDR and IP:Port formats")
    
    if st.button("🚀 Run Analysis"):
        if ip_input.strip():
            with st.spinner("Analyzing signatures..."):
                is_threat, info, asn_org = is_vpn_ip(ip_input, networks, asn_db=asn_db)
            
            if is_threat:
                st.error(f"### 🚨 THREAT DETECTED")
                st.markdown(f"**Verdict:** {info}")
                if asn_org: st.warning(f"🏢 **Organization:** {asn_org}")
            elif is_threat is None:
                st.warning(f"⚠️ {info}")
            else:
                st.success(f"### ✅ CLEAN IP")
                st.markdown(f"No match in known VPN/Proxy signature databases.")
                if asn_org: st.info(f"🏢 **Organization:** {asn_org}")
        else:
            st.warning("Please enter a valid IP address.")

with tab2:
    st.subheader("🏢 Infrastructure Analysis")
    st.markdown("Deep scan an organization's network to identify potential VPN hosting blocks.")
    
    org_input = st.text_input("Enter Organization Name or ASN", placeholder="e.g. Amazon or AS9009")
    if st.button("📊 Scan Infrastructure"):
        if org_input:
            with st.spinner("Loading network blocks..."):
                org_ranges = get_org_ranges(org_input, asn_db)
            
            if not org_ranges:
                st.warning("No network blocks discovered.")
            else:
                total_ips = sum(calculate_ip_count(s, e) for s, e, a, o, v in org_ranges)
                st.info(f"Found {len(org_ranges)} network blocks (Total IPs: {total_ips:,})")
                
                # Cross-reference
                with st.spinner("Cross-referencing signatures..."):
                    results = check_vpns_in_ranges(org_ranges, networks)
                
                if results:
                    st.warning(f"Detected {len(results)} known VPN/Proxy signatures in this infrastructure.")
                    st.dataframe(results, width='stretch')
                else:
                    st.success("No active VPN signatures discovered in these ranges.")
                
                # Add to Blocklist Feature
                with st.expander("🛠️ Advanced: Manage Blocklist"):
                    st.error("🚨 **STRICT INSTRUCTION**: ONLY proceed if you are 100% certain this entire infrastructure is dedicated to VPN/Proxy use. Adding these ranges will permanently flag ALL associated IPs as a threat in your local engine.")
                    block_label = st.text_input("Blocklist Label", value=org_input)
                    if st.button("➕ Add All Ranges to Blocklist"):
                        count = add_ranges_to_blocklist(org_ranges, block_label, is_org_tuples=True)
                        st.success(f"Added {count} ranges as '{block_label}'. System will reload on next action.")
                        st.cache_resource.clear()
                
                with st.expander("🌐 View All Network Blocks"):
                    st.dataframe(format_org_ranges(org_ranges), width='stretch')

with tab3:
    st.subheader("🛡️ VPN Provider Intelligence")
    st.markdown("Search for all blocked signatures associated with a specific VPN provider.")
    
    provider_input = st.text_input("Enter VPN Provider Name", placeholder="e.g. NordVPN")
    if st.button("🔍 Search VPN Provider"):
        if provider_input:
            with st.spinner("Querying database..."):
                matches = get_vpn_provider_networks(provider_input, networks)
            
            if matches:
                st.success(f"Found {len(matches)} associated network blocks.")
                st.dataframe(matches, width='stretch')
            else:
                st.warning("No fingerprint matches found for this provider.")
