"""Element command type annotations for OpenSeesPy"""

from typing import overload, Literal, Any, Union

class ElementCommands:
    """Type annotations for OpenSeesPy element commands"""
    
    # ============================================================================
    # Zero-Length Elements
    # ============================================================================
    
    @overload
    def element(self, element_type: Literal["zeroLength"], element_tag: int, node_i: int, node_j: int, 
                x: float, y: float, z: float, *args: Any) -> None:
        """Create zero-length element
        
        Args:
            element_type: Element type 'zeroLength'
            element_tag: Unique element identifier
            node_i: Start node tag
            node_j: End node tag
            x, y, z: Direction vector components
            args: Material tags and DOF directions
            
        Example:
            ops.element('zeroLength', 1, 1, 2, 0.0, 0.0, 1.0, '-mat', 1, '-dir', 1)
        """
        ...
    
    @overload
    def element(self, element_type: Literal["zeroLengthND"], element_tag: int, node_i: int, node_j: int, 
                nd: int, *args: Any) -> None:
        """Create zero-length ND element
        
        Args:
            element_type: Element type 'zeroLengthND'
            element_tag: Unique element identifier
            node_i: Start node tag
            node_j: End node tag
            nd: Number of dimensions
            args: Material tags and DOF directions
        """
        ...
    
    @overload
    def element(self, element_type: Literal["zeroLengthSection"], element_tag: int, node_i: int, node_j: int, 
                section_tag: int, *args: Any) -> None:
        """Create zero-length section element
        
        Args:
            element_type: Element type 'zeroLengthSection'
            element_tag: Unique element identifier
            node_i: Start node tag
            node_j: End node tag
            section_tag: Section tag
            args: Additional parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["CoupledZeroLength"], element_tag: int, node_i: int, node_j: int, 
                *args: Any) -> None:
        """Create coupled zero-length element
        
        Args:
            element_type: Element type 'CoupledZeroLength'
            element_tag: Unique element identifier
            node_i: Start node tag
            node_j: End node tag
            args: Coupling parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["zeroLengthContact"], element_tag: int, node_i: int, node_j: int, 
                *args: Any) -> None:
        """Create zero-length contact element
        
        Args:
            element_type: Element type 'zeroLengthContact'
            element_tag: Unique element identifier
            node_i: Start node tag
            node_j: End node tag
            args: Contact parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["zeroLengthContactNTS2D"], element_tag: int, node_i: int, node_j: int, 
                *args: Any) -> None:
        """Create zero-length contact NTS2D element
        
        Args:
            element_type: Element type 'zeroLengthContactNTS2D'
            element_tag: Unique element identifier
            node_i: Start node tag
            node_j: End node tag
            args: Contact parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["zeroLengthInterface2D"], element_tag: int, node_i: int, node_j: int, 
                *args: Any) -> None:
        """Create zero-length interface 2D element
        
        Args:
            element_type: Element type 'zeroLengthInterface2D'
            element_tag: Unique element identifier
            node_i: Start node tag
            node_j: End node tag
            args: Interface parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["zeroLengthImpact3D"], element_tag: int, node_i: int, node_j: int, 
                *args: Any) -> None:
        """Create zero-length impact 3D element
        
        Args:
            element_type: Element type 'zeroLengthImpact3D'
            element_tag: Unique element identifier
            node_i: Start node tag
            node_j: End node tag
            args: Impact parameters
        """
        ...
    
    # ============================================================================
    # Truss Elements
    # ============================================================================
    
    @overload
    def element(self, element_type: Literal["truss"], element_tag: int, node_i: int, node_j: int, 
                area: float, material_tag: int) -> None:
        """Create truss element
        
        Args:
            element_type: Element type 'truss'
            element_tag: Unique element identifier
            node_i: Start node tag
            node_j: End node tag
            area: Cross-sectional area
            material_tag: Material tag
            
        Example:
            ops.element('truss', 1, 1, 2, 100.0, 1)
        """
        ...
    
    @overload
    def element(self, element_type: Literal["corotTruss"], element_tag: int, node_i: int, node_j: int, 
                area: float, material_tag: int) -> None:
        """Create corotational truss element
        
        Args:
            element_type: Element type 'corotTruss'
            element_tag: Unique element identifier
            node_i: Start node tag
            node_j: End node tag
            area: Cross-sectional area
            material_tag: Material tag
        """
        ...
    
    # ============================================================================
    # Beam-Column Elements
    # ============================================================================
    
    @overload
    def element(self, element_type: Literal["elasticBeamColumn"], element_tag: int, node_i: int, node_j: int, 
                area: float, elastic_modulus: float, moment_of_inertia: float, geom_transf_tag: int) -> None:
        """Create elastic beam-column element
        
        Args:
            element_type: Element type 'elasticBeamColumn'
            element_tag: Unique element identifier
            node_i: Start node tag
            node_j: End node tag
            area: Cross-sectional area
            elastic_modulus: Elastic modulus
            moment_of_inertia: Moment of inertia
            geom_transf_tag: Geometric transformation tag
            
        Example:
            ops.element('elasticBeamColumn', 2, 1, 2, 100.0, 29000.0, 1000.0, 1)
        """
        ...
    
    @overload
    def element(self, element_type: Literal["elasticBeamColumn"], element_tag: int, node_i: int, node_j: int, 
                area: float, elastic_modulus: float, moment_of_inertia: float, geom_transf_tag: int,
                mass: float, *args: Any) -> None:
        """Create elastic beam-column element with stiffness modifiers
        
        Args:
            element_type: Element type 'elasticBeamColumn'
            element_tag: Unique element identifier
            node_i: Start node tag
            node_j: End node tag
            area: Cross-sectional area
            elastic_modulus: Elastic modulus
            moment_of_inertia: Moment of inertia
            geom_transf_tag: Geometric transformation tag
            mass: Mass per unit length
            args: Stiffness modifiers
        """
        ...
    
    @overload
    def element(self, element_type: Literal["elasticTimoshenkoBeam"], element_tag: int, node_i: int, node_j: int, 
                area: float, elastic_modulus: float, shear_modulus: float, moment_of_inertia: float, 
                geom_transf_tag: int, mass: float) -> None:
        """Create elastic Timoshenko beam-column element
        
        Args:
            element_type: Element type 'elasticTimoshenkoBeam'
            element_tag: Unique element identifier
            node_i: Start node tag
            node_j: End node tag
            area: Cross-sectional area
            elastic_modulus: Elastic modulus
            shear_modulus: Shear modulus
            moment_of_inertia: Moment of inertia
            geom_transf_tag: Geometric transformation tag
            mass: Mass per unit length
        """
        ...
    
    @overload
    def element(self, element_type: Literal["forceBeamColumn"], element_tag: int, node_i: int, node_j: int, 
                geom_transf_tag: int, integration_type: str, section_tag: int, num_integration_points: int) -> None:
        """Create force-based beam-column element
        
        Args:
            element_type: Element type 'forceBeamColumn'
            element_tag: Unique element identifier
            node_i: Start node tag
            node_j: End node tag
            geom_transf_tag: Geometric transformation tag
            integration_type: Integration type ('Lobatto', 'Legendre', etc.)
            section_tag: Section tag
            num_integration_points: Number of integration points
        """
        ...
    
    @overload
    def element(self, element_type: Literal["dispBeamColumn"], element_tag: int, node_i: int, node_j: int, 
                geom_transf_tag: int, integration_type: str, section_tag: int, num_integration_points: int) -> None:
        """Create displacement-based beam-column element
        
        Args:
            element_type: Element type 'dispBeamColumn'
            element_tag: Unique element identifier
            node_i: Start node tag
            node_j: End node tag
            geom_transf_tag: Geometric transformation tag
            integration_type: Integration type ('Lobatto', 'Legendre', etc.)
            section_tag: Section tag
            num_integration_points: Number of integration points
            
        Example:
            ops.element('dispBeamColumn', 3, 1, 2, 1, 'Lobatto', 1, 5)
        """
        ...
    
    @overload
    def element(self, element_type: Literal["nonlinearBeamColumn"], element_tag: int, node_i: int, node_j: int, 
                num_integration_points: int, section_tag: int, geom_transf_tag: int) -> None:
        """Create nonlinear beam-column element with fiber section
        
        Args:
            element_type: Element type 'nonlinearBeamColumn'
            element_tag: Unique element identifier
            node_i: Start node tag
            node_j: End node tag
            num_integration_points: Number of integration points
            section_tag: Section tag
            geom_transf_tag: Geometric transformation tag
            
        Example:
            ops.element('nonlinearBeamColumn', 4, 1, 2, 5, 1, 1)
        """
        ...
    
    @overload
    def element(self, element_type: Literal["beamWithHinges"], element_tag: int, node_i: int, node_j: int, 
                *args: Any) -> None:
        """Create beam with hinges element
        
        Args:
            element_type: Element type 'beamWithHinges'
            element_tag: Unique element identifier
            node_i: Start node tag
            node_j: End node tag
            args: Hinge parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["elasticPipe"], element_tag: int, node_i: int, node_j: int, 
                *args: Any) -> None:
        """Create elastic pipe element
        
        Args:
            element_type: Element type 'elasticPipe'
            element_tag: Unique element identifier
            node_i: Start node tag
            node_j: End node tag
            args: Pipe parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["curvedPipe"], element_tag: int, node_i: int, node_j: int, 
                *args: Any) -> None:
        """Create curved pipe element
        
        Args:
            element_type: Element type 'curvedPipe'
            element_tag: Unique element identifier
            node_i: Start node tag
            node_j: End node tag
            args: Curved pipe parameters
        """
        ...
    
    # ============================================================================
    # Joint Elements
    # ============================================================================
    
    @overload
    def element(self, element_type: Literal["beamColumnJoint"], element_tag: int, *args: Any) -> None:
        """Create beam-column joint element
        
        Args:
            element_type: Element type 'beamColumnJoint'
            element_tag: Unique element identifier
            args: Joint parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["elasticTubularJoint"], element_tag: int, *args: Any) -> None:
        """Create elastic tubular joint element
        
        Args:
            element_type: Element type 'elasticTubularJoint'
            element_tag: Unique element identifier
            args: Tubular joint parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["joint2D"], element_tag: int, *args: Any) -> None:
        """Create joint 2D element
        
        Args:
            element_type: Element type 'joint2D'
            element_tag: Unique element identifier
            args: Joint 2D parameters
        """
        ...
    
    # ============================================================================
    # Link Elements
    # ============================================================================
    
    @overload
    def element(self, element_type: Literal["twoNodeLink"], element_tag: int, node_i: int, node_j: int, 
                *args: Any) -> None:
        """Create two-node link element
        
        Args:
            element_type: Element type 'twoNodeLink'
            element_tag: Unique element identifier
            node_i: Start node tag
            node_j: End node tag
            args: Link parameters
            
        Example:
            ops.element('twoNodeLink', 8, 1, 2, '-mat', 1, '-dir', 1)
        """
        ...
    
    # ============================================================================
    # Bearing Elements
    # ============================================================================
    
    @overload
    def element(self, element_type: Literal["elastomericBearingPlasticity"], element_tag: int, *args: Any) -> None:
        """Create elastomeric bearing (plasticity) element
        
        Args:
            element_type: Element type 'elastomericBearingPlasticity'
            element_tag: Unique element identifier
            args: Bearing parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["elastomericBearingBoucWen"], element_tag: int, *args: Any) -> None:
        """Create elastomeric bearing (Bouc-Wen) element
        
        Args:
            element_type: Element type 'elastomericBearingBoucWen'
            element_tag: Unique element identifier
            args: Bearing parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["flatSliderBearing"], element_tag: int, *args: Any) -> None:
        """Create flat slider bearing element
        
        Args:
            element_type: Element type 'flatSliderBearing'
            element_tag: Unique element identifier
            args: Bearing parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["singleFPBearing"], element_tag: int, *args: Any) -> None:
        """Create single friction pendulum bearing element
        
        Args:
            element_type: Element type 'singleFPBearing'
            element_tag: Unique element identifier
            args: Bearing parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["tripleFPBearing"], element_tag: int, *args: Any) -> None:
        """Create triple friction pendulum bearing element
        
        Args:
            element_type: Element type 'tripleFPBearing'
            element_tag: Unique element identifier
            args: Bearing parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["multipleShearSpring"], element_tag: int, *args: Any) -> None:
        """Create multiple shear spring element
        
        Args:
            element_type: Element type 'multipleShearSpring'
            element_tag: Unique element identifier
            args: Spring parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["kikuchiBearing"], element_tag: int, *args: Any) -> None:
        """Create Kikuchi bearing element
        
        Args:
            element_type: Element type 'kikuchiBearing'
            element_tag: Unique element identifier
            args: Bearing parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["yamamotoBiaxialHDR"], element_tag: int, *args: Any) -> None:
        """Create Yamamoto biaxial HDR element
        
        Args:
            element_type: Element type 'yamamotoBiaxialHDR'
            element_tag: Unique element identifier
            args: HDR parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["elastomericX"], element_tag: int, *args: Any) -> None:
        """Create ElastomericX element
        
        Args:
            element_type: Element type 'elastomericX'
            element_tag: Unique element identifier
            args: Elastomeric parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["leadRubberX"], element_tag: int, *args: Any) -> None:
        """Create LeadRubberX element
        
        Args:
            element_type: Element type 'leadRubberX'
            element_tag: Unique element identifier
            args: Lead rubber parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["HDR"], element_tag: int, *args: Any) -> None:
        """Create HDR element
        
        Args:
            element_type: Element type 'HDR'
            element_tag: Unique element identifier
            args: HDR parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["RJWatsonEQS"], element_tag: int, *args: Any) -> None:
        """Create RJ-Watson EQS bearing element
        
        Args:
            element_type: Element type 'RJWatsonEQS'
            element_tag: Unique element identifier
            args: Bearing parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["FPBearingPTV"], element_tag: int, *args: Any) -> None:
        """Create FPBearingPTV element
        
        Args:
            element_type: Element type 'FPBearingPTV'
            element_tag: Unique element identifier
            args: Bearing parameters
        """
        ...
    
    # ============================================================================
    # Quadrilateral Elements
    # ============================================================================
    
    @overload
    def element(self, element_type: Literal["quad"], element_tag: int, node1: int, node2: int, node3: int, node4: int, 
                thickness: float, material_type: str, material_tag: int, *additional_params: float) -> None:
        """Create quad element
        
        Args:
            element_type: Element type 'quad'
            element_tag: Unique element identifier
            node1, node2, node3, node4: Corner node tags (counterclockwise)
            thickness: Element thickness
            material_type: Material type ('PlaneStrain', 'PlaneStress', etc.)
            material_tag: Material tag
            additional_params: Additional material parameters
            
        Example:
            ops.element('quad', 5, 1, 2, 3, 4, 0.1, 'PlaneStrain', 1)
        """
        ...
    
    @overload
    def element(self, element_type: Literal["shell"], element_tag: int, node1: int, node2: int, node3: int, node4: int, 
                section_tag: int) -> None:
        """Create shell element
        
        Args:
            element_type: Element type 'shell'
            element_tag: Unique element identifier
            node1, node2, node3, node4: Corner node tags
            section_tag: Section tag
        """
        ...
    
    @overload
    def element(self, element_type: Literal["shellMITC4"], element_tag: int, node1: int, node2: int, node3: int, node4: int, 
                section_tag: int) -> None:
        """Create shell MITC4 element
        
        Args:
            element_type: Element type 'shellMITC4'
            element_tag: Unique element identifier
            node1, node2, node3, node4: Corner node tags
            section_tag: Section tag
            
        Example:
            ops.element('shellMITC4', 6, 1, 2, 3, 4, 1)
        """
        ...
    
    @overload
    def element(self, element_type: Literal["shellDKGQ"], element_tag: int, node1: int, node2: int, node3: int, node4: int, 
                section_tag: int) -> None:
        """Create shell DKGQ element
        
        Args:
            element_type: Element type 'shellDKGQ'
            element_tag: Unique element identifier
            node1, node2, node3, node4: Corner node tags
            section_tag: Section tag
        """
        ...
    
    @overload
    def element(self, element_type: Literal["shellDKGT"], element_tag: int, node1: int, node2: int, node3: int, node4: int, 
                section_tag: int) -> None:
        """Create shell DKGT element
        
        Args:
            element_type: Element type 'shellDKGT'
            element_tag: Unique element identifier
            node1, node2, node3, node4: Corner node tags
            section_tag: Section tag
        """
        ...
    
    @overload
    def element(self, element_type: Literal["shellNLDKGQ"], element_tag: int, node1: int, node2: int, node3: int, node4: int, 
                section_tag: int) -> None:
        """Create shell NLDKGQ element
        
        Args:
            element_type: Element type 'shellNLDKGQ'
            element_tag: Unique element identifier
            node1, node2, node3, node4: Corner node tags
            section_tag: Section tag
        """
        ...
    
    @overload
    def element(self, element_type: Literal["shellNLDKGT"], element_tag: int, node1: int, node2: int, node3: int, node4: int, 
                section_tag: int) -> None:
        """Create shell NLDKGT element
        
        Args:
            element_type: Element type 'shellNLDKGT'
            element_tag: Unique element identifier
            node1, node2, node3, node4: Corner node tags
            section_tag: Section tag
        """
        ...
    
    @overload
    def element(self, element_type: Literal["shellNL"], element_tag: int, node1: int, node2: int, node3: int, node4: int, 
                section_tag: int) -> None:
        """Create shell NL element
        
        Args:
            element_type: Element type 'shellNL'
            element_tag: Unique element identifier
            node1, node2, node3, node4: Corner node tags
            section_tag: Section tag
        """
        ...
    
    @overload
    def element(self, element_type: Literal["bbarQuad"], element_tag: int, node1: int, node2: int, node3: int, node4: int, 
                thickness: float, material_type: str, material_tag: int) -> None:
        """Create Bbar plane strain quadrilateral element
        
        Args:
            element_type: Element type 'bbarQuad'
            element_tag: Unique element identifier
            node1, node2, node3, node4: Corner node tags
            thickness: Element thickness
            material_type: Material type
            material_tag: Material tag
        """
        ...
    
    @overload
    def element(self, element_type: Literal["enhancedQuad"], element_tag: int, node1: int, node2: int, node3: int, node4: int, 
                thickness: float, material_type: str, material_tag: int) -> None:
        """Create enhanced strain quadrilateral element
        
        Args:
            element_type: Element type 'enhancedQuad'
            element_tag: Unique element identifier
            node1, node2, node3, node4: Corner node tags
            thickness: Element thickness
            material_type: Material type
            material_tag: Material tag
        """
        ...
    
    @overload
    def element(self, element_type: Literal["SSPquad"], element_tag: int, node1: int, node2: int, node3: int, node4: int, 
                material_tag: int, thickness: float, *args: Any) -> None:
        """Create SSPquad element
        
        Args:
            element_type: Element type 'SSPquad'
            element_tag: Unique element identifier
            node1, node2, node3, node4: Corner node tags
            material_tag: Material tag
            thickness: Element thickness
            args: Additional parameters
        """
        ...
    
    # ============================================================================
    # Triangular Elements
    # ============================================================================
    
    @overload
    def element(self, element_type: Literal["tri31"], element_tag: int, node1: int, node2: int, node3: int, 
                thickness: float, material_type: str, material_tag: int) -> None:
        """Create Tri31 element
        
        Args:
            element_type: Element type 'tri31'
            element_tag: Unique element identifier
            node1, node2, node3: Corner node tags
            thickness: Element thickness
            material_type: Material type
            material_tag: Material tag
        """
        ...
    
    # ============================================================================
    # Brick Elements
    # ============================================================================
    
    @overload
    def element(self, element_type: Literal["brick"], element_tag: int, node1: int, node2: int, node3: int, node4: int,
                node5: int, node6: int, node7: int, node8: int, material_tag: int) -> None:
        """Create standard brick element
        
        Args:
            element_type: Element type 'brick'
            element_tag: Unique element identifier
            node1-node8: Corner node tags
            material_tag: Material tag
        """
        ...
    
    @overload
    def element(self, element_type: Literal["bbarBrick"], element_tag: int, node1: int, node2: int, node3: int, node4: int,
                node5: int, node6: int, node7: int, node8: int, material_tag: int) -> None:
        """Create Bbar brick element
        
        Args:
            element_type: Element type 'bbarBrick'
            element_tag: Unique element identifier
            node1-node8: Corner node tags
            material_tag: Material tag
        """
        ...
    
    @overload
    def element(self, element_type: Literal["twentyNodeBrick"], element_tag: int, *args: Any) -> None:
        """Create twenty node brick element
        
        Args:
            element_type: Element type 'twentyNodeBrick'
            element_tag: Unique element identifier
            args: Node tags and material parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["SSPbrick"], element_tag: int, node1: int, node2: int, node3: int, node4: int,
                node5: int, node6: int, node7: int, node8: int, material_tag: int, *args: Any) -> None:
        """Create SSPbrick element
        
        Args:
            element_type: Element type 'SSPbrick'
            element_tag: Unique element identifier
            node1-node8: Corner node tags
            material_tag: Material tag
            args: Additional parameters
        """
        ...
    
    # ============================================================================
    # Tetrahedron Elements
    # ============================================================================
    
    @overload
    def element(self, element_type: Literal["fourNodeTetrahedron"], element_tag: int, node1: int, node2: int, node3: int, node4: int,
                material_tag: int) -> None:
        """Create four node tetrahedron element
        
        Args:
            element_type: Element type 'fourNodeTetrahedron'
            element_tag: Unique element identifier
            node1, node2, node3, node4: Corner node tags
            material_tag: Material tag
        """
        ...
    
    # ============================================================================
    # UC San Diego u-p Elements (Saturated Soil)
    # ============================================================================
    
    @overload
    def element(self, element_type: Literal["quadUP"], element_tag: int, node1: int, node2: int, node3: int, node4: int,
                material_tag: int, thickness: float, *args: Any) -> None:
        """Create four node quad u-p element
        
        Args:
            element_type: Element type 'quadUP'
            element_tag: Unique element identifier
            node1, node2, node3, node4: Corner node tags
            material_tag: Material tag
            thickness: Element thickness
            args: Additional u-p parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["brickUP"], element_tag: int, node1: int, node2: int, node3: int, node4: int,
                node5: int, node6: int, node7: int, node8: int, material_tag: int, *args: Any) -> None:
        """Create brick u-p element
        
        Args:
            element_type: Element type 'brickUP'
            element_tag: Unique element identifier
            node1-node8: Corner node tags
            material_tag: Material tag
            args: Additional u-p parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["bbarQuadUP"], element_tag: int, node1: int, node2: int, node3: int, node4: int,
                material_tag: int, thickness: float, *args: Any) -> None:
        """Create Bbar quad u-p element
        
        Args:
            element_type: Element type 'bbarQuadUP'
            element_tag: Unique element identifier
            node1, node2, node3, node4: Corner node tags
            material_tag: Material tag
            thickness: Element thickness
            args: Additional u-p parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["bbarBrickUP"], element_tag: int, node1: int, node2: int, node3: int, node4: int,
                node5: int, node6: int, node7: int, node8: int, material_tag: int, *args: Any) -> None:
        """Create Bbar brick u-p element
        
        Args:
            element_type: Element type 'bbarBrickUP'
            element_tag: Unique element identifier
            node1-node8: Corner node tags
            material_tag: Material tag
            args: Additional u-p parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["nineFourNodeQuadUP"], element_tag: int, *args: Any) -> None:
        """Create nine four node quad u-p element
        
        Args:
            element_type: Element type 'nineFourNodeQuadUP'
            element_tag: Unique element identifier
            args: Node tags and material parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["twentyEightNodeBrickUP"], element_tag: int, *args: Any) -> None:
        """Create twenty eight node brick u-p element
        
        Args:
            element_type: Element type 'twentyEightNodeBrickUP'
            element_tag: Unique element identifier
            args: Node tags and material parameters
        """
        ...
    
    # ============================================================================
    # Other u-p Elements
    # ============================================================================
    
    @overload
    def element(self, element_type: Literal["SSPquadUP"], element_tag: int, node1: int, node2: int, node3: int, node4: int,
                material_tag: int, thickness: float, *args: Any) -> None:
        """Create SSPquadUP element
        
        Args:
            element_type: Element type 'SSPquadUP'
            element_tag: Unique element identifier
            node1, node2, node3, node4: Corner node tags
            material_tag: Material tag
            thickness: Element thickness
            args: Additional u-p parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["SSPbrickUP"], element_tag: int, node1: int, node2: int, node3: int, node4: int,
                node5: int, node6: int, node7: int, node8: int, material_tag: int, *args: Any) -> None:
        """Create SSPbrickUP element
        
        Args:
            element_type: Element type 'SSPbrickUP'
            element_tag: Unique element identifier
            node1-node8: Corner node tags
            material_tag: Material tag
            args: Additional u-p parameters
        """
        ...
    
    # ============================================================================
    # Contact Elements
    # ============================================================================
    
    @overload
    def element(self, element_type: Literal["simpleContact2D"], element_tag: int, *args: Any) -> None:
        """Create simple contact 2D element
        
        Args:
            element_type: Element type 'simpleContact2D'
            element_tag: Unique element identifier
            args: Contact parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["simpleContact3D"], element_tag: int, *args: Any) -> None:
        """Create simple contact 3D element
        
        Args:
            element_type: Element type 'simpleContact3D'
            element_tag: Unique element identifier
            args: Contact parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["beamContact2D"], element_tag: int, *args: Any) -> None:
        """Create beam contact 2D element
        
        Args:
            element_type: Element type 'beamContact2D'
            element_tag: Unique element identifier
            args: Contact parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["beamContact3D"], element_tag: int, *args: Any) -> None:
        """Create beam contact 3D element
        
        Args:
            element_type: Element type 'beamContact3D'
            element_tag: Unique element identifier
            args: Contact parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["beamEndContact3D"], element_tag: int, *args: Any) -> None:
        """Create beam end contact 3D element
        
        Args:
            element_type: Element type 'beamEndContact3D'
            element_tag: Unique element identifier
            args: Contact parameters
        """
        ...
    
    # ============================================================================
    # Cable Elements
    # ============================================================================
    
    @overload
    def element(self, element_type: Literal["catenaryCable"], element_tag: int, *args: Any) -> None:
        """Create catenary cable element
        
        Args:
            element_type: Element type 'catenaryCable'
            element_tag: Unique element identifier
            args: Cable parameters
        """
        ...
    
    # ============================================================================
    # PFEM Elements
    # ============================================================================
    
    @overload
    def element(self, element_type: Literal["PFEMElementBubble"], element_tag: int, *args: Any) -> None:
        """Create PFEM element bubble
        
        Args:
            element_type: Element type 'PFEMElementBubble'
            element_tag: Unique element identifier
            args: PFEM parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["PFEMElementCompressible"], element_tag: int, *args: Any) -> None:
        """Create PFEM element compressible
        
        Args:
            element_type: Element type 'PFEMElementCompressible'
            element_tag: Unique element identifier
            args: PFEM parameters
        """
        ...
    
    # ============================================================================
    # Misc Elements
    # ============================================================================
    
    @overload
    def element(self, element_type: Literal["surfaceLoad"], element_tag: int, *args: Any) -> None:
        """Create surface load element
        
        Args:
            element_type: Element type 'surfaceLoad'
            element_tag: Unique element identifier
            args: Surface load parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["VS3D4"], element_tag: int, *args: Any) -> None:
        """Create VS3D4 element
        
        Args:
            element_type: Element type 'VS3D4'
            element_tag: Unique element identifier
            args: VS3D4 parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["AC3D8"], element_tag: int, *args: Any) -> None:
        """Create AC3D8 element
        
        Args:
            element_type: Element type 'AC3D8'
            element_tag: Unique element identifier
            args: AC3D8 parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["ASI3D8"], element_tag: int, *args: Any) -> None:
        """Create ASI3D8 element
        
        Args:
            element_type: Element type 'ASI3D8'
            element_tag: Unique element identifier
            args: ASI3D8 parameters
        """
        ...
    
    @overload
    def element(self, element_type: Literal["AV3D4"], element_tag: int, node1: int, node2: int, node3: int, node4: int,
                node5: int, node6: int, node7: int, node8: int, material_tag: int) -> None:
        """Create AV3D4 element
        
        Args:
            element_type: Element type 'AV3D4'
            element_tag: Unique element identifier
            node1-node8: Corner node tags
            material_tag: Material tag
            
        Example:
            ops.element('AV3D4', 1, 1, 2, 3, 4, 5, 6, 7, 8, 1)
        """
        ...
    
    @overload
    def element(self, element_type: Literal["masonPan12"], element_tag: int, *args: Any) -> None:
        """Create 12 node masonry panel element
        
        Args:
            element_type: Element type 'masonPan12'
            element_tag: Unique element identifier
            args: Masonry panel parameters
        """
        ...
    
    # ============================================================================
    # Generic fallback for any element type
    # ============================================================================
    
    @overload
    def element(self, element_type: str, element_tag: int, *args: Any) -> None:
        """Create element (generic fallback)
        
        Args:
            element_type: Element type
            element_tag: Unique element identifier
            args: Element parameters
            
        Example:
            ops.element('someOtherElement', 1, 1, 2, ...)
        """
        ... 