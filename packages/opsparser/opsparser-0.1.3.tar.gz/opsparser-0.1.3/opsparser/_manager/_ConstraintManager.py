from typing import Any, Optional, Dict, List

from ._BaseHandler import BaseHandler


class ConstraintManager(BaseHandler):
    """Manager for constraint commands in OpenSeesPy
    
    Handles single-point (SP) constraints, multi-point (MP) constraints,
    and pressure constraints.
    """
    
    def __init__(self):
        self.sp_constraints = {}  # nodeTag -> constraint_info
        self.mp_constraints = []  # list of MP constraint info
        self.pressure_constraints = []  # list of pressure constraint info
        
    @property
    def _COMMAND_RULES(self) -> dict[str, dict[str, Any]]:
        """Define parsing rules for constraint commands"""
        return {
            # fix(nodeTag, *constrValues)
            "fix": {
                "positional": ["node_tag", "constraints*"],
            },
            # fixX(x, *constrValues, '-tol', tol)
            "fixX": {
                "positional": ["x", "constraints*"],
                "options": {
                    "-tol?": "tolerance",
                },
            },
            # fixY(y, *constrValues, '-tol', tol)
            "fixY": {
                "positional": ["y", "constraints*"],
                "options": {
                    "-tol?": "tolerance",
                },
            },
            # fixZ(z, *constrValues, '-tol', tol)
            "fixZ": {
                "positional": ["z", "constraints*"],
                "options": {
                    "-tol?": "tolerance",
                },
            },
            # equalDOF(rNodeTag, cNodeTag, *dofs)
            "equalDOF": {
                "positional": ["retained_node", "constrained_node", "dofs*"],
            },
            # equalDOF_Mixed(rNodeTag, cNodeTag, numDOF, rcdofs)
            "equalDOF_Mixed": {
                "positional": ["retained_node", "constrained_node", "num_dof", "dofs*"],
            },
            # rigidDiaphragm(perpDirn, rNodeTag, *cNodeTags)
            "rigidDiaphragm": {
                "positional": ["perp_dirn", "retained_node", "constrained_nodes*"],
            },
            # rigidLink(type, rNodeTag, cNodeTag)
            "rigidLink": {
                "positional": ["type", "retained_node", "constrained_node"],
            },
            # pressureConstraint(eleTag1, eleTag2, pressure)
            "pressureConstraint": {
                "positional": ["ele_tag1", "ele_tag2", "pressure"],
            },
        }
    
    def handles(self) -> List[str]:
        """Return list of commands this manager handles"""
        return [
            "fix", "fixX", "fixY", "fixZ",
            "equalDOF", "equalDOF_Mixed", 
            "rigidDiaphragm", "rigidLink",
            "pressureConstraint"
        ]
    
    def handle(self, func_name: str, arg_map: dict[str, Any]):
        """Handle constraint commands"""
        args, kwargs = arg_map.get("args"), arg_map.get("kwargs")
        
        if func_name == "fix":
            parsed_args = self._parse("fix", *args, **kwargs)
            self._handle_fix(parsed_args)
        elif func_name in ["fixX", "fixY", "fixZ"]:
            parsed_args = self._parse(func_name, *args, **kwargs)
            self._handle_fix_coordinate(func_name, parsed_args)
        elif func_name in ["equalDOF", "equalDOF_Mixed"]:
            parsed_args = self._parse(func_name, *args, **kwargs)
            self._handle_equal_dof(func_name, parsed_args)
        elif func_name == "rigidDiaphragm":
            parsed_args = self._parse("rigidDiaphragm", *args, **kwargs)
            self._handle_rigid_diaphragm(parsed_args)
        elif func_name == "rigidLink":
            parsed_args = self._parse("rigidLink", *args, **kwargs)
            self._handle_rigid_link(parsed_args)
        elif func_name == "pressureConstraint":
            parsed_args = self._parse("pressureConstraint", *args, **kwargs)
            self._handle_pressure_constraint(parsed_args)
    
    def _handle_fix(self, arg_map: dict[str, Any]):
        """Handle fix command"""
        node_tag = arg_map.get("node_tag")
        constraints = arg_map.get("constraints", [])
        
        if node_tag is None or not constraints:
            return
            
        constraint_info = {
            "type": "fix",
            "node_tag": node_tag,
            "constraints": constraints,
        }
        
        self.sp_constraints[node_tag] = constraint_info
    
    def _handle_fix_coordinate(self, func_name: str, arg_map: dict[str, Any]):
        """Handle fixX, fixY, fixZ commands"""
        coord_value = arg_map.get(func_name[-1].lower())  # x, y, or z
        constraints = arg_map.get("constraints", [])
        tolerance = arg_map.get("tolerance", 1e-10)
        
        if coord_value is None or not constraints:
            return
            
        constraint_info = {
            "type": func_name,
            "coordinate": func_name[-1],  # X, Y, or Z
            "value": coord_value,
            "constraints": constraints,
            "tolerance": tolerance,
        }
        
        # Store in a special key for coordinate-based constraints
        key = f"{func_name}_{coord_value}_{tolerance}"
        self.sp_constraints[key] = constraint_info
    
    def _handle_equal_dof(self, func_name: str, arg_map: dict[str, Any]):
        """Handle equalDOF and equalDOF_Mixed commands"""
        retained_node = arg_map.get("retained_node")
        constrained_node = arg_map.get("constrained_node")
        
        if retained_node is None or constrained_node is None:
            return
            
        constraint_info = {
            "type": func_name,
            "retained_node": retained_node,
            "constrained_node": constrained_node,
        }
        
        if func_name == "equalDOF":
            dofs = arg_map.get("dofs", [])
            constraint_info["dofs"] = dofs
        else:  # equalDOF_Mixed
            num_dof = arg_map.get("num_dof")
            dofs = arg_map.get("dofs", [])
            constraint_info["num_dof"] = num_dof
            constraint_info["dofs"] = dofs
            
        self.mp_constraints.append(constraint_info)
    
    def _handle_rigid_diaphragm(self, arg_map: dict[str, Any]):
        """Handle rigidDiaphragm command"""
        perp_dirn = arg_map.get("perp_dirn")
        retained_node = arg_map.get("retained_node")
        constrained_nodes = arg_map.get("constrained_nodes", [])
        
        if perp_dirn is None or retained_node is None or not constrained_nodes:
            return
            
        constraint_info = {
            "type": "rigidDiaphragm",
            "perp_dirn": perp_dirn,
            "retained_node": retained_node,
            "constrained_nodes": constrained_nodes,
        }
        
        self.mp_constraints.append(constraint_info)
    
    def _handle_rigid_link(self, arg_map: dict[str, Any]):
        """Handle rigidLink command"""
        link_type = arg_map.get("type")
        retained_node = arg_map.get("retained_node")
        constrained_node = arg_map.get("constrained_node")
        
        if link_type is None or retained_node is None or constrained_node is None:
            return
            
        constraint_info = {
            "type": "rigidLink",
            "link_type": link_type,
            "retained_node": retained_node,
            "constrained_node": constrained_node,
        }
        
        self.mp_constraints.append(constraint_info)
    
    def _handle_pressure_constraint(self, arg_map: dict[str, Any]):
        """Handle pressureConstraint command"""
        ele_tag1 = arg_map.get("ele_tag1")
        ele_tag2 = arg_map.get("ele_tag2")
        pressure = arg_map.get("pressure")
        
        if ele_tag1 is None or ele_tag2 is None or pressure is None:
            return
            
        constraint_info = {
            "type": "pressureConstraint",
            "ele_tag1": ele_tag1,
            "ele_tag2": ele_tag2,
            "pressure": pressure,
        }
        
        self.pressure_constraints.append(constraint_info)
    
    def get_sp_constraint(self, node_tag: int) -> Optional[Dict[str, Any]]:
        """Get single-point constraint for a node
        
        Args:
            node_tag: Node tag
            
        Returns:
            Constraint information or None if not found
        """
        return self.sp_constraints.get(node_tag)
    
    def get_mp_constraints(self) -> List[Dict[str, Any]]:
        """Get all multi-point constraints
        
        Returns:
            List of MP constraint information
        """
        return self.mp_constraints.copy()
    
    def get_pressure_constraints(self) -> List[Dict[str, Any]]:
        """Get all pressure constraints
        
        Returns:
            List of pressure constraint information
        """
        return self.pressure_constraints.copy()
    
    def clear(self):
        """Clear all constraint data"""
        self.sp_constraints.clear()
        self.mp_constraints.clear()
        self.pressure_constraints.clear() 