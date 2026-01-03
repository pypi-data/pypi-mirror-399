"""
VGD Reader - Parse Thermo Scientific VGD Files for XPS Analysis

A Python library for reading Thermo Scientific VGD (VG Data) binary files
commonly used in X-ray Photoelectron Spectroscopy (XPS).

Example usage:
    from vgd_reader import read_vgd, VGDFile
    
    # Simple usage
    data = read_vgd("sample.vgd")
    print(data.binding_energy)
    print(data.intensity)
    
    # Or use the class directly
    vgd = VGDFile("sample.vgd")
    for spectrum in vgd.spectra:
        print(spectrum.core_level, spectrum.binding_energy)
"""

from .parser import (
    read_vgd,
    parse_vgd_file,
    calculate_spectrum_data,
    extract_core_level_name,
    VGDFile,
    VGDSpectrum,
)

__version__ = "0.1.0"
__author__ = "Gwilherm Kerherve"
__email__ = "your.email@example.com"
__all__ = [
    "read_vgd",
    "parse_vgd_file", 
    "calculate_spectrum_data",
    "extract_core_level_name",
    "VGDFile",
    "VGDSpectrum",
]
