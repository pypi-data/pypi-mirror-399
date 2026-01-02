# src/tools/task_management.py
from typing import Dict, Any, Optional, List, Tuple
import datetime
import uuid
import json
import os
import asyncio # For potential future async operations, not strictly needed for simplified version

# --- In-memory "database" for tasks ---
# For a more robust solution, consider SQLite or a simple file-based JSON store.
# This will be lost if the server restarts.
TASKS_DB: Dict[str, Dict[str, Any]] = {}
TASKS_DB_FILE = "abacus_tasks_db.json" # Simple file persistence

# Lock for file operations if we go with file-based DB to prevent race conditions
# For asyncio, an asyncio.Lock would be appropriate. For now, this is conceptual.
# DB_LOCK = asyncio.Lock() # If using async file I/O

def _load_tasks_db_from_file() -> Dict[str, Dict[str, Any]]:
    """Loads tasks from a JSON file if it exists."""
    if os.path.exists(TASKS_DB_FILE):
        try:
            with open(TASKS_DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"[TaskManagement] Error loading tasks DB from {TASKS_DB_FILE}: {e}")
            # Fallback to empty or handle corruption (e.g., backup/rename old file)
            return {} 
    return {}

def _save_tasks_db_to_file(tasks_data: Dict[str, Dict[str, Any]]):
    """Saves tasks to a JSON file."""
    try:
        with open(TASKS_DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(tasks_data, f, indent=4, default=str) # Use default=str for datetime etc.
    except IOError as e:
        print(f"[TaskManagement] Error saving tasks DB to {TASKS_DB_FILE}: {e}")

# Initialize TASKS_DB from file at startup (module load time)
TASKS_DB = _load_tasks_db_from_file()


# --- Helper functions for task management ---

def register_new_task(
    calculation_type: str,
    input_parameters: Dict[str, Any],
    structure_dict: Optional[Dict[str, Any]] = None,
    kpoints_definition: Optional[Dict[str, Any]] = None,
    pseudo_map: Optional[Dict[str, str]] = None,
    orbital_map: Optional[Dict[str, str]] = None,
    working_directory: Optional[str] = None # Provided by execute_abacus_command
) -> str:
    """
    Registers a new calculation task when it's about to start.
    Returns the generated task_id.
    """
    task_id = str(uuid.uuid4())
    TASKS_DB[task_id] = {
        "task_id": task_id,
        "status": "submitted", # Initial status
        "calculation_type": calculation_type,
        "submission_time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "start_time": None,
        "end_time": None,
        "input_summary": { # Store a summary, not necessarily all huge dicts
            "calculation_type": calculation_type,
            "num_atoms": len(structure_dict.get("symbols", [])) if structure_dict else None,
            # Add other key params from input_parameters if desired
        },
        "working_directory": working_directory,
        "results_summary": None, # e.g., energy, converged status
        "error_message": None,
        # Full results and logs might be stored elsewhere or linked if too large
        # For this simplified version, we might store some log snippets or final result dict.
        "detailed_results_ref": None, # Placeholder for path or key to full results
        "logs_ref": None # Placeholder for path or key to full logs
    }
    _save_tasks_db_to_file(TASKS_DB)
    return task_id

def update_task_status(task_id: str, status: str, start_time: Optional[bool] = False, end_time: Optional[bool] = False):
    """Updates the status of a task. Optionally sets start/end times."""
    if task_id in TASKS_DB:
        TASKS_DB[task_id]["status"] = status
        if start_time:
            TASKS_DB[task_id]["start_time"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        if end_time:
             TASKS_DB[task_id]["end_time"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _save_tasks_db_to_file(TASKS_DB)
    else:
        print(f"[TaskManagement] Warning: Attempted to update status for non-existent task_id: {task_id}")


def record_task_completion(
    task_id: str,
    success: bool,
    results_data: Optional[Dict[str, Any]], # The 'data' part of a typical tool output
    logs_data: Optional[Dict[str, Any]], # The 'logs' part (e.g., stdout, stderr, work_dir)
    errors_list: Optional[List[str]]
):
    """Records the completion (success or failure) of a task."""
    if task_id in TASKS_DB:
        TASKS_DB[task_id]["status"] = "completed" if success else "failed"
        TASKS_DB[task_id]["end_time"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        if success and results_data:
            # Store a summary or key results. Avoid storing huge data directly in DB if possible.
            # Example: extract energy, convergence from results_data
            summary = {}
            if results_data.get("converged") is not None:
                summary["converged"] = results_data["converged"]
            if results_data.get("total_energy_ev") is not None:
                summary["total_energy_ev"] = results_data["total_energy_ev"]
            elif results_data.get("final_total_energy_ev") is not None: # from optimization
                summary["final_total_energy_ev"] = results_data["final_total_energy_ev"]
            TASKS_DB[task_id]["results_summary"] = summary
            # TASKS_DB[task_id]["detailed_results_ref"] = "path/to/results.json" # Example
        
        if errors_list:
            TASKS_DB[task_id]["error_message"] = "; ".join(errors_list)
        
        # Store reference to logs (e.g., working directory where logs are)
        if logs_data and logs_data.get("working_directory"):
            TASKS_DB[task_id]["logs_ref"] = logs_data.get("working_directory")
        elif logs_data and logs_data.get("stderr"): # Fallback for simple errors
             TASKS_DB[task_id]["logs_ref"] = {"stderr_snippet": logs_data["stderr"][:500]}


        _save_tasks_db_to_file(TASKS_DB)
    else:
         print(f"[TaskManagement] Warning: Attempted to record completion for non-existent task_id: {task_id}")

# --- Core Logic for Task Management Tools ---

async def get_calculation_status_core_logic(task_id: str) -> Dict[str, Any]:
    task_info = TASKS_DB.get(task_id)
    if not task_info:
        return {"success": False, "error": "Task ID not found."}
    
    return {
        "success": True,
        "task_id": task_id,
        "status": task_info.get("status"),
        "calculation_type": task_info.get("calculation_type"),
        "submission_time": task_info.get("submission_time"),
        "start_time": task_info.get("start_time"),
        "end_time": task_info.get("end_time"),
        "results_summary": task_info.get("results_summary"),
        "error_message": task_info.get("error_message")
    }

async def list_recent_calculations_core_logic(
    count: int = 10, 
    status_filter: Optional[str] = None
) -> Dict[str, Any]:
    
    # Sort tasks by submission_time (descending) to get recent ones
    # ISO format strings can be compared directly for recency.
    try:
        sorted_tasks = sorted(
            TASKS_DB.values(), 
            key=lambda t: t.get("submission_time", ""), 
            reverse=True
        )
    except Exception as e: # Catch any error during sorting (e.g. if submission_time is missing/malformed)
        return {"success": False, "tasks": [], "error": f"Error sorting tasks: {str(e)}"}

    
    filtered_tasks = []
    for task in sorted_tasks:
        if status_filter:
            if task.get("status", "").lower() == status_filter.lower():
                filtered_tasks.append(task)
        else:
            filtered_tasks.append(task)
            
    summaries = []
    for task_item in filtered_tasks[:count]:
        summaries.append({
            "task_id": task_item.get("task_id"),
            "calculation_type": task_item.get("calculation_type"),
            "status": task_item.get("status"),
            "submission_time": task_item.get("submission_time"),
            "results_summary": task_item.get("results_summary")
        })
        
    return {"success": True, "tasks": summaries}


async def get_calculation_results_core_logic(task_id: str) -> Dict[str, Any]:
    """
    Retrieves stored results and logs for a completed/failed task.
    In this simplified version, it mainly returns info from TASKS_DB.
    A full version would load detailed results/logs from their stored location.
    """
    task_info = TASKS_DB.get(task_id)
    if not task_info:
        return {"success": False, "error": "Task ID not found."}

    if task_info.get("status") not in ["completed", "failed"]:
        return {
            "success": False, 
            "error": f"Task '{task_id}' is still '{task_info.get('status')}'. Results are available only for 'completed' or 'failed' tasks.",
            "current_status": task_info.get("status")
        }
        
    # For this version, we assume results_summary and logs_ref are what we have.
    # A real implementation would use detailed_results_ref and logs_ref to fetch full data.
    # For example, if logs_ref is a working directory:
    # log_content = {}
    # if task_info.get("logs_ref") and isinstance(task_info["logs_ref"], str) and os.path.isdir(task_info["logs_ref"]):
    #     try:
    #         # Attempt to read common log files from that directory
    #         # This is just an example, would need more robust logic
    #         stdout_path = os.path.join(task_info["logs_ref"], "running_scf.log") # Or other typical names
    #         if os.path.exists(stdout_path):
    #             with open(stdout_path, 'r') as f: log_content["stdout"] = f.read(20000) # Limit size
    #         # ... read stderr etc.
    #     except Exception as e:
    #         log_content["error_reading_logs"] = str(e)
            
    return {
        "success": True,
        "task_id": task_id,
        "status": task_info.get("status"),
        "calculation_type": task_info.get("calculation_type"),
        "results_summary": task_info.get("results_summary"),
        "error_message": task_info.get("error_message"),
        "logs_reference": task_info.get("logs_ref"), # Could be path or a snippet
        "notes": ["This simplified version provides summary data. Full results/logs might be in the working directory referenced by 'logs_reference'."]
    }

async def monitor_calculation_core_logic(task_id: str) -> Dict[str, Any]:
    """
    Simplified monitoring: returns status.
    True monitoring requires non-blocking execution and log tailing.
    """
    task_info = TASKS_DB.get(task_id)
    if not task_info:
        return {"success": False, "error": "Task ID not found."}
    
    # In a true async setup, we might try to tail logs from task_info["working_directory"]
    # For now, just return the stored status.
    return {
        "success": True,
        "task_id": task_id,
        "status": task_info.get("status"),
        "message": "Simplified monitoring: provides current stored status. For live log updates, the execution model needs to be fully asynchronous.",
        "current_log_snippet": None # Placeholder
    }

async def cancel_calculation_core_logic(task_id: str) -> Dict[str, Any]:
    """
    Simplified cancellation: marks task as 'cancelled' if it's in a cancellable state.
    True cancellation requires process management.
    """
    task_info = TASKS_DB.get(task_id)
    if not task_info:
        return {"success": False, "error": "Task ID not found."}

    current_status = task_info.get("status")
    if current_status in ["submitted", "starting"]: # "running" would be ideal if we had PIDs
        TASKS_DB[task_id]["status"] = "cancelled_request" # Mark as requested
        TASKS_DB[task_id]["end_time"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        TASKS_DB[task_id]["error_message"] = "Cancellation requested by user."
        _save_tasks_db_to_file(TASKS_DB)
        return {
            "success": True, 
            "message": f"Cancellation requested for task '{task_id}'. Actual termination depends on the execution backend (currently simplified).",
            "new_status": "cancelled_request"
        }
    elif current_status in ["completed", "failed", "cancelled", "cancelled_request"]:
         return {"success": False, "message": f"Task '{task_id}' is already in a terminal state ('{current_status}') and cannot be cancelled."}
    else: # e.g. running, but we don't have PID to kill it in this simplified model
        return {"success": False, "message": f"Task '{task_id}' is in status '{current_status}'. True cancellation is not supported in this simplified version once fully running."}