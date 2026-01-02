"""
Recorder and Output Commands Manager for OpsParser

This module handles OpenSeesPy output and recorder commands including:
- recorder (Node, Element, EnvelopeNode, EnvelopeElement, etc.)
- record (Manual recording trigger)
- Output query commands (nodeDisp, nodeVel, nodeAccel, eleForce, etc.)
"""

from typing import Dict, List, Any, Optional, Union
from ._BaseHandler import BaseHandler, SingletonMeta


class RecorderManager(BaseHandler, metaclass=SingletonMeta):
    """
    Manager for OpenSeesPy recorder and output commands.
    
    Handles all recorder definitions and output query commands that allow
    users to monitor and extract data from finite element analyses.
    """
    
    _COMMAND_RULES = {
        'recorder': {
            'positional': ['type', 'response_args*'],
            'options': {'-file': 'filename', '-xml': 'xml_file', '-binary': 'binary_file', 
                       '-precision': 'precision_val', '-time?*0': 'time_flag', '-dT': 'delta_t',
                       '-closeOnWrite?*0': 'close_flag', '-timeSeries': 'ts_tag', '-node': 'node_list*',
                       '-element': 'ele_list*', '-ele': 'ele_list*', '-region': 'region_tag', 
                       '-eleRange': 'ele_range*', '-nodeRange': 'node_range*'},
            'description': 'Define data recorder'
        },
        'record': {
            'positional': [],
            'options': {},
            'description': 'Trigger manual recording'
        },
        'nodeDisp': {
            'positional': ['node_tag', 'dof?', 'args*'],
            'options': {},
            'description': 'Get node displacement'
        },
        'nodeVel': {
            'positional': ['node_tag', 'dof?', 'args*'],
            'options': {},
            'description': 'Get node velocity'
        },
        'nodeAccel': {
            'positional': ['node_tag', 'dof?', 'args*'],
            'options': {},
            'description': 'Get node acceleration'
        },
        'nodeReaction': {
            'positional': ['node_tag', 'dof?', 'args*'],
            'options': {},
            'description': 'Get node reaction'
        },
        'nodeResponse': {
            'positional': ['node_tag', 'response_type', 'args*'],
            'options': {},
            'description': 'Get node response'
        },
        'eleForce': {
            'positional': ['element_tag', 'args*'],
            'options': {},
            'description': 'Get element force'
        },
        'eleResponse': {
            'positional': ['element_tag', 'response_type', 'args*'],
            'options': {},
            'description': 'Get element response'
        },
        'getNodeTags': {
            'positional': [],
            'options': {},
            'description': 'Get all node tags'
        },
        'getEleTags': {
            'positional': [],
            'options': {},
            'description': 'Get all element tags'
        },
        'nodeCoord': {
            'positional': ['node_tag', 'args*'],
            'options': {},
            'description': 'Get node coordinates'
        },
        'nodeBounds': {
            'positional': [],
            'options': {},
            'description': 'Get node bounds'
        },
        'printModel': {
            'positional': ['args*'],
            'options': {'-JSON?*0': 'json_flag', '-file': 'output_file'},
            'description': 'Print model information'
        },
        'printA': {
            'positional': ['args*'],
            'options': {'-file': 'output_file'},
            'description': 'Print system matrix A'
        },
        'printB': {
            'positional': ['args*'],
            'options': {'-file': 'output_file'},
            'description': 'Print system vector B'
        }
    }

    def __init__(self):
        super().__init__()
        self.recorders: Dict[int, Dict[str, Any]] = {}
        self.recorder_counter: int = 0
        self.output_queries: List[Dict[str, Any]] = []
        self.recording_triggered: int = 0

    def handle(self, command: str, args: Dict[str, Any]) -> None:
        """Handle recorder commands and store information."""
        args_list, kwargs = args.get("args", []), args.get("kwargs", {})
        
        if command == 'recorder':
            self._handle_recorder(*args_list, **kwargs)
        elif command == 'record':
            self._handle_record(*args_list, **kwargs)
        elif command in ['nodeDisp', 'nodeVel', 'nodeAccel', 'nodeReaction', 'nodeResponse']:
            self._handle_node_query(command, *args_list, **kwargs)
        elif command in ['eleForce', 'eleResponse']:
            self._handle_element_query(command, *args_list, **kwargs)
        elif command in ['getTime', 'getNodeTags', 'getEleTags', 'nodeCoord', 'nodeBounds']:
            self._handle_general_query(command, *args_list, **kwargs)
        elif command in ['printModel', 'printA', 'printB']:
            self._handle_print_command(command, *args_list, **kwargs)

    def _handle_recorder(self, *args: Any, **kwargs: Any) -> None:
        """Handle recorder command."""
        parsed_args = self._parse('recorder', *args, **kwargs)
            
        self.recorder_counter += 1
        recorder_id = self.recorder_counter
        
        recorder_info = {
            'id': recorder_id,
            'type': parsed_args.get('type'),
            'args': parsed_args.get('response_args', []),
            'options': parsed_args,
            'output_file': parsed_args.get('filename'),
            'xml_file': parsed_args.get('xml_file'),
            'binary_file': parsed_args.get('binary_file'),
            'precision': parsed_args.get('precision_val', 6),
            'time_series': parsed_args.get('ts_tag'),
            'delta_t': parsed_args.get('delta_t', 0.0),
            'close_on_write': 'close_flag' in parsed_args,
            'include_time': 'time_flag' in parsed_args
        }
        
        # Handle specific recorder types
        recorder_type = parsed_args.get('type', '').lower()
        if recorder_type in ['node', 'envelopenode']:
            recorder_info['nodes'] = self._extract_node_list(parsed_args)
            recorder_info['response_type'] = parsed_args.get('response_args', ['disp'])[0] if parsed_args.get('response_args') else 'disp'
            
        elif recorder_type in ['element', 'envelopeelement']:
            recorder_info['elements'] = self._extract_element_list(parsed_args)
            recorder_info['response_args'] = parsed_args.get('response_args', [])
            
        self.recorders[recorder_id] = recorder_info

    def _extract_node_list(self, args: Dict[str, Any]) -> List[int]:
        """Extract node list from recorder arguments."""
        nodes = []
        
        # 如果有从选项解析出的node_list，使用它
        if 'node_list' in args and args['node_list']:
            node_args = args['node_list']
            if isinstance(node_args, list):
                nodes.extend([int(x) for x in node_args])
            else:
                nodes.append(int(node_args))
        
        if 'node_range' in args:
            # Extract node range
            range_args = args['node_range']
            if isinstance(range_args, list) and len(range_args) >= 2:
                start_node = int(range_args[0])
                end_node = int(range_args[1])
                nodes.extend(range(start_node, end_node + 1))
        
        if 'region_tag' in args:
            # Note: Region nodes would need to be resolved from RegionManager
            region_tag = args['region_tag']
            nodes.append(f"region_{region_tag}")
            
        return nodes

    def _extract_element_list(self, args: Dict[str, Any]) -> List[int]:
        """Extract element list from recorder arguments."""
        elements = []
        
        # 如果有从选项解析出的ele_list，使用它
        if 'ele_list' in args and args['ele_list']:
            ele_args = args['ele_list']
            if isinstance(ele_args, list):
                elements.extend([int(x) for x in ele_args])
            else:
                elements.append(int(ele_args))
        
        if 'ele_range' in args:
            # Extract element range
            range_args = args['ele_range']
            if isinstance(range_args, list) and len(range_args) >= 2:
                start_ele = int(range_args[0])
                end_ele = int(range_args[1])
                elements.extend(range(start_ele, end_ele + 1))
        
        if 'region_tag' in args:
            # Note: Region elements would need to be resolved from RegionManager
            region_tag = args['region_tag']
            elements.append(f"region_{region_tag}")
            
        return elements

    def _handle_record(self, *args: Any, **kwargs: Any) -> None:
        """Handle record command."""
        self.recording_triggered += 1

    def _handle_node_query(self, command: str, *args: Any, **kwargs: Any) -> None:
        """Handle node query commands."""
        parsed_args = self._parse(command, *args, **kwargs)
        query_info = {
            'type': 'node_query',
            'command': command,
            'node_tag': parsed_args.get('node_tag'),
            'dof': parsed_args.get('dof'),
            'args': parsed_args.get('args', []),
            'options': parsed_args
        }
        self.output_queries.append(query_info)

    def _handle_element_query(self, command: str, *args: Any, **kwargs: Any) -> None:
        """Handle element query commands."""
        parsed_args = self._parse(command, *args, **kwargs)
        query_info = {
            'type': 'element_query',
            'command': command,
            'element_tag': parsed_args.get('element_tag'),
            'response_type': parsed_args.get('response_type'),
            'response_args': parsed_args.get('args', []),
            'options': parsed_args
        }
        self.output_queries.append(query_info)

    def _handle_general_query(self, command: str, *args: Any, **kwargs: Any) -> None:
        """Handle general query commands."""
        parsed_args = self._parse(command, *args, **kwargs)
        query_info = {
            'type': 'general_query',
            'command': command,
            'args': parsed_args.get('args', []),
            'options': parsed_args
        }
        self.output_queries.append(query_info)

    def _handle_print_command(self, command: str, *args: Any, **kwargs: Any) -> None:
        """Handle print commands."""
        parsed_args = self._parse(command, *args, **kwargs)
        query_info = {
            'type': 'print_command',
            'command': command,
            'args': parsed_args.get('args', []),
            'options': parsed_args,
            'output_file': parsed_args.get('output_file')
        }
        self.output_queries.append(query_info)

    @classmethod
    def handles(cls) -> List[str]:
        """Return list of commands this manager handles."""
        return list(cls._COMMAND_RULES.keys())

    def clear(self) -> None:
        """Clear all stored recorder and output data."""
        self.recorders.clear()
        self.recorder_counter = 0
        self.output_queries.clear()
        self.recording_triggered = 0

    def get_recorders(self) -> Dict[int, Dict[str, Any]]:
        """Get all defined recorders."""
        return self.recorders.copy()

    def get_recorder_by_id(self, recorder_id: int) -> Optional[Dict[str, Any]]:
        """Get recorder by ID."""
        return self.recorders.get(recorder_id)

    def get_recorders_by_type(self, recorder_type: str) -> List[Dict[str, Any]]:
        """Get recorders by type."""
        return [r for r in self.recorders.values() if r['type'].lower() == recorder_type.lower()]

    def get_output_queries(self) -> List[Dict[str, Any]]:
        """Get all output queries."""
        return self.output_queries.copy()

    def get_queries_by_type(self, query_type: str) -> List[Dict[str, Any]]:
        """Get queries by type."""
        return [q for q in self.output_queries if q['type'] == query_type]

    def get_node_recorders(self) -> List[Dict[str, Any]]:
        """Get all node recorders."""
        return self.get_recorders_by_type('node') + self.get_recorders_by_type('envelopenode')

    def get_element_recorders(self) -> List[Dict[str, Any]]:
        """Get all element recorders."""
        return self.get_recorders_by_type('element') + self.get_recorders_by_type('envelopeelement')

    def get_recording_trigger_count(self) -> int:
        """Get number of times manual recording was triggered."""
        return self.recording_triggered 