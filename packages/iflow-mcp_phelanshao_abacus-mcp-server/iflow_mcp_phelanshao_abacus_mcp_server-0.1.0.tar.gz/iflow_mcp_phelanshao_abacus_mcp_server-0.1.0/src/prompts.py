# src/prompts.py
"""
MCP Prompts for ABACUS MCP Server
Provides intelligent prompts for common ABACUS calculation workflows.
"""

from typing import Dict, Any, List, Optional
from mcp.server.fastmcp import FastMCP

class AbacusPromptProvider:
    """Provides MCP prompts for ABACUS calculation workflows."""
    
    def __init__(self):
        self.prompts = {
            "setup_scf_calculation": self._setup_scf_calculation_prompt(),
            "optimize_structure": self._optimize_structure_prompt(),
            "calculate_band_structure": self._calculate_band_structure_prompt(),
            "run_molecular_dynamics": self._run_molecular_dynamics_prompt(),
            "troubleshoot_convergence": self._troubleshoot_convergence_prompt(),
            "analyze_results": self._analyze_results_prompt(),
            "setup_pyabacus_workflow": self._setup_pyabacus_workflow_prompt()
        }
    
    def get_prompt(self, prompt_name: str) -> Dict[str, Any]:
        """Get a specific prompt by name."""
        return self.prompts.get(prompt_name, {"error": f"Prompt '{prompt_name}' not found"})
    
    def list_prompts(self) -> List[str]:
        """List all available prompts."""
        return list(self.prompts.keys())
    
    def _setup_scf_calculation_prompt(self) -> Dict[str, Any]:
        """Prompt for setting up SCF calculations."""
        return {
            "name": "setup_scf_calculation",
            "description": "Guide user through setting up a self-consistent field calculation",
            "arguments": [
                {
                    "name": "structure_info",
                    "description": "Information about the crystal structure (formula, lattice parameters, etc.)",
                    "required": True
                },
                {
                    "name": "accuracy_level", 
                    "description": "Desired accuracy level (low/medium/high)",
                    "required": False,
                    "default": "medium"
                },
                {
                    "name": "calculation_purpose",
                    "description": "Purpose of the calculation (ground_state, pre_optimization, etc.)",
                    "required": False
                }
            ],
            "template": """
I'll help you set up an ABACUS SCF calculation for {structure_info}.

Based on your accuracy level ({accuracy_level}) and purpose ({calculation_purpose}), here's the recommended workflow:

1. **Structure Creation**:
   - Use `create_structure` tool with your structure information
   - Validate the structure with `validate_structure`

2. **Parameter Selection**:
   - Use `suggest_parameters` for calculation_type="scf" and desired_accuracy="{accuracy_level}"
   - Key parameters to consider:
     * ecutwfc: Energy cutoff (higher for better accuracy)
     * k-points: Sampling density (denser for metals)
     * scf_thr: Convergence threshold

3. **Pseudopotentials**:
   - Ensure you have appropriate pseudopotential files
   - Common choices: ONCV, SG15, or PseudoDojo

4. **Execution**:
   - Use `run_scf` tool with your structure and parameters
   - Monitor convergence and adjust if needed

5. **Analysis**:
   - Check total energy convergence
   - Verify electronic structure properties
   - Use results for further calculations if needed

Would you like me to help you with any specific step?
            """,
            "follow_up_suggestions": [
                "What type of material are you studying?",
                "Do you have specific accuracy requirements?",
                "Are you planning follow-up calculations (bands, DOS, etc.)?"
            ]
        }
    
    def _optimize_structure_prompt(self) -> Dict[str, Any]:
        """Prompt for structure optimization workflows."""
        return {
            "name": "optimize_structure", 
            "description": "Guide user through geometry and cell optimization",
            "arguments": [
                {
                    "name": "optimization_type",
                    "description": "Type of optimization (geometry, cell, both)",
                    "required": True
                },
                {
                    "name": "initial_structure",
                    "description": "Description of the initial structure",
                    "required": True
                },
                {
                    "name": "constraints",
                    "description": "Any constraints on the optimization",
                    "required": False
                }
            ],
            "template": """
I'll guide you through ABACUS structure optimization for {initial_structure}.

For {optimization_type} optimization with constraints: {constraints}

**Recommended Workflow:**

1. **Initial SCF Calculation**:
   - First run SCF to ensure reasonable starting point
   - Check for convergence issues before optimization

2. **Optimization Setup**:
   - For geometry only: use `run_optimization` with calculation="relax"
   - For cell optimization: use calculation="cell-relax"
   - Set appropriate force_thr (typically 0.01-0.001 eV/Å)

3. **Parameter Considerations**:
   - Use converged k-points from SCF test
   - Consider slightly looser SCF convergence during optimization
   - Set reasonable relax_nmax (50-200 steps)

4. **Monitoring**:
   - Check force convergence at each step
   - Watch for oscillations or slow convergence
   - Adjust parameters if needed

5. **Validation**:
   - Verify final structure is reasonable
   - Check that forces are below threshold
   - Consider phonon analysis for stability

**PyABACUS Integration**:
If using PyABACUS for analysis:
```python
import pyabacus as abacus
# Use ModuleBase for mathematical operations
# Use hsolver for eigenvalue problems during optimization
```

Ready to start the optimization?
            """,
            "follow_up_suggestions": [
                "What convergence criteria do you need?",
                "Are there symmetry constraints to consider?",
                "Do you need to validate the optimized structure?"
            ]
        }
    
    def _calculate_band_structure_prompt(self) -> Dict[str, Any]:
        """Prompt for band structure calculations."""
        return {
            "name": "calculate_band_structure",
            "description": "Guide user through band structure calculations",
            "arguments": [
                {
                    "name": "crystal_system",
                    "description": "Crystal system (cubic, hexagonal, etc.)",
                    "required": True
                },
                {
                    "name": "material_type",
                    "description": "Type of material (semiconductor, metal, insulator)",
                    "required": False
                }
            ],
            "template": """
I'll help you calculate the band structure for your {crystal_system} {material_type} system.

**Band Structure Calculation Workflow:**

1. **Preparatory SCF**:
   - Run converged SCF calculation first
   - Use dense k-point grid for accurate charge density
   - Ensure `out_chg=1` to save charge density

2. **High-Symmetry Path**:
   - For {crystal_system} systems, typical paths include:
     * Cubic: Γ-X-M-Γ-R-X
     * Hexagonal: Γ-M-K-Γ-A-L-H-A
   - Use 20-50 points per segment for smooth bands

3. **NSCF Calculation**:
   - Set `calculation=nscf` and `init_chg=file`
   - Increase `nbands` to see more bands
   - Use `out_band=1` for band output

4. **PyABACUS Analysis**:
   ```python
   import pyabacus as m
   # Use ModuleBase for band analysis
   # Calculate effective masses, band gaps
   ```

5. **Post-Processing**:
   - Use `analyze_electronic_properties` for band gap analysis
   - Plot bands using visualization tools
   - Compare with experimental data if available

**Key Parameters for {material_type}:**
- Metals: Dense k-grids, many bands around Fermi level
- Semiconductors: Focus on valence/conduction bands
- Insulators: May need fewer bands, check gap convergence

Ready to proceed with the calculation?
            """,
            "follow_up_suggestions": [
                "What specific electronic properties are you interested in?",
                "Do you need spin-polarized calculations?",
                "Are you comparing with experimental data?"
            ]
        }
    
    def _run_molecular_dynamics_prompt(self) -> Dict[str, Any]:
        """Prompt for molecular dynamics simulations."""
        return {
            "name": "run_molecular_dynamics",
            "description": "Guide user through MD simulation setup",
            "arguments": [
                {
                    "name": "system_size",
                    "description": "Number of atoms in the system",
                    "required": True
                },
                {
                    "name": "temperature",
                    "description": "Target temperature in Kelvin",
                    "required": True
                },
                {
                    "name": "simulation_time",
                    "description": "Desired simulation time",
                    "required": False
                }
            ],
            "template": """
I'll help you set up molecular dynamics simulation for your {system_size}-atom system at {temperature}K.

**MD Simulation Workflow:**

1. **System Preparation**:
   - Start with optimized structure
   - Ensure reasonable cell size for periodic systems
   - Consider supercell if needed for {system_size} atoms

2. **MD Parameters**:
   - Time step: 0.5-2.0 fs (depends on lightest atoms)
   - Total steps: Calculate from desired {simulation_time}
   - Thermostat: NVT (Nose-Hoover) recommended for {temperature}K

3. **Computational Considerations**:
   - Use Γ-point only for large supercells
   - Lower ecutwfc acceptable for MD (faster)
   - Consider using LCAO basis for efficiency

4. **Monitoring**:
   - Track temperature, energy conservation
   - Check for structural integrity
   - Monitor pressure if needed

5. **PyABACUS Integration**:
   ```python
   import pyabacus as m
   # Use for trajectory analysis
   # Calculate radial distribution functions
   # Analyze vibrational properties
   ```

6. **Analysis**:
   - Structural properties (RDF, coordination)
   - Dynamical properties (diffusion, vibrations)
   - Thermodynamic properties

**Estimated Resources:**
- System size: {system_size} atoms
- Memory: ~{system_size * 0.1:.1f} GB (rough estimate)
- Time: Depends on ecutwfc and time step

Ready to configure the simulation?
            """,
            "follow_up_suggestions": [
                "What properties do you want to analyze?",
                "Do you need pressure control (NPT ensemble)?",
                "Are there specific structural features to monitor?"
            ]
        }
    
    def _troubleshoot_convergence_prompt(self) -> Dict[str, Any]:
        """Prompt for troubleshooting convergence issues."""
        return {
            "name": "troubleshoot_convergence",
            "description": "Help diagnose and fix convergence problems",
            "arguments": [
                {
                    "name": "calculation_type",
                    "description": "Type of calculation having issues",
                    "required": True
                },
                {
                    "name": "error_symptoms",
                    "description": "Description of the convergence problem",
                    "required": True
                }
            ],
            "template": """
I'll help you troubleshoot the convergence issues in your {calculation_type} calculation.

**Problem**: {error_symptoms}

**Diagnostic Steps:**

1. **Check Log Files**:
   - Use `diagnose_failure` tool with your error logs
   - Look for specific error patterns and warnings

2. **Common Solutions for {calculation_type}**:

   **SCF Convergence Issues**:
   - Reduce mixing_beta (try 0.1-0.3)
   - Change mixing_type (pulay → broyden)
   - Increase scf_nmax
   - Check k-point sampling

   **Geometry Optimization Issues**:
   - Reduce force_thr temporarily
   - Check for imaginary frequencies
   - Use different optimization algorithm
   - Verify initial structure quality

   **Electronic Structure Issues**:
   - Increase ecutwfc
   - Add more bands (nbands)
   - Check pseudopotential quality
   - Consider spin polarization

3. **PyABACUS Diagnostics**:
   ```python
   import pyabacus as m
   # Use ModuleBase for numerical analysis
   # Check matrix conditioning, eigenvalue problems
   ```

4. **Parameter Validation**:
   - Use `validate_input` tool to check parameters
   - Verify structure with `validate_structure`
   - Check pseudopotential compatibility

5. **Systematic Approach**:
   - Start with minimal system
   - Gradually increase accuracy
   - Test parameter sensitivity

**Next Steps:**
1. Run diagnostics on your log files
2. Try suggested parameter adjustments
3. Test with simpler system if needed

Would you like me to analyze your specific error logs?
            """,
            "follow_up_suggestions": [
                "Can you share the error log content?",
                "What parameters have you already tried?",
                "Is this a new system or previously working setup?"
            ]
        }
    
    def _analyze_results_prompt(self) -> Dict[str, Any]:
        """Prompt for analyzing calculation results."""
        return {
            "name": "analyze_results",
            "description": "Guide user through result analysis and interpretation",
            "arguments": [
                {
                    "name": "calculation_type",
                    "description": "Type of completed calculation",
                    "required": True
                },
                {
                    "name": "analysis_goals",
                    "description": "What properties or insights are needed",
                    "required": True
                }
            ],
            "template": """
I'll help you analyze your {calculation_type} results to achieve: {analysis_goals}

**Analysis Workflow:**

1. **Data Extraction**:
   - Use `get_calculation_results` to retrieve output files
   - Check calculation completion and convergence
   - Identify available data types

2. **Property Analysis**:
   
   **For SCF Results**:
   - Total energy and convergence
   - Electronic structure properties
   - Charge density analysis
   
   **For Optimization Results**:
   - Final structure validation
   - Energy landscape analysis
   - Force and stress analysis
   
   **For Band Structure**:
   - Use `analyze_electronic_properties` for band gaps
   - Identify band character and symmetry
   - Compare with experimental data
   
   **For MD Results**:
   - Trajectory analysis
   - Thermodynamic properties
   - Structural evolution

3. **PyABACUS Post-Processing**:
   ```python
   import pyabacus as m
   
   # For mathematical analysis
   sphbes = m.ModuleBase.Sphbes()
   
   # For matrix operations
   # Use hsolver for eigenvalue analysis
   
   # Example: Analyze orbital overlaps
   # result = sphbes.sphbesj(l, x)
   ```

4. **Validation and Interpretation**:
   - Compare with literature values
   - Check physical reasonableness
   - Assess convergence with respect to parameters

5. **Visualization and Reporting**:
   - Generate plots and figures
   - Prepare summary of key findings
   - Document methodology and parameters

**Specific Analysis for {analysis_goals}**:
- Extract relevant properties from output
- Apply appropriate analysis methods
- Validate results against expectations

Ready to start the analysis? Please share your calculation results.
            """,
            "follow_up_suggestions": [
                "What specific properties are most important?",
                "Do you have reference data for comparison?",
                "Are you preparing results for publication?"
            ]
        }
    
    def _setup_pyabacus_workflow_prompt(self) -> Dict[str, Any]:
        """Prompt for PyABACUS workflow setup."""
        return {
            "name": "setup_pyabacus_workflow",
            "description": "Guide user through PyABACUS Python interface usage",
            "arguments": [
                {
                    "name": "workflow_type",
                    "description": "Type of PyABACUS workflow needed",
                    "required": True
                },
                {
                    "name": "python_experience",
                    "description": "User's Python experience level",
                    "required": False,
                    "default": "intermediate"
                }
            ],
            "template": """
I'll help you set up a PyABACUS workflow for {workflow_type}.

**PyABACUS Setup and Usage:**

1. **Installation and Import**:
   ```python
   # Ensure PyABACUS is installed
   import pyabacus as m
   
   # Available modules:
   # - ModuleBase: Mathematical functions
   # - ModuleNAO: Numerical atomic orbitals  
   # - hsolver: Hamiltonian solvers
   ```

2. **Basic Usage Examples**:
   
   **Spherical Bessel Functions**:
   ```python
   import pyabacus as m
   s = m.ModuleBase.Sphbes()
   
   # Calculate spherical Bessel function
   result = s.sphbesj(l=1, x=0.0)
   
   # For arrays
   import numpy as np
   r = np.linspace(0, 10, 100)
   jl = np.zeros_like(r)
   s.sphbesj(n=100, r=r, q=10, l=1, jl=jl)
   ```

   **Matrix Diagonalization**:
   ```python
   # Use hsolver for eigenvalue problems
   # (Specific usage depends on your matrices)
   ```

3. **Integration with ABACUS Calculations**:
   - Use PyABACUS for pre-processing input
   - Analyze ABACUS output with Python tools
   - Combine with ASE for structure manipulation

4. **Workflow for {workflow_type}**:
   
   **Data Analysis Workflow**:
   - Load ABACUS output files
   - Use PyABACUS for mathematical operations
   - Generate plots and analysis
   
   **Pre-processing Workflow**:
   - Generate specialized input files
   - Calculate orbital overlaps
   - Prepare k-point grids

5. **Best Practices**:
   - Type hints for better code quality
   - Error handling for robust workflows
   - Documentation and reproducibility

6. **Example Complete Workflow**:
   ```python
   import pyabacus as m
   import numpy as np
   import matplotlib.pyplot as plt
   
   # Your specific workflow here
   # Based on {workflow_type}
   ```

**For {python_experience} users**:
- Start with simple examples
- Build complexity gradually
- Use Jupyter notebooks for interactive development

Ready to implement your PyABACUS workflow?
            """,
            "follow_up_suggestions": [
                "What specific PyABACUS functions do you need?",
                "Are you working with existing ABACUS data?",
                "Do you need help with Python environment setup?"
            ]
        }

# Global prompt provider instance
prompt_provider = AbacusPromptProvider()