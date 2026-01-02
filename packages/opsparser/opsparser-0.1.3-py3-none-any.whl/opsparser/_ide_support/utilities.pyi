"""实用工具命令类型注解"""

from typing import List, Union, Optional, Any

class UtilityCommands:
    """实用工具命令的类型注解"""
    
    # Model management
    def wipe(self) -> None:
        """Clear all model data
        
        Example:
            ops.wipe()
        """
        ...
    
    def remove(self, object_type: str, *tags: int) -> None:
        """Remove objects from model
        
        Args:
            object_type: Type of object to remove ('node', 'element', 'loadPattern', etc.)
            tags: Object tags to remove
            
        Examples:
            ops.remove('node', 1, 2, 3)
            ops.remove('element', 1)
            ops.remove('loadPattern', 1)
        """
        ...
    
    # Information retrieval
    def getNodeTags(self) -> List[int]:
        """Get all node tags
        
        Returns:
            List of node tags
            
        Example:
            node_tags = ops.getNodeTags()
        """
        ...
    
    def getEleTags(self) -> List[int]:
        """Get all element tags
        
        Returns:
            List of element tags
            
        Example:
            element_tags = ops.getEleTags()
        """
        ...
    
    def getLoadTags(self, pattern_type: str = "Plain") -> List[int]:
        """Get load pattern tags
        
        Args:
            pattern_type: Type of load pattern (default 'Plain')
            
        Returns:
            List of load pattern tags
            
        Example:
            load_tags = ops.getLoadTags()
        """
        ...
    
    # Node information
    def nodeCoord(self, node_tag: int, dof: Optional[int] = None) -> Union[float, List[float]]:
        """Get node coordinates
        
        Args:
            node_tag: Node tag
            dof: Specific coordinate direction (optional)
            
        Returns:
            Node coordinate(s)
            
        Examples:
            coords = ops.nodeCoord(1)        # All coordinates
            x_coord = ops.nodeCoord(1, 1)    # X coordinate only
        """
        ...
    
    def nodeDisp(self, node_tag: int, dof: Optional[int] = None) -> Union[float, List[float]]:
        """Get node displacements
        
        Args:
            node_tag: Node tag
            dof: Specific DOF (optional)
            
        Returns:
            Node displacement(s)
            
        Examples:
            disps = ops.nodeDisp(1)          # All displacements
            u_x = ops.nodeDisp(1, 1)         # X displacement only
        """
        ...
    
    def nodeVel(self, node_tag: int, dof: Optional[int] = None) -> Union[float, List[float]]:
        """Get node velocities
        
        Args:
            node_tag: Node tag
            dof: Specific DOF (optional)
            
        Returns:
            Node velocity(ies)
            
        Examples:
            vels = ops.nodeVel(1)            # All velocities
            v_x = ops.nodeVel(1, 1)          # X velocity only
        """
        ...
    
    def nodeAccel(self, node_tag: int, dof: Optional[int] = None) -> Union[float, List[float]]:
        """Get node accelerations
        
        Args:
            node_tag: Node tag
            dof: Specific DOF (optional)
            
        Returns:
            Node acceleration(s)
            
        Examples:
            accels = ops.nodeAccel(1)        # All accelerations
            a_x = ops.nodeAccel(1, 1)        # X acceleration only
        """
        ...
    
    def nodeReaction(self, node_tag: int, dof: Optional[int] = None) -> Union[float, List[float]]:
        """Get node reactions
        
        Args:
            node_tag: Node tag
            dof: Specific DOF (optional)
            
        Returns:
            Node reaction(s)
            
        Examples:
            reactions = ops.nodeReaction(1)  # All reactions
            r_x = ops.nodeReaction(1, 1)     # X reaction only
        """
        ...
    
    # Element information
    def eleForce(self, element_tag: int, *args: Any) -> List[float]:
        """Get element forces
        
        Args:
            element_tag: Element tag
            args: Additional arguments (element type specific)
            
        Returns:
            Element force vector
            
        Example:
            forces = ops.eleForce(1)
        """
        ...
    
    def eleNodes(self, element_tag: int) -> List[int]:
        """Get element node tags
        
        Args:
            element_tag: Element tag
            
        Returns:
            List of node tags connected to element
            
        Example:
            nodes = ops.eleNodes(1)
        """
        ...
    
    def eleResponse(self, element_tag: int, *args: str) -> Union[float, List[float]]:
        """Get element response
        
        Args:
            element_tag: Element tag
            args: Response type arguments
            
        Returns:
            Element response value(s)
            
        Examples:
            stress = ops.eleResponse(1, 'material', '1', 'stress')
            strain = ops.eleResponse(1, 'material', '1', 'strain')
        """
        ...
    
    # Analysis information
    def getTime(self) -> float:
        """Get current analysis time
        
        Returns:
            Current time
            
        Example:
            current_time = ops.getTime()
        """
        ...
    
    def getLoadFactor(self, pattern_tag: int) -> float:
        """Get load factor for load pattern
        
        Args:
            pattern_tag: Load pattern tag
            
        Returns:
            Current load factor
            
        Example:
            lambda_factor = ops.getLoadFactor(1)
        """
        ...
    
    # Recording and output
    def recorder(self, recorder_type: str, *args: Any) -> None:
        """Create recorder
        
        Args:
            recorder_type: Type of recorder ('Node', 'Element', 'EnvelopeNode', etc.)
            args: Recorder-specific arguments
            
        Examples:
            ops.recorder('Node', '-file', 'disp.out', '-time', '-node', 1, 2, '-dof', 1, 2, 'disp')
            ops.recorder('Element', '-file', 'force.out', '-time', '-ele', 1, 2, 'force')
        """
        ...
    
    def record(self) -> None:
        """Record current state
        
        Example:
            ops.record()
        """
        ...
    
    # Print commands
    def printModel(self, *args: str) -> None:
        """Print model information
        
        Args:
            args: Print options ('-node', '-ele', etc.)
            
        Examples:
            ops.printModel()
            ops.printModel('-node')
            ops.printModel('-ele')
        """
        ...
    
    def printA(self, filename: Optional[str] = None) -> None:
        """Print system matrix A
        
        Args:
            filename: Output filename (optional)
            
        Example:
            ops.printA('matrix_A.out')
        """
        ... 