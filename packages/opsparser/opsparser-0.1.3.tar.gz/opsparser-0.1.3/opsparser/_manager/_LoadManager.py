from ._BaseHandler import BaseHandler
from typing import Any, Optional


class LoadManager(BaseHandler):
    def __init__(self):
        self.patterns = {}  # Load patterns: tag -> {type, tsTag, ...}
        self.node_loads = {}  # Node loads: (patternTag, nodeTag) -> values
        self.ele_loads = {}  # Element loads: (patternTag, eleTag) -> values
        self.current_pattern = None  # Current load pattern

    @property
    def _COMMAND_RULES(self) -> dict[str, dict[str, Any]]:
        return {
            # pattern(patternType, patternTag, tsTag, *args)
            "pattern": {
                "positional": ["patternType", "patternTag", "tsTag", "args*"],
                "options": {
                    "-factor?": "factor",
                },
            },
            # load(nodeTag, *loadValues)
            "load": {
                "positional": ["nodeTag", "loadValues*"],
            },
            # eleLoad(*args)
            "eleLoad": {
                "positional": ["args*"],
            },
        }

    def handles(self):
        return ["pattern", "load", "eleLoad"]

    def handle(self, func_name: str, arg_map: dict[str, Any]):
        args, kwargs = arg_map.get("args"), arg_map.get("kwargs")
        if func_name == "pattern":
            self._handle_pattern(*args, **kwargs)
        elif func_name == "load":
            self._handle_load(*args, **kwargs)
        elif func_name == "eleLoad":
            self._handle_eleLoad(*args, **kwargs)

    def _handle_pattern(self, *args: Any, **kwargs: Any):
        """Handle load pattern command"""
        arg_map = self._parse("pattern", *args, **kwargs)
        
        pattern_type = arg_map.get("patternType", "")
        tag = arg_map.get("patternTag", 0)
        ts_tag = arg_map.get("tsTag", 0)
        extra_args = arg_map.get("args", [])

        if not pattern_type or tag == 0:
            return

        pattern_info = {"type": pattern_type, "tsTag": ts_tag}

        # Check for factor option
        if "factor" in arg_map:
            pattern_info["factor"] = arg_map["factor"]

        if extra_args:
            pattern_info["args"] = extra_args

        self.patterns[tag] = pattern_info
        # Update current load pattern
        self.current_pattern = tag

    def _handle_load(self, *args: Any, **kwargs: Any):
        """Handle node load command"""
        arg_map = self._parse("load", *args, **kwargs)
        
        tag = arg_map.get("nodeTag")  # Node tag
        load_values = arg_map.get("loadValues", [])  # Load components

        if tag is None or not load_values:
            return

        # Use current load pattern
        pattern_tag = self.current_pattern
        if pattern_tag is None:
            return

        # Store node load with key as (load pattern tag, node tag) tuple
        load_key = (pattern_tag, tag)
        self.node_loads[load_key] = load_values

    def _handle_eleLoad(self, *args: Any, **kwargs: Any):
        """Handle element load command"""
        arg_map = self._parse("eleLoad", *args, **kwargs)
        args = arg_map.get("args", [])

        # Get load type
        load_type = ""
        if "-type" in args and args.index("-type") + 1 < len(args):
            type_idx = args.index("-type") + 1
            load_type = args[type_idx]

        # Extract element tag list
        ele_tags = []

        # Check for -ele option
        if "-ele" in args:
            ele_idx = args.index("-ele") + 1
            while ele_idx < len(args) and not args[ele_idx].startswith("-"):
                try:
                    ele_tags.append(int(args[ele_idx]))
                    ele_idx += 1
                except (ValueError, TypeError):
                    break

        # Check for -range option
        if "-range" in args and args.index("-range") + 2 < len(args):
            range_idx = args.index("-range")
            start_tag = int(args[range_idx + 1])
            end_tag = int(args[range_idx + 2])
            ele_tags.extend(range(start_tag, end_tag + 1))

        # Extract load component values
        load_values = []

        # For -beamUniform type loads
        if load_type == "-beamUniform" and "-beamUniform" in args:
            beam_idx = args.index("-beamUniform") + 1
            while beam_idx < len(args) and not args[beam_idx].startswith("-"):
                try:
                    load_values.append(float(args[beam_idx]))
                    beam_idx += 1
                except (ValueError, TypeError):
                    break

        # Use current load pattern
        pattern_tag = self.current_pattern
        if pattern_tag is None:
            return

        # Store load for each element
        for ele_tag in ele_tags:
            load_key = (pattern_tag, ele_tag)
            self.ele_loads[load_key] = {"type": load_type, "values": load_values}

    def get_pattern(self, tag: int) -> Optional[dict]:
        """Get load pattern by tag"""
        return self.patterns.get(tag)

    def get_node_load(self, pattern_tag: int, node_tag: int) -> list[float]:
        """Get node load under specified load pattern"""
        return self.node_loads.get((pattern_tag, node_tag), [])

    def get_ele_load(self, pattern_tag: int, ele_tag: int) -> dict:
        """Get element load under specified load pattern"""
        return self.ele_loads.get((pattern_tag, ele_tag), {})

    def get_patterns_by_time_series(self, ts_tag: int) -> list[int]:
        """Get all load patterns using specific time series"""
        return [tag for tag, info in self.patterns.items() if info.get("tsTag") == ts_tag]

    def clear(self):
        """Clear all data"""
        self.patterns.clear()
        self.node_loads.clear()
        self.ele_loads.clear()
        self.current_pattern = None
