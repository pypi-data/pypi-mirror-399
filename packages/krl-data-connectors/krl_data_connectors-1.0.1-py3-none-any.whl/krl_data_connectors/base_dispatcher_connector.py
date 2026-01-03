# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ and KRL Data Connectors™ are trademarks of Deloatch, Williams, Faison, & Parker, LLLP.
# Deloatch, Williams, Faison, & Parker, LLLP
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Base Dispatcher Connector

Provides base class for connectors that use the dispatcher pattern:
- fetch() acts as a router/switchboard based on parameters
- Returns pd.DataFrame (combines data retrieval + transformation)
- Routes to specific methods based on dispatch parameter

This pattern is used by connectors like:
- HUD FMR (routes by data_type)
- CBP (routes by geography)
- NCES (routes by data_type)
- LEHD (routes by data_type)
- FEC (routes by query_type)
"""

from typing import Any, Dict, Optional

import pandas as pd

from .base_connector import BaseConnector


class BaseDispatcherConnector(BaseConnector):
    """
    Base class for connectors using dispatcher pattern.

    Dispatcher connectors differ from standard connectors:

    Standard Pattern:
        fetch() -> dict/list (raw API response)
        get_X() -> DataFrame (transforms raw data)

    Dispatcher Pattern:
        fetch() -> DataFrame (routes to get_X, returns transformed data)
        get_X() -> DataFrame (handles API + transformation)

    Subclasses must define:
        DISPATCH_PARAM: str - Parameter name used for routing
        DISPATCH_MAP: Dict[str, str] - Maps param values to method names

    Example:
        class MyDispatcherConnector(BaseDispatcherConnector):
            DISPATCH_PARAM = "data_type"
            DISPATCH_MAP = {
                "schools": "get_school_data",
                "enrollment": "get_enrollment_data",
            }

            def get_school_data(self, **kwargs) -> pd.DataFrame:
                # Implementation
                pass
    """

    # Subclasses MUST override these
    DISPATCH_PARAM: str = None
    DISPATCH_MAP: Dict[str, str] = None

    def __init__(self, *args, **kwargs):
        """Initialize dispatcher connector and validate configuration."""
        super().__init__(*args, **kwargs)
        self._validate_dispatch_config()

    def _validate_dispatch_config(self) -> None:
        """
        Validate that dispatcher configuration is properly defined.

        Raises:
            NotImplementedError: If DISPATCH_PARAM or DISPATCH_MAP not defined
        """
        if self.DISPATCH_PARAM is None:
            raise NotImplementedError(
                f"{self.__class__.__name__} must define DISPATCH_PARAM class attribute. "
                f"Example: DISPATCH_PARAM = 'data_type'"
            )

        if self.DISPATCH_MAP is None or not self.DISPATCH_MAP:
            raise NotImplementedError(
                f"{self.__class__.__name__} must define DISPATCH_MAP class attribute. "
                f"Example: DISPATCH_MAP = {{'type1': 'get_type1_data', 'type2': 'get_type2_data'}}"
            )

        # Validate that all mapped methods exist
        for dispatch_value, method_name in self.DISPATCH_MAP.items():
            if not hasattr(self, method_name):
                raise NotImplementedError(
                    f"{self.__class__.__name__}.DISPATCH_MAP references method '{method_name}' "
                    f"for dispatch value '{dispatch_value}', but method does not exist"
                )

    def fetch(self, **kwargs) -> pd.DataFrame:
        """
        Dispatcher fetch that routes to appropriate method.

        This method acts as a switchboard/router, examining the dispatch
        parameter and calling the appropriate data-specific method.

        Args:
            **kwargs: Must include dispatch parameter (defined by DISPATCH_PARAM)
                     plus any additional parameters required by routed method

        Returns:
            DataFrame from the routed method

        Raises:
            ValueError: If dispatch parameter missing or invalid

        Example:
            >>> # If DISPATCH_PARAM = "data_type" and DISPATCH_MAP = {"schools": "get_school_data"}
            >>> df = connector.fetch(data_type="schools", state="RI", year=2023)
        """
        dispatch_value = kwargs.get(self.DISPATCH_PARAM)

        if not dispatch_value:
            valid_values = ", ".join(f"'{v}'" for v in self.DISPATCH_MAP.keys())
            raise ValueError(
                f"Parameter '{self.DISPATCH_PARAM}' is required for {self.__class__.__name__}.fetch(). "
                f"Valid values: {valid_values}"
            )

        if dispatch_value not in self.DISPATCH_MAP:
            valid_values = ", ".join(f"'{v}'" for v in self.DISPATCH_MAP.keys())
            raise ValueError(
                f"Invalid {self.DISPATCH_PARAM}: '{dispatch_value}'. "
                f"Valid values: {valid_values}"
            )

        # Get the method to call
        method_name = self.DISPATCH_MAP[dispatch_value]
        method = getattr(self, method_name)

        self.logger.info(
            f"Dispatching fetch to {method_name}",
            extra={
                "dispatch_param": self.DISPATCH_PARAM,
                "dispatch_value": dispatch_value,
                "method": method_name,
            },
        )

        # Remove dispatch parameter from kwargs before calling target method
        # (target method doesn't need to know about routing)
        kwargs_copy = kwargs.copy()
        kwargs_copy.pop(self.DISPATCH_PARAM, None)

        # Call the routed method with remaining kwargs
        return method(**kwargs_copy)

    def get_dispatch_info(self) -> Dict[str, Any]:
        """
        Get information about this dispatcher's routing configuration.

        Returns:
            Dict with dispatch parameter, available values, and method mappings

        Example:
            >>> info = connector.get_dispatch_info()
            >>> print(f"Route by: {info['dispatch_param']}")
            >>> print(f"Options: {info['valid_values']}")
        """
        return {
            "dispatch_param": self.DISPATCH_PARAM,
            "valid_values": list(self.DISPATCH_MAP.keys()),
            "method_map": self.DISPATCH_MAP.copy(),
            "connector_type": "dispatcher",
        }
