# velocitycmdb/app/blueprints/security/__init__.py
"""
Security Blueprint - CVE vulnerability tracking for network infrastructure.

Integrates with VelocityCMDB device inventory to track vulnerabilities
affecting deployed OS versions using NIST NVD data.
"""

from flask import Blueprint

security_bp = Blueprint('security', __name__)

from . import routes  # noqa: E402, F401
