"""荷载命令类型注解"""

from typing import overload, Literal, Optional, Any

class LoadCommands:
    """荷载命令的类型注解"""
    
    # Time series
    @overload
    def timeSeries(self, series_type: Literal["Linear"], series_tag: int, start_time: float = 0.0, factor: float = 1.0) -> None:
        """Define linear time series
        
        Args:
            series_type: Time series type 'Linear'
            series_tag: Unique time series identifier
            start_time: Start time (default 0.0)
            factor: Factor (default 1.0)
            
        Example:
            ops.timeSeries('Linear', 1)
            ops.timeSeries('Linear', 2, 0.0, 2.0)
        """
        ...
    
    @overload
    def timeSeries(self, series_type: Literal["Constant"], series_tag: int, start_time: float = 0.0, factor: float = 1.0) -> None:
        """Define constant time series
        
        Args:
            series_type: Time series type 'Constant'
            series_tag: Unique time series identifier
            start_time: Start time (default 0.0)
            factor: Factor (default 1.0)
            
        Example:
            ops.timeSeries('Constant', 1)
            ops.timeSeries('Constant', 2, 0.0, 1.5)
        """
        ...
    
    @overload
    def timeSeries(self, series_type: Literal["Path"], series_tag: int, file_path: str, dt: Optional[float] = None, factor: float = 1.0) -> None:
        """Define path time series from file
        
        Args:
            series_type: Time series type 'Path'
            series_tag: Unique time series identifier
            file_path: Path to data file
            dt: Time step (optional)
            factor: Factor (default 1.0)
            
        Example:
            ops.timeSeries('Path', 1, 'ground_motion.txt', 0.01)
        """
        ...
    
    @overload
    def timeSeries(self, series_type: str, series_tag: int, *args: Any) -> None:
        """Define time series (generic fallback)
        
        Args:
            series_type: Time series type
            series_tag: Unique time series identifier
            args: Time series parameters
            
        Example:
            ops.timeSeries('SomeOtherSeries', 1, ...)
        """
        ...
    
    # Load patterns
    def pattern(self, pattern_type: Literal["Plain"], pattern_tag: int, time_series_tag: int) -> None:
        """Define load pattern
        
        Args:
            pattern_type: Pattern type 'Plain'
            pattern_tag: Unique pattern identifier
            time_series_tag: Associated time series tag
            
        Example:
            ops.pattern('Plain', 1, 1)
        """
        ...
    
    # Nodal loads
    def load(self, node_tag: int, *load_values: float) -> None:
        """Apply load to node
        
        Args:
            node_tag: Node tag
            load_values: Load values for each DOF
            
        Examples:
            ops.load(1, 100.0, 0.0, 0.0)        # 2D: Fx, Fy, Mz
            ops.load(2, 0.0, -500.0, 0.0, 0.0, 0.0, 1000.0)  # 3D: Fx, Fy, Fz, Mx, My, Mz
        """
        ...
    
    # Element loads
    def eleLoad(self, load_type: Literal["beamUniform"], element_tag: int, w_transverse: float, w_axial: float = 0.0) -> None:
        """Apply uniform load to beam element
        
        Args:
            load_type: Load type 'beamUniform'
            element_tag: Element tag
            w_transverse: Transverse distributed load
            w_axial: Axial distributed load (default 0.0)
            
        Example:
            ops.eleLoad('-ele', 1, '-type', 'beamUniform', -10.0, 0.0)
        """
        ...
    
