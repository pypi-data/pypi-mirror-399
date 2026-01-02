# src/server.py
import sys
import os
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastmcp import FastMCP
from typing import Dict, Any, Optional, List

# 从我们创建的模块导入核心逻辑函数
from src.tools.structure_management import (
    create_ase_structure,
    validate_ase_structure_dict,
    convert_ase_structure_format
)
from src.tools.calculation_execution import (
    run_scf_core_logic,
    run_optimization_core_logic,
    run_md_core_logic,
    run_phonon_dfpt_preparation_core_logic
)
# 新增导入 property_analysis 模块的函数
from src.tools.property_analysis import (
    calculate_band_structure_core_logic,
    calculate_dos_core_logic,
    calculate_charge_density_core_logic,
    analyze_electronic_properties_core_logic
)
from src.tools.intelligent_assistant import (
    suggest_parameters_core_logic,
    diagnose_failure_core_logic,
    estimate_cost_core_logic,
    validate_input_core_logic # <-- 添加此行
)
# 新增导入 task_management 模块的函数
from src.tools.task_management import (
    get_calculation_status_core_logic,
    list_recent_calculations_core_logic,
    get_calculation_results_core_logic,
    monitor_calculation_core_logic,
    cancel_calculation_core_logic
)

# 导入MCP Resources和Prompts
from src.resources import resource_provider
from src.prompts import prompt_provider

# 导入日志记录
from src.logging_config import (
    log_resource_access, log_prompt_usage, log_user_action,
    log_validation_result, log_app_event
)

app = FastMCP(name="abacus-mcp-server", version="0.1.0")

# Log server startup
log_app_event("ABACUS MCP Server starting up", "info", version="0.1.0")

# === MCP RESOURCES ===

@app.resource("abacus://calculations/{task_id}/results")
async def get_calculation_results_resource(task_id: str) -> str:
    """Get calculation results for a specific task."""
    log_resource_access(f"abacus://calculations/{task_id}/results")
    results = await resource_provider.get_calculation_results(task_id)
    import json
    return json.dumps(results, indent=2)

@app.resource("abacus://calculations/{task_id}/logs")
async def get_calculation_logs_resource(task_id: str) -> str:
    """Get calculation logs for a specific task."""
    log_resource_access(f"abacus://calculations/{task_id}/logs")
    logs = await resource_provider.get_calculation_logs(task_id)
    import json
    return json.dumps(logs, indent=2)

@app.resource("abacus://system/status")
async def get_system_status_resource() -> str:
    """Get current system status and configuration."""
    log_resource_access("abacus://system/status")
    status = await resource_provider.get_system_status()
    import json
    return json.dumps(status, indent=2)

@app.resource("abacus://docs/{topic}")
async def get_documentation_resource(topic: str) -> str:
    """Get documentation for specific topics."""
    log_resource_access(f"abacus://docs/{topic}")
    docs = await resource_provider.get_documentation(topic)
    import json
    return json.dumps(docs, indent=2)

@app.resource("abacus://examples/{example_type}")
async def get_examples_resource(example_type: str) -> str:
    """Get example configurations and scripts."""
    log_resource_access(f"abacus://examples/{example_type}")
    examples = await resource_provider.get_examples(example_type)
    import json
    return json.dumps(examples, indent=2)

# === MCP PROMPTS ===

@app.prompt("setup_scf_calculation")
async def setup_scf_calculation_prompt(
    structure_info: str,
    accuracy_level: str = "medium",
    calculation_purpose: str = "ground_state"
) -> str:
    """Guide user through setting up a self-consistent field calculation."""
    log_prompt_usage("setup_scf_calculation", parameters={
        "structure_info": structure_info,
        "accuracy_level": accuracy_level,
        "calculation_purpose": calculation_purpose
    })
    prompt_data = prompt_provider.get_prompt("setup_scf_calculation")
    return prompt_data["template"].format(
        structure_info=structure_info,
        accuracy_level=accuracy_level,
        calculation_purpose=calculation_purpose
    )

@app.prompt("optimize_structure")
async def optimize_structure_prompt(
    optimization_type: str,
    initial_structure: str,
    constraints: str = "none"
) -> str:
    """Guide user through geometry and cell optimization."""
    prompt_data = prompt_provider.get_prompt("optimize_structure")
    return prompt_data["template"].format(
        optimization_type=optimization_type,
        initial_structure=initial_structure,
        constraints=constraints
    )

@app.prompt("calculate_band_structure")
async def calculate_band_structure_prompt(
    crystal_system: str,
    material_type: str = "unknown"
) -> str:
    """Guide user through band structure calculations."""
    prompt_data = prompt_provider.get_prompt("calculate_band_structure")
    return prompt_data["template"].format(
        crystal_system=crystal_system,
        material_type=material_type
    )

@app.prompt("run_molecular_dynamics")
async def run_molecular_dynamics_prompt(
    system_size: str,
    temperature: str,
    simulation_time: str = "1 ps"
) -> str:
    """Guide user through MD simulation setup."""
    prompt_data = prompt_provider.get_prompt("run_molecular_dynamics")
    return prompt_data["template"].format(
        system_size=system_size,
        temperature=temperature,
        simulation_time=simulation_time
    )

@app.prompt("troubleshoot_convergence")
async def troubleshoot_convergence_prompt(
    calculation_type: str,
    error_symptoms: str
) -> str:
    """Help diagnose and fix convergence problems."""
    prompt_data = prompt_provider.get_prompt("troubleshoot_convergence")
    return prompt_data["template"].format(
        calculation_type=calculation_type,
        error_symptoms=error_symptoms
    )

@app.prompt("analyze_results")
async def analyze_results_prompt(
    calculation_type: str,
    analysis_goals: str
) -> str:
    """Guide user through result analysis and interpretation."""
    prompt_data = prompt_provider.get_prompt("analyze_results")
    return prompt_data["template"].format(
        calculation_type=calculation_type,
        analysis_goals=analysis_goals
    )

@app.prompt("setup_pyabacus_workflow")
async def setup_pyabacus_workflow_prompt(
    workflow_type: str,
    python_experience: str = "intermediate"
) -> str:
    """Guide user through PyABACUS Python interface usage."""
    prompt_data = prompt_provider.get_prompt("setup_pyabacus_workflow")
    return prompt_data["template"].format(
        workflow_type=workflow_type,
        python_experience=python_experience
    )

@app.tool()
async def ping() -> str:
    """A simple ping tool to check if the MCP server is responsive."""
    return "pong"

# --- create_structure tool ---
CREATE_STRUCTURE_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "formula_or_data": {"type": "string", "description": "Chemical formula (e.g., 'H2O') or structure data string (CIF, XYZ)."},
        "input_format": {"type": "string", "enum": ["formula", "cif", "xyz"], "description": "Format of input_data."},
        "lattice_type": {"type": ["string", "null"], "description": "(Optional, legacy) Hint for lattice type if input_format is 'formula'. Prefer 'crystalstructure'.", "default": None},
        "a": {"type": ["number", "null"], "description": "(Optional) Lattice constant 'a' for formula-based crystal creation.", "default": None},
        "crystalstructure": {"type": ["string", "null"], "description": "(Optional) Crystal structure for formula-based creation (e.g., 'fcc', 'diamond').", "default": None}
    },
    "required": ["formula_or_data", "input_format"]
}
CREATE_STRUCTURE_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "data": {"type": ["object", "null"], "description": "Serialized ASE Atoms object if successful."}, # Simplified for brevity, actual properties in core logic
        "warnings": {"type": "array", "items": {"type": "string"}},
        "message": {"type": "string", "description": "Success message."},
        "error": {"type": "string", "description": "Error message on failure."}
    },
    "required": ["success", "warnings"]
}
@app.tool(name="create_structure", description="Create atomic/crystal structure from formula, CIF, or XYZ data.", annotations={"readOnlyHint": True, "idempotentHint": True})
async def create_structure_tool(formula_or_data: str, input_format: str, lattice_type: Optional[str] = None, a: Optional[float] = None, crystalstructure: Optional[str] = None) -> Dict[str, Any]:
    return await create_ase_structure(formula_or_data=formula_or_data, input_format=input_format, lattice_type=lattice_type, a=a, crystalstructure=crystalstructure)

# --- validate_structure tool ---
VALIDATE_STRUCTURE_INPUT_SCHEMA = {
    "type": "object", 
    "properties": {"structure_dict": {"type": "object", "description": "Dictionary representation of an ASE Atoms object (typically from create_structure's 'data' field)."}}, 
    "required": ["structure_dict"]
}
VALIDATE_STRUCTURE_OUTPUT_SCHEMA = {
    "type": "object", "properties": {"success": {"type": "boolean"}, "messages": {"type": "array", "items": {"type": "string"}}, "warnings": {"type": "array", "items": {"type": "string"}}}, "required": ["success", "messages", "warnings"]
}
@app.tool(name="validate_structure", description="Validate the reasonability of an atomic structure.", annotations={"readOnlyHint": True, "idempotentHint": True})
async def validate_structure_tool(structure_dict: Dict[str, Any]) -> Dict[str, Any]:
    return validate_ase_structure_dict(structure_dict)

# --- convert_structure tool ---
CONVERT_STRUCTURE_INPUT_SCHEMA = {
    "type": "object", "properties": {"input_structure_data": {"type": "string"}, "input_format": {"type": "string"}, "output_format": {"type": "string"}}, "required": ["input_structure_data", "input_format", "output_format"]
}
CONVERT_STRUCTURE_OUTPUT_SCHEMA = {
    "type": "object", "properties": {"success": {"type": "boolean"}, "data": {"type": ["object", "null"], "properties": {"output_structure_data": {"type": "string"}, "output_format": {"type": "string"}, "original_input_format": {"type": "string"}}}, "message": {"type": "string"}, "error": {"type": "string"}, "warnings": {"type": "array", "items": {"type": "string"}}}, "required": ["success", "warnings"]
}
@app.tool(name="convert_structure", description="Convert atomic structure data between formats.", annotations={"readOnlyHint": True, "idempotentHint": True})
async def convert_structure_tool(input_structure_data: str, input_format: str, output_format: str) -> Dict[str, Any]:
    return await convert_ase_structure_format(input_structure_data=input_structure_data, input_format=input_format, output_format=output_format)

# --- Base Schemas for Calculation Tools (to be reused) ---
SERIALIZED_ATOMS_SCHEMA = CREATE_STRUCTURE_OUTPUT_SCHEMA["properties"]["data"]

BASE_CALCULATION_INPUT_PROPERTIES = {
    "structure_dict": SERIALIZED_ATOMS_SCHEMA,
    "input_params": {"type": "object", "description": "ABACUS INPUT file parameters.", "default": {}},
    "kpoints_definition": {
        "type": "object", 
        "description": "K-point generation definition.", 
        "properties": {
            "mode": {"type": "string", "enum": ["Monkhorst-Pack", "Line", "Explicit"], "default": "Monkhorst-Pack"}, 
            "size": {"type": "array", "items": {"type": "integer"}, "minItems": 3, "maxItems": 3, "description": "For MP: [nx,ny,nz]"}, 
            "shift": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3, "default": [0,0,0], "description": "For MP: [sx,sy,sz]"}, 
            "path_definition": {"type": ["string", "object"], "description": "For Line: 'GXL' or {'path':'GX,XL','special_points':{...}}"}, 
            "npoints_per_segment": {"type": "integer", "description": "For Line: points per segment"}, 
            "kpts_list": {"type": "array", "items": {"type": "array", "items": {"type": "number"}, "minItems": 4, "maxItems": 4}, "description": "For Explicit: [[kx,ky,kz,w], ...]"}
        }, 
        "required": ["mode"]
    },
    "pseudo_potential_map": {"type": "object", "description": "Element symbol to pseudopotential filename map. E.g. {'Si': 'Si.UPF'}", "additionalProperties": {"type": "string"}},
    "orbital_file_map": {"type": ["object", "null"], "description": "(Optional) Element symbol to orbital filename map. E.g. {'Si': 'Si.orb'}", "additionalProperties": {"type": "string"}, "default": None},
    "abacus_command": {"type": "string", "description": "(Optional) ABACUS execution command.", "default": "abacus"},
    "pseudo_base_path": {"type": "string", "description": "(Optional) Base path for pseudopotentials.", "default": "./pseudos/"},
    "orbital_base_path": {"type": ["string", "null"], "description": "(Optional) Base path for orbital files.", "default": None}
}
BASE_CALCULATION_REQUIRED_FIELDS = ["structure_dict", "input_params", "kpoints_definition", "pseudo_potential_map"]

# --- run_scf tool ---
RUN_SCF_INPUT_SCHEMA = {"type": "object", "properties": BASE_CALCULATION_INPUT_PROPERTIES, "required": BASE_CALCULATION_REQUIRED_FIELDS}
RUN_SCF_OUTPUT_SCHEMA = {
    "type": "object", "properties": {"success": {"type": "boolean"}, "data": {"type": ["object", "null"], "properties": {"converged": {"type": "boolean"}, "total_energy_ry": {"type": ["number", "null"]}, "total_energy_ev": {"type": ["number", "null"]}, "fermi_energy_ry": {"type": ["number", "null"]}, "fermi_energy_ev": {"type": ["number", "null"]}, "scf_iterations": {"type": ["integer", "null"]}, "warnings": {"type": "array", "items": {"type": "string"}}, "errors": {"type": "array", "items": {"type": "string"}}}}, "logs": {"type": "object"}, "errors": {"type": "array", "items": {"type": "string"}}, "warnings": {"type": "array", "items": {"type": "string"}}}, "required": ["success", "data", "logs", "errors", "warnings"]
}
@app.tool(name="run_scf", description="Run ABACUS Self-Consistent Field (SCF) calculation.", annotations={"idempotentHint": False})
async def run_scf_tool(structure_dict: Dict[str, Any], input_params: Dict[str, Any], kpoints_definition: Dict[str, Any], pseudo_potential_map: Dict[str, str], orbital_file_map: Optional[Dict[str, str]] = None, abacus_command: str = "abacus", pseudo_base_path: str = "./pseudos/", orbital_base_path: Optional[str] = None) -> Dict[str, Any]:
    if orbital_file_map and orbital_base_path is None: orbital_base_path = pseudo_base_path
    return await run_scf_core_logic(structure_dict=structure_dict, input_params=input_params, kpoints_definition=kpoints_definition, pseudo_potential_map=pseudo_potential_map, orbital_file_map=orbital_file_map, abacus_command=abacus_command, pseudo_base_path=pseudo_base_path, orbital_base_path=orbital_base_path)

# --- run_optimization tool ---
RUN_OPTIMIZATION_INPUT_SCHEMA_PROPS = BASE_CALCULATION_INPUT_PROPERTIES.copy()
RUN_OPTIMIZATION_INPUT_SCHEMA_PROPS["input_params"] = {"type": "object", "description": "ABACUS INPUT parameters. Must include 'calculation': 'relax' or 'cell-relax'.", "default": {"calculation": "relax"}}
RUN_OPTIMIZATION_INPUT_SCHEMA = {"type": "object", "properties": RUN_OPTIMIZATION_INPUT_SCHEMA_PROPS, "required": BASE_CALCULATION_REQUIRED_FIELDS}
RUN_OPTIMIZATION_OUTPUT_SCHEMA = {
    "type": "object", "properties": {"success": {"type": "boolean"}, "data": {"type": ["object", "null"], "properties": {"converged": {"type": "boolean"}, "final_total_energy_ry": {"type": ["number", "null"]}, "final_total_energy_ev": {"type": ["number", "null"]}, "final_fermi_energy_ry": {"type": ["number", "null"]}, "final_fermi_energy_ev": {"type": ["number", "null"]}, "optimization_steps": {"type": ["integer", "null"]}, "final_structure_dict": SERIALIZED_ATOMS_SCHEMA, "max_force": {"type": ["number", "null"]}, "total_force": {"type": ["number", "null"]}, "stress_tensor_kbar": {"type": ["array", "null"], "items": {"type": "array", "items": {"type": "number"}}}, "warnings": {"type": "array", "items": {"type": "string"}}, "errors": {"type": "array", "items": {"type": "string"}}}}, "logs": RUN_SCF_OUTPUT_SCHEMA["properties"]["logs"], "errors": {"type": "array", "items": {"type": "string"}}, "warnings": {"type": "array", "items": {"type": "string"}}}, "required": ["success", "data", "logs", "errors", "warnings"]
}
@app.tool(name="run_optimization", description="Run ABACUS geometry optimization.", annotations={"idempotentHint": False})
async def run_optimization_tool(structure_dict: Dict[str, Any], input_params: Dict[str, Any], kpoints_definition: Dict[str, Any], pseudo_potential_map: Dict[str, str], orbital_file_map: Optional[Dict[str, str]] = None, abacus_command: str = "abacus", pseudo_base_path: str = "./pseudos/", orbital_base_path: Optional[str] = None) -> Dict[str, Any]:
    if orbital_file_map and orbital_base_path is None: orbital_base_path = pseudo_base_path
    return await run_optimization_core_logic(structure_dict=structure_dict, input_params=input_params, kpoints_definition=kpoints_definition, pseudo_potential_map=pseudo_potential_map, orbital_file_map=orbital_file_map, abacus_command=abacus_command, pseudo_base_path=pseudo_base_path, orbital_base_path=orbital_base_path)

# --- optimize_structure tool (alias) ---
@app.tool(name="optimize_structure", description="Alias for run_optimization tool. Performs geometry optimization.", annotations={"idempotentHint": False})
async def optimize_structure_tool(structure_dict: Dict[str, Any], input_params: Dict[str, Any], kpoints_definition: Dict[str, Any], pseudo_potential_map: Dict[str, str], orbital_file_map: Optional[Dict[str, str]] = None, abacus_command: str = "abacus", pseudo_base_path: str = "./pseudos/", orbital_base_path: Optional[str] = None) -> Dict[str, Any]:
    if orbital_file_map and orbital_base_path is None: orbital_base_path = pseudo_base_path
    current_input_params = input_params.copy()
    current_input_params.setdefault("calculation", "relax")
    return await run_optimization_core_logic(structure_dict=structure_dict, input_params=current_input_params, kpoints_definition=kpoints_definition, pseudo_potential_map=pseudo_potential_map, orbital_file_map=orbital_file_map, abacus_command=abacus_command, pseudo_base_path=pseudo_base_path, orbital_base_path=orbital_base_path)

# --- run_md tool ---
RUN_MD_INPUT_SCHEMA_PROPS = BASE_CALCULATION_INPUT_PROPERTIES.copy()
RUN_MD_INPUT_SCHEMA_PROPS["input_params"] = {"type": "object", "description": "ABACUS INPUT parameters for MD. Must include 'calculation': 'md', 'md_nstep', etc.", "default": {"calculation": "md", "md_nstep": 100, "md_dt": 1.0, "md_tfirst": 300}}
RUN_MD_INPUT_SCHEMA = {"type": "object", "properties": RUN_MD_INPUT_SCHEMA_PROPS, "required": BASE_CALCULATION_REQUIRED_FIELDS}
RUN_MD_OUTPUT_SCHEMA = {
    "type": "object", "properties": {"success": {"type": "boolean"}, "data": {"type": ["object", "null"], "properties": {"completed_all_steps": {"type": "boolean"}, "final_energy_ry": {"type": ["number", "null"]}, "final_energy_ev": {"type": ["number", "null"]}, "average_temperature_k": {"type": ["number", "null"]}, "average_pressure_kbar": {"type": ["number", "null"]}, "total_md_steps_performed": {"type": ["integer", "null"]}, "trajectory_file_path": {"type": ["string", "null"]}, "warnings": {"type": "array", "items": {"type": "string"}}, "errors": {"type": "array", "items": {"type": "string"}}}}, "logs": RUN_SCF_OUTPUT_SCHEMA["properties"]["logs"], "errors": {"type": "array", "items": {"type": "string"}}, "warnings": {"type": "array", "items": {"type": "string"}}}, "required": ["success", "data", "logs", "errors", "warnings"]
}
@app.tool(name="run_md", description="Run ABACUS Molecular Dynamics (MD) simulation.", annotations={"idempotentHint": False})
async def run_md_tool(structure_dict: Dict[str, Any], input_params: Dict[str, Any], kpoints_definition: Dict[str, Any], pseudo_potential_map: Dict[str, str], orbital_file_map: Optional[Dict[str, str]] = None, abacus_command: str = "abacus", pseudo_base_path: str = "./pseudos/", orbital_base_path: Optional[str] = None) -> Dict[str, Any]:
    if orbital_file_map and orbital_base_path is None: orbital_base_path = pseudo_base_path
    current_input_params = input_params.copy()
    current_input_params["calculation"] = "md"
    return await run_md_core_logic(structure_dict=structure_dict, input_params=current_input_params, kpoints_definition=kpoints_definition, pseudo_potential_map=pseudo_potential_map, orbital_file_map=orbital_file_map, abacus_command=abacus_command, pseudo_base_path=pseudo_base_path, orbital_base_path=orbital_base_path)

# --- run_phonon_preparation tool ---
RUN_PHONON_PREPARATION_INPUT_SCHEMA_PROPS = BASE_CALCULATION_INPUT_PROPERTIES.copy()
RUN_PHONON_PREPARATION_INPUT_SCHEMA_PROPS["input_params"] = {"type": "object", "description": "ABACUS INPUT parameters for DFPT phonon. 'calculation' will be set to 'phonon'.", "default": {}}
_phonon_kpts_def = RUN_PHONON_PREPARATION_INPUT_SCHEMA_PROPS["kpoints_definition"]["properties"].copy()
_phonon_kpts_def["mode"] = {"type": "string", "enum": ["Monkhorst-Pack"], "default": "Monkhorst-Pack"}
RUN_PHONON_PREPARATION_INPUT_SCHEMA_PROPS["kpoints_definition"] = {
    "type": "object",
    "description": "K-point generation for DFPT (Monkhorst-Pack grid).",
    "properties": _phonon_kpts_def,
    "required": ["mode", "size"] 
}
RUN_PHONON_PREPARATION_INPUT_SCHEMA = {"type": "object", "properties": RUN_PHONON_PREPARATION_INPUT_SCHEMA_PROPS, "required": BASE_CALCULATION_REQUIRED_FIELDS}
RUN_PHONON_PREPARATION_OUTPUT_SCHEMA = {
    "type": "object", "properties": {"success": {"type": "boolean"}, "data": {"type": ["object", "null"], "properties": {"input_file_content": {"type": "string"}, "stru_file_content": {"type": "string"}, "kpt_file_content": {"type": "string"}, "message": {"type": "string"}}}, "logs": {"type": "object"}, "errors": {"type": "array", "items": {"type": "string"}}, "warnings": {"type": "array", "items": {"type": "string"}}}, "required": ["success", "data", "logs", "errors", "warnings"]
}
@app.tool(name="run_phonon_preparation", description="Prepare input files for ABACUS DFPT phonon calculation.", annotations={"readOnlyHint": True, "idempotentHint": True})
async def run_phonon_preparation_tool(structure_dict: Dict[str, Any], input_params: Dict[str, Any], kpoints_definition: Dict[str, Any], pseudo_potential_map: Dict[str, str], orbital_file_map: Optional[Dict[str, str]] = None, pseudo_base_path: str = "./pseudos/", orbital_base_path: Optional[str] = None) -> Dict[str, Any]:
    if orbital_file_map and orbital_base_path is None: orbital_base_path = pseudo_base_path
    return await run_phonon_dfpt_preparation_core_logic(structure_dict=structure_dict, input_params=input_params, kpoints_definition=kpoints_definition, pseudo_potential_map=pseudo_potential_map, orbital_file_map=orbital_file_map, pseudo_base_path=pseudo_base_path, orbital_base_path=orbital_base_path)

# --- calculate_band_structure tool ---
CALCULATE_BAND_STRUCTURE_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "structure_dict": SERIALIZED_ATOMS_SCHEMA,
        "scf_input_params": {"type": "object", "description": "Parameters for the initial SCF run.", "default": {}},
        "nscf_input_params_overrides": {"type": "object", "description": "Parameters specific to or overriding for NSCF band run.", "default": {}},
        "kpoints_definition_scf": BASE_CALCULATION_INPUT_PROPERTIES["kpoints_definition"],
        "kpoints_definition_bandpath": {
            "type": "object", "description": "K-points definition for band path (must be 'Line' mode).",
            "properties": {
                "mode": {"type": "string", "enum": ["Line", "Bandpath"]},
                "path_definition": {"type": ["string", "object"]},
                "npoints_per_segment": {"type": "integer"}
            },
            "required": ["mode", "path_definition", "npoints_per_segment"]
        },
        "pseudo_potential_map": BASE_CALCULATION_INPUT_PROPERTIES["pseudo_potential_map"],
        "orbital_file_map": BASE_CALCULATION_INPUT_PROPERTIES["orbital_file_map"],
        "abacus_command": BASE_CALCULATION_INPUT_PROPERTIES["abacus_command"],
        "pseudo_base_path": BASE_CALCULATION_INPUT_PROPERTIES["pseudo_base_path"],
        "orbital_base_path": BASE_CALCULATION_INPUT_PROPERTIES["orbital_base_path"]
    },
    "required": ["structure_dict", "scf_input_params", "nscf_input_params_overrides", "kpoints_definition_scf", "kpoints_definition_bandpath", "pseudo_potential_map"]
}
CALCULATE_BAND_STRUCTURE_OUTPUT_SCHEMA = {
    "type": "object", "properties": {"success": {"type": "boolean"}, "data": {"type": ["object", "null"], "properties": {"k_points_path": {"type": "array", "items": {"type": "array"}}, "eigenvalues": {"type": "array", "items": {"type": "array"}}, "fermi_energy_ry": {"type": ["number", "null"]}, "fermi_energy_ev": {"type": ["number", "null"]}, "message": {"type": "string"}}}, "logs": {"type": "object"}, "errors": {"type": "array", "items": {"type": "string"}}, "warnings": {"type": "array", "items": {"type": "string"}}}, "required": ["success", "data", "logs", "errors", "warnings"]
}
@app.tool(name="calculate_band_structure", description="Calculate ABACUS band structure.", annotations={"idempotentHint": False})
async def calculate_band_structure_tool(structure_dict: Dict[str, Any], scf_input_params: Dict[str, Any], nscf_input_params_overrides: Dict[str, Any], kpoints_definition_scf: Dict[str, Any], kpoints_definition_bandpath: Dict[str, Any], pseudo_potential_map: Dict[str, str], orbital_file_map: Optional[Dict[str, str]] = None, abacus_command: str = "abacus", pseudo_base_path: str = "./pseudos/", orbital_base_path: Optional[str] = None) -> Dict[str, Any]:
    if orbital_file_map and orbital_base_path is None: orbital_base_path = pseudo_base_path
    return await calculate_band_structure_core_logic(structure_dict=structure_dict, scf_input_params=scf_input_params, nscf_input_params_overrides=nscf_input_params_overrides, kpoints_definition_scf=kpoints_definition_scf, kpoints_definition_bandpath=kpoints_definition_bandpath, pseudo_potential_map=pseudo_potential_map, orbital_file_map=orbital_file_map, abacus_command=abacus_command, pseudo_base_path=pseudo_base_path, orbital_base_path=orbital_base_path)
# --- calculate_dos tool ---
CALCULATE_DOS_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "structure_dict": SERIALIZED_ATOMS_SCHEMA,
        "scf_input_params": {"type": "object", "description": "Parameters for the initial SCF run.", "default": {}},
        "nscf_input_params_overrides": {"type": "object", "description": "Parameters specific to or overriding for NSCF DOS run (e.g., out_dos, dos_emin, dos_emax, dos_deltae, dos_sigma).", "default": {}},
        "kpoints_definition_scf": BASE_CALCULATION_INPUT_PROPERTIES["kpoints_definition"],
        "kpoints_definition_dos": {
            "type": "object", 
            "description": "K-points definition for NSCF DOS run (typically a denser Monkhorst-Pack grid).",
            "properties": {
                "mode": {"type": "string", "enum": ["Monkhorst-Pack", "Gamma", "MP"], "default": "Monkhorst-Pack"}, # Allow "MP" as alias
                "mp_grid": {"type": "array", "items": {"type": "integer"}, "minItems": 3, "maxItems": 3, "description": "For MP: [nx,ny,nz]"},
                "mp_offset": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3, "default": [0,0,0], "description": "For MP: [sx,sy,sz]"},
                "gamma_center": {"type": "boolean", "default": True, "description": "For MP: True if gamma centered, False otherwise."}
                # Explicit k-points could be added if a common use case for DOS arises
            },
            "required": ["mode", "mp_grid"] # mp_grid is essential for MP mode
        },
        "pseudo_potential_map": BASE_CALCULATION_INPUT_PROPERTIES["pseudo_potential_map"],
        "orbital_file_map": BASE_CALCULATION_INPUT_PROPERTIES["orbital_file_map"],
        "abacus_command": BASE_CALCULATION_INPUT_PROPERTIES["abacus_command"],
        "pseudo_base_path": BASE_CALCULATION_INPUT_PROPERTIES["pseudo_base_path"],
        "orbital_base_path": BASE_CALCULATION_INPUT_PROPERTIES["orbital_base_path"]
    },
    "required": ["structure_dict", "scf_input_params", "nscf_input_params_overrides", "kpoints_definition_scf", "kpoints_definition_dos", "pseudo_potential_map"]
}
CALCULATE_DOS_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "data": {
            "type": ["object", "null"],
            "properties": {
                "dos_data": {
                    "type": "object",
                    "description": "Parsed DOS data. Keys might include 'energy_ev', 'total_dos', 'total_dos_spin_up', 'total_dos_spin_down', 'pdos_data' (if available).",
                    # Actual structure depends on parse_abacus_dos_output
                },
                "fermi_energy_ry": {"type": ["number", "null"]},
                "fermi_energy_ev": {"type": ["number", "null"]},
                "nelect": {"type": ["number", "null"], "description": "Number of electrons from SCF calculation."},
                "spin_channels_present": {"type": "array", "items": {"type": "string"}, "description": "Indicates if spin-polarized data ('spin_up', 'spin_down') or 'non_spin_polarized' DOS is present."},
                "message": {"type": "string"}
            }
        },
        "logs": {"type": "object"}, # Similar to SCF/Band logs
        "errors": {"type": "array", "items": {"type": "string"}},
        "warnings": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["success", "data", "logs", "errors", "warnings"]
}
@app.tool(name="calculate_dos", description="Calculate ABACUS Density of States (DOS).", annotations={"idempotentHint": False})
async def calculate_dos_tool(
    structure_dict: Dict[str, Any],
    scf_input_params: Dict[str, Any],
    nscf_input_params_overrides: Dict[str, Any],
    kpoints_definition_scf: Dict[str, Any],
    kpoints_definition_dos: Dict[str, Any],
    pseudo_potential_map: Dict[str, str],
    orbital_file_map: Optional[Dict[str, str]] = None,
    abacus_command: str = "abacus", # Default from BASE_CALCULATION_INPUT_PROPERTIES
    pseudo_base_path: str = "./pseudos/", # Default from BASE_CALCULATION_INPUT_PROPERTIES
    orbital_base_path: Optional[str] = None  # Default from BASE_CALCULATION_INPUT_PROPERTIES
) -> Dict[str, Any]:
    if orbital_file_map and orbital_base_path is None:
        orbital_base_path = pseudo_base_path # Consistent default handling

    # Normalize kpoints_definition_dos mode if "MP" is used
    if kpoints_definition_dos.get("mode", "").upper() == "MP":
        kpoints_definition_dos["mode"] = "Monkhorst-Pack"
        
    return await calculate_dos_core_logic(
        structure_dict=structure_dict,
        scf_input_params=scf_input_params,
        nscf_input_params_overrides=nscf_input_params_overrides,
        kpoints_definition_scf=kpoints_definition_scf,
        kpoints_definition_dos=kpoints_definition_dos,
        pseudo_potential_map=pseudo_potential_map,
        orbital_file_map=orbital_file_map,
        abacus_command=abacus_command,
        pseudo_base_path=pseudo_base_path,
        orbital_base_path=orbital_base_path
        # server_config can be passed if needed by core logic in future
    )
# --- calculate_charge_density tool ---
CALCULATE_CHARGE_DENSITY_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "structure_dict": SERIALIZED_ATOMS_SCHEMA,
        "scf_input_params": {"type": "object", "description": "Parameters for the SCF run. 'out_chg' will be set to 1 if not already.", "default": {}},
        "kpoints_definition": BASE_CALCULATION_INPUT_PROPERTIES["kpoints_definition"],
        "pseudo_potential_map": BASE_CALCULATION_INPUT_PROPERTIES["pseudo_potential_map"],
        "orbital_file_map": BASE_CALCULATION_INPUT_PROPERTIES["orbital_file_map"],
        "abacus_command": BASE_CALCULATION_INPUT_PROPERTIES["abacus_command"],
        "pseudo_base_path": BASE_CALCULATION_INPUT_PROPERTIES["pseudo_base_path"],
        "orbital_base_path": BASE_CALCULATION_INPUT_PROPERTIES["orbital_base_path"],
        "charge_density_filename": {"type": "string", "description": "Expected name of the charge density file (e.g., 'SPIN1_CHG.cube', 'CHG.rho').", "default": "SPIN1_CHG.cube"}
    },
    "required": ["structure_dict", "scf_input_params", "kpoints_definition", "pseudo_potential_map"]
}
CALCULATE_CHARGE_DENSITY_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "data": {
            "type": ["object", "null"],
            "properties": {
                "charge_density_content": {"type": ["string", "null"], "description": "Content of the charge density file. Null if not found or too large (future)."},
                "charge_density_filename": {"type": ["string", "null"], "description": "Name of the charge density file found."},
                "charge_density_format": {"type": ["string", "null"], "description": "Format of the charge density file (e.g., 'cube', 'rho')."},
                "file_path_in_work_dir": {"type": ["string", "null"], "description": "Relative path of the file within the calculation's working directory."},
                "message": {"type": "string"}
            }
        },
        "logs": {"type": "object"}, # Similar to SCF logs
        "errors": {"type": "array", "items": {"type": "string"}},
        "warnings": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["success", "data", "logs", "errors", "warnings"]
}
@app.tool(name="calculate_charge_density", description="Calculate and retrieve ABACUS charge density.", annotations={"idempotentHint": False})
async def calculate_charge_density_tool(
    structure_dict: Dict[str, Any],
    scf_input_params: Dict[str, Any],
    kpoints_definition: Dict[str, Any],
    pseudo_potential_map: Dict[str, str],
    orbital_file_map: Optional[Dict[str, str]] = None,
    abacus_command: str = "abacus",
    pseudo_base_path: str = "./pseudos/",
    orbital_base_path: Optional[str] = None,
    charge_density_filename: str = "SPIN1_CHG.cube"
) -> Dict[str, Any]:
    if orbital_file_map and orbital_base_path is None:
        orbital_base_path = pseudo_base_path

    return await calculate_charge_density_core_logic(
        structure_dict=structure_dict,
        scf_input_params=scf_input_params,
        kpoints_definition=kpoints_definition,
        pseudo_potential_map=pseudo_potential_map,
        orbital_file_map=orbital_file_map,
        abacus_command=abacus_command,
        pseudo_base_path=pseudo_base_path,
        orbital_base_path=orbital_base_path,
        charge_density_filename=charge_density_filename
        # server_config can be passed if needed
    )
# --- analyze_electronic_properties tool ---
ANALYZE_ELECTRONIC_PROPERTIES_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "band_structure_data": {
            "type": ["object", "null"],
            "description": "Output data from the 'calculate_band_structure' tool. Expected keys: 'eigenvalues_ev', 'fermi_energy_ev', etc."
        },
        "dos_data": {
            "type": ["object", "null"],
            "description": "Output data from the 'calculate_dos' tool. (Optional, for metallicity check)."
        },
        "properties_to_analyze": {
            "type": "array",
            "items": {"type": "string", "enum": ["band_gap", "work_function"]},
            "description": "List of electronic properties to analyze.",
            "default": ["band_gap"]
        },
        "nelect": {
            "type": ["number", "null"],
            "description": "(Optional) Total number of electrons in the system. Aids in VBM/CBM identification."
        },
        "user_provided_fermi_level_ev": {
            "type": ["number", "null"],
            "description": "(Optional) Fermi level in eV, if not available or to override band_structure_data."
        },
        "user_provided_vacuum_level_ev": {
            "type": ["number", "null"],
            "description": "(Optional) Vacuum level in eV, required for work function calculation."
        }
    },
    "required": [], # band_structure_data becomes required if "band_gap" is in properties_to_analyze (handled in logic)
    "description": "Input for analyzing electronic properties. Provide band_structure_data for band gap analysis."
}
ANALYZE_ELECTRONIC_PROPERTIES_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "analyzed_properties": {
            "type": "object",
            "properties": {
                "band_gap_ev": {"type": ["number", "null"], "description": "Calculated band gap in eV."},
                "vbm_ev": {"type": ["number", "null"], "description": "Valence Band Maximum in eV."},
                "cbm_ev": {"type": ["number", "null"], "description": "Conduction Band Minimum in eV."},
                "gap_type": {"type": ["string", "null"], "enum": ["direct", "indirect", "unknown", None], "description": "Type of band gap."},
                "vbm_k_point_coordinates": {"type": ["array", "null"], "items": {"type": "number"}, "description": "K-point coordinates of VBM."},
                "cbm_k_point_coordinates": {"type": ["array", "null"], "items": {"type": "number"}, "description": "K-point coordinates of CBM."},
                "is_metallic_from_bands": {"type": ["boolean", "null"], "description": "True if band structure suggests metallicity."},
                "is_metallic_from_dos": {"type": ["boolean", "null"], "description": "True if DOS suggests metallicity (non-zero DOS at Fermi level)."},
                "work_function_ev": {"type": ["number", "null"], "description": "Calculated work function in eV."},
                "vacuum_level_ev_used": {"type": ["number", "null"], "description": "Vacuum level used for work function calculation."},
                "fermi_level_ev_used_for_wf": {"type": ["number", "null"], "description": "Fermi level used for work function calculation."},
                "work_function_message": {"type": ["string", "null"], "description": "Message regarding work function analysis."}
            },
            "description": "Dictionary of analyzed electronic properties and their values."
        },
        "errors": {"type": "array", "items": {"type": "string"}},
        "warnings": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["success", "analyzed_properties", "errors", "warnings"]
}
@app.tool(name="analyze_electronic_properties", description="Analyze electronic properties like band gap from pre-computed data.", annotations={"readOnlyHint": True, "idempotentHint": True})
async def analyze_electronic_properties_tool(
    band_structure_data: Optional[Dict[str, Any]] = None,
    dos_data: Optional[Dict[str, Any]] = None,
    properties_to_analyze: List[str] = ["band_gap"], # Default to analyze band_gap
    nelect: Optional[float] = None,
    user_provided_fermi_level_ev: Optional[float] = None,
    user_provided_vacuum_level_ev: Optional[float] = None
) -> Dict[str, Any]:
    return await analyze_electronic_properties_core_logic(
        band_structure_data=band_structure_data,
        dos_data=dos_data,
        properties_to_analyze=properties_to_analyze,
        nelect=nelect,
        user_provided_fermi_level_ev=user_provided_fermi_level_ev,
        user_provided_vacuum_level_ev=user_provided_vacuum_level_ev
    )
# --- suggest_parameters tool ---
SUGGEST_PARAMETERS_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "calculation_type": {
            "type": "string",
            "description": "Type of calculation for which parameters are suggested (e.g., 'scf', 'relax', 'bands', 'dos').",
            "enum": ["scf", "relax", "cell-relax", "md", "bands", "dos", "phonon"] # Allow 'phonon' as well
        },
        "structure_dict": {
            "type": ["object", "null"],
            "description": "(Optional) ASE Atoms object dictionary. Future use for structure-dependent suggestions.",
            "default": None
        },
        "desired_accuracy": {
            "type": "string",
            "enum": ["low", "medium", "high"],
            "description": "Desired level of accuracy for the calculation.",
            "default": "medium"
        }
    },
    "required": ["calculation_type"]
}
SUGGEST_PARAMETERS_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "suggested_params": {
            "type": "object",
            "description": "A dictionary containing suggested parameters. For 'bands' or 'dos', this will be nested (e.g., 'scf_input_params', 'nscf_input_params'). For others, it might contain 'input_params' and 'kpoints_definition'."
            # The actual structure of suggested_params depends on the core logic's output
        },
        "notes": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Explanatory notes and guidance for the suggested parameters."
        },
        "errors": {"type": "array", "items": {"type": "string"}},
        "warnings": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["success", "suggested_params", "notes", "errors", "warnings"]
}
@app.tool(name="suggest_parameters", description="Suggests ABACUS input parameters based on calculation type and desired accuracy.", annotations={"readOnlyHint": True, "idempotentHint": True})
async def suggest_parameters_tool(
    calculation_type: str,
    structure_dict: Optional[Dict[str, Any]] = None,
    desired_accuracy: str = "medium"
) -> Dict[str, Any]:
    # Normalize calculation_type for core logic if needed (e.g. "cell_relax" to "cell-relax")
    normalized_calc_type = calculation_type.lower().replace("_", "-")
    if normalized_calc_type == "phonon-dfpt-preparation": # Alias from dev plan
        normalized_calc_type = "phonon"
        
    return await suggest_parameters_core_logic(
        calculation_type=normalized_calc_type,
        structure_dict=structure_dict,
        desired_accuracy=desired_accuracy
    )
# --- diagnose_failure tool ---
DIAGNOSE_FAILURE_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "error_log_content": {
            "type": ["string", "null"],
            "description": "(Optional) Content of the stderr log from ABACUS or a specific error file."
        },
        "output_log_content": {
            "type": ["string", "null"],
            "description": "(Optional) Content of the main stdout log from ABACUS (e.g., running_scf.log, OUT.ABACUS)."
        }
        # "input_parameters": { # Future enhancement
        #     "type": ["object", "null"],
        #     "description": "(Optional) Dictionary of input parameters used for the failed calculation."
        # },
        # "calculation_type": { # Future enhancement
        #     "type": ["string", "null"],
        #     "description": "(Optional) Type of calculation that failed (e.g., 'scf', 'relax')."
        # }
    },
    "required": [], # At least one log should ideally be provided.
    "description": "Diagnoses ABACUS calculation failures based on provided log contents."
}
DIAGNOSE_FAILURE_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean", "description": "True if any diagnosis could be made, False otherwise."},
        "diagnoses": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "signature": {"type": "string", "description": "A unique identifier for the detected error type."},
                    "matched_pattern": {"type": "string", "description": "The regex pattern that matched in the logs."},
                    "possible_causes": {"type": "array", "items": {"type": "string"}, "description": "List of potential reasons for this error."},
                    "suggested_solutions": {"type": "array", "items": {"type": "string"}, "description": "List of suggested actions to resolve the error."}
                },
                "required": ["signature", "matched_pattern", "possible_causes", "suggested_solutions"]
            },
            "description": "List of identified failure diagnoses."
        },
        "summary": {"type": "string", "description": "A brief summary of the diagnosis outcome."},
        "errors": {"type": "array", "items": {"type": "string"}},
        "warnings": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["success", "diagnoses", "summary", "errors", "warnings"]
}
@app.tool(name="diagnose_failure", description="Diagnoses ABACUS calculation failures from logs and suggests solutions.", annotations={"readOnlyHint": True, "idempotentHint": True})
async def diagnose_failure_tool(
    error_log_content: Optional[str] = None,
    output_log_content: Optional[str] = None
    # input_parameters: Optional[Dict[str, Any]] = None, # Future
    # calculation_type: Optional[str] = None # Future
) -> Dict[str, Any]:
    if not error_log_content and not output_log_content:
        return {
            "success": False,
            "diagnoses": [],
            "summary": "No log content provided. Cannot perform diagnosis.",
            "errors": ["At least one of 'error_log_content' or 'output_log_content' must be provided."],
            "warnings": []
        }
        
    return await diagnose_failure_core_logic(
        error_log_content=error_log_content,
        output_log_content=output_log_content
        # input_parameters=input_parameters, # Pass when implemented
        # calculation_type=calculation_type  # Pass when implemented
    )
# --- estimate_cost tool ---
ESTIMATE_COST_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "structure_dict": SERIALIZED_ATOMS_SCHEMA, # Reusing from base schemas
        "kpoints_definition": BASE_CALCULATION_INPUT_PROPERTIES["kpoints_definition"],
        "input_params": {
            "type": ["object", "null"],
            "description": "(Optional) ABACUS INPUT parameters, especially 'calculation', 'ecutwfc', 'nbands', 'md_nstep'.",
            "default": {}
        },
        "num_mpi_processes": {
            "type": ["integer", "null"],
            "description": "(Optional) Number of MPI processes to be used. For informational notes.",
            "default": None
        }
    },
    "required": ["structure_dict", "kpoints_definition"],
    "description": "Provides a very rough, qualitative estimation of ABACUS computational cost."
}
ESTIMATE_COST_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "estimated_cost_category": {
            "type": "string",
            "enum": ["unknown", "low", "medium", "high", "very_high"],
            "description": "Qualitative category of the estimated computational cost."
        },
        "cost_factors": {
            "type": "object",
            "properties": {
                "num_atoms": {"type": "integer"},
                "num_kpoints_approx": {"type": "integer"},
                "calculation_type": {"type": "string"},
                "ecutwfc_ry": {"type": "number"},
                "nbands_approx": {"type": "integer"},
                "md_nstep": {"type": ["integer", "null"]} # Only if MD
            },
            "description": "Key factors influencing the cost estimation."
        },
        "raw_cost_score": {"type": "number", "description": "Internal raw score used for categorization (for reference/debugging)."},
        "notes": {"type": "array", "items": {"type": "string"}, "description": "Important notes and limitations of the cost estimation."},
        "errors": {"type": "array", "items": {"type": "string"}},
        "warnings": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["success", "estimated_cost_category", "cost_factors", "raw_cost_score", "notes", "errors", "warnings"]
}
@app.tool(name="estimate_cost", description="Estimates the qualitative computational cost of an ABACUS calculation.", annotations={"readOnlyHint": True, "idempotentHint": True})
async def estimate_cost_tool(
    structure_dict: Dict[str, Any],
    kpoints_definition: Dict[str, Any],
    input_params: Optional[Dict[str, Any]] = None,
    num_mpi_processes: Optional[int] = None
) -> Dict[str, Any]:
    return await estimate_cost_core_logic(
        structure_dict=structure_dict,
        kpoints_definition=kpoints_definition,
        input_params=input_params,
        num_mpi_processes=num_mpi_processes
    )
# --- validate_input tool ---
VALIDATE_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "input_params": {
            "type": "object",
            "description": "ABACUS INPUT file parameters dictionary."
        },
        "kpoints_definition": {
            "type": ["object", "null"],
            "description": "(Optional) K-points definition dictionary.",
            "default": None
        },
        "structure_dict": {
            "type": ["object", "null"],
            "description": "(Optional) ASE Atoms object dictionary, for structure-specific checks like PBC.",
            "default": None
        }
    },
    "required": ["input_params"],
    "description": "Validates ABACUS input parameters for common issues and incompatibilities."
}
VALIDATE_INPUT_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean", "description": "True if validation passes (no errors found), False if errors are present."},
        "validation_issues": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "level": {"type": "string", "enum": ["error", "warning"], "description": "Severity of the issue."},
                    "message": {"type": "string", "description": "Description of the validation issue."}
                },
                "required": ["level", "message"]
            },
            "description": "List of identified validation issues (errors or warnings)."
        },
        "errors": {"type": "array", "items": {"type": "string"}, "description": "Critical errors during tool execution (not validation errors)."},
        "warnings": {"type": "array", "items": {"type": "string"}, "description": "Warnings during tool execution (not validation warnings)."}
    },
    "required": ["success", "validation_issues", "errors", "warnings"]
}
@app.tool(name="validate_input", description="Validates ABACUS input parameters for common issues.", annotations={"readOnlyHint": True, "idempotentHint": True})
async def validate_input_tool(
    input_params: Dict[str, Any],
    kpoints_definition: Optional[Dict[str, Any]] = None,
    structure_dict: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    return await validate_input_core_logic(
        input_params=input_params,
        kpoints_definition=kpoints_definition,
        structure_dict=structure_dict
    )
# --- Task Management Tools ---

# --- get_calculation_status tool ---
GET_CALCULATION_STATUS_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "task_id": {"type": "string", "description": "The unique ID of the task to get status for."}
    },
    "required": ["task_id"]
}
GET_CALCULATION_STATUS_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "task_id": {"type": "string"},
        "status": {"type": "string"},
        "calculation_type": {"type": "string"},
        "submission_time": {"type": ["string", "null"], "format": "date-time"},
        "start_time": {"type": ["string", "null"], "format": "date-time"},
        "end_time": {"type": ["string", "null"], "format": "date-time"},
        "results_summary": {"type": ["object", "null"]},
        "error_message": {"type": ["string", "null"]},
        "error": {"type": "string", "description": "Error message if success is false."} 
    },
    "required": ["success"] 
}
@app.tool(name="get_calculation_status", description="Get the status of a previously submitted calculation task.", annotations={"readOnlyHint": True, "idempotentHint": True})
async def get_calculation_status_tool(task_id: str) -> Dict[str, Any]:
    return await get_calculation_status_core_logic(task_id=task_id)

# --- list_recent_calculations tool ---
LIST_RECENT_CALCULATIONS_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "count": {"type": "integer", "description": "Maximum number of recent tasks to list.", "default": 10, "minimum": 1},
        "status_filter": {
            "type": ["string", "null"],
            "description": "Optional. Filter tasks by status.",
            "enum": [None, "submitted", "starting", "running", "processing_output", "completed_execution_phase", "completed", "failed", "cancelled_request", "cancelled"],
            "default": None
        }
    },
    "additionalProperties": False
}
LIST_RECENT_CALCULATIONS_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "tasks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "calculation_type": {"type": "string"},
                    "status": {"type": "string"},
                    "submission_time": {"type": ["string", "null"], "format": "date-time"},
                    "results_summary": {"type": ["object", "null"]}
                },
                "required": ["task_id", "calculation_type", "status"]
            }
        },
        "error": {"type": "string", "description": "Error message if success is false."}
    },
    "required": ["success", "tasks"]
}
@app.tool(name="list_recent_calculations", description="List recently submitted calculation tasks.", annotations={"readOnlyHint": True, "idempotentHint": True})
async def list_recent_calculations_tool(count: int = 10, status_filter: Optional[str] = None) -> Dict[str, Any]:
    return await list_recent_calculations_core_logic(count=count, status_filter=status_filter)

# --- get_calculation_results tool ---
GET_CALCULATION_RESULTS_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "task_id": {"type": "string", "description": "The unique ID of the task to get results for."}
    },
    "required": ["task_id"]
}
GET_CALCULATION_RESULTS_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "task_id": {"type": "string"},
        "status": {"type": "string"},
        "calculation_type": {"type": "string"},
        "results_summary": {"type": ["object", "null"]},
        "error_message": {"type": ["string", "null"]},
        "logs_reference": {"type": ["string", "object", "null"], "description": "Reference to logs, e.g., working directory path or log snippet."},
        "notes": {"type": "array", "items": {"type": "string"}},
        "current_status": {"type": "string", "description": "Current status if task is not completed/failed."},
        "error": {"type": "string", "description": "Error message if success is false."}
    },
    "required": ["success"]
}
@app.tool(name="get_calculation_results", description="Get the results of a completed or failed calculation task.", annotations={"readOnlyHint": True, "idempotentHint": True})
async def get_calculation_results_tool(task_id: str) -> Dict[str, Any]:
    return await get_calculation_results_core_logic(task_id=task_id)

# --- monitor_calculation tool ---
MONITOR_CALCULATION_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "task_id": {"type": "string", "description": "The unique ID of the task to monitor."}
    },
    "required": ["task_id"]
}
MONITOR_CALCULATION_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "task_id": {"type": "string"},
        "status": {"type": "string"},
        "message": {"type": "string"},
        "current_log_snippet": {"type": ["string", "null"]},
        "error": {"type": "string", "description": "Error message if success is false."}
    },
    "required": ["success"]
}
@app.tool(name="monitor_calculation", description="Monitor a calculation task (simplified: returns current status).", annotations={"readOnlyHint": True, "idempotentHint": True})
async def monitor_calculation_tool(task_id: str) -> Dict[str, Any]:
    return await monitor_calculation_core_logic(task_id=task_id)

# --- cancel_calculation tool ---
CANCEL_CALCULATION_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "task_id": {"type": "string", "description": "The unique ID of the task to cancel."}
    },
    "required": ["task_id"]
}
CANCEL_CALCULATION_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "message": {"type": "string"},
        "new_status": {"type": ["string", "null"]}, 
        "error": {"type": "string", "description": "Error message if success is false (e.g. task not found)."}
    },
    "required": ["success", "message"]
}
@app.tool(name="cancel_calculation", description="Request cancellation of a calculation task (simplified).", annotations={"idempotentHint": False})
async def cancel_calculation_tool(task_id: str) -> Dict[str, Any]:
    return await cancel_calculation_core_logic(task_id=task_id)


def main():
    """Main entry point for the ABACUS MCP Server."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="ABACUS MCP Server")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--stdio", action="store_true", help="Use stdio transport (default)")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    
    args = parser.parse_args()
    
    # Set log level
    import os
    os.environ["LOG_LEVEL"] = args.log_level
    
    # Load configuration if provided
    if args.config:
        import json
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
            log_app_event(f"Loaded configuration from {args.config}", "info", config=config)
        except Exception as e:
            log_app_event(f"Failed to load configuration: {e}", "error")
    
    # Log startup
    log_app_event("ABACUS MCP Server starting", "info",
                  host=args.host, port=args.port, stdio=args.stdio)
    
    try:
        if args.stdio or len(sys.argv) == 1:
            # Use stdio transport (default for MCP)
            app.run(transport="stdio")
        else:
            # Use HTTP transport (for development/testing)
            app.run_http(host=args.host, port=args.port)
    except KeyboardInterrupt:
        log_app_event("ABACUS MCP Server shutting down", "info")
    except Exception as e:
        log_app_event(f"Server error: {e}", "error")
        sys.exit(1)

if __name__ == "__main__":
    main()