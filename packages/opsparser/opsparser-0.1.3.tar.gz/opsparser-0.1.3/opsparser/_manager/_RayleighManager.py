from typing import Any, Optional, Dict, List

from ._BaseHandler import BaseHandler


class RayleighManager(BaseHandler):
    """Manager for Rayleigh damping commands in OpenSeesPy
    
    Handles rayleigh command which assigns Rayleigh damping to all 
    previously-defined elements and nodes.
    """
    
    def __init__(self):
        self.rayleigh_params = None  # Current Rayleigh damping parameters
        self.history = []  # History of Rayleigh damping assignments
        
    @property
    def _COMMAND_RULES(self) -> dict[str, dict[str, Any]]:
        """Define parsing rules for rayleigh commands"""
        return {
            # rayleigh(alphaM, betaK, betaKinit, betaKcomm)
            "rayleigh": {
                "positional": ["alphaM", "betaK", "betaKinit", "betaKcomm"],
            },
        }
    
    def handles(self) -> List[str]:
        """Return list of commands this manager handles"""
        return ["rayleigh"]
    
    def handle(self, func_name: str, arg_map: dict[str, Any]):
        """Handle rayleigh commands"""
        if func_name == "rayleigh":
            args, kwargs = arg_map.get("args"), arg_map.get("kwargs")
            parsed_args = self._parse("rayleigh", *args, **kwargs)
            self._handle_rayleigh(parsed_args)
    
    def _handle_rayleigh(self, arg_map: dict[str, Any]):
        """Handle rayleigh command
        
        Args:
            arg_map: Parsed arguments from _parse method
        """
        alphaM = arg_map.get("alphaM")
        betaK = arg_map.get("betaK")
        betaKinit = arg_map.get("betaKinit")
        betaKcomm = arg_map.get("betaKcomm")
        
        if alphaM is None or betaK is None or betaKinit is None or betaKcomm is None:
            return
            
        # Store current Rayleigh damping parameters
        self.rayleigh_params = {
            "alphaM": alphaM,
            "betaK": betaK,
            "betaKinit": betaKinit,
            "betaKcomm": betaKcomm,
        }
        
        # Add to history
        self.history.append(self.rayleigh_params.copy())
    
    def get_current_rayleigh(self) -> Optional[Dict[str, float]]:
        """Get current Rayleigh damping parameters
        
        Returns:
            Dictionary with Rayleigh parameters or None if not set
        """
        return self.rayleigh_params.copy() if self.rayleigh_params else None
    
    def get_rayleigh_history(self) -> List[Dict[str, float]]:
        """Get history of Rayleigh damping assignments
        
        Returns:
            List of Rayleigh parameter dictionaries
        """
        return self.history.copy()
    
    def has_rayleigh_damping(self) -> bool:
        """Check if Rayleigh damping is currently set
        
        Returns:
            True if Rayleigh damping parameters are set, False otherwise
        """
        return self.rayleigh_params is not None
    
    def clear(self):
        """Clear all Rayleigh damping data"""
        self.rayleigh_params = None
        self.history.clear() 