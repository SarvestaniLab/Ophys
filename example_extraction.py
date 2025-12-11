"""
Example: Extract Suite2P traces and perform basic analysis

This script shows how to use the ophys_analysis package to extract
neural activity traces from Suite2P output and organize them into
trial structure.
"""

from fov_config_suite2p import fovs
from ophys_analysis import extract_suite2p_traces, save_extraction_hdf5, get_tuning_madineh
import numpy as np

# Example 1: Extract traces from a single FOV
print("="*70)
print("Example 1: Extract traces from FOV")
print("="*70)

# Make sure fovs list has been populated and auto-populated
# (run fov_config_suite2p.py first if needed)

if len(fovs) > 0:
    # Extract traces from first FOV
    ce = extract_suite2p_traces(fovs[0], fnum=0)

    # Print summary
    ce.print_summary()

    # Access individual cell data
    if len(ce.cells) > 0:
        cell = ce.cells[0]
        print(f"\nExample cell (0):")
        print(f"  Position: ({cell.xPos:.1f}, {cell.yPos:.1f})")
        print(f"  Responsive: {cell.ROI_responsiveness}")
        print(f"  Raw trace shape: {cell.raw.shape}")
        print(f"  Trial data shape: {cell.cyc.shape}")

    # Get responsive cells
    responsive = ce.get_responsive_cells()
    print(f"\nFound {len(responsive)} responsive cells")

    # Convert cell attributes to arrays
    x_positions = ce.to_array('xPos')
    y_positions = ce.to_array('yPos')
    print(f"\nCell positions:")
    print(f"  X range: {x_positions.min():.1f} - {x_positions.max():.1f}")
    print(f"  Y range: {y_positions.min():.1f} - {y_positions.max():.1f}")

    # Save to HDF5
    output_file = f"{fovs[0].animal_name}_extraction.h5"
    save_extraction_hdf5(ce, output_file)

    # Example 2: Analyze tuning for a responsive cell
    print("\n" + "="*70)
    print("Example 2: Analyze orientation tuning")
    print("="*70)

    if len(responsive) > 0:
        cell = responsive[0]

        # Get mean response per condition
        meanResponse = cell.condition_response

        # Assume grating stimulus with 8 directions
        n_dirs = len(cell.uniqStims) - 1  # Exclude blank
        if n_dirs > 0:
            stimInfo = np.arange(0, 360, 360/n_dirs)

            # Calculate tuning metrics
            tuning, response_fit, fitdata = get_tuning_madineh(
                meanResponse[:n_dirs], stimInfo
            )

            print(f"\nTuning metrics for cell:")
            print(f"  Preferred orientation: {tuning['pref_ort_fit']:.1f}°")
            print(f"  Preferred direction: {tuning['pref_dir_fit']:.1f}°")
            print(f"  OTI (orientation): {tuning['oti_fit']:.3f}")
            print(f"  DTI (direction): {tuning['dti_fit']:.3f}")
            print(f"  Tuning bandwidth: {tuning['fit_bandwidth']:.1f}°")
            print(f"  Fit quality (r): {tuning['fit_r']:.3f}")

else:
    print("No FOVs configured. Please run fov_config_suite2p.py first.")

print("\n" + "="*70)
print("✓ Examples complete!")
print("="*70)
