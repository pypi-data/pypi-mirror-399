"""
Analysis Commands Manager for OpsParser

This module handles OpenSeesPy analysis commands including:
- constraints (Plain, Lagrange, Penalty, Transformation)
- numberer (Plain, RCM, AMD, Parallel Plain, Parallel RCM)
- system (BandGeneral, BandSPD, ProfileSPD, SuperLU, UmfPack, FullGeneral, SparseSYM, MUMPS)
- test (NormUnbalance, NormDispIncr, energyIncr, RelativeNormUnbalance, etc.)
- algorithm (Linear, Newton, Modified Newton, BFGS, Broyden, etc.)
- integrator (LoadControl, DisplacementControl, Newmark, etc.)
- analysis (Static, Transient)
- eigen (eigenvalue analysis)
- analyze (perform analysis)
- modalProperties (modal analysis)
- responseSpectrumAnalysis (response spectrum analysis)
"""

from typing import Dict, List, Any, Optional, Union
from ._BaseHandler import BaseHandler, SingletonMeta


class AnalysisManager(BaseHandler, metaclass=SingletonMeta):
    """
    Manager for OpenSeesPy analysis commands.
    
    Handles all analysis-related commands that define how the finite element
    analysis is performed, including constraint handlers, DOF numberers,
    system solvers, convergence tests, solution algorithms, integrators,
    and analysis execution.
    """
    
    _COMMAND_RULES = {
        'constraints': {
            'positional': ['type', 'args*'],
            'options': {'-alphaS?': 'alpha_s', '-alphaM?': 'alpha_m', '-penalty?': 'penalty_value'},
            'description': 'Define constraint handler'
        },
        'numberer': {
            'positional': ['type', 'args*'],
            'options': {'-rcm?': 'rcm_flag', '-amd?': 'amd_flag'},
            'description': 'Define DOF numberer'
        },
        'system': {
            'positional': ['type', 'args*'],
            'options': {'-p?': 'parallel_flag', '-parallel?': 'parallel_config'},
            'description': 'Define system of equations solver'
        },
        'test': {
            'positional': ['type', 'args*'],
            'options': {'-iter?': 'max_iter', '-norm?': 'norm_type', '-energy?': 'energy_flag'},
            'description': 'Define convergence test'
        },
        'algorithm': {
            'positional': ['type', 'args*'],
            'options': {'-initial?': 'initial_flag', '-maxIter?': 'max_iter', '-minIter?': 'min_iter'},
            'description': 'Define solution algorithm'
        },
        'integrator': {
            'positional': ['type', 'args*'],
            'options': {'-form?': 'form_type', '-factor?': 'factor_value'},
            'description': 'Define integrator'
        },
        'analysis': {
            'positional': ['type'],
            'options': {},
            'description': 'Define analysis type'
        },
        'eigen': {
            'positional': ['num_modes', 'args*'],
            'options': {'-genBandArpack?': 'arpack_flag', '-fullGenLapack?': 'lapack_flag', '-symmBandLapack?': 'symm_flag'},
            'description': 'Perform eigenvalue analysis'
        },
        'analyze': {
            'positional': ['num_steps', 'args*'],
            'options': {'-dt?': 'time_step'},
            'description': 'Perform analysis'
        },
        'modalProperties': {
            'positional': ['args*'],
            'options': {'-print?': 'print_flag', '-return?': 'return_flag'},
            'description': 'Compute modal properties'
        },
        'responseSpectrumAnalysis': {
            'positional': ['spectrum_file', 'args*'],
            'options': {'-option?': 'option_value'},
            'description': 'Perform response spectrum analysis'
        }
    }

    def __init__(self):
        super().__init__()
        self.constraints_info: Dict[str, Any] = {}
        self.numberer_info: Dict[str, Any] = {}
        self.system_info: Dict[str, Any] = {}
        self.test_info: Dict[str, Any] = {}
        self.algorithm_info: Dict[str, Any] = {}
        self.integrator_info: Dict[str, Any] = {}
        self.analysis_info: Dict[str, Any] = {}
        self.eigen_results: List[Dict[str, Any]] = []
        self.analysis_history: List[Dict[str, Any]] = []
        self.modal_properties: Dict[str, Any] = {}
        self.response_spectrum_results: Dict[str, Any] = {}

    def handle(self, command: str, args: Dict[str, Any]) -> None:
        """Handle analysis commands and store information."""
        args_list, kwargs = args.get("args", []), args.get("kwargs", {})
        
        if command == 'constraints':
            self._handle_constraints(*args_list, **kwargs)
        elif command == 'numberer':
            self._handle_numberer(*args_list, **kwargs)
        elif command == 'system':
            self._handle_system(*args_list, **kwargs)
        elif command == 'test':
            self._handle_test(*args_list, **kwargs)
        elif command == 'algorithm':
            self._handle_algorithm(*args_list, **kwargs)
        elif command == 'integrator':
            self._handle_integrator(*args_list, **kwargs)
        elif command == 'analysis':
            self._handle_analysis(*args_list, **kwargs)
        elif command == 'eigen':
            self._handle_eigen(*args_list, **kwargs)
        elif command == 'analyze':
            self._handle_analyze(*args_list, **kwargs)
        elif command == 'modalProperties':
            self._handle_modal_properties(*args_list, **kwargs)
        elif command == 'responseSpectrumAnalysis':
            self._handle_response_spectrum(*args_list, **kwargs)

    def _handle_constraints(self, *args: Any, **kwargs: Any) -> None:
        """Handle constraints command."""
        parsed_args = self._parse('constraints', *args, **kwargs)
        constraint_type = parsed_args.get('type', 'Plain')
        
        self.constraints_info = {
            'type': constraint_type,
            'args': parsed_args.get('args', []),
            'options': parsed_args
        }

    def _handle_numberer(self, *args: Any, **kwargs: Any) -> None:
        """Handle numberer command."""
        parsed_args = self._parse('numberer', *args, **kwargs)
        numberer_type = parsed_args.get('type', 'Plain')
        
        self.numberer_info = {
            'type': numberer_type,
            'args': parsed_args.get('args', []),
            'options': parsed_args
        }

    def _handle_system(self, *args: Any, **kwargs: Any) -> None:
        """Handle system command."""
        parsed_args = self._parse('system', *args, **kwargs)
        system_type = parsed_args.get('type', 'BandGeneral')
        
        self.system_info = {
            'type': system_type,
            'args': parsed_args.get('args', []),
            'options': parsed_args
        }

    def _handle_test(self, *args: Any, **kwargs: Any) -> None:
        """Handle test command."""
        parsed_args = self._parse('test', *args, **kwargs)
        test_type = parsed_args.get('type', 'NormUnbalance')
        
        self.test_info = {
            'type': test_type,
            'args': parsed_args.get('args', []),
            'options': parsed_args
        }

    def _handle_algorithm(self, *args: Any, **kwargs: Any) -> None:
        """Handle algorithm command."""
        parsed_args = self._parse('algorithm', *args, **kwargs)
        algorithm_type = parsed_args.get('type', 'Newton')
        
        self.algorithm_info = {
            'type': algorithm_type,
            'args': parsed_args.get('args', []),
            'options': parsed_args
        }

    def _handle_integrator(self, *args: Any, **kwargs: Any) -> None:
        """Handle integrator command."""
        parsed_args = self._parse('integrator', *args, **kwargs)
        integrator_type = parsed_args.get('type', 'LoadControl')
        
        self.integrator_info = {
            'type': integrator_type,
            'args': parsed_args.get('args', []),
            'options': parsed_args
        }

    def _handle_analysis(self, *args: Any, **kwargs: Any) -> None:
        """Handle analysis command."""
        parsed_args = self._parse('analysis', *args, **kwargs)
        analysis_type = parsed_args.get('type', 'Static')
        
        self.analysis_info = {
            'type': analysis_type,
            'args': parsed_args.get('args', []),
            'options': parsed_args
        }

    def _handle_eigen(self, *args: Any, **kwargs: Any) -> None:
        """Handle eigen command."""
        parsed_args = self._parse('eigen', *args, **kwargs)
        num_modes = int(parsed_args.get('num_modes', 1))
        
        eigen_info = {
            'num_modes': num_modes,
            'args': parsed_args.get('args', []),
            'options': parsed_args,
            'solver_type': parsed_args.get('solver', 'genBandArpack')
        }
        self.eigen_results.append(eigen_info)

    def _handle_analyze(self, *args: Any, **kwargs: Any) -> None:
        """Handle analyze command."""
        parsed_args = self._parse('analyze', *args, **kwargs)
        num_steps = int(parsed_args.get('num_steps', 1))
        
        analyze_info = {
            'num_steps': num_steps,
            'args': parsed_args.get('args', []),
            'options': parsed_args,
            'analysis_type': self.analysis_info.get('type', 'Static')
        }
        self.analysis_history.append(analyze_info)

    def _handle_modal_properties(self, *args: Any, **kwargs: Any) -> None:
        """Handle modalProperties command."""
        parsed_args = self._parse('modalProperties', *args, **kwargs)
        self.modal_properties = {
            'args': parsed_args.get('args', []),
            'options': parsed_args
        }

    def _handle_response_spectrum(self, *args: Any, **kwargs: Any) -> None:
        """Handle responseSpectrumAnalysis command."""
        parsed_args = self._parse('responseSpectrumAnalysis', *args, **kwargs)
        spectrum_file = parsed_args.get('spectrum_file')
        
        self.response_spectrum_results = {
            'spectrum_file': spectrum_file,
            'args': parsed_args.get('args', []),
            'options': parsed_args
        }

    @classmethod
    def handles(cls) -> List[str]:
        """Return list of commands this manager handles."""
        return list(cls._COMMAND_RULES.keys())

    def clear(self) -> None:
        """Clear all stored analysis data."""
        self.constraints_info.clear()
        self.numberer_info.clear()
        self.system_info.clear()
        self.test_info.clear()
        self.algorithm_info.clear()
        self.integrator_info.clear()
        self.analysis_info.clear()
        self.eigen_results.clear()
        self.analysis_history.clear()
        self.modal_properties.clear()
        self.response_spectrum_results.clear()

    def get_current_analysis_setup(self) -> Dict[str, Any]:
        """Get current analysis setup configuration."""
        return {
            'constraints': self.constraints_info,
            'numberer': self.numberer_info,
            'system': self.system_info,
            'test': self.test_info,
            'algorithm': self.algorithm_info,
            'integrator': self.integrator_info,
            'analysis': self.analysis_info
        }

    def get_eigen_info(self) -> List[Dict[str, Any]]:
        """Get eigenvalue analysis information."""
        return self.eigen_results.copy()

    def get_analysis_history(self) -> List[Dict[str, Any]]:
        """Get analysis execution history."""
        return self.analysis_history.copy()

    def get_modal_properties(self) -> Dict[str, Any]:
        """Get modal properties information."""
        return self.modal_properties.copy()

    def get_response_spectrum_results(self) -> Dict[str, Any]:
        """Get response spectrum analysis results."""
        return self.response_spectrum_results.copy() 