"""
Main processor module for TruffleHog results
"""

import json
from typing import List, Dict, Any, Optional
from .deduplicator import (
    deduplicate,
    get_secret_value,
    deduplicate_within_group,
    deduplicate_custom_vs_not_verified
)
from .filter import apply_filters


def parse_json_output(json_output: str) -> List[Dict[str, Any]]:
    """
    Parse TruffleHog JSON output (one JSON object per line or multi-line JSON)
    
    Args:
        json_output: String containing JSON lines or list of JSON strings
        
    Returns:
        List of parsed finding dictionaries
    """
    findings = []
    
    if isinstance(json_output, str):
        # Try to parse as JSONL first (one JSON per line)
        lines = json_output.strip().split('\n')
        
        # Check if it's JSONL format (each line is valid JSON)
        jsonl_mode = True
        for line in lines[:3]:  # Check first 3 lines
            if line.strip():
                try:
                    json.loads(line)
                except json.JSONDecodeError:
                    jsonl_mode = False
                    break
        
        if jsonl_mode:
            # JSONL format: one JSON object per line
            for line in lines:
                if line.strip():
                    try:
                        findings.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        else:
            # Multi-line JSON: try to parse entire string or split by }{ pattern
            # Try parsing as array first
            try:
                data = json.loads(json_output)
                if isinstance(data, list):
                    findings = data
                elif isinstance(data, dict):
                    findings = [data]
            except json.JSONDecodeError:
                # Try splitting by }{ pattern (common in JSONL with multi-line objects)
                import re
                # Split on }{ but keep the braces
                parts = re.split(r'}\s*{', json_output)
                for i, part in enumerate(parts):
                    if i == 0:
                        part = part + '}'
                    elif i == len(parts) - 1:
                        part = '{' + part
                    else:
                        part = '{' + part + '}'
                    try:
                        findings.append(json.loads(part))
                    except json.JSONDecodeError:
                        continue
    elif isinstance(json_output, list):
        # Already a list, parse each item
        for item in json_output:
            if isinstance(item, str):
                try:
                    findings.append(json.loads(item))
                except json.JSONDecodeError:
                    continue
            elif isinstance(item, dict):
                findings.append(item)
    
    return findings


def separate_verified_custom(
    findings: List[Dict[str, Any]],
    custom_detector_names: List[str]
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Separate findings into verified and custom detector groups
    
    Args:
        findings: List of findings
        custom_detector_names: List of custom detector names to identify
        
    Returns:
        Tuple of (verified_findings, custom_findings)
    """
    verified = []
    custom = []
    
    for finding in findings:
        is_verified = finding.get('Verified') == True
        detector_name = finding.get('DetectorName', '')
        is_custom = detector_name in custom_detector_names
        
        if is_verified:
            verified.append(finding)
        elif is_custom:
            custom.append(finding)
    
    return verified, custom


def process_trufflehog_results(
    json_output: str,
    custom_detector_names: List[str],
    deduplicate_results: bool = True,
    filter_detectors: Optional[List[str]] = None,
    exclude_detectors: Optional[List[str]] = None,
    only_verified: bool = False
) -> Dict[str, Any]:
    """
    Main function to process TruffleHog results
    
    Args:
        json_output: TruffleHog JSON output (string or list)
        custom_detector_names: List of custom detector names (e.g., ['CustomRegex'])
        deduplicate_results: Whether to deduplicate findings
        
    Returns:
        Dictionary with processed results:
        {
            'verified': [...],
            'custom': [...],
            'deduplicated': [...],
            'removed': {
                'duplicates': [...]
            },
            'summary': {...}
        }
    """
    # Parse JSON - Get ALL findings (no initial filtering)
    all_findings = parse_json_output(json_output)
    
    # If deduplicate=False, skip all deduplication and just separate
    if not deduplicate_results:
        verified = []
        custom_regex = []
        not_verified_builtin = []
        
        for finding in all_findings:
            is_verified = finding.get('Verified') == True
            detector_name = finding.get('DetectorName', '')
            is_custom = detector_name in custom_detector_names
            
            if is_verified:
                verified.append(finding)
            elif is_custom:
                custom_regex.append(finding)
            else:
                not_verified_builtin.append(finding)
        
        # For deduplicate=False, return as-is (no deduplication)
        verified_final = verified
        custom_final = custom_regex
        not_verified_final = not_verified_builtin
    else:
        # Step 1: Separate into 3 groups
        verified = []
        custom_regex = []
        not_verified_builtin = []
        
        for finding in all_findings:
            is_verified = finding.get('Verified') == True
            detector_name = finding.get('DetectorName', '')
            is_custom = detector_name in custom_detector_names
            
            if is_verified:
                verified.append(finding)
            elif is_custom:
                custom_regex.append(finding)
            else:
                # Not verified and not custom = built-in not verified
                not_verified_builtin.append(finding)
        
        # Step 2: Handle verified custom findings
        # If a finding is both verified AND custom, keep it in verified, remove from custom
        # Fix: Only keep custom findings that don't match verified secrets
        verified_secrets = {get_secret_value(f) for f in verified if get_secret_value(f)}
        custom_only = [
            f for f in custom_regex
            if get_secret_value(f) not in verified_secrets
        ]
        
        # Step 3: Deduplicate within groups
        verified_dedup = deduplicate_within_group(verified)
        custom_dedup = deduplicate_within_group(custom_only)
        not_verified_dedup = deduplicate_within_group(not_verified_builtin)
        
        # Step 4: Phase 1 - Deduplicate Verified vs Custom
        # If same secret in verified and custom, keep verified, remove custom
        deduplicated_phase1, removed_phase1 = deduplicate(verified_dedup, custom_dedup)
        
        # Separate back into verified and custom
        # Fix: If a finding is verified, it should NOT appear in custom list
        verified_final = [f for f in deduplicated_phase1 if f.get('Verified') == True]
        # Only include custom findings that are NOT verified
        custom_after_phase1 = [
            f for f in deduplicated_phase1 
            if f.get('DetectorName') in custom_detector_names 
            and f.get('Verified') != True
        ]
        
        # Step 5: Phase 2 - Deduplicate Custom vs Not Verified Built-in
        # If same secret in custom and not verified, keep custom, remove not verified
        custom_final, not_verified_after_phase2 = deduplicate_custom_vs_not_verified(
            custom_after_phase1, not_verified_dedup
        )
        
        # Step 6: Phase 3 - Remove Not Verified that match Verified
        # If same secret in not verified and verified, remove not verified
        verified_secrets_final = {get_secret_value(f) for f in verified_final if get_secret_value(f)}
        not_verified_final = [
            f for f in not_verified_after_phase2
            if get_secret_value(f) not in verified_secrets_final
        ]
        
    
    # Step 7: Final - Discard all remaining not verified built-in
    # (not_verified_final is already filtered, but we don't include it in output)
    
    # Use verified_final and custom_final for output
    verified = verified_final
    custom = custom_final
    
    # Final deduplicated list (no redundant deduplication needed)
    deduplicated = verified + custom
    removed_duplicates = []
    
    # Additional filtering options
    if filter_detectors or exclude_detectors or only_verified:
        original_count = len(deduplicated)
        deduplicated = apply_filters(
            deduplicated,
            filter_detectors=filter_detectors,
            exclude_detectors=exclude_detectors,
            only_verified=only_verified
        )
        removed_by_filter = original_count - len(deduplicated)
    else:
        removed_by_filter = 0
    
    # Calculate summary
    total_input = len(all_findings)
    verified_count = len(verified)
    custom_count = len(custom)
    
    final_count = len(deduplicated)
    
    if deduplicate_results:
        not_verified_builtin_count = len(not_verified_builtin)
        not_verified_removed = len(not_verified_builtin) - len(not_verified_final)
        # Calculate duplicates removed: total_input - final_count - not_verified_removed - filtered_out
        duplicates_removed = total_input - final_count - not_verified_removed - removed_by_filter
    else:
        not_verified_builtin_count = len(not_verified_final)
        not_verified_removed = 0
        duplicates_removed = 0
    
    return {
        'verified': verified,
        'custom': custom,
        'deduplicated': deduplicated,
        'removed': {
            'duplicates': removed_duplicates
        },
        'summary': {
            'total_input': total_input,
            'verified_count': verified_count,
            'custom_count': custom_count,
            'not_verified_builtin_count': not_verified_builtin_count,
            'not_verified_removed': not_verified_removed,
            'final_count': final_count,
            'duplicates_removed': duplicates_removed,
            'filtered_out': removed_by_filter
        }
    }


class Processor:
    """
    Class-based processor for more advanced usage
    """
    
    def __init__(
        self,
        custom_detector_names: List[str],
        deduplicate: bool = True
    ):
        self.custom_detector_names = custom_detector_names
        self.deduplicate = deduplicate
    
    def process(self, json_output: str) -> Dict[str, Any]:
        """
        Process TruffleHog results with configured settings
        """
        return process_trufflehog_results(
            json_output,
            self.custom_detector_names,
            deduplicate_results=self.deduplicate,
        )
    
    def parse(self, json_output: str) -> List[Dict[str, Any]]:
        """Parse JSON output only"""
        return parse_json_output(json_output)
    
    def separate(self, findings: List[Dict[str, Any]]) -> tuple:
        """Separate findings into verified and custom"""
        return separate_verified_custom(findings, self.custom_detector_names)

