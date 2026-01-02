from typing import Any, Optional, Dict, List

from ._BaseHandler import BaseHandler


class RegionManager(BaseHandler):
    """Manager for region commands in OpenSeesPy
    
    Handles region command which creates regions of nodes and elements
    for applying constraints, loads, or other operations.
    """
    
    def __init__(self):
        self.regions = {}  # tag -> region_info
        
    @property
    def _COMMAND_RULES(self) -> dict[str, dict[str, Any]]:
        """Define parsing rules for region commands"""
        return {
            # region(regTag, '-node', *nodeTags, '-ele', *eleTags, '-eleRange', startEle, endEle, '-nodeRange', startNode, endNode, '-rayleigh', alphaM, betaK, betaKinit, betaKcomm)
            "region": {
                "positional": ["tag"],
                "options": {
                    "-node?": "node_tags*",
                    "-ele?": "ele_tags*",
                    "-eleRange?": "ele_range*",
                    "-nodeRange?": "node_range*",
                    "-rayleigh?": "rayleigh_params*",
                },
            },
        }
    
    def handles(self) -> List[str]:
        """Return list of commands this manager handles"""
        return ["region"]
    
    def handle(self, func_name: str, arg_map: dict[str, Any]):
        """Handle region commands"""
        if func_name == "region":
            args, kwargs = arg_map.get("args"), arg_map.get("kwargs")
            parsed_args = self._parse("region", *args, **kwargs)
            self._handle_region(parsed_args)
    
    def _handle_region(self, arg_map: dict[str, Any]):
        """Handle region command
        
        Args:
            arg_map: Parsed arguments from _parse method
        """
        tag = arg_map.get("tag")
        
        if tag is None:
            return
            
        region_info = {
            "tag": tag,
            "node_tags": [],
            "ele_tags": [],
        }
        
        # Handle node tags
        node_tags = arg_map.get("node_tags", [])
        if node_tags:
            region_info["node_tags"].extend(node_tags)
            
        # Handle element tags
        ele_tags = arg_map.get("ele_tags", [])
        if ele_tags:
            region_info["ele_tags"].extend(ele_tags)
            
        # Handle element range
        ele_range = arg_map.get("ele_range", [])
        if len(ele_range) >= 2:
            start_ele, end_ele = ele_range[0], ele_range[1]
            region_info["ele_tags"].extend(range(start_ele, end_ele + 1))
            
        # Handle node range
        node_range = arg_map.get("node_range", [])
        if len(node_range) >= 2:
            start_node, end_node = node_range[0], node_range[1]
            region_info["node_tags"].extend(range(start_node, end_node + 1))
            
        # Handle Rayleigh damping parameters
        rayleigh_params = arg_map.get("rayleigh_params", [])
        if len(rayleigh_params) >= 4:
            region_info["rayleigh"] = {
                "alphaM": rayleigh_params[0],
                "betaK": rayleigh_params[1],
                "betaKinit": rayleigh_params[2],
                "betaKcomm": rayleigh_params[3],
            }
            
        # Store region information
        self.regions[tag] = region_info
    
    def get_region(self, tag: int) -> Optional[Dict[str, Any]]:
        """Get region information by tag
        
        Args:
            tag: Region tag
            
        Returns:
            Region information dictionary or None if not found
        """
        return self.regions.get(tag)
    
    def get_regions_with_node(self, node_tag: int) -> List[Dict[str, Any]]:
        """Get all regions containing a specific node
        
        Args:
            node_tag: Node tag
            
        Returns:
            List of region information dictionaries
        """
        result = []
        for region_info in self.regions.values():
            if node_tag in region_info.get("node_tags", []):
                result.append(region_info)
        return result
    
    def get_regions_with_element(self, ele_tag: int) -> List[Dict[str, Any]]:
        """Get all regions containing a specific element
        
        Args:
            ele_tag: Element tag
            
        Returns:
            List of region information dictionaries
        """
        result = []
        for region_info in self.regions.values():
            if ele_tag in region_info.get("ele_tags", []):
                result.append(region_info)
        return result
    
    def get_region_tags(self) -> List[int]:
        """Get all region tags
        
        Returns:
            List of region tags
        """
        return list(self.regions.keys())
    
    def clear(self):
        """Clear all region data"""
        self.regions.clear() 