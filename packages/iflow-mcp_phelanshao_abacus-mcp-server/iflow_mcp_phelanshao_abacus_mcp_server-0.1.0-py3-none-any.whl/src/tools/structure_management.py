# src/tools/structure_management.py
import io
from typing import Dict, Any, Optional, List

from ase import Atoms
from ase.io import read as ase_read
from ase.build import bulk

def serialize_atoms_to_dict(atoms: Atoms) -> Dict[str, Any]:
    """
    Serializes an ASE Atoms object to a dictionary.
    Includes symbols, positions, cell, pbc, and basic info.
    """
    if not isinstance(atoms, Atoms): # Ensure it's an Atoms object
        return {}
    data = {
        "symbols": atoms.get_chemical_symbols(),
        "positions": atoms.get_positions().tolist(),
        "cell": atoms.get_cell().tolist(),
        "pbc": atoms.get_pbc().tolist(),
    }
    # Optional attributes
    if atoms.has("masses"):
        data["masses"] = atoms.get_masses().tolist()
    if atoms.has("tags"):
        data["tags"] = atoms.get_tags().tolist()
    if atoms.has("momenta"):
        data["momenta"] = atoms.get_momenta().tolist()
    
    # Store cell displacement if it's not zero (or always store it)
    celldisp = atoms.get_celldisp()
    if celldisp is not None and celldisp.any(): # Only include if non-zero
        data["celldisp"] = celldisp.tolist()
    else:
        data["celldisp"] = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]


    # Basic string representation for constraints, can be expanded
    data["constraints"] = [str(c) for c in atoms.constraints]
    data["info"] = dict(atoms.info) # General information dictionary

    return data

async def create_ase_structure(
    formula_or_data: str,
    input_format: str,
    lattice_type: Optional[str] = None, # Kept for compatibility, but crystalstructure is preferred for bulk
    a: Optional[float] = None,
    crystalstructure: Optional[str] = None
) -> Dict[str, Any]:
    """
    Creates an ASE Atoms object from various input formats and returns it as a dictionary.

    Args:
        formula_or_data: Chemical formula (e.g., "H2O", "NaCl") or structure data string (CIF, XYZ).
        input_format: The format of the input_data ("formula", "cif", "xyz").
        lattice_type: (Legacy, prefer crystalstructure) For "formula" input, can hint at lattice.
        a: Lattice constant for formula-based creation using `ase.build.bulk`.
        crystalstructure: Crystal structure for formula-based creation using `ase.build.bulk`
                          (e.g., 'sc', 'fcc', 'bcc', 'hcp', 'diamond').

    Returns:
        A dictionary containing the structure representation or an error message.
    """
    atoms: Optional[Atoms] = None
    warnings: List[str] = []

    try:
        input_format_lower = input_format.lower()
        if not formula_or_data:
            raise ValueError(f"Input data/formula cannot be empty for '{input_format_lower}' format.")

        if input_format_lower == "formula":
            if not crystalstructure:
                # If only lattice_type is given, try a simple mapping or warn.
                if lattice_type and lattice_type.lower() in ['sc', 'fcc', 'bcc', 'hcp', 'diamond', 'zincblende', 'rocksalt', 'cesiumchloride', 'fluorite', 'wurtzite']:
                    crystalstructure = lattice_type.lower()
                    warnings.append(f"Used 'lattice_type' ({lattice_type}) as 'crystalstructure'. Prefer explicitly setting 'crystalstructure'.")
                else:
                    # This case typically creates an isolated molecule/atom cluster if crystalstructure is missing
                    # For a single atom type, it might be okay. For a formula like "NaCl", it's not a crystal.
                    atoms = Atoms(formula_or_data)
                    warnings.append(f"Created structure from formula '{formula_or_data}' without crystal structure information. This likely results in an isolated molecule/cluster, not a periodic crystal. For bulk crystals, provide 'crystalstructure' and 'a'.")
            
            if crystalstructure: # This implies a bulk crystal is intended
                if not a:
                    raise ValueError("Lattice constant 'a' is required when 'crystalstructure' is specified for 'formula' input.")
                atoms = bulk(formula_or_data, crystalstructure=crystalstructure, a=a)
        
        elif input_format_lower == "cif":
            with io.StringIO(formula_or_data) as sio:
                atoms = ase_read(sio, format="cif")
        elif input_format_lower == "xyz":
            with io.StringIO(formula_or_data) as sio:
                atoms = ase_read(sio, format="xyz")
        else:
            raise ValueError(f"Unsupported input format: {input_format}. Supported formats are 'formula', 'cif', 'xyz'.")

        if not isinstance(atoms, Atoms): # Final check
            raise ValueError("Failed to create a valid ASE Atoms object from the input.")

        return {
            "success": True,
            "data": serialize_atoms_to_dict(atoms),
            "warnings": warnings,
            "message": f"Successfully created structure from {input_format_lower}."
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error creating structure: {str(e)}",
            "data": None,
            "warnings": warnings
        }

if __name__ == '__main__':
    import asyncio

    async def test_structure_creation():
        print("--- Testing Structure Creation ---")

        # Test 1: Formula - Diamond Silicon (Correct usage for bulk)
        print("\nTest 1: Formula - Diamond Silicon")
        result_si_diamond = await create_ase_structure("Si", "formula", crystalstructure='diamond', a=5.43)
        print(f"Success: {result_si_diamond.get('success')}, Message: {result_si_diamond.get('message', result_si_diamond.get('error'))}")
        if result_si_diamond.get('success'):
            print(f"  Symbols: {result_si_diamond['data']['symbols']}, Cell: {result_si_diamond['data']['cell'][0]}")
            assert len(result_si_diamond['data']['symbols']) > 0

        # Test 2: Formula - H2O (Molecule, no crystalstructure)
        print("\nTest 2: Formula - H2O (Molecule)")
        result_h2o_formula = await create_ase_structure("H2O", "formula")
        print(f"Success: {result_h2o_formula.get('success')}, Message: {result_h2o_formula.get('message', result_h2o_formula.get('error'))}")
        print(f"  Warnings: {result_h2o_formula.get('warnings')}")
        if result_h2o_formula.get('success'):
            print(f"  Symbols: {result_h2o_formula['data']['symbols']}, PBC: {result_h2o_formula['data']['pbc']}")
            assert result_h2o_formula['data']['symbols'] == ['H', 'H', 'O'] # Order might vary based on Atoms()

        # Test 3: Formula - NaCl with crystalstructure but no 'a' (Error)
        print("\nTest 3: Formula - NaCl with crystalstructure, no 'a' (Error expected)")
        result_nacl_error = await create_ase_structure("NaCl", "formula", crystalstructure='rocksalt')
        print(f"Success: {result_nacl_error.get('success')}, Error: {result_nacl_error.get('error')}")
        assert not result_nacl_error.get('success')

        # Test 4: CIF - Silicon
        print("\nTest 4: CIF - Silicon")
        cif_data_si = """
data_Si
_symmetry_space_group_name_H-M   'F d -3 m'
_cell_length_a   5.43000
_cell_length_b   5.43000
_cell_length_c   5.43000
_cell_angle_alpha   90.00000
_cell_angle_beta   90.00000
_cell_angle_gamma   90.00000
loop_
  _atom_site_label
  _atom_site_fract_x
  _atom_site_fract_y
  _atom_site_fract_z
  Si   0.00000   0.00000   0.00000
  Si   0.25000   0.25000   0.25000
"""
        result_cif = await create_ase_structure(cif_data_si, "cif")
        print(f"Success: {result_cif.get('success')}, Message: {result_cif.get('message', result_cif.get('error'))}")
        if result_cif.get('success'):
            print(f"  Symbols: {result_cif['data']['symbols']}, Cell: {result_cif['data']['cell'][0]}")
            assert len(result_cif['data']['symbols']) == 2 # Based on this minimal CIF

        # Test 5: XYZ - H2O
        print("\nTest 5: XYZ - H2O")
        xyz_data_h2o = """3
H2O example from XYZ
O  0.000000  0.000000  0.117300
H  0.000000  0.757200  -0.469200
H  0.000000 -0.757200  -0.469200
"""
        result_xyz = await create_ase_structure(xyz_data_h2o, "xyz")
        print(f"Success: {result_xyz.get('success')}, Message: {result_xyz.get('message', result_xyz.get('error'))}")
        if result_xyz.get('success'):
            print(f"  Symbols: {result_xyz['data']['symbols']}, Positions[0]: {result_xyz['data']['positions'][0]}")
            assert result_xyz['data']['symbols'] == ['O', 'H', 'H']

        # Test 6: Unsupported format
        print("\nTest 6: Unsupported format")
        result_unsupported = await create_ase_structure("data", "pdb")
        print(f"Success: {result_unsupported.get('success')}, Error: {result_unsupported.get('error')}")
        assert not result_unsupported.get('success')

        # Test 7: Empty input data
        print("\nTest 7: Empty CIF data")
        result_empty_cif = await create_ase_structure("", "cif")
        print(f"Success: {result_empty_cif.get('success')}, Error: {result_empty_cif.get('error')}")
        assert not result_empty_cif.get('success')

        print("\n--- All tests completed ---")

    asyncio.run(test_structure_creation())
import numpy as np
from ase.data import chemical_symbols, atomic_numbers, covalent_radii

def validate_ase_structure_dict(structure_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates a dictionary representing an ASE Atoms object.

    Args:
        structure_dict: A dictionary, typically from serialize_atoms_to_dict.

    Returns:
        A dictionary containing validation results (success, messages, warnings).
    """
    validation_messages: List[str] = []
    validation_warnings: List[str] = []
    is_valid = True

    if not isinstance(structure_dict, dict):
        return {"success": False, "messages": ["Input is not a dictionary."], "warnings": []}

    required_keys = ["symbols", "positions", "cell", "pbc"]
    for key in required_keys:
        if key not in structure_dict:
            validation_messages.append(f"Missing required key: '{key}'.")
            is_valid = False
    
    if not is_valid: # Stop if basic keys are missing
        return {"success": False, "messages": validation_messages, "warnings": validation_warnings}

    symbols = structure_dict.get("symbols", [])
    positions = np.array(structure_dict.get("positions", []))
    cell = np.array(structure_dict.get("cell", np.zeros((3,3))))
    pbc = structure_dict.get("pbc", [False, False, False])

    # 1. Check for atoms
    if not symbols:
        validation_messages.append("Structure has no atoms (symbols list is empty).")
        is_valid = False
    elif len(symbols) != len(positions):
        validation_messages.append(f"Mismatch between number of symbols ({len(symbols)}) and positions ({len(positions)}).")
        is_valid = False

    # 2. Validate symbols
    for i, sym in enumerate(symbols):
        if sym not in chemical_symbols:
            validation_messages.append(f"Invalid chemical symbol '{sym}' at index {i}.")
            is_valid = False

    # 3. Validate positions (are they numbers, correct shape)
    if positions.ndim != 2 or (positions.shape[0] > 0 and positions.shape[1] != 3):
        validation_messages.append(f"Positions array has incorrect shape: {positions.shape}. Expected (N, 3).")
        is_valid = False
    if not np.issubdtype(positions.dtype, np.number):
         validation_messages.append("Positions array contains non-numeric values.")
         is_valid = False


    # 4. Validate cell (are they numbers, correct shape)
    if cell.shape != (3, 3):
        validation_messages.append(f"Cell matrix has incorrect shape: {cell.shape}. Expected (3, 3).")
        is_valid = False
    if not np.issubdtype(cell.dtype, np.number):
         validation_messages.append("Cell matrix contains non-numeric values.")
         is_valid = False
    
    # 5. Validate PBC (is it a list/array of 3 booleans)
    if not (isinstance(pbc, (list, np.ndarray)) and len(pbc) == 3 and all(isinstance(val, bool) for val in pbc)):
        validation_messages.append(f"PBC flags are invalid: {pbc}. Expected a list of 3 booleans.")
        is_valid = False

    # 6. (Optional) Check for very short interatomic distances if periodic
    # This is a more complex check and can be computationally intensive for large structures.
    # We'll add a simplified version.
    if is_valid and len(symbols) > 1 and any(pbc): # Only if structure is somewhat valid and periodic
        try:
            # Attempt to create a temporary Atoms object for distance checks
            # This assumes the dictionary structure is mostly fine if basic checks passed
            temp_atoms = Atoms(symbols=symbols, positions=positions, cell=cell, pbc=pbc)
            
            # Check for atoms too close to each other
            # Using covalent radii as a rough guide for minimum distance
            # Factor can be adjusted, e.g., 0.4 means less than 40% of sum of covalent radii
            min_dist_factor = 0.6 
            all_distances = temp_atoms.get_all_distances(mic=True) # mic=True for periodic systems

            for i in range(len(temp_atoms)):
                for j in range(i + 1, len(temp_atoms)):
                    r_i = covalent_radii[atomic_numbers[temp_atoms[i].symbol]]
                    r_j = covalent_radii[atomic_numbers[temp_atoms[j].symbol]]
                    min_allowed_dist = (r_i + r_j) * min_dist_factor
                    if all_distances[i, j] < min_allowed_dist:
                        validation_warnings.append(
                            f"Warning: Atoms {i}({temp_atoms[i].symbol}) and {j}({temp_atoms[j].symbol}) "
                            f"are very close: {all_distances[i,j]:.3f} Å. "
                            f"Minimum expected based on covalent radii sum * {min_dist_factor}: {min_allowed_dist:.3f} Å."
                        )
        except Exception as e:
            validation_warnings.append(f"Could not perform interatomic distance check: {str(e)}")


    if not validation_messages: # If no hard errors, it's considered valid for now
        validation_messages.append("Structure dictionary passed basic validation checks.")
    
    return {
        "success": is_valid,
        "messages": validation_messages,
        "warnings": validation_warnings
    }

async def test_structure_validation():
    print("\n--- Testing Structure Validation ---")
    
    valid_si_dict = {
        "symbols": ["Si", "Si"],
        "positions": [[0.0, 0.0, 0.0], [1.3575, 1.3575, 1.3575]],
        "cell": [[5.43, 0.0, 0.0], [0.0, 5.43, 0.0], [0.0, 0.0, 5.43]],
        "pbc": [True, True, True]
    }
    print("\nTest Valid Silicon:")
    result = validate_ase_structure_dict(valid_si_dict)
    print(f"Success: {result['success']}, Messages: {result['messages']}, Warnings: {result['warnings']}")
    assert result['success']

    invalid_symbols_dict = {
        "symbols": ["Xx", "Si"], "positions": [[0,0,0],[1,1,1]], "cell": np.eye(3).tolist(), "pbc": [True,True,True]
    }
    print("\nTest Invalid Symbol:")
    result = validate_ase_structure_dict(invalid_symbols_dict)
    print(f"Success: {result['success']}, Messages: {result['messages']}")
    assert not result['success']
    assert "Invalid chemical symbol 'Xx'" in result['messages'][0]

    mismatch_len_dict = {
        "symbols": ["Si"], "positions": [[0,0,0],[1,1,1]], "cell": np.eye(3).tolist(), "pbc": [True,True,True]
    }
    print("\nTest Mismatch Length:")
    result = validate_ase_structure_dict(mismatch_len_dict)
    print(f"Success: {result['success']}, Messages: {result['messages']}")
    assert not result['success']
    assert "Mismatch between number of symbols" in result['messages'][0]
    
    atoms_too_close_dict = { # Two Si atoms very close
        "symbols": ["Si", "Si"],
        "positions": [[0.0, 0.0, 0.0], [0.1, 0.1, 0.1]], # Very close
        "cell": [[10.0, 0.0, 0.0], [0.0, 10.0, 0.0], [0.0, 0.0, 10.0]],
        "pbc": [True, True, True]
    }
    print("\nTest Atoms Too Close (Warning Expected):")
    result = validate_ase_structure_dict(atoms_too_close_dict)
    print(f"Success: {result['success']}, Messages: {result['messages']}, Warnings: {result['warnings']}")
    assert result['success'] # Basic validation passes
    assert len(result['warnings']) > 0
    assert "are very close" in result['warnings'][0]

    missing_key_dict = {"symbols": ["Si"]}
    print("\nTest Missing Keys:")
    result = validate_ase_structure_dict(missing_key_dict)
    print(f"Success: {result['success']}, Messages: {result['messages']}")
    assert not result['success']
    assert "Missing required key: 'positions'" in result['messages']

if __name__ == '__main__': # Assuming this block already exists from create_ase_structure
    # asyncio.run(test_structure_creation()) # Keep previous tests if desired
    import asyncio # Ensure asyncio is imported if this is the only test function in the main block
    asyncio.run(test_structure_validation()) # Run new tests
# 注意：io, Atoms, ase_read, serialize_atoms_to_dict, Dict, Any, Optional, List 应该已经从文件顶部导入了
from ase.io import write as ase_write # 需要 ase.io.write

async def convert_ase_structure_format(
    input_structure_data: str,
    input_format: str,
    output_format: str
) -> Dict[str, Any]:
    """
    Converts structure data from one format to another using ASE.

    Args:
        input_structure_data: String containing the structure data.
        input_format: The format of the input_structure_data (e.g., "cif", "xyz", "vasp").
        output_format: The desired output format (e.g., "xyz", "cif", "vasp", "pdb").

    Returns:
        A dictionary containing the converted structure string or an error message.
    """
    warnings: List[str] = []
    try:
        if not input_structure_data:
            raise ValueError("Input structure data cannot be empty.")
        if not input_format:
            raise ValueError("Input format must be specified.")
        if not output_format:
            raise ValueError("Output format must be specified.")

        input_fmt_lower = input_format.lower()
        output_fmt_lower = output_format.lower()

        # Read the input structure
        with io.StringIO(input_structure_data) as sio_in:
            atoms = ase_read(sio_in, format=input_fmt_lower)
        
        if not isinstance(atoms, Atoms):
             raise ValueError(f"Failed to read input structure data in '{input_fmt_lower}' format.")

        # Write the structure to the output format
        with io.StringIO() as sio_out:
            ase_write(sio_out, atoms, format=output_fmt_lower)
            converted_data_string = sio_out.getvalue()

        return {
            "success": True,
            "data": {
                "output_structure_data": converted_data_string,
                "output_format": output_fmt_lower,
                "original_input_format": input_fmt_lower
            },
            "message": f"Successfully converted structure from {input_fmt_lower} to {output_fmt_lower}.",
            "warnings": warnings
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error during structure conversion: {str(e)}",
            "data": None,
            "warnings": warnings
        }

async def test_structure_conversion():
    print("\n--- Testing Structure Conversion ---")

    cif_data_si_for_conversion = """
data_Si_conv
_symmetry_space_group_name_H-M   'F d -3 m'
_cell_length_a   5.43000
_cell_length_b   5.43000
_cell_length_c   5.43000
_cell_angle_alpha   90.00000
_cell_angle_beta   90.00000
_cell_angle_gamma   90.00000
loop_
  _atom_site_label
  _atom_site_fract_x
  _atom_site_fract_y
  _atom_site_fract_z
  Si   0.00000   0.00000   0.00000
  Si   0.25000   0.25000   0.25000
"""
    # Test 1: CIF to XYZ
    print("\nTest 1: CIF to XYZ")
    result_cif_to_xyz = await convert_ase_structure_format(cif_data_si_for_conversion, "cif", "xyz")
    print(f"Success: {result_cif_to_xyz.get('success')}, Message: {result_cif_to_xyz.get('message', result_cif_to_xyz.get('error'))}")
    if result_cif_to_xyz.get('success'):
        # print(f"  Output XYZ:\n{result_cif_to_xyz['data']['output_structure_data']}")
        assert "Si" in result_cif_to_xyz['data']['output_structure_data']
        assert len(result_cif_to_xyz['data']['output_structure_data'].splitlines()) == 4 # 2 atoms + 2 header lines for XYZ
    else:
        assert False, "CIF to XYZ conversion failed"


    xyz_data_h2o_for_conversion = """3
Water molecule
O  0.000000  0.000000  0.117300
H  0.000000  0.757200  -0.469200
H  0.000000 -0.757200  -0.469200
"""
    # Test 2: XYZ to PDB (PDB is a common format, though less for pure materials science)
    print("\nTest 2: XYZ to PDB")
    result_xyz_to_pdb = await convert_ase_structure_format(xyz_data_h2o_for_conversion, "xyz", "pdb")
    print(f"Success: {result_xyz_to_pdb.get('success')}, Message: {result_xyz_to_pdb.get('message', result_xyz_to_pdb.get('error'))}")
    if result_xyz_to_pdb.get('success'):
        # print(f"  Output PDB:\n{result_xyz_to_pdb['data']['output_structure_data']}")
        assert "HETATM" in result_xyz_to_pdb['data']['output_structure_data'] # PDB uses HETATM for non-standard residues
    else:
        assert False, "XYZ to PDB conversion failed"

    # Test 3: Invalid input format
    print("\nTest 3: Invalid input format")
    result_invalid_in = await convert_ase_structure_format(cif_data_si_for_conversion, "nonexistent", "xyz")
    print(f"Success: {result_invalid_in.get('success')}, Error: {result_invalid_in.get('error')}")
    assert not result_invalid_in.get('success')

    # Test 4: Invalid output format (ASE might handle some gracefully, others not)
    # This behavior depends on ASE's capabilities.
    print("\nTest 4: Invalid output format")
    result_invalid_out = await convert_ase_structure_format(cif_data_si_for_conversion, "cif", "nonexistent_fmt")
    print(f"Success: {result_invalid_out.get('success')}, Error: {result_invalid_out.get('error')}")
    assert not result_invalid_out.get('success') # Expecting ASE to raise an error for unknown format

    # Test 5: Empty input data
    print("\nTest 5: Empty input data")
    result_empty_data = await convert_ase_structure_format("", "cif", "xyz")
    print(f"Success: {result_empty_data.get('success')}, Error: {result_empty_data.get('error')}")
    assert not result_empty_data.get('success')


if __name__ == '__main__': # Assuming this block already exists
    import asyncio # Ensure asyncio is imported if this is the only test function in the main block
    # asyncio.run(test_structure_creation())
    # asyncio.run(test_structure_validation())
    asyncio.run(test_structure_conversion())