# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# KR-Labs is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
Environment Fingerprint Collector

Collects machine and runtime environment information for:
- License binding verification
- Anomaly detection
- Challenge-response authentication
- Session validation
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import platform
import socket
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone, UTC
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class NetworkInfo:
    """Network environment information."""
    hostname: str
    fqdn: str
    ip_addresses: List[str]
    mac_address: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "hostname": self.hostname,
            "fqdn": self.fqdn,
            "ip_addresses": self.ip_addresses,
            "mac_address": self.mac_address,
        }


@dataclass
class HardwareInfo:
    """Hardware environment information."""
    cpu_count: int
    cpu_type: str
    machine_type: str
    total_memory_mb: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "cpu_count": self.cpu_count,
            "cpu_type": self.cpu_type,
            "machine_type": self.machine_type,
            "total_memory_mb": self.total_memory_mb,
        }


@dataclass
class RuntimeInfo:
    """Python runtime environment information."""
    python_version: str
    python_implementation: str
    python_compiler: str
    executable_path: str
    virtual_env: Optional[str]
    packages_hash: str  # Hash of installed packages
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "python_version": self.python_version,
            "python_implementation": self.python_implementation,
            "python_compiler": self.python_compiler,
            "executable_path": self.executable_path,
            "virtual_env": self.virtual_env,
            "packages_hash": self.packages_hash,
        }


@dataclass
class OSInfo:
    """Operating system information."""
    system: str
    release: str
    version: str
    platform: str
    is_64bit: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "system": self.system,
            "release": self.release,
            "version": self.version,
            "platform": self.platform,
            "is_64bit": self.is_64bit,
        }


@dataclass
class EnvironmentFingerprint:
    """
    Complete environment fingerprint.
    
    Contains all collected environment information and provides
    stable identifiers for license binding and verification.
    """
    machine_id: str
    hardware: HardwareInfo
    os_info: OSInfo
    network: NetworkInfo
    runtime: RuntimeInfo
    collected_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    nonce: str = field(default_factory=lambda: uuid.uuid4().hex)
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """
        Convert to dictionary for transmission.
        
        Args:
            include_sensitive: Include sensitive info (IPs, paths)
        """
        data = {
            "machine_id": self.machine_id,
            "hardware": self.hardware.to_dict(),
            "os_info": self.os_info.to_dict(),
            "runtime": {
                "python_version": self.runtime.python_version,
                "python_implementation": self.runtime.python_implementation,
                "packages_hash": self.runtime.packages_hash,
            },
            "collected_at": self.collected_at,
            "nonce": self.nonce,
        }
        
        if include_sensitive:
            data["network"] = self.network.to_dict()
            data["runtime"]["executable_path"] = self.runtime.executable_path
            data["runtime"]["virtual_env"] = self.runtime.virtual_env
        else:
            # Anonymized network info
            data["network"] = {
                "hostname_hash": hashlib.sha256(
                    self.network.hostname.encode()
                ).hexdigest()[:16],
                "mac_hash": hashlib.sha256(
                    self.network.mac_address.encode()
                ).hexdigest()[:16],
            }
        
        return data
    
    def create_signature(self, secret: bytes) -> str:
        """Create HMAC signature of fingerprint."""
        import hmac
        
        # Create stable signature from key components
        components = [
            self.machine_id,
            self.hardware.cpu_type,
            str(self.hardware.cpu_count),
            self.os_info.system,
            self.os_info.release,
            self.runtime.python_version,
            self.network.mac_address,
            self.collected_at,
            self.nonce,
        ]
        
        payload = "|".join(components)
        return hmac.new(secret, payload.encode(), hashlib.sha256).hexdigest()
    
    @property
    def stability_score(self) -> float:
        """
        Calculate fingerprint stability score (0-1).
        
        Higher score = more stable/reliable fingerprint.
        """
        score = 0.0
        max_score = 6.0
        
        # Machine ID present
        if self.machine_id and len(self.machine_id) >= 32:
            score += 1.0
        
        # MAC address valid
        if self.network.mac_address and self.network.mac_address != "00:00:00:00:00:00":
            score += 1.0
        
        # Hostname present
        if self.network.hostname and self.network.hostname != "localhost":
            score += 1.0
        
        # CPU info complete
        if self.hardware.cpu_count > 0 and self.hardware.cpu_type:
            score += 1.0
        
        # OS info complete
        if self.os_info.system and self.os_info.release:
            score += 1.0
        
        # Python runtime info
        if self.runtime.python_version:
            score += 1.0
        
        return score / max_score


class EnvironmentCollector:
    """
    Collects comprehensive environment fingerprint.
    
    Features:
    - Hardware identification
    - OS detection
    - Network information
    - Python runtime details
    - Stable machine ID generation
    """
    
    def __init__(self, cache_duration_seconds: float = 60.0):
        """
        Initialize collector.
        
        Args:
            cache_duration_seconds: How long to cache fingerprint
        """
        self._cache_duration = cache_duration_seconds
        self._cached_fingerprint: Optional[EnvironmentFingerprint] = None
        self._cache_time: Optional[datetime] = None
        
        logger.debug("EnvironmentCollector initialized")
    
    def collect(self, force_refresh: bool = False) -> EnvironmentFingerprint:
        """
        Collect environment fingerprint.
        
        Args:
            force_refresh: Force collection even if cached
            
        Returns:
            Environment fingerprint
        """
        # Check cache
        if not force_refresh and self._cached_fingerprint:
            if self._cache_time:
                elapsed = (datetime.now(timezone.utc) - self._cache_time).total_seconds()
                if elapsed < self._cache_duration:
                    return self._cached_fingerprint
        
        # Collect all components
        hardware = self._collect_hardware()
        os_info = self._collect_os()
        network = self._collect_network()
        runtime = self._collect_runtime()
        
        # Generate stable machine ID
        machine_id = self._generate_machine_id(hardware, os_info, network)
        
        fingerprint = EnvironmentFingerprint(
            machine_id=machine_id,
            hardware=hardware,
            os_info=os_info,
            network=network,
            runtime=runtime,
        )
        
        # Cache result
        self._cached_fingerprint = fingerprint
        self._cache_time = datetime.now(timezone.utc)
        
        logger.debug("Environment fingerprint collected (stability: %.2f)", 
                    fingerprint.stability_score)
        
        return fingerprint
    
    def _collect_hardware(self) -> HardwareInfo:
        """Collect hardware information."""
        # Get memory info
        try:
            import resource
            # Try to get memory (Unix-like)
            memory_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024
        except (ImportError, AttributeError):
            memory_mb = 0
        
        # Fallback memory detection
        if memory_mb == 0:
            try:
                # Try reading from /proc/meminfo
                with open("/proc/meminfo", "r") as f:
                    for line in f:
                        if line.startswith("MemTotal:"):
                            memory_mb = int(line.split()[1]) // 1024
                            break
            except (FileNotFoundError, PermissionError):
                memory_mb = 4096  # Default fallback
        
        return HardwareInfo(
            cpu_count=os.cpu_count() or 1,
            cpu_type=platform.processor() or platform.machine(),
            machine_type=platform.machine(),
            total_memory_mb=memory_mb,
        )
    
    def _collect_os(self) -> OSInfo:
        """Collect OS information."""
        return OSInfo(
            system=platform.system(),
            release=platform.release(),
            version=platform.version(),
            platform=platform.platform(),
            is_64bit=sys.maxsize > 2**32,
        )
    
    def _collect_network(self) -> NetworkInfo:
        """Collect network information."""
        hostname = socket.gethostname()
        
        try:
            fqdn = socket.getfqdn()
        except Exception:
            fqdn = hostname
        
        # Get IP addresses
        ip_addresses = []
        try:
            # Get all IPs for hostname
            for info in socket.getaddrinfo(hostname, None):
                ip = info[4][0]
                if ip not in ip_addresses and not ip.startswith("127."):
                    ip_addresses.append(ip)
        except socket.gaierror:
            pass
        
        # Get MAC address
        mac_int = uuid.getnode()
        mac_address = ":".join(
            f"{(mac_int >> (8 * (5 - i))) & 0xff:02x}"
            for i in range(6)
        )
        
        return NetworkInfo(
            hostname=hostname,
            fqdn=fqdn,
            ip_addresses=ip_addresses[:5],  # Limit to 5 IPs
            mac_address=mac_address,
        )
    
    def _collect_runtime(self) -> RuntimeInfo:
        """Collect Python runtime information."""
        # Get virtual environment
        virtual_env = os.environ.get("VIRTUAL_ENV") or os.environ.get("CONDA_PREFIX")
        
        # Generate hash of installed packages
        packages_hash = self._get_packages_hash()
        
        return RuntimeInfo(
            python_version=platform.python_version(),
            python_implementation=platform.python_implementation(),
            python_compiler=platform.python_compiler(),
            executable_path=sys.executable,
            virtual_env=virtual_env,
            packages_hash=packages_hash,
        )
    
    def _get_packages_hash(self) -> str:
        """Get hash of installed packages."""
        try:
            # Try using importlib.metadata (Python 3.8+)
            from importlib.metadata import distributions
            
            packages = sorted(
                f"{d.metadata['Name']}=={d.version}"
                for d in distributions()
            )
            packages_str = "\n".join(packages[:100])  # Limit to 100 packages
            return hashlib.sha256(packages_str.encode()).hexdigest()[:16]
        except ImportError:
            pass
        
        try:
            # Fallback to pkg_resources
            import pkg_resources
            
            packages = sorted(
                f"{d.project_name}=={d.version}"
                for d in pkg_resources.working_set
            )
            packages_str = "\n".join(packages[:100])
            return hashlib.sha256(packages_str.encode()).hexdigest()[:16]
        except ImportError:
            pass
        
        return hashlib.sha256(b"unknown").hexdigest()[:16]
    
    def _generate_machine_id(
        self,
        hardware: HardwareInfo,
        os_info: OSInfo,
        network: NetworkInfo,
    ) -> str:
        """
        Generate stable machine identifier.
        
        Uses multiple sources for stability:
        - MAC address
        - Hostname
        - CPU info
        - OS info
        """
        # Combine stable components
        components = [
            network.mac_address,
            network.hostname,
            hardware.cpu_type,
            str(hardware.cpu_count),
            os_info.system,
            hardware.machine_type,
        ]
        
        combined = "|".join(components)
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def get_machine_id(self) -> str:
        """Get just the machine ID (cached)."""
        return self.collect().machine_id
    
    def validate_fingerprint(
        self,
        stored_fingerprint: Dict[str, Any],
        tolerance: float = 0.8,
    ) -> tuple[bool, List[str]]:
        """
        Validate current environment against stored fingerprint.
        
        Args:
            stored_fingerprint: Previously stored fingerprint
            tolerance: Similarity threshold (0-1)
            
        Returns:
            Tuple of (valid, list of differences)
        """
        current = self.collect()
        differences: List[str] = []
        
        # Check machine ID
        if stored_fingerprint.get("machine_id") != current.machine_id:
            differences.append("machine_id")
        
        # Check OS
        stored_os = stored_fingerprint.get("os_info", {})
        if stored_os.get("system") != current.os_info.system:
            differences.append("os_system")
        if stored_os.get("release") != current.os_info.release:
            differences.append("os_release")
        
        # Check hardware
        stored_hw = stored_fingerprint.get("hardware", {})
        if stored_hw.get("cpu_count") != current.hardware.cpu_count:
            differences.append("cpu_count")
        if stored_hw.get("cpu_type") != current.hardware.cpu_type:
            differences.append("cpu_type")
        
        # Check runtime
        stored_runtime = stored_fingerprint.get("runtime", {})
        if stored_runtime.get("python_version") != current.runtime.python_version:
            differences.append("python_version")
        
        # Calculate similarity
        total_checks = 6
        similarity = (total_checks - len(differences)) / total_checks
        
        is_valid = similarity >= tolerance
        
        if not is_valid:
            logger.warning(
                "Fingerprint validation failed: similarity=%.2f, differences=%s",
                similarity, differences
            )
        
        return is_valid, differences
