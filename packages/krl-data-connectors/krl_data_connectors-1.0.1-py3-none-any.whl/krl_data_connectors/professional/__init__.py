# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
KRL Data Connectors - Professional Tier

Professional tier includes 48 connectors across multiple domains.
Requires Professional license (purchased separately).

License: Professional tier ($149-599/month)
Rate Limit: 10,000 requests/day
Code Protection: PyArmor obfuscation

Domains:
- Economic (4): FRED_Full, BLS_Enhanced, World_Bank_Full, Census_BDS
- Demographic (1): Census_ACS_Detailed
- Health (4): HRSA, County_Health_Rankings, NIH_Reporter, BRFSS
- Labor (2): OSHA, Census_LEHD_Full
- Environmental (3): EPA_EJScreen, EPA_Water_Quality, EPA_Air_Quality_Full
- Education (3): NCES_CCD, College_Scorecard, IPEDS
- Housing (3): HUD_FMR, Zillow_Research, Eviction_Lab
- Energy (1): EIA_Full
- Agricultural (2): USDA_NASS, USDA_Food_Atlas
- Science (2): NSF, USPTO
- Financial (4): SEC_Filings, FDIC_Bank_Data, HMDA, IRS990
- Transportation (2): FAA, NHTS
- Political (3): FEC, LegScan, MIT_Election_Lab
- Social (1): Social_Media_Harvester
- Cultural (2): NEA, Cultural_Sentiment
- Business (1): Local_Business
- Civic (1): Google_Civic_Info
- Events (1): Events_Venues
- Recreation (1): Parks_Recreation
- Web (1): Web_Scraper
- Transit (1): Transit
- Technology (1): FCC_Broadband
- Media (1): GDELT
- Mobility (1): Opportunity_Insights
- Local Gov (1): Local_Gov_Finance

Usage:
    from krl_data_connectors.professional import FREDFullConnector
    
    fred = FREDFullConnector()  # License validated automatically
    data = fred.fetch(query_type="series", series_id="GDP")
"""

from .agricultural.usda_food_atlas import USDAFoodAtlasConnector

# Agricultural
from .agricultural.usda_nass import USDANASSConnector
from .agricultural.datagov_agricultural_full import DataGovAgriculturalFullConnector

# Business
from .business.local_business import LocalBusinessConnector
from .business.datagov_business_full import DataGovBusinessFullConnector

# Civic
from .civic.datagov_full import DataGovFullConnector
from .civic.google_civic_info import GoogleCivicInfoConnector
from .cultural.cultural_sentiment import CulturalSentimentConnector

# Cultural
from .cultural.nea import NEACulturalDataConnector
from .cultural.datagov_cultural_full import DataGovCulturalFullConnector

# Demographic
from .demographic.census_acs_detailed import CensusConnector as CensusACSDetailedConnector
from .demographic.datagov_demographic_full import DataGovDemographicFullConnector

# Economic
from .economic.bls_enhanced import BLSConnector as BLSEnhancedConnector
from .economic.census_bds import CensusBDSConnector
from .economic.world_bank_full import WorldBankConnector
from .economic.datagov_economic_full import DataGovEconomicFullConnector
from .education.college_scorecard import CollegeScorecardConnector
from .education.ipeds import IPEDSConnector

# Education
from .education.nces_ccd import NCESConnector as NCESCCDConnector
from .education.datagov_education_full import DataGovEducationFullConnector

# Energy
from .energy.eia_full import EIAConnector
from .energy.datagov_energy_full import DataGovEnergyFullConnector
from .environmental.epa_air_quality_full import EPAAirQualityConnector

# Environmental
from .environmental.epa_ejscreen import EJScreenConnector
from .environmental.epa_water_quality import WaterQualityConnector

# Events
from .events.events_venues import EventsVenuesConnector
from .events.datagov_events_full import DataGovEventsFullConnector
from .financial.fdic_bank_data import FDICConnector
from .financial.hmda import HMDAConnector
from .financial.irs990 import IRS990Connector

# Financial
from .financial.sec_filings import SECConnector
from .financial.datagov_financial_full import DataGovFinancialFullConnector

# Root-level
from .fred_full import FREDFullConnector
from .health.brfss import BRFSSConnector
from .health.county_health_rankings import CountyHealthRankingsConnector

# Health
from .health.hrsa import HRSAConnector
from .health.nih_reporter import NIHConnector
from .housing.eviction_lab import EvictionLabConnector

# Housing
from .housing.hud_fair_market_rents import HUDFMRConnector
from .housing.zillow_research import ZillowConnector
from .housing.datagov_housing_full import DataGovHousingFullConnector
from .labor.census_lehd_full import LEHDConnector

# Labor
from .labor.osha import OSHAConnector
from .labor.datagov_labor_full import DataGovLaborFullConnector

# Local Government
from .local_gov.local_gov_finance import LocalGovFinanceConnector
from .local_gov.datagov_local_gov_full import DataGovLocalGovFullConnector

# Media
from .media.gdelt import GDELTConnector
from .media.datagov_media_full import DataGovMediaFullConnector

# Mobility
from .mobility.opportunity_insights import OpportunityInsightsConnector
from .mobility.datagov_mobility_full import DataGovMobilityFullConnector

# Political
from .political.fec import FECConnector
from .political.legiscan import LegiScanConnector
from .political.mit_election_lab import MITElectionLabConnector
from .political.datagov_political_full import DataGovPoliticalFullConnector

# Recreation
from .recreation.parks_recreation import ParksRecreationConnector
from .recreation.datagov_recreation_full import DataGovRecreationFullConnector

# Science
from .science.nsf import NSFConnector
from .science.uspto import USPTOConnector
from .science.datagov_science_full import DataGovScienceFullConnector

# Social
from .social.social_media_harvester import SocialMediaHarvesterConnector
from .social.datagov_social_full import DataGovSocialFullConnector

# Technology
from .technology.fcc_broadband import FCCBroadbandConnector
from .technology.datagov_technology_full import DataGovTechnologyFullConnector

# Transit
from .transit.transit import TransitConnector
from .transit.datagov_transit_full import DataGovTransitFullConnector

# Transportation
from .transportation.faa import FAAConnector
from .transportation.nhts import NHTSConnector
from .transportation.datagov_transportation_full import DataGovTransportationFullConnector

# Web
from .web.web_scraper import WebScraperConnector
from .web.datagov_web_full import DataGovWebFullConnector

__all__ = [
    # Root
    "FREDFullConnector",
    # Economic
    "BLSEnhancedConnector",
    "WorldBankConnector",
    "CensusBDSConnector",
    "DataGovEconomicFullConnector",
    # Demographic
    "CensusACSDetailedConnector",
    "DataGovDemographicFullConnector",
    # Health
    "HRSAConnector",
    "CountyHealthRankingsConnector",
    "NIHConnector",
    "BRFSSConnector",
    # Labor
    "OSHAConnector",
    "LEHDConnector",
    "DataGovLaborFullConnector",
    # Environmental
    "EJScreenConnector",
    "WaterQualityConnector",
    "EPAAirQualityConnector",
    # Education
    "NCESCCDConnector",
    "CollegeScorecardConnector",
    "IPEDSConnector",
    "DataGovEducationFullConnector",
    # Housing
    "HUDFMRConnector",
    "ZillowConnector",
    "EvictionLabConnector",
    "DataGovHousingFullConnector",
    # Energy
    "EIAConnector",
    "DataGovEnergyFullConnector",
    # Agricultural
    "USDANASSConnector",
    "USDAFoodAtlasConnector",
    "DataGovAgriculturalFullConnector",
    # Science
    "NSFConnector",
    "USPTOConnector",
    "DataGovScienceFullConnector",
    # Financial
    "SECConnector",
    "FDICConnector",
    "HMDAConnector",
    "IRS990Connector",
    "DataGovFinancialFullConnector",
    # Transportation
    "FAAConnector",
    "NHTSConnector",
    "DataGovTransportationFullConnector",
    # Political
    "FECConnector",
    "LegiScanConnector",
    "MITElectionLabConnector",
    "DataGovPoliticalFullConnector",
    # Social
    "SocialMediaHarvesterConnector",
    "DataGovSocialFullConnector",
    # Cultural
    "NEACulturalDataConnector",
    "CulturalSentimentConnector",
    "DataGovCulturalFullConnector",
    # Business
    "LocalBusinessConnector",
    "DataGovBusinessFullConnector",
    # Civic
    "DataGovFullConnector",
    "GoogleCivicInfoConnector",
    # Events
    "EventsVenuesConnector",
    "DataGovEventsFullConnector",
    # Recreation
    "ParksRecreationConnector",
    "DataGovRecreationFullConnector",
    # Web
    "WebScraperConnector",
    "DataGovWebFullConnector",
    # Transit
    "TransitConnector",
    "DataGovTransitFullConnector",
    # Technology
    "FCCBroadbandConnector",
    "DataGovTechnologyFullConnector",
    # Media
    "GDELTConnector",
    "DataGovMediaFullConnector",
    # Mobility
    "OpportunityInsightsConnector",
    "DataGovMobilityFullConnector",
    # Local Government
    "LocalGovFinanceConnector",
    "DataGovLocalGovFullConnector",
]
