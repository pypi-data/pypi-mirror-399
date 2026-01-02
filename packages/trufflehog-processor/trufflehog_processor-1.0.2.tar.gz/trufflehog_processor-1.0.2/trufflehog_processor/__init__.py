"""
TruffleHog Processor - Process and deduplicate TruffleHog scan results

Simple usage:
    from trufflehog_processor import process_trufflehog_results
    
    results = process_trufflehog_results(json_output, custom_detector_names=['CustomRegex'])
"""

from .processor import process_trufflehog_results, Processor
from .deduplicator import deduplicate, Deduplicator
from .filter import apply_filters
from .get_final_json import get_final_json, get_final_json_dict

__version__ = "1.0.1"
__all__ = [
    'process_trufflehog_results',
    'Processor',
    'deduplicate',
    'Deduplicator',
    'apply_filters',
    'get_final_json',
    'get_final_json_dict'
]

