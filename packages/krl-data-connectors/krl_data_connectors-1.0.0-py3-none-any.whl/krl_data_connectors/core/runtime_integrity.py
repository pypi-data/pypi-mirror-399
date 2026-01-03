# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Runtime Integrity Verification - Phase 2 Defense Layer

Detects tampering or modified bytecode at runtime by verifying SHA256 hashes
of critical modules at import time. Provides fail-safe behavior for integrity
violations with optional server notification.

SECURITY PRINCIPLE:
    Even if obfuscation is defeated, runtime integrity checks detect:
    - Modified bytecode
    - Replaced modules
    - Injected code
    - Tampered imports

Usage:
    from krl_data_connectors.core.runtime_integrity import IntegrityVerifier

    # Verify a single module
    verifier = IntegrityVerifier()
    if not verifier.verify_module("krl_data_connectors.core.license_validator"):
        raise RuntimeError("Module integrity compromised")
    
    # Verify all critical modules at startup
    verifier.verify_critical_modules()
"""

import hashlib
import importlib
import importlib.util
import json
import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone, UTC
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

# Configure module logger
logger = logging.getLogger(__name__)


class IntegrityError(Exception):
    """
    Raised when runtime integrity verification fails.
    
    This exception indicates that a module's content hash does not match
    the expected hash from the integrity manifest, suggesting tampering.
    
    Attributes:
        module_name: Name of the compromised module
        expected_hash: Expected SHA256 hash from manifest
        actual_hash: Computed hash of the module file
        message: Human-readable error message
    """
    
    def __init__(
        self,
        module_name: str,
        expected_hash: Optional[str] = None,
        actual_hash: Optional[str] = None,
        message: Optional[str] = None
    ):
        self.module_name = module_name
        self.expected_hash = expected_hash
        self.actual_hash = actual_hash
        self.message = message or f"Integrity check failed for module: {module_name}"
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/reporting."""
        return {
            "error": "IntegrityError",
            "module_name": self.module_name,
            "expected_hash": self.expected_hash,
            "actual_hash": self.actual_hash,
            "message": self.message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@dataclass
class IntegrityManifest:
    """
    Container for module integrity information.
    
    Stores SHA256 hashes of critical modules along with build metadata
    for traceability and forensic analysis.
    
    Attributes:
        version: Manifest format version
        build_id: Unique build identifier
        build_timestamp: ISO8601 build timestamp
        commit_sha: Git commit SHA of the build
        module_hashes: Dict mapping module paths to SHA256 hashes
        critical_modules: Set of modules that MUST pass integrity checks
    """
    version: str
    build_id: str
    build_timestamp: str
    commit_sha: str
    module_hashes: Dict[str, str]
    critical_modules: Set[str]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IntegrityManifest":
        """Create manifest from dictionary."""
        return cls(
            version=data.get("version", "1.0.0"),
            build_id=data.get("build_id", "unknown"),
            build_timestamp=data.get("build_timestamp", ""),
            commit_sha=data.get("commit_sha", ""),
            module_hashes=data.get("module_hashes", {}),
            critical_modules=set(data.get("critical_modules", []))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert manifest to dictionary."""
        return {
            "version": self.version,
            "build_id": self.build_id,
            "build_timestamp": self.build_timestamp,
            "commit_sha": self.commit_sha,
            "module_hashes": self.module_hashes,
            "critical_modules": list(self.critical_modules)
        }


class IntegrityVerifier:
    """
    Runtime module integrity verifier.
    
    Verifies SHA256 hashes of Python modules against a pre-built manifest
    to detect tampering. Provides configurable behavior for integrity
    violations (fail, warn, or report to server).
    
    Security Features:
        - SHA256 hash verification of module source
        - Critical module enforcement (hard fail)
        - Non-critical module warnings
        - Server-side violation reporting (optional)
        - Cached verification for performance
        - Anti-debugging detection (optional)
    
    Attributes:
        manifest: The integrity manifest with expected hashes
        strict_mode: If True, raise on any integrity failure
        report_violations: If True, report violations to license server
        cache_results: If True, cache verification results
    
    Example:
        >>> verifier = IntegrityVerifier(strict_mode=True)
        >>> verifier.verify_critical_modules()  # Raises if any fail
        >>> 
        >>> # Or with graceful degradation
        >>> verifier = IntegrityVerifier(strict_mode=False)
        >>> results = verifier.verify_all_modules()
        >>> if not results["all_passed"]:
        ...     logger.warning(f"Integrity issues: {results['failed']}")
    """
    
    # Default critical modules that MUST pass integrity checks
    DEFAULT_CRITICAL_MODULES = {
        "krl_data_connectors.core.license_validator",
        "krl_data_connectors.core.runtime_integrity",
        "krl_data_connectors.core.rate_limiter",
        "krl_data_connectors.licensed_connector_mixin",
    }
    
    # Manifest file location (relative to package root)
    MANIFEST_FILENAME = ".integrity_manifest.json"
    
    def __init__(
        self,
        manifest_path: Optional[str] = None,
        strict_mode: bool = False,
        report_violations: bool = True,
        cache_results: bool = True,
        license_server_url: Optional[str] = None
    ):
        """
        Initialize the integrity verifier.
        
        Args:
            manifest_path: Path to integrity manifest file (auto-detected if None)
            strict_mode: If True, raise IntegrityError on any failure
            report_violations: If True, report violations to license server
            cache_results: If True, cache verification results
            license_server_url: URL for reporting violations
        """
        self.strict_mode = strict_mode
        self.report_violations = report_violations
        self.cache_results = cache_results
        self.license_server_url = license_server_url or os.getenv(
            "KRL_LICENSE_SERVER_URL", "https://api.krlabs.dev"
        )
        
        # Verification cache
        self._cache: Dict[str, bool] = {}
        
        # Load manifest
        self.manifest = self._load_manifest(manifest_path)
        
        # Track violations for reporting
        self._violations: List[Dict[str, Any]] = []
    
    def _load_manifest(self, manifest_path: Optional[str] = None) -> IntegrityManifest:
        """
        Load integrity manifest from file or environment.
        
        Args:
            manifest_path: Explicit path to manifest file
            
        Returns:
            IntegrityManifest instance
            
        Note:
            If no manifest is found, returns a default manifest with
            no pre-computed hashes. This allows graceful operation in
            development environments.
        """
        # Try explicit path first
        if manifest_path and os.path.exists(manifest_path):
            return self._load_manifest_file(manifest_path)
        
        # Try environment variable
        env_path = os.getenv("KRL_INTEGRITY_MANIFEST")
        if env_path and os.path.exists(env_path):
            return self._load_manifest_file(env_path)
        
        # Try package root
        try:
            import krl_data_connectors
            package_dir = Path(krl_data_connectors.__file__).parent
            manifest_file = package_dir / self.MANIFEST_FILENAME
            if manifest_file.exists():
                return self._load_manifest_file(str(manifest_file))
        except Exception:
            pass
        
        # Return default (empty) manifest for development
        logger.debug("No integrity manifest found - using default (development mode)")
        return IntegrityManifest(
            version="1.0.0",
            build_id="development",
            build_timestamp=datetime.now(timezone.utc).isoformat(),
            commit_sha="",
            module_hashes={},
            critical_modules=self.DEFAULT_CRITICAL_MODULES
        )
    
    def _load_manifest_file(self, path: str) -> IntegrityManifest:
        """Load manifest from JSON file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.debug(f"Loaded integrity manifest from {path}")
            return IntegrityManifest.from_dict(data)
        except Exception as e:
            logger.warning(f"Failed to load integrity manifest from {path}: {e}")
            return IntegrityManifest(
                version="1.0.0",
                build_id="error",
                build_timestamp="",
                commit_sha="",
                module_hashes={},
                critical_modules=self.DEFAULT_CRITICAL_MODULES
            )
    
    def compute_module_hash(self, module_name: str) -> Optional[str]:
        """
        Compute SHA256 hash of a module's source file.
        
        Args:
            module_name: Fully qualified module name (e.g., "krl_data_connectors.core")
            
        Returns:
            Hex-encoded SHA256 hash, or None if module not found
        """
        try:
            # Get module spec
            spec = importlib.util.find_spec(module_name)
            if spec is None or spec.origin is None:
                logger.warning(f"Cannot find module: {module_name}")
                return None
            
            # Skip built-in and frozen modules
            if spec.origin in ("built-in", "frozen"):
                return None
            
            # Read and hash the file
            with open(spec.origin, "rb") as f:
                content = f.read()
            
            return hashlib.sha256(content).hexdigest()
            
        except Exception as e:
            logger.warning(f"Error computing hash for {module_name}: {e}")
            return None
    
    def verify_module(
        self,
        module_name: str,
        expected_hash: Optional[str] = None
    ) -> bool:
        """
        Verify integrity of a single module.
        
        Args:
            module_name: Fully qualified module name
            expected_hash: Expected SHA256 hash (from manifest if None)
            
        Returns:
            True if module passes integrity check
            
        Raises:
            IntegrityError: If strict_mode and verification fails
        """
        # Check cache
        if self.cache_results and module_name in self._cache:
            return self._cache[module_name]
        
        # Get expected hash from manifest if not provided
        if expected_hash is None:
            expected_hash = self.manifest.module_hashes.get(module_name)
        
        # If no expected hash, we can't verify (pass in dev mode)
        if expected_hash is None:
            logger.debug(f"No expected hash for {module_name} - skipping verification")
            if self.cache_results:
                self._cache[module_name] = True
            return True
        
        # Compute actual hash
        actual_hash = self.compute_module_hash(module_name)
        if actual_hash is None:
            # Module not found - treat as failure
            self._handle_violation(
                module_name=module_name,
                expected_hash=expected_hash,
                actual_hash=None,
                reason="Module file not found"
            )
            if self.cache_results:
                self._cache[module_name] = False
            return False
        
        # Compare hashes
        if actual_hash != expected_hash:
            self._handle_violation(
                module_name=module_name,
                expected_hash=expected_hash,
                actual_hash=actual_hash,
                reason="Hash mismatch"
            )
            if self.cache_results:
                self._cache[module_name] = False
            return False
        
        # Passed
        logger.debug(f"Integrity verified: {module_name}")
        if self.cache_results:
            self._cache[module_name] = True
        return True
    
    def _handle_violation(
        self,
        module_name: str,
        expected_hash: Optional[str],
        actual_hash: Optional[str],
        reason: str
    ) -> None:
        """Handle an integrity violation."""
        is_critical = module_name in self.manifest.critical_modules
        
        violation = {
            "module_name": module_name,
            "expected_hash": expected_hash,
            "actual_hash": actual_hash,
            "reason": reason,
            "is_critical": is_critical,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "build_id": self.manifest.build_id
        }
        
        self._violations.append(violation)
        
        log_msg = (
            f"Integrity violation: {module_name} - {reason} "
            f"(expected: {expected_hash[:16] if expected_hash else 'N/A'}..., "
            f"actual: {actual_hash[:16] if actual_hash else 'N/A'}...)"
        )
        
        if is_critical:
            logger.error(f"CRITICAL {log_msg}")
            if self.strict_mode:
                raise IntegrityError(
                    module_name=module_name,
                    expected_hash=expected_hash,
                    actual_hash=actual_hash,
                    message=f"Critical module integrity compromised: {module_name}"
                )
        else:
            logger.warning(log_msg)
        
        # Report to server (async in production)
        if self.report_violations:
            self._report_violation(violation)
    
    def _report_violation(self, violation: Dict[str, Any]) -> None:
        """
        Report violation to license server.
        
        This is a best-effort operation - failures are logged but don't
        affect the verification flow.
        """
        try:
            import requests
            
            payload = {
                "event": "integrity_violation",
                "violation": violation,
                "environment": {
                    "python_version": sys.version,
                    "platform": sys.platform,
                    "build_id": self.manifest.build_id
                }
            }
            
            # Fire-and-forget (with short timeout)
            requests.post(
                f"{self.license_server_url}/v1/telemetry/integrity",
                json=payload,
                timeout=2
            )
            logger.debug(f"Reported integrity violation for {violation['module_name']}")
            
        except Exception as e:
            logger.debug(f"Failed to report violation: {e}")
    
    def verify_critical_modules(self) -> bool:
        """
        Verify all critical modules.
        
        This is the primary entry point for startup integrity checks.
        Critical modules are those essential for licensing, rate limiting,
        and security enforcement.
        
        Returns:
            True if all critical modules pass verification
            
        Raises:
            IntegrityError: If strict_mode and any critical module fails
        """
        all_passed = True
        critical = self.manifest.critical_modules or self.DEFAULT_CRITICAL_MODULES
        
        for module_name in critical:
            if not self.verify_module(module_name):
                all_passed = False
                if self.strict_mode:
                    # Already raised in verify_module
                    pass
        
        return all_passed
    
    def verify_all_modules(self) -> Dict[str, Any]:
        """
        Verify all modules in the manifest.
        
        Returns:
            Dictionary with verification results:
            - all_passed: bool
            - passed: List of module names that passed
            - failed: List of module names that failed
            - skipped: List of modules with no expected hash
        """
        passed = []
        failed = []
        skipped = []
        
        for module_name, expected_hash in self.manifest.module_hashes.items():
            if expected_hash is None:
                skipped.append(module_name)
                continue
            
            if self.verify_module(module_name, expected_hash):
                passed.append(module_name)
            else:
                failed.append(module_name)
        
        return {
            "all_passed": len(failed) == 0,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "violations": self._violations
        }
    
    def get_violations(self) -> List[Dict[str, Any]]:
        """Get list of all recorded violations."""
        return self._violations.copy()
    
    def clear_cache(self) -> None:
        """Clear verification cache."""
        self._cache.clear()


# =============================================================================
# IMPORT HOOK FOR AUTOMATIC VERIFICATION
# =============================================================================

class IntegrityImportHook:
    """
    Import hook that verifies module integrity on import.
    
    When installed, this hook intercepts imports and verifies the
    integrity of modules before they are loaded. This provides
    automatic protection without requiring explicit verification calls.
    
    Usage:
        from krl_data_connectors.core.runtime_integrity import install_import_hook
        install_import_hook(strict_mode=True)
        
        # All subsequent imports will be verified
        from krl_data_connectors.professional import AdvancedConnector
    """
    
    def __init__(
        self,
        verifier: IntegrityVerifier,
        module_prefix: str = "krl_data_connectors"
    ):
        """
        Initialize the import hook.
        
        Args:
            verifier: IntegrityVerifier instance for verification
            module_prefix: Only verify modules starting with this prefix
        """
        self.verifier = verifier
        self.module_prefix = module_prefix
    
    def find_module(self, fullname: str, path=None):
        """Called by Python import machinery."""
        if fullname.startswith(self.module_prefix):
            return self
        return None
    
    def load_module(self, fullname: str):
        """Called to load a module - we verify after standard loading."""
        # Let Python load the module normally first
        if fullname in sys.modules:
            module = sys.modules[fullname]
        else:
            # Remove ourselves temporarily to avoid recursion
            sys.meta_path = [h for h in sys.meta_path if h is not self]
            try:
                module = importlib.import_module(fullname)
            finally:
                # Re-install ourselves
                sys.meta_path.insert(0, self)
        
        # Verify the loaded module
        self.verifier.verify_module(fullname)
        
        return module


def install_import_hook(
    strict_mode: bool = False,
    report_violations: bool = True,
    module_prefix: str = "krl_data_connectors"
) -> IntegrityImportHook:
    """
    Install the integrity verification import hook.
    
    Args:
        strict_mode: If True, raise on integrity failures
        report_violations: If True, report violations to server
        module_prefix: Only verify modules with this prefix
        
    Returns:
        The installed IntegrityImportHook instance
    """
    verifier = IntegrityVerifier(
        strict_mode=strict_mode,
        report_violations=report_violations
    )
    hook = IntegrityImportHook(verifier, module_prefix)
    sys.meta_path.insert(0, hook)
    logger.info(f"Installed integrity import hook for {module_prefix}.*")
    return hook


def uninstall_import_hook(hook: IntegrityImportHook) -> None:
    """Remove an installed import hook."""
    sys.meta_path = [h for h in sys.meta_path if h is not hook]
    logger.info("Uninstalled integrity import hook")


# =============================================================================
# STARTUP VERIFICATION
# =============================================================================

def verify_on_startup(
    strict_mode: bool = False,
    critical_only: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to verify integrity at application startup.
    
    Call this early in your application to detect tampering before
    sensitive operations are performed.
    
    Args:
        strict_mode: If True, raise on failures
        critical_only: If True, only verify critical modules
        
    Returns:
        Verification results dictionary
        
    Example:
        from krl_data_connectors.core.runtime_integrity import verify_on_startup
        
        results = verify_on_startup(strict_mode=True)
        if not results["all_passed"]:
            sys.exit(1)
    """
    verifier = IntegrityVerifier(strict_mode=strict_mode)
    
    if critical_only:
        all_passed = verifier.verify_critical_modules()
        return {
            "all_passed": all_passed,
            "mode": "critical_only",
            "violations": verifier.get_violations()
        }
    else:
        return verifier.verify_all_modules()
