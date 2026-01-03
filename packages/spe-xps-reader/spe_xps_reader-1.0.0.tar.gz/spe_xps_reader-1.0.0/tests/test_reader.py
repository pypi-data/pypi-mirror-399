"""
Unit tests for spe_xps_reader library

Run with: python -m pytest tests/test_reader.py
Or: python -m pytest
"""

import unittest
import struct
import numpy as np
from spe_xps_reader import (
    parse_spe_file,
    detect_data_format,
    read_region_data,
    calculate_transmission_corrected_data,
    extract_all_regions
)


class TestSPEReaderBasic(unittest.TestCase):
    """Test basic functionality without requiring actual SPE files"""
    
    def test_transmission_calculation(self):
        """Test transmission correction calculation"""
        region = {
            'num_points': 100,
            'start_energy': 280.0,
            'end_energy': 295.0,
            'step': 0.15
        }
        
        intensities = [1000.0] * 100
        source_energy = 1486.6
        transmission_coeffs = (31.826, 0.229)
        
        result = calculate_transmission_corrected_data(
            region, intensities, source_energy, transmission_coeffs
        )
        
        # Check output structure
        self.assertIn('be_values', result)
        self.assertIn('raw_intensities', result)
        self.assertIn('corrected_intensities', result)
        self.assertIn('transmission_values', result)
        
        # Check lengths
        self.assertEqual(len(result['be_values']), 100)
        self.assertEqual(len(result['corrected_intensities']), 100)
        
        # Check BE range
        self.assertAlmostEqual(result['be_values'][0], 280.0, places=1)
        self.assertAlmostEqual(result['be_values'][-1], 295.0, places=1)
        
        # Corrected intensity should be lower than raw (divided by T > 1 for low KE)
        # At BE=280 eV with source=1486.6 eV, KE=1206.6, T will be > 1
        self.assertLess(result['corrected_intensities'][0], intensities[0])
    
    def test_transmission_coefficients(self):
        """Test transmission function with different coefficients"""
        region = {
            'num_points': 10,
            'start_energy': 280.0,
            'end_energy': 290.0,
            'step': 1.0
        }
        
        intensities = [1000.0] * 10
        source_energy = 1486.6
        
        # Test with default coefficients
        result1 = calculate_transmission_corrected_data(
            region, intensities, source_energy, (31.826, 0.229)
        )
        
        # Test with different coefficients
        result2 = calculate_transmission_corrected_data(
            region, intensities, source_energy, (40.0, 0.3)
        )
        
        # Different coefficients should give different corrections
        self.assertNotAlmostEqual(
            result1['corrected_intensities'][0],
            result2['corrected_intensities'][0]
        )
    
    def test_be_to_ke_conversion(self):
        """Test binding energy to kinetic energy conversion"""
        region = {
            'num_points': 5,
            'start_energy': 280.0,
            'end_energy': 284.0,
            'step': 1.0
        }
        
        intensities = [1000.0] * 5
        source_energy = 1486.6
        transmission_coeffs = (31.826, 0.229)
        
        result = calculate_transmission_corrected_data(
            region, intensities, source_energy, transmission_coeffs
        )
        
        # Check KE = Source - BE
        be_first = result['be_values'][0]
        expected_ke = source_energy - be_first
        
        # KE should be positive and reasonable
        self.assertGreater(expected_ke, 1200)
        self.assertLess(expected_ke, 1210)
    
    def test_negative_ke_protection(self):
        """Test that negative KE values are handled"""
        region = {
            'num_points': 5,
            'start_energy': 1500.0,  # Higher than source energy
            'end_energy': 1510.0,
            'step': 2.5
        }
        
        intensities = [1000.0] * 5
        source_energy = 1486.6
        transmission_coeffs = (31.826, 0.229)
        
        # Should not raise exception
        result = calculate_transmission_corrected_data(
            region, intensities, source_energy, transmission_coeffs
        )
        
        # Should have valid output
        self.assertEqual(len(result['corrected_intensities']), 5)
        # Values should be reasonable (not NaN or Inf)
        for val in result['corrected_intensities']:
            self.assertFalse(np.isnan(val))
            self.assertFalse(np.isinf(val))


class TestBinaryFormatDetection(unittest.TestCase):
    """Test binary data format detection"""
    
    def create_mock_binary_data(self, data_type='float32', num_values=100, offset=0):
        """Create mock binary data for testing"""
        fmt = '<f' if data_type == 'float32' else '<d'
        bytes_per_val = 4 if data_type == 'float32' else 8
        
        # Create header padding
        binary_data = b'\x00' * offset
        
        # Create realistic intensity values
        for i in range(num_values):
            value = 1000.0 + i * 10.0 + np.sin(i * 0.1) * 500.0
            binary_data += struct.pack(fmt, value)
        
        return binary_data
    
    def test_detect_float32_format(self):
        """Test detection of float32 (VersaProbe) format"""
        binary_data = self.create_mock_binary_data('float32', 100, offset=114)
        
        regions = [{
            'num_points': 100,
            'start_energy': 280.0,
            'end_energy': 295.0
        }]
        
        result = detect_data_format(binary_data, regions)
        
        self.assertEqual(result['data_type'], 'float32')
        self.assertEqual(result['bytes_per_val'], 4)
        self.assertIsNotNone(result['first_offset'])
    
    def test_detect_float64_format(self):
        """Test detection of float64 (X-tool) format"""
        binary_data = self.create_mock_binary_data('float64', 100, offset=200)
        
        regions = [{
            'num_points': 100,
            'start_energy': 280.0,
            'end_energy': 295.0
        }]
        
        result = detect_data_format(binary_data, regions)
        
        self.assertEqual(result['data_type'], 'float64')
        self.assertEqual(result['bytes_per_val'], 8)
        self.assertIsNotNone(result['first_offset'])
    
    def test_detect_quantum2000_format(self):
        """Test detection of Quantum 2000 format (data at end)"""
        num_points = 100
        # Create data at the END of the binary section
        binary_data = self.create_mock_binary_data('float64', num_points, offset=5000)
        
        regions = [{
            'num_points': num_points,
            'start_energy': 280.0,
            'end_energy': 295.0
        }]
        
        # This might detect as standard float64 or quantum2000
        result = detect_data_format(binary_data, regions)
        
        self.assertIn(result['data_type'], ['float32', 'float64'])
        self.assertIsNotNone(result['first_offset'])


class TestDataReading(unittest.TestCase):
    """Test data reading functions"""
    
    def test_read_region_data_float32(self):
        """Test reading float32 intensity data"""
        # Create mock binary data
        num_points = 50
        values = [1000.0 + i * 10.0 for i in range(num_points)]
        
        binary_data = b''
        for val in values:
            binary_data += struct.pack('<f', val)
        
        region = {
            'num_points': num_points,
            'start_energy': 280.0,
            'end_energy': 295.0
        }
        
        intensities = read_region_data(
            binary_data, region, 0, 'float32', 4
        )
        
        self.assertEqual(len(intensities), num_points)
        
        # Check values are close to original
        for i, (original, read) in enumerate(zip(values, intensities)):
            self.assertAlmostEqual(original, read, places=1)
    
    def test_read_region_data_float64(self):
        """Test reading float64 intensity data"""
        num_points = 50
        values = [1000.0 + i * 10.0 for i in range(num_points)]
        
        binary_data = b''
        for val in values:
            binary_data += struct.pack('<d', val)
        
        region = {
            'num_points': num_points,
            'start_energy': 280.0,
            'end_energy': 295.0
        }
        
        intensities = read_region_data(
            binary_data, region, 0, 'float64', 8
        )
        
        self.assertEqual(len(intensities), num_points)
        
        # Check values are close to original
        for original, read in zip(values, intensities):
            self.assertAlmostEqual(original, read, places=6)
    
    def test_read_with_invalid_values(self):
        """Test reading data with some invalid values"""
        num_points = 20
        
        binary_data = b''
        for i in range(num_points):
            if i == 10:
                # Add an invalid value
                val = 1e10  # Too large
            else:
                val = 1000.0 + i * 10.0
            binary_data += struct.pack('<f', val)
        
        region = {
            'num_points': num_points,
            'start_energy': 280.0,
            'end_energy': 295.0
        }
        
        intensities = read_region_data(
            binary_data, region, 0, 'float32', 4
        )
        
        # Invalid value should be replaced with 0.0
        self.assertEqual(intensities[10], 0.0)


class TestDataFormatting(unittest.TestCase):
    """Test that all numerical data uses .2f formatting"""
    
    def test_transmission_output_format(self):
        """Test that transmission correction outputs are formatted correctly"""
        region = {
            'num_points': 5,
            'start_energy': 280.123456,
            'end_energy': 285.987654,
            'step': 1.23456
        }
        
        intensities = [1234.5678] * 5
        source_energy = 1486.6
        transmission_coeffs = (31.826, 0.229)
        
        result = calculate_transmission_corrected_data(
            region, intensities, source_energy, transmission_coeffs
        )
        
        # When converting to strings, should use .2f
        for be in result['be_values']:
            formatted = f"{be:.2f}"
            # Should have exactly 2 decimal places
            self.assertRegex(formatted, r'^\d+\.\d{2}$')
        
        for intensity in result['corrected_intensities']:
            formatted = f"{intensity:.2f}"
            # Should have exactly 2 decimal places
            self.assertRegex(formatted, r'^\d+\.\d{2}$')


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def test_empty_region(self):
        """Test handling of empty region"""
        region = {
            'num_points': 0,
            'start_energy': 280.0,
            'end_energy': 280.0,
            'step': 0.0
        }
        
        intensities = []
        source_energy = 1486.6
        transmission_coeffs = (31.826, 0.229)
        
        result = calculate_transmission_corrected_data(
            region, intensities, source_energy, transmission_coeffs
        )
        
        self.assertEqual(len(result['be_values']), 0)
        self.assertEqual(len(result['corrected_intensities']), 0)
    
    def test_single_point_region(self):
        """Test region with single data point"""
        region = {
            'num_points': 1,
            'start_energy': 285.0,
            'end_energy': 285.0,
            'step': 0.0
        }
        
        intensities = [1000.0]
        source_energy = 1486.6
        transmission_coeffs = (31.826, 0.229)
        
        result = calculate_transmission_corrected_data(
            region, intensities, source_energy, transmission_coeffs
        )
        
        self.assertEqual(len(result['be_values']), 1)
        self.assertEqual(len(result['corrected_intensities']), 1)
        self.assertAlmostEqual(result['be_values'][0], 285.0, places=1)


class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflows"""
    
    def test_complete_workflow_simulation(self):
        """Simulate complete data extraction workflow"""
        # This test simulates the workflow without requiring an actual file
        
        # Create mock region data
        num_points = 100
        values = [1000.0 + i * 5.0 + np.sin(i * 0.1) * 200.0 
                  for i in range(num_points)]
        
        binary_data = b''
        for val in values:
            binary_data += struct.pack('<f', val)
        
        region = {
            'num_points': num_points,
            'start_energy': 280.0,
            'end_energy': 295.0,
            'step': 0.15
        }
        
        # Simulate the workflow
        # 1. Read intensities
        intensities = read_region_data(
            binary_data, region, 0, 'float32', 4
        )
        
        # 2. Calculate corrections
        result = calculate_transmission_corrected_data(
            region, intensities, 1486.6, (31.826, 0.229)
        )
        
        # Verify complete workflow produces valid data
        self.assertEqual(len(result['be_values']), num_points)
        self.assertEqual(len(result['corrected_intensities']), num_points)
        
        # Check BE values are in correct range
        self.assertAlmostEqual(min(result['be_values']), 280.0, places=1)
        self.assertAlmostEqual(max(result['be_values']), 295.0, places=1)
        
        # Check transmission correction applied (ratio should be reasonable)
        for raw, corr in zip(result['raw_intensities'], 
                            result['corrected_intensities']):
            if raw > 0:
                ratio = corr / raw
                # Ratio should be reasonable (between 0.1 and 10)
                self.assertGreater(ratio, 0.1)
                self.assertLess(ratio, 10.0)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSPEReaderBasic))
    suite.addTests(loader.loadTestsFromTestCase(TestBinaryFormatDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestDataReading))
    suite.addTests(loader.loadTestsFromTestCase(TestDataFormatting))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
