from typing import Any, Dict, List, Optional, Set, Union
import math

from ._Selector import Selector, SelectType, NodeSelectItem, NodeSelectComp

class NodeSelector(Selector):
    """Node selector implementing functionality similar to ANSYS NSEL command"""
    
    def _select_new(self,
                   item: NodeSelectItem = None,
                   comp: NodeSelectComp = None,
                   vmin: Union[int, float, str] = None,
                   vmax: Union[int, float, str] = None,
                   vinc: int = 1,
                   kabs: int = 0,
                   **kwargs) -> Set[int]:
        """
        Create new node selection based on criteria
        
        Args:
            item: Selection item type
            comp: Component for coordinate selection
            vmin: Minimum value
            vmax: Maximum value
            vinc: Value increment
            kabs: Absolute value key (0=Check sign, 1=Use absolute value)
            **kwargs: Additional selection criteria
            
        Returns:
            Set of selected node IDs
        """
        if not item:
            return set()
        
        if not isinstance(item, NodeSelectItem):
            try:
                item = NodeSelectItem(item)
            except ValueError:
                print(f"Invalid NodeSelectItem: {item}")
                return set()
            
        if comp and not isinstance(comp, NodeSelectComp):
            try:
                comp = NodeSelectComp(comp)
            except ValueError:
                print(f"Invalid NodeSelectComp: {comp}")
                return set()
            
        vmax = vmax if vmax is not None else vmin
        selected = set()
        
        # Select by node ID
        if item == NodeSelectItem.TAG:
            if isinstance(vmin, (int, float)):
                tol = kwargs.get('tol', 1e-6)
                selected = {nid for nid in self._items.keys() 
                          if vmin - tol <= nid <= vmax + tol and (nid - vmin) % vinc == 0}
                          
        # Select by coordinates
        elif item == NodeSelectItem.COORD:
            if not isinstance(comp, NodeSelectComp):
                return set()
                
            idx = {'X': 0, 'Y': 1, 'Z': 2}[comp.value]
            for nid, node in self._items.items():
                coords = node.get('coords', [])
                if len(coords) > idx:
                    val = abs(coords[idx]) if kabs else coords[idx]
                    if vmin <= val <= vmax:
                        selected.add(nid)
                        
        # Select by number of DOFs
        elif item == NodeSelectItem.NDF:
            for nid, node in self._items.items():
                ndf = node.get('ndf', 0)
                if vmin <= ndf <= vmax:
                    selected.add(nid)
                    
        # Select by radial distance
        elif item == NodeSelectItem.RADIUS:
            for nid, node in self._items.items():
                coords = node.get('coords', [])
                if len(coords) >= 2:
                    radius = math.sqrt(sum(c*c for c in coords[:2]))
                    if vmin <= radius <= vmax:
                        selected.add(nid)
                            
        return selected
        
    def get_coords(self) -> List[List[float]]:
        """Get coordinates of selected nodes"""
        return [node.get('coords', []) for node in self]
        
    def get_masses(self) -> List[List[float]]:
        """Get masses of selected nodes"""
        return [node.get('mass', []) for node in self]
        
    def get_displacements(self) -> List[List[float]]:
        """Get displacements of selected nodes"""
        return [node.get('disp', []) for node in self]
        
    def get_velocities(self) -> List[List[float]]:
        """Get velocities of selected nodes"""
        return [node.get('vel', []) for node in self]
        
    def get_accelerations(self) -> List[List[float]]:
        """Get accelerations of selected nodes"""
        return [node.get('accel', []) for node in self]
        
    def get_connected_elements(self) -> List[int]:
        """Get elements connected to selected nodes"""
        if not self._element_manager:
            return []
            
        result = []
        for node_id in self._current_selection:
            elements = self._element_manager.get_elements_by_nodes(node_id)
            result.extend(elements)
        return list(set(result))
        
    def by_coords(self, x: Optional[float] = None, y: Optional[float] = None, z: Optional[float] = None) -> 'NodeSelector':
        """Filter nodes by coordinates"""
        def coord_filter(node):
            coords = node.get('coords', [])
            if len(coords) < 1:
                return False
            if x is not None and (len(coords) < 1 or abs(coords[0] - x) > 1e-6):
                return False
            if y is not None and (len(coords) < 2 or abs(coords[1] - y) > 1e-6):
                return False
            if z is not None and (len(coords) < 3 or abs(coords[2] - z) > 1e-6):
                return False
            return True
        return self.filter(coord_filter) 