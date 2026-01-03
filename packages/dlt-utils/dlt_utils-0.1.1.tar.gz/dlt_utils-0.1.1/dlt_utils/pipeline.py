"""
Pipeline helper utilities for dlt pipelines.

This module provides common functionality for running dlt pipelines.

Usage:
    from dlt_utils import validate_refresh_args, filter_resources, print_resources
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)


def validate_refresh_args(
    refresh: str | None,
    resources_filter: list[str] | None,
) -> None:
    """
    Validate that refresh arguments are used correctly.
    
    Raises ValueError if drop_sources is used with a resource filter,
    as this would drop ALL tables but only reload selected resources.
    
    Args:
        refresh: The refresh mode ('drop_sources' or 'drop_resources').
        resources_filter: List of resources being loaded (None = all).
        
    Raises:
        ValueError: If drop_sources is used with a resource filter.
    """
    if refresh == "drop_sources" and resources_filter:
        raise ValueError(
            f"--refresh drop_sources cannot be used with --resources filter. "
            f"This would drop ALL tables but only reload selected resources. "
            f"Use --refresh drop_resources to only drop and rebuild specific resources, "
            f"or remove --resources to do a full rebuild of all resources."
        )


def filter_resources(
    available_resources: list[str],
    requested_resources: list[str] | None,
) -> list[str]:
    """
    Filter available resources based on requested resources.
    
    Args:
        available_resources: List of all available resource names.
        requested_resources: List of requested resources (None = all).
        
    Returns:
        List of valid resources to load.
        
    Raises:
        ValueError: If no valid resources are found.
    """
    if requested_resources is None:
        return available_resources
    
    valid_resources = [r for r in requested_resources if r in available_resources]
    
    if not valid_resources:
        raise ValueError(
            f"No valid resources found. "
            f"Requested: {requested_resources}. "
            f"Available: {available_resources}"
        )
    
    # Log any requested resources that weren't found
    invalid = set(requested_resources) - set(valid_resources)
    if invalid:
        logger.warning(f"Ignored invalid resources: {invalid}")
    
    return valid_resources


def print_resources(source: Any) -> None:
    """
    Print available resources from a dlt source and exit.
    
    Args:
        source: A dlt source object with a resources attribute.
    """
    available_resources = sorted(get_resource_names(source))
    
    print("\nAvailable resources:")
    print("-" * 40)
    for resource in available_resources:
        print(f"  - {resource}")
    print("-" * 40)
    print(f"\nTotal: {len(available_resources)} resources")


def get_resource_names(source: Any) -> list[str]:
    """
    Get list of resource names from a dlt source.
    
    Args:
        source: A dlt source object with a resources attribute.
        
    Returns:
        List of resource names.
    """
    return [r.name for r in source.resources.values()]


def mask_sensitive_value(value: str | None, show_chars: int = 2) -> str:
    """
    Mask a sensitive value (like API key) showing only first and middle characters.
    
    Args:
        value: The value to mask.
        show_chars: Number of characters to show at start and middle.
        
    Returns:
        Masked value like "ab..cd..***" or "N/A" if not set.
    """
    if not value:
        return "N/A"
    
    if len(value) < 6:
        return value[:1] + "***"
    
    mid = len(value) // 2
    return f"{value[:show_chars]}..{value[mid:mid+show_chars]}..***"
