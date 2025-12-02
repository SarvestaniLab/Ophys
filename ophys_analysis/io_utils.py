"""
HDF5 I/O utilities for saving and loading cell extraction data.
"""

import h5py
import numpy as np
from pathlib import Path
from typing import Optional
import json

from .cell_data import Cell, CellExtraction


def save_extraction_hdf5(ce: CellExtraction, filename: str):
    """
    Save CellExtraction to HDF5 file.

    Structure:
        /fov_metadata/ - FOV parameters
        /acquisition/ - Timing and stimulus data
        /cells/cell_0/ - Individual cell data
        /cells/cell_1/
        ...

    Args:
        ce: CellExtraction object
        filename: Output HDF5 filename
    """
    filepath = Path(filename)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with h5py.File(filepath, 'w') as f:
        # Save FOV metadata
        if ce.fov is not None:
            fov_grp = f.create_group('fov_metadata')
            from fov_config_suite2p import export_fov_to_dict
            fov_dict = export_fov_to_dict(ce.fov)
            for key, val in fov_dict.items():
                if val is not None:
                    try:
                        fov_grp.attrs[key] = val
                    except:
                        fov_grp.attrs[key] = str(val)

        # Save acquisition data
        acq_grp = f.create_group('acquisition')
        if ce.twophotontimes is not None:
            acq_grp.create_dataset('twophotontimes', data=ce.twophotontimes)
        if ce.stimOn is not None:
            acq_grp.create_dataset('stimOn', data=ce.stimOn)
        if ce.stimID is not None:
            acq_grp.create_dataset('stimID', data=ce.stimID)
        if ce.uniqStims is not None:
            acq_grp.create_dataset('uniqStims', data=ce.uniqStims)
        if ce.regOffsets is not None:
            acq_grp.create_dataset('regOffsets', data=ce.regOffsets)

        # Save cells
        cells_grp = f.create_group('cells')
        for i, cell in enumerate(ce.cells):
            cell_grp = cells_grp.create_group(f'cell_{i}')

            # Save all cell attributes
            for attr in dir(cell):
                if not attr.startswith('_'):
                    val = getattr(cell, attr)
                    if val is not None and not callable(val):
                        if isinstance(val, np.ndarray):
                            cell_grp.create_dataset(attr, data=val)
                        elif isinstance(val, (int, float, bool)):
                            cell_grp.attrs[attr] = val
                        elif isinstance(val, str):
                            cell_grp.attrs[attr] = val

    print(f"✓ Saved to {filepath}")


def load_extraction_hdf5(filename: str) -> CellExtraction:
    """
    Load CellExtraction from HDF5 file.

    Args:
        filename: HDF5 filename

    Returns:
        CellExtraction object
    """
    ce = CellExtraction()

    with h5py.File(filename, 'r') as f:
        # Load acquisition data
        if 'acquisition' in f:
            acq_grp = f['acquisition']
            if 'twophotontimes' in acq_grp:
                ce.twophotontimes = acq_grp['twophotontimes'][:]
            if 'stimOn' in acq_grp:
                ce.stimOn = acq_grp['stimOn'][:]
            if 'stimID' in acq_grp:
                ce.stimID = acq_grp['stimID'][:]
            if 'uniqStims' in acq_grp:
                ce.uniqStims = acq_grp['uniqStims'][:]
            if 'regOffsets' in acq_grp:
                ce.regOffsets = acq_grp['regOffsets'][:]

        # Load cells
        if 'cells' in f:
            cells_grp = f['cells']
            cell_names = sorted(cells_grp.keys(), key=lambda x: int(x.split('_')[1]))

            for cell_name in cell_names:
                cell_grp = cells_grp[cell_name]
                cell = Cell()

                # Load datasets
                for key in cell_grp.keys():
                    setattr(cell, key, cell_grp[key][:])

                # Load attributes
                for key, val in cell_grp.attrs.items():
                    setattr(cell, key, val)

                ce.cells.append(cell)

    print(f"✓ Loaded {len(ce.cells)} cells from {filename}")
    return ce
