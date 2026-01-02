"""Geometry transformation command type annotations"""

from typing import overload, Literal, Optional, Any, List

class GeometryCommands:
    """Type annotations for geometry transformation commands"""
    
    # Linear transformation
    @overload  
    def geomTransf(self, transf_type: Literal["Linear"], transf_tag: int, vec_x: Optional[float] = None, vec_y: Optional[float] = None, vec_z: Optional[float] = None, jnt_offset: Optional[Literal["-jntOffset"]] = None, *offsets: float) -> None:
        """Define linear coordinate transformation
        
        Args:
            transf_type: Transformation type 'Linear'
            transf_tag: Integer tag identifying transformation
            vec_x, vec_y, vec_z: X, Y, and Z components of vecxz vector defining local x-z plane (3D only)
            jnt_offset: Joint offset flag '-jntOffset' (optional)
            offsets: Joint offset values for nodes i and j (when jnt_offset is specified)
            
        Examples:
            ops.geomTransf('Linear', 1)                                    # 2D basic
            ops.geomTransf('Linear', 1, 0.0, 0.0, 1.0)                     # 3D with vecxz
            ops.geomTransf('Linear', 1, None, None, None, '-jntOffset', dI1, dI2, dJ1, dJ2)  # with offsets
            ops.geomTransf('Linear', 1, 0.0, 0.0, 1.0, '-jntOffset', dI1, dI2, dI3, dJ1, dJ2, dJ3)  # 3D with offsets
        """
        ...
    
    # PDelta transformation
    @overload
    def geomTransf(self, transf_type: Literal["PDelta"], transf_tag: int, vec_x: Optional[float] = None, vec_y: Optional[float] = None, vec_z: Optional[float] = None, jnt_offset: Optional[Literal["-jntOffset"]] = None, *offsets: float) -> None:
        """Define P-Delta coordinate transformation
        
        Args:
            transf_type: Transformation type 'PDelta'
            transf_tag: Integer tag identifying transformation
            vec_x, vec_y, vec_z: X, Y, and Z components of vecxz vector defining local x-z plane (3D only)
            jnt_offset: Joint offset flag '-jntOffset' (optional)
            offsets: Joint offset values for nodes i and j (when jnt_offset is specified)
            
        Examples:
            ops.geomTransf('PDelta', 1)                                    # 2D basic
            ops.geomTransf('PDelta', 1, 0.0, 0.0, 1.0)                     # 3D with vecxz
            ops.geomTransf('PDelta', 1, None, None, None, '-jntOffset', dI1, dI2, dJ1, dJ2)  # with offsets
            ops.geomTransf('PDelta', 1, 0.0, 0.0, 1.0, '-jntOffset', dI1, dI2, dI3, dJ1, dJ2, dJ3)  # 3D with offsets
        """
        ...
    
    # Corotational transformation
    @overload
    def geomTransf(self, transf_type: Literal["Corotational"], transf_tag: int, vec_x: Optional[float] = None, vec_y: Optional[float] = None, vec_z: Optional[float] = None, jnt_offset: Optional[Literal["-jntOffset"]] = None, *offsets: float) -> None:
        """Define corotational coordinate transformation
        
        Args:
            transf_type: Transformation type 'Corotational'
            transf_tag: Integer tag identifying transformation
            vec_x, vec_y, vec_z: X, Y, and Z components of vecxz vector defining local x-z plane (3D only)
            jnt_offset: Joint offset flag '-jntOffset' (optional)
            offsets: Joint offset values for nodes i and j (when jnt_offset is specified)
            
        Examples:
            ops.geomTransf('Corotational', 1)                              # 2D basic
            ops.geomTransf('Corotational', 1, 0.0, 0.0, 1.0)               # 3D with vecxz
            ops.geomTransf('Corotational', 1, None, None, None, '-jntOffset', dI1, dI2, dJ1, dJ2)  # with offsets
        """
        ...
    
    # Generic transformation fallback
    @overload
    def geomTransf(self, transf_type: Literal["Linear", "PDelta", "Corotational"], transf_tag: int, *transf_args: Any) -> None:
        """Define coordinate transformation (generic fallback with known types)
        
        Args:
            transf_type: Transformation type (Linear, PDelta, or Corotational)
            transf_tag: Integer tag identifying transformation
            transf_args: Transformation arguments
            
        Example:
            ops.geomTransf('Linear', 1, *args)
        """
        ... 