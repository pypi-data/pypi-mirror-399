#!/usr/bin/env python3
"""
VelocityCMDB Security Module - CVE Cache
=========================================

SQLite-based cache for NVD CVE data using direct API calls.
No nvdlib dependency - uses requests with proper URL encoding.

Usage:
    from nvd_cache import CVECache

    cache = CVECache("cve_cache.db")

    # Sync specific versions from your CMDB
    versions = [
        {"vendor": "juniper", "product": "junos", "version": "14.1x53-d35.3"},
        {"vendor": "arista", "product": "eos", "version": "4.23.3m"},
    ]
    cache.sync_versions(versions)

    # Fast local lookups
    cves = cache.get_cves_for_version("juniper", "junos", "14.1x53-d35.3")
"""

import sqlite3
import json
import logging
import time
import requests
from urllib.parse import quote
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# NVD API settings
NVD_BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
REQUEST_DELAY = 6.0  # seconds between requests (no API key)

# ============================================================================
# Database Schema
# ============================================================================

SCHEMA = """
-- CVE records from NVD
CREATE TABLE IF NOT EXISTS cve_records (
    cve_id TEXT PRIMARY KEY,
    description TEXT,
    severity TEXT,
    cvss_v2_score REAL,
    cvss_v2_vector TEXT,
    cvss_v3_score REAL,
    cvss_v3_vector TEXT,
    cwe_ids TEXT,
    published_date TEXT,
    last_modified TEXT,
    in_kev INTEGER DEFAULT 0,
    ref_urls TEXT,
    cached_at TEXT
);

-- CPE to CVE mappings (affected versions)
CREATE TABLE IF NOT EXISTS cpe_cve_mapping (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cve_id TEXT REFERENCES cve_records(cve_id),
    cpe_vendor TEXT,
    cpe_product TEXT,
    version_start TEXT,
    version_start_type TEXT,
    version_end TEXT,
    version_end_type TEXT,
    version_exact TEXT,
    vulnerable INTEGER DEFAULT 1,
    UNIQUE(cve_id, cpe_vendor, cpe_product, version_exact, version_start, version_end)
);

-- Track which versions have been synced
CREATE TABLE IF NOT EXISTS synced_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor TEXT,
    product TEXT,
    version TEXT,
    cve_count INTEGER,
    last_synced TEXT,
    UNIQUE(vendor, product, version)
);

-- Device vulnerability associations
CREATE TABLE IF NOT EXISTS device_vulnerabilities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT,
    device_name TEXT,
    vendor TEXT,
    os_version TEXT,
    cve_id TEXT REFERENCES cve_records(cve_id),
    match_type TEXT,
    first_detected TEXT,
    status TEXT DEFAULT 'open',
    notes TEXT,
    UNIQUE(device_id, cve_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_cve_severity ON cve_records(severity);
CREATE INDEX IF NOT EXISTS idx_cve_published ON cve_records(published_date);
CREATE INDEX IF NOT EXISTS idx_cpe_vendor_product ON cpe_cve_mapping(cpe_vendor, cpe_product);
CREATE INDEX IF NOT EXISTS idx_cpe_version ON cpe_cve_mapping(version_exact);
CREATE INDEX IF NOT EXISTS idx_synced_versions ON synced_versions(vendor, product, version);
"""


# ============================================================================
# NVD API Client (Direct Requests)
# ============================================================================

class NVDClient:
    """Direct NVD API client without nvdlib"""

    def __init__(self, delay: float = REQUEST_DELAY):
        self.delay = delay
        self._last_request = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Accept': 'application/json',
        })

    def _rate_limit(self):
        """Enforce rate limiting"""
        elapsed = time.time() - self._last_request
        if elapsed < self.delay:
            sleep_time = self.delay - elapsed
            logger.debug(f"Rate limiting: sleeping {sleep_time:.1f}s")
            time.sleep(sleep_time)
        self._last_request = time.time()

    def _build_cpe_url(self, vendor: str, product: str, version: str) -> str:
        """Build properly encoded NVD API URL for CPE query"""
        # Build CPE 2.3 string
        cpe = f"cpe:2.3:o:{vendor}:{product}:{version}:*:*:*:*:*:*:*"
        # URL encode the CPE
        encoded_cpe = quote(cpe, safe='')
        return f"{NVD_BASE_URL}?cpeName={encoded_cpe}"

    def get_cves_for_version(self, vendor: str, product: str, version: str) -> Dict[str, Any]:
        """
        Query NVD for CVEs affecting a specific version

        Returns dict with totalResults and list of CVE data
        """
        self._rate_limit()

        url = self._build_cpe_url(vendor.lower(), product.lower(), version.lower())
        logger.debug(f"Querying: {url[:80]}...")

        try:
            response = self.session.get(url, timeout=30)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                # Could be rate limited or invalid CPE
                logger.warning(f"404 for {vendor}:{product}:{version} - may be rate limited")
                return {"totalResults": 0, "vulnerabilities": []}
            else:
                logger.error(f"HTTP {response.status_code}: {response.text[:100]}")
                return {"totalResults": 0, "vulnerabilities": []}

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return {"totalResults": 0, "vulnerabilities": []}


# ============================================================================
# CVE Cache
# ============================================================================

class CVECache:
    """SQLite-based CVE cache with NVD sync"""

    def __init__(self, db_path: str = "cve_cache.db"):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
        self.nvd = NVDClient()
        logger.info(f"CVE cache initialized at {self.db_path}")

    def _init_schema(self):
        """Create tables"""
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def close(self):
        self.conn.close()

    # ========================================================================
    # Sync Methods
    # ========================================================================

    def sync_versions(self, versions: List[Dict[str, str]], force: bool = False) -> Dict[str, Any]:
        """
        Sync CVEs for a list of specific versions

        Args:
            versions: List of dicts with vendor, product, version keys
            force: If True, re-sync even if already cached

        Returns:
            Stats dict
        """
        stats = {
            "versions_processed": 0,
            "versions_skipped": 0,
            "cves_added": 0,
            "cves_updated": 0,
            "errors": [],
        }

        total = len(versions)

        for i, v in enumerate(versions, 1):
            vendor = v.get("vendor", "").lower()
            product = v.get("product", "").lower()
            version = v.get("version", "").lower()

            if not all([vendor, product, version]):
                continue

            # Check if already synced
            if not force and self._is_version_synced(vendor, product, version):
                logger.info(f"[{i}/{total}] Skipping {vendor}:{product}:{version} (already synced)")
                stats["versions_skipped"] += 1
                continue

            logger.info(f"[{i}/{total}] Syncing {vendor}:{product}:{version}...")

            try:
                result = self.nvd.get_cves_for_version(vendor, product, version)
                total_cves = result.get("totalResults", 0)

                logger.info(f"  Found {total_cves} CVEs")

                # Store CVEs
                for vuln in result.get("vulnerabilities", []):
                    cve_data = vuln.get("cve", {})
                    is_new = self._upsert_cve(cve_data, vendor, product, version)
                    if is_new:
                        stats["cves_added"] += 1
                    else:
                        stats["cves_updated"] += 1

                # Mark version as synced
                self._mark_version_synced(vendor, product, version, total_cves)
                stats["versions_processed"] += 1

                self.conn.commit()

            except Exception as e:
                logger.error(f"  Error: {e}")
                stats["errors"].append({
                    "version": f"{vendor}:{product}:{version}",
                    "error": str(e)
                })

        return stats

    def sync_from_cmdb_data(self, cmdb_versions: List[Dict]) -> Dict[str, Any]:
        """
        Sync CVEs for versions exported from VelocityCMDB

        Args:
            cmdb_versions: List of dicts with keys: vendor, os_version
                          (as exported from OS Versions page)
        """
        # Map CMDB vendor names to CPE vendor/product
        vendor_map = {
            'juniper networks': ('juniper', 'junos'),
            'juniper': ('juniper', 'junos'),
            'arista networks': ('arista', 'eos'),
            'arista': ('arista', 'eos'),
            'cisco systems': ('cisco', 'ios'),
            'cisco': ('cisco', 'ios'),
            'palo alto networks': ('paloaltonetworks', 'pan-os'),
            'fortinet': ('fortinet', 'fortios'),
        }

        versions = []
        for row in cmdb_versions:
            vendor_name = row.get('vendor', '').lower()
            os_version = row.get('os_version', '').lower()

            if vendor_name in vendor_map and os_version:
                cpe_vendor, cpe_product = vendor_map[vendor_name]
                versions.append({
                    'vendor': cpe_vendor,
                    'product': cpe_product,
                    'version': os_version,
                })

        logger.info(f"Syncing {len(versions)} unique versions from CMDB")
        return self.sync_versions(versions)

    def _is_version_synced(self, vendor: str, product: str, version: str) -> bool:
        """Check if version has been synced"""
        row = self.conn.execute(
            "SELECT id FROM synced_versions WHERE vendor=? AND product=? AND version=?",
            (vendor, product, version)
        ).fetchone()
        return row is not None

    def _mark_version_synced(self, vendor: str, product: str, version: str, cve_count: int):
        """Mark version as synced"""
        now = datetime.now(timezone.utc).isoformat()
        self.conn.execute("""
            INSERT OR REPLACE INTO synced_versions (vendor, product, version, cve_count, last_synced)
            VALUES (?, ?, ?, ?, ?)
        """, (vendor, product, version, cve_count, now))

    def _upsert_cve(self, cve_data: Dict, vendor: str, product: str, version: str) -> bool:
        """Insert or update CVE record. Returns True if new."""
        cve_id = cve_data.get("id", "")
        if not cve_id:
            return False

        # Check existing
        existing = self.conn.execute(
            "SELECT cve_id FROM cve_records WHERE cve_id = ?", (cve_id,)
        ).fetchone()

        # Extract description
        description = ""
        for desc in cve_data.get("descriptions", []):
            if desc.get("lang") == "en":
                description = desc.get("value", "")
                break

        # Extract CVSS scores
        metrics = cve_data.get("metrics", {})
        cvss_v3_score, cvss_v3_vector, severity = self._extract_cvss_v3(metrics)
        cvss_v2_score, cvss_v2_vector = self._extract_cvss_v2(metrics)

        # Extract CWE IDs
        cwe_ids = []
        for weakness in cve_data.get("weaknesses", []):
            for desc in weakness.get("description", []):
                if desc.get("value"):
                    cwe_ids.append(desc["value"])

        # Extract references
        ref_urls = [ref.get("url") for ref in cve_data.get("references", [])[:10]]

        now = datetime.now(timezone.utc).isoformat()

        if existing:
            self.conn.execute("""
                UPDATE cve_records SET
                    description=?, severity=?, cvss_v3_score=?, cvss_v3_vector=?,
                    cvss_v2_score=?, cvss_v2_vector=?, cwe_ids=?,
                    published_date=?, last_modified=?, ref_urls=?, cached_at=?
                WHERE cve_id=?
            """, (
                description, severity, cvss_v3_score, cvss_v3_vector,
                cvss_v2_score, cvss_v2_vector, json.dumps(cwe_ids),
                cve_data.get("published"), cve_data.get("lastModified"),
                json.dumps(ref_urls), now, cve_id
            ))
            return False
        else:
            self.conn.execute("""
                INSERT INTO cve_records (
                    cve_id, description, severity, cvss_v3_score, cvss_v3_vector,
                    cvss_v2_score, cvss_v2_vector, cwe_ids,
                    published_date, last_modified, ref_urls, cached_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cve_id, description, severity, cvss_v3_score, cvss_v3_vector,
                cvss_v2_score, cvss_v2_vector, json.dumps(cwe_ids),
                cve_data.get("published"), cve_data.get("lastModified"),
                json.dumps(ref_urls), now
            ))

            # Store CPE mapping
            self.conn.execute("""
                INSERT OR IGNORE INTO cpe_cve_mapping 
                (cve_id, cpe_vendor, cpe_product, version_exact, vulnerable)
                VALUES (?, ?, ?, ?, 1)
            """, (cve_id, vendor, product, version))

            return True

    def _extract_cvss_v3(self, metrics: Dict) -> tuple:
        """Extract CVSS v3.x score, vector, severity"""
        for key in ["cvssMetricV31", "cvssMetricV30"]:
            if key in metrics and metrics[key]:
                m = metrics[key][0]
                cvss = m.get("cvssData", {})
                return (
                    cvss.get("baseScore"),
                    cvss.get("vectorString"),
                    cvss.get("baseSeverity", "UNKNOWN")
                )
        return (None, None, "UNKNOWN")

    def _extract_cvss_v2(self, metrics: Dict) -> tuple:
        """Extract CVSS v2 score and vector"""
        if "cvssMetricV2" in metrics and metrics["cvssMetricV2"]:
            m = metrics["cvssMetricV2"][0]
            cvss = m.get("cvssData", {})
            return (cvss.get("baseScore"), cvss.get("vectorString"))
        return (None, None)

    # ========================================================================
    # Query Methods
    # ========================================================================

    def get_cves_for_version(self, vendor: str, product: str, version: str) -> List[Dict]:
        """Get cached CVEs for a specific version"""
        rows = self.conn.execute("""
            SELECT c.* FROM cve_records c
            JOIN cpe_cve_mapping m ON c.cve_id = m.cve_id
            WHERE m.cpe_vendor = ? AND m.cpe_product = ? AND m.version_exact = ?
            ORDER BY c.cvss_v3_score DESC NULLS LAST
        """, (vendor.lower(), product.lower(), version.lower())).fetchall()
        return [dict(row) for row in rows]

    def get_summary(self, vendor: str = None) -> Dict[str, Any]:
        """Get CVE summary statistics"""
        if vendor:
            rows = self.conn.execute("""
                SELECT severity, COUNT(*) as count FROM cve_records
                WHERE cve_id IN (SELECT cve_id FROM cpe_cve_mapping WHERE cpe_vendor = ?)
                GROUP BY severity
            """, (vendor.lower(),)).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT severity, COUNT(*) as count FROM cve_records GROUP BY severity"
            ).fetchall()

        summary = {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0}
        for row in rows:
            sev = (row["severity"] or "unknown").lower()
            summary["total"] += row["count"]
            if sev in summary:
                summary[sev] = row["count"]
        return summary

    def get_synced_versions(self) -> List[Dict]:
        """Get list of all synced versions"""
        rows = self.conn.execute(
            "SELECT * FROM synced_versions ORDER BY vendor, product, version"
        ).fetchall()
        return [dict(row) for row in rows]

    def get_version_report(self) -> List[Dict]:
        """Get CVE counts per synced version"""
        rows = self.conn.execute("""
            SELECT 
                sv.vendor, sv.product, sv.version, sv.cve_count,
                COUNT(CASE WHEN c.severity = 'CRITICAL' THEN 1 END) as critical,
                COUNT(CASE WHEN c.severity = 'HIGH' THEN 1 END) as high,
                COUNT(CASE WHEN c.severity = 'MEDIUM' THEN 1 END) as medium,
                COUNT(CASE WHEN c.severity = 'LOW' THEN 1 END) as low
            FROM synced_versions sv
            LEFT JOIN cpe_cve_mapping m ON sv.vendor = m.cpe_vendor 
                AND sv.product = m.cpe_product AND sv.version = m.version_exact
            LEFT JOIN cve_records c ON m.cve_id = c.cve_id
            GROUP BY sv.vendor, sv.product, sv.version
            ORDER BY sv.cve_count DESC
        """).fetchall()
        return [dict(row) for row in rows]


# ============================================================================
# CLI
# ============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description="CVE Cache Manager")
    parser.add_argument("--db", default="cve_cache.db", help="Database path")
    parser.add_argument("--sync-demo", action="store_true", help="Sync demo Kentik versions")
    parser.add_argument("--stats", action="store_true", help="Show cache statistics")
    parser.add_argument("--versions", action="store_true", help="Show synced versions")
    parser.add_argument("--report", action="store_true", help="Show version CVE report")
    parser.add_argument("--query", help="Query CVEs: vendor:product:version")
    parser.add_argument("--force", action="store_true", help="Force re-sync")

    args = parser.parse_args()
    cache = CVECache(args.db)

    try:
        if args.sync_demo:
            # Demo versions from VelocityCMDB screenshot
            demo_versions = [
                {"vendor": "arista", "product": "eos", "version": "4.33.1f"},
                {"vendor": "arista", "product": "eos", "version": "4.28.13m"},
                {"vendor": "arista", "product": "eos", "version": "4.23.3m"},
                {"vendor": "arista", "product": "eos", "version": "4.17.6m"},
                {"vendor": "juniper", "product": "junos", "version": "21.1r1.11"},
                {"vendor": "juniper", "product": "junos", "version": "14.1x53-d35.3"},
                {"vendor": "juniper", "product": "junos", "version": "23.2r1-s2.5"},
                {"vendor": "cisco", "product": "ios", "version": "12.2\\(54\\)sg1"},
                {"vendor": "cisco", "product": "ios", "version": "15.0\\(2\\)sg10"},
            ]

            print("Syncing demo versions (this will take ~1 minute due to rate limiting)...\n")
            stats = cache.sync_versions(demo_versions, force=args.force)
            print(f"\n{json.dumps(stats, indent=2)}")

        elif args.stats:
            summary = cache.get_summary()
            print("\n=== CVE Cache Statistics ===")
            print(f"Total CVEs: {summary['total']}")
            print(f"  Critical: {summary['critical']}")
            print(f"  High:     {summary['high']}")
            print(f"  Medium:   {summary['medium']}")
            print(f"  Low:      {summary['low']}")

        elif args.versions:
            versions = cache.get_synced_versions()
            print(f"\n=== Synced Versions ({len(versions)}) ===")
            for v in versions:
                print(f"  {v['vendor']}:{v['product']}:{v['version']} - {v['cve_count']} CVEs")

        elif args.report:
            report = cache.get_version_report()
            print("\n=== Version CVE Report ===")
            print(f"{'Version':<40} {'Total':>6} {'Crit':>5} {'High':>5} {'Med':>5} {'Low':>5}")
            print("-" * 70)
            for r in report:
                ver = f"{r['vendor']}:{r['product']}:{r['version']}"
                print(
                    f"{ver:<40} {r['cve_count'] or 0:>6} {r['critical'] or 0:>5} {r['high'] or 0:>5} {r['medium'] or 0:>5} {r['low'] or 0:>5}")

        elif args.query:
            parts = args.query.split(':')
            if len(parts) != 3:
                print("Query format: vendor:product:version")
                return
            vendor, product, version = parts
            cves = cache.get_cves_for_version(vendor, product, version)
            print(f"\n{len(cves)} CVEs for {vendor}:{product}:{version}\n")
            for cve in cves[:15]:
                sev = cve['severity'] or 'N/A'
                score = cve['cvss_v3_score'] or 'N/A'
                print(f"  {cve['cve_id']} ({sev}, {score})")
                if cve['description']:
                    print(f"    {cve['description'][:80]}...")

        else:
            parser.print_help()

    finally:
        cache.close()


if __name__ == "__main__":
    main()