from typing import Any, Optional, Dict, List

from ._BaseHandler import BaseHandler


class GeomTransfManager(BaseHandler):
    """Manager for geomTransf commands in OpenSeesPy
    
    Handles geomTransf command which creates coordinate transformation objects
    for geometric transformation of beam-column elements.
    """
    
    def __init__(self):
        self.transformations = {}  # tag -> transformation_info
        
    @property
    def _COMMAND_RULES(self) -> dict[str, dict[str, Any]]:
        """Define parsing rules for geomTransf commands"""
        return {
            # geomTransf(type, tag, *args)
            "geomTransf": {
                "positional": ["transf_type", "tag", "args*"],
                "options": {
                    "-jntOffset?": "joint_offset*",
                },
            },
        }
    
    def handles(self) -> List[str]:
        """Return list of commands this manager handles"""
        return ["geomTransf"]
    
    def handle(self, func_name: str, arg_map: dict[str, Any]):
        """Handle geomTransf commands"""
        if func_name == "geomTransf":
            args, kwargs = arg_map.get("args"), arg_map.get("kwargs")
            parsed_args = self._parse("geomTransf", *args, **kwargs)
            self._handle_geom_transf(parsed_args)
    
    def _handle_geom_transf(self, arg_map: dict[str, Any]):
        """Handle geomTransf command
        
        Args:
            arg_map: Parsed arguments from _parse method
        """
        transf_type = arg_map.get("transf_type")
        tag = arg_map.get("tag")
        
        if not transf_type or tag is None:
            return
            
        args = arg_map.get("args", [])
        joint_offset = arg_map.get("joint_offset", [])
        
        transformation_info = {
            "type": transf_type,
            "tag": tag,
            "args": args,
        }
        
        # Handle joint offset option
        if joint_offset:
            transformation_info["joint_offset"] = joint_offset
        
        # Parse specific transformation types and their parameters
        if transf_type == "Linear":
            # Linear(tag) for 2D
            # Linear(tag, vecxzX, vecxzY, vecxzZ) for 3D
            if len(args) >= 3:
                transformation_info["vecxz"] = [args[0], args[1], args[2]]
            elif len(args) == 0:
                transformation_info["dimension"] = "2D"
            else:
                transformation_info["dimension"] = "3D"
                
        elif transf_type == "PDelta":
            # PDelta(tag) for 2D
            # PDelta(tag, vecxzX, vecxzY, vecxzZ) for 3D
            if len(args) >= 3:
                transformation_info["vecxz"] = [args[0], args[1], args[2]]
            elif len(args) == 0:
                transformation_info["dimension"] = "2D"
            else:
                transformation_info["dimension"] = "3D"
                
        elif transf_type == "Corotational":
            # Corotational(tag) for 2D
            # Corotational(tag, vecxzX, vecxzY, vecxzZ) for 3D
            if len(args) >= 3:
                transformation_info["vecxz"] = [args[0], args[1], args[2]]
            elif len(args) == 0:
                transformation_info["dimension"] = "2D"
            else:
                transformation_info["dimension"] = "3D"
        
        # Store transformation information
        self.transformations[tag] = transformation_info
    
    def get_transformation(self, tag: int) -> Optional[Dict[str, Any]]:
        """Get geometric transformation information by tag
        
        Args:
            tag: Transformation tag
            
        Returns:
            Transformation information dictionary or None if not found
        """
        return self.transformations.get(tag)
    
    def get_transformations_by_type(self, transf_type: str) -> List[Dict[str, Any]]:
        """Get all transformations of a specific type
        
        Args:
            transf_type: Transformation type (e.g., 'Linear', 'PDelta', 'Corotational')
            
        Returns:
            List of transformation information dictionaries
        """
        result = []
        for transformation_info in self.transformations.values():
            if transformation_info.get("type") == transf_type:
                result.append(transformation_info)
        return result
    
    def get_2d_transformations(self) -> List[Dict[str, Any]]:
        """Get all 2D transformations
        
        Returns:
            List of 2D transformation information dictionaries
        """
        result = []
        for transformation_info in self.transformations.values():
            if transformation_info.get("dimension") == "2D":
                result.append(transformation_info)
            elif "vecxz" not in transformation_info and "dimension" not in transformation_info:
                # Assume 2D if no vector specified and no dimension info
                result.append(transformation_info)
        return result
    
    def get_3d_transformations(self) -> List[Dict[str, Any]]:
        """Get all 3D transformations
        
        Returns:
            List of 3D transformation information dictionaries
        """
        result = []
        for transformation_info in self.transformations.values():
            if transformation_info.get("dimension") == "3D" or "vecxz" in transformation_info:
                result.append(transformation_info)
        return result
    
    def get_transformation_tags(self) -> List[int]:
        """Get all transformation tags
        
        Returns:
            List of transformation tags
        """
        return list(self.transformations.keys())
    
    def clear(self):
        """Clear all geometric transformation data"""
        self.transformations.clear() 