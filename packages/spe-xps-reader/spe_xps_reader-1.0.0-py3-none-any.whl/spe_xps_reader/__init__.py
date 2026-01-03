"""
spe-xps-reader: A Python library for reading PHI Instruments SPE files for XPS data analysis

Supports multiple PHI instrument formats:
- PHI VersaProbe III (float32)
- PHI X-tool (float64)
- PHI Quantum 2000 (float64 at end)
"""

from .reader import (
    parse_spe_file,
    detect_data_format,
    read_region_data,
    calculate_transmission_corrected_data,
    extract_all_regions
)

__version__ = "1.0.0"
__author__ = "Gwilherm Kerherve"
__license__ = "GPL-3.0"

__all__ = [
    'parse_spe_file',
    'detect_data_format',
    'read_region_data',
    'calculate_transmission_corrected_data',
    'extract_all_regions',
]
