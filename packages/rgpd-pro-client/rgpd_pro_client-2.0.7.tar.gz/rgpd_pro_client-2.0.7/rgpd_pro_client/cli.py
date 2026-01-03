#!/usr/bin/env python3
"""
RGPD_PRO - Remote CLI Client
Connect to RGPD_PRO API server to run remote scans
"""

import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import requests


def print_banner():
    """Display ASCII banner"""
    print("\n" + "=" * 80)
    print("🛡️  RGPD_PRO - Remote GDPR Compliance Scanner")
    print("=" * 80 + "\n")


def print_menu(title: str, options: list, show_details: bool = False) -> int:
    """Display a numbered menu and get user choice"""
    print(f"\n📋 {title}")
    print("-" * 80)

    for i, option in enumerate(options, 1):
        if isinstance(option, dict):
            if show_details:
                label = option.get("label", "")
                description = option.get("description", "")
                print(f"{i:2}. {label}")
                if description:
                    print(f"    → {description}")
            else:
                print(f"{i:2}. {option.get('label', option.get('key', ''))}")
        else:
            print(f"{i:2}. {option}")

    print("-" * 80)

    while True:
        try:
            choice = input(f"Choose option (1-{len(options)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return idx
            print(
                f"❌ Invalid choice. Please enter a number between 1 and {len(options)}")
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\n\n⚠️  Cancelled by user")
            sys.exit(0)


def get_url_input() -> str:
    """Get and validate URL from user"""
    print("\n🌐 Target Website")
    print("-" * 80)

    while True:
        try:
            url = input(
                "Enter URL to scan (e.g., https://example.com): ").strip()

            if not url:
                print("❌ URL cannot be empty")
                continue

            # Add https:// if missing
            if not url.startswith(("http://", "https://")):
                url = f"https://{url}"

            # Validate URL
            parsed = urlparse(url)
            if not parsed.netloc:
                print(f"❌ Invalid URL: {url}")
                continue

            return url

        except KeyboardInterrupt:
            print("\n\n⚠️  Cancelled by user")
            sys.exit(0)


def get_api_url() -> str:
    """Get API server URL"""
    print("\n🌐 API Server")
    print("-" * 80)

    # Production server - change to your domain if you have one
    default_url = "http://65.108.59.188:8000"
    url = default_url
    return url.rstrip("/")


def display_summary(config: dict, api_url: str):
    """Display scan configuration summary"""
    print("\n" + "=" * 80)
    print("📊 SCAN CONFIGURATION SUMMARY")
    print("=" * 80)
    print(f"\n🌐 API Server:       {api_url}")
    print(f"🎯 Target URL:       {config['url']}")
    print(f"💰 Revenue:          {config['revenue_bracket']}")
    print(f"👥 Employees:        {config['employee_bracket']}")
    print(f"🏢 Sector:           {config['sector']}")
    print("=" * 80 + "\n")


def wait_for_completion(api_url: str, scan_id: str) -> dict:
    """Poll API until scan completes with detailed progress tracking"""
    print("\n⏳ Scan in progress...\n")

    status_url = f"{api_url}/scans/{scan_id}"
    
    # Phase mapping basé sur les vrais logs
    PHASES = {
        0: "🚀 Initialisation...",
        5: "🔵 Navigation & Pre-Consent",
        15: "🍪 Détection des cookies",
        25: "🕵️  Analyse des trackers",
        35: "🎭 Détection CMP",
        45: "✅ Test de consentement",
        55: "🔬 Analyse avancée",
        65: "💰 Calcul du risque financier",
        75: "🤖 Génération insights IA",
        90: "📦 Génération du rapport",
        100: "✅ Scan terminé"
    }
    
    last_phase = -1
    start_time = time.time()

    while True:
        try:
            response = requests.get(status_url, timeout=120)
            response.raise_for_status()
            status = response.json()
            
            progress = status.get("progress", 0)
            
            # Trouver la phase actuelle
            current_phase_pct = 0
            current_phase_text = "En cours..."
            for pct in sorted(PHASES.keys()):
                if progress >= pct:
                    current_phase_pct = pct
                    current_phase_text = PHASES[pct]
            
            # Afficher la phase uniquement si elle change
            if current_phase_pct != last_phase and current_phase_pct > 0:
                elapsed = int(time.time() - start_time)
                print(f"\n{current_phase_text} [{elapsed}s]")
                last_phase = current_phase_pct
            
            # Barre de progression
            bar_length = 50
            filled = int(bar_length * progress / 100)
            bar = "█" * filled + "░" * (bar_length - filled)
            print(f"\r[{bar}] {progress}%", end="", flush=True)

            # Check status
            if status["status"] == "completed":
                elapsed = int(time.time() - start_time)
                print(f"\n\n✅ Scan completed in {elapsed}s!")
                return status

            elif status["status"] == "failed":
                print(f"\n\n❌ Scan failed: {status.get('error', 'Unknown error')}")
                return status

            # Wait before next poll
            time.sleep(2)

        except requests.exceptions.RequestException as e:
            print(f"\n\n❌ Error polling status: {e}")
            return None
        except KeyboardInterrupt:
            print("\n\n⚠️  Monitoring interrupted by user")
            print(f"ℹ️  Scan is still running on server. Check status: {status_url}")
            sys.exit(130)


def download_file(url: str, filename: str) -> bool:
    """Download file from URL"""
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        output_dir = Path("downloads")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / filename

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"   ✅ Downloaded: {output_path.resolve()}")
        return True

    except Exception as e:
        print(f"   ❌ Download failed: {e}")
        return False


def display_results(api_url: str, status: dict):
    """Display scan results with download links"""
    print("\n" + "=" * 80)
    print("📊 SCAN RESULTS")
    print("=" * 80)

    scan_id = status["scan_id"]

    # HTML Report
    if status.get("html_url"):
        html_url = f"{api_url}{status['html_url']}"
        print(f"\n📄 HTML Report:")
        print(f"   {html_url}")

    # Evidence ZIP
    if status.get("zip_url"):
        zip_url = f"{api_url}{status['zip_url']}"
        print(f"\n📦 Evidence Package (ZIP):")
        print(f"   {zip_url}")

    # Ask if user wants to download
    print("\n" + "=" * 80)
    try:
        download = input("\nDownload files now? (Y/n): ").strip().lower()
        if not download or download == "y":
            print("\n📥 Downloading files...\n")

            if status.get("html_url"):
                html_url = f"{api_url}{status['html_url']}"
                download_file(html_url, f"report_{scan_id[:8]}.html")

            if status.get("zip_url"):
                zip_url = f"{api_url}{status['zip_url']}"
                download_file(zip_url, f"evidence_{scan_id[:8]}.zip")

    except KeyboardInterrupt:
        print("\n\n⚠️  Download cancelled")

    print("\n" + "=" * 80 + "\n")


def main():
    """Main CLI entry point"""
    print_banner()

    # Get API URL
    api_url = get_api_url()

    # Test connection
    try:
        response = requests.get(f"{api_url}/health", timeout=10)
        response.raise_for_status()
        print("✅ Connected to API server")
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API server: {e}")
        print("ℹ️  Make sure the server is running: python api_server.py")
        return 1

    # Fetch configuration from API
    try:
        sectors_resp = requests.get(f"{api_url}/config/sectors").json()
        revenue_resp = requests.get(
            f"{api_url}/config/revenue-brackets").json()
        employee_resp = requests.get(
            f"{api_url}/config/employee-brackets").json()
    except Exception as e:
        print(f"❌ Error fetching configuration: {e}")
        return 1

    # Step 1: Get URL
    url = get_url_input()

    # Step 2: Choose revenue bracket
    revenue_idx = print_menu(
        "Select Annual Revenue Bracket", revenue_resp["brackets"], show_details=True
    )
    revenue_key = revenue_resp["brackets"][revenue_idx]["key"]

    # Step 3: Choose employee bracket
    employee_idx = print_menu(
        "Select Employee Count Bracket", employee_resp["brackets"], show_details=True
    )
    employee_key = employee_resp["brackets"][employee_idx]["key"]

    # Step 4: Choose sector
    sector_idx = print_menu(
        "Select Industry Sector", sectors_resp["sectors"], show_details=True
    )
    sector_key = sectors_resp["sectors"][sector_idx]["key"]

    # Build config
    config = {
        "url": url,
        "revenue_bracket": revenue_key,
        "employee_bracket": employee_key,
        "sector": sector_key,
    }

    # Display summary
    display_summary(config, api_url)

    # Confirm before scanning
    try:
        confirm = input("Start remote scan? (Y/n): ").strip().lower()
        if confirm and confirm != "y":
            print("❌ Scan cancelled")
            return 1
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        return 130

    # Submit scan
    try:
        print("\n🚀 Submitting scan to server...")
        response = requests.post(f"{api_url}/scans", json=config, timeout=30)
        response.raise_for_status()
        result = response.json()

        scan_id = result["scan_id"]
        print(f"✅ Scan created: {scan_id}")

        # Wait for completion
        status = wait_for_completion(api_url, scan_id)

        if status and status["status"] == "completed":
            display_results(api_url, status)
            return 0
        else:
            return 1

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error submitting scan: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        return 130


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
