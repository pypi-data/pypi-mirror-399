from typing import Any, Optional, Dict, List

from ._BaseHandler import BaseHandler


class BeamIntegrationManager(BaseHandler):
    """Manager for beamIntegration commands in OpenSeesPy
    
    Handles beamIntegration command which creates BeamIntegration objects
    for force-based beam-column elements.
    """
    
    def __init__(self):
        self.integrations = {}  # tag -> integration_info
        
    @property
    def _COMMAND_RULES(self) -> dict[str, dict[str, Any]]:
        """Define parsing rules for beamIntegration commands"""
        return {
            # beamIntegration(type, tag, *args)
            "beamIntegration": {
                "positional": ["integration_type", "tag", "args*"],
            },
        }
    
    def handles(self) -> List[str]:
        """Return list of commands this manager handles"""
        return ["beamIntegration"]
    
    def handle(self, func_name: str, arg_map: dict[str, Any]):
        """Handle beamIntegration commands"""
        if func_name == "beamIntegration":
            args, kwargs = arg_map.get("args"), arg_map.get("kwargs")
            parsed_args = self._parse("beamIntegration", *args, **kwargs)
            self._handle_beam_integration(parsed_args)
    
    def _handle_beam_integration(self, arg_map: dict[str, Any]):
        """Handle beamIntegration command
        
        Args:
            arg_map: Parsed arguments from _parse method
        """
        integration_type = arg_map.get("integration_type")
        tag = arg_map.get("tag")
        
        if not integration_type or tag is None:
            return
            
        args = arg_map.get("args", [])
        
        integration_info = {
            "type": integration_type,
            "tag": tag,
            "args": args,
        }
        
        # Parse specific integration types and their parameters
        if integration_type == "Lobatto":
            # Lobatto(tag, secTag, N)
            if len(args) >= 2:
                integration_info["sec_tag"] = args[0]
                integration_info["N"] = args[1]
        elif integration_type == "Legendre":
            # Legendre(tag, secTag, N)
            if len(args) >= 2:
                integration_info["sec_tag"] = args[0]
                integration_info["N"] = args[1]
        elif integration_type == "NewtonCotes":
            # NewtonCotes(tag, secTag, N)
            if len(args) >= 2:
                integration_info["sec_tag"] = args[0]
                integration_info["N"] = args[1]
        elif integration_type == "Radau":
            # Radau(tag, secTag, N)
            if len(args) >= 2:
                integration_info["sec_tag"] = args[0]
                integration_info["N"] = args[1]
        elif integration_type == "Trapezoidal":
            # Trapezoidal(tag, secTag, N)
            if len(args) >= 2:
                integration_info["sec_tag"] = args[0]
                integration_info["N"] = args[1]
        elif integration_type == "CompositeSimpson":
            # CompositeSimpson(tag, secTag, N)
            if len(args) >= 2:
                integration_info["sec_tag"] = args[0]
                integration_info["N"] = args[1]
        elif integration_type == "UserDefined":
            # UserDefined(tag, *secTags, *locs, *wts)
            # This type has variable arguments structure
            integration_info["sec_tags"] = []
            integration_info["locations"] = []
            integration_info["weights"] = []
            # Parse would depend on specific implementation
        elif integration_type == "FixedLocation":
            # FixedLocation(tag, N, *secTags, *locs)
            if len(args) >= 1:
                integration_info["N"] = args[0]
                if len(args) >= 2:
                    # Remaining args are section tags and locations
                    integration_info["sec_tags"] = args[1::2] if len(args) > 2 else []
                    integration_info["locations"] = args[2::2] if len(args) > 3 else []
        elif integration_type == "LowOrder":
            # LowOrder(tag, N, *secTags)
            if len(args) >= 1:
                integration_info["N"] = args[0]
                integration_info["sec_tags"] = args[1:] if len(args) > 1 else []
        elif integration_type == "MidDistance":
            # MidDistance(tag, N, *secTags)
            if len(args) >= 1:
                integration_info["N"] = args[0]
                integration_info["sec_tags"] = args[1:] if len(args) > 1 else []
        elif integration_type == "UserHinges":
            # UserHinges(tag, *secEtags, *lpI, *phis, *lnI, *phiN, *secCtags, *lpJ, *phiJ)
            # Complex structure, store as args for now
            pass
        
        # Store integration information
        self.integrations[tag] = integration_info
    
    def get_integration(self, tag: int) -> Optional[Dict[str, Any]]:
        """Get beam integration information by tag
        
        Args:
            tag: Integration tag
            
        Returns:
            Integration information dictionary or None if not found
        """
        return self.integrations.get(tag)
    
    def get_integrations_by_type(self, integration_type: str) -> List[Dict[str, Any]]:
        """Get all integrations of a specific type
        
        Args:
            integration_type: Integration type (e.g., 'Lobatto', 'Legendre', etc.)
            
        Returns:
            List of integration information dictionaries
        """
        result = []
        for integration_info in self.integrations.values():
            if integration_info.get("type") == integration_type:
                result.append(integration_info)
        return result
    
    def get_integrations_using_section(self, sec_tag: int) -> List[Dict[str, Any]]:
        """Get all integrations using a specific section
        
        Args:
            sec_tag: Section tag
            
        Returns:
            List of integration information dictionaries
        """
        result = []
        for integration_info in self.integrations.values():
            # Check single section tag
            if integration_info.get("sec_tag") == sec_tag:
                result.append(integration_info)
            # Check multiple section tags
            elif sec_tag in integration_info.get("sec_tags", []):
                result.append(integration_info)
        return result
    
    def get_integration_tags(self) -> List[int]:
        """Get all integration tags
        
        Returns:
            List of integration tags
        """
        return list(self.integrations.keys())
    
    def clear(self):
        """Clear all beam integration data"""
        self.integrations.clear() 