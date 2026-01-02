from typing import Any, Optional, Dict, List

from ._BaseHandler import BaseHandler


class BlockManager(BaseHandler):
    """Manager for block commands in OpenSeesPy
    
    Handles block commands for creating regular meshes of nodes and elements.
    """
    
    def __init__(self):
        self.blocks = {}  # tag -> block_info
        
    @property
    def _COMMAND_RULES(self) -> dict[str, dict[str, Any]]:
        """Define parsing rules for block commands"""
        return {
            # block2D(nx, ny, startNode, startEle, eleType, *eleArgs)
            "block2D": {
                "positional": ["nx", "ny", "start_node", "start_ele", "ele_type", "ele_args*"],
            },
            # block3D(nx, ny, nz, startNode, startEle, eleType, *eleArgs)
            "block3D": {
                "positional": ["nx", "ny", "nz", "start_node", "start_ele", "ele_type", "ele_args*"],
            },
        }
    
    def handles(self) -> List[str]:
        """Return list of commands this manager handles"""
        return ["block2D", "block3D"]
    
    def handle(self, func_name: str, arg_map: dict[str, Any]):
        """Handle block commands"""
        args, kwargs = arg_map.get("args"), arg_map.get("kwargs")
        
        if func_name == "block2D":
            parsed_args = self._parse("block2D", *args, **kwargs)
            self._handle_block2d(parsed_args)
        elif func_name == "block3D":
            parsed_args = self._parse("block3D", *args, **kwargs)
            self._handle_block3d(parsed_args)
    
    def _handle_block2d(self, arg_map: dict[str, Any]):
        """Handle block2D command
        
        Args:
            arg_map: Parsed arguments from _parse method
        """
        nx = arg_map.get("nx")
        ny = arg_map.get("ny")
        start_node = arg_map.get("start_node")
        start_ele = arg_map.get("start_ele")
        ele_type = arg_map.get("ele_type")
        ele_args = arg_map.get("ele_args", [])
        
        if any(param is None for param in [nx, ny, start_node, start_ele, ele_type]):
            return
            
        block_info = {
            "type": "block2D",
            "dimensions": {"nx": nx, "ny": ny},
            "start_node": start_node,
            "start_ele": start_ele,
            "ele_type": ele_type,
            "ele_args": ele_args,
            "generated_nodes": self._calculate_2d_nodes(nx, ny, start_node),
            "generated_elements": self._calculate_2d_elements(nx, ny, start_ele),
        }
        
        # Use a unique key based on start node and element
        block_key = f"2D_{start_node}_{start_ele}"
        self.blocks[block_key] = block_info
    
    def _handle_block3d(self, arg_map: dict[str, Any]):
        """Handle block3D command
        
        Args:
            arg_map: Parsed arguments from _parse method
        """
        nx = arg_map.get("nx")
        ny = arg_map.get("ny")
        nz = arg_map.get("nz")
        start_node = arg_map.get("start_node")
        start_ele = arg_map.get("start_ele")
        ele_type = arg_map.get("ele_type")
        ele_args = arg_map.get("ele_args", [])
        
        if any(param is None for param in [nx, ny, nz, start_node, start_ele, ele_type]):
            return
            
        block_info = {
            "type": "block3D",
            "dimensions": {"nx": nx, "ny": ny, "nz": nz},
            "start_node": start_node,
            "start_ele": start_ele,
            "ele_type": ele_type,
            "ele_args": ele_args,
            "generated_nodes": self._calculate_3d_nodes(nx, ny, nz, start_node),
            "generated_elements": self._calculate_3d_elements(nx, ny, nz, start_ele),
        }
        
        # Use a unique key based on start node and element
        block_key = f"3D_{start_node}_{start_ele}"
        self.blocks[block_key] = block_info
    
    def _calculate_2d_nodes(self, nx: int, ny: int, start_node: int) -> List[int]:
        """Calculate generated node tags for 2D block
        
        Args:
            nx: Number of divisions in x direction
            ny: Number of divisions in y direction
            start_node: Starting node tag
            
        Returns:
            List of generated node tags
        """
        nodes = []
        for j in range(ny + 1):
            for i in range(nx + 1):
                node_tag = start_node + j * (nx + 1) + i
                nodes.append(node_tag)
        return nodes
    
    def _calculate_3d_nodes(self, nx: int, ny: int, nz: int, start_node: int) -> List[int]:
        """Calculate generated node tags for 3D block
        
        Args:
            nx: Number of divisions in x direction
            ny: Number of divisions in y direction
            nz: Number of divisions in z direction
            start_node: Starting node tag
            
        Returns:
            List of generated node tags
        """
        nodes = []
        for k in range(nz + 1):
            for j in range(ny + 1):
                for i in range(nx + 1):
                    node_tag = start_node + k * (nx + 1) * (ny + 1) + j * (nx + 1) + i
                    nodes.append(node_tag)
        return nodes
    
    def _calculate_2d_elements(self, nx: int, ny: int, start_ele: int) -> List[int]:
        """Calculate generated element tags for 2D block
        
        Args:
            nx: Number of divisions in x direction
            ny: Number of divisions in y direction
            start_ele: Starting element tag
            
        Returns:
            List of generated element tags
        """
        elements = []
        for j in range(ny):
            for i in range(nx):
                ele_tag = start_ele + j * nx + i
                elements.append(ele_tag)
        return elements
    
    def _calculate_3d_elements(self, nx: int, ny: int, nz: int, start_ele: int) -> List[int]:
        """Calculate generated element tags for 3D block
        
        Args:
            nx: Number of divisions in x direction
            ny: Number of divisions in y direction
            nz: Number of divisions in z direction
            start_ele: Starting element tag
            
        Returns:
            List of generated element tags
        """
        elements = []
        for k in range(nz):
            for j in range(ny):
                for i in range(nx):
                    ele_tag = start_ele + k * nx * ny + j * nx + i
                    elements.append(ele_tag)
        return elements
    
    def get_block(self, block_key: str) -> Optional[Dict[str, Any]]:
        """Get block information by key
        
        Args:
            block_key: Block key (e.g., "2D_1_1" or "3D_1_1")
            
        Returns:
            Block information dictionary or None if not found
        """
        return self.blocks.get(block_key)
    
    def get_blocks_by_type(self, block_type: str) -> List[Dict[str, Any]]:
        """Get all blocks of a specific type
        
        Args:
            block_type: Block type ("block2D" or "block3D")
            
        Returns:
            List of block information dictionaries
        """
        result = []
        for block_info in self.blocks.values():
            if block_info.get("type") == block_type:
                result.append(block_info)
        return result
    
    def get_all_generated_nodes(self) -> List[int]:
        """Get all node tags generated by blocks
        
        Returns:
            List of all generated node tags
        """
        all_nodes = []
        for block_info in self.blocks.values():
            all_nodes.extend(block_info.get("generated_nodes", []))
        return list(set(all_nodes))  # Remove duplicates
    
    def get_all_generated_elements(self) -> List[int]:
        """Get all element tags generated by blocks
        
        Returns:
            List of all generated element tags
        """
        all_elements = []
        for block_info in self.blocks.values():
            all_elements.extend(block_info.get("generated_elements", []))
        return list(set(all_elements))  # Remove duplicates
    
    def clear(self):
        """Clear all block data"""
        self.blocks.clear() 