# test_my_vgd.py
from vgd_reader import read_vgd

# Test with a real file
data = read_vgd("Ni2p Scan.VGD")

# Check basic data
print(f"Core level: {data.core_level}")
print(f"Number of spectra: {data.num_spectra}")
print(f"BE range: {data.binding_energy[0]:.2f} to {data.binding_energy[-1]:.2f} eV")
print(f"Points: {len(data.binding_energy)}")

# Check all metadata
for spectrum in data.spectra:
    print("\n--- Spectrum Info ---")
    d = spectrum.to_dict()
    for key, value in d.items():
        if not isinstance(value, list):  # Skip arrays
            print(f"{key}: {value}")

# Test Excel export
data.to_excel("test_output.xlsx")
print("\nExcel file created: test_output.xlsx")

# Test DataFrame export (if pandas installed)
try:
    df = data.to_dataframe()
    print(f"\nDataFrame shape: {df.shape}")
    print(df.head())
except ImportError:
    print("pandas not installed, skipping DataFrame test")