#!/usr/bin/env python3
"""
Enhanced OpenSees with Perfect IDE Support + Hook Functionality
Unified solution that combines IDE support with powerful parsing capabilities
"""

from typing import Any, Callable
import openseespy.opensees as ops
import inspect

class EnhancedOpenSees:
    """Enhanced OpenSees wrapper with complete IDE support + optional parsing"""
    
    def __init__(self, original_ops: Any, debug: bool = False):
        """Initialize with original openseespy.opensees module
        
        Args:
            original_ops: Original openseespy.opensees module
            debug: Enable debug output for parsing
        """
        self._ops = original_ops
        self._debug = debug  # 确保在访问之前设置这个属性
        
        # Copy all other attributes from original ops (non-callable)
        for attr_name in dir(original_ops):
            if not attr_name.startswith('_') and not hasattr(self, attr_name):
                attr_value = getattr(original_ops, attr_name)
                if not callable(attr_value):
                    setattr(self, attr_name, attr_value)

    def _create_wrapper(self, func_name: str, original_func: Callable[..., Any]) -> Callable[..., Any]:
        """Create a wrapper function that converts kwargs to positional args"""
        
        def wrapper(*args, **kwargs):
            # 使用 getattr 避免无限递归
            debug = getattr(self, '_debug', False)
            if debug:
                print(f"🔧 Calling {func_name}: args={args}, kwargs={kwargs}")
            
            # Convert all arguments to positional arguments
            all_args = list(args)
            
            # Add keyword arguments as positional arguments in the order they were provided
            for value in kwargs.values():
                all_args.append(value)
            
            if debug:
                print(f"🔄 Converted positional arguments: {all_args}")
            
            # Call the original function with only positional arguments
            result = original_func(*all_args)
            
            return result
        
        return wrapper

    def __getattr__(self, name: str) -> Any:
        """Forwards all attribute access to the original ops module with argument conversion"""
        # 避免无限递归：如果访问的是内部属性，直接抛出 AttributeError
        if name.startswith('_'):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        
        original_attr = getattr(self._ops, name)
        
        # If it's a callable, wrap it with argument conversion
        if callable(original_attr):
            return self._create_wrapper(name, original_attr)
        else:
            return original_attr


def enhance_opensees(original_ops: Any, debug: bool = False) -> EnhancedOpenSees:
    """Create an enhanced OpenSees object with IDE support and optional parsing
    
    Args:
        original_ops: Original openseespy.opensees module
        debug: Enable debug output for parsing operations
        
    Returns:
        EnhancedOpenSees: Enhanced object with complete functionality
        
    Examples:
        # IDE support only (lightweight)
        ops = enhance_opensees(original_ops)
        
        # With debug output
        ops = enhance_opensees(original_ops, debug=True)
    """
    return EnhancedOpenSees(original_ops, debug)


# For convenient import
__all__ = ['enhance_opensees', 'EnhancedOpenSees']