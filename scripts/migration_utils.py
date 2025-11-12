"""Utilities for migration validation, comparison, and statistics reporting."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Tuple


def validate_migrated_data(taxonomy: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate that migrated data follows ideal schema structure.
    
    Args:
        taxonomy: The migrated taxonomy dictionary
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    def check_node(node_data: Dict[str, Any], path: str = "") -> None:
        """Recursively check nodes for ideal schema compliance."""
        if not isinstance(node_data, dict):
            return
        
        # Check if this looks like a method node
        if 'name' in node_data or 'method_name' in node_data:
            # This is a method node - validate ideal structure
            if 'techniques' not in node_data or not node_data.get('techniques'):
                errors.append(f"{path}: Missing or empty 'techniques' field")
            
            if 'performance' not in node_data or not isinstance(node_data.get('performance'), dict):
                errors.append(f"{path}: Missing or invalid 'performance' field (must be dict)")
            else:
                perf = node_data['performance']
                required_perf_fields = ['latency_speedup', 'compression_ratio', 'accuracy_retention']
                for field in required_perf_fields:
                    if field not in perf:
                        errors.append(f"{path}: Missing 'performance.{field}' field")
            
            if 'validation' not in node_data or not isinstance(node_data.get('validation'), dict):
                errors.append(f"{path}: Missing or invalid 'validation' field (must be dict)")
            else:
                val = node_data['validation']
                if 'confidence' not in val:
                    errors.append(f"{path}: Missing 'validation.confidence' field")
                if 'sample_count' not in val:
                    errors.append(f"{path}: Missing 'validation.sample_count' field")
            
            if 'architecture' not in node_data:
                errors.append(f"{path}: Missing 'architecture' field")
            elif isinstance(node_data['architecture'], str):
                # Legacy format - should have been migrated to dict
                errors.append(f"{path}: 'architecture' is still a string (should be dict)")
            elif isinstance(node_data['architecture'], dict):
                arch = node_data['architecture']
                if 'family' not in arch or 'variant' not in arch:
                    errors.append(f"{path}: 'architecture' dict missing 'family' or 'variant'")
            
            if 'paper' not in node_data or not isinstance(node_data.get('paper'), dict):
                errors.append(f"{path}: Missing or invalid 'paper' field (must be dict)")
        
        # Recursively check nested structures
        if 'optimization_methods' in node_data:
            opt_methods = node_data['optimization_methods']
            if isinstance(opt_methods, dict):
                for category, category_data in opt_methods.items():
                    if isinstance(category_data, dict):
                        if 'methods' in category_data:
                            # Flat structure
                            for i, method in enumerate(category_data['methods']):
                                if isinstance(method, dict):
                                    check_node(method, f"{path}/{category}/methods[{i}]")
                        else:
                            # Nested structure
                            for subcat, subcat_data in category_data.items():
                                if isinstance(subcat_data, dict) and 'methods' in subcat_data:
                                    for i, method in enumerate(subcat_data['methods']):
                                        if isinstance(method, dict):
                                            check_node(method, f"{path}/{category}/{subcat}/methods[{i}]")
        
        # Check nested model families
        for key, value in node_data.items():
            if key not in ['optimization_methods', 'model_characteristics', 'calibration_free_status', 'relationships']:
                if isinstance(value, dict):
                    check_node(value, f"{path}/{key}" if path else key)
    
    check_node(taxonomy)
    return len(errors) == 0, errors


def compare_old_vs_new(old_taxonomy: Dict[str, Any], new_taxonomy: Dict[str, Any]) -> Dict[str, Any]:
    """Compare old and new taxonomies to show what changed.
    
    Args:
        old_taxonomy: The original taxonomy
        new_taxonomy: The migrated taxonomy
        
    Returns:
        Dictionary with comparison statistics
    """
    stats = {
        'nodes_migrated': 0,
        'nodes_with_techniques': 0,
        'nodes_with_performance': 0,
        'nodes_with_validation': 0,
        'nodes_with_architecture_dict': 0,
        'nodes_with_paper': 0,
        'warnings': []
    }
    
    def count_nodes(taxonomy: Dict[str, Any], is_new: bool = False) -> None:
        """Recursively count nodes and check migration status."""
        if not isinstance(taxonomy, dict):
            return
        
        # Check if this is a method node
        if 'name' in taxonomy or 'method_name' in taxonomy:
            if is_new:
                stats['nodes_migrated'] += 1
                if taxonomy.get('techniques'):
                    stats['nodes_with_techniques'] += 1
                if isinstance(taxonomy.get('performance'), dict):
                    stats['nodes_with_performance'] += 1
                if isinstance(taxonomy.get('validation'), dict):
                    stats['nodes_with_validation'] += 1
                if isinstance(taxonomy.get('architecture'), dict):
                    stats['nodes_with_architecture_dict'] += 1
                if isinstance(taxonomy.get('paper'), dict):
                    stats['nodes_with_paper'] += 1
        
        # Recursively process
        if 'optimization_methods' in taxonomy:
            opt_methods = taxonomy['optimization_methods']
            if isinstance(opt_methods, dict):
                for category_data in opt_methods.values():
                    if isinstance(category_data, dict):
                        if 'methods' in category_data:
                            for method in category_data['methods']:
                                if isinstance(method, dict):
                                    count_nodes(method, is_new)
                        else:
                            for subcat_data in category_data.values():
                                if isinstance(subcat_data, dict) and 'methods' in subcat_data:
                                    for method in subcat_data['methods']:
                                        if isinstance(method, dict):
                                            count_nodes(method, is_new)
        
        for value in taxonomy.values():
            if isinstance(value, dict):
                count_nodes(value, is_new)
    
    count_nodes(old_taxonomy, is_new=False)
    count_nodes(new_taxonomy, is_new=True)
    
    return stats


def generate_migration_report(
    old_taxonomy: Dict[str, Any],
    new_taxonomy: Dict[str, Any],
    validation_errors: List[str]
) -> str:
    """Generate a human-readable migration report.
    
    Args:
        old_taxonomy: Original taxonomy
        new_taxonomy: Migrated taxonomy
        validation_errors: List of validation errors
        
    Returns:
        Formatted report string
    """
    comparison = compare_old_vs_new(old_taxonomy, new_taxonomy)
    is_valid, errors = validate_migrated_data(new_taxonomy)
    
    report = []
    report.append("=" * 60)
    report.append("MIGRATION REPORT")
    report.append("=" * 60)
    report.append("")
    report.append(f"Nodes Migrated: {comparison['nodes_migrated']}")
    report.append(f"  - With techniques: {comparison['nodes_with_techniques']}")
    report.append(f"  - With performance dict: {comparison['nodes_with_performance']}")
    report.append(f"  - With validation dict: {comparison['nodes_with_validation']}")
    report.append(f"  - With architecture dict: {comparison['nodes_with_architecture_dict']}")
    report.append(f"  - With paper dict: {comparison['nodes_with_paper']}")
    report.append("")
    report.append(f"Validation Status: {'PASSED' if is_valid else 'FAILED'}")
    if errors:
        report.append(f"Validation Errors: {len(errors)}")
        for error in errors[:10]:  # Show first 10 errors
            report.append(f"  - {error}")
        if len(errors) > 10:
            report.append(f"  ... and {len(errors) - 10} more errors")
    report.append("")
    report.append("=" * 60)
    
    return "\n".join(report)

