# velocitycmdb/app/blueprints/security/routes.py
"""
Security Dashboard Routes - CVE vulnerability tracking.

Integrates with VelocityCMDB device inventory to track vulnerabilities
affecting deployed OS versions using NIST NVD data.
"""

from flask import render_template, jsonify, request, current_app, flash, redirect, url_for
from . import security_bp
from velocitycmdb.app.utils.database import get_db_connection
import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime


# ============================================================================
# CVE Database Access
# ============================================================================

def get_cve_db_path() -> Path:
    """Get path to CVE cache database in data directory"""
    data_dir = current_app.config.get('VELOCITYCMDB_DATA_DIR', '~/.velocitycmdb/data')
    data_dir = os.path.expanduser(data_dir)
    return Path(data_dir) / 'cve_cache.db'


def get_cve_db():
    """Get CVE database connection"""
    db_path = get_cve_db_path()
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def ensure_cve_schema():
    """Ensure CVE database tables exist"""
    db_path = get_cve_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(db_path))
    conn.executescript("""
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

        -- Indexes
        CREATE INDEX IF NOT EXISTS idx_cve_severity ON cve_records(severity);
        CREATE INDEX IF NOT EXISTS idx_cve_published ON cve_records(published_date);
        CREATE INDEX IF NOT EXISTS idx_cpe_vendor_product ON cpe_cve_mapping(cpe_vendor, cpe_product);
        CREATE INDEX IF NOT EXISTS idx_cpe_version ON cpe_cve_mapping(version_exact);
        CREATE INDEX IF NOT EXISTS idx_synced_versions ON synced_versions(vendor, product, version);
    """)
    conn.commit()
    conn.close()


# Vendor mapping from CMDB names to CPE vendor/product
VENDOR_MAP = {
    'juniper networks': ('juniper', 'junos'),
    'juniper': ('juniper', 'junos'),
    'arista networks': ('arista', 'eos'),
    'arista': ('arista', 'eos'),
    'cisco systems': ('cisco', 'ios'),
    'cisco': ('cisco', 'ios'),
    'palo alto networks': ('paloaltonetworks', 'pan-os'),
    'palo alto': ('paloaltonetworks', 'pan-os'),
    'fortinet': ('fortinet', 'fortios'),
}


def normalize_version(vendor: str, version: str) -> str:
    """Normalize OS version string for CPE matching"""
    version = version.lower().strip()
    
    # Cisco: escape parentheses
    if 'cisco' in vendor.lower():
        version = version.replace('(', '\\(').replace(')', '\\)')
    
    return version


def get_cmdb_versions():
    """Get unique vendor/version combinations from CMDB devices table"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT 
                v.name as vendor,
                d.os_version,
                COUNT(d.id) as device_count
            FROM devices d
            LEFT JOIN vendors v ON d.vendor_id = v.id
            WHERE d.os_version IS NOT NULL 
              AND d.os_version != ''
              AND d.os_version != 'Unknown'
              AND v.name IS NOT NULL
            GROUP BY v.name, d.os_version
            ORDER BY device_count DESC
        """)
        return [dict(row) for row in cursor.fetchall()]


def get_devices_by_version(vendor: str, os_version: str):
    """Get list of devices running a specific OS version"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                d.id,
                d.name,
                d.site_code,
                d.model,
                d.management_ip,
                s.name as site_name
            FROM devices d
            LEFT JOIN vendors v ON d.vendor_id = v.id
            LEFT JOIN sites s ON d.site_code = s.code
            WHERE v.name = ? AND d.os_version = ?
            ORDER BY d.site_code, d.name
        """, (vendor, os_version))
        return [dict(row) for row in cursor.fetchall()]


# ============================================================================
# Template Filters
# ============================================================================

@security_bp.app_template_filter('from_json')
def from_json_filter(value):
    """Parse JSON string to Python object"""
    if value:
        try:
            return json.loads(value)
        except:
            return []
    return []


# ============================================================================
# Dashboard Routes
# ============================================================================

@security_bp.route('/')
@security_bp.route('/dashboard')
def dashboard():
    """Main security dashboard"""
    ensure_cve_schema()
    
    try:
        cve_conn = get_cve_db()
        
        # Get CVE summary stats
        summary = get_cve_summary(cve_conn)
        
        # Get version report with device counts
        version_report = get_version_report_with_devices(cve_conn)
        
        # Get recent CVEs
        recent_cves = get_recent_cves(cve_conn, limit=10)
        
        # Get severity distribution for chart
        severity_dist = get_severity_distribution(cve_conn)
        
        cve_conn.close()
        
        return render_template('security/dashboard.html',
                              summary=summary,
                              version_report=version_report,
                              recent_cves=recent_cves,
                              severity_dist=severity_dist)
    
    except Exception as e:
        current_app.logger.error(f"Security dashboard error: {e}", exc_info=True)
        return render_template('security/dashboard.html',
                              error=str(e),
                              summary={'total': 0, 'critical': 0, 'high': 0, 
                                      'medium': 0, 'low': 0, 'versions_tracked': 0},
                              version_report=[],
                              recent_cves=[],
                              severity_dist={'labels': [], 'values': []})


@security_bp.route('/versions')
def versions():
    """Version vulnerability list"""
    ensure_cve_schema()
    cve_conn = get_cve_db()
    version_report = get_version_report_with_devices(cve_conn)
    cve_conn.close()
    return render_template('security/versions.html', versions=version_report)


@security_bp.route('/version/<vendor>/<product>/<path:version>')
def version_detail(vendor, product, version):
    """CVE details for a specific version"""
    ensure_cve_schema()
    cve_conn = get_cve_db()
    
    # Get CVEs for this version
    cves = cve_conn.execute("""
        SELECT c.* FROM cve_records c
        JOIN cpe_cve_mapping m ON c.cve_id = m.cve_id
        WHERE m.cpe_vendor = ? AND m.cpe_product = ? AND m.version_exact = ?
        ORDER BY c.cvss_v3_score DESC NULLS LAST
    """, (vendor.lower(), product.lower(), version.lower())).fetchall()
    
    # Get version sync info
    version_info = cve_conn.execute("""
        SELECT * FROM synced_versions 
        WHERE vendor = ? AND product = ? AND version = ?
    """, (vendor.lower(), product.lower(), version.lower())).fetchone()
    
    cve_conn.close()
    
    # Map CPE vendor back to CMDB vendor name for device lookup
    cmdb_vendor = None
    for cmdb_name, (cpe_v, cpe_p) in VENDOR_MAP.items():
        if cpe_v == vendor.lower() and cpe_p == product.lower():
            cmdb_vendor = cmdb_name.title()
            break
    
    # Get affected devices from CMDB
    affected_devices = []
    if cmdb_vendor:
        # Try both original case and various normalizations
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    d.id, d.name, d.site_code, d.model, d.management_ip,
                    d.os_version, s.name as site_name
                FROM devices d
                LEFT JOIN vendors v ON d.vendor_id = v.id
                LEFT JOIN sites s ON d.site_code = s.code
                WHERE LOWER(v.name) LIKE ? 
                  AND LOWER(d.os_version) = ?
                ORDER BY d.site_code, d.name
            """, (f"%{vendor.lower()}%", version.lower()))
            affected_devices = [dict(row) for row in cursor.fetchall()]
    
    return render_template('security/version_detail.html',
                          vendor=vendor,
                          product=product,
                          version=version,
                          version_info=dict(version_info) if version_info else None,
                          cves=[dict(c) for c in cves],
                          affected_devices=affected_devices)


@security_bp.route('/cve/<cve_id>')
def cve_detail(cve_id):
    """Single CVE detail view"""
    ensure_cve_schema()
    cve_conn = get_cve_db()
    
    cve = cve_conn.execute(
        "SELECT * FROM cve_records WHERE cve_id = ?", (cve_id,)
    ).fetchone()
    
    if not cve:
        cve_conn.close()
        return "CVE not found", 404
    
    # Get affected versions (from our synced data)
    affected = cve_conn.execute("""
        SELECT DISTINCT cpe_vendor, cpe_product, version_exact 
        FROM cpe_cve_mapping WHERE cve_id = ?
    """, (cve_id,)).fetchall()
    
    cve_conn.close()
    
    # For each affected version, get device counts from CMDB
    affected_with_devices = []
    for a in affected:
        a_dict = dict(a)
        # Find CMDB vendor name
        for cmdb_name, (cpe_v, cpe_p) in VENDOR_MAP.items():
            if cpe_v == a_dict['cpe_vendor'] and cpe_p == a_dict['cpe_product']:
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT COUNT(*) as count FROM devices d
                        LEFT JOIN vendors v ON d.vendor_id = v.id
                        WHERE LOWER(v.name) LIKE ? AND LOWER(d.os_version) = ?
                    """, (f"%{a_dict['cpe_vendor']}%", a_dict['version_exact']))
                    result = cursor.fetchone()
                    a_dict['device_count'] = result['count'] if result else 0
                break
        else:
            a_dict['device_count'] = 0
        affected_with_devices.append(a_dict)
    
    return render_template('security/cve_detail.html',
                          cve=dict(cve),
                          affected=affected_with_devices)


@security_bp.route('/devices')
def vulnerable_devices():
    """Show devices grouped by vulnerability severity"""
    ensure_cve_schema()
    
    # Get all versions from CMDB
    cmdb_versions = get_cmdb_versions()
    
    cve_conn = get_cve_db()
    
    # Build device vulnerability report
    device_vulns = []
    for cv in cmdb_versions:
        vendor_lower = cv['vendor'].lower()
        if vendor_lower not in VENDOR_MAP:
            continue
            
        cpe_vendor, cpe_product = VENDOR_MAP[vendor_lower]
        version = normalize_version(cv['vendor'], cv['os_version'])
        
        # Get CVE summary for this version
        row = cve_conn.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN c.severity = 'CRITICAL' THEN 1 END) as critical,
                COUNT(CASE WHEN c.severity = 'HIGH' THEN 1 END) as high
            FROM cpe_cve_mapping m
            JOIN cve_records c ON m.cve_id = c.cve_id
            WHERE m.cpe_vendor = ? AND m.cpe_product = ? AND m.version_exact = ?
        """, (cpe_vendor, cpe_product, version)).fetchone()
        
        if row and row['total'] > 0:
            # Get devices running this version
            devices = get_devices_by_version(cv['vendor'], cv['os_version'])
            for device in devices:
                device_vulns.append({
                    'device': device,
                    'vendor': cv['vendor'],
                    'os_version': cv['os_version'],
                    'cpe_vendor': cpe_vendor,
                    'cpe_product': cpe_product,
                    'cpe_version': version,
                    'total_cves': row['total'],
                    'critical': row['critical'],
                    'high': row['high'],
                })
    
    cve_conn.close()
    
    # Sort by critical then high count
    device_vulns.sort(key=lambda x: (-(x['critical'] or 0), -(x['high'] or 0)))
    
    return render_template('security/devices.html', device_vulns=device_vulns)


# ============================================================================
# Sync Routes
# ============================================================================

@security_bp.route('/sync', methods=['GET', 'POST'])
def sync_versions():
    """Sync CVE data for CMDB versions"""
    if request.method == 'GET':
        # Show sync status page
        cmdb_versions = get_cmdb_versions()
        ensure_cve_schema()
        cve_conn = get_cve_db()
        
        # Check sync status for each version
        sync_status = []
        for cv in cmdb_versions:
            vendor_lower = cv['vendor'].lower()
            if vendor_lower not in VENDOR_MAP:
                sync_status.append({
                    **cv,
                    'supported': False,
                    'synced': False,
                    'cve_count': None
                })
                continue
            
            cpe_vendor, cpe_product = VENDOR_MAP[vendor_lower]
            version = normalize_version(cv['vendor'], cv['os_version'])
            
            # Check if synced
            row = cve_conn.execute("""
                SELECT cve_count, last_synced FROM synced_versions
                WHERE vendor = ? AND product = ? AND version = ?
            """, (cpe_vendor, cpe_product, version)).fetchone()
            
            sync_status.append({
                **cv,
                'supported': True,
                'cpe_vendor': cpe_vendor,
                'cpe_product': cpe_product,
                'cpe_version': version,
                'synced': row is not None,
                'cve_count': row['cve_count'] if row else None,
                'last_synced': row['last_synced'] if row else None
            })
        
        cve_conn.close()
        
        return render_template('security/sync.html', sync_status=sync_status)
    
    else:
        # POST - trigger sync
        # Note: This should ideally be a background task
        # For now, sync just the selected versions
        selected = request.form.getlist('versions')
        force = request.form.get('force') == '1'
        
        if not selected:
            flash('No versions selected for sync', 'warning')
            return redirect(url_for('security.sync_versions'))
        
        # Import the cache module for sync
        from .nvd_cache import CVECache
        
        cache = CVECache(str(get_cve_db_path()))
        
        versions_to_sync = []
        for v in selected:
            parts = v.split('|')
            if len(parts) == 3:
                versions_to_sync.append({
                    'vendor': parts[0],
                    'product': parts[1],
                    'version': parts[2]
                })
        
        try:
            stats = cache.sync_versions(versions_to_sync, force=force)
            flash(f"Sync complete: {stats['versions_processed']} versions processed, "
                  f"{stats['cves_added']} new CVEs found", 'success')
        except Exception as e:
            flash(f"Sync error: {str(e)}", 'error')
        finally:
            cache.close()
        
        return redirect(url_for('security.dashboard'))


# ============================================================================
# API Endpoints
# ============================================================================

@security_bp.route('/api/summary')
def api_summary():
    """API: Get CVE summary stats"""
    ensure_cve_schema()
    cve_conn = get_cve_db()
    summary = get_cve_summary(cve_conn)
    cve_conn.close()
    return jsonify(summary)


@security_bp.route('/api/versions')
def api_versions():
    """API: Get version CVE report"""
    ensure_cve_schema()
    cve_conn = get_cve_db()
    report = get_version_report_with_devices(cve_conn)
    cve_conn.close()
    return jsonify(report)


@security_bp.route('/api/version/<vendor>/<product>/<path:version>')
def api_version_cves(vendor, product, version):
    """API: Get CVEs for specific version"""
    ensure_cve_schema()
    cve_conn = get_cve_db()
    
    cves = cve_conn.execute("""
        SELECT c.* FROM cve_records c
        JOIN cpe_cve_mapping m ON c.cve_id = m.cve_id
        WHERE m.cpe_vendor = ? AND m.cpe_product = ? AND m.version_exact = ?
        ORDER BY c.cvss_v3_score DESC NULLS LAST
    """, (vendor.lower(), product.lower(), version.lower())).fetchall()
    
    cve_conn.close()
    return jsonify([dict(c) for c in cves])


@security_bp.route('/api/severity-chart')
def api_severity_chart():
    """API: Severity distribution for charts"""
    ensure_cve_schema()
    cve_conn = get_cve_db()
    dist = get_severity_distribution(cve_conn)
    cve_conn.close()
    return jsonify(dist)


@security_bp.route('/api/cmdb-versions')
def api_cmdb_versions():
    """API: Get CMDB versions with sync status"""
    cmdb_versions = get_cmdb_versions()
    ensure_cve_schema()
    cve_conn = get_cve_db()
    
    result = []
    for cv in cmdb_versions:
        vendor_lower = cv['vendor'].lower()
        if vendor_lower not in VENDOR_MAP:
            continue
        
        cpe_vendor, cpe_product = VENDOR_MAP[vendor_lower]
        version = normalize_version(cv['vendor'], cv['os_version'])
        
        row = cve_conn.execute("""
            SELECT cve_count, last_synced FROM synced_versions
            WHERE vendor = ? AND product = ? AND version = ?
        """, (cpe_vendor, cpe_product, version)).fetchone()
        
        result.append({
            'cmdb_vendor': cv['vendor'],
            'os_version': cv['os_version'],
            'device_count': cv['device_count'],
            'cpe_vendor': cpe_vendor,
            'cpe_product': cpe_product,
            'cpe_version': version,
            'synced': row is not None,
            'cve_count': row['cve_count'] if row else None,
            'last_synced': row['last_synced'] if row else None
        })
    
    cve_conn.close()
    return jsonify(result)


# ============================================================================
# Helper Functions
# ============================================================================

def get_cve_summary(cve_conn) -> dict:
    """Get overall CVE statistics"""
    rows = cve_conn.execute(
        "SELECT severity, COUNT(*) as count FROM cve_records GROUP BY severity"
    ).fetchall()
    
    summary = {
        "total": 0,
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "unknown": 0,
    }
    
    for row in rows:
        sev = (row["severity"] or "unknown").lower()
        summary["total"] += row["count"]
        if sev in summary:
            summary[sev] = row["count"]
    
    # Get version count
    version_count = cve_conn.execute(
        "SELECT COUNT(*) FROM synced_versions"
    ).fetchone()[0]
    summary["versions_tracked"] = version_count
    
    return summary


def get_version_report_with_devices(cve_conn) -> list:
    """Get CVE counts per version with device counts from CMDB"""
    # Get synced versions from CVE database
    rows = cve_conn.execute("""
        SELECT 
            sv.vendor, 
            sv.product, 
            sv.version, 
            sv.cve_count,
            sv.last_synced,
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
    
    result = []
    for row in rows:
        row_dict = dict(row)
        
        # Get device count from CMDB
        device_count = 0
        cmdb_vendor = None
        for cmdb_name, (cpe_v, cpe_p) in VENDOR_MAP.items():
            if cpe_v == row_dict['vendor'] and cpe_p == row_dict['product']:
                cmdb_vendor = cmdb_name
                break
        
        if cmdb_vendor:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) as count FROM devices d
                    LEFT JOIN vendors v ON d.vendor_id = v.id
                    WHERE LOWER(v.name) LIKE ? AND LOWER(d.os_version) = ?
                """, (f"%{row_dict['vendor']}%", row_dict['version']))
                result_row = cursor.fetchone()
                device_count = result_row['count'] if result_row else 0
        
        row_dict['device_count'] = device_count
        row_dict['cmdb_vendor'] = cmdb_vendor
        result.append(row_dict)
    
    return result


def get_recent_cves(cve_conn, limit=10) -> list:
    """Get most recently published CVEs"""
    rows = cve_conn.execute("""
        SELECT * FROM cve_records 
        ORDER BY published_date DESC 
        LIMIT ?
    """, (limit,)).fetchall()
    
    return [dict(row) for row in rows]


def get_severity_distribution(cve_conn) -> dict:
    """Get severity counts for pie chart"""
    rows = cve_conn.execute("""
        SELECT severity, COUNT(*) as count 
        FROM cve_records 
        WHERE severity IS NOT NULL 
        GROUP BY severity
    """).fetchall()
    
    return {
        "labels": [row["severity"] for row in rows],
        "values": [row["count"] for row in rows],
        "colors": {
            "CRITICAL": "#dc3545",
            "HIGH": "#fd7e14",
            "MEDIUM": "#ffc107",
            "LOW": "#28a745",
            "UNKNOWN": "#6c757d",
        }
    }
