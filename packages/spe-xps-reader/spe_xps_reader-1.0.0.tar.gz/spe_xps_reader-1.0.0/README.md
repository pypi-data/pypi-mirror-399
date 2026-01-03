# SPE_Reader

A Python library for reading and parsing PHI Instruments SPE files for X-ray Photoelectron Spectroscopy (XPS) data analysis.

## Overview

SPE_Reader is a standalone Python module that extracts spectral data from PHI instrument binary files (.spe format). It supports multiple PHI instrument formats and automatically detects the binary data structure.

## Supported Instruments

- **PHI VersaProbe III**: float32 (4 bytes) format, data after metadata header
- **PHI X-tool**: float64 (8 bytes) format, data after metadata header  
- **PHI Quantum 2000**: float64 (8 bytes) format, data at END of binary section

## Features

- Automatic detection of binary data format and offset
- Extraction of all spectral regions from multi-region files
- Transmission function correction using instrument calibration coefficients
- Conversion from kinetic energy to binding energy
- Extraction of experimental metadata (pass energy, work function, source energy, etc.)
- No external dependencies beyond NumPy

## Installation

Copy `SPE_Reader.py` to your project directory or install via:

```bash
pip install numpy
# Then copy SPE_Reader.py to your working directory
```

## Requirements

- Python 3.6+
- NumPy

## Usage

### Basic Usage

```python
from spe_xps_reader import extract_all_regions

# Extract all data from a SPE file
result = extract_all_regions('sample.spe')

# Access regions data
for region in result['regions_data']:
    name = region['name']
    be_values = region['be_values']
    corrected_intensities = region['corrected_intensities']
    
    print(f"Region: {name}")
    print(f"BE range: {be_values[0]:.2f} - {be_values[-1]:.2f} eV")
    print(f"Points: {len(be_values)}")
```

### Advanced Usage

```python
from spe_xps_reader import parse_spe_file, detect_data_format, read_region_data, calculate_transmission_corrected_data

# Step 1: Parse the file header and metadata
parsed = parse_spe_file('sample.spe')
print(f"Found {len(parsed['regions'])} regions")
print(f"Source energy: {parsed['source_energy']} eV")

# Step 2: Detect binary data format
format_info = detect_data_format(parsed['binary_data'], parsed['regions'])
print(f"Data type: {format_info['data_type']}")
print(f"Data starts at offset: {format_info['first_offset']}")

# Step 3: Read data for first region
region = parsed['regions'][0]
intensities = read_region_data(
    parsed['binary_data'],
    region,
    format_info['first_offset'],
    format_info['data_type'],
    format_info['bytes_per_val']
)

# Step 4: Apply transmission correction
corrected_data = calculate_transmission_corrected_data(
    region,
    intensities,
    parsed['source_energy'],
    parsed['transmission_coeffs']
)

print(f"BE values: {corrected_data['be_values'][:5]}...")
print(f"Corrected intensities: {corrected_data['corrected_intensities'][:5]}...")
```

### Command Line Usage

```bash
python -m spe_xps_reader sample.spe
# or after installation:
spe-reader sample.spe
```

This will print a summary of all regions and metadata found in the file.

## Data Structure

### `extract_all_regions()` returns:

```python
{
    'regions_data': [
        {
            'name': 'C1s',
            'num_points': 401,
            'start_energy': 280.0,
            'end_energy': 295.0,
            'step': 0.0375,
            'be_values': [280.00, 280.04, ...],
            'raw_intensities': [1234.5, 1250.2, ...],
            'corrected_intensities': [2456.7, 2489.3, ...],
            'transmission_values': [0.502, 0.503, ...]
        },
        # ... more regions
    ],
    'metadata': {
        'Sample ID': 'sample.spe',
        'Date': '2024/01/15',
        'Time': '14:30:22',
        'Technique': 'XPS',
        'Instrument': 'PHI VersaProbe III',
        'Source Label': 'Al',
        'Source Energy': '1486.6',
        'Pass Energy': '224',
        'Work Function': '4.339',
        # ... more metadata
    },
    'instrument_model': 'PHI VersaProbe III'
}
```

## SPE File Format

SPE files consist of:

1. **Text Header Section** (between SOFH and EOFH markers):
   - Instrument parameters
   - Spectral region definitions
   - Acquisition settings
   - Calibration coefficients

2. **Binary Data Section** (after EOFH):
   - Raw intensity values as float32 or float64
   - Contiguous data for all regions
   - Different offset strategies depending on instrument model

## Functions

### `parse_spe_file(file_path)`
Parse the SPE file header and extract metadata and region definitions.

**Returns:** dict with regions, metadata, binary_data, source_energy, transmission_coeffs, instrument_model

### `detect_data_format(binary_data, regions)`
Auto-detect the binary data format and offset.

**Returns:** dict with data_type, bytes_per_val, first_offset

### `read_region_data(binary_data, region, offset, data_type, bytes_per_val)`
Read raw intensity values for a single region.

**Returns:** list of intensity values

### `calculate_transmission_corrected_data(region, intensity_values, source_energy, transmission_coeffs)`
Calculate binding energies and apply transmission correction.

**Returns:** dict with be_values, raw_intensities, corrected_intensities, transmission_values

### `extract_all_regions(file_path)`
Complete one-step extraction of all regions with corrections applied.

**Returns:** dict with regions_data, metadata, instrument_model

## Transmission Function

The transmission function correction is applied as:

```
T(KE) = a × KE^(-b)
I_corrected = I_raw / T(KE)
```

Where:
- `a`, `b` are calibration coefficients from the file (default: a=31.826, b=0.229)
- `KE` is kinetic energy = Source Energy - Binding Energy
- `T(KE)` is the transmission function value

## Error Handling

The library includes validation for:
- Missing header sections
- Invalid binary data formats
- Regions with insufficient valid data points (< 50%)
- Out-of-range values

## License

GPL-3.0

## Author

Gwilherm Kerherve

## Contributing

This library is part of the KherveFitting project. Contributions and bug reports are welcome.

## Version History

- **1.0.0** (2024): Initial release
  - Support for VersaProbe III, X-tool, and Quantum 2000 formats
  - Automatic format detection
  - Transmission function correction
  - Metadata extraction

## See Also

- KherveFitting: Full XPS analysis software
- VGD_Reader: Companion library for Thermo/VG Scienta VGD files
