"""基础模型命令类型注解"""

from typing import overload, Literal, Optional

class BasicCommands:
    """基础模型命令的类型注解"""
    
    # Model command
    def model(self, model_type: Literal["basic"], ndm_flag: Literal["-ndm"], ndm: int, ndf_flag: Literal["-ndf"], ndf: int) -> None:
        """Define the model
        
        Args:
            model_type: Model type 'basic'
            ndm_flag: Flag '-ndm' 
            ndm: Number of dimensions (1, 2, or 3)
            ndf_flag: Flag '-ndf'
            ndf: Number of degrees of freedom per node (ndm*(ndm+1)/2))
            
        Example:
            ops.model('basic', '-ndm', 2, '-ndf', 3)

            ops.model('basic', '-ndm', 3, '-ndf', 6)
        """
        ...

    # Node commands
    @overload
    def node(self, nodeTag: int, x_coord: float, y_coord: float) -> None:
        """Create a 2D node.

        Args:
            nodeTag (int): node tag.
            x_coord (float): X-coordinate.
            y_coord (float): Y-coordinate.

        Example:
            ops.node(1, 0.0, 0.0)  # 2D node
        """
        ...

    @overload
    def node(self, nodeTag: int, x_coord: float, y_coord: float, z_coord: float) -> None:
        """Create a 3D node.

        Args:
            nodeTag (int): node tag.
            x_coord (float): X-coordinate.
            y_coord (float): Y-coordinate.
            z_coord (float): Z-coordinate.

        Example:
            ops.node(1, 0.0, 0.0, 0.0)  # 3D node
        """
        ...

    @overload
    def node(self, nodeTag: int, x_coord: float, y_coord: float, flag: Literal["-ndf", "-mass", "-disp", "-vel", "-accel"], *args: float) -> None:
        """Create a 2D node with flag-based syntax.

        Args:
            nodeTag (int): node tag.
            x_coord (float): X-coordinate.
            y_coord (float): Y-coordinate.
            flag (Literal["-ndf", "-mass", "-disp", "-vel", "-accel"]): Flag for property type.
            args (float): Property values.

        Example:
            ops.node(1, 0.0, 0.0, '-mass', 100.0, 100.0, 0.1)

            ops.node(1, 0.0, 0.0, '-disp', 1.0, 0.0, 0.0)

            ops.node(1, 0.0, 0.0, '-vel', 1.0, 0.0, 0.0)

            ops.node(1, 0.0, 0.0, '-accel', 1.0, 0.0, 0.0)
        """
        ...

    @overload
    def node(self, nodeTag: int, x_coord: float, y_coord: float, z_coord: float, flag: Literal["-ndf", "-mass", "-disp", "-vel", "-accel"], *args: float) -> None:
        """Create a 3D node with flag-based syntax.

        Args:
            nodeTag (int): node tag.
            x_coord (float): X-coordinate.
            y_coord (float): Y-coordinate.
            z_coord (float): Z-coordinate.
            flag (Literal["-ndf", "-mass", "-disp", "-vel", "-accel"]): Flag for property type.
            args (float): Property values.

        Example:
            ops.node(1, 0.0, 0.0, 0.0, '-mass', 100.0, 100.0, 0.1)

            ops.node(1, 0.0, 0.0, 0.0, '-disp', 1.0, 0.0, 0.0)

            ops.node(1, 0.0, 0.0, 0.0, '-vel', 1.0, 0.0, 0.0)
            
            ops.node(1, 0.0, 0.0, 0.0, '-accel', 1.0, 0.0, 0.0)
        """
        ...

    # Mass command
    def mass(self, nodeTag: int, *massValues: float) -> None:
        """Assign mass to node
        
        Args:
            nodeTag: Node tag
            massValues: Mass values for each DOF
            
        Example:
            ops.mass(1, 100, 100, 100)

            ops.mass(1, *[100, 100, 100]) # use unpacking to pass a list of mass values
        """
        ...

    # Constraint commands
    def fix(self, nodeTag: int, *constraints: int) -> None:
        """Fix node DOFs
        
        Args:
            nodeTag: Node tag
            constraints: Constraint flags (1=fixed, 0=free)
            
        Example:
            ops.fix(1, 1, 1, 0)  # Fix X and Y, free rotation(ndf=3)
            
            ops.fix(1, *[1, 1, 1, 1, 1, 1])  # Fix All DOFs(ndf=6)
        """
        ...

    @overload  
    def fixX(self, x: float, *constrValues: int, tol: float = 1e-10) -> None:
        """Create homogeneous SP constraints along X-coordinate with tolerance
        
        Args:
            x: X-coordinate of nodes to be constrained
            constrValues: Constraint values (0=free, 1=fixed), must be preceded with *
            tol: User-defined tolerance (default: 1e-10)
            
        Example:
            ops.fixX(0.0, *[1, 1, 0], tol=1e-8)
        """
        ...

    @overload
    def fixY(self, y: float, *constrValues: int, tol: float = 1e-10) -> None:
        """Create homogeneous SP constraints along Y-coordinate with tolerance
        
        Args:
            y: Y-coordinate of nodes to be constrained
            constrValues: Constraint values (0=free, 1=fixed), must be preceded with *
            tol: User-defined tolerance (default: 1e-10)
            
        Example:
            ops.fixY(0.0, *[1, 1, 0], tol=1e-8)
        """
        ...

    @overload
    def fixZ(self, z: float, *constrValues: int) -> None:
        """Create homogeneous SP constraints along Z-coordinate
        
        Args:
            z: Z-coordinate of nodes to be constrained
            constrValues: Constraint values (0=free, 1=fixed), must be preceded with *
            
        Example:
            ops.fixZ(0.0, *[1, 1, 1, 1, 1, 1])  # Fix all DOFs at z=0.0
        """
        ...

    @overload
    def fixZ(self, z: float, *constrValues: int, tol: float = 1e-10) -> None:
        """Create homogeneous SP constraints along Z-coordinate with tolerance
        
        Args:
            z: Z-coordinate of nodes to be constrained
            constrValues: Constraint values (0=free, 1=fixed), must be preceded with *
            tol: User-defined tolerance (default: 1e-10)
            
        Example:
            ops.fixZ(0.0, *[1, 1, 1, 1, 1, 1], tol=1e-8)
        """
        ...
    
    def equalDOF(self, rNodeTag: int, cNodeTag: int, *dofs: int) -> None:
        """Create a multi-point constraint between nodes
        
        Args:
            rNodeTag: Integer tag identifying the retained, or primary node
            cNodeTag: Integer tag identifying the constrained, or secondary node  
            dofs: Nodal degrees-of-freedom that are constrained at the cNode to be the same as those at the rNode.
                  Valid range is from 1 through ndf, the number of nodal degrees-of-freedom
            
        Example:
            ops.equalDOF(1, 2, 1, 2)  # Equal X and Y displacements between nodes 1 and 2
            
            ops.equalDOF(1, 2, 1, 2, 3)  # Equal X, Y and Z displacements
        """
        ...
    
    def equalDOF_Mixed(self, rNodeTag: int, cNodeTag: int, numDOF: int, *rcdofs: int) -> None:
        """Create a multi-point constraint between nodes with mixed DOF mapping
        
        Args:
            rNodeTag: Integer tag identifying the retained, or master node
            cNodeTag: Integer tag identifying the constrained, or slave node
            numDOF: Number of DOFs to be constrained
            rcdofs: Nodal degrees-of-freedom mapping [rdof1, cdof1, rdof2, cdof2, ...].
                   Valid range is from 1 through ndf, the number of nodal degrees-of-freedom
            
        Example:
            ops.equalDOF_Mixed(1, 2, 2, 1, 1, 2, 3)  # Map DOF 1 of node 1 to DOF 1 of node 2, and DOF 2 of node 1 to DOF 3 of node 2
            
            ops.equalDOF_Mixed(1, 2, 1, 3, 2)  # Map DOF 3 of node 1 to DOF 2 of node 2
        """
        ...
    
    def rigidDiaphragm(self, perpDirn: int, rNodeTag: int, *cNodeTags: int) -> None:
        """Create a multi-point constraint between nodes for rigid diaphragm
        
        Args:
            perpDirn: Direction perpendicular to the rigid plane (i.e. direction 3 corresponds to the 1-2 plane)
            rNodeTag: Integer tag identifying the retained (primary) node
            cNodeTags: Integer tags identifying the constrained (secondary) nodes
            
        Note:
            These objects will constrain certain degrees-of-freedom at the listed secondary nodes 
            to move as if in a rigid plane with the primary (retained) node. 
            To enforce this constraint, Transformation constraint handler is recommended.
            
        Example:
            ops.rigidDiaphragm(3, 1, 2, 3, 4)  # XY plane rigid diaphragm (perpendicular to Z direction)
            
            ops.rigidDiaphragm(1, 5, 6, 7, 8, 9)  # YZ plane rigid diaphragm (perpendicular to X direction)
        """
        ...
    
    def rigidLink(self, type: Literal["bar", "beam"], rNodeTag: int, cNodeTag: int) -> None:
        """Create a multi-point constraint between nodes using rigid link
        
        Args:
            type: String-based argument for rigid-link type:
                  - 'bar': only the translational degree-of-freedom will be constrained to be exactly the same as those at the master node
                  - 'beam': both the translational and rotational degrees of freedom are constrained
            rNodeTag: Integer tag identifying the master node
            cNodeTag: Integer tag identifying the slave node
            
        Example:
            ops.rigidLink('bar', 1, 2)  # Rigid bar link between nodes 1 and 2 (translation only)
            
            ops.rigidLink('beam', 1, 2)  # Rigid beam link between nodes 1 and 2 (translation and rotation)
        """
        ... 