"""
Tests for vgd_reader library.
"""

import pytest
import numpy as np
from pathlib import Path


def test_import():
    """Test that the library can be imported."""
    from vgd_reader import read_vgd, VGDFile, VGDSpectrum
    from vgd_reader import parse_vgd_file, calculate_spectrum_data
    from vgd_reader import extract_core_level_name


def test_extract_core_level_name():
    """Test core level name extraction from filenames."""
    from vgd_reader import extract_core_level_name
    
    assert extract_core_level_name("O1s_Scan.VGD") == "O1s"
    assert extract_core_level_name("O1s Scan.VGD") == "O1s"
    assert extract_core_level_name("Sr3d_Region.VGD") == "Sr3d"
    assert extract_core_level_name("Ni2p core level.VGD") == "Ni2p"
    assert extract_core_level_name("C1s.VGD") == "C1s"
    assert extract_core_level_name("Fe2p3_Spectrum.VGD") == "Fe2p3"


def test_vgd_spectrum_to_dict():
    """Test VGDSpectrum.to_dict() method."""
    from vgd_reader.parser import VGDSpectrum

    spectrum = VGDSpectrum(
        binding_energy=np.array([530.0, 529.9, 529.8]),
        kinetic_energy=np.array([956.68, 956.78, 956.88]),
        intensity=np.array([1000.0, 1500.0, 1200.0]),
        corrected_intensity=np.array([100.0, 150.0, 120.0]),
        core_level="O1s",
        spectrum_index=0,
        be_start=530.0,
        be_end=529.8,
        be_step=-0.1,
        source_energy=1486.68,
        pass_energy=50.0,
    )

    d = spectrum.to_dict()

    # Keys match KherveFitting format
    assert d['Species & Transition'] == "O1s"
    assert d['BE Start'] == "530.00"
    assert d['Pass Energy'] == "50.00"
    assert len(d['binding_energy']) == 3
    assert d['Source Energy'] == "1486.68"
    assert d['Spectrum Index'] == "0"


# Integration tests require actual VGD files
# Add them to tests/data/ directory and uncomment below

# @pytest.fixture
# def sample_vgd_file():
#     return Path(__file__).parent / "data" / "O1s_Scan.VGD"

# def test_read_vgd_file(sample_vgd_file):
#     from vgd_reader import read_vgd
#     
#     if not sample_vgd_file.exists():
#         pytest.skip("Sample VGD file not found")
#     
#     data = read_vgd(str(sample_vgd_file))
#     
#     assert data.num_spectra >= 1
#     assert len(data.binding_energy) > 0
#     assert data.core_level == "O1s"
