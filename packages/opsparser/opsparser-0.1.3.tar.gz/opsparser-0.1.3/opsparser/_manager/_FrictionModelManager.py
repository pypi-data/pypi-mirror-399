from typing import Any, Optional, Dict, List

from ._BaseHandler import BaseHandler


class FrictionModelManager(BaseHandler):
    """Manager for frictionModel commands in OpenSeesPy
    
    Handles frictionModel command which creates FrictionModel objects
    for friction-based bearings and isolators.
    """
    
    def __init__(self):
        self.friction_models = {}  # tag -> friction_model_info
        
    @property
    def _COMMAND_RULES(self) -> dict[str, dict[str, Any]]:
        """Define parsing rules for frictionModel commands"""
        return {
            # frictionModel(type, tag, *args)
            "frictionModel": {
                "positional": ["model_type", "tag", "args*"],
            },
        }
    
    def handles(self) -> List[str]:
        """Return list of commands this manager handles"""
        return ["frictionModel"]
    
    def handle(self, func_name: str, arg_map: dict[str, Any]):
        """Handle frictionModel commands"""
        if func_name == "frictionModel":
            args, kwargs = arg_map.get("args"), arg_map.get("kwargs")
            parsed_args = self._parse("frictionModel", *args, **kwargs)
            self._handle_friction_model(parsed_args)
    
    def _handle_friction_model(self, arg_map: dict[str, Any]):
        """Handle frictionModel command
        
        Args:
            arg_map: Parsed arguments from _parse method
        """
        model_type = arg_map.get("model_type")
        tag = arg_map.get("tag")
        
        if not model_type or tag is None:
            return
            
        args = arg_map.get("args", [])
        
        friction_model_info = {
            "type": model_type,
            "tag": tag,
            "args": args,
        }
        
        # Parse specific friction model types and their parameters
        if model_type == "Coulomb":
            # Coulomb(tag, mu)
            if len(args) >= 1:
                friction_model_info["mu"] = args[0]
        elif model_type == "VelDependent":
            # VelDependent(tag, muSlow, muFast, transRate)
            if len(args) >= 3:
                friction_model_info["mu_slow"] = args[0]
                friction_model_info["mu_fast"] = args[1]
                friction_model_info["trans_rate"] = args[2]
        elif model_type == "VelPressureDep":
            # VelPressureDep(tag, muSlow, muFast0, A, deltaMu, alpha, transRate)
            if len(args) >= 6:
                friction_model_info["mu_slow"] = args[0]
                friction_model_info["mu_fast0"] = args[1]
                friction_model_info["A"] = args[2]
                friction_model_info["delta_mu"] = args[3]
                friction_model_info["alpha"] = args[4]
                friction_model_info["trans_rate"] = args[5]
        elif model_type == "VelNormalFrcDep":
            # VelNormalFrcDep(tag, aSlow, nSlow, aFast, nFast, alpha0, alpha1, alpha2, maxMuFac)
            if len(args) >= 8:
                friction_model_info["a_slow"] = args[0]
                friction_model_info["n_slow"] = args[1]
                friction_model_info["a_fast"] = args[2]
                friction_model_info["n_fast"] = args[3]
                friction_model_info["alpha0"] = args[4]
                friction_model_info["alpha1"] = args[5]
                friction_model_info["alpha2"] = args[6]
                friction_model_info["max_mu_fac"] = args[7]
        elif model_type == "VelDepMultiLinear":
            # VelDepMultiLinear(tag, '-vel', *velocities, '-frn', *frictionCoeffs)
            # Parse velocities and friction coefficients
            vel_idx = args.index('-vel') if '-vel' in args else -1
            frn_idx = args.index('-frn') if '-frn' in args else -1
            
            if vel_idx >= 0 and frn_idx >= 0 and frn_idx > vel_idx:
                friction_model_info["velocities"] = args[vel_idx + 1:frn_idx]
                friction_model_info["friction_coeffs"] = args[frn_idx + 1:]
        
        # Store friction model information
        self.friction_models[tag] = friction_model_info
    
    def get_friction_model(self, tag: int) -> Optional[Dict[str, Any]]:
        """Get friction model information by tag
        
        Args:
            tag: Friction model tag
            
        Returns:
            Friction model information dictionary or None if not found
        """
        return self.friction_models.get(tag)
    
    def get_friction_models_by_type(self, model_type: str) -> List[Dict[str, Any]]:
        """Get all friction models of a specific type
        
        Args:
            model_type: Friction model type (e.g., 'Coulomb', 'VelDependent', etc.)
            
        Returns:
            List of friction model information dictionaries
        """
        result = []
        for friction_model_info in self.friction_models.values():
            if friction_model_info.get("type") == model_type:
                result.append(friction_model_info)
        return result
    
    def get_friction_model_tags(self) -> List[int]:
        """Get all friction model tags
        
        Returns:
            List of friction model tags
        """
        return list(self.friction_models.keys())
    
    def clear(self):
        """Clear all friction model data"""
        self.friction_models.clear() 