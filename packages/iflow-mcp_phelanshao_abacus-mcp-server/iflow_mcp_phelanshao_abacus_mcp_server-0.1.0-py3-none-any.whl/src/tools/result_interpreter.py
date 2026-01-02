# src/tools/result_interpreter.py
"""
Result interpretation and recommendation module for ABACUS calculations.
Provides intelligent analysis and suggestions based on calculation results.
"""

from typing import Dict, Any, List, Optional
import numpy as np

class AbacusResultInterpreter:
    """Interprets ABACUS calculation results and provides recommendations."""
    
    def __init__(self):
        self.convergence_thresholds = {
            "scf_energy_change": 1e-6,  # Ry
            "force_threshold": 0.01,    # eV/Å
            "stress_threshold": 0.5,    # kBar
            "md_temperature_stability": 50.0  # K
        }
    
    def interpret_scf_results(self, scf_data: Dict[str, Any], input_params: Dict[str, Any]) -> Dict[str, Any]:
        """Interpret SCF calculation results."""
        interpretation = []
        recommendations = []
        
        converged = scf_data.get("converged", False)
        total_energy_ry = scf_data.get("total_energy_ry")
        fermi_energy_ry = scf_data.get("fermi_energy_ry")
        scf_iterations = scf_data.get("scf_iterations", 0)
        
        # Convergence analysis
        if converged:
            interpretation.append("SCF calculation converged successfully.")
            if scf_iterations < 10:
                interpretation.append("Fast convergence achieved, indicating good initial guess or well-conditioned system.")
            elif scf_iterations > 50:
                interpretation.append("Slow convergence observed, but calculation eventually converged.")
                recommendations.append("Consider adjusting mixing parameters for faster convergence in future calculations.")
        else:
            interpretation.append("SCF calculation failed to converge within the specified iterations.")
            recommendations.extend([
                "Increase scf_nmax to allow more iterations",
                "Reduce mixing_beta (try 0.1-0.3) for better stability",
                "Consider using different mixing_type (pulay, broyden)",
                "Check if system is metallic and requires smearing"
            ])
        
        # Energy analysis
        if total_energy_ry is not None:
            total_energy_ev = total_energy_ry * 13.6057  # Convert to eV
            interpretation.append(f"Total energy: {total_energy_ry:.6f} Ry ({total_energy_ev:.6f} eV)")
            
            # Energy per atom analysis
            if "structure_info" in scf_data:
                natoms = scf_data["structure_info"].get("natoms", 1)
                energy_per_atom = total_energy_ev / natoms
                interpretation.append(f"Energy per atom: {energy_per_atom:.3f} eV")
                
                if energy_per_atom > 0:
                    recommendations.append("Positive energy per atom detected - check structure and pseudopotentials.")
        
        # Electronic structure analysis
        if fermi_energy_ry is not None:
            fermi_energy_ev = fermi_energy_ry * 13.6057
            interpretation.append(f"Fermi energy: {fermi_energy_ry:.6f} Ry ({fermi_energy_ev:.6f} eV)")
            
            # Metallicity check based on smearing
            smearing_method = input_params.get("smearing_method", "").lower()
            if smearing_method and smearing_method != "none":
                interpretation.append("System treated as metallic (smearing applied).")
            else:
                interpretation.append("System treated as insulating (no smearing).")
                recommendations.append("If system is metallic, consider adding smearing parameters.")
        
        # Parameter recommendations
        ecutwfc = input_params.get("ecutwfc", 0)
        if ecutwfc < 50:
            recommendations.append("Consider increasing ecutwfc for better accuracy (typical range: 50-150 Ry).")
        elif ecutwfc > 200:
            recommendations.append("Very high ecutwfc detected - ensure this level of accuracy is necessary.")
        
        return {
            "interpretation": interpretation,
            "recommendations": recommendations
        }
    
    def interpret_optimization_results(self, opt_data: Dict[str, Any], input_params: Dict[str, Any]) -> Dict[str, Any]:
        """Interpret geometry/cell optimization results."""
        interpretation = []
        recommendations = []
        
        converged = opt_data.get("converged", False)
        optimization_steps = opt_data.get("optimization_steps", 0)
        max_force = opt_data.get("max_force")
        total_force = opt_data.get("total_force")
        
        # Convergence analysis
        if converged:
            interpretation.append(f"Optimization converged successfully in {optimization_steps} steps.")
            if optimization_steps < 5:
                interpretation.append("Very fast convergence - structure was already close to optimum.")
            elif optimization_steps > 50:
                interpretation.append("Many optimization steps required - initial structure was far from optimum.")
        else:
            interpretation.append("Optimization failed to converge within maximum steps.")
            recommendations.extend([
                "Increase relax_nmax to allow more optimization steps",
                "Check if force_thr is too strict for the system",
                "Consider using different optimization algorithm (bfgs, cg, sd)",
                "Verify initial structure quality"
            ])
        
        # Force analysis
        if max_force is not None:
            interpretation.append(f"Maximum force: {max_force:.4f} eV/Å")
            force_thr = input_params.get("force_thr", 0.01)
            
            if max_force < force_thr:
                interpretation.append("Forces are below convergence threshold.")
            else:
                interpretation.append("Forces are above convergence threshold.")
                if max_force > 0.1:
                    recommendations.append("Large forces detected - structure may need significant relaxation.")
        
        if total_force is not None:
            interpretation.append(f"Total force: {total_force:.4f} eV/Å")
        
        # Energy change analysis
        final_energy = opt_data.get("final_total_energy_ev")
        if final_energy is not None:
            interpretation.append(f"Final total energy: {final_energy:.6f} eV")
        
        # Stress analysis for cell optimization
        if input_params.get("calculation") == "cell-relax":
            stress_tensor = opt_data.get("stress_tensor_kbar")
            if stress_tensor is not None:
                max_stress = max(abs(s) for row in stress_tensor for s in row)
                interpretation.append(f"Maximum stress component: {max_stress:.3f} kBar")
                
                press_thr = input_params.get("press_thr", 0.5)
                if max_stress < press_thr:
                    interpretation.append("Stress is below convergence threshold.")
                else:
                    recommendations.append("Consider tighter stress convergence or check cell optimization.")
        
        return {
            "interpretation": interpretation,
            "recommendations": recommendations
        }
    
    def interpret_md_results(self, md_data: Dict[str, Any], input_params: Dict[str, Any]) -> Dict[str, Any]:
        """Interpret molecular dynamics results."""
        interpretation = []
        recommendations = []
        
        completed_all_steps = md_data.get("completed_all_steps", False)
        total_md_steps = md_data.get("total_md_steps_performed", 0)
        avg_temperature = md_data.get("average_temperature_k")
        avg_pressure = md_data.get("average_pressure_kbar")
        
        # Completion analysis
        requested_steps = input_params.get("md_nstep", 0)
        if completed_all_steps:
            interpretation.append(f"MD simulation completed successfully ({total_md_steps}/{requested_steps} steps).")
        else:
            interpretation.append(f"MD simulation incomplete ({total_md_steps}/{requested_steps} steps).")
            recommendations.append("Check for convergence issues or increase computational resources.")
        
        # Temperature analysis
        target_temp = input_params.get("md_tfirst", 300)
        if avg_temperature is not None:
            interpretation.append(f"Average temperature: {avg_temperature:.1f} K (target: {target_temp} K)")
            
            temp_deviation = abs(avg_temperature - target_temp)
            if temp_deviation > 50:
                interpretation.append("Large temperature deviation from target detected.")
                recommendations.extend([
                    "Check thermostat settings (md_thermostat)",
                    "Consider equilibration period before production run",
                    "Verify time step (md_dt) is appropriate"
                ])
            else:
                interpretation.append("Temperature control is working well.")
        
        # Pressure analysis
        if avg_pressure is not None:
            interpretation.append(f"Average pressure: {avg_pressure:.2f} kBar")
            if abs(avg_pressure) > 10:
                recommendations.append("High pressure detected - consider NPT ensemble or larger cell.")
        
        # Time step analysis
        md_dt = input_params.get("md_dt", 1.0)
        if md_dt > 2.0:
            recommendations.append("Large time step detected - ensure energy conservation and stability.")
        elif md_dt < 0.5:
            recommendations.append("Very small time step - consider increasing for efficiency if stable.")
        
        return {
            "interpretation": interpretation,
            "recommendations": recommendations
        }
    
    def interpret_band_structure_results(self, band_data: Dict[str, Any], analysis_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Interpret band structure calculation results."""
        interpretation = []
        recommendations = []
        
        eigenvalues = band_data.get("eigenvalues")
        fermi_energy_ev = band_data.get("fermi_energy_ev")
        
        if eigenvalues is not None:
            nkpts = len(eigenvalues)
            nbands = len(eigenvalues[0]) if eigenvalues else 0
            interpretation.append(f"Band structure calculated with {nkpts} k-points and {nbands} bands.")
        
        # Band gap analysis
        if analysis_data:
            band_gap = analysis_data.get("band_gap_ev")
            gap_type = analysis_data.get("gap_type")
            is_metallic = analysis_data.get("is_metallic_from_bands")
            
            if band_gap is not None:
                if band_gap > 0.1:
                    interpretation.append(f"Semiconductor/insulator with band gap: {band_gap:.3f} eV ({gap_type} gap)")
                    if gap_type == "indirect":
                        interpretation.append("Indirect band gap - optical transitions may be weak.")
                    elif gap_type == "direct":
                        interpretation.append("Direct band gap - suitable for optical applications.")
                elif band_gap > 0.01:
                    interpretation.append(f"Small band gap detected: {band_gap:.3f} eV - may be metallic or narrow-gap semiconductor.")
                else:
                    interpretation.append("Metallic behavior detected (no band gap).")
            
            if is_metallic:
                interpretation.append("Electronic structure indicates metallic behavior.")
                recommendations.append("Ensure adequate k-point sampling for metallic systems.")
        
        # Recommendations for band structure calculations
        if nkpts < 50:
            recommendations.append("Consider more k-points along the path for smoother band structure.")
        
        if fermi_energy_ev is not None:
            interpretation.append(f"Fermi level at {fermi_energy_ev:.3f} eV")
        
        recommendations.extend([
            "Verify band structure against experimental data if available",
            "Consider calculating DOS for complete electronic structure picture",
            "Check convergence with respect to ecutwfc and k-point sampling"
        ])
        
        return {
            "interpretation": interpretation,
            "recommendations": recommendations
        }
    
    def interpret_dos_results(self, dos_data: Dict[str, Any], input_params: Dict[str, Any]) -> Dict[str, Any]:
        """Interpret density of states results."""
        interpretation = []
        recommendations = []
        
        dos_info = dos_data.get("dos_data", {})
        fermi_energy_ev = dos_data.get("fermi_energy_ev")
        spin_channels = dos_data.get("spin_channels_present", [])
        
        # Basic DOS information
        if "energy_ev" in dos_info:
            energy_range = dos_info["energy_ev"]
            if isinstance(energy_range, list) and len(energy_range) > 1:
                emin, emax = min(energy_range), max(energy_range)
                interpretation.append(f"DOS calculated over energy range: {emin:.2f} to {emax:.2f} eV")
        
        # Spin analysis
        if len(spin_channels) > 1:
            interpretation.append("Spin-polarized calculation detected.")
            recommendations.append("Compare spin-up and spin-down DOS for magnetic properties.")
        else:
            interpretation.append("Non-spin-polarized calculation.")
        
        # Fermi level analysis
        if fermi_energy_ev is not None:
            interpretation.append(f"Fermi energy: {fermi_energy_ev:.3f} eV")
            
            # Check DOS at Fermi level for metallicity
            if "total_dos" in dos_info and "energy_ev" in dos_info:
                try:
                    energies = np.array(dos_info["energy_ev"])
                    total_dos = np.array(dos_info["total_dos"])
                    
                    # Find DOS at Fermi level
                    fermi_idx = np.argmin(np.abs(energies - fermi_energy_ev))
                    dos_at_fermi = total_dos[fermi_idx]
                    
                    if dos_at_fermi > 0.1:  # states/eV threshold
                        interpretation.append(f"Significant DOS at Fermi level ({dos_at_fermi:.2f} states/eV) - metallic behavior.")
                    else:
                        interpretation.append("Low DOS at Fermi level - semiconducting/insulating behavior.")
                        
                except Exception:
                    interpretation.append("Could not analyze DOS at Fermi level.")
        
        # Energy resolution analysis
        dos_deltae = input_params.get("dos_deltae", 0.01)
        interpretation.append(f"DOS energy resolution: {dos_deltae} eV")
        if dos_deltae > 0.05:
            recommendations.append("Consider finer energy resolution (smaller dos_deltae) for detailed features.")
        
        # K-point sampling recommendations
        kpoints_def = input_params.get("kpoints_definition_dos", {})
        mp_grid = kpoints_def.get("mp_grid", [1, 1, 1])
        total_kpts = np.prod(mp_grid)
        
        if total_kpts < 64:
            recommendations.append("Consider denser k-point grid for more accurate DOS.")
        
        recommendations.extend([
            "Integrate DOS to verify total number of electrons",
            "Compare with experimental photoemission or inverse photoemission data",
            "Consider projected DOS (PDOS) for orbital-resolved analysis"
        ])
        
        return {
            "interpretation": interpretation,
            "recommendations": recommendations
        }

# Global interpreter instance
result_interpreter = AbacusResultInterpreter()