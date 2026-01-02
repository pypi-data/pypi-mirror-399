# src/tools/calculation_execution.py
from typing import Dict, Any, Optional, List, Tuple
import os # For path joining

# 从核心模块导入所需的函数
from src.core.abacus_runner import (
    generate_abacus_input,
    generate_abacus_stru,
    generate_abacus_kpt,
    execute_abacus_command,
    parse_abacus_scf_output,
    parse_abacus_opt_output, # Added for run_optimization_core_logic
    parse_abacus_md_output,  # Added for run_md_core_logic
    # atoms_from_dict # 可能需要这个来获取ntype或传递给KPT生成
)

# 导入结果解释器
from src.tools.result_interpreter import result_interpreter

# 导入日志记录
from src.logging_config import (
    log_calculation_start, log_calculation_end, log_error,
    log_performance, log_app_event
)
import time
# 假设我们有一个配置对象或字典来存储服务器级别的设置
# 例如: SERVER_CONFIG = {"PSEUDO_POTENTIAL_DIR": "/path/to/pseudos", "ABACUS_COMMAND": "abacus"}
# 这个配置应该在服务器启动时加载。为了简单起见，我们暂时硬编码或传递这些。

# 默认ABACUS命令，可以被覆盖
DEFAULT_ABACUS_EXEC_COMMAND = "abacus" 

# 默认赝势和轨道文件基础路径 (这些应该是可配置的)
# 在实际应用中，这些路径应该从服务器配置中读取
# 例如: server_config.get("PSEUDO_DIR", "./pseudos")
# 为简单起见，我们假设工具调用时会提供这些基础路径，或者它们在工作目录中
# 或者，MCP工具的输入参数可以包含这些路径。

async def run_scf_core_logic(
    structure_dict: Dict[str, Any],
    input_params: Dict[str, Any],
    kpoints_definition: Dict[str, Any], # e.g., {"mode": "Monkhorst-Pack", "size": [2,2,2], "shift": [0,0,0]}
    pseudo_potential_map: Dict[str, str], # e.g., {"Si": "Si.SG15.UPF"} - Filenames, not paths yet
    orbital_file_map: Optional[Dict[str, str]] = None, # e.g., {"Si": "Si_gga_8au_100Ry_2s2p1d.orb"}
    abacus_command: str = DEFAULT_ABACUS_EXEC_COMMAND,
    pseudo_base_path: str = "./", # Base path where pseudopotential files are located
    orbital_base_path: Optional[str] = None, # Base path for orbital files
    server_config: Optional[Dict[str, Any]] = None # For future expansion
) -> Dict[str, Any]:
    """
    Core logic for running an SCF calculation using ABACUS.
    """
    start_time = time.time()
    results: Dict[str, Any] = {"success": False, "data": None, "logs": {}, "errors": [], "warnings": [], "task_id": None}
    stru_content_str = ""
    ntype_from_stru = 0
    task_id = None

    try:
        # Log calculation start
        log_app_event("Starting SCF calculation setup", "info")
        stru_content_str, ntype_from_stru = generate_abacus_stru(
            atoms_obj_or_dict=structure_dict,
            pseudo_potential_map=pseudo_potential_map, 
            orbital_file_map=orbital_file_map,       
            coordinate_type=input_params.get("stru_coordinate_type", "Cartesian_Angstrom"), 
            fixed_atoms_indices=input_params.get("stru_fixed_atoms_indices")
        )
        results["logs"]["stru_file_content"] = stru_content_str
        
        input_params_updated = input_params.copy()
        input_params_updated["ntype"] = ntype_from_stru
        input_params_updated.setdefault("pseudo_dir", "./") 

        input_content_str = generate_abacus_input(input_params_updated)
        results["logs"]["input_file_content"] = input_content_str

        kpt_mode = kpoints_definition.get("mode", "Monkhorst-Pack").lower()
        kpt_content_str = generate_abacus_kpt(
            kpt_generation_mode=kpt_mode,
            atoms_obj_or_dict=structure_dict if kpt_mode in ["line", "bandpath"] else None,
            kpts_size=kpoints_definition.get("size"),
            kpts_shift=kpoints_definition.get("shift"),
            kpath_definition=kpoints_definition.get("path_definition"), 
            kpts_npoints_per_segment=kpoints_definition.get("npoints_per_segment"),
            explicit_kpoints_list=kpoints_definition.get("kpts_list")
        )
        results["logs"]["kpt_file_content"] = kpt_content_str

        full_path_pseudo_files = {
            fname: os.path.join(pseudo_base_path, fname)
            for symbol, fname in pseudo_potential_map.items()
        }
        full_path_orbital_files = None
        if orbital_file_map:
            current_orbital_base_path = orbital_base_path if orbital_base_path else pseudo_base_path
            full_path_orbital_files = {
                fname: os.path.join(current_orbital_base_path, fname)
                for symbol, fname in orbital_file_map.items()
            }
        
        timeout = input_params.get("execution_timeout_seconds", 3600.0)
        
        exec_results = await execute_abacus_command(
            abacus_command=abacus_command,
            input_content=input_content_str,
            stru_content=stru_content_str,
            kpt_content=kpt_content_str,
            pseudo_potential_files=full_path_pseudo_files,
            orbital_files=full_path_orbital_files,
            timeout_seconds=timeout,
            calculation_type_for_task_mgmt="scf",
            input_params_for_task_mgmt=input_params_updated,
            structure_dict_for_task_mgmt=structure_dict,
            kpoints_def_for_task_mgmt=kpoints_definition,
            pseudo_map_for_task_mgmt=pseudo_potential_map,
            orbital_map_for_task_mgmt=orbital_file_map
        )
        task_id = exec_results.get("task_id")
        results["task_id"] = task_id
        results["logs"]["stdout"] = exec_results.get("stdout", "")
        results["logs"]["stderr"] = exec_results.get("stderr", "")
        results["logs"]["working_directory"] = exec_results.get("working_directory")
        
        # Log calculation start with task ID
        if task_id:
            log_calculation_start(task_id, "scf", current_input_params)
        
        if not exec_results.get("success"):
            error_msg = exec_results.get("error", "ABACUS execution failed.")
            results["errors"].append(error_msg)
            if exec_results.get("stderr") and (not exec_results.get("error") or exec_results.get("stderr") not in exec_results.get("error", "")):
                 results["errors"].append(f"ABACUS stderr: {exec_results.get('stderr')}")
            
            # Log execution failure
            if task_id:
                execution_time = (time.time() - start_time) * 1000
                log_calculation_end(task_id, "scf", False, execution_time)
            
            return results

        output_to_parse = results["logs"]["stdout"]
        log_file_name = "running_scf.log"
        potential_log_file_path_out_suffix = os.path.join(
            exec_results["working_directory"], 
            f"OUT.{input_params_updated.get('suffix', 'ABACUS')}", 
            log_file_name
        )
        potential_log_file_path_root = os.path.join(exec_results["working_directory"], log_file_name)
        actual_log_file_parsed = "stdout"

        if os.path.exists(potential_log_file_path_out_suffix):
            try:
                with open(potential_log_file_path_out_suffix, "r", encoding='utf-8') as f_log:
                    output_to_parse = f_log.read()
                actual_log_file_parsed = potential_log_file_path_out_suffix
            except Exception as e_read_log:
                results["warnings"].append(f"Could not read SCF log file {potential_log_file_path_out_suffix}: {e_read_log}. Trying root or parsing stdout.")
        elif os.path.exists(potential_log_file_path_root):
            try:
                with open(potential_log_file_path_root, "r", encoding='utf-8') as f_log:
                    output_to_parse = f_log.read()
                actual_log_file_parsed = potential_log_file_path_root
            except Exception as e_read_log:
                results["warnings"].append(f"Could not read SCF log file {potential_log_file_path_root}: {e_read_log}. Parsing stdout instead.")
        results["logs"]["parsed_log_file"] = actual_log_file_parsed

        parsed_output = parse_abacus_scf_output(output_to_parse)
        
        # Add interpretation and recommendations
        interpretation_data = result_interpreter.interpret_scf_results(parsed_output, current_input_params)
        parsed_output["interpretation"] = interpretation_data["interpretation"]
        parsed_output["recommendations"] = interpretation_data["recommendations"]
        
        results["data"] = parsed_output
        results["success"] = parsed_output.get("converged", False)
        if parsed_output.get("warnings"): results["warnings"].extend(parsed_output["warnings"])
        if parsed_output.get("errors"): results["errors"].extend(parsed_output["errors"]); results["success"] = False
        if not results["success"] and not any("convergence NOT achieved" in w for w in results.get("warnings",[])):
            if not results.get("errors"): results["errors"].append("SCF calculation did not converge or output parsing failed.")
        
        # Log calculation completion
        if task_id:
            execution_time = (time.time() - start_time) * 1000
            result_summary = {
                "converged": parsed_output.get("converged", False),
                "total_energy_ry": parsed_output.get("total_energy_ry"),
                "scf_iterations": parsed_output.get("scf_iterations")
            }
            log_calculation_end(task_id, "scf", results["success"], execution_time, result_summary)
            log_performance("scf_calculation", execution_time, task_id=task_id)
            
    except FileNotFoundError as e:
        results["errors"].append(f"File not found (SCF): {e}")
        results["success"] = False
        log_error("SCF file not found", e, task_id, "scf")
    except ValueError as e:
        results["errors"].append(f"Input error (SCF): {e}")
        results["success"] = False
        log_error("SCF input error", e, task_id, "scf")
    except Exception as e:
        results["errors"].append(f"Unexpected error (SCF): {e}")
        results["success"] = False
        log_error("SCF unexpected error", e, task_id, "scf")
    
    return results

async def test_run_scf():
    if 'tempfile' not in globals(): import tempfile
    if 'shutil' not in globals(): import shutil
    print("--- Testing SCF Core Logic ---")
    si_dict = {"symbols": ["Si", "Si"], "positions": [[0,0,0],[1.3575,1.3575,1.3575]], "cell": [[5.43,0,0],[0,5.43,0],[0,0,5.43]], "pbc": True}
    scf_params = {"suffix":"Si_scf_test","ecutwfc":50,"scf_thr":1e-7,"dft_functional":"PBE","pseudo_dir":"./","stru_coordinate_type":"Cartesian_Angstrom"}
    kpts_def = {"mode":"Monkhorst-Pack","size":[2,2,2],"shift":[0,0,0]}
    test_pseudo_dir = tempfile.mkdtemp(prefix="test_pseudos_scf_")
    with open(os.path.join(test_pseudo_dir, "Si.UPF_dummy"), "w") as f: f.write("dummy Si pseudo")
    pseudo_map = {"Si": "Si.UPF_dummy"}
    original_execute = globals().get('execute_abacus_command')

    async def mock_exec_scf_ok(*_, **kwargs_exec):
        wd = tempfile.mkdtemp(prefix="abacus_scf_ok_")
        out_dir = os.path.join(wd, f"OUT.{scf_params['suffix']}")
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "running_scf.log"), "w") as f: f.write("!FINAL_ETOTAL_IS -100.0 Ry\nEFERMI -0.5 Ry\nconvergence has been achieved\nITER 10\n")
        return {"success":True,"return_code":0,"stdout":"...","stderr":"","working_directory":wd,"error":None,"task_id":"scf_ok_1"}
    globals()['execute_abacus_command'] = mock_exec_scf_ok
    res_ok = await run_scf_core_logic(si_dict,scf_params,kpts_def,pseudo_map,pseudo_base_path=test_pseudo_dir)
    print(f"SCF OK: Success={res_ok['success']}, TaskID={res_ok['task_id']}, Converged={res_ok['data'].get('converged')}")
    assert res_ok["success"] and res_ok["task_id"] == "scf_ok_1" and res_ok["data"]["converged"]
    if os.path.exists(res_ok["logs"]["working_directory"]): shutil.rmtree(res_ok["logs"]["working_directory"])
    
    globals()['execute_abacus_command'] = original_execute # Restore
    shutil.rmtree(test_pseudo_dir)
    print("--- SCF Tests Done ---")

async def run_optimization_core_logic(
    structure_dict: Dict[str, Any], input_params: Dict[str, Any], kpoints_definition: Dict[str, Any],
    pseudo_potential_map: Dict[str, str], orbital_file_map: Optional[Dict[str, str]] = None,
    abacus_command: str = DEFAULT_ABACUS_EXEC_COMMAND, pseudo_base_path: str = "./",
    orbital_base_path: Optional[str] = None, server_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    results: Dict[str, Any] = {"success": False, "data": None, "logs": {}, "errors": [], "warnings": [], "task_id": None}
    calc_type = input_params.get("calculation", "relax").lower()
    if calc_type not in ["relax", "cell-relax"]:
        results["errors"].append(f"Invalid 'calculation' type for optimization: {calc_type}."); return results
    current_input_params = input_params.copy(); current_input_params["calculation"] = calc_type
    try:
        stru_content_str, ntype = generate_abacus_stru(structure_dict, pseudo_potential_map, orbital_file_map, current_input_params.get("stru_coordinate_type", "Cartesian_Angstrom"), current_input_params.get("stru_fixed_atoms_indices"))
        results["logs"]["stru_file_content"] = stru_content_str; current_input_params["ntype"] = ntype; current_input_params.setdefault("pseudo_dir", "./")
        if calc_type=="relax" and not current_input_params.get("cal_force"): current_input_params["cal_force"]=1; results["warnings"].append("Set 'cal_force=1' for relax.")
        if calc_type=="cell-relax":
            if not current_input_params.get("cal_force"): current_input_params["cal_force"]=1; results["warnings"].append("Set 'cal_force=1' for cell-relax.")
            if not current_input_params.get("cal_stress"): current_input_params["cal_stress"]=1; results["warnings"].append("Set 'cal_stress=1' for cell-relax.")
        if not current_input_params.get("out_stru"): current_input_params["out_stru"]=1; results["warnings"].append("Set 'out_stru=1' for opt.")
        input_content_str = generate_abacus_input(current_input_params); results["logs"]["input_file_content"] = input_content_str
        kpt_mode = kpoints_definition.get("mode", "Monkhorst-Pack").lower()
        kpt_content_str = generate_abacus_kpt(kpt_mode, structure_dict if kpt_mode in ["line","bandpath"] else None, kpoints_definition.get("size"), kpoints_definition.get("shift"), kpoints_definition.get("path_definition"), kpoints_definition.get("npoints_per_segment"), kpoints_definition.get("kpts_list"))
        results["logs"]["kpt_file_content"] = kpt_content_str
        full_pseudo = {fname:os.path.join(pseudo_base_path,fname) for _,fname in pseudo_potential_map.items()}
        full_orbital = None
        if orbital_file_map: full_orbital = {fname:os.path.join(orbital_base_path if orbital_base_path else pseudo_base_path, fname) for _,fname in orbital_file_map.items()}
        timeout = current_input_params.get("execution_timeout_seconds", 7200.0)
        exec_res = await execute_abacus_command(abacus_command,input_content_str,stru_content_str,kpt_content_str,full_pseudo,full_orbital,timeout,calc_type,current_input_params,structure_dict,kpoints_definition,pseudo_potential_map,orbital_file_map)
        results["task_id"]=exec_res.get("task_id"); results["logs"].update({"stdout":exec_res.get("stdout",""),"stderr":exec_res.get("stderr",""),"working_directory":exec_res.get("working_directory")})
        if not exec_res.get("success"):
            results["errors"].append(exec_res.get("error", "ABACUS opt exec failed.")); results["success"]=False
            if exec_res.get("stderr") and (not exec_res.get("error") or exec_res.get("stderr") not in exec_res.get("error","")): results["errors"].append(f"ABACUS stderr: {exec_res.get('stderr')}")
            return results
        output_parse = results["logs"]["stdout"]; opt_log_name=f"running_{calc_type}.log"
        log_path_suffix = os.path.join(exec_res["working_directory"],f"OUT.{current_input_params.get('suffix','ABACUS')}",opt_log_name)
        log_path_root = os.path.join(exec_res["working_directory"],opt_log_name); actual_log_parsed="stdout"
        if os.path.exists(log_path_suffix):
            try: 
                with open(log_path_suffix,"r",encoding='utf-8') as f:output_parse=f.read();actual_log_parsed=log_path_suffix
            except Exception as e: results["warnings"].append(f"Failed to read {log_path_suffix}: {e}")
        elif os.path.exists(log_path_root):
            try: 
                with open(log_path_root,"r",encoding='utf-8') as f:output_parse=f.read();actual_log_parsed=log_path_root
            except Exception as e: results["warnings"].append(f"Failed to read {log_path_root}: {e}")
        results["logs"]["parsed_log_file"]=actual_log_parsed
        parsed_out = parse_abacus_opt_output(output_parse,exec_res["working_directory"],current_input_params.get('suffix','ABACUS'),calc_type,current_input_params.get("out_stru")==1)
        
        # Add interpretation and recommendations
        interpretation_data = result_interpreter.interpret_optimization_results(parsed_out, current_input_params)
        parsed_out["interpretation"] = interpretation_data["interpretation"]
        parsed_out["recommendations"] = interpretation_data["recommendations"]
        
        results["data"]=parsed_out; results["success"]=parsed_out.get("converged",False)
        if exec_res.get("return_code")==-1: results["success"]=False; results["errors"].append(exec_res.get("error","Opt timed out."))
        if parsed_out.get("warnings"):results["warnings"].extend(parsed_out["warnings"])
        if parsed_out.get("errors"):results["errors"].extend(parsed_out["errors"]);results["success"]=False
        if exec_res.get("success") and not results["success"] and not parsed_out.get("errors"): results["warnings"].append(f"Opt ({calc_type}) finished but not converged/parsed.")
    except FileNotFoundError as e:results["errors"].append(f"File not found (opt): {e}");results["success"]=False
    except ValueError as e:results["errors"].append(f"Input error (opt): {e}");results["success"]=False
    except Exception as e:results["errors"].append(f"Unexpected error (opt): {e}");results["success"]=False
    return results

async def test_run_optimization():
    if 'tempfile' not in globals(): import tempfile
    if 'shutil' not in globals(): import shutil
    print("--- Testing Optimization Core Logic ---")
    si_dimer = {"symbols":["Si","Si"],"positions":[[0,0,0],[0,0,2.5]],"cell":[[10,0,0],[0,10,0],[0,0,10]],"pbc":True}
    opt_params = {"suffix":"Si_dimer_relax","calculation":"relax","ecutwfc":40,"force_thr_ev":0.01,"out_stru":1}
    kpts_opt = {"mode":"Monkhorst-Pack","size":[1,1,1]}
    test_pseudo_opt_dir = tempfile.mkdtemp(prefix="test_pseudos_opt_")
    with open(os.path.join(test_pseudo_opt_dir, "Si_opt.UPF"),"w") as f:f.write("Si pseudo opt")
    pseudo_map_opt = {"Si":"Si_opt.UPF"}
    original_execute_opt = globals().get('execute_abacus_command')

    async def mock_exec_opt_ok(*_, **kwargs_exec_opt):
        wd_opt = tempfile.mkdtemp(prefix="abacus_opt_ok_")
        out_dir_opt = os.path.join(wd_opt, f"OUT.{opt_params['suffix']}")
        os.makedirs(out_dir_opt, exist_ok=True)
        with open(os.path.join(out_dir_opt, f"running_{opt_params['calculation']}.log"),"w") as f: f.write("TOTAL ENERGY = -200.0 Ry\nCONVERGENCE ACHIEVED\n")
        with open(os.path.join(out_dir_opt, f"STRU_{opt_params['suffix']}_ION0_AFTER_RELAX"),"w") as f: f.write("ATOMIC_POSITIONS\nCartesian_Angstrom\nSi\n0 0 0\nSi\n0 0 2.2\n")
        return {"success":True,"return_code":0,"stdout":"...","stderr":"","working_directory":wd_opt,"error":None,"task_id":"opt_ok_1"}
    globals()['execute_abacus_command'] = mock_exec_opt_ok
    res_opt_ok = await run_optimization_core_logic(si_dimer,opt_params,kpts_opt,pseudo_map_opt,pseudo_base_path=test_pseudo_opt_dir)
    print(f"Opt OK: Success={res_opt_ok['success']}, TaskID={res_opt_ok['task_id']}, Converged={res_opt_ok['data'].get('converged')}")
    assert res_opt_ok["success"] and res_opt_ok["task_id"]=="opt_ok_1" and res_opt_ok["data"]["converged"]
    assert abs(res_opt_ok["data"]["final_structure_dict"]["positions"][1][2] - 2.2) < 1e-5
    if os.path.exists(res_opt_ok["logs"]["working_directory"]): shutil.rmtree(res_opt_ok["logs"]["working_directory"])

    globals()['execute_abacus_command'] = original_execute_opt # Restore
    shutil.rmtree(test_pseudo_opt_dir)
    print("--- Optimization Tests Done ---")

async def run_md_core_logic(
    structure_dict: Dict[str, Any], input_params: Dict[str, Any], kpoints_definition: Dict[str, Any],
    pseudo_potential_map: Dict[str, str], orbital_file_map: Optional[Dict[str, str]] = None,
    abacus_command: str = DEFAULT_ABACUS_EXEC_COMMAND, pseudo_base_path: str = "./",
    orbital_base_path: Optional[str] = None, server_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    results: Dict[str, Any] = {"success": False, "data": None, "logs": {}, "errors": [], "warnings": [], "task_id": None}
    current_input_params = input_params.copy(); current_input_params["calculation"] = "md"
    try:
        if "md_nstep" not in current_input_params or not isinstance(current_input_params["md_nstep"],int) or current_input_params["md_nstep"]<=0:
            results["errors"].append("'md_nstep' (positive integer) is required for MD."); results["success"]=False; return results
        current_input_params.setdefault("md_dt",1.0); current_input_params.setdefault("md_tfirst",300.0); current_input_params.setdefault("md_tlast",current_input_params["md_tfirst"])
        if "md_dumpfreq" in current_input_params and "out_interval" not in current_input_params:
            current_input_params["out_interval"]=current_input_params["md_dumpfreq"]; results["warnings"].append(f"Set 'out_interval={current_input_params['md_dumpfreq']}' from 'md_dumpfreq'.")
        elif "out_interval" not in current_input_params:
            current_input_params["out_interval"]=max(1,current_input_params["md_nstep"]//100 if current_input_params["md_nstep"]>0 else 1); results["warnings"].append(f"Set default 'out_interval={current_input_params['out_interval']}'.")

        stru_content_str, ntype = generate_abacus_stru(structure_dict,pseudo_potential_map,orbital_file_map,current_input_params.get("stru_coordinate_type","Cartesian_Angstrom"),current_input_params.get("stru_fixed_atoms_indices"))
        results["logs"]["stru_file_content"]=stru_content_str; current_input_params["ntype"]=ntype; current_input_params.setdefault("pseudo_dir","./")
        input_content_str = generate_abacus_input(current_input_params); results["logs"]["input_file_content"]=input_content_str
        kpt_mode = kpoints_definition.get("mode","Monkhorst-Pack").lower()
        kpt_content_str = generate_abacus_kpt(kpt_mode,structure_dict if kpt_mode in ["line","bandpath"] else None, kpoints_definition.get("size",[1,1,1]), kpoints_definition.get("shift",[0,0,0]), kpoints_definition.get("path_definition"), kpoints_definition.get("npoints_per_segment"), kpoints_definition.get("kpts_list"))
        results["logs"]["kpt_file_content"]=kpt_content_str
        full_pseudo = {fname:os.path.join(pseudo_base_path,fname) for _,fname in pseudo_potential_map.items()}
        full_orbital = None
        if orbital_file_map: full_orbital = {fname:os.path.join(orbital_base_path if orbital_base_path else pseudo_base_path, fname) for _,fname in orbital_file_map.items()}
        timeout = current_input_params.get("execution_timeout_seconds", 86400.0)
        exec_res = await execute_abacus_command(abacus_command,input_content_str,stru_content_str,kpt_content_str,full_pseudo,full_orbital,timeout,"md",current_input_params,structure_dict,kpoints_definition,pseudo_potential_map,orbital_file_map)
        results["task_id"]=exec_res.get("task_id"); results["logs"].update({"stdout":exec_res.get("stdout",""),"stderr":exec_res.get("stderr",""),"working_directory":exec_res.get("working_directory")})
        if not exec_res.get("success"):
            results["errors"].append(exec_res.get("error", "ABACUS MD exec failed.")); results["success"]=False
            if exec_res.get("stderr") and (not exec_res.get("error") or exec_res.get("stderr") not in exec_res.get("error","")): results["errors"].append(f"ABACUS stderr: {exec_res.get('stderr')}")
            return results
        output_parse = results["logs"]["stdout"]; md_log_name=f"running_md.log"
        log_path_suffix = os.path.join(exec_res["working_directory"],f"OUT.{current_input_params.get('suffix','ABACUS')}",md_log_name)
        log_path_root = os.path.join(exec_res["working_directory"],md_log_name); actual_log_parsed="stdout"
        if os.path.exists(log_path_suffix):
            try:
                with open(log_path_suffix,"r",encoding='utf-8') as f:output_parse=f.read();actual_log_parsed=log_path_suffix
            except Exception as e: results["warnings"].append(f"Failed to read {log_path_suffix}: {e}")
        elif os.path.exists(log_path_root):
            try:
                with open(log_path_root,"r",encoding='utf-8') as f:output_parse=f.read();actual_log_parsed=log_path_root
            except Exception as e: results["warnings"].append(f"Failed to read {log_path_root}: {e}")
        results["logs"]["parsed_log_file"]=actual_log_parsed
        parsed_out = parse_abacus_md_output(output_parse, current_input_params.get("md_nstep"))
        
        # Add interpretation and recommendations
        interpretation_data = result_interpreter.interpret_md_results(parsed_out, current_input_params)
        parsed_out["interpretation"] = interpretation_data["interpretation"]
        parsed_out["recommendations"] = interpretation_data["recommendations"]
        
        results["data"]=parsed_out; results["success"]=parsed_out.get("completed_all_steps",False)
        if exec_res.get("return_code")==-1: results["success"]=False; results["errors"].append(exec_res.get("error","MD timed out."))
        if parsed_out.get("warnings"):results["warnings"].extend(parsed_out["warnings"])
        if parsed_out.get("errors"):results["errors"].extend(parsed_out["errors"]);results["success"]=False
        if exec_res.get("success") and not results["success"] and not parsed_out.get("errors"): results["warnings"].append("MD finished but not all steps completed/parsed.")
    except FileNotFoundError as e:results["errors"].append(f"File not found (MD): {e}");results["success"]=False
    except ValueError as e:results["errors"].append(f"Input error (MD): {e}");results["success"]=False
    except Exception as e:results["errors"].append(f"Unexpected error (MD): {e}");results["success"]=False
    return results

async def test_run_md():
    if 'tempfile' not in globals(): import tempfile
    if 'shutil' not in globals(): import shutil
    print("--- Testing MD Core Logic ---")
    h2o_md = {"symbols":["O","H","H"],"positions":[[0,0,0],[0.757,0.586,0],[-0.757,0.586,0]],"cell":[[10,0,0],[0,10,0],[0,0,10]],"pbc":True}
    md_params = {"suffix":"H2O_md_test","ecutwfc":30,"md_nstep":10,"md_dt":0.5,"md_dumpfreq":2}
    kpts_md = {"mode":"Monkhorst-Pack","size":[1,1,1]}
    test_pseudo_md_dir = tempfile.mkdtemp(prefix="test_pseudos_md_")
    with open(os.path.join(test_pseudo_md_dir,"O_md.UPF"),"w") as f:f.write("O pseudo")
    with open(os.path.join(test_pseudo_md_dir,"H_md.UPF"),"w") as f:f.write("H pseudo")
    pseudo_map_md = {"O":"O_md.UPF","H":"H_md.UPF"}
    original_execute_md = globals().get('execute_abacus_command')

    async def mock_exec_md_ok(*_, **kwargs_exec_md):
        wd_md = tempfile.mkdtemp(prefix="abacus_md_ok_")
        out_dir_md = os.path.join(wd_md, f"OUT.{md_params['suffix']}")
        os.makedirs(out_dir_md, exist_ok=True)
        log_content_md = "MD_NSTEP = 10\n" + "\n".join([f"STEP: {i} E={-50.0+i*0.01}" for i in range(1,11)]) + "\nThe MD simulation has finished."
        with open(os.path.join(out_dir_md, "running_md.log"),"w") as f: f.write(log_content_md)
        return {"success":True,"return_code":0,"stdout":"...","stderr":"","working_directory":wd_md,"error":None,"task_id":"md_ok_1"}
    globals()['execute_abacus_command'] = mock_exec_md_ok
    res_md_ok = await run_md_core_logic(h2o_md,md_params,kpts_md,pseudo_map_md,pseudo_base_path=test_pseudo_md_dir)
    print(f"MD OK: Success={res_md_ok['success']}, TaskID={res_md_ok['task_id']}, Completed={res_md_ok['data'].get('completed_all_steps')}")
    assert res_md_ok["success"] and res_md_ok["task_id"]=="md_ok_1" and res_md_ok["data"]["completed_all_steps"]
    assert len(res_md_ok["data"]["trajectory"]) == md_params["md_nstep"]
    if os.path.exists(res_md_ok["logs"]["working_directory"]): shutil.rmtree(res_md_ok["logs"]["working_directory"])

    globals()['execute_abacus_command'] = original_execute_md # Restore
    shutil.rmtree(test_pseudo_md_dir)
    print("--- MD Tests Done ---")

async def run_phonon_dfpt_preparation_core_logic(
    structure_dict: Dict[str, Any], input_params: Dict[str, Any], kpoints_definition: Dict[str, Any],
    supercell_matrix: List[List[int]], pseudo_potential_map: Dict[str, str], orbital_file_map: Optional[Dict[str, str]] = None,
    abacus_command: str = DEFAULT_ABACUS_EXEC_COMMAND, pseudo_base_path: str = "./",
    orbital_base_path: Optional[str] = None, server_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    results: Dict[str, Any] = {"success": False, "data": None, "logs": {}, "errors": [], "warnings": [], "task_id": None}
    current_input_params = input_params.copy()
    current_input_params.update({"calculation":"scf","cal_force":1,"lr_dav":1,"drhoc_thresh":1e-10,"ethr_pert":1e-8,"deeq":0.01,"out_alllog":1})
    if "ph_ngq" not in current_input_params: results["warnings"].append("'ph_ngq' usually needed for DFPT FC generation.")
    elif not (isinstance(current_input_params["ph_ngq"],list) and len(current_input_params["ph_ngq"])==3 and all(isinstance(x,int) for x in current_input_params["ph_ngq"])):
        results["errors"].append("'ph_ngq' must be list of 3 ints."); results["success"]=False; return results
    try:
        stru_content_str, ntype = generate_abacus_stru(structure_dict,pseudo_potential_map,orbital_file_map,current_input_params.get("stru_coordinate_type","Cartesian_Angstrom"),current_input_params.get("stru_fixed_atoms_indices"))
        results["logs"]["stru_file_content"]=stru_content_str; current_input_params["ntype"]=ntype; current_input_params.setdefault("pseudo_dir","./")
        input_content_str = generate_abacus_input(current_input_params); results["logs"]["input_file_content"]=input_content_str
        kpt_mode = kpoints_definition.get("mode","Monkhorst-Pack").lower()
        kpt_content_str = generate_abacus_kpt(kpt_mode,structure_dict if kpt_mode in ["line","bandpath"] else None,kpoints_definition.get("size"),kpoints_definition.get("shift"),kpoints_definition.get("path_definition"),kpoints_definition.get("npoints_per_segment"),kpoints_definition.get("kpts_list"))
        results["logs"]["kpt_file_content"]=kpt_content_str
        full_pseudo = {fname:os.path.join(pseudo_base_path,fname) for _,fname in pseudo_potential_map.items()}
        full_orbital = None
        if orbital_file_map: full_orbital = {fname:os.path.join(orbital_base_path if orbital_base_path else pseudo_base_path, fname) for _,fname in orbital_file_map.items()}
        timeout = current_input_params.get("execution_timeout_seconds", 14400.0)
        exec_res = await execute_abacus_command(abacus_command,input_content_str,stru_content_str,kpt_content_str,full_pseudo,full_orbital,timeout,"phonon_dfpt_prep",current_input_params,structure_dict,kpoints_definition,pseudo_potential_map,orbital_file_map)
        results["task_id"]=exec_res.get("task_id"); results["logs"].update({"stdout":exec_res.get("stdout",""),"stderr":exec_res.get("stderr",""),"working_directory":exec_res.get("working_directory")})
        if not exec_res.get("success"):
            results["errors"].append(exec_res.get("error", "ABACUS DFPT SCF exec failed.")); results["success"]=False
            if exec_res.get("stderr") and (not exec_res.get("error") or exec_res.get("stderr") not in exec_res.get("error","")): results["errors"].append(f"ABACUS stderr: {exec_res.get('stderr')}")
            return results
        output_parse = results["logs"]["stdout"]; scf_log_name="running_scf.log"
        log_path_suffix = os.path.join(exec_res["working_directory"],f"OUT.{current_input_params.get('suffix','ABACUS')}",scf_log_name)
        log_path_root = os.path.join(exec_res["working_directory"],scf_log_name); actual_log_parsed="stdout"
        if os.path.exists(log_path_suffix):
            try:
                with open(log_path_suffix,"r",encoding='utf-8') as f:output_parse=f.read();actual_log_parsed=log_path_suffix
            except Exception: pass
        if actual_log_parsed=="stdout" and os.path.exists(log_path_root):
            try:
                with open(log_path_root,"r",encoding='utf-8') as f:output_parse=f.read();actual_log_parsed=log_path_root
            except Exception as e: results["warnings"].append(f"Failed to read {log_path_root}: {e}")
        results["logs"]["parsed_log_file"]=actual_log_parsed
        scf_parsed = parse_abacus_scf_output(output_parse); results["data"]={"scf_results":scf_parsed}; results["success"]=scf_parsed.get("converged",False)
        if not results["success"]: results["errors"].append("Underlying SCF for DFPT failed.")
        else:
            suffix=current_input_params.get('suffix','ABACUS'); fc_name1=f"{suffix}.fc"; fc_name2="FORCE_CONSTANT"
            fc_path1=os.path.join(exec_res["working_directory"],fc_name1); fc_path2=os.path.join(exec_res["working_directory"],f"OUT.{suffix}",fc_name1)
            fc_path3=os.path.join(exec_res["working_directory"],fc_name2); fc_path4=os.path.join(exec_res["working_directory"],f"OUT.{suffix}",fc_name2)
            found_fc=None
            if os.path.exists(fc_path1):found_fc=fc_path1
            elif os.path.exists(fc_path2):found_fc=fc_path2
            elif os.path.exists(fc_path3):found_fc=fc_path3
            elif os.path.exists(fc_path4):found_fc=fc_path4
            if found_fc: results["data"]["force_constant_file_path"]=found_fc; results["data"]["force_constant_file_name"]=os.path.basename(found_fc); results["warnings"].append(f"FC file '{os.path.basename(found_fc)}' likely generated.")
            else: results["warnings"].append(f"FC file (e.g. {fc_name1} or {fc_name2}) not found."); results["success"]=False
        if scf_parsed.get("warnings"):results["warnings"].extend(scf_parsed["warnings"])
        if scf_parsed.get("errors"):results["errors"].extend(scf_parsed["errors"]);results["success"]=False
    except FileNotFoundError as e:results["errors"].append(f"File not found (DFPT): {e}");results["success"]=False
    except ValueError as e:results["errors"].append(f"Input error (DFPT): {e}");results["success"]=False
    except Exception as e:results["errors"].append(f"Unexpected error (DFPT): {e}");results["success"]=False
    return results

async def test_run_phonon_prep():
    if 'tempfile' not in globals(): import tempfile
    if 'shutil' not in globals(): import shutil
    print("--- Testing Phonon DFPT Prep Core Logic ---")
    si_ph = {"symbols":["Si","Si"],"positions":[[0,0,0],[1.35,1.35,1.35]],"cell":[[5.4,0,0],[0,5.4,0],[0,0,5.4]],"pbc":True}
    ph_params = {"suffix":"Si_dfpt","ecutwfc":40,"ph_ngq":[2,2,1]}
    kpts_ph = {"mode":"Monkhorst-Pack","size":[2,2,2]}
    pseudo_map_ph = {"Si":"Si_ph.UPF"}
    test_pseudo_ph_dir = tempfile.mkdtemp(prefix="test_pseudos_ph_")
    with open(os.path.join(test_pseudo_ph_dir,"Si_ph.UPF"),"w") as f:f.write("Si pseudo ph")
    original_execute_ph = globals().get('execute_abacus_command')

    async def mock_exec_dfpt_ok(*_, **kwargs_exec_ph):
        wd_ph = tempfile.mkdtemp(prefix="abacus_dfpt_ok_")
        out_dir_ph = os.path.join(wd_ph, f"OUT.{ph_params['suffix']}")
        os.makedirs(out_dir_ph, exist_ok=True)
        with open(os.path.join(out_dir_ph,"running_scf.log"),"w") as f:f.write("!FINAL_ETOTAL_IS -150.0 Ry\nconvergence has been achieved\n")
        with open(os.path.join(wd_ph,f"{ph_params['suffix']}.fc"),"w") as f:f.write("Dummy FC data") # FC in root
        return {"success":True,"return_code":0,"stdout":"...","stderr":"","working_directory":wd_ph,"error":None,"task_id":"dfpt_ok_1"}
    globals()['execute_abacus_command'] = mock_exec_dfpt_ok
    res_ph_ok = await run_phonon_dfpt_preparation_core_logic(si_ph,ph_params,kpts_ph,[[1,0,0],[0,1,0],[0,0,1]],pseudo_map_ph,pseudo_base_path=test_pseudo_ph_dir)
    print(f"Phonon OK: Success={res_ph_ok['success']}, TaskID={res_ph_ok['task_id']}, SCF Converged={res_ph_ok['data']['scf_results'].get('converged')}, FC File={res_ph_ok['data'].get('force_constant_file_name')}")
    assert res_ph_ok["success"] and res_ph_ok["task_id"]=="dfpt_ok_1" and res_ph_ok["data"]["scf_results"]["converged"]
    assert res_ph_ok["data"]["force_constant_file_name"] == f"{ph_params['suffix']}.fc"
    if os.path.exists(res_ph_ok["logs"]["working_directory"]): shutil.rmtree(res_ph_ok["logs"]["working_directory"])

    globals()['execute_abacus_command'] = original_execute_ph # Restore
    shutil.rmtree(test_pseudo_ph_dir)
    print("--- Phonon DFPT Prep Tests Done ---")

async def run_all_calculation_execution_tests():
    # Ensure asyncio, tempfile, shutil are available in this scope if not globally
    if 'asyncio' not in globals(): import asyncio
    if 'tempfile' not in globals(): import tempfile
    if 'shutil' not in globals(): import shutil
    
    await test_run_scf()
    await test_run_optimization()
    await test_run_md()
    await test_run_phonon_prep()

if __name__ == '__main__':
    if 'asyncio' not in globals(): import asyncio # Final check for asyncio
    asyncio.run(run_all_calculation_execution_tests())