"""
Deduplication module for TruffleHog findings
"""

from typing import List, Dict, Any, Tuple


def get_secret_value(finding: Dict[str, Any]) -> str:
    """
    Extract secret value from finding for deduplication
    
    Args:
        finding: Finding dictionary
        
    Returns:
        Secret value (from Redacted or Raw field)
    """
    # Try Redacted first, fallback to Raw
    secret = finding.get('Redacted', '') or finding.get('Raw', '')
    return secret


def create_finding_key(finding: Dict[str, Any], strategy: str = 'value') -> str:
    """
    Create unique key for finding based on strategy
    
    Args:
        finding: Finding dictionary
        strategy: 'value' (secret only) or 'location' (secret + file + line)
        
    Returns:
        Unique key string
    """
    secret = get_secret_value(finding)
    
    if strategy == 'location':
        metadata = finding.get('SourceMetadata', {}).get('Data', {})
        filesystem = metadata.get('Filesystem', {})
        file = filesystem.get('file', '')
        line = filesystem.get('line', '')
        return f"{secret}:{file}:{line}"
    else:  # 'value' strategy
        return secret


def deduplicate_within_group(
    findings: List[Dict[str, Any]],
    strategy: str = 'value'
) -> List[Dict[str, Any]]:
    """
    Deduplicate findings within a single group
    
    Args:
        findings: List of findings from same group
        strategy: Deduplication strategy ('value' or 'location')
        
    Returns:
        Deduplicated findings
    """
    results = []
    seen_secrets = set()
    
    for finding in findings:
        secret = get_secret_value(finding)
        if secret:
            key = create_finding_key(finding, strategy)
            if key not in seen_secrets:
                seen_secrets.add(key)
                results.append(finding)
    
    return results


def deduplicate_custom_vs_not_verified(
    custom: List[Dict[str, Any]],
    not_verified: List[Dict[str, Any]],
    strategy: str = 'value'
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Deduplicate: If same secret in custom and not verified built-in,
    keep custom, remove not verified duplicate.
    
    Args:
        custom: List of custom detector findings
        not_verified: List of not verified built-in findings
        strategy: Deduplication strategy ('value' or 'location')
        
    Returns:
        Tuple of (custom_final, not_verified_remaining)
    """
    custom_final = []
    not_verified_remaining = []
    seen_custom_secrets = set()
    
    # Step 1: Add all custom findings
    for finding in custom:
        secret = get_secret_value(finding)
        if secret:
            key = create_finding_key(finding, strategy)
            seen_custom_secrets.add(key)
            custom_final.append(finding)
    
    # Step 2: Add not verified only if not duplicate of custom
    for finding in not_verified:
        secret = get_secret_value(finding)
        if secret:
            key = create_finding_key(finding, strategy)
            if key not in seen_custom_secrets:
                # Check if same secret value exists (for value strategy)
                if strategy == 'value':
                    exists = any(
                        get_secret_value(f) == secret
                        for f in custom_final
                    )
                    if not exists:
                        not_verified_remaining.append(finding)
                else:
                    not_verified_remaining.append(finding)
    
    return custom_final, not_verified_remaining


def deduplicate(
    verified: List[Dict[str, Any]],
    custom: List[Dict[str, Any]],
    strategy: str = 'value'
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Deduplicate findings: If same secret found by both verified and custom,
    keep verified, remove custom duplicate.
    
    Args:
        verified: List of verified findings
        custom: List of custom detector findings
        strategy: Deduplication strategy ('value' or 'location')
        
    Returns:
        Tuple of (deduplicated_findings, removed_duplicates)
    """
    results = []
    seen_secrets = set()
    removed = []
    
    # Step 1: Add all verified findings (highest priority)
    for finding in verified:
        secret = get_secret_value(finding)
        if secret:  # Only if secret exists
            key = create_finding_key(finding, strategy)
            if key not in seen_secrets:
                seen_secrets.add(key)
                results.append(finding)
            else:
                # Duplicate within verified group
                removed.append(finding)
    
    # Step 2: Add custom findings only if not duplicate of verified
    for finding in custom:
        secret = get_secret_value(finding)
        if secret:
            key = create_finding_key(finding, strategy)
            
            # Check if same location/key already in verified
            if key not in seen_secrets:
                # Check if same secret value exists (different location)
                if strategy == 'location':
                    # For location strategy, key already checked above
                    results.append(finding)
                else:
                    # For value strategy, check if secret value exists
                    exists = any(
                        get_secret_value(f) == secret
                        for f in results
                    )
                    if not exists:
                        results.append(finding)
                    else:
                        removed.append(finding)
            else:
                # Duplicate of verified finding
                removed.append(finding)
    
    return results, removed


class Deduplicator:
    """
    Class-based deduplicator for more control
    """
    
    def __init__(self, strategy: str = 'value'):
        """
        Args:
            strategy: 'value' (secret only) or 'location' (secret + file + line)
        """
        self.strategy = strategy
    
    def deduplicate(
        self,
        verified: List[Dict[str, Any]],
        custom: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Deduplicate with configured strategy"""
        return deduplicate(verified, custom, self.strategy)
    
    def get_secret(self, finding: Dict[str, Any]) -> str:
        """Get secret value from finding"""
        return get_secret_value(finding)
    
    def create_key(self, finding: Dict[str, Any]) -> str:
        """Create key for finding"""
        return create_finding_key(finding, self.strategy)

