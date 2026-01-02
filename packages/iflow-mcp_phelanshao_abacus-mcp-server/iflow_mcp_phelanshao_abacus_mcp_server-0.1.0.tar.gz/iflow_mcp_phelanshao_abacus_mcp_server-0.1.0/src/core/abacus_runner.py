# src/core/abacus_runner.py
from typing import Dict, Any, Optional, List, Union
import textwrap
import asyncio # Already used for subprocess
import os # Already used for path ops
import tempfile # Already used
import shutil # Already used
from src.tools.task_management import register_new_task, update_task_status, record_task_completion # <-- 新增导入

# ABACUS INPUT参数的默认值，来自您的项目概述
# 我们可以根据需要扩展这个字典
DEFAULT_ABACUS_PARAMS = {
    "calculation": "scf",       # 默认计算类型
    "ntype": 1,                 # 默认原子种类数 (需要根据实际结构动态设置)
    "nbands": "auto",           # 默认能带数 (ABACUS可以自动计算)
    "ecutwfc": 100,             # 平面波截断能 (Ry)
    "scf_thr": 1e-6,            # SCF收敛阈值
    "scf_nmax": 100,            # 最大SCF迭代次数
    "basis_type": "pw",         # 基组类型 (平面波)
    "mixing_type": "broyden",   # SCF混合方法
    "mixing_beta": 0.7,         # SCF混合参数
    "ks_solver": "cg",          # KS方程求解器
    "symmetry": 1,              # 是否使用对称性
    "pseudo_dir": "./",         # 赝势文件目录 (通常在运行时指定或服务器配置)
    "cal_force": 0,             # 是否计算力
    "cal_stress": 0,            # 是否计算应力
    "out_stru": 0,              # 是否输出结构
    "out_chg": 0,               # 是否输出电荷密度
    "out_pot": 0,               # 是否输出势函数
    "out_wfc_pw": 0,            # 是否输出平面波波函数
    "out_dos": 0,               # 是否输出态密度
    "out_band": 0,              # 是否输出能带结构
    "out_proj_band":0,          # 是否输出投影能带
    "out_mat_hs": 0,            # 是否输出哈密顿/重叠矩阵 (for Hefei-NAMD)
    "out_wfc_lcao": 0,          # 是否输出LCAO波函数 (for Hefei-NAMD)
    "smearing_method": "gauss", # Smearing方法
    "smearing_sigma": 0.002,    # Smearing宽度 (Ry)
    # K点相关的参数将单独处理或通过ASE生成KPT文件
}

# 参数分组，用于格式化输出INPUT文件
PARAM_GROUPS = {
    "GENERAL": ["suffix", "calculation", "ntype", "nbands", "ecutwfc", "dft_functional", 
                "pseudo_dir", "pseudo_type", "basis_type", "ks_solver", "symmetry", 
                "init_wfc", "init_chg", "diag_thr", "diag_nmax", "scf_dim", "scf_thr", "scf_nmax"],
    "RELAX": ["cal_force", "force_thr", "force_thr_ev", "force_thr_ev2", "cal_stress", "stress_thr", 
              "press1", "press2", "press3", "relax_method", "relax_nmax", "relax_bfgs_w1", "relax_bfgs_w2",
              "relax_cg_thr", "cell_factor", "fixed_axes", "fixed_ibrav", "fixed_atoms"],
    "MD": ["md_type", "md_nstep", "md_dt", "md_tfirst", "md_tlast", "md_temp_zone", "md_thermostat",
           "md_dumpfreq", "md_restartfreq", "md_seed", "md_prec_level"],
    "OUTPUT": ["out_stru", "out_chg", "out_pot", "out_wfc_pw", "out_wfc_lcao", "out_dos", "out_band", 
               "out_proj_band", "out_mat_hs", "out_mat_r", "out_mat_t", "out_mat_dh", "out_element_info",
               "out_all_ion", "out_interval", "out_app_flag", "out_level", "out_dm", "out_freq_elec", "out_freq_ion"],
    "SMEARING": ["smearing_method", "smearing_sigma", "smearing_temp"],
    "MIXING": ["mixing_type", "mixing_beta", "mixing_ndim", "mixing_gg0", "mixing_beta_decay", "mixing_restart"],
    "VDW": ["vdw_method", "vdw_s6", "vdw_s8", "vdw_a1", "vdw_a2", "vdw_d", "vdw_abc", "vdw_C6_file", "vdw_C6_org_file"],
    "DFT_PLUS_U": ["dft_plus_u", "orbital_type", "hubbard_u", "yukawa_lambda", "omc"],
    "TDDFT": ["tddft", "tddft_method", "tddft_dim", "tddft_dt", "tddft_nstep", "tddft_epsilon", "tddft_potential_type"],
    "EXX": ["exx_hybrid_alpha", "exx_hse_omega", "exx_separate_loop", "exx_hybrid_type", "exx_screen_type"],
    # ... 可以根据ABACUS文档添加更多分组和参数
}


def format_input_value(value: Any) -> str:
    """Formats a parameter value for the ABACUS INPUT file."""
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, str) and value.lower() in ["true", "false"]: # Handle string bools
        return "1" if value.lower() == "true" else "0"
    if isinstance(value, (list, tuple)): # e.g. for fixed_axes = x y z
        return " ".join(map(str, value))
    if value is None: # Should not happen if defaults are handled, but as a safeguard
        return "" 
    return str(value)

def generate_abacus_input(params: Dict[str, Any], user_comments: Optional[str] = None) -> str:
    """
    Generates the content for an ABACUS INPUT file.

    Args:
        params: A dictionary of parameters to include in the INPUT file.
                Defaults from DEFAULT_ABACUS_PARAMS will be used if not provided.
        user_comments: Optional string for user-defined comments at the top of the file.

    Returns:
        A string containing the formatted INPUT file content.
    """
    input_content = "INPUT_PARAMETERS\n"
    if user_comments:
        input_content += textwrap.indent(user_comments, "# ") + "\n\n"

    # Combine user params with defaults, user params take precedence
    # We need to be careful about ntype, as it depends on the STRU file.
    # For now, let's assume it's provided or correctly defaulted.
    # A more robust approach would be to determine ntype from the Atoms object.
    final_params = DEFAULT_ABACUS_PARAMS.copy()
    final_params.update(params)

    # Organize parameters by known groups for better readability
    # Parameters not in any group will be added at the end or in a 'MISC' group
    
    processed_params = set()

    for group_name, group_params_list in PARAM_GROUPS.items():
        group_lines = []
        for key in group_params_list:
            if key in final_params:
                value = final_params[key]
                # Skip None values unless they are explicitly meant to be empty strings or handled by format_input_value
                if value is not None: 
                    group_lines.append(f"{key:<20} {format_input_value(value)}")
                    processed_params.add(key)
        
        if group_lines:
            input_content += f"# Parameters ({group_name.capitalize()})\n"
            input_content += "\n".join(group_lines) + "\n\n"

    # Add any remaining parameters that were not in predefined groups
    misc_lines = []
    for key, value in final_params.items():
        if key not in processed_params and value is not None:
            misc_lines.append(f"{key:<20} {format_input_value(value)}")
    
    if misc_lines:
        input_content += "# Parameters (Miscellaneous)\n"
        input_content += "\n".join(misc_lines) + "\n\n"
        
    return input_content.strip() + "\n" # Ensure a trailing newline

if __name__ == '__main__':
    print("--- Testing ABACUS INPUT Generation ---")

    # Test 1: Basic SCF with defaults and a few overrides
    test_params_1 = {
        "suffix": "Si_scf_test",
        "ecutwfc": 120,
        "ntype": 1, # Assuming Si, will be set by STRU
        "dft_functional": "PBE", # Example of a parameter not in simple defaults
        "cal_force": True
    }
    input_str_1 = generate_abacus_input(test_params_1, user_comments="Test SCF for Silicon bulk")
    print("\nTest 1: Basic SCF")
    print(input_str_1)
    assert "suffix             Si_scf_test" in input_str_1
    assert "ecutwfc            120" in input_str_1
    assert "dft_functional     PBE" in input_str_1
    assert "cal_force          1" in input_str_1 # Boolean converted to 1
    assert "scf_thr            1e-06" in input_str_1 # Default value
    assert "# Parameters (General)" in input_str_1
    assert "# Parameters (Relax)" in input_str_1


    # Test 2: MD calculation with specific MD parameters
    test_params_2 = {
        "calculation": "md",
        "suffix": "H2O_md",
        "ntype": 2, # H, O
        "md_nstep": 1000,
        "md_dt": 0.5, # fs
        "md_tfirst": 300, # K
        "out_stru": True, # Output structure during MD
        "out_interval": 100
    }
    input_str_2 = generate_abacus_input(test_params_2)
    print("\nTest 2: MD Calculation")
    print(input_str_2)
    assert "calculation        md" in input_str_2
    assert "md_nstep           1000" in input_str_2
    assert "out_stru           1" in input_str_2
    assert "out_interval       100" in input_str_2
    assert "# Parameters (Md)" in input_str_2
    assert "# Parameters (Output)" in input_str_2

    # Test 3: Using a parameter not in any predefined group
    test_params_3 = {
        "custom_param_for_test": "custom_value",
        "another_one": 123.45
    }
    input_str_3 = generate_abacus_input(test_params_3)
    print("\nTest 3: Miscellaneous Parameters")
    print(input_str_3)
    assert "custom_param_for_test custom_value" in input_str_3
    assert "another_one        123.45" in input_str_3
    assert "# Parameters (Miscellaneous)" in input_str_3
    
    # Test 4: Boolean false value
    test_params_4 = {
        "cal_stress": False,
        "symmetry": "false" # string false
    }
    input_str_4 = generate_abacus_input(test_params_4)
    print("\nTest 4: Boolean False Values")
    print(input_str_4)
    assert "cal_stress         0" in input_str_4
    assert "symmetry           0" in input_str_4

    print("\n--- ABACUS INPUT Generation Tests Completed ---")
import numpy as np
from ase import Atoms # ASE Atoms 对象
from ase.data import atomic_masses, chemical_symbols as ase_chemical_symbols # ASE提供的原子质量和符号

# Bohr <-> Angstrom conversion factor
BOHR_TO_ANGSTROM = 0.529177210903
ANGSTROM_TO_BOHR = 1 / BOHR_TO_ANGSTROM

def atoms_from_dict(structure_dict: Dict[str, Any]) -> Atoms:
    """
    Helper function to create an ASE Atoms object from a dictionary.
    Assumes the dictionary follows the serialization format used by serialize_atoms_to_dict.
    """
    symbols = structure_dict.get("symbols")
    positions = structure_dict.get("positions")
    cell = structure_dict.get("cell")
    pbc = structure_dict.get("pbc")

    if not all([symbols, positions is not None, cell is not None, pbc is not None]):
        raise ValueError("Structure dictionary is missing one or more required keys: symbols, positions, cell, pbc.")

    atoms = Atoms(symbols=symbols, positions=positions, cell=cell, pbc=pbc)
    
    # Optional attributes
    if "masses" in structure_dict:
        atoms.set_masses(structure_dict["masses"])
    if "tags" in structure_dict:
        atoms.set_tags(structure_dict["tags"])
    if "momenta" in structure_dict:
        atoms.set_momenta(structure_dict["momenta"])
    if "celldisp" in structure_dict:
        atoms.set_celldisp(structure_dict["celldisp"])
    if "constraints" in structure_dict:
        # Reconstructing constraints from strings is non-trivial and depends on ASE's constraint classes.
        # For now, we'll skip fully reconstructing them, or one might need a more robust serialization.
        # This part might need to be enhanced if complex constraints are used.
        pass
    if "info" in structure_dict:
        atoms.info = structure_dict["info"]
        
    return atoms

def generate_abacus_stru(
    atoms_obj_or_dict: Union[Atoms, Dict[str, Any]],
    pseudo_potential_map: Dict[str, str],
    orbital_file_map: Optional[Dict[str, str]] = None,
    coordinate_type: str = "Cartesian_Angstrom", # "Cartesian_Angstrom", "Direct", "Cartesian_Bohr"
    user_comments: Optional[str] = None,
    fixed_atoms_indices: Optional[List[int]] = None # 0-indexed list of atoms to fix
) -> str:
    """
    Generates the content for an ABACUS STRU file from an ASE Atoms object or its dictionary representation.

    Args:
        atoms_obj_or_dict: ASE Atoms object or a dictionary from serialize_atoms_to_dict.
        pseudo_potential_map: Dictionary mapping element symbol to its pseudopotential file name.
                              e.g., {"Si": "Si.UPF", "O": "O.UPF"}
        orbital_file_map: Optional dictionary mapping element symbol to its numerical orbital file name.
                          e.g., {"Si": "Si_gga_8au_100Ry_2s2p1d.orb"}
        coordinate_type: Specifies the type and unit of atomic positions.
                         - "Cartesian_Angstrom": Cartesian coordinates in Angstrom (default).
                                                 LATTICE_CONSTANT will be 1.0, LATTICE_VECTORS in Angstrom.
                                                 ABACUS will internally convert if its default is Bohr.
                         - "Direct": Direct (fractional) coordinates.
                         - "Cartesian_Bohr": Cartesian coordinates in Bohr.
                                             LATTICE_CONSTANT will be 1.0, LATTICE_VECTORS in Bohr.
        user_comments: Optional string for user-defined comments at the top of the file.
        fixed_atoms_indices: Optional list of 0-indexed atom indices whose positions should be fixed.
                             Example: [0, 2] means the first and third atoms are fixed.

    Returns:
        A string containing the formatted STRU file content.
        The 'ntype' (number of atom types) is also returned as part of the dictionary for use in INPUT.
    """
    if isinstance(atoms_obj_or_dict, dict):
        try:
            atoms = atoms_from_dict(atoms_obj_or_dict)
        except ValueError as e:
            raise ValueError(f"Invalid structure dictionary for STRU generation: {e}")
    elif isinstance(atoms_obj_or_dict, Atoms):
        atoms = atoms_obj_or_dict
    else:
        raise TypeError("atoms_obj_or_dict must be an ASE Atoms object or a valid dictionary representation.")

    stru_content = ""
    if user_comments:
        stru_content += textwrap.indent(user_comments, "# ") + "\n\n"

    # ATOMIC_SPECIES section
    stru_content += "ATOMIC_SPECIES\n"
    unique_symbols = sorted(list(set(atoms.get_chemical_symbols())))
    ntype = len(unique_symbols)

    for symbol in unique_symbols:
        if symbol not in pseudo_potential_map:
            raise ValueError(f"Pseudopotential file for element '{symbol}' not found in pseudo_potential_map.")
        mass = atomic_masses[ase_chemical_symbols.index(symbol)] # Get mass from ASE
        pseudo_file = pseudo_potential_map[symbol]
        stru_content += f"{symbol:<5} {mass:<10.4f} {pseudo_file}\n"
    stru_content += "\n"

    # NUMERICAL_ORBITAL section (optional)
    if orbital_file_map:
        stru_content += "NUMERICAL_ORBITAL\n"
        for symbol in unique_symbols:
            if symbol not in orbital_file_map:
                raise ValueError(f"Orbital file for element '{symbol}' not found in orbital_file_map.")
            orbital_file = orbital_file_map[symbol]
            stru_content += f"{orbital_file}\n" # ABACUS expects one orbital file per line, matching species order
        stru_content += "\n"

    # LATTICE_CONSTANT and LATTICE_VECTORS
    # ABACUS default unit for LATTICE_CONSTANT is Bohr.
    # ASE cell vectors are in Angstrom.
    cell_vectors_angstrom = atoms.get_cell()

    if coordinate_type.lower() == "cartesian_angstrom":
        # Provide cell in Angstrom, positions in Angstrom. ABACUS handles conversion if its internal unit is Bohr.
        # This is often the most straightforward way if ABACUS supports Angstrom inputs directly for Cartesian.
        # Or, if ABACUS expects LATTICE_VECTORS in units of LATTICE_CONSTANT, and LATTICE_CONSTANT is Bohr,
        # then we must convert cell vectors to Bohr.
        # Let's assume for now we set LATTICE_CONSTANT to 1.0 (Angstrom) and provide vectors in Angstrom.
        # This might need adjustment based on precise ABACUS STRU spec for Cartesian coordinates.
        # A safer bet if ABACUS strictly wants Bohr for Cartesian with LATTICE_CONSTANT=1 Bohr:
        # lattice_constant_bohr = 1.0
        # cell_vectors_bohr = cell_vectors_angstrom * ANGSTROM_TO_BOHR
        # stru_content += f"LATTICE_CONSTANT\n{lattice_constant_bohr:.8f} # Unit: Bohr\n\n"
        # stru_content += "LATTICE_VECTORS # Unit: Bohr, scaled by LATTICE_CONSTANT\n"
        # for vec in cell_vectors_bohr:
        #     stru_content += f"{vec[0]:<12.8f} {vec[1]:<12.8f} {vec[2]:<12.8f}\n"
        
        # Simpler: Provide LATTICE_CONSTANT in Angstrom, and vectors in Angstrom.
        # This is how ASE's own ABACUS calculator seems to handle it.
        stru_content += f"LATTICE_CONSTANT\n1.0 # Unit: Angstrom (positions and vectors also in Angstrom)\n\n"
        stru_content += "LATTICE_VECTORS # Unit: Angstrom\n"
        for vec in cell_vectors_angstrom:
            stru_content += f"{vec[0]:<12.8f} {vec[1]:<12.8f} {vec[2]:<12.8f}\n"

    elif coordinate_type.lower() == "cartesian_bohr":
        lattice_constant_bohr = 1.0 # Bohr
        cell_vectors_bohr = cell_vectors_angstrom * ANGSTROM_TO_BOHR
        stru_content += f"LATTICE_CONSTANT\n{lattice_constant_bohr:.8f} # Unit: Bohr\n\n"
        stru_content += "LATTICE_VECTORS # Unit: Bohr\n"
        for vec in cell_vectors_bohr:
            stru_content += f"{vec[0]:<12.8f} {vec[1]:<12.8f} {vec[2]:<12.8f}\n"
    
    elif coordinate_type.lower() == "direct":
        # For Direct coordinates, LATTICE_CONSTANT is usually 1.0 (unitless scaling for vectors)
        # and LATTICE_VECTORS are given in Angstroms.
        stru_content += f"LATTICE_CONSTANT\n1.0 # Unitless for Direct coordinates, vectors in Angstrom\n\n"
        stru_content += "LATTICE_VECTORS # Unit: Angstrom\n"
        for vec in cell_vectors_angstrom:
            stru_content += f"{vec[0]:<12.8f} {vec[1]:<12.8f} {vec[2]:<12.8f}\n"
    else:
        raise ValueError(f"Unsupported coordinate_type: {coordinate_type}")
    stru_content += "\n"


    # ATOMIC_POSITIONS section
    if coordinate_type.lower() == "cartesian_angstrom":
        stru_content += "ATOMIC_POSITIONS # Cartesian coordinates in Angstrom\n"
        positions_to_write = atoms.get_positions() # Angstrom
    elif coordinate_type.lower() == "cartesian_bohr":
        stru_content += "ATOMIC_POSITIONS # Cartesian coordinates in Bohr\n"
        positions_to_write = atoms.get_positions() * ANGSTROM_TO_BOHR # Convert to Bohr
    elif coordinate_type.lower() == "direct":
        stru_content += "ATOMIC_POSITIONS # Direct (fractional) coordinates\n"
        positions_to_write = atoms.get_scaled_positions(wrap=False) # Fractional
    else: # Should have been caught above
        raise ValueError(f"Unsupported coordinate_type for positions: {coordinate_type}")

    # Determine movement constraints (m_x, m_y, m_z)
    # 1 for movable, 0 for fixed. Default is all movable.
    atom_movement_flags = [[1, 1, 1] for _ in range(len(atoms))]
    if fixed_atoms_indices:
        for idx in fixed_atoms_indices:
            if 0 <= idx < len(atoms):
                atom_movement_flags[idx] = [0, 0, 0] # Fix x, y, z
            else:
                # Handle warning or error for invalid index
                print(f"Warning: Invalid index {idx} in fixed_atoms_indices. Skipping.")


    for i, symbol in enumerate(atoms.get_chemical_symbols()):
        pos = positions_to_write[i]
        m_flags = atom_movement_flags[i]
        stru_content += f"{symbol:<5}\n" # Atom label line
        stru_content += f"{pos[0]:<12.8f} {pos[1]:<12.8f} {pos[2]:<12.8f}  {m_flags[0]} {m_flags[1]} {m_flags[2]}\n" # Coordinates and movement flags
    
    return stru_content.strip() + "\n", ntype


if __name__ == '__main__':
    # Keep previous tests for generate_abacus_input
    # ... (code from previous if __name__ block, ensure it runs or is commented out) ...
    # For example, if the previous main block ended with:
    # print("\n--- ABACUS INPUT Generation Tests Completed ---")
    # Then we append the new tests after that.
    # It's important that only one asyncio.run() is active if tests are combined,
    # or they are run in separate script executions.
    # For simplicity here, I'll assume the previous tests are run, then these.
    # A better way would be to have a main test runner function.
    
    # To ensure the previous tests in the same file don't interfere if __main__ is run multiple times
    # or to combine them, one might do:
    # async def main_tests():
    #    print("--- Testing ABACUS INPUT Generation ---")
    #    # ... (input tests) ...
    #    print("\n--- ABACUS INPUT Generation Tests Completed ---")
    #    print("\n--- Testing ABACUS STRU Generation ---")
    #    # ... (stru tests) ...
    #    print("\n--- ABACUS STRU Generation Tests Completed ---")
    # asyncio.run(main_tests())
    # For now, just appending the test call:

    import asyncio # Ensure asyncio is imported
    from ase.build import bulk as ase_bulk # For testing

    print("\n--- Testing ABACUS STRU Generation ---")
    
    # Test 1: Silicon Diamond, Cartesian Angstrom
    si_atoms = ase_bulk("Si", "diamond", a=5.43)
    pseudo_map_si = {"Si": "Si_ONCV_PBE-1.0.upf"}
    stru_str_1, ntype_1 = generate_abacus_stru(si_atoms, pseudo_map_si, coordinate_type="Cartesian_Angstrom")
    print("\nTest 1: Silicon Diamond (Cartesian Angstrom)")
    print(stru_str_1)
    assert "ATOMIC_SPECIES" in stru_str_1
    assert "Si     28.0850 Si_ONCV_PBE-1.0.upf" in stru_str_1 # Mass might vary slightly based on ASE version
    assert "LATTICE_CONSTANT\n1.0 # Unit: Angstrom" in stru_str_1
    assert "LATTICE_VECTORS # Unit: Angstrom" in stru_str_1
    assert "ATOMIC_POSITIONS # Cartesian coordinates in Angstrom" in stru_str_1
    assert "0.00000000   0.00000000   0.00000000  1 1 1" in stru_str_1 # Example position line
    assert ntype_1 == 1

    # Test 2: NaCl, Direct coordinates, with orbitals
    nacl_atoms = ase_bulk("NaCl", "rocksalt", a=5.64)
    pseudo_map_nacl = {"Na": "Na.upf", "Cl": "Cl.upf"}
    orbital_map_nacl = {"Na": "Na.orb", "Cl": "Cl.orb"}
    stru_str_2, ntype_2 = generate_abacus_stru(
        nacl_atoms, 
        pseudo_map_nacl, 
        orbital_file_map=orbital_map_nacl, 
        coordinate_type="Direct"
    )
    print("\nTest 2: NaCl Rocksalt (Direct), with Orbitals")
    print(stru_str_2)
    assert "NUMERICAL_ORBITAL" in stru_str_2
    # Order of species in STRU is sorted alphabetically: Cl, Na
    assert "Cl.orb" in stru_str_2 
    assert "Na.orb" in stru_str_2
    assert "LATTICE_CONSTANT\n1.0 # Unitless for Direct coordinates" in stru_str_2
    assert "ATOMIC_POSITIONS # Direct (fractional) coordinates" in stru_str_2
    assert ntype_2 == 2
    
    # Test 3: H2O molecule, Cartesian Bohr, with fixed atoms
    h2o_atoms_o_first = Atoms('OH2', positions=[(0,0,0), (0,0.757,0.586), (0,-0.757,0.586)], cell=[5,5,5], pbc=True)
    pseudo_map_h2o = {"H": "H.upf", "O": "O.upf"}
    stru_str_3b, ntype_3b = generate_abacus_stru(
        h2o_atoms_o_first, 
        pseudo_map_h2o, 
        coordinate_type="Cartesian_Bohr",
        fixed_atoms_indices=[0] # Fix the Oxygen atom (which is now the first atom)
    )
    print("\nTest 3b: OH2 (Cartesian Bohr), Oxygen (first atom) fixed")
    print(stru_str_3b)
    assert "LATTICE_CONSTANT\n1.00000000 # Unit: Bohr" in stru_str_3b
    assert "LATTICE_VECTORS # Unit: Bohr" in stru_str_3b
    assert "ATOMIC_POSITIONS # Cartesian coordinates in Bohr" in stru_str_3b
    oxygen_pos_line_index = stru_str_3b.find("O\n") # Element symbol is on its own line
    assert oxygen_pos_line_index != -1
    # The coordinate line is the one immediately following the element symbol line
    coord_line_start = stru_str_3b.find("\n", oxygen_pos_line_index) + 1
    coord_line_end = stru_str_3b.find("\n", coord_line_start)
    oxygen_coord_line = stru_str_3b[coord_line_start:coord_line_end]
    assert oxygen_coord_line.strip().endswith("0 0 0")


    # Test 4: Missing pseudopotential
    try:
        # Create a simple Si atom for this test
        si_single_atom = Atoms('Si', positions=[(0,0,0)], cell=[5,5,5], pbc=True)
        generate_abacus_stru(si_single_atom, {"X": "X.upf"}) # Si is in atoms, but X in map
        assert False, "Should have raised ValueError for missing pseudopotential"
    except ValueError as e:
        print(f"\nTest 4: Missing pseudopotential - Caught expected error: {e}")
        assert "Pseudopotential file for element 'Si' not found" in str(e)

    print("\n--- ABACUS STRU Generation Tests Completed ---")
# (在 src/core/abacus_runner.py 文件末尾追加)
# 需要从ASE导入的额外模块
from ase.dft.kpoints import monkhorst_pack, get_special_points # For MP grid and bandpath special points
from ase.cell import Cell # For bandpath generation

def generate_abacus_kpt(
    kpt_generation_mode: str,
    atoms_obj_or_dict: Optional[Union[Atoms, Dict[str, Any]]] = None, # Needed for bandpath
    kpts_size: Optional[List[int]] = None, # For Monkhorst-Pack, e.g., [4, 4, 4]
    kpts_shift: Optional[List[float]] = None, # For Monkhorst-Pack, e.g., [0, 0, 0]
    kpath_definition: Optional[Union[str, Dict[str, Any]]] = None, # For Line mode, e.g., "GXL" or explicit path dict
    kpts_npoints_per_segment: Optional[int] = None, # For Line mode
    explicit_kpoints_list: Optional[List[List[float]]] = None, # For Explicit mode, e.g., [[kx,ky,kz,w], ...]
    user_comments: Optional[str] = None
) -> str:
    """
    Generates the content for an ABACUS KPT file.

    Args:
        kpt_generation_mode: "Monkhorst-Pack", "Line" (or "Bandpath"), or "Explicit".
        atoms_obj_or_dict: ASE Atoms object or its dictionary representation.
                           Required for "Line" mode to get cell and special points.
        kpts_size: For "Monkhorst-Pack" mode, list of 3 integers for grid dimensions.
        kpts_shift: For "Monkhorst-Pack" mode, list of 3 floats for grid shift. Default [0,0,0].
        kpath_definition: For "Line" mode. Can be:
                          - A string defining path by special point names, e.g., "GXLKM".
                          - A dictionary defining segments: {"path": "GX,XL", "special_points": {"G":[0,0,0], "X":[0.5,0,0.5]...}}
        kpts_npoints_per_segment: For "Line" mode, number of k-points per segment.
        explicit_kpoints_list: For "Explicit" mode, a list of k-points, where each k-point
                               is [kx, ky, kz, weight].
        user_comments: Optional string for user-defined comments at the top of the file.

    Returns:
        A string containing the formatted KPT file content.
    """
    kpt_content = ""
    if user_comments:
        kpt_content += textwrap.indent(user_comments, "# ") + "\n\n"

    mode = kpt_generation_mode.lower()

    if mode in ["monkhorst-pack", "mp", "grid"]:
        if not kpts_size or len(kpts_size) != 3:
            raise ValueError("For Monkhorst-Pack mode, 'kpts_size' (list of 3 ints) is required.")
        
        shift = kpts_shift if kpts_shift and len(kpts_shift) == 3 else [0.0, 0.0, 0.0]
        
        kpt_content += "K_POINTS\n"
        kpt_content += "0 # Number of k-points, 0 means Monkhorst-Pack from next line\n"
        kpt_content += f"{kpts_size[0]} {kpts_size[1]} {kpts_size[2]}  {shift[0]} {shift[1]} {shift[2]} # nx ny nz sx sy sz\n"

    elif mode in ["line", "bandpath"]:
        if not atoms_obj_or_dict:
            raise ValueError("For Line (Bandpath) mode, 'atoms_obj_or_dict' is required.")
        if not kpath_definition or not kpts_npoints_per_segment:
            raise ValueError("For Line (Bandpath) mode, 'kpath_definition' and 'kpts_npoints_per_segment' are required.")

        if isinstance(atoms_obj_or_dict, dict):
            atoms = atoms_from_dict(atoms_obj_or_dict) # Assumes atoms_from_dict is defined in the same file
        else:
            atoms = atoms_obj_or_dict
        
        cell_obj = Cell(atoms.get_cell()) # Create ASE Cell object

        kpt_content += "K_POINTS\n"
        # ABACUS Line mode: first line is number of k-points, then "Line"
        # The actual k-points are then listed one by one with weight 1.0 (for band structure)
        
        path_kpts_list = [] # Changed variable name to avoid conflict if path_kpts is used elsewhere
        if isinstance(kpath_definition, str): # e.g. "GXL"
            try:
                bandpath = cell_obj.bandpath(kpath_definition, npoints=kpts_npoints_per_segment)
                path_kpts_list = bandpath.kpts
            except Exception as e:
                raise ValueError(f"Could not generate bandpath from string '{kpath_definition}': {e}. Ensure special points are defined for the cell or provide explicit path dictionary.")

        elif isinstance(kpath_definition, dict): # e.g. {"path": "GX,XL", "special_points": {...}}
            path_str = kpath_definition.get("path")
            special_points_dict = kpath_definition.get("special_points")
            if not path_str or not special_points_dict:
                raise ValueError("For dictionary kpath_definition, 'path' string and 'special_points' dict are required.")
            try:
                bandpath = cell_obj.bandpath(path_str, special_points=special_points_dict, npoints=kpts_npoints_per_segment)
                path_kpts_list = bandpath.kpts
            except Exception as e:
                raise ValueError(f"Could not generate bandpath from dictionary definition: {e}")
        else:
            raise TypeError("'kpath_definition' must be a string or a dictionary.")

        if not path_kpts_list.any(): # Check if the numpy array is empty
             raise ValueError("Generated k-point path is empty.")

        kpt_content += f"{len(path_kpts_list)} # Total number of k-points for band structure\n"
        kpt_content += "Line # Indicates line mode for band structure\n"
        for kpt_coords in path_kpts_list: # Iterate through coordinates
            # ABACUS KPT for line mode: kx ky kz 1.0 (weight is 1.0 for band structure points)
            kpt_content += f"{kpt_coords[0]:<12.8f} {kpt_coords[1]:<12.8f} {kpt_coords[2]:<12.8f}  1.0\n"
            
    elif mode == "explicit":
        if not explicit_kpoints_list or not isinstance(explicit_kpoints_list, list):
            raise ValueError("For Explicit mode, 'explicit_kpoints_list' (list of [kx,ky,kz,w]) is required.")
        
        kpt_content += "K_POINTS\n"
        kpt_content += f"{len(explicit_kpoints_list)} # Number of k-points\n"
        kpt_content += "Cartesian # Or Direct, assuming Cartesian for explicit k-points for now\n" # ABACUS might need specific keyword
        for kpt_info in explicit_kpoints_list:
            if len(kpt_info) != 4:
                raise ValueError("Each item in 'explicit_kpoints_list' must be [kx, ky, kz, weight].")
            kpt_content += f"{kpt_info[0]:<12.8f} {kpt_info[1]:<12.8f} {kpt_info[2]:<12.8f}  {kpt_info[3]:<8.4f}\n"
            
    else:
        raise ValueError(f"Unsupported kpt_generation_mode: {mode}. Supported modes: Monkhorst-Pack, Line, Explicit.")

    return kpt_content.strip() + "\n"


if __name__ == '__main__':
    # ... (previous test blocks for generate_abacus_input and generate_abacus_stru) ...
    # Ensure asyncio is imported if not already
    import asyncio # Make sure asyncio is imported in this scope
    from ase.build import bulk as ase_bulk # Already imported for STRU tests

    # It's better to define an async main function to run all tests if they are async
    # or ensure they are called correctly if some are sync and some async.
    # For now, assuming the previous test calls in __main__ are handled (e.g. commented out or part of a larger async test runner)
    
    async def run_kpt_tests(): # Wrap KPT tests in an async function if other tests are async
        print("\n--- Testing ABACUS KPT Generation ---")

        # Test 1: Monkhorst-Pack
        kpt_str_1 = generate_abacus_kpt(
            kpt_generation_mode="Monkhorst-Pack",
            kpts_size=[4, 4, 4],
            kpts_shift=[0.0, 0.0, 0.0],
            user_comments="MP grid for Si SCF"
        )
        print("\nTest 1: Monkhorst-Pack grid")
        print(kpt_str_1)
        assert "K_POINTS" in kpt_str_1
        assert "0 # Number of k-points" in kpt_str_1
        assert "4 4 4  0.0 0.0 0.0" in kpt_str_1
        assert "# MP grid for Si SCF" in kpt_str_1

        # Test 2: Line mode (Bandpath) for FCC structure (e.g., Si)
        si_atoms_for_kpt = ase_bulk("Si", "diamond", a=5.43) # Diamond is FCC-like for bandpath
        
        kpt_str_2 = generate_abacus_kpt(
            kpt_generation_mode="Line",
            atoms_obj_or_dict=si_atoms_for_kpt,
            kpath_definition="GXWKGLUWLK", 
            kpts_npoints_per_segment=20
        )
        print("\nTest 2: Line mode (Bandpath) for Si (FCC-like)")
        print(kpt_str_2)
        assert "K_POINTS" in kpt_str_2
        assert "Line # Indicates line mode" in kpt_str_2
        num_kpts_line_2 = int(kpt_str_2.splitlines()[1].split("#")[0].strip()) 
        assert num_kpts_line_2 > 20 
        assert "1.0" in kpt_str_2 

        fcc_special_points = get_special_points('fcc')
        kpt_str_2b = generate_abacus_kpt(
            kpt_generation_mode="Line",
            atoms_obj_or_dict=si_atoms_for_kpt,
            kpath_definition={"path": "G-X-L", "special_points": fcc_special_points},
            kpts_npoints_per_segment=15
        )
        print("\nTest 2b: Line mode (Bandpath) with explicit special points dict")
        print(kpt_str_2b)
        assert "K_POINTS" in kpt_str_2b
        assert "Line # Indicates line mode" in kpt_str_2b
        num_kpts_line_2b = int(kpt_str_2b.splitlines()[1].split("#")[0].strip())
        assert num_kpts_line_2b >= 2 * (15-1) + 1


        # Test 3: Explicit k-points
        explicit_kpts = [
            [0.0, 0.0, 0.0, 0.5],
            [0.5, 0.0, 0.0, 0.25],
            [0.0, 0.5, 0.0, 0.25]
        ]
        kpt_str_3 = generate_abacus_kpt(
            kpt_generation_mode="Explicit",
            explicit_kpoints_list=explicit_kpts
        )
        print("\nTest 3: Explicit k-points")
        print(kpt_str_3)
        assert "K_POINTS" in kpt_str_3
        assert "3 # Number of k-points" in kpt_str_3
        assert "Cartesian # Or Direct" in kpt_str_3
        assert "0.00000000   0.00000000   0.00000000  0.5000" in kpt_str_3
        assert "0.50000000   0.00000000   0.00000000  0.2500" in kpt_str_3

        # Test 4: Invalid mode
        try:
            generate_abacus_kpt(kpt_generation_mode="Unknown")
            assert False, "Should have raised ValueError for unknown mode"
        except ValueError as e:
            print(f"\nTest 4: Unknown mode - Caught expected error: {e}")
            assert "Unsupported kpt_generation_mode" in str(e)

        print("\n--- ABACUS KPT Generation Tests Completed ---")

    # If the other tests in __main__ are also async, they should be awaited in a single asyncio.run(main_async_test_runner())
    # For now, just running the KPT tests.
    # To run all tests if they are defined as async functions:
    # async def run_all_core_tests():
    #    await test_input_generation_async_wrapper() # Assuming previous tests are wrapped if needed
    #    await test_stru_generation_async_wrapper()  # Assuming previous tests are wrapped if needed
    #    await run_kpt_tests()
    # asyncio.run(run_all_core_tests())
    
    # This will append the KPT test execution to whatever was in __main__ before.
    # If previous tests were not async, this might cause issues or run them sequentially if not awaited.
    # For isolated testing of this new function:
    if __name__ == '__main__': # This condition might be redundant if already inside one.
                               # It's better to have one main async runner.
        # Comment out or integrate previous asyncio.run calls if they exist in the same __main__ block
        asyncio.run(run_kpt_tests())
import asyncio # Ensure asyncio is imported at the top level of the module if not already
import os
import tempfile
import shutil # For managing temporary directories

async def execute_abacus_command(
    abacus_command: str, # e.g., "abacus" or "mpirun -n 4 abacus"
    input_content: str,
    stru_content: str,
    kpt_content: str,
    pseudo_potential_files: Dict[str, str], # {"Si.UPF": "/path/to/Si.UPF", ...}
    orbital_files: Optional[Dict[str, str]] = None, # {"Si.orb": "/path/to/Si.orb", ...}
    working_directory_base: Optional[str] = None, # Base for temp working dir
    timeout_seconds: Optional[float] = 3600.0 # Default timeout 1 hour
) -> Dict[str, Any]:
    """
    Executes an ABACUS command in a temporary working directory with generated input files.

    Args:
        abacus_command: The command to execute ABACUS (e.g., "abacus", "mpirun -n 4 abacus").
        input_content: String content for the INPUT file.
        stru_content: String content for the STRU file.
        kpt_content: String content for the KPT file.
        pseudo_potential_files: A dictionary mapping pseudopotential filenames (as used in STRU)
                                to their actual source file paths.
        orbital_files: An optional dictionary mapping orbital filenames (as used in STRU)
                       to their actual source file paths.
        working_directory_base: Optional base path to create the temporary working directory.
                                If None, system's default temp dir is used.
        timeout_seconds: Timeout for the ABACUS command execution.

    Returns:
        A dictionary containing:
            - success (bool): True if ABACUS ran and exited with code 0.
            - return_code (int): Exit code of the ABACUS process.
            - stdout (str): Standard output from ABACUS.
            - stderr (str): Standard error from ABACUS.
            - working_directory (str): Path to the temporary working directory used.
            - error (str, optional): Error message if setup or execution failed before ABACUS run.
    """
    temp_work_dir = tempfile.mkdtemp(prefix="abacus_run_", dir=working_directory_base)
    
    results = {
        "success": False,
        "return_code": None,
        "stdout": "",
        "stderr": "",
        "working_directory": temp_work_dir,
        "error": None
    }

    try:
        # 1. Write INPUT, STRU, KPT files
        with open(os.path.join(temp_work_dir, "INPUT"), "w") as f:
            f.write(input_content)
        with open(os.path.join(temp_work_dir, "STRU"), "w") as f:
            f.write(stru_content)
        with open(os.path.join(temp_work_dir, "KPT"), "w") as f:
            f.write(kpt_content)

        # 2. Copy pseudopotential files
        # The pseudo_dir in INPUT should ideally point to the current directory "."
        # if we copy files directly into temp_work_dir.
        for dest_filename, src_path in pseudo_potential_files.items():
            if not os.path.exists(src_path):
                raise FileNotFoundError(f"Pseudopotential source file not found: {src_path}")
            shutil.copy(src_path, os.path.join(temp_work_dir, dest_filename))

        # 3. Copy orbital files (if any)
        if orbital_files:
            for dest_filename, src_path in orbital_files.items():
                if not os.path.exists(src_path):
                    raise FileNotFoundError(f"Orbital source file not found: {src_path}")
                shutil.copy(src_path, os.path.join(temp_work_dir, dest_filename))

        # Copy additional files (e.g. charge density for NSCF)
        if additional_files_to_copy:
            for dest_filename, src_full_path in additional_files_to_copy.items():
                if not os.path.exists(src_full_path):
                    print(f"Warning: Additional file to copy not found: {src_full_path}. Skipping.")
                    results.setdefault("warnings", []).append(f"Additional file to copy not found and skipped: {src_full_path}")
                    continue
                shutil.copy(src_full_path, os.path.join(temp_work_dir, dest_filename))
        
        if results["task_id"]: update_task_status(task_id, "running", start_time=True)
        
        # 4. Execute ABACUS command
        command_parts = abacus_command.split()
        env = os.environ.copy()
        if "OMP_NUM_THREADS" not in env:
            env["OMP_NUM_THREADS"] = "1"

        process = await asyncio.create_subprocess_exec(
            *command_parts,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=temp_work_dir,
            env=env
        )

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(process.communicate(), timeout=timeout_seconds)
            results["stdout"] = stdout_bytes.decode(errors='replace')
            results["stderr"] = stderr_bytes.decode(errors='replace')
            results["return_code"] = process.returncode
            if process.returncode == 0:
                results["success"] = True
                if results["task_id"]: update_task_status(task_id, "processing_output")
            else:
                results["error"] = f"ABACUS process exited with code {process.returncode}."
                results["success"] = False
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            results["error"] = f"ABACUS command timed out after {timeout_seconds} seconds."
            results["return_code"] = -1
            results["stderr"] = results.get("stderr","") + "\nEXECUTION TIMEOUT"
            results["success"] = False
            if results["task_id"]: update_task_status(task_id, "failed_timeout", end_time=True)
        
        # Capture specified output files
        if capture_output_files:
            current_input_params = input_params_for_task_mgmt or {}
            output_subdir_name = f"OUT.{current_input_params.get('prefix', 'ABACUS')}"
            possible_output_locations = [
                os.path.join(temp_work_dir, output_subdir_name),
                temp_work_dir
            ]
            for fname_to_capture in capture_output_files:
                found_file = False
                for loc in possible_output_locations:
                    fpath = os.path.join(loc, fname_to_capture)
                    if os.path.exists(fpath) and os.path.isfile(fpath):
                        try:
                            with open(fpath, 'r', encoding='utf-8', errors='replace') as f_out:
                                results["captured_files_content"][fname_to_capture] = f_out.read()
                            found_file = True
                            break
                        except Exception as e_read:
                            results.setdefault("warnings", []).append(f"Could not read captured output file {fpath}: {str(e_read)}")
                if not found_file:
                     results.setdefault("warnings", []).append(f"Specified output file to capture not found: {fname_to_capture} in {possible_output_locations}")
        
        if results["success"] and results["task_id"]:
            update_task_status(task_id, "completed_execution_phase")

    except FileNotFoundError as fnf_err:
        results["error"] = f"File setup error: {str(fnf_err)}"
        results["success"] = False
        if results["task_id"]: update_task_status(task_id, "failed_file_not_found", end_time=True)
    except Exception as e:
        results["error"] = f"An unexpected error occurred: {str(e)}"
        results["success"] = False
        if results["task_id"]: update_task_status(task_id, "failed_exception", end_time=True)
    finally:
        if results["task_id"]:
            errors_for_task_mgmt = []
            if results.get("error"): errors_for_task_mgmt.append(results["error"])
            
            stderr_content = results.get("stderr", "")
            if stderr_content and not results.get("success"):
                is_stderr_in_error = results.get("error") and stderr_content in results.get("error", "")
                if not is_stderr_in_error:
                    errors_for_task_mgmt.append(f"STDERR: {stderr_content[:1000]}")

            data_summary_for_task_mgmt = {
                "execution_successful": results["success"],
                "return_code": results.get("return_code"),
                "captured_files_count": len(results.get("captured_files_content", {}))
            }
            
            logs_for_task_mgmt = {
                "working_directory": temp_work_dir,
                "stdout_snippet": results.get("stdout", "")[:2000],
                "stderr_snippet": stderr_content[:2000] if stderr_content else None
            }

            record_task_completion(
                task_id=task_id,
                success=results["success"],
                results_data=data_summary_for_task_mgmt,
                logs_data=logs_for_task_mgmt,
                errors_list=errors_for_task_mgmt
            )
        
        try:
            temp_work_dir_obj.cleanup()
        except Exception as e_cleanup:
            print(f"Error cleaning up temporary directory {temp_work_dir}: {e_cleanup}")
            results.setdefault("warnings", []).append(f"Error cleaning up temp dir: {e_cleanup}")
            
    return results

if __name__ == '__main__':
    # ... (previous test blocks for generate_abacus_input, stru, kpt) ...
    # Ensure asyncio is imported
    import asyncio 
    # from ase.build import bulk as ase_bulk # Not strictly needed for this test block if others are separate

    async def test_execute_abacus():
        print("\n--- Testing ABACUS Command Execution (Mocked) ---")

        # Create dummy pseudo file for testing
        dummy_pseudo_dir = tempfile.mkdtemp(prefix="dummy_pseudo_")
        dummy_si_upf_path = os.path.join(dummy_pseudo_dir, "Si.UPF")
        with open(dummy_si_upf_path, "w") as f:
            f.write("This is a dummy Si UPF file.")

        # Create a mock abacus executable (simple echo script)
        mock_abacus_dir = tempfile.mkdtemp(prefix="mock_abacus_")
        # Choose script extension based on OS or make it a python script for x-platform
        mock_abacus_script_name = "mock_abacus.bat" if os.name == 'nt' else "mock_abacus.sh"
        mock_abacus_script_path = os.path.join(mock_abacus_dir, mock_abacus_script_name)
        
        if os.name == 'nt':
            mock_script_content = f"""@echo off
echo Mock ABACUS Standard Output
echo Mock ABACUS Standard Error >&2
rem Simulate reading input files by checking existence (optional)
rem if not exist INPUT exit /b 2
rem if not exist STRU exit /b 3
rem if not exist KPT exit /b 4
mkdir OUT.ABACUS 2>nul
echo Total energy = -100.0 Ry > OUT.ABACUS\\running_scf.log
exit /b 0
"""
        else: # POSIX-like
            mock_script_content = f"""#!/bin/bash
echo "Mock ABACUS Standard Output"
echo "Mock ABACUS Standard Error" >&2
# Simulate reading input files
cat INPUT STRU KPT > /dev/null 
# Simulate creating an output file
mkdir -p OUT.ABACUS
echo "Total energy = -100.0 Ry" > OUT.ABACUS/running_scf.log 
exit 0
"""
        with open(mock_abacus_script_path, "w") as f:
            f.write(mock_script_content)
        if os.name != 'nt':
            os.chmod(mock_abacus_script_path, 0o755) # Make it executable

        # Test 1: Successful execution
        print("\nTest 1: Mock successful ABACUS run")
        input_content = "INPUT_PARAMETERS\n..."
        stru_content = "ATOMIC_SPECIES\nSi 28 Si.UPF\n..."
        kpt_content = "K_POINTS\n0\n2 2 2 0 0 0"
        
        results_success = await execute_abacus_command(
            abacus_command=mock_abacus_script_path, 
            input_content=input_content,
            stru_content=stru_content,
            kpt_content=kpt_content,
            pseudo_potential_files={"Si.UPF": dummy_si_upf_path},
            working_directory_base=None, 
            timeout_seconds=10
        )
        print(f"  Success: {results_success['success']}")
        print(f"  Return Code: {results_success['return_code']}")
        print(f"  Stdout: {results_success['stdout'].strip()}")
        print(f"  Stderr: {results_success['stderr'].strip()}")
        print(f"  Working Dir: {results_success['working_directory']}")
        assert results_success['success']
        assert results_success['return_code'] == 0
        assert "Mock ABACUS Standard Output" in results_success['stdout']
        assert "Mock ABACUS Standard Error" in results_success['stderr']
        mock_output_file = os.path.join(results_success['working_directory'], "OUT.ABACUS", "running_scf.log")
        assert os.path.exists(mock_output_file)
        shutil.rmtree(results_success['working_directory']) 

        # Test 2: Mock command failure
        mock_fail_script_name = "mock_abacus_fail.bat" if os.name == 'nt' else "mock_abacus_fail.sh"
        mock_fail_script_path = os.path.join(mock_abacus_dir, mock_fail_script_name)
        if os.name == 'nt':
            mock_fail_content = "@echo off\necho Error occurred\nexit /b 1"
        else:
            mock_fail_content = "#!/bin/bash\necho 'Error occurred'\nexit 1"
        with open(mock_fail_script_path, "w") as f:
            f.write(mock_fail_content)
        if os.name != 'nt':
            os.chmod(mock_fail_script_path, 0o755)

        print("\nTest 2: Mock ABACUS run with non-zero exit code")
        results_fail = await execute_abacus_command(
            abacus_command=mock_fail_script_path,
            input_content="input", stru_content="stru", kpt_content="kpt",
            pseudo_potential_files={"Si.UPF": dummy_si_upf_path},
            timeout_seconds=5
        )
        print(f"  Success: {results_fail['success']}")
        print(f"  Return Code: {results_fail['return_code']}")
        print(f"  Error: {results_fail['error']}")
        assert not results_fail['success']
        assert results_fail['return_code'] == 1
        shutil.rmtree(results_fail['working_directory'])

        # Test 3: Timeout
        mock_timeout_script_name = "mock_abacus_timeout.bat" if os.name == 'nt' else "mock_abacus_timeout.sh"
        mock_timeout_script_path = os.path.join(mock_abacus_dir, mock_timeout_script_name)
        if os.name == 'nt':
            mock_timeout_content = "@echo off\necho Starting sleep...\nping 127.0.0.1 -n 6 > nul \necho Sleep finished" # Approx 5s sleep
        else:
            mock_timeout_content = "#!/bin/bash\necho 'Starting sleep...'\nsleep 5\necho 'Sleep finished (should not reach here)'"
        with open(mock_timeout_script_path, "w") as f:
            f.write(mock_timeout_content)
        if os.name != 'nt':
            os.chmod(mock_timeout_script_path, 0o755)

        print("\nTest 3: ABACUS command timeout")
        results_timeout = await execute_abacus_command(
            abacus_command=mock_timeout_script_path,
            input_content="input", stru_content="stru", kpt_content="kpt",
            pseudo_potential_files={"Si.UPF": dummy_si_upf_path},
            timeout_seconds=1 
        )
        print(f"  Success: {results_timeout['success']}")
        print(f"  Return Code: {results_timeout['return_code']}")
        print(f"  Error: {results_timeout['error']}")
        print(f"  Stderr: {results_timeout['stderr'].strip()}")
        assert not results_timeout['success']
        assert results_timeout['return_code'] == -1 
        assert "timed out" in results_timeout['error']
        assert "EXECUTION TIMEOUT" in results_timeout['stderr']
        shutil.rmtree(results_timeout['working_directory'])


        shutil.rmtree(dummy_pseudo_dir)
        shutil.rmtree(mock_abacus_dir)
        print("\n--- ABACUS Command Execution Tests Completed ---")
    
    # This structure for __main__ assumes you might have other async test functions
    # like run_input_tests(), run_stru_tests(), run_kpt_tests() defined elsewhere
    # and want to run them all.
    async def run_all_core_tests():
        # Placeholder: Call other test functions if they are refactored to be async and callable
        # print("--- Running All Core ABACUS Runner Tests ---")
        # await test_input_generation_async_wrapper() # If exists
        # await test_stru_generation_async_wrapper()  # If exists
        # await run_kpt_tests() # If run_kpt_tests is defined as async
        await test_execute_abacus()

    if __name__ == '__main__':
        asyncio.run(run_all_core_tests())
import re # For regular expression parsing

def parse_abacus_scf_output(output_content: str) -> Dict[str, Any]:
    """
    Parses the output content from an ABACUS SCF calculation to extract key information.

    Args:
        output_content: String content of the ABACUS output (e.g., from running_scf.log or stdout).

    Returns:
        A dictionary containing parsed data:
            - "converged" (bool): Whether the SCF calculation converged.
            - "total_energy_ry" (float | None): Total energy in Rydberg, if found.
            - "total_energy_ev" (float | None): Total energy in eV, if found.
            - "fermi_energy_ry" (float | None): Fermi energy in Rydberg, if found.
            - "fermi_energy_ev" (float | None): Fermi energy in eV, if found.
            - "scf_iterations" (int | None): Number of SCF iterations, if found.
            - "warnings" (List[str]): List of any parsing warnings.
            - "errors" (List[str]): List of parsing errors or messages indicating missing data.
    """
    results: Dict[str, Any] = {
        "converged": False,
        "total_energy_ry": None,
        "total_energy_ev": None,
        "fermi_energy_ry": None,
        "fermi_energy_ev": None,
        "scf_iterations": None,
        "forces_on_atoms": None, # Placeholder for future force parsing
        "stress_tensor": None,   # Placeholder for future stress parsing
        "warnings": [],
        "errors": []
    }

    # Regex patterns (these might need refinement based on exact ABACUS output versions)
    # For total energy (usually the last one reported is the most relevant)
    # Example: "!FINAL_ETOTAL_IS        -7.6017368461 Ry"
    # Example: "TOTAL ENERGY      =     -103.39468523 eV" (from some calcs)
    total_energy_ry_pattern = re.compile(r"!FINAL_ETOTAL_IS\s+([-+]?\d*\.\d+|\d+)\s+Ry", re.IGNORECASE)
    total_energy_ev_pattern = re.compile(r"TOTAL ENERGY\s+=\s*([-+]?\d*\.\d+|\d+)\s+eV", re.IGNORECASE) # More general

    # For Fermi energy
    # Example: "EFERMI                  INPUTAS         -0.00000000 Ry"
    # Example: "E_FERMI: XXX Ry" or "E_FERMI: XXX eV"
    fermi_energy_ry_pattern = re.compile(r"EFERMI\s+([-+]?\d*\.\d+|\d+)\s+Ry", re.IGNORECASE)
    fermi_energy_ev_pattern = re.compile(r"E_FERMI:\s*([-+]?\d*\.\d+|\d+)\s*(eV|Ry)", re.IGNORECASE)


    # For SCF convergence status
    convergence_achieved_pattern = re.compile(r"convergence has been achieved", re.IGNORECASE)
    convergence_not_achieved_pattern = re.compile(r"convergence NOT achieved", re.IGNORECASE)
    
    # For SCF iterations
    # Example: "ITER            ETOT(RY)          DRHO    RMS_DRHO   TIME(S)"
    #          "   1        -7.60172997      0.11E-05    0.11E-05      6.09S"
    #          ...
    #          "   5        -7.60173685      0.12E-06    0.12E-06      6.10S"
    # Or: "Mixing method = BROYDEN, Iteration =   15"
    scf_iter_line_pattern = re.compile(r"^\s*(\d+)\s+([-+]?\d*\.\d+)\s+", re.MULTILINE) # Captures iter and etot
    scf_iter_mixing_pattern = re.compile(r"Iteration\s*=\s*(\d+)", re.IGNORECASE)


    # Search for convergence
    if convergence_achieved_pattern.search(output_content):
        results["converged"] = True
    elif convergence_not_achieved_pattern.search(output_content):
        results["converged"] = False
        results["warnings"].append("SCF convergence was NOT achieved according to the output.")
    else:
        results["warnings"].append("SCF convergence status could not be definitively determined from the output.")

    # Search for total energy (Ry)
    # Find all matches and take the last one, as it's usually the final value
    all_etotal_ry = total_energy_ry_pattern.findall(output_content)
    if all_etotal_ry:
        results["total_energy_ry"] = float(all_etotal_ry[-1])
    
    # Search for total energy (eV) - often appears in different contexts or as summary
    all_etotal_ev = total_energy_ev_pattern.findall(output_content)
    if all_etotal_ev:
        # If Ry value already found, this eV might be redundant or a different type of total energy.
        # Prioritize the Ry one if both exist, or decide on a conversion strategy.
        # For now, just store it if found.
        results["total_energy_ev"] = float(all_etotal_ev[-1])


    # If only one energy is found, try to convert (1 Ry = 13.605693122994 eV)
    RY_TO_EV = 13.605693122994
    if results["total_energy_ry"] is not None and results["total_energy_ev"] is None:
        results["total_energy_ev"] = results["total_energy_ry"] * RY_TO_EV
    elif results["total_energy_ev"] is not None and results["total_energy_ry"] is None:
        # Check if the eV pattern might have captured Ry by mistake due to unit in regex
        # This is less likely with the current specific Ry pattern.
        # results["total_energy_ry"] = results["total_energy_ev"] / RY_TO_EV
        pass # Avoid back-converting if eV was explicitly found with "eV" unit

    if results["total_energy_ry"] is None and results["total_energy_ev"] is None:
         results["errors"].append("Total energy could not be parsed from the output.")


    # Search for Fermi energy
    all_fermi_ry = fermi_energy_ry_pattern.findall(output_content)
    if all_fermi_ry:
        results["fermi_energy_ry"] = float(all_fermi_ry[-1]) # Take the last one

    all_fermi_ev_matches = fermi_energy_ev_pattern.findall(output_content)
    if all_fermi_ev_matches:
        val_str, unit_str = all_fermi_ev_matches[-1]
        val = float(val_str)
        if unit_str.lower() == "ev":
            results["fermi_energy_ev"] = val
            if results["fermi_energy_ry"] is None: # Convert if Ry not found
                 results["fermi_energy_ry"] = val / RY_TO_EV
        elif unit_str.lower() == "ry":
            if results["fermi_energy_ry"] is None: # Prioritize if already found by specific Ry pattern
                results["fermi_energy_ry"] = val
            if results["fermi_energy_ev"] is None:
                results["fermi_energy_ev"] = val * RY_TO_EV
    
    # Final conversion check for Fermi energy
    if results["fermi_energy_ry"] is not None and results["fermi_energy_ev"] is None:
        results["fermi_energy_ev"] = results["fermi_energy_ry"] * RY_TO_EV
    elif results["fermi_energy_ev"] is not None and results["fermi_energy_ry"] is None:
        results["fermi_energy_ry"] = results["fermi_energy_ev"] / RY_TO_EV
    
    if results["fermi_energy_ry"] is None and results["fermi_energy_ev"] is None: # Check after all attempts
        results["errors"].append("Fermi energy could not be parsed from the output.")


    # Search for SCF iterations
    max_iter_found = 0
    for match in scf_iter_line_pattern.finditer(output_content):
        max_iter_found = max(max_iter_found, int(match.group(1)))
    
    if max_iter_found > 0:
        results["scf_iterations"] = max_iter_found
    else: # Try alternative pattern if the table-like one isn't found
        all_iter_mixing = scf_iter_mixing_pattern.findall(output_content)
        if all_iter_mixing:
            results["scf_iterations"] = int(all_iter_mixing[-1]) # Last iteration number reported
            
    if results["scf_iterations"] is None:
        results["errors"].append("Number of SCF iterations could not be parsed.")

    return results


if __name__ == '__main__':
    # ... (previous test blocks) ...
    import asyncio # Ensure asyncio is imported

    async def test_parse_scf_output(): # Make it async if other tests are, or run separately
        print("\n--- Testing ABACUS SCF Output Parsing ---")

        sample_output_converged = """
        Some initial lines...
        Begin SCF Calculation
        ITER            ETOT(RY)          DRHO    RMS_DRHO   TIME(S)
           1        -7.60172997      0.11E-05    0.11E-05      6.09S
           2        -7.60173500      0.10E-06    0.10E-06      6.10S
        Mixing method = BROYDEN, Iteration =    2
        !FINAL_ETOTAL_IS        -7.6017368461 Ry
        EFERMI                  0.123456 Ry  some other text
        E_FERMI: 3.3593 eV
        convergence has been achieved
        Total time: 12.0 s
        """
        parsed1 = parse_abacus_scf_output(sample_output_converged)
        print("\nTest 1: Converged SCF")
        print(parsed1)
        assert parsed1["converged"]
        assert abs(parsed1["total_energy_ry"] - (-7.6017368461)) < 1e-9
        assert abs(parsed1["total_energy_ev"] - (-7.6017368461 * 13.605693122994)) < 1e-7
        assert abs(parsed1["fermi_energy_ry"] - 0.123456) < 1e-9
        assert abs(parsed1["fermi_energy_ev"] - 3.3593) < 1e-7 # Check if eV from E_FERMI is picked up
        assert parsed1["scf_iterations"] == 2

        sample_output_not_converged = """
        Begin SCF Calculation
        ITER            ETOT(RY)          DRHO    RMS_DRHO   TIME(S)
           1        -5.12300000      0.10E-02    0.10E-02      1.00S
          ...
          50        -5.12345678      0.50E-05    0.50E-05      50.0S
        Mixing method = PULAY, Iteration =   50
        !FINAL_ETOTAL_IS        -5.1234567800 Ry
        EFERMI                  -0.0500000 Ry
        convergence NOT achieved after 50 iterations
        """
        parsed2 = parse_abacus_scf_output(sample_output_not_converged)
        print("\nTest 2: Not Converged SCF")
        print(parsed2)
        assert not parsed2["converged"]
        assert "SCF convergence was NOT achieved" in parsed2["warnings"][0]
        assert abs(parsed2["total_energy_ry"] - (-5.1234567800)) < 1e-9
        assert abs(parsed2["fermi_energy_ry"] - (-0.0500000)) < 1e-9
        assert parsed2["scf_iterations"] == 50

        sample_output_no_fermi = """
        !FINAL_ETOTAL_IS        -2.0 Ry
        convergence has been achieved
        ITERATION    1
        """
        parsed3 = parse_abacus_scf_output(sample_output_no_fermi)
        print("\nTest 3: No Fermi Energy, minimal iter info")
        print(parsed3)
        assert parsed3["converged"]
        assert abs(parsed3["total_energy_ry"] - (-2.0)) < 1e-9
        assert "Fermi energy could not be parsed" in parsed3["errors"]
        assert parsed3["scf_iterations"] == 1 # From ITERATION 1

        sample_output_total_ev_only = """
        TOTAL ENERGY      =     -103.39468523 eV
        E_FERMI: -1.234 eV
        convergence has been achieved
        Iteration = 3
        """
        parsed4 = parse_abacus_scf_output(sample_output_total_ev_only)
        print("\nTest 4: Total Energy in eV only, Fermi in eV")
        print(parsed4)
        assert parsed4["converged"]
        assert parsed4["total_energy_ry"] is not None # Should be converted
        assert abs(parsed4["total_energy_ev"] - (-103.39468523)) < 1e-7
        assert abs(parsed4["fermi_energy_ev"] - (-1.234)) < 1e-7
        assert parsed4["fermi_energy_ry"] is not None # Should be converted
        assert parsed4["scf_iterations"] == 3


        print("\n--- ABACUS SCF Output Parsing Tests Completed ---")

    # Modify the main execution block to run all tests
    async def run_all_core_tests():
        # print("--- Testing ABACUS INPUT Generation ---")
        # # Inline or call previous input tests if they were async
        # print("\n--- ABACUS INPUT Generation Tests Completed ---")
        
        # print("\n--- Testing ABACUS STRU Generation ---")
        # # Inline or call previous stru tests if they were async
        # print("\n--- ABACUS STRU Generation Tests Completed ---")

        # print("\n--- Testing ABACUS KPT Generation ---")
        # await run_kpt_tests() # Assuming run_kpt_tests is defined as async above

        # print("\n--- Testing ABACUS Command Execution (Mocked) ---")
        # await test_execute_abacus() # Assuming test_execute_abacus is defined as async above
        
        await test_parse_scf_output()

    if __name__ == '__main__':
        # This will now only run the SCF parsing test if other test calls are commented out
        # or ideally, all tests are called from run_all_core_tests.
        # For a clean run of all tests, the previous asyncio.run calls in __main__
        # for individual test functions should be removed or integrated into run_all_core_tests.
        
        # For now, to ensure this new test runs:
        # If previous tests were also in an async def and called by asyncio.run(previous_main_async_runner),
        # this new asyncio.run will effectively replace it if not structured carefully.
        # The best approach is one asyncio.run(main_test_suite()) in the entire file.
        
        # Let's assume we are refactoring __main__ to call a comprehensive test runner
        # For this step, we'll just ensure the new test can be run.
        # If you uncomment the other calls in run_all_core_tests, ensure those functions are defined async.
        # The previous __main__ blocks for other tests might need to be converted to async functions.
        asyncio.run(run_all_core_tests()) # This will run the SCF parsing test via run_all_core_tests
import re # Should be already imported

def parse_abacus_opt_output(
    output_content: str, 
    initial_atoms_dict: Optional[Dict[str, Any]] = None, # To reconstruct final Atoms object
    out_stru_file_content: Optional[str] = None # Content of the final STRU file if out_stru was enabled
) -> Dict[str, Any]:
    """
    Parses the output content from an ABACUS geometry optimization (relax/cell-relax)
    to extract key information, including the final structure.

    Args:
        output_content: String content of the main ABACUS output log.
        initial_atoms_dict: Optional. The dictionary representation of the initial structure.
                            Used as a template for the final structure if parsing coordinates from log.
        out_stru_file_content: Optional. String content of the final STRU file output by ABACUS
                               (e.g., from "OUT.ABACUS/STRU_ION_D" or similar if out_stru=1).
                               This is the preferred way to get the final structure.
    Returns:
        A dictionary containing parsed data:
            - "converged" (bool): Whether the optimization converged.
            - "final_total_energy_ry" (float | None): Final total energy in Rydberg.
            - "final_total_energy_ev" (float | None): Final total energy in eV.
            - "final_fermi_energy_ry" (float | None): Final Fermi energy in Rydberg.
            - "final_fermi_energy_ev" (float | None): Final Fermi energy in eV.
            - "optimization_steps" (int | None): Number of optimization steps.
            - "final_structure_dict" (Dict | None): Dictionary representation of the final structure.
            - "max_force" (float | None): Maximum force component on atoms at the end.
            - "total_force" (float | None): Total force (norm of all forces) on atoms at the end.
            - "stress_tensor_kbar" (List[List[float]] | None): Final stress tensor in kBar.
            - "warnings" (List[str]): List of any parsing warnings.
            - "errors" (List[str]): List of parsing errors or messages indicating missing data.
    """
    results: Dict[str, Any] = {
        "converged": False,
        "final_total_energy_ry": None,
        "final_total_energy_ev": None,
        "final_fermi_energy_ry": None,
        "final_fermi_energy_ev": None,
        "optimization_steps": None,
        "final_structure_dict": None,
        "max_force": None,
        "total_force": None,
        "stress_tensor_kbar": None,
        "warnings": [],
        "errors": []
    }
    RY_TO_EV = 13.605693122994

    # --- Attempt to parse final structure first (if out_stru_file_content is provided) ---
    if out_stru_file_content and initial_atoms_dict:
        try:
            # We need a robust way to parse a STRU file back into an Atoms object or dict.
            # This is non-trivial as STRU format can vary slightly.
            # For now, let's assume a simplified parsing or that a dedicated STRU parser exists.
            # Placeholder: This part needs a proper STRU parser.
            # For a temporary solution, if the out_stru_file_content is simple enough,
            # we might try to extract coordinates and cell.
            # This is highly dependent on the exact format of ABACUS's output STRU.
            
            # Let's try to use generate_abacus_stru's logic in reverse (conceptually)
            # or use ASE to read it if it's a standard format ASE recognizes (e.g. if it's like a POSCAR)
            # ABACUS STRU is specific. We'd need a dedicated parser.
            # For now, we'll mark that it needs implementation.
            # If we had a function `parse_stru_to_dict(stru_content_str) -> Dict`, we'd use it here.
            # results["final_structure_dict"] = parse_stru_to_dict(out_stru_file_content)
            results["warnings"].append("Parsing final structure from out_stru_file_content is not fully implemented yet. Final structure might be missing or incomplete.")
            # As a fallback, we can try to extract coordinates from the main log if available.
        except Exception as e:
            results["warnings"].append(f"Could not parse final structure from out_stru_file_content: {e}")


    # --- Parse main log content ---
    # Optimization convergence
    opt_converged_pattern = re.compile(r"GEOMETRY OPTIMIZATION HAS CONVERGED", re.IGNORECASE)
    opt_not_converged_pattern = re.compile(r"GEOMETRY OPTIMIZATION HAS NOT CONVERGED", re.IGNORECASE)
    
    if opt_converged_pattern.search(output_content):
        results["converged"] = True
    elif opt_not_converged_pattern.search(output_content):
        results["converged"] = False
        results["warnings"].append("Geometry optimization did NOT converge according to the output.")
    else:
        results["warnings"].append("Geometry optimization convergence status could not be definitively determined.")

    # Optimization steps
    # Example: "RELAXATION STEP :    1" or "STEP OF RELAXATION : 50"
    opt_step_pattern = re.compile(r"STEP OF RELAXATION\s*:\s*(\d+)|RELAXATION STEP\s*:\s*(\d+)", re.IGNORECASE)
    max_opt_step = 0
    for match in opt_step_pattern.finditer(output_content):
        step = match.group(1) or match.group(2)
        if step:
            max_opt_step = max(max_opt_step, int(step))
    if max_opt_step > 0:
        results["optimization_steps"] = max_opt_step
    else:
        results["errors"].append("Number of optimization steps could not be parsed.")

    # Final energies and Fermi level (often at the end of the last SCF cycle within optimization)
    # We look for the last occurrences of energy/fermi patterns.
    # This assumes the final SCF cycle's output is representative.
    
    # Re-use SCF parsing logic for the tail of the output, or for sections marked as final.
    # A simple approach: parse the whole output, the SCF parser will pick the last values.
    # This might not be robust if intermediate SCF cycles print similar "final" looking lines.
    # A better way is to find the output block for the *last* ionic step.
    
    # For now, let's use the existing SCF parser on the whole output.
    # The `parse_abacus_scf_output` already tends to find the *last* occurrences.
    scf_like_results = parse_abacus_scf_output(output_content) # Parse the whole log
    
    results["final_total_energy_ry"] = scf_like_results["total_energy_ry"]
    results["final_total_energy_ev"] = scf_like_results["total_energy_ev"]
    results["final_fermi_energy_ry"] = scf_like_results["fermi_energy_ry"]
    results["final_fermi_energy_ev"] = scf_like_results["fermi_energy_ev"]

    if results["final_total_energy_ry"] is None and results["final_total_energy_ev"] is None:
        results["errors"].append("Final total energy could not be parsed from optimization output.")
    if results["final_fermi_energy_ry"] is None and results["final_fermi_energy_ev"] is None:
        results["errors"].append("Final Fermi energy could not be parsed from optimization output.")


    # Max and Total Force
    # Example: "TOTAL-FORCE (eV/Angstrom)  = 0.00209 Max_Force = 0.00123"
    force_pattern = re.compile(r"TOTAL-FORCE\s*\(eV/Angstrom\)\s*=\s*([-+]?\d*\.\d+|\d+)\s*Max_Force\s*=\s*([-+]?\d*\.\d+|\d+)", re.IGNORECASE)
    last_force_match = None
    for match in force_pattern.finditer(output_content):
        last_force_match = match
    if last_force_match:
        results["total_force"] = float(last_force_match.group(1))
        results["max_force"] = float(last_force_match.group(2))
    else:
        results["errors"].append("Final forces (total/max) could not be parsed.")

    # Stress Tensor (kBar)
    # Example:
    #          TOTAL STRESS (KBAR):
    #              0.00011     -0.00000      0.00000
    #             -0.00000      0.00011      0.00000
    #              0.00000      0.00000      0.00011
    stress_header_pattern = re.compile(r"TOTAL STRESS \(KBAR\):", re.IGNORECASE)
    stress_tensor: List[List[float]] = []
    stress_block_match = None
    for match in stress_header_pattern.finditer(output_content):
        stress_block_match = match # Find the last occurrence

    if stress_block_match:
        stress_block_start = stress_block_match.end()
        stress_lines_str = output_content[stress_block_start:].splitlines()
        count = 0
        for line in stress_lines_str:
            line = line.strip()
            if not line: continue # Skip empty lines
            try:
                row = [float(x) for x in line.split()]
                if len(row) == 3:
                    stress_tensor.append(row)
                    count += 1
                    if count == 3: break # Found 3 rows
                else: # If a line doesn't have 3 numbers, stop parsing this block
                    if count > 0 : results["warnings"].append("Stress tensor block seems incomplete.")
                    break 
            except ValueError: # If a line cannot be converted to float, stop
                if count > 0 : results["warnings"].append("Encountered non-numeric data in stress tensor block.")
                break 
        if len(stress_tensor) == 3:
            results["stress_tensor_kbar"] = stress_tensor
        else:
            results["errors"].append("Final stress tensor could not be fully parsed (expected 3x3 matrix).")
    else:
        results["errors"].append("Final stress tensor block not found.")


    # Attempt to parse final coordinates from log if not available from STRU file
    # This is a fallback and can be very fragile.
    if results["final_structure_dict"] is None and initial_atoms_dict:
        # Look for a block like:
        # ATOMIC_POSITIONS (ANGSTROM)
        # Si      0.00000000      0.00000000      0.00000000   1   1   1
        # Si      1.35750000      1.35750000      1.35750000   1   1   1
        # Or similar for LATTICE_VECTORS if cell is relaxed.
        # This requires knowing the number of atoms and their order from initial_atoms_dict.
        # This is complex and highly dependent on ABACUS output verbosity and format.
        # For now, we'll skip this complex log parsing for coordinates.
        results["warnings"].append("Parsing final structure coordinates directly from optimization log is not implemented. Use out_stru=1 in ABACUS for reliable final structure.")


    # If converged but some key data is missing from parsing, add a general warning
    if results["converged"] and (results["final_total_energy_ry"] is None or results["max_force"] is None):
        results["warnings"].append("Optimization reported as converged, but some key final metrics (energy/force) could not be parsed.")

    return results


if __name__ == '__main__':
    # ... (previous test blocks) ...
    import asyncio # Should be at the top if used by other tests in __main__

    async def test_parse_opt_output(): # Make async if other tests are
        print("\n--- Testing ABACUS Optimization Output Parsing ---")

        sample_opt_converged_log = """
        Some header info...
        STEP OF RELAXATION :    1
        TOTAL-FORCE (eV/Angstrom)  = 0.10000 Max_Force = 0.05000
        !FINAL_ETOTAL_IS        -10.123 Ry  (SCF at step 1)
        EFERMI                  -0.1 Ry

        STEP OF RELAXATION :    2
        TOTAL-FORCE (eV/Angstrom)  = 0.00209 Max_Force = 0.00123
        !FINAL_ETOTAL_IS        -10.56789012 Ry (Final SCF)
        EFERMI                  -0.2345 Ry
        E_FERMI: -3.190 eV
        convergence has been achieved (for this SCF)
        
        TOTAL STRESS (KBAR):
             0.10000     -0.01000      0.00100
            -0.01000      0.11000      0.00200
             0.00100      0.00200      0.12000

        GEOMETRY OPTIMIZATION HAS CONVERGED!
        Final Coordinates, etc. (not parsed by this basic parser yet from log)
        """
        parsed_opt1 = parse_abacus_opt_output(sample_opt_converged_log)
        print("\nTest 1: Converged Optimization")
        print(parsed_opt1)
        assert parsed_opt1["converged"]
        assert parsed_opt1["optimization_steps"] == 2
        assert abs(parsed_opt1["final_total_energy_ry"] - (-10.56789012)) < 1e-7
        assert abs(parsed_opt1["final_fermi_energy_ry"] - (-0.2345)) < 1e-7
        assert abs(parsed_opt1["final_fermi_energy_ev"] - (-3.190)) < 1e-7
        assert abs(parsed_opt1["total_force"] - 0.00209) < 1e-5
        assert abs(parsed_opt1["max_force"] - 0.00123) < 1e-5
        assert parsed_opt1["stress_tensor_kbar"] is not None
        assert abs(parsed_opt1["stress_tensor_kbar"][0][0] - 0.10000) < 1e-5

        sample_opt_not_converged_log = """
        STEP OF RELAXATION :   50
        !FINAL_ETOTAL_IS        -20.0 Ry
        TOTAL-FORCE (eV/Angstrom)  = 0.50000 Max_Force = 0.20000
        GEOMETRY OPTIMIZATION HAS NOT CONVERGED AFTER 50 STEPS.
        """
        parsed_opt2 = parse_abacus_opt_output(sample_opt_not_converged_log)
        print("\nTest 2: Not Converged Optimization")
        print(parsed_opt2)
        assert not parsed_opt2["converged"]
        assert "Geometry optimization did NOT converge" in parsed_opt2["warnings"][0]
        assert parsed_opt2["optimization_steps"] == 50
        assert abs(parsed_opt2["final_total_energy_ry"] - (-20.0)) < 1e-7
        assert abs(parsed_opt2["max_force"] - 0.20000) < 1e-5

        # Test with out_stru_file_content (mocked content)
        # This part of parsing is marked as "not fully implemented yet" in the function
        mock_stru_content = """
        ATOMIC_SPECIES
        Si  28.0850 Si.UPF
        LATTICE_CONSTANT
        1.0
        LATTICE_VECTORS
        5.43 0.00 0.00
        0.00 5.43 0.00
        0.00 0.00 5.43
        ATOMIC_POSITIONS
        Si
        0.01 0.01 0.01 1 1 1 
        Si
        1.36 1.36 1.36 1 1 1
        """
        initial_si_dict = {"symbols": ["Si","Si"], "positions": [[0,0,0],[1,1,1]], "cell":[[1,0,0],[0,1,0],[0,0,1]], "pbc": [True,True,True]}
        parsed_opt3 = parse_abacus_opt_output(sample_opt_converged_log, 
                                            initial_atoms_dict=initial_si_dict, 
                                            out_stru_file_content=mock_stru_content)
        print("\nTest 3: Converged Opt with (mocked) out_stru content")
        # print(parsed_opt3)
        assert "Parsing final structure from out_stru_file_content is not fully implemented yet" in parsed_opt3["warnings"]
        # We expect other fields to be parsed correctly from the main log
        assert parsed_opt3["converged"]
        assert abs(parsed_opt3["final_total_energy_ry"] - (-10.56789012)) < 1e-7


        print("\n--- ABACUS Optimization Output Parsing Tests Completed ---")

    # Add to the main test runner
    async def run_all_core_tests():
        # This function should ideally call all async test functions defined in this file.
        # For example:
        # await test_input_generation_async_wrapper() # If input tests were wrapped
        # await test_stru_generation_async_wrapper()  # If stru tests were wrapped
        # await run_kpt_tests()                       # If kpt tests are in an async function
        # await test_execute_abacus()                 # If execute tests are in an async function
        # await test_parse_scf_output()               # If scf parse tests are in an async function
        await test_parse_opt_output()

    if __name__ == '__main__':
        # This ensures that if the script is run directly, all defined tests (or at least this one) run.
        # It's crucial that previous asyncio.run() calls in the __main__ block are removed or
        # integrated into a single main async test suite function like run_all_core_tests.
        asyncio.run(run_all_core_tests())
import re # Should be already imported

def parse_abacus_opt_output(
    output_content: str, 
    initial_atoms_dict: Optional[Dict[str, Any]] = None, # To reconstruct final Atoms object
    out_stru_file_content: Optional[str] = None, # Content of the final STRU file if out_stru was enabled
    calculation_type: str = "relax" # "relax" or "cell-relax"
) -> Dict[str, Any]:
    """
    Parses the output content from an ABACUS geometry optimization (relax/cell-relax)
    to extract key information, including the final structure.

    Args:
        output_content: String content of the main ABACUS output log.
        initial_atoms_dict: Optional. The dictionary representation of the initial structure.
                            Used as a template for the final structure if parsing coordinates from log.
        out_stru_file_content: Optional. String content of the final STRU file output by ABACUS
                               (e.g., from "OUT.ABACUS/STRU_ION_D" or similar if out_stru=1).
                               This is the preferred way to get the final structure.
        calculation_type: Type of optimization, "relax" or "cell-relax". Affects what to look for.

    Returns:
        A dictionary containing parsed data.
    """
    results: Dict[str, Any] = {
        "converged": False,
        "final_total_energy_ry": None,
        "final_total_energy_ev": None,
        "final_fermi_energy_ry": None,
        "final_fermi_energy_ev": None,
        "optimization_steps": None,
        "final_structure_dict": None, # This will store the dict representation of the final Atoms
        "max_force": None,
        "total_force": None,
        "stress_tensor_kbar": None, # Only relevant for cell-relax
        "warnings": [],
        "errors": []
    }
    RY_TO_EV = 13.605693122994

    # --- Attempt to parse final structure from out_stru_file_content (preferred) ---
    if out_stru_file_content:
        try:
            # This is a placeholder. A robust STRU parser is needed.
            # For now, we'll assume if out_stru_file_content is present,
            # it represents the final structure, but we can't easily convert it back to a dict
            # without a proper parser or by re-using generate_abacus_stru in a complex way.
            # A simple approach for now: if this content exists, we assume ABACUS produced it.
            # The actual conversion to a usable dict for the 'final_structure_dict'
            # would require parsing the STRU format.
            # For now, we can store the raw content if needed, or try a very basic parse.
            
            # Let's try a very basic extraction if it looks like our generated STRU format
            # This is highly fragile and should be replaced with a proper STRU parser.
            temp_symbols = []
            temp_positions = []
            temp_cell = []
            lines = out_stru_file_content.splitlines()
            reading_species = False
            reading_vectors = False
            reading_positions = False
            
            # This is a simplified parser, assuming Cartesian_Angstrom for output STRU
            # and that the output STRU format is somewhat predictable.
            current_species_symbols_ordered = []

            for line in lines:
                if "ATOMIC_SPECIES" in line: reading_species = True; continue
                if "NUMERICAL_ORBITAL" in line: reading_species = False; continue
                if "LATTICE_CONSTANT" in line: reading_species = False; continue
                if "LATTICE_VECTORS" in line: reading_vectors = True; reading_species = False; continue
                if "ATOMIC_POSITIONS" in line: reading_positions = True; reading_vectors = False; continue

                if reading_species and line.strip():
                    parts = line.split()
                    if len(parts) >= 1:
                        current_species_symbols_ordered.append(parts[0])
                elif reading_vectors and line.strip():
                    try:
                        temp_cell.append([float(x) for x in line.split()[:3]])
                    except ValueError: pass # ignore lines that are not 3 floats
                elif reading_positions and line.strip():
                    # ABACUS STRU output for positions: Symbol on one line, coords on next
                    if not line.replace(".","").replace("-","").replace("e","").replace("E","").replace("+","").isspace() and \
                       not any(c.isalpha() for c in line.split()[0]): # Check if it's a coordinate line
                        try:
                            coords = [float(x) for x in line.split()[:3]]
                            temp_positions.append(coords)
                        except ValueError: pass
                    elif line.strip() in ase_chemical_symbols: # It's a symbol line
                        temp_symbols.append(line.strip())


            if len(temp_cell) == 3 and len(temp_symbols) > 0 and len(temp_symbols) == len(temp_positions):
                # Reconstruct a dictionary similar to what create_structure produces
                # This assumes the output STRU used Cartesian_Angstrom and LATTICE_CONSTANT=1.0
                # and pbc is [True, True, True] for typical bulk relaxations.
                # This is a BIG assumption and needs a proper STRU parser.
                final_struc_dict_from_file = {
                    "symbols": temp_symbols,
                    "positions": temp_positions,
                    "cell": temp_cell,
                    "pbc": [True, True, True], # Assume PBC for optimized bulk
                    "info": {"source": "Parsed from ABACUS output STRU file"}
                }
                # Validate this reconstructed dict
                # validation_check = validate_ase_structure_dict(final_struc_dict_from_file) # validate_ase_structure_dict is in structure_management
                # if validation_check["success"]:
                results["final_structure_dict"] = final_struc_dict_from_file
                # else:
                #     results["warnings"].append(f"Reconstructed final structure from STRU output failed validation: {validation_check['messages']}")
            else:
                 results["warnings"].append("Could not reliably parse final structure from out_stru_file_content. Data was incomplete or format unexpected.")

        except Exception as e:
            results["warnings"].append(f"Error parsing final structure from out_stru_file_content: {str(e)}")


    # --- Parse main log content ---
    opt_converged_pattern = re.compile(r"GEOMETRY OPTIMIZATION HAS CONVERGED", re.IGNORECASE)
    opt_not_converged_pattern = re.compile(r"GEOMETRY OPTIMIZATION HAS NOT CONVERGED", re.IGNORECASE)
    
    if opt_converged_pattern.search(output_content):
        results["converged"] = True
    elif opt_not_converged_pattern.search(output_content):
        results["converged"] = False
        results["warnings"].append("Geometry optimization did NOT converge according to the output.")
    else:
        # If neither is found, but we have many opt steps, it likely didn't converge.
        # However, some short runs might finish without these exact lines if max steps reached.
        results["warnings"].append("Geometry optimization convergence status could not be definitively determined from explicit messages.")

    opt_step_pattern = re.compile(r"STEP OF RELAXATION\s*:\s*(\d+)|RELAXATION STEP\s*:\s*(\d+)", re.IGNORECASE)
    max_opt_step = 0
    for match in opt_step_pattern.finditer(output_content):
        step = match.group(1) or match.group(2)
        if step:
            max_opt_step = max(max_opt_step, int(step))
    if max_opt_step > 0:
        results["optimization_steps"] = max_opt_step
    # else:
        # results["errors"].append("Number of optimization steps could not be parsed.") # Might be 0 steps if already converged

    # Use the SCF parser for final energies, assuming it picks the last relevant values
    scf_like_results = parse_abacus_scf_output(output_content)
    results["final_total_energy_ry"] = scf_like_results["total_energy_ry"]
    results["final_total_energy_ev"] = scf_like_results["total_energy_ev"]
    results["final_fermi_energy_ry"] = scf_like_results["fermi_energy_ry"]
    results["final_fermi_energy_ev"] = scf_like_results["fermi_energy_ev"]

    if results["final_total_energy_ry"] is None and results["final_total_energy_ev"] is None:
        results["errors"].append("Final total energy could not be parsed from optimization output.")
    # Fermi energy might not always be present or relevant for just opt.
    # if results["final_fermi_energy_ry"] is None and results["final_fermi_energy_ev"] is None:
    #     results["warnings"].append("Final Fermi energy could not be parsed from optimization output.")


    force_pattern = re.compile(r"TOTAL-FORCE\s*\(eV/Angstrom\)\s*=\s*([-+]?\d*\.\d+(?:[eE][-+]?\d+)?)\s*Max_Force\s*=\s*([-+]?\d*\.\d+(?:[eE][-+]?\d+)?)", re.IGNORECASE)
    last_force_match = None
    for match in force_pattern.finditer(output_content):
        last_force_match = match
    if last_force_match:
        try:
            results["total_force"] = float(last_force_match.group(1))
            results["max_force"] = float(last_force_match.group(2))
        except ValueError:
            results["errors"].append("Could not convert parsed force values to float.")
    # else:
        # results["errors"].append("Final forces (total/max) could not be parsed.") # Not an error if not printed or not converged

    if calculation_type.lower() == "cell-relax":
        stress_header_pattern = re.compile(r"TOTAL STRESS \(KBAR\):", re.IGNORECASE)
        stress_tensor: List[List[float]] = []
        stress_block_match = None
        for match in stress_header_pattern.finditer(output_content):
            stress_block_match = match

        if stress_block_match:
            stress_block_start = stress_block_match.end()
            stress_lines_str = output_content[stress_block_start:].splitlines()
            count = 0
            for line in stress_lines_str:
                line = line.strip()
                if not line: continue
                try:
                    row = [float(x) for x in line.split()[:3]] # Take first 3 numbers
                    if len(row) == 3:
                        stress_tensor.append(row)
                        count += 1
                        if count == 3: break
                    else:
                        if count > 0: results["warnings"].append("Stress tensor block seems incomplete after starting.")
                        break 
                except ValueError:
                    if count > 0: results["warnings"].append("Encountered non-numeric data in stress tensor block after starting.")
                    break 
            if len(stress_tensor) == 3:
                results["stress_tensor_kbar"] = stress_tensor
            # else:
            #     results["errors"].append("Final stress tensor could not be fully parsed (expected 3x3 matrix).")
        # else:
        #     results["errors"].append("Final stress tensor block not found for cell-relax.")


    # Fallback: If final structure not from STRU file, and if initial_atoms_dict is given,
    # we could try to parse coordinates from a "FINAL COORDINATES" block in the log.
    # This is very fragile and highly dependent on ABACUS version and verbosity.
    # Example:
    # FINAL COORDINATES (ANGSTROMS)
    # atom    x              y              z
    # Si      0.00000000     0.00000000     0.00000000
    # Si      1.35700000     1.35700000     1.35700000
    if results["final_structure_dict"] is None and initial_atoms_dict:
        final_coords_block_pattern = re.compile(r"FINAL COORDINATES \((ANGSTROMS?|AU|BOHR)\)", re.IGNORECASE)
        coord_match = final_coords_block_pattern.search(output_content)
        if coord_match:
            unit_from_log = coord_match.group(1).lower()
            block_start = coord_match.end()
            # Skip header lines like "atom x y z"
            coord_lines_str = output_content[block_start:].splitlines()
            parsed_positions = []
            num_atoms = len(initial_atoms_dict["symbols"])
            
            header_skipped = False
            for line_idx, line_str in enumerate(coord_lines_str):
                line_str = line_str.strip()
                if not line_str: continue
                if not header_skipped and any(hdr in line_str.lower() for hdr in ["atom", "x", "y", "z", "element"]):
                    header_skipped = True
                    continue
                if not header_skipped and line_idx > 2: # Give up if header not found quickly
                    break

                parts = line_str.split()
                if len(parts) >= 4 and parts[0] in initial_atoms_dict["symbols"]: # Check symbol and enough parts
                    try:
                        pos = [float(parts[1]), float(parts[2]), float(parts[3])]
                        parsed_positions.append(pos)
                        if len(parsed_positions) == num_atoms:
                            break
                    except ValueError:
                        results["warnings"].append(f"Could not parse coordinate line: {line_str}")
                        parsed_positions = [] # Invalidate if error
                        break
            
            if len(parsed_positions) == num_atoms:
                final_struc_dict_from_log = initial_atoms_dict.copy() # Start with initial
                final_struc_dict_from_log["positions"] = parsed_positions
                final_struc_dict_from_log["info"] = {"source": f"Parsed from log, unit: {unit_from_log}"}
                
                # Unit conversion if necessary (assuming initial_atoms_dict is Angstrom)
                if unit_from_log in ["au", "bohr"]:
                    final_struc_dict_from_log["positions"] = (np.array(parsed_positions) * BOHR_TO_ANGSTROM).tolist()
                
                # If cell-relax, try to parse final cell vectors too
                if calculation_type.lower() == "cell-relax":
                    final_cell_pattern = re.compile(r"FINAL LATTICE VECTORS \(ANGSTROMS?\):\s*([\s\S]*?)(?:\n\n|\Z)", re.IGNORECASE)
                    cell_match = final_cell_pattern.search(output_content)
                    if cell_match:
                        cell_block = cell_match.group(1).strip()
                        cell_lines = cell_block.splitlines()
                        parsed_cell = []
                        for c_line in cell_lines:
                            try:
                                parsed_cell.append([float(x) for x in c_line.split()[:3]])
                            except ValueError:
                                parsed_cell = [] # Invalidate
                                break
                        if len(parsed_cell) == 3:
                            final_struc_dict_from_log["cell"] = parsed_cell
                        else:
                            results["warnings"].append("Could not parse final cell vectors from log for cell-relax.")
                
                results["final_structure_dict"] = final_struc_dict_from_log
            else:
                results["warnings"].append("Could not parse final coordinates from log or atom count mismatch.")
        # else:
            # results["warnings"].append("Final coordinates block not found in log.")


    if not results["converged"] and results["optimization_steps"] is not None:
         # If not explicitly converged, but steps were taken, it's likely a failure or max steps reached
         if "Geometry optimization did NOT converge" not in " ".join(results["warnings"]): # Avoid duplicate
            results["warnings"].append("Optimization likely did not converge (max steps reached or other issue).")

    return results


if __name__ == '__main__':
    # ... (previous test blocks) ...
    import asyncio # Should be at the top

    async def test_parse_opt_output():
        print("\n--- Testing ABACUS Optimization Output Parsing ---")

        sample_opt_converged_log = """
        Begin OPTIMIZATION Calculation
        STEP OF RELAXATION :    1
        TOTAL-FORCE (eV/Angstrom)  = 0.10000 Max_Force = 0.05000
        !FINAL_ETOTAL_IS        -10.123 Ry
        EFERMI                  -0.1 Ry

        STEP OF RELAXATION :    2
        TOTAL-FORCE (eV/Angstrom)  = 0.00209 Max_Force = 0.00123
        !FINAL_ETOTAL_IS        -10.56789012 Ry
        EFERMI                  -0.2345 Ry
        E_FERMI: -3.190 eV
        convergence has been achieved (for this SCF)
        
        TOTAL STRESS (KBAR):
             0.10000     -0.01000      0.00100
            -0.01000      0.11000      0.00200
             0.00100      0.00200      0.12000

        GEOMETRY OPTIMIZATION HAS CONVERGED!
        FINAL COORDINATES (ANGSTROMS)
        ATOM    X              Y              Z
        Si      0.00000000     0.00000000     0.00000000
        Si      1.35700000     1.35700000     1.35700000
        FINAL LATTICE VECTORS (ANGSTROMS):
          5.43000000     0.00000000     0.00000000
          0.00000000     5.43000000     0.00000000
          0.00000000     0.00000000     5.43000000
        """
        initial_si_atoms_dict = {
            "symbols": ["Si", "Si"], 
            "positions": [[0,0,0],[1,1,1]], # Dummy initial
            "cell": [[5,0,0],[0,5,0],[0,0,5]], # Dummy initial
            "pbc": [True,True,True]
        }
        parsed_opt1 = parse_abacus_opt_output(sample_opt_converged_log, initial_atoms_dict=initial_si_atoms_dict, calculation_type="cell-relax")
        print("\nTest 1: Converged Cell-Relaxation")
        # print(parsed_opt1)
        assert parsed_opt1["converged"]
        assert parsed_opt1["optimization_steps"] == 2
        assert abs(parsed_opt1["final_total_energy_ry"] - (-10.56789012)) < 1e-7
        assert abs(parsed_opt1["max_force"] - 0.00123) < 1e-5
        assert parsed_opt1["stress_tensor_kbar"] is not None
        assert abs(parsed_opt1["stress_tensor_kbar"][0][0] - 0.10000) < 1e-5
        assert parsed_opt1["final_structure_dict"] is not None
        assert parsed_opt1["final_structure_dict"]["symbols"] == ["Si", "Si"]
        assert abs(parsed_opt1["final_structure_dict"]["positions"][1][0] - 1.3570) < 1e-5
        assert abs(parsed_opt1["final_structure_dict"]["cell"][0][0] - 5.43) < 1e-5


        sample_opt_not_converged_log = """
        STEP OF RELAXATION :   50
        !FINAL_ETOTAL_IS        -20.0 Ry
        TOTAL-FORCE (eV/Angstrom)  = 0.50000 Max_Force = 0.20000
        GEOMETRY OPTIMIZATION HAS NOT CONVERGED AFTER 50 STEPS.
        """
        parsed_opt2 = parse_abacus_opt_output(sample_opt_not_converged_log, calculation_type="relax")
        print("\nTest 2: Not Converged Optimization")
        # print(parsed_opt2)
        assert not parsed_opt2["converged"]
        assert "Geometry optimization did NOT converge" in parsed_opt2["warnings"][0]
        assert parsed_opt2["optimization_steps"] == 50
        assert abs(parsed_opt2["final_total_energy_ry"] - (-20.0)) < 1e-7
        assert abs(parsed_opt2["max_force"] - 0.20000) < 1e-5

        # Test with out_stru_file_content (mocked content)
        # This part of parsing is marked as "not fully implemented yet" in the function
        mock_stru_content = """
        ATOMIC_SPECIES
        Si  28.0850 Si.UPF
        LATTICE_CONSTANT
        1.0
        LATTICE_VECTORS
        5.43 0.00 0.00
        0.00 5.43 0.00
        0.00 0.00 5.43
        ATOMIC_POSITIONS
        Si
        0.01 0.01 0.01 1 1 1 
        Si
        1.36 1.36 1.36 1 1 1
        """
        initial_si_dict_2 = {"symbols": ["Si","Si"], "positions": [[0,0,0],[1,1,1]], "cell":[[1,0,0],[0,1,0],[0,0,1]], "pbc": [True,True,True]}
        parsed_opt3 = parse_abacus_opt_output(sample_opt_converged_log, 
                                            initial_atoms_dict=initial_si_dict_2, 
                                            out_stru_file_content=mock_stru_content)
        print("\nTest 3: Converged Opt with (mocked) out_stru content")
        # print(parsed_opt3)
        assert "Could not reliably parse final structure from out_stru_file_content" in parsed_opt3["warnings"] or \
               "Parsing final structure from out_stru_file_content is not fully implemented yet" in parsed_opt3["warnings"]

        # We expect other fields to be parsed correctly from the main log
        assert parsed_opt3["converged"]
        assert abs(parsed_opt3["final_total_energy_ry"] - (-10.56789012)) < 1e-7


        print("\n--- ABACUS Optimization Output Parsing Tests Completed ---")

    # Add to the main test runner
    async def run_all_core_tests():
        # This function should ideally call all async test functions defined in this file.
        # For example:
        # await test_input_generation_async_wrapper() # If input tests were wrapped
        # await test_stru_generation_async_wrapper()  # If stru tests were wrapped
        # await run_kpt_tests()                       # If kpt tests are in an async function
        # await test_execute_abacus()                 # If execute tests are in an async function
        # await test_parse_scf_output()               # If scf parse tests are in an async function
        await test_parse_opt_output()

    if __name__ == '__main__':
        # This ensures that if the script is run directly, all defined tests (or at least this one) run.
        # It's crucial that previous asyncio.run() calls in the __main__ block are removed or
        # integrated into a single main async test suite function like run_all_core_tests.
        asyncio.run(run_all_core_tests())
import re # Should be already imported

def parse_abacus_md_output(output_content: str, md_nstep: Optional[int] = None) -> Dict[str, Any]:
    """
    Parses the output content from an ABACUS Molecular Dynamics (MD) simulation.

    Args:
        output_content: String content of the main ABACUS MD output log.
        md_nstep: The expected number of MD steps, used to check for completion.

    Returns:
        A dictionary containing parsed data:
            - "completed_all_steps" (bool): True if the log indicates all md_nstep were performed.
            - "final_energy_ry" (float | None): Final total energy in Rydberg, if found at the end.
            - "final_energy_ev" (float | None): Final total energy in eV, if found at the end.
            - "average_temperature_k" (float | None): Average temperature if reported.
            - "average_pressure_kbar" (float | None): Average pressure if reported.
            - "total_md_steps_performed" (int | None): Number of MD steps actually performed.
            - "warnings" (List[str]): List of any parsing warnings.
            - "errors" (List[str]): List of parsing errors or messages indicating issues.
    """
    results: Dict[str, Any] = {
        "completed_all_steps": False,
        "final_energy_ry": None,
        "final_energy_ev": None,
        "average_temperature_k": None,
        "average_pressure_kbar": None,
        "total_md_steps_performed": None,
        "warnings": [],
        "errors": []
    }
    RY_TO_EV = 13.605693122994

    # Regex for MD step completion
    # Example: "STEP:      1000  ETOTAL:   -300.123 Ry  TEMP:  300.0 K  PRESSURE: 0.1 kBar"
    # Example: "MD STEP   1000   TIME(PS) ... ETOTAL(eV) ... TEMP(K) ... PRESSURE(KBAR)"
    md_step_line_pattern = re.compile(
        r"^\s*(?:MD STEP|STEP:)\s*(\d+).*?ETOTAL(?:_IS)?\s*:\s*([-+]?\d*\.\d+(?:[eE][-+]?\d+)?)\s*(?:Ry|eV)?.*?TEMP(?:ERATURE)?\s*:\s*([-+]?\d*\.\d+(?:[eE][-+]?\d+)?)\s*K?(?:.*?PRESSURE\s*:\s*([-+]?\d*\.\d+(?:[eE][-+]?\d+)?)\s*K?BAR)?",
        re.IGNORECASE | re.MULTILINE
    )
    
    # Regex for final summary if available
    # Example: " JOB DONE." or "TOTAL TIME:"
    job_done_pattern = re.compile(r"JOB DONE|TOTAL TIME:", re.IGNORECASE)

    max_step_performed = 0
    last_energy_ry: Optional[float] = None
    last_energy_ev: Optional[float] = None
    temperatures: List[float] = []
    pressures: List[float] = []

    for match in md_step_line_pattern.finditer(output_content):
        step = int(match.group(1))
        max_step_performed = max(max_step_performed, step)
        
        try:
            energy_val_str = match.group(2)
            # Determine unit from context if not in regex (tricky, assume Ry if not specified for ETOTAL:)
            # The regex tries to capture Ry/eV if present with ETOTAL(eV)
            # If it's from "ETOTAL:", it's usually Ry.
            # This part is simplified; a more robust parser would look for explicit units near energy.
            
            # A common ABACUS MD output line is like:
            # STEP:        1  ETOTAL:     -15.2345 Ry  TEMP:  299.8 K  PRESSURE:   0.01 kBar
            # If "ETOTAL(eV)" is used, the unit is clear.
            # If just "ETOTAL:", it's typically Ry.
            
            # Simplification: if "ev" in match.group(0).lower() and "etotal" in match.group(0).lower(): # Heuristic
            # A slightly better heuristic: check if "eV" is explicitly next to the energy value or in the column header context
            energy_part_for_unit_check = match.group(0)[match.start(2):].lower() # Part of string from energy value onwards

            if "ev" in energy_part_for_unit_check.split()[0:2]: # Check if "eV" is very close to the number
                last_energy_ev = float(energy_val_str)
                last_energy_ry = last_energy_ev / RY_TO_EV
            else: # Assume Ry by default for "ETOTAL:" lines if "eV" is not immediately obvious
                last_energy_ry = float(energy_val_str)
                last_energy_ev = last_energy_ry * RY_TO_EV

            temperatures.append(float(match.group(3)))
            if match.group(4): # Pressure might be optional
                pressures.append(float(match.group(4)))
        except (ValueError, TypeError, IndexError) as e:
            results["warnings"].append(f"Could not parse all data from MD step line: {match.group(0)} -> {e}")

    if max_step_performed > 0:
        results["total_md_steps_performed"] = max_step_performed
        results["final_energy_ry"] = last_energy_ry
        results["final_energy_ev"] = last_energy_ev
        if temperatures:
            results["average_temperature_k"] = sum(temperatures) / len(temperatures)
        if pressures:
            results["average_pressure_kbar"] = sum(pressures) / len(pressures)
    else:
        results["errors"].append("No MD step information found in the output.")


    if md_nstep is not None:
        if results["total_md_steps_performed"] is not None and results["total_md_steps_performed"] >= md_nstep:
            results["completed_all_steps"] = True
        else:
            results["completed_all_steps"] = False
            results["warnings"].append(f"MD simulation performed {results['total_md_steps_performed']} steps, but {md_nstep} were expected.")
    elif job_done_pattern.search(output_content) and max_step_performed > 0:
        # If md_nstep not given, but job finished and some steps ran, assume it completed as configured.
        results["completed_all_steps"] = True
    else:
        # This warning might be too strong if md_nstep is None and job_done is not found.
        # It's hard to be certain without md_nstep.
        if md_nstep is not None: # Only add this warning if md_nstep was actually provided
            results["warnings"].append("Could not determine if all MD steps were completed (md_nstep provided but job end not clear or steps mismatch).")
        elif max_step_performed == 0 and not job_done_pattern.search(output_content):
             results["errors"].append("MD run did not seem to start or complete (no steps, no job done message).")


        
    # Check for common error messages in MD
    error_patterns = [
        re.compile(r"Too many errors", re.IGNORECASE),
        re.compile(r"Problem with SCF convergence during MD", re.IGNORECASE),
        re.compile(r"ERROR IN ABACUS", re.IGNORECASE)
    ]
    for pattern in error_patterns:
        if pattern.search(output_content):
            results["errors"].append(f"Potential MD error indicated by: '{pattern.pattern}'")
            results["completed_all_steps"] = False # Override if error found

    if not results["errors"] and not results["completed_all_steps"] and md_nstep is not None and \
       (results["total_md_steps_performed"] is None or results["total_md_steps_performed"] < md_nstep) :
        results["errors"].append("MD simulation did not complete all expected steps and no specific error message found.")


    return results


if __name__ == '__main__':
    # ... (previous test blocks) ...
    import asyncio # Should be at the top

    async def test_parse_md_output():
        print("\n--- Testing ABACUS MD Output Parsing ---")

        sample_md_log_completed = """
        Starting MD simulation...
        MD_NSTEP = 100
        STEP:        1  ETOTAL:     -15.2345 Ry  TEMP:  299.8 K  PRESSURE:   0.01 kBar
        STEP:        2  ETOTAL:     -15.2350 Ry  TEMP:  301.2 K  PRESSURE:  -0.02 kBar
        ...
        STEP:      100  ETOTAL:     -15.2360 Ry  TEMP:  300.5 K  PRESSURE:   0.00 kBar
        JOB DONE.
        """
        parsed_md1 = parse_abacus_md_output(sample_md_log_completed, md_nstep=100)
        print("\nTest 1: Completed MD")
        # print(parsed_md1)
        assert parsed_md1["completed_all_steps"]
        assert parsed_md1["total_md_steps_performed"] == 100
        assert abs(parsed_md1["final_energy_ry"] - (-15.2360)) < 1e-4
        assert abs(parsed_md1["average_temperature_k"] - (299.8 + 301.2 + 300.5) / 3) < 1 # Rough avg
        assert abs(parsed_md1["average_pressure_kbar"] - (0.01 - 0.02 + 0.00) / 3) < 0.01

        sample_md_log_incomplete = """
        Starting MD simulation...
        MD_NSTEP = 100
        STEP:        1  ETOTAL:     -10.0 Ry  TEMP:  300 K
        STEP:        2  ETOTAL:     -10.1 Ry  TEMP:  302 K
        STEP:       50  ETOTAL:     -10.5 Ry  TEMP:  305 K
        (Program terminated early, no JOB DONE)
        """
        parsed_md2 = parse_abacus_md_output(sample_md_log_incomplete, md_nstep=100)
        print("\nTest 2: Incomplete MD")
        # print(parsed_md2)
        assert not parsed_md2["completed_all_steps"]
        assert parsed_md2["total_md_steps_performed"] == 50
        assert "MD simulation performed 50 steps, but 100 were expected" in parsed_md2["warnings"]
        assert "MD simulation did not complete all expected steps" in parsed_md2["errors"]


        sample_md_log_error = """
        Starting MD simulation...
        MD_NSTEP = 100
        STEP:        1  ETOTAL:     -20.0 Ry  TEMP:  300 K
        ERROR IN ABACUS: SCF did not converge in MD step 2
        """
        parsed_md3 = parse_abacus_md_output(sample_md_log_error, md_nstep=100)
        print("\nTest 3: MD with error")
        # print(parsed_md3)
        assert not parsed_md3["completed_all_steps"]
        assert "Potential MD error indicated by: 'ERROR IN ABACUS'" in parsed_md3["errors"]
        assert parsed_md3["total_md_steps_performed"] == 1 

        sample_md_log_ev_energy = """
        MD STEP      1   TIME(PS)      0.00200   ETOTAL(eV)   -270.00   TEMP(K)    300.00
        MD STEP      2   TIME(PS)      0.00400   ETOTAL(eV)   -270.05   TEMP(K)    301.00
        JOB DONE.
        """
        parsed_md4 = parse_abacus_md_output(sample_md_log_ev_energy, md_nstep=2)
        print("\nTest 4: MD with ETOTAL(eV)")
        # print(parsed_md4)
        assert parsed_md4["completed_all_steps"]
        assert parsed_md4["total_md_steps_performed"] == 2
        assert abs(parsed_md4["final_energy_ev"] - (-270.05)) < 1e-2
        assert abs(parsed_md4["final_energy_ry"] - (-270.05 / 13.605693122994)) < 1e-3


        print("\n--- ABACUS MD Output Parsing Tests Completed ---")

    # Add to the main test runner
    async def run_all_core_tests():
        # This function should ideally call all async test functions defined in this file.
        # For example:
        # await test_input_generation_async_wrapper() 
        # await test_stru_generation_async_wrapper()  
        # await run_kpt_tests() 
        # await test_execute_abacus()
        # await test_parse_scf_output() 
        # await test_parse_opt_output()
        await test_parse_md_output()

    if __name__ == '__main__':
        asyncio.run(run_all_core_tests())
import re # Already imported
import os # Already imported
import numpy as np # Already imported

def parse_abacus_band_output(
    nscf_working_directory: str,
    out_band_prefix: str = "BANDS", # Default prefix for band files from ABACUS
    num_kpts_expected: Optional[int] = None, # Optional: from KPT file for validation
    num_bands_expected: Optional[int] = None # Optional: from INPUT (nbands) for validation
) -> Dict[str, Any]:
    """
    Parses ABACUS band structure output files (e.g., BANDS_1.dat).

    Args:
        nscf_working_directory: The directory where the NSCF calculation was run
                                and where band output files are located.
        out_band_prefix: The prefix for the band data files (default "BANDS").
                         ABACUS might output BANDS_1.dat (spin-up/non-spin-polarized)
                         and BANDS_2.dat (spin-down).
        num_kpts_expected: Optional. Expected number of k-points from the KPT file.
        num_bands_expected: Optional. Expected number of bands from the INPUT file.

    Returns:
        A dictionary containing parsed band data:
            - "parsing_successful" (bool): True if parsing was successful.
            - "k_points_coordinates": List of [kx, ky, kz] for each k-point in the path.
            - "eigenvalues_ry": List of lists (or dict of lists for spin-polarized) 
                                where each inner list contains eigenvalues (in Ry)
                                for a k-point. Structure: [kpt_index][band_index].
            - "eigenvalues_ev": List of lists (or dict of lists), converted to eV.
            - "num_kpoints_found" (int): Number of k-points found in the band file.
            - "num_bands_found" (int): Number of bands found per k-point.
            - "spin_channels" (int): Number of spin channels found (1 or 2).
            - "warnings" (List[str]): List of parsing warnings.
            - "errors" (List[str]): List of parsing errors.
    """
    results: Dict[str, Any] = {
        "parsing_successful": False,
        "k_points_coordinates": [], 
        "eigenvalues_ry": {}, # Will store as {"spin1": [...], "spin2": [...]}
        "eigenvalues_ev": {},
        "num_kpoints_found": 0,
        "num_bands_found": 0,
        "spin_channels": 0,
        "warnings": [],
        "errors": []
    }
    RY_TO_EV = 13.605693122994

    # Determine actual path for band files (could be in OUT.suffix/ or CWD)
    # This logic might need to be more sophisticated if `suffix` is used.
    # For now, check CWD of nscf_working_directory first, then a common OUT.ABACUS subdir.
    
    base_search_paths = [nscf_working_directory]
    # A common pattern is OUT.suffix, but suffix is not passed here.
    # Let's try a generic OUT.ABACUS as a fallback if files not in CWD.
    # This should ideally be more robust, e.g. by knowing the suffix used.
    potential_out_dir = os.path.join(nscf_working_directory, "OUT.ABACUS") # A common default
    if os.path.isdir(potential_out_dir):
        base_search_paths.append(potential_out_dir)

    band_files_found_paths = []
    for i in [1, 2]: # Check for spin1 and spin2
        found_in_path = None
        for b_path in base_search_paths:
            current_try_path = os.path.join(b_path, f"{out_band_prefix}_{i}.dat")
            if os.path.exists(current_try_path):
                found_in_path = current_try_path
                break
        if found_in_path:
            band_files_found_paths.append(found_in_path)
        elif i == 1: # Primary band file (spin1 or non-spin) must exist
            results["errors"].append(f"Primary band data file (e.g., {out_band_prefix}_1.dat) not found in search paths: {base_search_paths}.")
            return results


    if not band_files_found_paths:
        results["errors"].append(f"No band data files starting with prefix '{out_band_prefix}' found.")
        return results

    spin_channel_count = 0
    for band_filepath in band_files_found_paths:
        spin_channel_count += 1
        current_spin_key = f"spin{spin_channel_count}"
        
        # Initialize lists for current spin channel
        results["eigenvalues_ry"][current_spin_key] = []
        results["eigenvalues_ev"][current_spin_key] = []
        
        kpts_for_this_spin: List[List[float]] = [] 
        eigenvalues_for_this_spin_ry: List[List[float]] = []

        try:
            with open(band_filepath, "r") as f:
                lines = f.readlines()
            
            if not lines:
                results["errors"].append(f"Band file {band_filepath} is empty.")
                continue

            header = lines[0].strip().split()
            if len(header) < 2:
                results["errors"].append(f"Invalid header in {band_filepath}: '{lines[0].strip()}'")
                continue
            
            try:
                nbands_in_file = int(header[0])
                nkpts_in_file = int(header[1])
            except ValueError:
                results["errors"].append(f"Could not parse nbands/nkpts from header in {band_filepath}: '{lines[0].strip()}'")
                continue

            if spin_channel_count == 1:
                results["num_bands_found"] = nbands_in_file
                results["num_kpoints_found"] = nkpts_in_file
                if num_bands_expected and nbands_in_file != num_bands_expected:
                    results["warnings"].append(f"Expected {num_bands_expected} bands, found {nbands_in_file} in {band_filepath}.")
                if num_kpts_expected and nkpts_in_file != num_kpts_expected:
                    results["warnings"].append(f"Expected {num_kpts_expected} k-points, found {nkpts_in_file} in {band_filepath}.")
            elif results["num_bands_found"] != nbands_in_file or results["num_kpoints_found"] != nkpts_in_file:
                results["errors"].append(f"Mismatch in bands/kpoints numbers between different spin channel files (e.g. {band_files_found_paths[0]} vs {band_filepath}).")
                continue 

            line_idx = 1
            for ikpt in range(nkpts_in_file):
                if line_idx >= len(lines):
                    results["errors"].append(f"Unexpected end of file in {band_filepath} at k-point {ikpt+1} (expected k-coords).")
                    break
                
                kpt_coord_line = lines[line_idx].strip()
                try:
                    kx, ky, kz = map(float, kpt_coord_line.split()[:3])
                    if spin_channel_count == 1: 
                        kpts_for_this_spin.append([kx, ky, kz])
                except (ValueError, IndexError):
                    results["errors"].append(f"Could not parse k-point coordinates from line: '{kpt_coord_line}' in {band_filepath}.")
                    break 
                line_idx += 1

                if line_idx >= len(lines):
                    results["errors"].append(f"Unexpected end of file in {band_filepath} at k-point {ikpt+1} (expected eigenvalues).")
                    break
                
                eigenval_line = lines[line_idx].strip()
                try:
                    current_kpt_eigenvals_ry = [float(e) for e in eigenval_line.split()]
                    if len(current_kpt_eigenvals_ry) != nbands_in_file:
                        results["warnings"].append(f"Num eigenvalues ({len(current_kpt_eigenvals_ry)}) != num_bands_found ({nbands_in_file}) for kpt {ikpt+1} in {band_filepath}.")
                        current_kpt_eigenvals_ry = current_kpt_eigenvals_ry[:nbands_in_file]
                        while len(current_kpt_eigenvals_ry) < nbands_in_file: current_kpt_eigenvals_ry.append(float('nan'))
                    eigenvalues_for_this_spin_ry.append(current_kpt_eigenvals_ry)
                except ValueError:
                    results["errors"].append(f"Could not parse eigenvalues from line: '{eigenval_line}' in {band_filepath}.")
                    break
                line_idx += 1
            
            if not results["errors"]: 
                if spin_channel_count == 1:
                    results["k_points_coordinates"] = kpts_for_this_spin
                
                results["eigenvalues_ry"][current_spin_key] = eigenvalues_for_this_spin_ry
                results["eigenvalues_ev"][current_spin_key] = [[e * RY_TO_EV for e in k_eigenvals] for k_eigenvals in eigenvalues_for_this_spin_ry]

        except Exception as e:
            results["errors"].append(f"Failed to process band file {band_filepath}: {str(e)}")

    results["spin_channels"] = spin_channel_count
    if spin_channel_count > 0 and not results["errors"]:
        results["parsing_successful"] = True
    
    # Simplify output if only one spin channel and it's named "spin1"
    if results["parsing_successful"] and spin_channel_count == 1 and "spin1" in results["eigenvalues_ry"]:
        results["eigenvalues_ry"] = results["eigenvalues_ry"]["spin1"]
        results["eigenvalues_ev"] = results["eigenvalues_ev"]["spin1"]
    elif spin_channel_count == 0 and not results["errors"]:
        results["errors"].append("No band data files could be processed successfully.")

    return results


if __name__ == '__main__':
    # ... (previous test blocks) ...
    import asyncio 
    import tempfile
    import shutil
    import os # Ensure os is imported for path operations in test

    async def test_parse_band_output():
        print("\n--- Testing ABACUS Band Output Parsing ---")
        
        test_nscf_dir = tempfile.mkdtemp(prefix="test_bands_")
        
        # Test 1: Single spin channel
        band_content_spin1 = """2  3
0.0  0.0  0.0
-5.0  1.0
0.5  0.0  0.0
-4.5  1.5
0.5  0.5  0.0
-4.0  2.0
"""
        with open(os.path.join(test_nscf_dir, "BANDS_1.dat"), "w") as f:
            f.write(band_content_spin1)

        parsed_b1 = parse_abacus_band_output(test_nscf_dir, num_kpts_expected=3, num_bands_expected=2)
        print("\nTest 1: Parsed BANDS_1.dat")
        assert parsed_b1["parsing_successful"]
        assert parsed_b1["num_kpoints_found"] == 3
        assert parsed_b1["num_bands_found"] == 2
        assert parsed_b1["spin_channels"] == 1
        assert len(parsed_b1["k_points_coordinates"]) == 3
        assert abs(parsed_b1["k_points_coordinates"][1][0] - 0.5) < 1e-9
        assert len(parsed_b1["eigenvalues_ry"]) == 3 
        assert len(parsed_b1["eigenvalues_ry"][0]) == 2 
        assert abs(parsed_b1["eigenvalues_ry"][0][0] - (-5.0)) < 1e-9
        assert abs(parsed_b1["eigenvalues_ev"][2][1] - (2.0 * 13.605693122994)) < 1e-7

        # Test 2: Two spin channels
        band_content_spin2 = """2  3
0.0  0.0  0.0
-5.1  0.9
0.5  0.0  0.0
-4.6  1.4
0.5  0.5  0.0
-4.1  1.9
"""
        with open(os.path.join(test_nscf_dir, "BANDS_2.dat"), "w") as f:
            f.write(band_content_spin2)
        
        parsed_b2 = parse_abacus_band_output(test_nscf_dir) 
        print("\nTest 2: Parsed BANDS_1.dat and BANDS_2.dat")
        assert parsed_b2["parsing_successful"]
        assert parsed_b2["spin_channels"] == 2
        assert "spin1" in parsed_b2["eigenvalues_ry"]
        assert "spin2" in parsed_b2["eigenvalues_ry"]
        assert len(parsed_b2["eigenvalues_ry"]["spin1"]) == 3
        assert abs(parsed_b2["eigenvalues_ry"]["spin2"][1][0] - (-4.6)) < 1e-9

        # Test 3: Band file not found
        empty_dir = tempfile.mkdtemp(prefix="empty_bands_")
        parsed_b3 = parse_abacus_band_output(empty_dir)
        print("\nTest 3: Band file not found")
        assert not parsed_b3["parsing_successful"]
        assert "not found" in parsed_b3["errors"][0]
        shutil.rmtree(empty_dir)
        
        shutil.rmtree(test_nscf_dir) 
        print("\n--- ABACUS Band Output Parsing Tests Completed ---")

    async def run_all_core_tests():
        # ... (calls to previous test functions)
        # await test_input_generation_async_wrapper() 
        # await test_stru_generation_async_wrapper()  
        # await run_kpt_tests() 
        # await test_execute_abacus()
        # await test_parse_scf_output() 
        # await test_parse_opt_output()
        # await test_parse_md_output()
        await test_parse_band_output()

    if __name__ == '__main__':
        asyncio.run(run_all_core_tests())
import re # Already imported
import os # Already imported
import numpy as np # Already imported
import glob # For file pattern matching

def parse_abacus_dos_output(
    nscf_working_directory: str, # Directory where DOS calculation was run
    dos_filename_pattern: str = "DOS1*.dat", # Pattern to find DOS files, e.g., "DOS1_*.dat" or specific name
    efermi_ry: Optional[float] = None # Fermi energy in Rydberg, to shift energy axis
) -> Dict[str, Any]:
    """
    Parses ABACUS Density of States (DOS) output files.
    Assumes a simple two-column format: Energy(eV) DOS(states/eV/cell or /unit cell).
    ABACUS might output DOS relative to Fermi energy or absolute.
    If efermi_ry is provided, the energy axis will be shifted to be E - E_fermi.

    Args:
        nscf_working_directory: The directory containing the DOS output file(s).
        dos_filename_pattern: A glob pattern to find the DOS data file(s).
                              ABACUS might output DOS1_*.dat, DOS2_*.dat for spin-polarized.
        efermi_ry: Optional Fermi energy in Rydberg. If provided, energy values
                   in DOS data will be shifted (E - E_fermi).

    Returns:
        A dictionary containing parsed DOS data:
            - "parsing_successful" (bool): True if parsing was successful.
            - "energies_ev": List of energy values (eV), possibly shifted relative to E_fermi.
            - "dos_values": Dictionary {"spin1": [...], "spin2": [...]} or List for non-spin,
                            containing DOS values.
            - "efermi_ry_used_for_shift" (float | None): Fermi energy used for shifting.
            - "spin_channels" (int): Number of spin channels found (1 or 2).
            - "warnings" (List[str]): List of parsing warnings.
            - "errors" (List[str]): List of parsing errors.
    """
    results: Dict[str, Any] = {
        "parsing_successful": False,
        "energies_ev": [], 
        "dos_values": {},  
        "efermi_ry_used_for_shift": efermi_ry,
        "spin_channels": 0,
        "warnings": [],
        "errors": []
    }
    RY_TO_EV = 13.605693122994
    efermi_ev_for_shift = None
    if efermi_ry is not None:
        efermi_ev_for_shift = efermi_ry * RY_TO_EV

    search_paths = [nscf_working_directory]
    potential_out_dir = os.path.join(nscf_working_directory, "OUT.ABACUS") 
    if os.path.isdir(potential_out_dir):
        search_paths.append(potential_out_dir)
    
    dos_files_found = []
    for s_path in search_paths:
        dos_files_found.extend(glob.glob(os.path.join(s_path, dos_filename_pattern)))
    
    if not dos_files_found and dos_filename_pattern == "DOS1*.dat": # Default pattern check
        for s_path in search_paths: # Try common exact names
            if os.path.exists(os.path.join(s_path, "DOS1")): 
                dos_files_found.append(os.path.join(s_path, "DOS1"))
            elif os.path.exists(os.path.join(s_path, "DOS")): # Non-spin default
                 dos_files_found.append(os.path.join(s_path, "DOS"))
            # Break if primary DOS1 or DOS is found to avoid duplicates if pattern was too general
            if any(f.endswith("DOS1") or f.endswith("DOS") for f in dos_files_found): break


    if not dos_files_found:
        results["errors"].append(f"No DOS data files matching pattern '{dos_filename_pattern}' found in search paths: {search_paths}.")
        return results

    dos_files_found = sorted(list(set(dos_files_found))) # Unique and sorted

    first_file_energies = None

    for filepath in dos_files_found:
        # Try to determine spin channel from filename if possible (e.g. DOS1, DOS2)
        filename_only = os.path.basename(filepath)
        spin_match = re.search(r"DOS([12])", filename_only, re.IGNORECASE)
        
        # If we are processing a file that seems like a specific spin (e.g. DOS1.dat, DOS2.dat)
        # and we haven't assigned a spin key yet, or if it's a new spin.
        temp_spin_key_suffix = ""
        if spin_match:
            temp_spin_key_suffix = spin_match.group(1)
        
        # If it's the first file or a new spin type based on filename
        if results["spin_channels"] == 0 or (temp_spin_key_suffix and f"spin{temp_spin_key_suffix}" not in results["dos_values"]):
            results["spin_channels"] += 1
            spin_key = f"spin{temp_spin_key_suffix if temp_spin_key_suffix else results['spin_channels']}"
        elif not temp_spin_key_suffix and results["spin_channels"] == 1 and "spin1" in results["dos_values"]:
            # This case might be a generic "DOS" file after a "DOS1" was already processed.
            # This logic might need refinement if filenames are ambiguous.
            results["warnings"].append(f"Processing generic DOS file {filename_only} after a spin-specific one. Behavior might be unexpected.")
            spin_key = f"spin{results['spin_channels'] + 1}" # Treat as new spin for now
            results["spin_channels"] +=1
        elif temp_spin_key_suffix and f"spin{temp_spin_key_suffix}" in results["dos_values"]:
            results["warnings"].append(f"Duplicate spin channel data found for {spin_key} from file {filename_only}. Skipping.")
            continue # Skip if this spin channel data is already populated
        else: # Fallback if no numeric suffix, and spin1 already exists
             results["spin_channels"] += 1
             spin_key = f"spin{results['spin_channels']}"


        current_energies_ev: List[float] = []
        current_dos_values: List[float] = []

        try:
            with open(filepath, "r") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines):
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("@"): 
                    continue
                parts = line.split()
                if len(parts) >= 2: 
                    try:
                        energy = float(parts[0]) 
                        dos_val = float(parts[1]) 
                        
                        if efermi_ev_for_shift is not None:
                            energy -= efermi_ev_for_shift
                        
                        current_energies_ev.append(energy)
                        current_dos_values.append(dos_val)
                    except ValueError:
                        results["warnings"].append(f"Could not parse data line in {filepath}: '{line}'. Skipping.")
                else:
                    results["warnings"].append(f"Skipping malformed line in {filepath}: '{line}'. Expected at least 2 columns.")
            
            if not current_dos_values:
                results["errors"].append(f"No valid DOS data parsed from {filepath}.")
                # results["spin_channels"] -= 1 # Don't decrement here, let overall logic handle it
                continue

            if first_file_energies is None: 
                first_file_energies = current_energies_ev
                results["energies_ev"] = first_file_energies
            elif len(current_energies_ev) != len(first_file_energies):
                results["errors"].append(f"Energy grid mismatch between primary DOS file and {filepath}.")
                results["warnings"].append(f"Using DOS data from {filepath} despite energy grid mismatch. Lengths: {len(first_file_energies)} vs {len(current_energies_ev)}")
            
            results["dos_values"][spin_key] = current_dos_values

        except Exception as e:
            results["errors"].append(f"Failed to process DOS file {filepath}: {str(e)}")
            # results["spin_channels"] -=1 # Don't decrement here

    # Final check on spin channels based on successfully parsed data
    actual_parsed_spin_channels = len(results["dos_values"])
    results["spin_channels"] = actual_parsed_spin_channels

    if actual_parsed_spin_channels > 0 and not results["errors"]:
        results["parsing_successful"] = True
        if actual_parsed_spin_channels == 1:
            # If only one spin channel was parsed, simplify dos_values to be a list directly
            # Find the key (e.g., "spin1" or whatever it was named)
            single_spin_key = list(results["dos_values"].keys())[0]
            results["dos_values"] = results["dos_values"][single_spin_key]
    elif not results["errors"] and actual_parsed_spin_channels == 0 : 
         results["errors"].append("No DOS data could be successfully parsed from any found files.")

    return results


if __name__ == '__main__':
    # ... (previous test blocks) ...
    import asyncio 
    import tempfile
    import shutil
    import os # Ensure os is imported for path operations in test

    async def test_parse_dos_output():
        print("\n--- Testing ABACUS DOS Output Parsing ---")
        test_dos_dir = tempfile.mkdtemp(prefix="test_dos_")

        # Test 1: Single DOS file (non-spin-polarized or spin1)
        dos_content1 = """# E(eV)    DOS(states/eV/cell)
-10.0   0.0
-9.5    0.1
-9.0    0.5
-8.5    0.2
-8.0    0.0
"""
        with open(os.path.join(test_dos_dir, "DOS1_total.dat"), "w") as f: # Matches default pattern
            f.write(dos_content1)
        
        parsed_dos1 = parse_abacus_dos_output(test_dos_dir, dos_filename_pattern="DOS1*.dat")
        print("\nTest 1: Parsed single DOS file (DOS1_total.dat)")
        assert parsed_dos1["parsing_successful"]
        assert parsed_dos1["spin_channels"] == 1
        assert len(parsed_dos1["energies_ev"]) == 5
        assert isinstance(parsed_dos1["dos_values"], list) and len(parsed_dos1["dos_values"]) == 5
        assert abs(parsed_dos1["energies_ev"][1] - (-9.5)) < 1e-9
        assert abs(parsed_dos1["dos_values"][2] - 0.5) < 1e-9

        # Test 1b: Generic DOS file name
        with open(os.path.join(test_dos_dir, "DOS"), "w") as f: # Generic name
            f.write(dos_content1)
        # Remove DOS1_total.dat to ensure "DOS" is picked up by fallback
        os.remove(os.path.join(test_dos_dir, "DOS1_total.dat"))
        parsed_dos1b = parse_abacus_dos_output(test_dos_dir, dos_filename_pattern="DOS1*.dat") # Still use default pattern
        print("\nTest 1b: Parsed single DOS file (DOS)")
        assert parsed_dos1b["parsing_successful"]
        assert parsed_dos1b["spin_channels"] == 1
        assert len(parsed_dos1b["energies_ev"]) == 5

        # Recreate DOS1 for next test
        with open(os.path.join(test_dos_dir, "DOS1_total.dat"), "w") as f:
            f.write(dos_content1)


        # Test 2: With Fermi energy shift
        efermi_test_ry = 0.1 * (1/13.605693122994) 
        parsed_dos1_shifted = parse_abacus_dos_output(test_dos_dir, dos_filename_pattern="DOS1*.dat", efermi_ry=efermi_test_ry)
        print("\nTest 2: Parsed single DOS file with E-fermi shift")
        assert parsed_dos1_shifted["parsing_successful"]
        assert abs(parsed_dos1_shifted["energies_ev"][1] - (-9.5 - 0.1)) < 1e-7

        # Test 3: Spin-polarized DOS (DOS1 and DOS2)
        dos_content2 = """# E(eV)    DOS(states/eV/cell) spin_down
-10.0   0.01
-9.5    0.11
-9.0    0.51
-8.5    0.21
-8.0    0.01
"""
        with open(os.path.join(test_dos_dir, "DOS2_total.dat"), "w") as f: # Matches DOS*.dat
            f.write(dos_content2)

        parsed_dos2 = parse_abacus_dos_output(test_dos_dir, dos_filename_pattern="DOS*total.dat") 
        print("\nTest 3: Parsed spin-polarized DOS files")
        assert parsed_dos2["parsing_successful"]
        assert parsed_dos2["spin_channels"] == 2
        assert "spin1" in parsed_dos2["dos_values"]
        assert "spin2" in parsed_dos2["dos_values"]
        assert len(parsed_dos2["dos_values"]["spin1"]) == 5
        assert len(parsed_dos2["dos_values"]["spin2"]) == 5
        assert abs(parsed_dos2["dos_values"]["spin2"][2] - 0.51) < 1e-9

        # Test 4: File not found
        empty_dir_dos = tempfile.mkdtemp(prefix="empty_dos_")
        parsed_dos4 = parse_abacus_dos_output(empty_dir_dos, dos_filename_pattern="NonExistent*.dat")
        print("\nTest 4: DOS file not found")
        assert not parsed_dos4["parsing_successful"]
        assert "No DOS data files matching pattern" in parsed_dos4["errors"][0]
        shutil.rmtree(empty_dir_dos)
        
        shutil.rmtree(test_dos_dir)
        print("\n--- ABACUS DOS Output Parsing Tests Completed ---")

    async def run_all_core_tests():
        # ... (calls to previous test functions)
        await test_parse_dos_output()

    if __name__ == '__main__':
        asyncio.run(run_all_core_tests())