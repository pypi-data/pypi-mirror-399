# src/tools/property_analysis.py
from typing import Dict, Any, Optional, List

# Import core logic functions from other modules as needed
# For band structure, we'll likely need to call SCF logic first,
# then set up and run an NSCF calculation, then parse band output.

from src.tools.calculation_execution import run_scf_core_logic
from src.core.abacus_runner import (
    generate_abacus_input,
    generate_abacus_stru,
    generate_abacus_kpt,
    execute_abacus_command,
    parse_abacus_band_output,
    parse_abacus_dos_output, # <--- 添加 DOS 解析器导入
    atoms_from_dict
)
import os
import tempfile # Might be needed if we save intermediate files explicitly

# 导入结果解释器
from src.tools.result_interpreter import result_interpreter

DEFAULT_ABACUS_EXEC_COMMAND = "abacus" # Consistent default

async def calculate_band_structure_core_logic(
    structure_dict: Dict[str, Any],
    scf_input_params: Dict[str, Any], # Parameters for the initial SCF run
    nscf_input_params_overrides: Dict[str, Any], # Parameters specific to or overriding for NSCF band run
    kpoints_definition_scf: Dict[str, Any], # K-points for initial SCF
    kpoints_definition_bandpath: Dict[str, Any], # K-points for band path (Line mode)
    pseudo_potential_map: Dict[str, str],
    orbital_file_map: Optional[Dict[str, str]] = None,
    abacus_command: str = DEFAULT_ABACUS_EXEC_COMMAND,
    pseudo_base_path: str = "./",
    orbital_base_path: Optional[str] = None,
    server_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Core logic for calculating band structure using ABACUS.
    Involves an initial SCF run, then an NSCF run along a k-path.
    """
    results: Dict[str, Any] = {"success": False, "data": None, "logs": {}, "errors": [], "warnings": [], "task_ids": {}}
    
    # --- Step 1: Perform initial SCF calculation ---
    scf_results = await run_scf_core_logic(
        structure_dict=structure_dict,
        input_params=scf_input_params,
        kpoints_definition=kpoints_definition_scf,
        pseudo_potential_map=pseudo_potential_map,
        orbital_file_map=orbital_file_map,
        abacus_command=abacus_command,
        pseudo_base_path=pseudo_base_path,
        orbital_base_path=orbital_base_path,
        server_config=server_config
    )

    results["logs"]["scf_run"] = scf_results.get("logs", {})
    results["warnings"].extend(scf_results.get("warnings", []))
    results["task_ids"]["scf_task_id"] = scf_results.get("task_id")
    
    if not scf_results.get("success"):
        results["errors"].append("Initial SCF calculation failed or did not converge.")
        results["errors"].extend(scf_results.get("errors", []))
        return results

    scf_data = scf_results.get("data", {})
    if not scf_data.get("converged"):
        results["errors"].append("Initial SCF calculation did not converge.")
        return results

    scf_working_directory = scf_results.get("logs", {}).get("working_directory")
    if not scf_working_directory:
        results["errors"].append("Working directory from SCF run not found.")
        return results
    
    results["logs"]["initial_scf_data"] = scf_data
    fermi_energy_ry_from_scf = scf_data.get("fermi_energy_ry")
    fermi_energy_ev_from_scf = scf_data.get("fermi_energy_ev")


    # --- Step 2: Prepare and run NSCF calculation for band structure ---
    try:
        # Prepare NSCF input parameters
        nscf_params = scf_input_params.copy() # Start with SCF params
        nscf_params["calculation"] = "nscf" # Non-self-consistent field calculation
        nscf_params["init_chg"] = "file"    # Read charge density from previous SCF
        # Ensure other relevant NSCF parameters are set, e.g., nbands might need to be larger
        nscf_params.update(nscf_input_params_overrides) # Apply NSCF specific overrides/additions
        
        # ntype is already in nscf_params from the copy of scf_input_params (which got it from stru)
        # pseudo_dir should also be set correctly to point to where pseudos are (usually CWD for the run)
        nscf_params.setdefault("pseudo_dir", "./")
        # Ensure out_band is set if not provided by user, ABACUS default might be 0
        nscf_params.setdefault("out_band", 1)


        # Generate STRU (usually the same as SCF, unless relaxation happened before band calc)
        # For simplicity, assume structure_dict is the one to use for NSCF too.
        stru_content_nscf, ntype_nscf = generate_abacus_stru(
            atoms_obj_or_dict=structure_dict,
            pseudo_potential_map=pseudo_potential_map,
            orbital_file_map=orbital_file_map,
            coordinate_type=nscf_params.get("stru_coordinate_type", "Cartesian_Angstrom"),
             fixed_atoms_indices=nscf_params.get("stru_fixed_atoms_indices")
        )
        results["logs"]["nscf_stru_file_content"] = stru_content_nscf
        nscf_params["ntype"] = ntype_nscf # Ensure ntype is consistent

        # Generate INPUT for NSCF
        input_content_nscf = generate_abacus_input(nscf_params)
        results["logs"]["nscf_input_file_content"] = input_content_nscf

        # Generate KPT for band path
        if kpoints_definition_bandpath.get("mode", "").lower() not in ["line", "bandpath"]:
            results["errors"].append("K-points definition for band structure must be 'Line' or 'Bandpath' mode.")
            return results
        
        kpt_content_band = generate_abacus_kpt(
            kpt_generation_mode=kpoints_definition_bandpath["mode"],
            atoms_obj_or_dict=structure_dict,
            kpath_definition=kpoints_definition_bandpath.get("path_definition"),
            kpts_npoints_per_segment=kpoints_definition_bandpath.get("npoints_per_segment")
        )
        results["logs"]["nscf_kpt_file_content"] = kpt_content_band
        
        # Extract expected number of k-points for band parsing validation
        num_kpts_band_expected = None
        if kpt_content_band:
            try:
                num_kpts_band_expected = int(kpt_content_band.splitlines()[1].split("#")[0].strip())
            except (IndexError, ValueError):
                results["warnings"].append("Could not determine expected number of k-points from generated KPT file for band path.")


        # Prepare pseudo/orbital files (same as SCF)
        full_path_pseudo_files_nscf = {
            fname: os.path.join(pseudo_base_path, fname)
            for symbol, fname in pseudo_potential_map.items()
        }
        full_path_orbital_files_nscf = None
        if orbital_file_map:
            current_orbital_base_path_nscf = orbital_base_path if orbital_base_path else pseudo_base_path
            full_path_orbital_files_nscf = {
                fname: os.path.join(current_orbital_base_path_nscf, fname)
                for symbol, fname in orbital_file_map.items()
            }

        # Execute NSCF ABACUS command
        # Important: NSCF run needs access to the charge density file from the SCF run.
        # This means it should ideally run in the same directory or have `out_dir` from SCF copied.
        # For simplicity, we'll assume execute_abacus_command handles running in a new temp dir
        # and we need to copy the charge density file (e.g. SPIN1_CHG) from scf_working_directory.
        
        # This part is tricky: how to pass the charge density.
        # Option 1: Copy relevant files from scf_working_directory to a new temp dir for NSCF.
        # Option 2: Modify execute_abacus_command to accept a list of pre-existing files to link/copy.
        # Option 3: If ABACUS allows specifying path to charge file, use that. (e.g. `read_file_dir`)
        
        # For now, let's assume the NSCF run will be in a new directory,
        # and we'd need to copy the charge density.
        # This requires knowing the charge density filename (e.g., "SPIN1_CHG.cube" or just "SPIN1_CHG")
        # ABACUS `INPUT` parameter `read_file_dir` can point to the SCF output directory.
        # Let's assume `init_chg = "file"` and `read_file_dir` is set in `nscf_params` by the user,
        # or we set it to `scf_working_directory`.
        
        # If `read_file_dir` is not set, we might need to copy files.
        # For now, let's assume user sets `read_file_dir` in `nscf_input_params_overrides`
        # to point to `scf_results["logs"]["working_directory"]`.
        # Or, the `execute_abacus_command` could be enhanced to handle this.
        # A simpler approach for now: if `read_file_dir` is not in nscf_params, set it.
        if "read_file_dir" not in nscf_params:
            nscf_params["read_file_dir"] = os.path.abspath(scf_working_directory)
            # Re-generate input_content_nscf if read_file_dir was added
            input_content_nscf = generate_abacus_input(nscf_params)
            results["logs"]["nscf_input_file_content"] = input_content_nscf # Update log
            results["warnings"].append(f"Set 'read_file_dir' for NSCF to SCF working directory: {nscf_params['read_file_dir']}")


        timeout_nscf = nscf_params.get("execution_timeout_seconds", 3600.0)
        
        nscf_exec_results = await execute_abacus_command(
            abacus_command=abacus_command,
            input_content=input_content_nscf,
            stru_content=stru_content_nscf, # Usually same STRU as SCF
            kpt_content=kpt_content_band,   # Band path KPT
            pseudo_potential_files=full_path_pseudo_files_nscf,
            orbital_files=full_path_orbital_files_nscf,
            timeout_seconds=timeout_nscf,
            calculation_type_for_task_mgmt="nscf_band",
            input_params_for_task_mgmt=nscf_params,
            structure_dict_for_task_mgmt=structure_dict,
            kpoints_def_for_task_mgmt=kpoints_definition_bandpath, # Definition used for band KPTs
            pseudo_map_for_task_mgmt=pseudo_potential_map,
            orbital_map_for_task_mgmt=orbital_file_map
        )

        results["logs"]["nscf_run"] = nscf_exec_results
        results["task_ids"]["nscf_band_task_id"] = nscf_exec_results.get("task_id")
        
        if not nscf_exec_results.get("success"):
            results["errors"].append(nscf_exec_results.get("error", "ABACUS NSCF (band) execution failed."))
            if not nscf_exec_results.get("error") and nscf_exec_results.get("stderr"):
                 results["errors"].append(f"ABACUS NSCF stderr: {nscf_exec_results.get('stderr')}")
            return results

        # --- Step 3: Parse band structure output ---
        # --- Step 3: Parse band structure output ---
        nscf_work_dir = nscf_exec_results.get("working_directory")
        if not nscf_work_dir:
            results["errors"].append("NSCF working directory not found after execution, cannot parse band data.")
            return results

        # Determine the band file prefix from INPUT if specified, otherwise use default
        out_band_prefix_from_input = nscf_params.get("out_band_prefix", "BANDS")

        band_data_parsed = parse_abacus_band_output(
            nscf_working_directory=nscf_work_dir,
            out_band_prefix=out_band_prefix_from_input,
            num_kpts_expected=num_kpts_band_expected,
            num_bands_expected=nscf_params.get("nbands") # nbands from NSCF input
        )
        
        if band_data_parsed.get("parsing_successful"):
            band_results_data = {
                "k_points_coordinates": band_data_parsed.get("k_points_coordinates"),
                "eigenvalues_ry": band_data_parsed.get("eigenvalues_ry"),
                "eigenvalues_ev": band_data_parsed.get("eigenvalues_ev"),
                "fermi_energy_ry": fermi_energy_ry_from_scf, # Fermi energy from initial SCF
                "fermi_energy_ev": fermi_energy_ev_from_scf,
                "num_kpoints": band_data_parsed.get("num_kpoints_found"),
                "num_bands": band_data_parsed.get("num_bands_found"),
                "spin_channels": band_data_parsed.get("spin_channels"),
                "message": "Band structure calculation and parsing successful."
            }
            
            # Add interpretation and recommendations
            interpretation_data = result_interpreter.interpret_band_structure_results(band_results_data)
            band_results_data["interpretation"] = interpretation_data["interpretation"]
            band_results_data["recommendations"] = interpretation_data["recommendations"]
            
            results["data"] = band_results_data
            results["success"] = True
        else:
            results["errors"].append("Failed to parse band structure data from ABACUS output.")
            results["errors"].extend(band_data_parsed.get("errors", []))
            results["data"] = {"message": "NSCF run completed, but band data parsing failed."}
        
        results["warnings"].extend(band_data_parsed.get("warnings", []))

    except Exception as e:
        results["errors"].append(f"An unexpected error in calculate_band_structure_core_logic: {str(e)}")
        results["success"] = False # Ensure success is false on exception
    
    return results

# No __main__ test block here yet, as it depends on parse_abacus_band_output
# and more complex mocking of two-step calculations.
async def calculate_dos_core_logic(
    structure_dict: Dict[str, Any],
    scf_input_params: Dict[str, Any],
    nscf_input_params_overrides: Dict[str, Any], # Params for NSCF DOS run (e.g., out_dos, dos_emin, dos_emax)
    kpoints_definition_scf: Dict[str, Any],
    kpoints_definition_dos: Dict[str, Any], # K-points for NSCF DOS (typically denser MP grid)
    pseudo_potential_map: Dict[str, str],
    orbital_file_map: Optional[Dict[str, str]] = None,
    abacus_command: str = DEFAULT_ABACUS_EXEC_COMMAND,
    pseudo_base_path: str = "./",
    orbital_base_path: Optional[str] = None,
    server_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Core logic for calculating Density of States (DOS) using ABACUS.
    Involves an initial SCF run, then an NSCF run with a denser k-point grid for DOS.
    """
    results: Dict[str, Any] = {"success": False, "data": None, "logs": {}, "errors": [], "warnings": [], "task_ids": {}}

    # --- Step 1: Perform initial SCF calculation ---
    scf_results = await run_scf_core_logic(
        structure_dict=structure_dict,
        input_params=scf_input_params,
        kpoints_definition=kpoints_definition_scf,
        pseudo_potential_map=pseudo_potential_map,
        orbital_file_map=orbital_file_map,
        abacus_command=abacus_command,
        pseudo_base_path=pseudo_base_path,
        orbital_base_path=orbital_base_path,
        server_config=server_config
    )

    results["logs"]["scf_run"] = scf_results.get("logs", {})
    results["warnings"].extend(scf_results.get("warnings", []))
    results["task_ids"]["scf_task_id"] = scf_results.get("task_id")

    if not scf_results.get("success"):
        results["errors"].append("Initial SCF calculation failed or did not converge.")
        results["errors"].extend(scf_results.get("errors", []))
        return results

    scf_data = scf_results.get("data", {})
    if not scf_data.get("converged"):
        results["errors"].append("Initial SCF calculation did not converge.")
        return results

    scf_working_directory = scf_results.get("logs", {}).get("working_directory")
    if not scf_working_directory:
        results["errors"].append("Working directory from SCF run not found.")
        return results
    
    results["logs"]["initial_scf_data"] = scf_data
    fermi_energy_ry_from_scf = scf_data.get("fermi_energy_ry")
    fermi_energy_ev_from_scf = scf_data.get("fermi_energy_ev")
    nelect_from_scf = scf_data.get("nelect") # Number of electrons, useful for DOS normalization/plotting

    # --- Step 2: Prepare and run NSCF calculation for DOS ---
    try:
        # Prepare NSCF input parameters for DOS
        nscf_dos_params = scf_input_params.copy() # Start with SCF params
        nscf_dos_params["calculation"] = "nscf"    # Non-self-consistent field calculation
        nscf_dos_params["init_chg"] = "file"       # Read charge density from previous SCF
        
        # DOS specific parameters
        nscf_dos_params.setdefault("out_dos", 1) # Enable DOS output (1 for total DOS)
        # User can override dos_emin, dos_emax, dos_deltae, dos_sigma in nscf_input_params_overrides
        
        nscf_dos_params.update(nscf_input_params_overrides) # Apply NSCF/DOS specific overrides

        # Ensure pseudo_dir is set
        nscf_dos_params.setdefault("pseudo_dir", "./")

        # Generate STRU (same as SCF, assuming no relaxation before DOS)
        stru_content_nscf_dos, ntype_nscf_dos = generate_abacus_stru(
            atoms_obj_or_dict=structure_dict,
            pseudo_potential_map=pseudo_potential_map,
            orbital_file_map=orbital_file_map,
            coordinate_type=nscf_dos_params.get("stru_coordinate_type", "Cartesian_Angstrom"),
            fixed_atoms_indices=nscf_dos_params.get("stru_fixed_atoms_indices")
        )
        results["logs"]["nscf_dos_stru_file_content"] = stru_content_nscf_dos
        nscf_dos_params["ntype"] = ntype_nscf_dos

        # Generate INPUT for NSCF DOS
        input_content_nscf_dos = generate_abacus_input(nscf_dos_params)
        results["logs"]["nscf_dos_input_file_content"] = input_content_nscf_dos

        # Generate KPT for DOS (typically denser Monkhorst-Pack grid)
        if kpoints_definition_dos.get("mode", "").lower() not in ["mp", "gamma", "monkhorst-pack"]:
            results["errors"].append("K-points definition for DOS NSCF run should be 'MP' (Monkhorst-Pack) or 'Gamma' mode.")
            # Allow explicit k-points if needed, but MP is typical for DOS
            # return results # Or just warn and proceed if explicit k-points are provided correctly
            results["warnings"].append(f"K-points mode for DOS is '{kpoints_definition_dos.get('mode', '')}'. Ensure it's appropriate for DOS.")

        kpt_content_dos = generate_abacus_kpt(
            kpt_generation_mode=kpoints_definition_dos["mode"],
            atoms_obj_or_dict=structure_dict, # For cell vectors if needed by kpt generator
            kpts_mp_grid=kpoints_definition_dos.get("mp_grid"),
            kpts_mp_offset=kpoints_definition_dos.get("mp_offset", [0,0,0]),
            kpts_mp_gamma_center=kpoints_definition_dos.get("gamma_center", True),
            # Add other kpt params if necessary (e.g. explicit k-points)
        )
        results["logs"]["nscf_dos_kpt_file_content"] = kpt_content_dos

        # Prepare pseudo/orbital files (same as SCF)
        full_path_pseudo_files_nscf_dos = {
            fname: os.path.join(pseudo_base_path, fname)
            for symbol, fname in pseudo_potential_map.items()
        }
        full_path_orbital_files_nscf_dos = None
        if orbital_file_map:
            current_orbital_base_path_nscf_dos = orbital_base_path if orbital_base_path else pseudo_base_path
            full_path_orbital_files_nscf_dos = {
                fname: os.path.join(current_orbital_base_path_nscf_dos, fname)
                for symbol, fname in orbital_file_map.items()
            }

        # Set read_file_dir for NSCF to point to SCF working directory
        if "read_file_dir" not in nscf_dos_params:
            nscf_dos_params["read_file_dir"] = os.path.abspath(scf_working_directory)
            # Re-generate input_content_nscf_dos if read_file_dir was added
            input_content_nscf_dos = generate_abacus_input(nscf_dos_params)
            results["logs"]["nscf_dos_input_file_content"] = input_content_nscf_dos # Update log
            results["warnings"].append(f"Set 'read_file_dir' for NSCF (DOS) to SCF working directory: {nscf_dos_params['read_file_dir']}")

        timeout_nscf_dos = nscf_dos_params.get("execution_timeout_seconds", 3600.0)

        nscf_dos_exec_results = await execute_abacus_command(
            abacus_command=abacus_command,
            input_content=input_content_nscf_dos,
            stru_content=stru_content_nscf_dos,
            kpt_content=kpt_content_dos,
            pseudo_potential_files=full_path_pseudo_files_nscf_dos,
            orbital_files=full_path_orbital_files_nscf_dos,
            timeout_seconds=timeout_nscf_dos,
            calculation_type_for_task_mgmt="nscf_dos",
            input_params_for_task_mgmt=nscf_dos_params,
            structure_dict_for_task_mgmt=structure_dict,
            kpoints_def_for_task_mgmt=kpoints_definition_dos,
            pseudo_map_for_task_mgmt=pseudo_potential_map,
            orbital_map_for_task_mgmt=orbital_file_map
        )

        results["logs"]["nscf_dos_run"] = nscf_dos_exec_results
        results["task_ids"]["nscf_dos_task_id"] = nscf_dos_exec_results.get("task_id")

        if not nscf_dos_exec_results.get("success"):
            results["errors"].append(nscf_dos_exec_results.get("error", "ABACUS NSCF (DOS) execution failed."))
            if not nscf_dos_exec_results.get("error") and nscf_dos_exec_results.get("stderr"):
                 results["errors"].append(f"ABACUS NSCF (DOS) stderr: {nscf_dos_exec_results.get('stderr')}")
            return results

        # --- Step 3: Parse DOS output ---
        nscf_dos_work_dir = nscf_dos_exec_results.get("working_directory")
        if not nscf_dos_work_dir:
            results["errors"].append("NSCF (DOS) working directory not found after execution, cannot parse DOS data.")
            return results

        # Determine DOS filename pattern from INPUT if specified, otherwise use default
        # ABACUS typically outputs DOS files like DOS1_*.dat, DOS2_*.dat (if spin-polarized)
        # The `out_dos` parameter in INPUT controls this. If `out_dos = 1`, it's total DOS.
        # `parse_abacus_dos_output` has a default pattern.
        dos_filename_pattern = nscf_dos_params.get("dos_filename_pattern", "DOS*.dat") # Or be more specific if needed

        dos_data_parsed = parse_abacus_dos_output(
            nscf_working_directory=nscf_dos_work_dir,
            dos_filename_pattern=dos_filename_pattern,
            fermi_energy_ry=fermi_energy_ry_from_scf # Pass Fermi energy for energy axis shifting
        )

        if dos_data_parsed.get("parsing_successful"):
            # Construct the data part of the results
            parsed_dos_data = dos_data_parsed.get("dos_data", {})
            
            # Check if spin-polarized data exists
            spin_channels_present = []
            if "total_dos_spin_up" in parsed_dos_data or "total_dos_spin_1" in parsed_dos_data:
                spin_channels_present.append("spin_up") # or "spin_1"
            if "total_dos_spin_down" in parsed_dos_data or "total_dos_spin_2" in parsed_dos_data:
                spin_channels_present.append("spin_down") # or "spin_2"
            
            if not spin_channels_present and "total_dos" in parsed_dos_data:
                 spin_channels_present.append("non_spin_polarized")


            dos_results_data = {
                "dos_data": parsed_dos_data, # Contains energy_ev, total_dos, etc.
                "fermi_energy_ry": fermi_energy_ry_from_scf,
                "fermi_energy_ev": fermi_energy_ev_from_scf,
                "nelect": nelect_from_scf,
                "spin_channels_present": spin_channels_present,
                "message": "DOS calculation and parsing successful."
            }
            
            # Add interpretation and recommendations
            # Prepare input parameters for DOS interpretation
            dos_input_params = nscf_dos_params.copy()
            dos_input_params["kpoints_definition_dos"] = kpoints_definition_dos
            interpretation_data = result_interpreter.interpret_dos_results(dos_results_data, dos_input_params)
            dos_results_data["interpretation"] = interpretation_data["interpretation"]
            dos_results_data["recommendations"] = interpretation_data["recommendations"]
            
            results["data"] = dos_results_data
            results["success"] = True
        else:
            results["errors"].append("Failed to parse DOS data from ABACUS output.")
            results["errors"].extend(dos_data_parsed.get("errors", []))
            results["data"] = {"message": "NSCF (DOS) run completed, but DOS data parsing failed."}
        
        results["warnings"].extend(dos_data_parsed.get("warnings", []))

    except Exception as e:
        results["errors"].append(f"An unexpected error in calculate_dos_core_logic: {str(e)}")
        results["success"] = False # Ensure success is false on exception
    
    return results
async def calculate_charge_density_core_logic(
    structure_dict: Dict[str, Any],
    scf_input_params: Dict[str, Any], # Parameters for the SCF run, ensure 'out_chg' is set
    kpoints_definition: Dict[str, Any], # K-points for SCF
    pseudo_potential_map: Dict[str, str],
    orbital_file_map: Optional[Dict[str, str]] = None,
    abacus_command: str = DEFAULT_ABACUS_EXEC_COMMAND,
    pseudo_base_path: str = "./",
    orbital_base_path: Optional[str] = None,
    server_config: Optional[Dict[str, Any]] = None,
    charge_density_filename: str = "SPIN1_CHG.cube" # Default, ABACUS might output .rho or other formats too
) -> Dict[str, Any]:
    """
    Core logic for calculating and retrieving charge density using ABACUS.
    Involves an SCF run with charge density output enabled.
    """
    results: Dict[str, Any] = {"success": False, "data": None, "logs": {}, "errors": [], "warnings": [], "task_ids": {}}

    # Ensure 'out_chg' is enabled in SCF parameters
    current_scf_params = scf_input_params.copy()
    if current_scf_params.get("out_chg", 0) == 0:
        current_scf_params["out_chg"] = 1 # Enable charge density output
        results["warnings"].append("Forced 'out_chg = 1' in SCF input parameters to enable charge density output.")
    
    # ABACUS might also need `out_pot` for some charge/potential related outputs,
    # but `out_chg` is primary for charge density.
    # The format (e.g., cube) might be controlled by other parameters or defaults.

    # --- Step 1: Perform SCF calculation ---
    scf_results = await run_scf_core_logic(
        structure_dict=structure_dict,
        input_params=current_scf_params, # Use modified params
        kpoints_definition=kpoints_definition,
        pseudo_potential_map=pseudo_potential_map,
        orbital_file_map=orbital_file_map,
        abacus_command=abacus_command,
        pseudo_base_path=pseudo_base_path,
        orbital_base_path=orbital_base_path,
        server_config=server_config
    )

    results["logs"]["scf_run"] = scf_results.get("logs", {})
    results["warnings"].extend(scf_results.get("warnings", [])) # Collect warnings from scf_run too
    results["task_ids"]["scf_task_id"] = scf_results.get("task_id")

    if not scf_results.get("success"):
        results["errors"].append("SCF calculation for charge density failed or did not converge.")
        results["errors"].extend(scf_results.get("errors", []))
        return results

    scf_data = scf_results.get("data", {})
    if not scf_data.get("converged"):
        results["errors"].append("SCF calculation for charge density did not converge.")
        return results

    scf_working_directory = scf_results.get("logs", {}).get("working_directory")
    if not scf_working_directory:
        results["errors"].append("Working directory from SCF run not found, cannot retrieve charge density.")
        return results

    # --- Step 2: Retrieve charge density file ---
    # The actual filename might depend on ABACUS version, input parameters (like `out_chg_format`),
    # and whether it's spin-polarized (SPIN1_CHG, SPIN2_CHG).
    # For simplicity, we use a user-provided or default filename.
    # A more robust solution would inspect the OUT.ABACUS/output directory for expected files.
    
    # Default output directory within the working directory is often "OUT.ABACUS" or similar.
    # Let's assume the charge density file is in a subdirectory named based on `prefix` from INPUT.
    # ABACUS `INPUT` parameter `prefix` (default "ABACUS") determines subdirectory name.
    # e.g., OUT.{prefix}/SPIN1_CHG.cube
    
    input_prefix = current_scf_params.get("prefix", "ABACUS")
    # Common output sub-directory pattern. This might need to be configurable or detected.
    output_subdir_name = f"OUT.{input_prefix}" 
    
    # Construct the full path to the expected charge density file
    # This is an assumption. ABACUS might place it directly in work_dir or a different subdir.
    # For now, let's try the output_subdir_name first, then the root of work_dir.
    
    possible_charge_density_paths = [
        os.path.join(scf_working_directory, output_subdir_name, charge_density_filename),
        os.path.join(scf_working_directory, charge_density_filename) 
    ]
    
    # If spin polarized (nspin=2 or 4), there might be SPIN1_CHG and SPIN2_CHG.
    # The `charge_density_filename` parameter should reflect what the user wants.
    # If they want total charge, and ABACUS outputs SPIN1_CHG for non-spin and total for spin-polarized,
    # then "SPIN1_CHG.cube" might be okay. If they want spin-up, it'd be "SPIN1_CHG.cube", spin-down "SPIN2_CHG.cube".
    # This logic assumes `charge_density_filename` is correctly specified by the caller for what they need.

    charge_density_file_path_found = None
    for path_attempt in possible_charge_density_paths:
        if os.path.exists(path_attempt) and os.path.isfile(path_attempt):
            charge_density_file_path_found = path_attempt
            break
            
    if charge_density_file_path_found:
        try:
            with open(charge_density_file_path_found, 'r', encoding='utf-8') as f:
                charge_density_content = f.read()
            
            # Cube files can be large. Consider if returning content is always wise.
            # For now, we return it. An alternative is to return the path or a presigned URL if stored remotely.
            results["data"] = {
                "charge_density_content": charge_density_content,
                "charge_density_filename": os.path.basename(charge_density_file_path_found),
                "charge_density_format": os.path.splitext(charge_density_filename)[1].lstrip('.'), # e.g. "cube"
                "message": f"Charge density file '{os.path.basename(charge_density_file_path_found)}' retrieved successfully.",
                "file_path_in_work_dir": os.path.relpath(charge_density_file_path_found, scf_working_directory)
            }
            results["success"] = True
        except Exception as e:
            results["errors"].append(f"Error reading charge density file '{charge_density_file_path_found}': {str(e)}")
            results["data"] = {"message": f"SCF successful, but failed to read charge density file '{os.path.basename(charge_density_file_path_found)}'."}
    else:
        results["errors"].append(f"Charge density file '{charge_density_filename}' not found in expected locations: {possible_charge_density_paths}")
        results["data"] = {"message": "SCF successful, but charge density file not found."}
        # Add a warning if out_chg was 0 initially, as it might be the reason.
        if scf_input_params.get("out_chg", 0) == 0:
             results["warnings"].append(f"Original 'out_chg' was 0. While forced to 1, ensure ABACUS version/settings produce '{charge_density_filename}' with this setting.")


    return results
import numpy as np # For numerical operations, e.g., finding min/max

async def analyze_electronic_properties_core_logic(
    band_structure_data: Optional[Dict[str, Any]] = None,
    dos_data: Optional[Dict[str, Any]] = None, # DOS data might also indicate metallicity
    properties_to_analyze: List[str] = ["band_gap"],
    nelect: Optional[float] = None, # Number of electrons, crucial for identifying VBM/CBM
    user_provided_fermi_level_ev: Optional[float] = None, # If band_structure_data doesn't have it
    user_provided_vacuum_level_ev: Optional[float] = None # For work function
) -> Dict[str, Any]:
    """
    Analyzes electronic properties like band gap from pre-computed band structure data.
    Work function analysis is placeholder due to vacuum level dependency.

    Args:
        band_structure_data: Output from calculate_band_structure_tool.
                             Expected keys: 'eigenvalues_ev', 'fermi_energy_ev', 'k_points_coordinates', 'spin_channels'.
        dos_data: Output from calculate_dos_tool. (Currently used to supplement metallicity check)
        properties_to_analyze: List of properties to analyze. Currently supports "band_gap".
                               "work_function" is a placeholder.
        nelect: Total number of electrons in the system. Used to determine the highest occupied band.
                If not provided, the function will try to infer VBM based on energies below Fermi level.
        user_provided_fermi_level_ev: Optional Fermi level if not in band_structure_data.
        user_provided_vacuum_level_ev: Optional vacuum level for work function calculation.

    Returns:
        Dictionary containing the analysis results.
    """
    results: Dict[str, Any] = {"success": False, "analyzed_properties": {}, "errors": [], "warnings": []}
    analyzed_props = {}

    if not band_structure_data and "band_gap" in properties_to_analyze:
        results["errors"].append("Band structure data is required to calculate band gap.")
        return results

    fermi_level_ev = user_provided_fermi_level_ev
    if band_structure_data and 'fermi_energy_ev' in band_structure_data:
        fermi_level_ev = band_structure_data['fermi_energy_ev']
    
    if fermi_level_ev is None and "band_gap" in properties_to_analyze:
        results["errors"].append("Fermi level (either from band_structure_data or user_provided_fermi_level_ev) is required for band gap analysis.")
        # We could try to infer it if nelect is given and eigenvalues are absolute, but that's more complex.
        # For now, require it.
        # return results # Let it proceed, it might still find something if nelect is very reliable.

    if "band_gap" in properties_to_analyze:
        eigenvalues_ev_all_spins = band_structure_data.get("eigenvalues_ev")
        k_points_coords = band_structure_data.get("k_points_coordinates") # For direct/indirect gap
        spin_channels = band_structure_data.get("spin_channels", 1) # Default to 1 if not specified

        if not eigenvalues_ev_all_spins:
            results["errors"].append("Eigenvalues (eigenvalues_ev) not found in band_structure_data.")
            return results
        
        if nelect is None:
            results["warnings"].append("Number of electrons (nelect) not provided. Band gap analysis might be less reliable, relying solely on Fermi energy to distinguish occupied/unoccupied states.")
            # If fermi_level_ev is also None here, we are in trouble.
            if fermi_level_ev is None:
                results["errors"].append("Cannot determine VBM/CBM without nelect or a reliable Fermi level.")
                return results


        num_bands_per_kpoint = 0
        if spin_channels == 1 and eigenvalues_ev_all_spins: # Non-spin-polarized
             if eigenvalues_ev_all_spins and len(eigenvalues_ev_all_spins) > 0 and isinstance(eigenvalues_ev_all_spins[0], list):
                num_bands_per_kpoint = len(eigenvalues_ev_all_spins[0]) # Number of bands for the first k-point
        elif spin_channels == 2 and eigenvalues_ev_all_spins: # Spin-polarized, expect dict or list of lists of lists
            if isinstance(eigenvalues_ev_all_spins, dict) and "spin_up" in eigenvalues_ev_all_spins:
                if eigenvalues_ev_all_spins["spin_up"] and len(eigenvalues_ev_all_spins["spin_up"]) > 0 and isinstance(eigenvalues_ev_all_spins["spin_up"][0], list):
                    num_bands_per_kpoint = len(eigenvalues_ev_all_spins["spin_up"][0]) 
            elif isinstance(eigenvalues_ev_all_spins, list) and len(eigenvalues_ev_all_spins) == 2: # [[spin_up_bands_k1, ...], [spin_down_bands_k1, ...]]
                 # This structure is less common from our parser, but to be safe:
                 # Assuming eigenvalues_ev_all_spins[0] is for spin_up, and eigenvalues_ev_all_spins[0][0] is list of bands for first kpt
                if eigenvalues_ev_all_spins[0] and len(eigenvalues_ev_all_spins[0]) > 0 and isinstance(eigenvalues_ev_all_spins[0][0], list):
                     num_bands_per_kpoint = len(eigenvalues_ev_all_spins[0][0])


        if num_bands_per_kpoint == 0:
            results["errors"].append("Could not determine the number of bands from eigenvalues_ev structure.")
            return results

        # Determine valence band maximum (VBM) and conduction band minimum (CBM)
        # For insulators/semiconductors, VBM is the highest occupied state, CBM is the lowest unoccupied.
        # For metals, VBM and CBM might be the same (Fermi level crossing bands).
        
        vbm_overall = -np.inf
        cbm_overall = np.inf
        vbm_k_point_idx = -1
        cbm_k_point_idx = -1
        
        # Highest occupied band index. Each band can hold 2 electrons (non-spin) or 1 electron (spin-polarized per spin channel).
        # If nelect is provided, it's more robust.
        # ABACUS band indexing is 1-based in some contexts, Python is 0-based. Assume eigenvalues are 0-indexed.
        
        highest_occupied_band_index_0based = -1
        if nelect is not None:
            if spin_channels == 1: # Non-spin-polarized
                highest_occupied_band_index_0based = int(np.ceil(nelect / 2.0)) - 1
            elif spin_channels == 2: # Spin-polarized
                # For spin-polarized, nelect is total. Each state (per k-point, per band, per spin) holds 1 electron.
                # So, if we have N bands, the first N*num_kpoints states for spin_up are filled up to nelect_spin_up,
                # and similarly for spin_down.
                # This simplification assumes an even distribution or that we are looking at total nelect.
                # A common convention is that `nbands` in input is per spin channel.
                # So, if `nelect` electrons, and `nbands` states per spin, then `nelect/2` electrons per spin channel.
                # The (nelect/2)-th band (0-indexed) would be the highest occupied for that spin channel.
                highest_occupied_band_index_0based = int(np.ceil(nelect / float(spin_channels))) -1 # Simplified: assumes nelect is total and bands are per spin.
                                                                                                   # More accurately, it's the (N_elec_per_spin)-th band.
                                                                                                   # If nelect is total, then N_elec_per_spin = nelect / 2 (for nspin=2)
                                                                                                   # So, (nelect/2)-th band is VBM.
                # This assumes `nbands` in the input was sufficient to cover all occupied states.
        
        if highest_occupied_band_index_0based < 0 and fermi_level_ev is None:
             results["errors"].append("Cannot determine VBM without nelect or Fermi level.")
             return results
        if highest_occupied_band_index_0based >= num_bands_per_kpoint:
            results["warnings"].append(f"Calculated highest_occupied_band_index ({highest_occupied_band_index_0based}) >= num_bands_per_kpoint ({num_bands_per_kpoint}). System might be metallic or nbands too small.")
            # Proceed, but band gap might be ill-defined or zero.


        list_of_eigenvalue_sets = []
        if spin_channels == 1:
            list_of_eigenvalue_sets.append(eigenvalues_ev_all_spins)
        elif spin_channels == 2:
            if isinstance(eigenvalues_ev_all_spins, dict):
                if "spin_up" in eigenvalues_ev_all_spins: list_of_eigenvalue_sets.append(eigenvalues_ev_all_spins["spin_up"])
                if "spin_down" in eigenvalues_ev_all_spins: list_of_eigenvalue_sets.append(eigenvalues_ev_all_spins["spin_down"])
            elif isinstance(eigenvalues_ev_all_spins, list) and len(eigenvalues_ev_all_spins) == 2: # Should be list of kpts, each kpt a list of bands
                 list_of_eigenvalue_sets.extend(eigenvalues_ev_all_spins) # [[kpt_bands_spin1], [kpt_bands_spin2]]


        if not list_of_eigenvalue_sets:
            results["errors"].append("No valid eigenvalue sets found for band gap analysis.")
            return results

        for eigenvalues_one_spin in list_of_eigenvalue_sets:
            if not isinstance(eigenvalues_one_spin, list) or not all(isinstance(kpt_bands, list) for kpt_bands in eigenvalues_one_spin):
                results["errors"].append(f"Malformed eigenvalues_ev structure for a spin channel: expected list of lists. Got: {type(eigenvalues_one_spin)}")
                continue

            for k_idx, k_point_bands in enumerate(eigenvalues_one_spin):
                if not k_point_bands or not isinstance(k_point_bands, list): 
                    results["warnings"].append(f"Empty or invalid band list for k-point index {k_idx} in a spin channel.")
                    continue

                current_vbm_at_k = -np.inf
                current_cbm_at_k = np.inf

                if highest_occupied_band_index_0based >= 0: # Use nelect-derived VBM index
                    if highest_occupied_band_index_0based < len(k_point_bands):
                        current_vbm_at_k = k_point_bands[highest_occupied_band_index_0based]
                    else: # Not enough bands to reach this index
                        results["warnings"].append(f"highest_occupied_band_index {highest_occupied_band_index_0based} is out of range for k-point {k_idx} with {len(k_point_bands)} bands.")
                        # This k-point might not have a clear VBM based on nelect, could be an issue with nbands parameter.
                        # Fallback to Fermi level if available for this k-point, or skip.
                        if fermi_level_ev is not None:
                             for band_energy in k_point_bands:
                                if band_energy <= fermi_level_ev:
                                    current_vbm_at_k = max(current_vbm_at_k, band_energy)
                        else: # Cannot determine VBM for this k-point
                            continue 
                    
                    # CBM is the next band up, if it exists
                    if highest_occupied_band_index_0based + 1 < len(k_point_bands):
                        current_cbm_at_k = k_point_bands[highest_occupied_band_index_0based + 1]
                    else: # No conduction band found immediately above VBM based on nelect
                        # This implies either metallic or an issue. If metallic, CBM might be VBM.
                        # If fermi_level_ev is available, we can refine.
                        pass # CBM remains np.inf if no higher band

                elif fermi_level_ev is not None: # Fallback to Fermi level if nelect is not useful
                    for band_energy in k_point_bands:
                        if band_energy <= fermi_level_ev:
                            current_vbm_at_k = max(current_vbm_at_k, band_energy)
                        if band_energy > fermi_level_ev: # Small tolerance might be needed for metals
                            current_cbm_at_k = min(current_cbm_at_k, band_energy)
                else: # Should have been caught earlier
                    continue


                if current_vbm_at_k > vbm_overall:
                    vbm_overall = current_vbm_at_k
                    vbm_k_point_idx = k_idx
                
                if current_cbm_at_k < cbm_overall:
                    cbm_overall = current_cbm_at_k
                    cbm_k_point_idx = k_idx
        
        band_gap_ev = None
        gap_type = "unknown"

        if vbm_overall > -np.inf and cbm_overall < np.inf : # Both VBM and CBM found
            band_gap_ev = cbm_overall - vbm_overall
            if band_gap_ev < 0: # Should not happen if logic is correct, implies overlap / metallic
                band_gap_ev = 0.0 # Or handle as metallic
                analyzed_props["is_metallic_from_bands"] = True
                results["warnings"].append("Calculated CBM < VBM, system is likely metallic. Band gap set to 0.")
            
            if band_gap_ev >= 0: # Check for direct/indirect only if non-negative gap
                if vbm_k_point_idx == cbm_k_point_idx and vbm_k_point_idx != -1:
                    gap_type = "direct"
                elif vbm_k_point_idx != -1 and cbm_k_point_idx != -1:
                    gap_type = "indirect"
        
        elif vbm_overall > -np.inf and cbm_overall == np.inf: # Only VBM found, no CBM above it (or above Fermi)
            results["warnings"].append("VBM found, but no CBM identified above it (or above Fermi level). System might be metallic or nbands too small for conduction bands.")
            band_gap_ev = 0.0 # Effectively metallic or undefined higher up
            analyzed_props["is_metallic_from_bands"] = True


        if band_gap_ev is not None:
            analyzed_props["band_gap_ev"] = round(band_gap_ev, 4)
            analyzed_props["vbm_ev"] = round(vbm_overall, 4) if vbm_overall > -np.inf else None
            analyzed_props["cbm_ev"] = round(cbm_overall, 4) if cbm_overall < np.inf else None
            analyzed_props["gap_type"] = gap_type
            if k_points_coords and vbm_k_point_idx != -1 and vbm_k_point_idx < len(k_points_coords):
                analyzed_props["vbm_k_point_coordinates"] = k_points_coords[vbm_k_point_idx]
            if k_points_coords and cbm_k_point_idx != -1 and cbm_k_point_idx < len(k_points_coords):
                analyzed_props["cbm_k_point_coordinates"] = k_points_coords[cbm_k_point_idx]
        else: # Could not determine band gap
            results["warnings"].append("Could not determine band gap. VBM or CBM not clearly identified.")
            # Check DOS for metallicity if available
            if dos_data and dos_data.get("dos_data"):
                dos_at_fermi = 0.0
                # Simplified check: if any DOS value at/near Fermi (0 eV if shifted) is non-zero
                energy_ev_dos = dos_data["dos_data"].get("energy_ev_shifted", dos_data["dos_data"].get("energy_ev"))
                total_dos = dos_data["dos_data"].get("total_dos")
                if energy_ev_dos and total_dos:
                    try:
                        # Find DOS value closest to 0 eV (Fermi level)
                        idx_fermi_dos = np.abs(np.array(energy_ev_dos)).argmin()
                        if idx_fermi_dos < len(total_dos):
                            dos_at_fermi = total_dos[idx_fermi_dos]
                    except Exception: # pylint: disable=broad-except
                        pass # Ignore error in this heuristic
                if dos_at_fermi > 1e-3: # Some small threshold
                     analyzed_props["is_metallic_from_dos"] = True
                     results["warnings"].append("DOS data suggests system is metallic (non-zero DOS at Fermi level).")


    if "work_function" in properties_to_analyze:
        if user_provided_vacuum_level_ev is not None and fermi_level_ev is not None:
            work_function_ev = user_provided_vacuum_level_ev - fermi_level_ev
            analyzed_props["work_function_ev"] = round(work_function_ev, 4)
            analyzed_props["vacuum_level_ev_used"] = user_provided_vacuum_level_ev
            analyzed_props["fermi_level_ev_used_for_wf"] = fermi_level_ev
        else:
            results["warnings"].append("Work function analysis requires both 'user_provided_vacuum_level_ev' and a Fermi level (from band_structure_data or 'user_provided_fermi_level_ev').")
            analyzed_props["work_function_ev"] = None
            analyzed_props["work_function_message"] = "Insufficient data for work function (vacuum level or Fermi level missing)."


    if analyzed_props:
        results["analyzed_properties"] = analyzed_props
        results["success"] = True # Success if any property was processed, even with warnings
    else:
        if not results["errors"]: # No errors, but nothing analyzed (e.g. wrong property name)
            results["warnings"].append("No requested properties could be analyzed or no data provided.")
    
    return results