"""
Filtering module for TruffleHog findings
"""

from typing import List, Dict, Any, Optional


# get_secret_value is imported from deduplicator to avoid duplication


def apply_filters(
    findings: List[Dict[str, Any]],
    filter_detectors: Optional[List[str]] = None,
    exclude_detectors: Optional[List[str]] = None,
    only_verified: bool = False
) -> List[Dict[str, Any]]:
    """
    Apply additional filters to findings
    
    Args:
        findings: List of findings to filter
        filter_detectors: Only keep findings from these detectors
        exclude_detectors: Exclude findings from these detectors
        only_verified: Only keep verified findings
        
    Returns:
        Filtered findings
    """
    filtered = findings
    
    # Filter: Only keep specified detectors
    if filter_detectors:
        filtered = [
            f for f in filtered
            if f.get('DetectorName', '') in filter_detectors
        ]
    
    # Exclude: Remove specified detectors
    if exclude_detectors:
        filtered = [
            f for f in filtered
            if f.get('DetectorName', '') not in exclude_detectors
        ]
    
    # Only verified
    if only_verified:
        filtered = [
            f for f in filtered
            if f.get('Verified') == True
        ]
    
    return filtered



