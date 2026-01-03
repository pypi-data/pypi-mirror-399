"""
SPE File Reader Module for XPS Data Analysis
PHI Instruments Binary Format (.spe files)

Supports multiple PHI instrument formats:
- PHI VersaProbe III: float32 (4 bytes), data after metadata header
- PHI X-tool: float64 (8 bytes), data after metadata header  
- PHI Quantum 2000: float64 (8 bytes), data at END of binary section

SPE files store XPS spectral data with regions in a text header (SOFH...EOFH)
followed by binary intensity data. Data is stored and output as Binding Energy.

Author: Gwilherm Kerherve
License: GPL-3.0
"""

import os
import re
import struct
import numpy as np


def parse_spe_file(file_path):
    """
    Parse a PHI SPE file and return extracted data.
    
    Args:
        file_path: Path to .spe file
        
    Returns:
        dict with keys:
            - regions: List of region dictionaries
            - metadata: Experimental metadata dict
            - binary_data: Raw binary data section
            - source_energy: X-ray source energy in eV
            - transmission_coeffs: Tuple (a, b) for transmission correction
            - instrument_model: Instrument model string
    """
    with open(file_path, 'rb') as f:
        content = f.read()
    
    # Extract header section
    header_match = re.search(rb'SOFH(.*?)EOFH', content, re.DOTALL)
    if not header_match:
        raise ValueError("Cannot find header section (SOFH...EOFH)")
    
    header_text = header_match.group(1).decode('utf-8', errors='ignore')
    header_lines = [line.strip() for line in header_text.strip().split('\n')]
    
    # Extract intensity calibration coefficients (transmission function)
    a, b = 31.826, 0.229  # Default values
    for line in header_lines:
        if 'IntensityCalCoeff:' in line:
            try:
                _, coeffs = line.split(':', 1)
                parts = coeffs.strip().split()
                if len(parts) >= 2:
                    a = float(parts[0])
                    b = float(parts[1])
            except:
                pass
            break
    
    # Extract source energy
    source_energy = 1486.6  # Default Al K-alpha
    for line in header_lines:
        if 'XraySource:' in line:
            if 'Al' in line:
                source_energy = 1486.6
            elif 'Mg' in line:
                source_energy = 1253.6
            # Try to extract exact value if present
            try:
                parts = line.split()
                for part in parts:
                    try:
                        val = float(part)
                        if 1200 < val < 1600:
                            source_energy = val
                            break
                    except:
                        pass
            except:
                pass
            break
    
    # Get instrument model
    instrument_model = "Unknown"
    for line in header_lines:
        if 'InstrumentModel:' in line:
            instrument_model = line.split(':', 1)[1].strip()
            break
    
    # Find active spectral regions
    regions = []
    for line in header_lines:
        if line.startswith('SpectralRegDef:') and 'Full' not in line and '2:' not in line:
            parts = line.split()
            if len(parts) >= 9:
                region = {
                    'number': int(parts[1]),
                    'name': parts[3],
                    'atomic_number': int(parts[4]) if parts[4].lstrip('-').isdigit() else 0,
                    'num_points': int(parts[5]),
                    'step': float(parts[6]),
                    'start_energy': float(parts[7]),
                    'end_energy': float(parts[8])
                }
                
                # Normalize region name
                if region['name'] == 'Su1s':
                    region['name'] = 'Survey'
                
                regions.append(region)
    
    if not regions:
        raise ValueError("No spectral regions found in file")
    
    # Extract metadata
    metadata = {
        'Sample ID': os.path.basename(file_path),
        'Date': '1970/1/1',
        'Time': '0:0:0',
        'Technique': 'XPS',
        'Instrument': instrument_model,
        'Source Label': 'Al' if source_energy > 1400 else 'Mg',
        'Source Energy': str(source_energy),
        'Pass Energy': '224',
        'Work Function': '4.339',
        'Analyzer Mode': 'FAT',
        'X Label': 'Binding Energy',
        'X Units': 'eV',
        'Num Scans': '1',
        'Collection Time': '0.16',
        'Y Unit': 'counts',
    }
    
    # Update metadata from header
    for line in header_lines:
        if 'FileDateTime:' in line:
            parts = line.split(':', 1)[1].strip().split()
            if len(parts) >= 2:
                metadata['Date'] = parts[0]
                metadata['Time'] = parts[1]
        elif 'FileDate:' in line:
            metadata['Date'] = line.split(':', 1)[1].strip().replace(' ', '/')
        elif 'PassEnergy:' in line:
            try:
                metadata['Pass Energy'] = line.split(':', 1)[1].strip().split()[0]
            except:
                pass
        elif 'AnalyserWorkFcn:' in line or 'WorkFunction:' in line:
            try:
                metadata['Work Function'] = line.split(':', 1)[1].strip().split()[0]
            except:
                pass
        elif 'AnalyserMode:' in line:
            metadata['Analyzer Mode'] = line.split(':', 1)[1].strip()
        elif 'XrayBeamDiameter:' in line:
            try:
                size = line.split(':', 1)[1].strip().split()[0]
                metadata['Source width X'] = size
                metadata['Source width Y'] = size
            except:
                pass
        elif 'Comments:' in line:
            metadata['Block Comment'] = line.split(':', 1)[1].strip()
    
    # Get binary data section
    data_start = content.find(b'EOFH') + 4
    binary_data = content[data_start:]
    
    return {
        'regions': regions,
        'metadata': metadata,
        'binary_data': binary_data,
        'source_energy': source_energy,
        'transmission_coeffs': (a, b),
        'instrument_model': instrument_model
    }


def detect_data_format(binary_data, regions):
    """
    Auto-detect the data format and offset in the binary section.
    
    Args:
        binary_data: Binary data section after EOFH marker
        regions: List of region dictionaries
        
    Returns:
        dict with keys: data_type ('float32' or 'float64'), 
                       bytes_per_val (4 or 8),
                       first_offset (byte offset to start of data)
    """
    total_points = sum(r['num_points'] for r in regions)
    first_region = regions[0]
    
    def try_find_offset_standard(dtype, bytes_per_val):
        """Try to find data offset for standard formats."""
        fmt = '<f' if dtype == 'float32' else '<d'
        num_points = first_region['num_points']
        
        first_region_size = num_points * bytes_per_val
        max_offset = len(binary_data) - first_region_size
        if max_offset < 0:
            return None
        max_offset = min(2000, max_offset)
        
        for offset in range(0, max_offset + 1, 2):
            try:
                values = []
                valid = True
                for i in range(min(20, num_points)):
                    byte_pos = offset + i * bytes_per_val
                    if byte_pos + bytes_per_val > len(binary_data):
                        valid = False
                        break
                    val = struct.unpack(fmt, binary_data[byte_pos:byte_pos + bytes_per_val])[0]
                    if not (1 < val < 1e8):
                        valid = False
                        break
                    values.append(val)
                
                if valid and len(values) >= 10 and max(values) - min(values) > 1:
                    # Verify all points in first region
                    all_valid = True
                    for i in range(num_points):
                        byte_pos = offset + i * bytes_per_val
                        if byte_pos + bytes_per_val > len(binary_data):
                            all_valid = False
                            break
                        val = struct.unpack(fmt, binary_data[byte_pos:byte_pos + bytes_per_val])[0]
                        if not (0 <= val < 1e8):
                            all_valid = False
                            break
                    
                    if all_valid:
                        return offset
            except:
                pass
        
        return None
    
    def try_quantum2000_format():
        """Try Quantum 2000 format: float64 data at END of binary section."""
        expected_size = total_points * 8
        if expected_size > len(binary_data):
            return None
        
        offset = len(binary_data) - expected_size
        num_points = first_region['num_points']
        
        try:
            values = []
            valid = True
            for i in range(min(20, num_points)):
                byte_pos = offset + i * 8
                val = struct.unpack('<d', binary_data[byte_pos:byte_pos + 8])[0]
                if not (0 < val < 1e8):
                    valid = False
                    break
                values.append(val)
            
            if valid and len(values) >= 10 and max(values) - min(values) > 1:
                return offset
        except:
            pass
        
        return None
    
    # Try different formats
    # Method 1: Try float32 (VersaProbe format)
    offset = try_find_offset_standard('float32', 4)
    if offset is not None:
        return {
            'data_type': 'float32',
            'bytes_per_val': 4,
            'first_offset': offset
        }
    
    # Method 2: Try float64 standard (X-tool format)
    offset = try_find_offset_standard('float64', 8)
    if offset is not None:
        return {
            'data_type': 'float64',
            'bytes_per_val': 8,
            'first_offset': offset
        }
    
    # Method 3: Try Quantum 2000 format (float64 at end)
    offset = try_quantum2000_format()
    if offset is not None:
        return {
            'data_type': 'float64',
            'bytes_per_val': 8,
            'first_offset': offset
        }
    
    raise ValueError("Could not detect data format or find valid data offset")


def read_region_data(binary_data, region, offset, data_type, bytes_per_val):
    """
    Read intensity data for a single region.
    
    Args:
        binary_data: Binary data section
        region: Region dictionary
        offset: Byte offset to start of region data
        data_type: 'float32' or 'float64'
        bytes_per_val: 4 or 8
        
    Returns:
        List of intensity values (floats)
    """
    fmt = '<f' if data_type == 'float32' else '<d'
    num_points = region['num_points']
    
    intensity_values = []
    for j in range(num_points):
        data_offset = offset + (j * bytes_per_val)
        if data_offset + bytes_per_val <= len(binary_data):
            try:
                val = struct.unpack(fmt, binary_data[data_offset:data_offset + bytes_per_val])[0]
                if 0 <= val < 1e8:
                    intensity_values.append(val)
                else:
                    intensity_values.append(0.0)
            except:
                intensity_values.append(0.0)
        else:
            intensity_values.append(0.0)
    
    return intensity_values


def calculate_transmission_corrected_data(region, intensity_values, source_energy, transmission_coeffs):
    """
    Calculate binding energies, transmission function, and corrected intensities.
    
    Args:
        region: Region dictionary with start_energy, end_energy, num_points
        intensity_values: List of raw intensity values
        source_energy: X-ray source energy in eV
        transmission_coeffs: Tuple (a, b) for transmission function
        
    Returns:
        dict with keys:
            - be_values: Binding energy values (list)
            - raw_intensities: Raw intensity values (list)
            - corrected_intensities: Transmission-corrected intensities (list)
            - transmission_values: Transmission function values (list)
    """
    a, b = transmission_coeffs
    num_points = region['num_points']
    
    # Calculate energy values
    be_values = np.linspace(region['start_energy'], region['end_energy'], num_points)
    
    # Calculate kinetic energies
    ke_values = source_energy - be_values
    
    # Protect against negative or zero KE values
    ke_values = np.maximum(ke_values, 1.0)
    
    # Calculate transmission function: T = a * KE^(-b)
    transmission_values = a * np.power(ke_values, -b)
    
    # Apply transmission correction
    corrected_intensities = np.array(intensity_values) / transmission_values
    
    return {
        'be_values': be_values.tolist(),
        'raw_intensities': intensity_values,
        'corrected_intensities': corrected_intensities.tolist(),
        'transmission_values': transmission_values.tolist()
    }


def extract_all_regions(file_path):
    """
    Complete extraction of all regions from a SPE file.
    
    Args:
        file_path: Path to .spe file
        
    Returns:
        dict with keys:
            - regions_data: List of region data dictionaries
            - metadata: Global metadata dictionary
            - instrument_model: Instrument model string
    """
    # Parse file
    parsed = parse_spe_file(file_path)
    
    # Detect data format
    format_info = detect_data_format(parsed['binary_data'], parsed['regions'])
    
    # Calculate offsets for all regions (data is contiguous)
    region_offsets = []
    current_offset = format_info['first_offset']
    for region in parsed['regions']:
        region_offsets.append(current_offset)
        current_offset += region['num_points'] * format_info['bytes_per_val']
    
    # Extract data for each region
    regions_data = []
    for i, region in enumerate(parsed['regions']):
        # Read raw intensities
        intensities = read_region_data(
            parsed['binary_data'],
            region,
            region_offsets[i],
            format_info['data_type'],
            format_info['bytes_per_val']
        )
        
        # Check if region has valid data
        valid_count = sum(1 for val in intensities if val > 0)
        if valid_count < len(intensities) * 0.5:
            continue  # Skip regions with < 50% valid data
        
        # Calculate corrected data
        corrected_data = calculate_transmission_corrected_data(
            region,
            intensities,
            parsed['source_energy'],
            parsed['transmission_coeffs']
        )
        
        # Combine region info with data
        region_data = {
            'name': region['name'],
            'num_points': region['num_points'],
            'start_energy': region['start_energy'],
            'end_energy': region['end_energy'],
            'step': region['step'],
            'be_values': corrected_data['be_values'],
            'raw_intensities': corrected_data['raw_intensities'],
            'corrected_intensities': corrected_data['corrected_intensities'],
            'transmission_values': corrected_data['transmission_values']
        }
        
        regions_data.append(region_data)
    
    return {
        'regions_data': regions_data,
        'metadata': parsed['metadata'],
        'instrument_model': parsed['instrument_model']
    }
