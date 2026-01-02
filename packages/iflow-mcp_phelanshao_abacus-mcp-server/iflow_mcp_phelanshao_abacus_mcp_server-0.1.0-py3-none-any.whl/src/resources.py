# src/resources.py
"""
MCP Resources for ABACUS MCP Server
Provides access to calculation results, documentation, and system information.
"""

from typing import Dict, Any, List, Optional
from mcp.server.fastmcp import FastMCP
import os
import json
import glob
from pathlib import Path

# Resource URIs
CALCULATION_RESULTS_URI = "abacus://calculations/{task_id}/results"
CALCULATION_LOGS_URI = "abacus://calculations/{task_id}/logs"
SYSTEM_STATUS_URI = "abacus://system/status"
DOCUMENTATION_URI = "abacus://docs/{topic}"
EXAMPLES_URI = "abacus://examples/{example_type}"

class AbacusResourceProvider:
    """Provides MCP resources for ABACUS calculations and documentation."""
    
    def __init__(self, work_dir: str = "./abacus_calculations"):
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(exist_ok=True)
    
    async def get_calculation_results(self, task_id: str) -> Dict[str, Any]:
        """Get calculation results for a specific task."""
        task_dir = self.work_dir / task_id
        if not task_dir.exists():
            return {"error": f"Task {task_id} not found"}
        
        results = {}
        
        # Look for common ABACUS output files
        output_files = {
            "running_scf.log": "main_log",
            "OUT.ABACUS": "output_summary", 
            "STRU_ION_D": "final_structure",
            "istate.info": "eigenvalues",
            "BANDS_1.dat": "band_structure",
            "DOS1_smearing.dat": "density_of_states",
            "SPIN1_CHG.cube": "charge_density"
        }
        
        for filename, key in output_files.items():
            filepath = task_dir / filename
            if filepath.exists():
                try:
                    with open(filepath, 'r') as f:
                        results[key] = f.read()
                except Exception as e:
                    results[key] = f"Error reading {filename}: {str(e)}"
        
        return results
    
    async def get_calculation_logs(self, task_id: str) -> Dict[str, Any]:
        """Get calculation logs for a specific task."""
        task_dir = self.work_dir / task_id
        if not task_dir.exists():
            return {"error": f"Task {task_id} not found"}
        
        logs = {}
        
        # Collect all log files
        log_patterns = ["*.log", "*.out", "*.err"]
        for pattern in log_patterns:
            for log_file in task_dir.glob(pattern):
                try:
                    with open(log_file, 'r') as f:
                        logs[log_file.name] = f.read()
                except Exception as e:
                    logs[log_file.name] = f"Error reading {log_file.name}: {str(e)}"
        
        return logs
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and configuration."""
        return {
            "abacus_version": await self._get_abacus_version(),
            "work_directory": str(self.work_dir),
            "available_pseudopotentials": await self._list_pseudopotentials(),
            "recent_calculations": await self._list_recent_calculations(),
            "system_resources": await self._get_system_resources()
        }
    
    async def get_documentation(self, topic: str) -> Dict[str, Any]:
        """Get documentation for specific topics."""
        docs = {
            "input_parameters": {
                "description": "ABACUS input parameters reference",
                "content": await self._get_input_params_doc()
            },
            "calculation_types": {
                "description": "Available calculation types in ABACUS",
                "content": await self._get_calc_types_doc()
            },
            "troubleshooting": {
                "description": "Common issues and solutions",
                "content": await self._get_troubleshooting_doc()
            },
            "pyabacus": {
                "description": "PyABACUS Python interface documentation",
                "content": await self._get_pyabacus_doc()
            }
        }
        
        return docs.get(topic, {"error": f"Documentation topic '{topic}' not found"})
    
    async def get_examples(self, example_type: str) -> Dict[str, Any]:
        """Get example configurations and scripts."""
        examples = {
            "scf": await self._get_scf_examples(),
            "relax": await self._get_relax_examples(),
            "band_structure": await self._get_band_examples(),
            "dos": await self._get_dos_examples(),
            "md": await self._get_md_examples()
        }
        
        return examples.get(example_type, {"error": f"Example type '{example_type}' not found"})
    
    # Helper methods
    async def _get_abacus_version(self) -> str:
        """Get ABACUS version information."""
        try:
            import subprocess
            result = subprocess.run(['abacus', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.stdout.strip() if result.returncode == 0 else "Unknown"
        except:
            return "Not available"
    
    async def _list_pseudopotentials(self) -> List[str]:
        """List available pseudopotential files."""
        pseudo_dir = Path("./pseudos")
        if not pseudo_dir.exists():
            return []
        
        pseudo_files = []
        for ext in ["*.upf", "*.UPF", "*.psp8", "*.xml"]:
            pseudo_files.extend([f.name for f in pseudo_dir.glob(ext)])
        
        return sorted(pseudo_files)
    
    async def _list_recent_calculations(self) -> List[Dict[str, Any]]:
        """List recent calculation directories."""
        calculations = []
        for task_dir in self.work_dir.iterdir():
            if task_dir.is_dir():
                stat = task_dir.stat()
                calculations.append({
                    "task_id": task_dir.name,
                    "created": stat.st_ctime,
                    "modified": stat.st_mtime
                })
        
        return sorted(calculations, key=lambda x: x["modified"], reverse=True)[:10]
    
    async def _get_system_resources(self) -> Dict[str, Any]:
        """Get system resource information."""
        import psutil
        return {
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "memory_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
            "disk_free_gb": round(psutil.disk_usage('.').free / (1024**3), 2)
        }
    
    async def _get_input_params_doc(self) -> str:
        """Get input parameters documentation."""
        return """
ABACUS Input Parameters Reference:

GENERAL PARAMETERS:
- calculation: Type of calculation (scf, relax, cell-relax, md, nscf)
- ecutwfc: Plane wave energy cutoff in Ry
- nbands: Number of bands (auto or integer)
- basis_type: Basis set type (pw, lcao, lcao_in_pw)
- ks_solver: Kohn-Sham equation solver (cg, dav, lapack, genelpa, scalapack_gvx)

SCF PARAMETERS:
- scf_thr: SCF convergence threshold
- scf_nmax: Maximum SCF iterations
- mixing_type: SCF mixing method (plain, pulay, broyden)
- mixing_beta: SCF mixing parameter

STRUCTURE OPTIMIZATION:
- force_thr: Force convergence threshold
- relax_nmax: Maximum optimization steps
- relax_method: Optimization algorithm (bfgs, cg, sd)

For complete documentation, see: https://abacus.deepmodeling.com/en/latest/
        """
    
    async def _get_calc_types_doc(self) -> str:
        """Get calculation types documentation."""
        return """
ABACUS Calculation Types:

1. SCF (Self-Consistent Field):
   - Basic ground state calculation
   - Outputs: total energy, charge density, electronic structure

2. RELAX (Geometry Optimization):
   - Optimizes atomic positions
   - Outputs: optimized structure, forces

3. CELL-RELAX (Cell Optimization):
   - Optimizes both atomic positions and cell parameters
   - Outputs: optimized structure and cell

4. MD (Molecular Dynamics):
   - Time evolution simulation
   - Outputs: trajectory, thermodynamic properties

5. NSCF (Non-Self-Consistent Field):
   - Used for band structure and DOS calculations
   - Requires converged charge density from SCF
        """
    
    async def _get_troubleshooting_doc(self) -> str:
        """Get troubleshooting documentation."""
        return """
Common ABACUS Issues and Solutions:

1. SCF Convergence Problems:
   - Increase scf_nmax
   - Adjust mixing_beta (try 0.1-0.7)
   - Use different mixing_type (pulay, broyden)
   - Check k-point sampling

2. Memory Issues:
   - Reduce ecutwfc
   - Use fewer k-points
   - Enable memory optimization flags

3. Force/Stress Calculation Errors:
   - Ensure pseudopotentials support force calculation
   - Check STRU file format
   - Verify cell parameters

4. File I/O Errors:
   - Check file permissions
   - Verify pseudopotential file paths
   - Ensure sufficient disk space
        """
    
    async def _get_pyabacus_doc(self) -> str:
        """Get PyABACUS documentation."""
        return """
PyABACUS Python Interface:

PyABACUS provides Python bindings for ABACUS functionality:

1. Basic Usage:
   import pyabacus as abacus
   
2. Available Modules:
   - ModuleBase: Basic mathematical functions
   - ModuleNAO: Numerical atomic orbitals
   - hsolver: Hamiltonian solvers

3. Example - Spherical Bessel Functions:
   import pyabacus as m
   s = m.ModuleBase.Sphbes()
   result = s.sphbesj(1, 0.0)

4. Matrix Diagonalization:
   Use pyabacus.hsolver for eigenvalue problems

For more examples, see: https://github.com/deepmodeling/abacus-develop/tree/develop/python
        """
    
    async def _get_scf_examples(self) -> Dict[str, Any]:
        """Get SCF calculation examples."""
        return {
            "basic_scf": {
                "input_params": {
                    "calculation": "scf",
                    "ecutwfc": 100,
                    "scf_thr": 1e-6,
                    "basis_type": "pw"
                },
                "kpoints": {"mode": "Monkhorst-Pack", "size": [4, 4, 4]},
                "description": "Basic SCF calculation for crystalline systems"
            }
        }
    
    async def _get_relax_examples(self) -> Dict[str, Any]:
        """Get relaxation examples."""
        return {
            "geometry_optimization": {
                "input_params": {
                    "calculation": "relax",
                    "force_thr": 0.01,
                    "relax_nmax": 100
                },
                "description": "Geometry optimization with force threshold"
            }
        }
    
    async def _get_band_examples(self) -> Dict[str, Any]:
        """Get band structure examples."""
        return {
            "band_structure": {
                "scf_params": {"calculation": "scf", "out_chg": 1},
                "nscf_params": {"calculation": "nscf", "init_chg": "file", "out_band": 1},
                "kpath": {"mode": "Line", "path": "G-X-L-G", "npoints": 20},
                "description": "Band structure calculation along high-symmetry path"
            }
        }
    
    async def _get_dos_examples(self) -> Dict[str, Any]:
        """Get DOS examples."""
        return {
            "density_of_states": {
                "scf_params": {"calculation": "scf", "out_chg": 1},
                "nscf_params": {"calculation": "nscf", "init_chg": "file", "out_dos": 1},
                "kpoints": {"mode": "Monkhorst-Pack", "size": [8, 8, 8]},
                "description": "Density of states calculation with dense k-grid"
            }
        }
    
    async def _get_md_examples(self) -> Dict[str, Any]:
        """Get MD examples."""
        return {
            "molecular_dynamics": {
                "input_params": {
                    "calculation": "md",
                    "md_nstep": 1000,
                    "md_dt": 1.0,
                    "md_tfirst": 300,
                    "md_thermostat": "nhc"
                },
                "description": "NVT molecular dynamics simulation"
            }
        }

# Global resource provider instance
resource_provider = AbacusResourceProvider()