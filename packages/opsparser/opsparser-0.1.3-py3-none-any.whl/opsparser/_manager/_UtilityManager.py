"""
Utility Commands Manager for OpsParser

This module handles OpenSeesPy utility commands including:
- Model state commands (wipe, reset, remove, save, restore)
- Time and loading commands (setTime, loadConst, reactions)
- Parameter and precision commands (setPrecision, setParameter)
- Database and file commands (database, logFile)
- Other utility commands
"""

from typing import Dict, List, Any, Optional, Union
from ._BaseHandler import BaseHandler, SingletonMeta


class UtilityManager(BaseHandler, metaclass=SingletonMeta):
    """
    Manager for OpenSeesPy utility commands.
    
    Handles various utility commands that control model state, 
    time management, file operations, and other miscellaneous functions.
    """
    
    _COMMAND_RULES = {
        'wipe': {
            'positional': [],
            'options': {},
            'description': 'Wipe model completely'
        },
        'wipeAnalysis': {
            'positional': [],
            'options': {},
            'description': 'Wipe analysis objects only'
        },
        'reset': {
            'positional': [],
            'options': {},
            'description': 'Reset model to last committed state'
        },
        'remove': {
            'positional': ['type', 'args*'],
            'options': {},
            'description': 'Remove model components'
        },
        'save': {
            'positional': ['state_tag'],
            'options': {},
            'description': 'Save current state'
        },
        'restore': {
            'positional': ['state_tag'],
            'options': {},
            'description': 'Restore saved state'
        },
        'loadConst': {
            'positional': ['args*'],
            'options': {'-time': 'time_value'},
            'description': 'Set loads constant'
        },
        'reactions': {
            'positional': ['args*'],
            'options': {'-dynamic?*0': 'dynamic_flag', '-rayleigh?*0': 'rayleigh_flag'},
            'description': 'Calculate reactions'
        },
        'setTime': {
            'positional': ['time_value'],
            'options': {},
            'description': 'Set current time'
        },
        'getTime': {
            'positional': [],
            'options': {},
            'description': 'Get current time'
        },
        'setPrecision': {
            'positional': ['precision'],
            'options': {},
            'description': 'Set output precision'
        },
        'setParameter': {
            'positional': [],
            'options': {'-val*1': 'value', '-ele?*': 'ele_tags', '-eleRange?*2': ['start','end']},
            'description': 'Set parameter value'
        },
        'database': {
            'positional': ['db_type', 'db_name', 'args*'],
            'options': {},
            'description': 'Define database'
        },
        'logFile': {
            'positional': ['filename', 'args*'],
            'options': {},
            'description': 'Set log file'
        },
        'setNodeCoord': {
            'positional': ['node_tag', 'args*'],
            'options': {},
            'description': 'Set node coordinates'
        },
        'setNodeDisp': {
            'positional': ['node_tag', 'args*'],
            'options': {},
            'description': 'Set node displacement'
        },
        'setNodeVel': {
            'positional': ['node_tag', 'args*'],
            'options': {},
            'description': 'Set node velocity'
        },
        'setNodeAccel': {
            'positional': ['node_tag', 'args*'],
            'options': {},
            'description': 'Set node acceleration'
        },
        'setElementRayleighDampingFactors': {
            'positional': ['element_tag', 'args*'],
            'options': {},
            'description': 'Set element Rayleigh damping factors'
        },
        'modalDamping': {
            'positional': ['args*'],
            'options': {},
            'description': 'Set modal damping'
        },
        'start': {
            'positional': [],
            'options': {},
            'description': 'Start timing'
        },
        'stop': {
            'positional': [],
            'options': {},
            'description': 'Stop timing'
        },
        'updateElementDomain': {
            'positional': [],
            'options': {},
            'description': 'Update element domain'
        },
        'updateMaterialStage': {
            'positional': ['args*'],
            'options': {},
            'description': 'Update material stage'
        }
    }

    def __init__(self):
        super().__init__()
        self.model_states: Dict[int, Dict[str, Any]] = {}
        self.current_time: float = 0.0
        self.precision: int = 6
        self.parameters: Dict[int, Dict[str, Any]] = {}
        self.load_constant_info: Dict[str, Any] = {}
        self.reactions_info: Dict[str, Any] = {}
        self.database_info: Dict[str, Any] = {}
        self.log_file: Optional[str] = None
        self.utility_history: List[Dict[str, Any]] = []
        self.timing_started: bool = False

    def handle(self, command: str, args: Dict[str, Any]) -> None:
        """Handle utility commands and store information."""
        args_list, kwargs = args.get("args", []), args.get("kwargs", {})
        
        # Store command in history
        self.utility_history.append({
            'command': command,
            'args': args_list,
            'kwargs': kwargs,
            'timestamp': len(self.utility_history)
        })
        
        if command == 'wipe':
            self._handle_wipe(*args_list, **kwargs)
        elif command == 'wipeAnalysis':
            self._handle_wipe_analysis(*args_list, **kwargs)
        elif command == 'reset':
            self._handle_reset(*args_list, **kwargs)
        elif command == 'remove':
            self._handle_remove(*args_list, **kwargs)
        elif command == 'save':
            self._handle_save(*args_list, **kwargs)
        elif command == 'restore':
            self._handle_restore(*args_list, **kwargs)
        elif command == 'loadConst':
            self._handle_load_const(*args_list, **kwargs)
        elif command == 'reactions':
            self._handle_reactions(*args_list, **kwargs)
        elif command == 'setTime':
            self._handle_set_time(*args_list, **kwargs)
        elif command == 'getTime':
            self._handle_get_time(*args_list, **kwargs)
        elif command == 'setPrecision':
            self._handle_set_precision(*args_list, **kwargs)
        elif command == 'setParameter':
            self._handle_set_parameter(*args_list, **kwargs)
        elif command == 'database':
            self._handle_database(*args_list, **kwargs)
        elif command == 'logFile':
            self._handle_log_file(*args_list, **kwargs)
        elif command in ['setNodeCoord', 'setNodeDisp', 'setNodeVel', 'setNodeAccel']:
            self._handle_set_node_property(command, *args_list, **kwargs)
        elif command == 'setElementRayleighDampingFactors':
            self._handle_set_element_damping(*args_list, **kwargs)
        elif command == 'modalDamping':
            self._handle_modal_damping(*args_list, **kwargs)
        elif command in ['start', 'stop']:
            self._handle_timing(command, *args_list, **kwargs)
        elif command in ['updateElementDomain', 'updateMaterialStage']:
            self._handle_update_command(command, *args_list, **kwargs)

    def _handle_wipe(self, *args: Any, **kwargs: Any) -> None:
        """Handle wipe command."""
        # Clear all state except utility history
        self.model_states.clear()
        self.parameters.clear()
        self.current_time = 0.0
        self.precision = 6
        self.log_file = None
        self.database_info = {}

    def _handle_wipe_analysis(self, *args: Any, **kwargs: Any) -> None:
        """Handle wipeAnalysis command."""
        # Would clear analysis objects only
        pass

    def _handle_reset(self, *args: Any, **kwargs: Any) -> None:
        """Handle reset command."""
        # Reset to last committed state
        pass

    def _handle_remove(self, *args: Any, **kwargs: Any) -> None:
        """Handle remove command."""
        parsed_args = self._parse('remove', *args, **kwargs)
        remove_type = parsed_args.get('type')
        remove_tags = parsed_args.get('args', [])
        
        remove_info = {
            'type': remove_type,
            'tags': remove_tags,
            'options': parsed_args
        }

    def _handle_save(self, *args: Any, **kwargs: Any) -> None:
        """Handle save command."""
        parsed_args = self._parse('save', *args, **kwargs)
        state_tag = int(parsed_args.get('state_tag', 1))
        
        self.model_states[state_tag] = {
            'time': self.current_time,
            'saved_at': len(self.utility_history)
        }

    def _handle_restore(self, *args: Any, **kwargs: Any) -> None:
        """Handle restore command."""
        parsed_args = self._parse('restore', *args, **kwargs)
        state_tag = int(parsed_args.get('state_tag', 1))
        
        if state_tag in self.model_states:
            state_info = self.model_states[state_tag]
            self.current_time = state_info['time']

    def _handle_load_const(self, *args: Any, **kwargs: Any) -> None:
        """Handle loadConst command."""
        parsed_args = self._parse('loadConst', *args, **kwargs)
        self.load_constant_info = {
            'time': parsed_args.get('time_value', self.current_time),
            'options': parsed_args
        }

    def _handle_reactions(self, *args: Any, **kwargs: Any) -> None:
        """Handle reactions command."""
        parsed_args = self._parse('reactions', *args, **kwargs)
        self.reactions_info = {
            'dynamic': 'dynamic_flag' in parsed_args,
            'rayleigh': 'rayleigh_flag' in parsed_args,
            'options': parsed_args
        }

    def _handle_set_time(self, *args: Any, **kwargs: Any) -> None:
        """Handle setTime command."""
        parsed_args = self._parse('setTime', *args, **kwargs)
        time_value = parsed_args.get('time_value')
        if time_value is not None:
            self.current_time = float(time_value)

    def _handle_get_time(self, *args: Any, **kwargs: Any) -> None:
        """Handle getTime command."""
        # Return current time
        return self.current_time

    def _handle_set_precision(self, *args: Any, **kwargs: Any) -> None:
        """Handle setPrecision command."""
        parsed_args = self._parse('setPrecision', *args, **kwargs)
        precision = parsed_args.get('precision')
        if precision is not None:
            self.precision = int(precision)

    def _handle_set_parameter(self, *args: Any, **kwargs: Any) -> None:
        """Handle setParameter command."""
        parsed_args = self._parse('setParameter', *args, **kwargs)
        # setParameter('-val', newValue, <'-ele', *eleTags>, <'-eleRange', start, end>, <*args>)
        
        # New syntax does not use param_tag, but sets value directly
        value = parsed_args.get('value')
        
        # Extract extra arguments (parameter names)
        param_args = parsed_args.get('args', [])
        
        # Store in history is enough for now as we don't track individual parameter objects without tags
        # If we wanted to track, we'd need to know which parameters are being updated (by ele tags or args)
        if value is not None:
             # Just for compatibility, we might want to store it if we can identify it, 
             # but without a tag, we can't put it in self.parameters dict keyed by int.
             pass

    def _handle_database(self, *args: Any, **kwargs: Any) -> None:
        """Handle database command."""
        parsed_args = self._parse('database', *args, **kwargs)
        db_type = parsed_args.get('db_type')
        db_name = parsed_args.get('db_name')
        
        if db_type and db_name:
            self.database_info = {
                'type': db_type,
                'name': db_name,
                'args': parsed_args.get('args', []),
                'options': parsed_args
            }

    def _handle_log_file(self, *args: Any, **kwargs: Any) -> None:
        """Handle logFile command."""
        parsed_args = self._parse('logFile', *args, **kwargs)
        filename = parsed_args.get('filename')
        if filename:
            self.log_file = filename

    def _handle_set_node_property(self, command: str, *args: Any, **kwargs: Any) -> None:
        """Handle setNode* commands."""
        parsed_args = self._parse(command, *args, **kwargs)
        node_tag = parsed_args.get('node_tag')
        if node_tag is not None:
            property_info = {
                'command': command,
                'node_tag': int(node_tag),
                'values': parsed_args.get('args', []),
                'options': parsed_args
            }

    def _handle_set_element_damping(self, *args: Any, **kwargs: Any) -> None:
        """Handle setElementRayleighDampingFactors command."""
        parsed_args = self._parse('setElementRayleighDampingFactors', *args, **kwargs)
        element_tag = parsed_args.get('element_tag')
        if element_tag is not None:
            damping_info = {
                'element_tag': int(element_tag),
                'factors': parsed_args.get('args', []),
                'options': parsed_args
            }

    def _handle_modal_damping(self, *args: Any, **kwargs: Any) -> None:
        """Handle modalDamping command."""
        parsed_args = self._parse('modalDamping', *args, **kwargs)
        damping_info = {
            'values': parsed_args.get('args', []),
            'options': parsed_args
        }

    def _handle_timing(self, command: str, *args: Any, **kwargs: Any) -> None:
        """Handle timing commands (start/stop)."""
        if command == 'start':
            self.timing_started = True
        elif command == 'stop':
            self.timing_started = False
            
        timing_info = {
            'command': command,
            'timestamp': len(self.utility_history)
        }

    def _handle_update_command(self, command: str, *args: Any, **kwargs: Any) -> None:
        """Handle update commands."""
        parsed_args = self._parse(command, *args, **kwargs)
        update_info = {
            'command': command,
            'args': parsed_args.get('args', []),
            'options': parsed_args
        }

    @classmethod
    def handles(cls) -> List[str]:
        """Return list of commands this manager handles."""
        return list(cls._COMMAND_RULES.keys())

    def clear(self) -> None:
        """Clear all stored utility data."""
        self.model_states.clear()
        self.current_time = 0.0
        self.precision = 6
        self.parameters.clear()
        self.load_constant_info.clear()
        self.reactions_info.clear()
        if isinstance(self.database_info, dict):
            self.database_info.clear()
        else:
            self.database_info = {}
        self.log_file = None
        self.utility_history.clear()
        self.timing_started = False

    def get_current_time(self) -> float:
        """Get current analysis time."""
        return self.current_time

    def get_precision(self) -> int:
        """Get current output precision."""
        return self.precision

    def get_model_states(self) -> Dict[int, Dict[str, Any]]:
        """Get all saved model states."""
        return self.model_states.copy()

    def get_parameters(self) -> Dict[int, Dict[str, Any]]:
        """Get all parameters."""
        return self.parameters.copy()

    def get_load_constant_info(self) -> Dict[str, Any]:
        """Get load constant information."""
        return self.load_constant_info.copy()

    def get_reactions_info(self) -> Dict[str, Any]:
        """Get reactions calculation information."""
        return self.reactions_info.copy()

    def get_database_info(self) -> Dict[str, Any]:
        """Get database information."""
        return self.database_info.copy()

    def get_log_file(self) -> Optional[str]:
        """Get log file path."""
        return self.log_file

    def get_utility_history(self) -> List[Dict[str, Any]]:
        """Get utility command history."""
        return self.utility_history.copy()

    def is_timing_active(self) -> bool:
        """Check if timing is currently active."""
        return self.timing_started 