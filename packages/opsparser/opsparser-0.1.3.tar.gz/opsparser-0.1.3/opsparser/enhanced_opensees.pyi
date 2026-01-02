from typing import overload, Literal, Optional, Any, Union, List, Dict

# Import all specialized command classes
from ._ide_support.basic import BasicCommands
from ._ide_support.elements import ElementCommands  
from ._ide_support.uniaxialmaterials import uniaxialMaterialCommands
from ._ide_support.ndmaterials import nDMaterialCommands
from ._ide_support.geometry import GeometryCommands
from ._ide_support.loads import LoadCommands
from ._ide_support.analysis import AnalysisCommands
from ._ide_support.utilities import UtilityCommands

class EnhancedOpenSees(
    BasicCommands,
    ElementCommands, 
    uniaxialMaterialCommands,
    nDMaterialCommands,
    GeometryCommands,
    LoadCommands,
    AnalysisCommands,
    UtilityCommands
):
    """Enhanced OpenSees interface with intelligent type hints
    
    This class inherits type annotations from specialized command classes:
    - BasicCommands: model, node, mass, fix, equalDOF, rigidDiaphragm
    - ElementCommands: element (with smart parameter hints for different element types)
    - uniaxialMaterialCommands: uniaxialMaterial (with material-specific parameters)
    - nDMaterialCommands: nDMaterial (with material-specific parameters)
    - GeometryCommands: geomTransf (with transformation-specific parameters)
    - LoadCommands: timeSeries, pattern, load, eleLoad
    - AnalysisCommands: constraints, numberer, system, test, algorithm, integrator, analysis, analyze, eigen
    - UtilityCommands: wipe, remove, get*, node*, ele*, recorder, record, print*
    """
    
    def __init__(self, original_ops: Any, enable_parsing: bool = False, debug: bool = False): ...

    # Generic fallback for any other function
    def __getattr__(self, name: str) -> Any: ...

def enhance_opensees(original_ops: Any, enable_parsing: bool = False, debug: bool = False) -> EnhancedOpenSees:
    """
    Creates an enhanced OpenSees interface with perfect IDE type hinting.
    
    Args:
        original_ops: The original opensees module (e.g., openseespy.opensees).
        enable_parsing: Whether to enable command parsing and data collection (default is False, providing only IDE support).
        debug: Whether to enable debug output (default is False).
    
    Returns:
        An enhanced OpenSees object with smart type hints.
    
    Example:
        # IDE support only mode (recommended, zero performance overhead)
        import openseespy.opensees as ops
        from opsparser.enhanced_opensees import enhance_opensees
        
        ops = enhance_opensees(ops)
        ops.element('truss', 1, 1, 2, area=0.1, material_tag=1)  # Perfect IDE hints
        
        # Full feature mode (IDE support + parsing + data collection)
        ops = enhance_opensees(ops, enable_parsing=True)
    """
    ... 