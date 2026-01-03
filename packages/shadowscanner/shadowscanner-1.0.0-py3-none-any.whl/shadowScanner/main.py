#!/usr/bin/env python3

import os
import re
import json
import time
import logging
import argparse
import requests
import urllib3
from tqdm import tqdm
from wakepy import keep
from datetime import datetime
from typing import List, Dict, Optional
import shadowScanner.helpers as HELPERS
import shadowScanner.globals as GLOBALS
from requests.adapters import HTTPAdapter
from urllib.parse import urlparse, urlunparse
from shadowScanner.validation import validate_args
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger()

# if This is not done every single request will output something when verbosity is high
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

# To silence some specific messages
logging.getLogger("charset_normalizer").setLevel(logging.WARNING)


class TargetFinder:
    def __init__(
        self,
        hackerone_key: Optional[str],
        use_subdomains: bool,
        target_path: str,
        max_threads: int,
        success_status_codes: List[int],
        exclude_content: List[str],
        include_content: List[str],
    ):
        self.hackerone_key = hackerone_key
        self.use_subdomains = use_subdomains
        self.target_path = (
            target_path if target_path.startswith("/") else f"/{target_path}"
        )
        self.max_threads = max_threads
        self.success_status_codes = success_status_codes
        self.exclude_content = [s.lower() for s in (exclude_content or [])]
        self.include_content = [s.lower() for s in (include_content or [])]

        self.session = requests.Session()
        adapter = HTTPAdapter(
            pool_connections=self.max_threads,
            pool_maxsize=self.max_threads,
            max_retries=0
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def fetch_hackerone_programs(self) -> List[Dict]:
        if not self.hackerone_key:
            return []

        spinner = HELPERS.Spinner("Fetching HackerOne programs metadata...")
        with spinner:
            programs = []
            metadata = []
            page = 1

            username, token = HELPERS.split_hackerone_key(self.hackerone_key)

            while True:
                try:
                    url = f"https://api.hackerone.com/v1/hackers/programs"
                    params = {"page[number]": page, "page[size]": 100}

                    response = self.session.get(
                        url,
                        auth=(username, token),
                        headers={"Accept": "application/json"},
                        params=params,
                        timeout=30,
                    )

                    if response.status_code != 200:
                        logger.error(f"\rHackerOne API error: {response.status_code}")
                        logger.error(f"\rResponse: {response.text[:500]}")
                        break

                    data = response.json()
                    batch = data.get("data", [])
                    metadata.extend(batch)

                    page += 1
                    time.sleep(0.1)

                    if len(batch) < 100:
                        break

                except Exception as e:
                    logger.error(f"\rError fetching HackerOne programs metadata: {e}")
                    time.sleep(5)
                    break

            num_programs = len(metadata)
            for i, program in enumerate(metadata):
                try:
                    handle = program["attributes"]["handle"]
                    spinner.updateMessage(f"Fetching programs data {i}/{num_programs}")
                    scope_response = self.session.get(
                        f"https://api.hackerone.com/v1/hackers/programs/{handle}",
                        auth=(username, token),
                        headers={"Accept": "application/json"},
                        timeout=30,
                    )

                    if scope_response.status_code == 200:
                        scope_data = scope_response.json()
                        programs.append(
                            {
                                "platform": "hackerone",
                                "name": program["attributes"]["name"],
                                "handle": handle,
                                "url": f"https://hackerone.com/{handle}",
                                "data": scope_data,
                            }
                        )
                except Exception as e:
                    logger.warning(f"\rError fetching program details: {e}")

        return programs

    def fetch_bugcrowd_programs(self) -> List[Dict]:
        """
        Fetches Bugcrowd programs from the community-maintained list
        instead of the official API.
        """
        logger.info("Fetching BugCrowd programs from community data...")
        programs = []

        try:
            url = "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/main/data/bugcrowd_data.json"
            response = self.session.get(url, timeout=30)

            if response.status_code == 200:
                data = response.json()

                for program in data:
                    programs.append(
                        {
                            "platform": "bugcrowd",
                            "name": program.get("name"),
                            "code": program.get("url").split("/")[-1],  #
                            "url": program.get("url"),
                            "data": {
                                "targets": program.get("targets", {}).get(
                                    "in_scope", []
                                )
                            },
                        }
                    )

            logger.info(f"Found {len(programs)} BugCrowd programs")

        except Exception as e:
            logger.error(f"Error fetching community data: {e}")

        return programs


    def fetch_intigriti_programs(self) -> List[Dict]:
        """
        Fetches Intigriti programs from the community-maintained list.
        """
        logger.info("Fetching Intigriti programs from community data...")
        programs = []

        try:
            url = "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/main/data/intigriti_data.json"
            response = self.session.get(url, timeout=30)

            if response.status_code == 200:
                data = response.json()

                for program in data:
                    programs.append(
                        {
                            "platform": "intigriti",
                            "name": program.get("name"),
                            "handle": program.get("handle"),
                            "url": program.get("url"),
                            "data": {
                                "targets": program.get("targets", {}).get("in_scope", [])
                            },
                        }
                    )

            logger.info(f"Found {len(programs)} Intigriti programs")

        except Exception as e:
            logger.error(f"Error fetching Intigriti data: {e}")

        return programs

    def extract_targets(self, program: Dict) -> List[str]:
        targets = []
        platform = program.get("platform", "unknown")

        if platform == "hackerone":
            try:
                relationships = program["data"].get("relationships", {})
                structured_scopes = relationships.get("structured_scopes", {}).get(
                    "data", []
                )

                for scope in structured_scopes:
                    attrs = scope.get("attributes", {})
                    if not attrs.get("eligible_for_bounty", True):
                        continue

                    asset_type = attrs.get("asset_type", "")
                    asset_identifier = attrs.get("asset_identifier", "")

                    if asset_type in ["URL", "WILDCARD"]:
                        if asset_type == "WILDCARD":
                            if self.use_subdomains:
                                targets.append(asset_identifier)
                            else:
                                clean_domain = asset_identifier.replace("*.", "")
                                targets.append(HELPERS.add_https_prefix(clean_domain))
                        else:
                            targets.append(HELPERS.add_https_prefix(asset_identifier))
            except Exception as e:
                logger.warning(f"Error extracting HackerOne targets: {e}")
        elif platform == "bugcrowd":
            try:
                for target in program["data"].get("targets", []):
                    target_name = target.get("uri") or target.get("name")

                    if not target_name:
                        continue

                    if "http" in target_name.lower() or "." in target_name:
                        if "*" in target_name:
                            if self.use_subdomains:
                                targets.append(target_name)
                            else:
                                clean_domain = target_name.replace("*.", "")
                                targets.append(HELPERS.add_https_prefix(clean_domain))
                        else:
                            targets.append(HELPERS.add_https_prefix(target_name))
            except Exception as e:
                logger.warning(f"Error extracting BugCrowd targets: {e}")

        elif platform == "intigriti":
            try:
                raw_targets = program["data"].get("targets", [])
                
                for target in raw_targets:
                    t_type = target.get("type", "")
                    if not t_type:
                        continue
                    
                    t_type = t_type.lower()
                    endpoint = target.get("endpoint", "")
                    
                    if t_type == "wildcard":
                        if self.use_subdomains:
                            targets.append(endpoint)
                        else:
                            clean = endpoint.replace("*.", "")
                            targets.append(HELPERS.add_https_prefix(clean))
                    elif t_type == "url":
                        targets.append(HELPERS.add_https_prefix(endpoint))
                            
            except Exception as e:
                logger.warning(f"Error extracting Intigriti targets: {e}")

        return targets


    def save_targets_list(self, urls: set[str]):
        """Saves the fully enumerated list of URLs to disk."""
        data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "urls": sorted(urls)
        }
        with open(GLOBALS.TARGETS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved {len(urls)} resolved targets to {GLOBALS.TARGETS_FILE}")

    def load_targets_list(self) -> Optional[set[str]]:
        """Loads the fully enumerated list if it exists."""
        if not GLOBALS.TARGETS_FILE.exists():
            return None

        try:
            with open(GLOBALS.TARGETS_FILE, 'r') as f:
                data = json.load(f)
            
            print(f"\n[!] Found cached target list from {data.get('timestamp')}")
            print(f"    Contains {len(data.get('urls', []))} pre-resolved URLs.")
            
            while True:
                choice = input("    Skip generation and use this list? (y/n): ").strip().lower()
                if choice in ['y', 'yes']:
                    return set(data.get("urls", {}))
                elif choice in ['n', 'no']:
                    return None
        except Exception as e:
            logger.warning(f"Could not load targets file: {e}")
            return None

    def save_checkpoint(self, scanned_urls: set, findings: List[Dict]):
        """Saves progress and findings."""
        data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "target_path": self.target_path,
            "scanned_urls": list(scanned_urls),
            "findings": findings
        }
        
        temp = GLOBALS.CHECKPOINT_FILE.with_suffix('.tmp')
        with open(temp, 'w') as f:
            json.dump(data, f)
        temp.replace(GLOBALS.CHECKPOINT_FILE)

    def load_checkpoint(self) -> tuple[set, List[Dict]]:
        """Returns (set_of_scanned_urls, list_of_findings)"""
        if not GLOBALS.CHECKPOINT_FILE.exists():
            return set(), []

        try:
            with open(GLOBALS.CHECKPOINT_FILE, 'r') as f:
                data = json.load(f)

            if data.get("target_path") != self.target_path:
                return set(), []

            print(f"\n[!] Found scan checkpoint.")
            print(f"    Already scanned: {len(data.get('scanned_urls', []))} URLs")
            print(f"    Found so far: {len(data.get('findings', []))} issues")
            
            if input("    Resume scan? (y/n): ").lower() in ['y', 'yes']:
                return set(data.get("scanned_urls", [])), data.get("findings", [])
        except Exception:
            pass
        return set(), []


    def enumerate_subdomains(self, wildcard: str) -> List[str]:
        subdomains = []
        domains = re.findall(
            r"\*[\w\.-]*?\.([\w\.-]+[a-z]{2,})", wildcard, re.IGNORECASE
        )

        if not domains:
            logger.info(
                f"  No wildcard domain found in target string: {wildcard[:30]}..."
            )
            return []

        unique_domains = set(domains)

        for domain in unique_domains:
            logger.info(
                f"Enumerating subdomains for {domain} via certificate transparency..."
            )

            try:
                response = self.session.get(
                    f"https://crt.sh/?q=%.{domain}&output=json", timeout=30
                )

                if response.status_code == 200:
                    try:
                        certs = response.json()
                        found_domains = set()

                        for cert in certs:
                            name_value = cert.get("name_value", "")
                            for subdomain in name_value.split("\n"):
                                subdomain = subdomain.strip()
                                if subdomain and "*" not in subdomain:
                                    found_domains.add(subdomain)

                        for subdomain in list(found_domains):
                            subdomains.append(f"https://{subdomain}")

                    except json.JSONDecodeError:
                        logger.warning(f"crt.sh returned invalid JSON for {domain}")

            except Exception as e:
                logger.warning(f"Error enumerating subdomains for {domain}: {e}")

        if not subdomains:
            for domain in unique_domains:
                subdomains.append(f"https://{domain}")

        return subdomains

    def load_existing_programs(self) -> List[Dict]:
        programs = HELPERS.get_from_cache("programs")

        if not programs:
            return []

        timestamp = programs.get("timestamp")
        data = programs.get("data")

        try:
            print(f"\nFound existing program data:")
            print(f"  Collected: {timestamp}")
            print(f"  Programs: {len(data)}")

            while True:
                response = input("\nUse this data? (y/n): ").strip().lower()
                if response in ["y", "yes"]:
                    logger.info(f"Using existing program data from {timestamp}")
                    return data
                elif response in ["n", "no"]:
                    logger.info("Will fetch fresh program data")
                    return []
                else:
                    print("Please enter 'y' or 'n'")

        except Exception as e:
            logger.warning(f"Error reading existing program file: {e}")
            return []

    def check_path(self, url: str) -> Optional[Dict]:
        parsed = urlparse(url)
        clean_path = parsed.path.replace("*", "").rstrip("/")
        base_url = urlunparse((parsed.scheme, parsed.netloc, clean_path, "", "", ""))

        full_url = f"{base_url}{self.target_path}"

        try:
            response = self.session.get(
                full_url, timeout=(3, 5), verify=False, allow_redirects=True,
            )

            if response.status_code in self.success_status_codes:
                content = response.text
                content_lower = content.lower()

                if self.exclude_content:
                    if any(
                        exclusion in content_lower for exclusion in self.exclude_content
                    ):
                        return None

                if self.include_content:
                    if not (
                        any(
                            [
                                inclusion in content_lower
                                for inclusion in self.include_content
                            ]
                        )
                    ):
                        return None

                return {
                    "url": full_url,
                    "vulnerability": f"Exposed {self.target_path}",
                    "status": response.status_code,
                    "length": len(response.content),
                    "content": content,
                }

        except requests.RequestException:
            pass

        return None

    def process_program(self, program: Dict) -> List[str]:
        raw_targets = self.extract_targets(program)
        final_urls = []

        for t in raw_targets:
            if "*" in t and self.use_subdomains:
                subdomains = self.enumerate_subdomains(t)
                final_urls.extend(subdomains)
            else:
                final_urls.append(t)

        return final_urls

    def run(self, use_hackerone: bool, use_bugcrowd: bool, use_intigriti: bool):
        with keep.running():
            all_urls = self.load_targets_list()

            if all_urls is None:
                logger.info("Generating fresh target list (Fetching APIs + Enumerating Subdomains)...")
                
                all_programs = self.load_existing_programs()
                if not all_programs:
                    if use_hackerone: all_programs.extend(self.fetch_hackerone_programs())
                    if use_bugcrowd: all_programs.extend(self.fetch_bugcrowd_programs())
                    if use_intigriti: all_programs.extend(self.fetch_intigriti_programs())
                    
                    HELPERS.store_in_cache("programs", {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "data": all_programs
                    })

                logger.info(f"Enumerating subdomains for {len(all_programs)} programs...")
                generated_urls = []
                for prog in tqdm(all_programs, desc="Processing Programs"):
                    generated_urls.extend(self.process_program(prog))
                
                all_urls = set(generated_urls)
                
                self.save_targets_list(all_urls)


            scanned_urls, current_findings = self.load_checkpoint()
            
            targets_to_scan = list(all_urls - scanned_urls)
            
            logger.info(f"Total Targets: {len(all_urls)}")
            if scanned_urls:
                logger.info(f"Already Scanned: {len(scanned_urls)}")
                logger.info(f"Remaining: {len(targets_to_scan)}")

            if not targets_to_scan:
                logger.info("No targets remaining.")
                return
            
            save_interval = 1000
            processed_since_save = 0
            
            try:
                with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
                    future_to_url = {
                        executor.submit(self.check_path, url): url 
                        for url in targets_to_scan
                    }

                    for future in tqdm(as_completed(future_to_url), total=len(targets_to_scan), ncols=100, desc="Scanning"):
                        url = future_to_url[future]

                        scanned_urls.add(url)
                        processed_since_save += 1

                        try:
                            result = future.result()
                            if result:
                                current_findings.append(result)
                                
                                msg = f" [FOUND] {result['url']} ({result['status']})"
                                tqdm.write(f"\033[41m{msg}\033[0m")
                                
                                with open("findings.txt", "a") as f:
                                    f.write(f"{json.dumps(result)}\n")
                        except Exception:
                            pass

                        if processed_since_save >= save_interval:
                            self.save_checkpoint(scanned_urls, current_findings)
                            processed_since_save = 0

                logger.info(f"Scan finished. Total findings: {len(current_findings)}")
                
                with open(GLOBALS.FINDINGS_FILE, 'w') as f:
                    json.dump(current_findings, f, indent=2)
                
                if GLOBALS.CHECKPOINT_FILE.exists():
                    os.remove(GLOBALS.CHECKPOINT_FILE)

            except KeyboardInterrupt:
                tqdm.write("\n[!] Scan Interrupted. Saving state...")
                self.save_checkpoint(scanned_urls, current_findings)
                tqdm.write("[!] State saved. You can resume later.")
                raise


def main():
    parser = argparse.ArgumentParser(
        description="A scanner that could be used to discover certain files or paths on bug bounty programs."
    )

    parser.add_argument(
        "--hackerone", "-H", action="store", help="Set the HackerOne api key"
    )

    parser.add_argument(
        "--status-codes",
        "-sc",
        type=int,
        nargs="*",
        default=[200, 206],
        help="Status Codes that indicate a finding",
    )

    parser.add_argument(
        "--subdomains",
        action="store_true",
        help="Enumerate subdomains from certificate transparency logs for wildcards",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        help="Enable verbose output showing detailed analysis of each target",
    )

    parser.add_argument(
        "--path",
        "-p",
        default="/",
        help="Path to scan for (default: /)",
    )

    parser.add_argument(
        "--threads",
        "-t",
        type=int,
        default=20,
        help="Number of concurrent threads (default: 20)",
    )

    parser.add_argument(
        "--exclude-content",
        "-e",
        nargs="*",
        default=[],
        help="List of strings that, if found in the response, mark the result as a false positive (case-insensitive).",
    )

    parser.add_argument(
        "--include-content",
        "-i",
        nargs="*",
        default=[],
        help="List of strings that MUST be present in the response for it to be valid (case-insensitive).",
    )

    args = parser.parse_args()
    validate_args(args)

    HELPERS.configure_logging(args.verbose)

    if args.hackerone:
        hackerone_key = args.hackerone
        HELPERS.store_in_cache("hackerone_api_key", hackerone_key)
    else:
        hackerone_key = HELPERS.get_from_cache("hackerone_api_key")

    use_hackerone = True
    use_bugcrowd = True
    use_intigriti = True

    if not hackerone_key:
        logging.warning("No HackerOne key found. Skipping HackerOne.")

    finder = TargetFinder(
        hackerone_key=hackerone_key,
        use_subdomains=args.subdomains,
        target_path=args.path,
        max_threads=args.threads,
        success_status_codes=args.status_codes,
        exclude_content=args.exclude_content,
        include_content=args.include_content,
    )

    finder.run(use_hackerone=use_hackerone, use_bugcrowd=use_bugcrowd, use_intigriti=use_intigriti)


if __name__ == "__main__":
    main()
