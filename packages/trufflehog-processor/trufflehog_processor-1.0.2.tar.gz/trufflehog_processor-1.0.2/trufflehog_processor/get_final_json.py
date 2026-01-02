"""
Utility function to get final JSON output from TruffleHog results
"""

import json
from typing import Dict, Any, List, Optional
from .processor import process_trufflehog_results


def get_final_json(
    trufflehog_output: str,
    custom_detector_names: List[str],
    deduplicate: bool = True,
    verbose: bool = False,
    filter_detectors: Optional[List[str]] = None,
    exclude_detectors: Optional[List[str]] = None,
    only_verified: bool = False
) -> str:
    """
    Get final JSON output from TruffleHog results
    
    Args:
        trufflehog_output: TruffleHog JSON output
        custom_detector_names: List of custom detector names
        deduplicate: Whether to deduplicate
        verbose: If True, return complete JSON with all sections. If False (default), return only verified and custom sections
        filter_detectors: Only keep findings from these detectors
        exclude_detectors: Exclude findings from these detectors
        only_verified: Only keep verified findings
        
    Returns:
        JSON string
    """
    results = process_trufflehog_results(
        trufflehog_output,
        custom_detector_names,
        deduplicate_results=deduplicate,
        filter_detectors=filter_detectors,
        exclude_detectors=exclude_detectors,
        only_verified=only_verified
    )
    
    if verbose:
        # Verbose mode: Return complete results with all sections (structured JSON)
        return json.dumps(results, indent=2, default=str)
    else:
        # Default: Return findings in TruffleHog JSONL format (pretty-printed, one JSON per line)
        all_findings = results['verified'] + results['custom']
        # Return as JSONL with pretty-printing (one JSON object per line, but formatted)
        jsonl_lines = [json.dumps(finding, indent=2, default=str) for finding in all_findings]
        return '\n'.join(jsonl_lines)


def get_final_json_dict(
    trufflehog_output: str,
    custom_detector_names: List[str],
    deduplicate: bool = True,
    verbose: bool = False,
    filter_detectors: Optional[List[str]] = None,
    exclude_detectors: Optional[List[str]] = None,
    only_verified: bool = False
) -> Dict[str, Any]:
    """
    Get final JSON as dictionary (not string)
    
    Args:
        trufflehog_output: TruffleHog JSON output
        custom_detector_names: List of custom detector names
        deduplicate: Whether to deduplicate
        verbose: If True, return complete JSON with all sections. If False (default), return only verified and custom sections
        filter_detectors: Only keep findings from these detectors
        exclude_detectors: Exclude findings from these detectors
        only_verified: Only keep verified findings
        
    Returns:
        Dictionary with processed results
    """
    results = process_trufflehog_results(
        trufflehog_output,
        custom_detector_names,
        deduplicate_results=deduplicate,
        filter_detectors=filter_detectors,
        exclude_detectors=exclude_detectors,
        only_verified=only_verified
    )
    
    if verbose:
        # Verbose mode: Return complete results (structured dict)
        return results
    else:
        # Default: Return findings as list (TruffleHog format)
        return results['verified'] + results['custom']

