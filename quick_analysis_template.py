#!/usr/bin/env python
"""
Quick Analysis Template

Simple template for analyzing a single FOV. Just edit the paths below and run!

Usage:
    python quick_analysis_template.py
"""

from pathlib import Path
from fov_utils import create_fov_from_stimfile
from ophys_analysis import (
    extract_suite2p_traces,
    save_extraction_hdf5,
    create_full_analysis_report,
)

# ============================================================================
# EDIT THESE PATHS FOR YOUR ANALYSIS
# ============================================================================

# Path to your data directory (contains suite2p/ and imaging_processed/)
DATA_DIR = r'X:/Madineh/Calcium_Imaging/20251113_Derrick'

# Path to your stimulus file (or set to None to auto-detect)
STIM_FILE = None  # Will auto-find *visual*.py, *stim*.py, etc.
# STIM_FILE = r'X:/Madineh/Calcium_Imaging/20251113_Derrick/visual_stim.py'

# Output directory for results
OUTPUT_DIR = r'X:/Madineh/Calcium_Imaging/20251113_Derrick/analysis_results'

# Experimental parameters
IMAGING_FILES = [0]       # Which imaging file(s) to use
SPK2_FILES = [0]          # Which Spike2 file(s) to use
BRAIN_REGION = 'V1'       # Brain region
LAYER = 'L2/3'            # Cortical layer (or None)
FACTOR = 1                # Downsampling factor

# ============================================================================
# ANALYSIS CODE (no need to edit below)
# ============================================================================

def main():
    print("="*70)
    print("QUICK FOV ANALYSIS")
    print("="*70)
    print(f"Data directory: {DATA_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print()

    # Create output directory
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)

    # Find stimulus file if not specified
    stim_file = STIM_FILE
    if stim_file is None:
        data_path = Path(DATA_DIR)
        stim_patterns = ['*visual*.py', '*stim*.py', '*grating*.py', '*.py']
        for pattern in stim_patterns:
            matches = list(data_path.glob(pattern))
            if matches:
                stim_file = str(matches[0])
                print(f"Found stimulus file: {Path(stim_file).name}")
                break

        if stim_file is None:
            raise FileNotFoundError("No stimulus file found! Set STIM_FILE manually.")

    # Step 1: Configure FOV
    print("\n[1/4] Configuring FOV...")
    fov = create_fov_from_stimfile(
        stimfile=stim_file,
        TifStack_path=DATA_DIR,
        ImagingFile=IMAGING_FILES,
        Spk2File=SPK2_FILES,
    )
    fov.factor = FACTOR
    fov.brain_region = BRAIN_REGION
    fov.layer = LAYER

    print(f"  Animal: {fov.animal_name}")
    print(f"  Recording date: {fov.recording_date}")
    print(f"  Stim type: {fov.stim_type}")

    # Step 2: Extract traces
    print("\n[2/4] Extracting Suite2P traces...")
    ce = extract_suite2p_traces(fov, fnum=0)
    print()
    ce.print_summary()

    # Step 3: Save to HDF5
    print("\n[3/4] Saving extraction results...")
    h5_file = output_path / 'extraction_results.h5'
    save_extraction_hdf5(ce, str(h5_file))

    # Step 4: Generate full analysis report
    print("\n[4/4] Generating analysis report...")
    create_full_analysis_report(ce, output_dir=str(output_path))

    print(f"\n{'='*70}")
    print("ANALYSIS COMPLETE!")
    print(f"{'='*70}")
    print(f"Results saved to: {output_path}")
    print(f"  - extraction_results.h5")
    print(f"  - population_summary.png")
    print(f"  - orientation_maps.png")
    print(f"  - tuning_distributions.png")
    print(f"  - cell_*_tuning.png (first 10 responsive cells)")


if __name__ == '__main__':
    main()
