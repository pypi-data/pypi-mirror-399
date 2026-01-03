# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
KRL Data Connectors - Enterprise Tier

Enterprise tier includes 8 premium connectors for healthcare, crime,
environmental, and social services data requiring enhanced security.

License: Enterprise tier ($999-5,000/month)
Rate Limit: 50,000 requests/day
Code Protection: PyArmor + device binding
Features: Priority support, on-premise deployment, custom connectors

Domains:
- Crime (3): FBI_UCR_Detailed, Bureau_Of_Justice, Victims_Of_Crime
- Health (2): SAMHSA, CDC_Full_API
- Environmental (1): EPA_Superfund_Full
- Social Services (2): Veterans_Affairs, ACF_Full

Compliance: HIPAA, FISMA, SOC 2 Type II certified
Security: End-to-end encryption, audit logging, device binding

Usage:
    from krl_data_connectors.enterprise import FBIUCRConnector
    
    fbi = FBIUCRConnector()  # License validated automatically
    data = fbi.fetch(query_type="offense_data", year=2024)
    
Note: Enterprise connectors require additional agreements and
certifications for handling sensitive data.
"""

from .crime.bureau_of_justice import BureauOfJusticeConnector

# Crime
from .crime.fbi_ucr_connector import FBIUCRConnector
from .crime.victims_of_crime import VictimsOfCrimeConnector

# Environmental
from .environmental.epa_superfund_full import SuperfundConnector
from .health.cdc_full_api import CDCWonderConnector

# Health
from .health.samhsa import SAMHSAConnector
from .social_services.acf_full import ACFConnector

# Social Services
from .social_services.veterans_affairs import VAConnector

# Airbyte Integration (600+ additional sources)
# Requires: pip install krl-data-connectors[enterprise]
try:
    from .airbyte import (
        AirbyteClient,
        AirbyteConnector,
        AirbyteSourceCatalog,
        DatabaseSources,
        SaaSSources,
        WarehouseSources,
        SyncManager,
        SyncJob,
        SyncStatus,
    )
    AIRBYTE_AVAILABLE = True
except ImportError:
    AIRBYTE_AVAILABLE = False
    AirbyteClient = None
    AirbyteConnector = None
    AirbyteSourceCatalog = None
    DatabaseSources = None
    SaaSSources = None
    WarehouseSources = None
    SyncManager = None
    SyncJob = None
    SyncStatus = None

# AI Integration (OpenRouter + Supermemory)
# Provides multi-model LLM routing and memory/RAG capabilities
# Requires: pip install krl-data-connectors[enterprise]
try:
    from .ai import (
        OpenRouterClient,
        SupermemoryClient,
        AIConnector,
        create_ai_connector,
        # Data classes
        Message,
        ChatResponse,
        Document,
        SearchResult,
    )
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    OpenRouterClient = None
    SupermemoryClient = None
    AIConnector = None
    create_ai_connector = None
    Message = None
    ChatResponse = None
    Document = None
    SearchResult = None

__all__ = [
    # Crime
    "FBIUCRConnector",
    "BureauOfJusticeConnector",
    "VictimsOfCrimeConnector",
    # Health
    "SAMHSAConnector",
    "CDCWonderConnector",
    # Environmental
    "SuperfundConnector",
    # Social Services
    "VAConnector",
    "ACFConnector",
    # Airbyte Integration
    "AirbyteClient",
    "AirbyteConnector",
    "AirbyteSourceCatalog",
    "DatabaseSources",
    "SaaSSources",
    "WarehouseSources",
    "SyncManager",
    "SyncJob",
    "SyncStatus",
    "AIRBYTE_AVAILABLE",
    # AI Integration (OpenRouter + Supermemory)
    "OpenRouterClient",
    "SupermemoryClient",
    "AIConnector",
    "create_ai_connector",
    "Message",
    "ChatResponse",
    "Document",
    "SearchResult",
    "AI_AVAILABLE",
]
