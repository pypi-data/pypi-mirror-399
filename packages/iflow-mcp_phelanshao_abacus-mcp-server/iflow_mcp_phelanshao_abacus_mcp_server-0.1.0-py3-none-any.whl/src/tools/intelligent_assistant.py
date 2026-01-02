# src/tools/intelligent_assistant.py
from typing import Dict, Any, Optional, List
import copy # For deep copying parameter dictionaries

# 导入日志记录
from src.logging_config import log_validation_result, log_app_event

# Placeholder for more sophisticated structure analysis if needed in the future
# from ase import Atoms 
# from ase.geometry import get_layers

DEFAULT_SUGGESTIONS = {
    "common": {
        "input_params": {
            "ecutwfc": 50, # Default energy cutoff in Ry
            "scf_thr": 1e-7, # Default SCF convergence threshold
            "basis_type": "pw", # Plane-wave basis
            "ks_solver": "cg", # Kohn-Sham solver
            "mixing_type": "pulay",
            "mixing_beta": 0.7,
        },
        "kpoints_definition": { # General purpose Monkhorst-Pack
            "mode": "Monkhorst-Pack",
            "mp_grid": [3, 3, 3], # Placeholder, should be structure-dependent
            "mp_offset": [0, 0, 0],
            "gamma_center": True
        },
        "notes": ["These are general starting points. Always verify and adjust based on your specific system and desired accuracy."]
    },
    "scf": {
        "input_params": {
            "calculation": "scf",
            "out_chg": 1, # Usually good to output charge density
            "out_pot": 0, # Potential output often not needed unless for specific analysis
            "out_wfc": 0, # Wavefunction output usually not needed
        },
        "notes": ["For SCF, ensure `ecutwfc` and k-points are converged for your system."]
    },
    "relax": {
        "input_params": {
            "calculation": "relax",
            "force_thr": 0.01, # Ry/Bohr or eV/Angstrom depending on ABACUS version/defaults
            "relax_nmax": 100,
            "out_stru": 1, # Output final structure
        },
        "notes": ["For geometry optimization (relax), `force_thr` is crucial. Ensure k-points and ecutwfc are sufficient."]
    },
    "cell-relax": {
        "input_params": {
            "calculation": "cell-relax",
            "force_thr": 0.01,
            "press_thr": 0.5, # kBar
            "relax_nmax": 100,
            "out_stru": 1,
            "cell_factor": 1.5 # Default cell factor for cell optimization search range
        },
        "notes": ["For cell optimization (cell-relax), both `force_thr` and `press_thr` are important."]
    },
    "md": {
        "input_params": {
            "calculation": "md",
            "md_nstep": 1000,
            "md_dt": 1.0, # fs
            "md_tfirst": 300, # K
            "md_tlast": 300, # K
            "md_thermostat": "nhc", # Nose-Hoover chain
            "out_stru": 1, # Output trajectory or final structure
        },
        "notes": ["For MD, `md_dt` (timestep) and `md_nstep` (number of steps) determine simulation length. Choose thermostat and ensemble appropriately."]
    },
    "bands": {
        "scf_input_params": { # Parameters for the preceding SCF run
            "calculation": "scf",
            "out_chg": 1,
        },
        "nscf_input_params": { # Parameters for the NSCF band run
            "calculation": "nscf",
            "init_chg": "file",
            "out_band": 1,
            # "nbands": "auto" # Placeholder, nbands needs careful consideration
        },
        "kpoints_definition_scf": { # K-points for preceding SCF
            "mode": "Monkhorst-Pack",
            "mp_grid": [5, 5, 5], # Denser for SCF before bands
            "mp_offset": [0,0,0],
            "gamma_center": True
        },
        "kpoints_definition_bandpath": { # K-points for band path
            "mode": "Line",
            "path_definition": "G-X-L-G", # Example path, highly system dependent
            "npoints_per_segment": 20
        },
        "notes": [
            "Band structure calculation requires an initial SCF run, then an NSCF run along a k-path.",
            "Ensure `nbands` in the NSCF run is sufficient to cover desired energy range.",
            "The `path_definition` for k-points is highly dependent on your crystal symmetry."
        ]
    },
    "dos": {
        "scf_input_params": { # Parameters for the preceding SCF run
             "calculation": "scf",
             "out_chg": 1,
        },
        "nscf_input_params": { # Parameters for the NSCF DOS run
            "calculation": "nscf",
            "init_chg": "file",
            "out_dos": 1, # Enable DOS output
            "dos_emin": -10, # eV, relative to Fermi if shifted
            "dos_emax": 10,  # eV
            "dos_deltae": 0.05 # eV
            # "nbands": "auto" # Placeholder
        },
        "kpoints_definition_scf": { # K-points for preceding SCF
            "mode": "Monkhorst-Pack",
            "mp_grid": [5, 5, 5], 
            "mp_offset": [0,0,0],
            "gamma_center": True
        },
        "kpoints_definition_dos": { # K-points for NSCF DOS (typically denser)
            "mode": "Monkhorst-Pack",
            "mp_grid": [9, 9, 9], # Denser for DOS
            "mp_offset": [0,0,0],
            "gamma_center": True
        },
        "notes": [
            "DOS calculation requires an initial SCF run, then an NSCF run with a denser k-point grid.",
            "Ensure `nbands` in the NSCF run is sufficient.",
            "Adjust `dos_emin`, `dos_emax`, `dos_deltae` for desired energy range and resolution."
        ]
    }
}

# Accuracy modifiers (can be expanded)
ACCURACY_MODIFIERS = {
    "low": {"ecutwfc_factor": 0.8, "kpoint_density_factor": 0.8, "scf_thr_factor": 10},
    "medium": {"ecutwfc_factor": 1.0, "kpoint_density_factor": 1.0, "scf_thr_factor": 1},
    "high": {"ecutwfc_factor": 1.2, "kpoint_density_factor": 1.2, "scf_thr_factor": 0.1}
}


async def suggest_parameters_core_logic(
    calculation_type: str,
    structure_dict: Optional[Dict[str, Any]] = None, # Currently unused, for future enhancements
    desired_accuracy: str = "medium"
) -> Dict[str, Any]:
    """
    Suggests input parameters for ABACUS based on calculation type and desired accuracy.
    This is a basic implementation providing general guidance.
    """
    results: Dict[str, Any] = {
        "success": False,
        "suggested_params": {},
        "notes": [],
        "errors": [],
        "warnings": []
    }
    
    calc_type_lower = calculation_type.lower().replace("_", "-") # Normalize type

    if calc_type_lower not in DEFAULT_SUGGESTIONS and calc_type_lower not in ["bands", "dos"]: # bands/dos are special
        results["errors"].append(f"Unsupported calculation_type: {calculation_type}. Supported types: {list(DEFAULT_SUGGESTIONS.keys()) + ['bands', 'dos']}.")
        return results

    # Start with common defaults
    suggested_input_params = copy.deepcopy(DEFAULT_SUGGESTIONS["common"]["input_params"])
    suggested_kpoints_definition = copy.deepcopy(DEFAULT_SUGGESTIONS["common"]["kpoints_definition"])
    notes = list(DEFAULT_SUGGESTIONS["common"]["notes"]) # Copy list

    # Layer specific suggestions
    specific_suggestions = {}
    if calc_type_lower in ["bands", "dos"]: # Special handling for two-step calcs
        specific_suggestions = DEFAULT_SUGGESTIONS.get(calc_type_lower, {})
        # These will return a structure like:
        # { "scf_input_params": {...}, "nscf_input_params": {...}, "kpoints_definition_scf": {...}, ... }
        results["suggested_params"] = copy.deepcopy(specific_suggestions) # Store the whole structure
        notes.extend(specific_suggestions.get("notes", []))

    elif calc_type_lower in DEFAULT_SUGGESTIONS:
        specific_suggestions = DEFAULT_SUGGESTIONS.get(calc_type_lower, {})
        if "input_params" in specific_suggestions:
            suggested_input_params.update(specific_suggestions["input_params"])
        if "kpoints_definition" in specific_suggestions: # Some might not change kpoints
            suggested_kpoints_definition.update(specific_suggestions["kpoints_definition"])
        notes.extend(specific_suggestions.get("notes", []))
        
        results["suggested_params"]["input_params"] = suggested_input_params
        results["suggested_params"]["kpoints_definition"] = suggested_kpoints_definition
    
    # Apply accuracy modifiers if not a special "bands" or "dos" structure
    if calc_type_lower not in ["bands", "dos"]:
        modifier = ACCURACY_MODIFIERS.get(desired_accuracy.lower(), ACCURACY_MODIFIERS["medium"])
        
        if "ecutwfc" in results["suggested_params"].get("input_params", {}):
            original_ecut = results["suggested_params"]["input_params"]["ecutwfc"]
            results["suggested_params"]["input_params"]["ecutwfc"] = round(original_ecut * modifier["ecutwfc_factor"])
        
        if "scf_thr" in results["suggested_params"].get("input_params", {}):
            original_scf_thr = results["suggested_params"]["input_params"]["scf_thr"]
            results["suggested_params"]["input_params"]["scf_thr"] = original_scf_thr * modifier["scf_thr_factor"]

        if "mp_grid" in results["suggested_params"].get("kpoints_definition", {}):
            original_kgrid = results["suggested_params"]["kpoints_definition"]["mp_grid"]
            results["suggested_params"]["kpoints_definition"]["mp_grid"] = [
                max(1, round(k * modifier["kpoint_density_factor"])) for k in original_kgrid
            ]
        notes.append(f"Parameters adjusted for '{desired_accuracy}' accuracy level.")

    elif calc_type_lower in ["bands", "dos"]: # Apply to relevant sub-dictionaries for bands/dos
        modifier = ACCURACY_MODIFIERS.get(desired_accuracy.lower(), ACCURACY_MODIFIERS["medium"])
        param_sets_to_modify = []
        if "scf_input_params" in results["suggested_params"]:
             param_sets_to_modify.append(results["suggested_params"]["scf_input_params"])
        if "nscf_input_params" in results["suggested_params"]: # e.g. for nbands, ecutwfc if set
             param_sets_to_modify.append(results["suggested_params"]["nscf_input_params"])
        
        for param_set in param_sets_to_modify:
            if "ecutwfc" in param_set:
                param_set["ecutwfc"] = round(param_set.get("ecutwfc", DEFAULT_SUGGESTIONS["common"]["input_params"]["ecutwfc"]) * modifier["ecutwfc_factor"])
            if "scf_thr" in param_set: # Less relevant for NSCF, but if present
                param_set["scf_thr"] = param_set.get("scf_thr", DEFAULT_SUGGESTIONS["common"]["input_params"]["scf_thr"]) * modifier["scf_thr_factor"]

        kpoint_sets_to_modify = []
        if "kpoints_definition_scf" in results["suggested_params"] and "mp_grid" in results["suggested_params"]["kpoints_definition_scf"]:
            kpoint_sets_to_modify.append(results["suggested_params"]["kpoints_definition_scf"])
        if "kpoints_definition_dos" in results["suggested_params"] and "mp_grid" in results["suggested_params"]["kpoints_definition_dos"]:
             kpoint_sets_to_modify.append(results["suggested_params"]["kpoints_definition_dos"])

        for kpt_set in kpoint_sets_to_modify:
            original_kgrid = kpt_set["mp_grid"]
            kpt_set["mp_grid"] = [max(1, round(k * modifier["kpoint_density_factor"])) for k in original_kgrid]
        
        if param_sets_to_modify or kpoint_sets_to_modify:
            notes.append(f"Parameters for '{calc_type_lower}' (including SCF and NSCF steps) adjusted for '{desired_accuracy}' accuracy level.")


    # TODO: Future - analyze structure_dict to suggest better k-points or ecutwfc based on elements/lattice.
    if structure_dict:
        notes.append("Structure analysis for parameter suggestion is a future enhancement.")


    results["notes"] = notes
    results["success"] = True
    return results
import re

# Basic knowledge base for ABACUS error diagnosis
# This can be significantly expanded over time.
ERROR_PATTERNS_DIAGNOSIS = [
    {
        "pattern": r"convergence NOT achieved",
        "signature": "SCF_NOT_CONVERGED",
        "possible_causes": [
            "SCF cycle limit (scf_nmax) reached before convergence threshold (scf_thr) met.",
            "Poor initial guess for charge density or wavefunction.",
            "Inappropriate mixing parameters (mixing_type, mixing_beta, mixing_ndim).",
            "System is metallic and requires smearing (smearing_method, smearing_sigma) but not set or too small.",
            "Numerical instability (e.g., due to very small energy differences or ill-conditioned system).",
            "Energy cutoff (ecutwfc) or k-point mesh might be too coarse for the required precision."
        ],
        "suggested_solutions": [
            "Increase `scf_nmax` (e.g., to 100, 200).",
            "Decrease `scf_thr` if it's too stringent for a quick check, but aim for good convergence.",
            "Try different mixing parameters: decrease `mixing_beta` (e.g., to 0.4, 0.2, 0.1), or try `mixing_type = 'pulay-kerker'` or `'broydens'`. Increase `mixing_ndim` if using Pulay.",
            "If metallic, ensure `smearing_method` (e.g., 'gaussian', 'methfessel-paxton') and `smearing_sigma` (e.g., 0.01 - 0.02 Ry) are set.",
            "Check the initial structure for any unusually close atoms or other geometric issues.",
            "Consider starting from a pre-converged charge density from a simpler calculation if available (`init_chg = 'file'`).",
            "Gradually increase `ecutwfc` and k-point density to check for convergence.",
            "If using `ks_solver = 'dav'`, try `'cg'` or vice-versa, especially if numerical errors appear in diagonalization."
        ]
    },
    {
        "pattern": r"Too many k-points", # This is a generic phrase, ABACUS might have specific messages
        "signature": "TOO_MANY_KPOINTS_MEM",
        "possible_causes": [
            "The number of k-points combined with the number of plane waves (set by ecutwfc) and bands exceeds available memory.",
            "Error in k-point generation logic leading to an unexpectedly large number of k-points."
        ],
        "suggested_solutions": [
            "Reduce the k-point mesh density (e.g., decrease values in `mp_grid`).",
            "Reduce `ecutwfc` if possible, but this affects accuracy.",
            "Reduce `nbands` if calculating more bands than necessary.",
            "Run on a machine with more memory or distribute the calculation over more MPI processes if memory per process is the issue."
        ]
    },
    {
        "pattern": r"Error in DAV|Error in ZHEGV|Error in davidson", # Common diagonalization errors
        "signature": "DIAGONALIZATION_ERROR",
        "possible_causes": [
            "Numerical instability during the diagonalization step.",
            "Poorly conditioned Hamiltonian matrix, possibly due to problematic input structure or parameters.",
            "Memory issues, although often reported differently.",
            "Sometimes related to `ecutwfc` being too low for the pseudopotentials used."
        ],
        "suggested_solutions": [
            "Try a different `ks_solver` (e.g., if 'dav', try 'cg'; if 'cg', try 'dav').",
            "Check the input structure for any unusually close atoms or other geometric issues.",
            "Slightly perturb atomic positions if starting from a highly symmetric or problematic configuration.",
            "Increase `ecutwfc`.",
            "Ensure pseudopotentials are appropriate and correctly specified.",
            "Reduce `mixing_beta` or try a more robust mixing scheme."
        ]
    },
    {
        "pattern": r"segmentation fault|SIGSEGV",
        "signature": "SEGMENTATION_FAULT",
        "possible_causes": [
            "A critical error in the ABACUS executable, often due to memory corruption, array out-of-bounds, or a bug.",
            "Incorrect input parameters leading to an unexpected state.",
            "Incompatibility with linked libraries or system environment.",
            "Insufficient memory leading to a crash (though often reported more directly)."
        ],
        "suggested_solutions": [
            "Carefully review all input files (INPUT, STRU, KPT, pseudo/orbital files) for correctness and consistency.",
            "Try a simpler version of the calculation (e.g., fewer atoms, smaller basis set, fewer k-points) to isolate the issue.",
            "Ensure ABACUS was compiled correctly for your system architecture and with compatible libraries.",
            "Check for any system-level memory limits (ulimit).",
            "If reproducible, this might indicate a bug in ABACUS that should be reported to developers with a minimal test case."
        ]
    },
    {
        "pattern": r"not enough memory|memory allocation failed|malloc error",
        "signature": "MEMORY_ALLOCATION_ERROR",
        "possible_causes": [
            "The calculation requires more RAM than available on the system or allocated to the process.",
            "Parameters like `ecutwfc`, number of k-points, `nbands`, and system size heavily influence memory usage."
        ],
        "suggested_solutions": [
            "Reduce `ecutwfc`.",
            "Reduce the density of the k-point mesh.",
            "Reduce `nbands` if more than necessary are being calculated.",
            "For very large systems, consider running on a machine with more memory or using more MPI processes to distribute memory load (if ABACUS scales well for memory with MPI for your calculation type).",
            "Check for system memory limits (ulimit -v)."
        ]
    },
    {
        "pattern": r"WARNING:?(.*)charge density file error", # Example for specific warning
        "signature": "CHARGE_FILE_ERROR_WARN",
        "possible_causes": [
            "Problem reading the initial charge density file when `init_chg = 'file'`.",
            "File not found, corrupted, or in an incompatible format."
        ],
        "suggested_solutions": [
            "Ensure the charge density file (e.g., SPIN1_CHG) exists in the specified `read_file_dir` or current working directory.",
            "Verify the charge density file is not corrupted and was generated by a compatible ABACUS version/calculation.",
            "Check if the format of the charge density file is consistent with what ABACUS expects."
        ]
    },
    {
        "pattern": r"LATTICE_CONSTANT_TOO_SMALL", # ABACUS specific error code
        "signature": "LATTICE_CONSTANT_TOO_SMALL",
        "possible_causes": ["Lattice constant 'lat0' is too small, or cell vectors define a very small volume."],
        "suggested_solutions": ["Increase 'lat0' in INPUT or check cell vectors in STRU for correctness."]
    },
     {
        "pattern": r"SETUP_CELL_FAILED",
        "signature": "SETUP_CELL_FAILED",
        "possible_causes": ["Error during cell setup, often related to lattice parameters or symmetry issues."],
        "suggested_solutions": ["Verify lattice constants, cell angles, and atomic positions. Check symmetry settings if used."]
    }
    # More patterns can be added here
]

async def diagnose_failure_core_logic(
    error_log_content: Optional[str] = None,
    output_log_content: Optional[str] = None,
    # input_parameters: Optional[Dict[str, Any]] = None, # For future context-aware suggestions
    # calculation_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Diagnoses calculation failures based on error messages and output logs.
    Provides potential causes and suggested solutions from a knowledge base.
    """
    results: Dict[str, Any] = {
        "success": False,
        "diagnoses": [],
        "summary": "No specific issues identified from provided logs, or logs were empty.",
        "errors": [],
        "warnings": []
    }
    diagnoses_found = []
    
    combined_log = ""
    if error_log_content:
        combined_log += error_log_content + "\n"
    if output_log_content:
        combined_log += output_log_content

    if not combined_log.strip():
        results["warnings"].append("No log content provided for diagnosis.")
        return results

    for entry in ERROR_PATTERNS_DIAGNOSIS:
        if re.search(entry["pattern"], combined_log, re.IGNORECASE | re.MULTILINE):
            diagnoses_found.append({
                "signature": entry["signature"],
                "matched_pattern": entry["pattern"],
                "possible_causes": list(entry["possible_causes"]),
                "suggested_solutions": list(entry["suggested_solutions"])
            })

    if diagnoses_found:
        results["diagnoses"] = diagnoses_found
        results["summary"] = f"Found {len(diagnoses_found)} potential issue(s). Review diagnoses for details."
        results["success"] = True # Considered successful if any diagnosis is made
    else:
        results["summary"] = "Could not match specific known error patterns in the logs. General troubleshooting may be needed."
        results["warnings"].append("No specific known error patterns matched. The failure might be due to a less common issue or a new problem.")
        # success remains False if no specific diagnosis

    return results
import numpy as np # For math operations like log, ceil

# Cost estimation parameters (very rough, for qualitative scaling)
# These are not calibrated and serve as placeholders for a more rigorous model.
COST_BASE_FACTORS = {
    "natoms_exp": 2.0,  # Simplified exponent for N_atoms scaling (e.g., N^2 to N^3)
    "nkpts_factor": 1.0,
    "ecutwfc_exp": 1.5, # Scaling with ecutwfc (related to N_pw)
    "nbands_factor": 1.0
}

CALC_TYPE_MULTIPLIERS = {
    "scf": 1.0,
    "relax": 5.0, # Relaxation usually involves multiple SCF steps (e.g., 5-50)
    "cell-relax": 10.0, # Cell relaxation can be more expensive
    "md": 1.0, # This will be multiplied by md_nstep later
    "nscf": 0.5, # NSCF is usually faster than SCF per k-point
    "phonon": 20.0 # Phonon calculations (DFPT) can be very expensive (many perturbations)
    # 'bands' and 'dos' will be handled as scf + nscf
}

# Qualitative cost categories based on a raw score
# Thresholds are arbitrary and need calibration if a more quantitative estimate is desired.
COST_CATEGORIES = [
    {"threshold": 100, "category": "low"},
    {"threshold": 500, "category": "medium"},
    {"threshold": 2000, "category": "high"},
    {"threshold": np.inf, "category": "very_high"} # Catch-all for anything larger
]

def _estimate_nkpts(kpoints_definition: Dict[str, Any]) -> int:
    """Roughly estimates the number of k-points."""
    mode = kpoints_definition.get("mode", "").lower()
    if mode in ["monkhorst-pack", "mp", "gamma"]:
        grid = kpoints_definition.get("mp_grid", [1,1,1])
        if isinstance(grid, list) and len(grid) == 3:
            # This doesn't account for symmetry reduction, so it's an upper bound.
            return int(np.prod(grid))
    elif mode in ["line", "bandpath"]:
        nsegments = 0
        path_def = kpoints_definition.get("path_definition")
        if isinstance(path_def, str): # e.g., "G-X-L-G"
            nsegments = len(path_def.split('-')) -1
        elif isinstance(path_def, dict) and "path" in path_def: # e.g. {'path':'GX,XL'}
            nsegments = len(path_def["path"].split(','))
        
        npoints_per_segment = kpoints_definition.get("npoints_per_segment", 20)
        return nsegments * npoints_per_segment
    elif mode == "explicit":
        kpts_list = kpoints_definition.get("kpts_list", [])
        return len(kpts_list)
    return 1 # Default if unknown

async def estimate_cost_core_logic(
    structure_dict: Dict[str, Any],
    kpoints_definition: Dict[str, Any],
    input_params: Optional[Dict[str, Any]] = None,
    num_mpi_processes: Optional[int] = None # Currently for notes only
) -> Dict[str, Any]:
    """
    Provides a very rough, qualitative estimation of computational cost.
    This is NOT a precise prediction of CPU hours.
    """
    results: Dict[str, Any] = {
        "success": False,
        "estimated_cost_category": "unknown",
        "cost_factors": {},
        "raw_cost_score": 0.0, # For internal reference or future calibration
        "notes": [],
        "errors": [],
        "warnings": []
    }
    cost_factors = {}

    if not structure_dict or "symbols" not in structure_dict:
        results["errors"].append("Valid 'structure_dict' with 'symbols' is required.")
        return results
    
    num_atoms = len(structure_dict["symbols"])
    cost_factors["num_atoms"] = num_atoms
    if num_atoms == 0:
        results["errors"].append("Structure contains no atoms.")
        return results

    approx_nkpts = _estimate_nkpts(kpoints_definition)
    cost_factors["num_kpoints_approx"] = approx_nkpts
    if approx_nkpts == 0: # Should not happen if kpoints_definition is valid
        approx_nkpts = 1 
        results["warnings"].append("Could not estimate k-points, assuming 1 for cost calculation.")


    current_input_params = input_params if input_params else {}
    calculation_type = current_input_params.get("calculation", "scf").lower()
    cost_factors["calculation_type"] = calculation_type
    
    ecutwfc = float(current_input_params.get("ecutwfc", 50)) # Default 50 Ry
    cost_factors["ecutwfc_ry"] = ecutwfc

    nbands = int(current_input_params.get("nbands", num_atoms * 4)) # Rough default for nbands
    cost_factors["nbands_approx"] = nbands


    # --- Raw cost score calculation (highly empirical) ---
    raw_score = 0.0
    
    # Base scaling: N_atoms, N_kpts, Ecut (N_pw ~ Ecut^1.5 * V)
    # We simplify N_pw part by just using Ecut^exp
    base_scf_score = (
        (num_atoms ** COST_BASE_FACTORS["natoms_exp"]) *
        (approx_nkpts * COST_BASE_FACTORS["nkpts_factor"]) *
        (ecutwfc ** COST_BASE_FACTORS["ecutwfc_exp"]) *
        (nbands * COST_BASE_FACTORS["nbands_factor"])
    ) / 1e6 # Normalization factor to keep numbers manageable

    calc_multiplier = CALC_TYPE_MULTIPLIERS.get(calculation_type, 1.0)
    raw_score = base_scf_score * calc_multiplier

    if calculation_type == "md":
        md_nstep = int(current_input_params.get("md_nstep", 100))
        raw_score *= md_nstep
        cost_factors["md_nstep"] = md_nstep
    
    # For bands/DOS, it's usually SCF + NSCF. The provided params are for the main step.
    # This simple model doesn't explicitly add SCF cost for bands/DOS here,
    # assuming the multiplier for "nscf" (if calc_type is nscf) handles it.
    # A more complex model would sum costs of sub-calculations.

    results["raw_cost_score"] = round(raw_score, 2)

    # --- Determine qualitative category ---
    cost_category = "unknown"
    for cat_info in COST_CATEGORIES:
        if raw_score <= cat_info["threshold"]:
            cost_category = cat_info["category"]
            break
    results["estimated_cost_category"] = cost_category
    
    # --- Notes ---
    notes = [
        "This is a very rough qualitative cost estimation. Actual CPU time can vary significantly based on hardware, ABACUS version, compilation, parallelization efficiency, and specific system characteristics not fully captured by this model.",
        "Convergence behavior (SCF cycles, optimization steps) can greatly influence actual cost and is not predicted here.",
        f"Cost score is primarily influenced by: number of atoms ({num_atoms}), approximate k-points ({approx_nkpts}), ecutwfc ({ecutwfc} Ry), and calculation type ('{calculation_type}')."
    ]
    if num_mpi_processes and num_mpi_processes > 1:
        notes.append(f"Running with {num_mpi_processes} MPI processes may reduce wall time, but total CPU hours might increase due to communication overhead. Ideal scaling depends on the system and calculation type.")
    else:
        notes.append("Running in serial. Parallelization (MPI/OpenMP) can significantly reduce wall time for larger calculations.")

    if calculation_type in ["relax", "cell-relax"]:
        relax_nmax = current_input_params.get("relax_nmax", 100)
        notes.append(f"For '{calculation_type}', cost assumes it converges within `relax_nmax` ({relax_nmax}) steps. If more steps are needed, cost will be higher.")
    
    results["cost_factors"] = cost_factors
    results["notes"] = notes
    results["success"] = True
    
    return results
async def validate_input_core_logic(
    input_params: Dict[str, Any],
    kpoints_definition: Optional[Dict[str, Any]] = None,
    structure_dict: Optional[Dict[str, Any]] = None # For PBC checks etc.
) -> Dict[str, Any]:
    """
    Validates ABACUS input parameters for common issues and incompatibilities.
    """
    results: Dict[str, Any] = {
        "success": True, # Assume valid until an error is found
        "validation_issues": [], # List of {"level": "error"|"warning", "message": "..."}
        "errors": [], # For critical function errors, not validation errors
        "warnings": [] # For critical function warnings
    }
    issues = []

    # --- General Parameter Checks ---
    ecutwfc = input_params.get("ecutwfc")
    if ecutwfc is not None:
        try:
            ecutwfc_val = float(ecutwfc)
            if ecutwfc_val <= 5.0:
                issues.append({"level": "warning", "message": f"Energy cutoff 'ecutwfc' ({ecutwfc_val} Ry) is very low. Ensure this is intended and appropriate for your pseudopotentials."})
            if ecutwfc_val > 300.0:
                issues.append({"level": "warning", "message": f"Energy cutoff 'ecutwfc' ({ecutwfc_val} Ry) is very high. This will be computationally expensive."})
        except ValueError:
            issues.append({"level": "error", "message": f"'ecutwfc' must be a number, got: {ecutwfc}."})

    scf_thr = input_params.get("scf_thr")
    if scf_thr is not None:
        try:
            scf_thr_val = float(scf_thr)
            if scf_thr_val <= 0:
                issues.append({"level": "error", "message": f"'scf_thr' must be a positive number, got: {scf_thr_val}."})
            if scf_thr_val > 1e-2:
                 issues.append({"level": "warning", "message": f"'scf_thr' ({scf_thr_val}) is very loose. Results may not be well converged."})
        except ValueError:
            issues.append({"level": "error", "message": f"'scf_thr' must be a number, got: {scf_thr}."})
            
    mixing_beta = input_params.get("mixing_beta")
    if mixing_beta is not None:
        try:
            beta_val = float(mixing_beta)
            if not (0 < beta_val <= 1.0): # Typically, though some schemes might allow slightly > 1
                issues.append({"level": "warning", "message": f"'mixing_beta' ({beta_val}) is outside the typical range (0, 1.0]. This might lead to convergence issues."})
        except ValueError:
            issues.append({"level": "error", "message": f"'mixing_beta' must be a number, got: {mixing_beta}."})

    # --- Calculation Type Specific Checks ---
    calc_type = input_params.get("calculation", "scf").lower()

    if calc_type == "nscf":
        if input_params.get("init_chg") != "file":
            issues.append({"level": "warning", "message": "For 'nscf' calculations, 'init_chg' should typically be 'file' to read a converged charge density."})
        if input_params.get("scf_nmax", 0) > 0 or input_params.get("scf_thr") is not None:
             # ABACUS might ignore scf_nmax for nscf, but good to note if user sets it.
             pass # No strong warning/error, just an observation.

    if kpoints_definition:
        k_mode = kpoints_definition.get("mode", "").lower()
        if calc_type == "bands" or (calc_type == "nscf" and input_params.get("out_band", 0) > 0):
            if k_mode not in ["line", "bandpath"]:
                issues.append({"level": "error", "message": f"For band structure calculations (calculation='{calc_type}', out_band>0), k-point mode should be 'Line' or 'Bandpath', not '{k_mode}'."})
        
        if calc_type == "dos" or (calc_type == "nscf" and input_params.get("out_dos", 0) > 0):
            if k_mode not in ["monkhorst-pack", "mp", "gamma"]: # Gamma is a special case of MP
                 issues.append({"level": "warning", "message": f"For DOS calculations, k-point mode is typically 'Monkhorst-Pack' (or 'Gamma'), not '{k_mode}'. Ensure the chosen k-points are dense enough."})
            mp_grid = kpoints_definition.get("mp_grid")
            if mp_grid and (not isinstance(mp_grid, list) or len(mp_grid) != 3 or not all(isinstance(n, int) and n > 0 for n in mp_grid)):
                issues.append({"level": "error", "message": f"'mp_grid' for Monkhorst-Pack k-points must be a list of 3 positive integers, got: {mp_grid}."})


    # Smearing checks
    smearing_method = input_params.get("smearing_method")
    smearing_sigma = input_params.get("smearing_sigma")
    if smearing_method and smearing_method.lower() != "none":
        if smearing_sigma is None:
            issues.append({"level": "error", "message": f"'smearing_method' ({smearing_method}) is set, but 'smearing_sigma' is missing."})
        else:
            try:
                sigma_val = float(smearing_sigma)
                if sigma_val <= 0:
                    issues.append({"level": "error", "message": f"'smearing_sigma' must be positive, got: {sigma_val}."})
                if sigma_val > 0.1: # Ry
                    issues.append({"level": "warning", "message": f"'smearing_sigma' ({sigma_val} Ry) is quite large. This can affect total energy accuracy."})
            except ValueError:
                issues.append({"level": "error", "message": f"'smearing_sigma' must be a number, got: {smearing_sigma}."})

    # --- Enhanced Validation Based on PyABACUS Documentation ---
    
    # Basis type validation
    basis_type = input_params.get("basis_type", "pw").lower()
    if basis_type not in ["pw", "lcao", "lcao_in_pw"]:
        issues.append({"level": "error", "message": f"Invalid 'basis_type': {basis_type}. Must be 'pw', 'lcao', or 'lcao_in_pw'."})
    
    # KS solver validation based on basis type
    ks_solver = input_params.get("ks_solver", "cg").lower()
    valid_solvers = ["cg", "dav", "lapack", "genelpa", "scalapack_gvx", "cusolver"]
    if ks_solver not in valid_solvers:
        issues.append({"level": "error", "message": f"Invalid 'ks_solver': {ks_solver}. Must be one of {valid_solvers}."})
    
    # Basis-specific validations
    if basis_type == "lcao":
        if ks_solver in ["cg"]:
            issues.append({"level": "warning", "message": f"KS solver '{ks_solver}' may not be optimal for LCAO basis. Consider 'genelpa' or 'scalapack_gvx'."})
        
        # Check for orbital files requirement
        if not input_params.get("orbital_file_map") and not input_params.get("numerical_orbital"):
            issues.append({"level": "error", "message": "LCAO basis requires orbital files. Ensure 'orbital_file_map' is provided or 'numerical_orbital' is set."})
    
    # DFT functional validation
    dft_functional = input_params.get("dft_functional", "").upper()
    if dft_functional:
        valid_functionals = ["LDA", "PBE", "PW91", "PBE0", "HSE", "SCAN", "B3LYP"]
        if dft_functional not in valid_functionals:
            issues.append({"level": "warning", "message": f"DFT functional '{dft_functional}' may not be supported. Common choices: {valid_functionals}."})
    
    # Mixing type validation
    mixing_type = input_params.get("mixing_type", "pulay").lower()
    valid_mixing = ["plain", "pulay", "broyden", "pulay-kerker"]
    if mixing_type not in valid_mixing:
        issues.append({"level": "error", "message": f"Invalid 'mixing_type': {mixing_type}. Must be one of {valid_mixing}."})
    
    # Force and stress calculation validation
    cal_force = input_params.get("cal_force", 0)
    cal_stress = input_params.get("cal_stress", 0)
    if calc_type in ["relax", "cell-relax", "md"]:
        if not cal_force:
            issues.append({"level": "error", "message": f"Calculation type '{calc_type}' requires 'cal_force=1' for force calculation."})
        if calc_type == "cell-relax" and not cal_stress:
            issues.append({"level": "error", "message": "Cell relaxation requires 'cal_stress=1' for stress calculation."})
    
    # MD-specific validations
    if calc_type == "md":
        md_nstep = input_params.get("md_nstep")
        if md_nstep is None:
            issues.append({"level": "error", "message": "MD calculation requires 'md_nstep' parameter."})
        elif not isinstance(md_nstep, int) or md_nstep <= 0:
            issues.append({"level": "error", "message": f"'md_nstep' must be a positive integer, got: {md_nstep}."})
        
        md_dt = input_params.get("md_dt")
        if md_dt is None:
            issues.append({"level": "error", "message": "MD calculation requires 'md_dt' (time step) parameter."})
        else:
            try:
                dt_val = float(md_dt)
                if dt_val <= 0:
                    issues.append({"level": "error", "message": f"'md_dt' must be positive, got: {dt_val}."})
                elif dt_val > 5.0:
                    issues.append({"level": "warning", "message": f"'md_dt' ({dt_val} fs) is quite large. Consider smaller time step for stability."})
            except ValueError:
                issues.append({"level": "error", "message": f"'md_dt' must be a number, got: {md_dt}."})
        
        md_thermostat = input_params.get("md_thermostat", "").lower()
        if md_thermostat and md_thermostat not in ["nhc", "anderson", "berendsen", "langevin"]:
            issues.append({"level": "warning", "message": f"MD thermostat '{md_thermostat}' may not be supported. Common choices: nhc, anderson, berendsen, langevin."})
    
    # Band structure specific validations
    if calc_type == "nscf" and input_params.get("out_band", 0) > 0:
        nbands = input_params.get("nbands")
        if nbands and nbands != "auto":
            try:
                nbands_val = int(nbands)
                if nbands_val <= 0:
                    issues.append({"level": "error", "message": f"'nbands' must be positive or 'auto', got: {nbands_val}."})
            except ValueError:
                if nbands != "auto":
                    issues.append({"level": "error", "message": f"'nbands' must be an integer or 'auto', got: {nbands}."})
    
    # DOS specific validations
    if calc_type == "nscf" and input_params.get("out_dos", 0) > 0:
        dos_emin = input_params.get("dos_emin")
        dos_emax = input_params.get("dos_emax")
        if dos_emin is not None and dos_emax is not None:
            try:
                emin_val = float(dos_emin)
                emax_val = float(dos_emax)
                if emin_val >= emax_val:
                    issues.append({"level": "error", "message": f"'dos_emin' ({emin_val}) must be less than 'dos_emax' ({emax_val})."})
            except ValueError:
                issues.append({"level": "error", "message": "DOS energy range parameters must be numbers."})
    
    # PyABACUS-specific parameter validation
    if input_params.get("use_pyabacus_interface"):
        # Validate parameters that are important for PyABACUS integration
        if basis_type == "lcao":
            issues.append({"level": "info", "message": "PyABACUS ModuleNAO can be used for numerical atomic orbital analysis with LCAO basis."})
        
        if input_params.get("out_mat_hs", 0) > 0:
            issues.append({"level": "info", "message": "Hamiltonian/overlap matrix output enabled - useful for PyABACUS hsolver module analysis."})
    
    # Structure-dependent validations
    if structure_dict:
        try:
            # Check PBC consistency
            pbc = structure_dict.get("pbc", [True, True, True])
            if not any(pbc) and calc_type in ["scf", "relax", "cell-relax"]:
                issues.append({"level": "warning", "message": "Non-periodic system detected. Ensure vacuum space is sufficient and consider gamma-point only k-sampling."})
            
            # Check for reasonable cell dimensions
            cell = structure_dict.get("cell")
            if cell:
                import numpy as np
                cell_array = np.array(cell)
                cell_lengths = np.linalg.norm(cell_array, axis=1)
                if any(length < 5.0 for length in cell_lengths):
                    issues.append({"level": "warning", "message": "Very small cell dimensions detected. Ensure this is intended and consider vacuum effects."})
                if any(length > 50.0 for length in cell_lengths):
                    issues.append({"level": "warning", "message": "Very large cell dimensions detected. This will be computationally expensive."})
            
            # Check number of atoms vs computational cost
            positions = structure_dict.get("positions", [])
            natoms = len(positions)
            if natoms > 100:
                issues.append({"level": "warning", "message": f"Large system with {natoms} atoms. Consider computational cost and memory requirements."})
            
        except Exception as e:
            issues.append({"level": "warning", "message": f"Could not validate structure-dependent parameters: {str(e)}"})
    
    # K-points validation enhancement
    if kpoints_definition:
        k_mode = kpoints_definition.get("mode", "").lower()
        
        if k_mode in ["monkhorst-pack", "mp"]:
            mp_grid = kpoints_definition.get("mp_grid") or kpoints_definition.get("size")
            if mp_grid:
                try:
                    total_kpts = 1
                    for k in mp_grid:
                        total_kpts *= int(k)
                    
                    if total_kpts > 1000:
                        issues.append({"level": "warning", "message": f"Very dense k-point grid ({total_kpts} points). This will be computationally expensive."})
                    elif total_kpts < 8 and calc_type in ["scf", "relax"]:
                        issues.append({"level": "warning", "message": f"Sparse k-point grid ({total_kpts} points). Results may not be well converged."})
                        
                except (ValueError, TypeError):
                    issues.append({"level": "error", "message": "K-point grid values must be integers."})
        
        elif k_mode in ["line", "bandpath"]:
            npoints = kpoints_definition.get("npoints_per_segment")
            if npoints and npoints < 10:
                issues.append({"level": "warning", "message": f"Few k-points per segment ({npoints}). Band structure may not be smooth."})
    
    # Memory and performance warnings
    if ecutwfc and kpoints_definition:
        try:
            ecutwfc_val = float(ecutwfc)
            mp_grid = kpoints_definition.get("mp_grid") or kpoints_definition.get("size", [1, 1, 1])
            total_kpts = 1
            for k in mp_grid:
                total_kpts *= int(k)
            
            # Rough memory estimate (very approximate)
            memory_factor = ecutwfc_val * total_kpts
            if memory_factor > 50000:  # Arbitrary threshold
                issues.append({"level": "warning", "message": "High memory usage expected due to large ecutwfc and k-point grid combination."})
                
        except (ValueError, TypeError):
            pass  # Skip if values can't be converted

    # Additional smearing validation
    if smearing_sigma is not None and (not smearing_method or smearing_method.lower() == "none"):
        issues.append({"level": "warning", "message": "'smearing_sigma' is set, but 'smearing_method' is not, or is 'none'. Sigma will likely be ignored."})

    # --- Finalize ---
    results["validation_issues"] = issues
    for issue in issues:
        if issue["level"] == "error":
            results["success"] = False # At least one error makes overall validation fail
            break
            # No break, collect all errors and warnings. Success is based on presence of errors.
    
    # Re-evaluate success based on collected issues
    if any(issue["level"] == "error" for issue in issues):
        results["success"] = False

    # Log validation result
    log_validation_result("input_parameters", results["success"], issues)

    return results