"""
Command-line interface for spe-xps-reader
"""

import sys
from .reader import extract_all_regions


def main():
    """Main function for command-line usage"""
    if len(sys.argv) < 2:
        print("Usage: python -m spe_xps_reader <file.spe>")
        print("   or: spe-reader <file.spe>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        # Extract all data
        result = extract_all_regions(file_path)
        
        print(f"\nInstrument: {result['instrument_model']}")
        print(f"Found {len(result['regions_data'])} regions:")
        
        for region in result['regions_data']:
            print(f"\n  Region: {region['name']}")
            print(f"    Points: {region['num_points']}")
            print(f"    BE range: {region['start_energy']:.2f} - {region['end_energy']:.2f} eV")
            print(f"    Max intensity (raw): {max(region['raw_intensities']):.2f}")
            print(f"    Max intensity (corrected): {max(region['corrected_intensities']):.2f}")
        
        print("\nMetadata:")
        for key, value in result['metadata'].items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
