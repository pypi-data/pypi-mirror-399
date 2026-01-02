from typing import Any, Dict, List, Optional, Set, Union
from ._Selector import Selector, SelectType, ElementSelectItem, ElementSelectComp
import math

class ElementSelector(Selector):
    """Element selector implementing functionality similar to ANSYS ESEL command"""
    
    def _select_new(self,
                   item: ElementSelectItem = None,
                   comp: ElementSelectComp = None,
                   vmin: Union[int, float, str] = None,
                   vmax: Union[int, float, str] = None,
                   vinc: int = 1,
                   kabs: int = 0,
                   **kwargs) -> Set[int]:
        """
        Create new element selection based on criteria
        
        Args:
            item: Selection item type
            comp: Component for selection
            vmin: Minimum value
            vmax: Maximum value
            vinc: Value increment
            kabs: Absolute value key (0=Check sign, 1=Use absolute value)
            **kwargs: Additional selection criteria
            
        Returns:
            Set of selected element IDs
        """
        if not item:
            return set()
            
        vmax = vmax if vmax is not None else vmin
        selected = set()
        
        # Select by element ID
        if item == ElementSelectItem.TAG.value:
            if isinstance(vmin, (int, float)):
                selected = {eid for eid in self._items.keys() 
                          if vmin <= eid <= vmax and (eid - vmin) % vinc == 0}
                          
        # Select by element type
        elif item == ElementSelectItem.TYPE.value:
            for eid, elem in self._items.items():
                if elem.get('eleType', '') == vmin:
                    selected.add(eid)
                    
        # Select by material ID
        elif item == ElementSelectItem.MAT.value:
            for eid, elem in self._items.items():
                if vmin <= elem.get('matTag', 0) <= vmax:
                    selected.add(eid)
                    

                    
        # Select by section number
        elif item == ElementSelectItem.SECTION.value:
            for eid, elem in self._items.items():
                if vmin <= elem.get('secTag', 0) <= vmax:
                    selected.add(eid)
                    
        # Select by node
        elif item == ElementSelectItem.NODE.value:
            if not self._node_manager:
                return set()
                
            # 获取选中的节点ID
            selected_node_ids = set()
            node_selector = self._node_manager.sel().sel(type=SelectType.NEW, item='Tag', vmin=vmin, vmax=vmax)
            for node_id, _ in node_selector:
                selected_node_ids.add(node_id)
                
            for eid, elem in self._items.items():
                if any(nid in selected_node_ids for nid in elem.get('eleNodes', [])):
                    selected.add(eid)
                    
                    
        return selected
        
    def get_types(self) -> List[int]:
        """Get types of selected elements"""
        return [elem.get('eleType', '') for elem in self]
        
    def get_materials(self) -> List[int]:
        """Get materials of selected elements"""
        return [elem.get('matTag', 0) for elem in self]
        
    def get_nodes(self) -> List[List[int]]:
        """Get nodes of selected elements"""
        return [elem.get('eleNodes', []) for elem in self]
        
    def get_sections(self) -> List[int]:
        """Get sections of selected elements"""
        return [elem.get('secTag', 0) for elem in self]
        
    def get_coordinate_systems(self) -> List[int]:
        """Get coordinate systems of selected elements"""
        return [elem.get('esys', 0) for elem in self]
        
    def get_real_constants(self) -> List[int]:
        """Get real constants of selected elements"""
        return [elem.get('real', 0) for elem in self]
        
    def get_layers(self) -> List[int]:
        """Get layers of selected elements"""
        return [elem.get('layer', 0) for elem in self]
        
    def get_centroids(self) -> List[List[float]]:
        """Get centroids of selected elements"""
        if not self._node_manager:
            return []
            
        result = []
        for elem in self:
            nodes = elem.get('eleNodes', [])
            if not nodes:
                result.append([])
                continue
                
            coords = [self._node_manager.get_node_coords(nid) for nid in nodes]
            if not all(coords):
                result.append([])
                continue
                
            centroid = [sum(c[i] for c in coords) / len(coords) for i in range(len(coords[0]))]
            result.append(centroid)
            
        return result
        
    def get_straightness(self) -> List[float]:
        """Get straightness of selected elements"""
        if not self._node_manager:
            return []
            
        result = []
        for elem in self:
            nodes = elem.get('eleNodes', [])
            if len(nodes) != 2:
                result.append(0.0)
                continue
                
            coords1 = self._node_manager.get_node_coords(nodes[0])
            coords2 = self._node_manager.get_node_coords(nodes[1])
            if not (coords1 and coords2):
                result.append(0.0)
                continue
                
            length = math.sqrt(sum((c2 - c1)**2 for c1, c2 in zip(coords1, coords2)))
            result.append(length)
            
        return result
        
    def by_type(self, type_name: str) -> 'ElementSelector':
        """Filter elements by type"""
        return self.filter(lambda elem: elem.get('eleType', '') == type_name)
        
    def by_nodes(self, node_ids: List[int]) -> 'ElementSelector':
        """Filter elements by nodes"""
        return self.filter(lambda elem: all(nid in elem.get('eleNodes', []) for nid in node_ids))
        
    def by_material(self, material_id: int) -> 'ElementSelector':
        """Filter elements by material"""
        return self.filter(lambda elem: elem.get('matTag', 0) == material_id)
        
    def by_section(self, section_id: int) -> 'ElementSelector':
        """Filter elements by section"""
        return self.filter(lambda elem: elem.get('secTag', 0) == section_id)
        
    def by_transformation(self, esys_id: int) -> 'ElementSelector':
        """Filter elements by coordinate system"""
        return self.filter(lambda elem: elem.get('esys', 0) == esys_id)
        
    def by_category(self, category: str) -> 'ElementSelector':
        """Filter elements by category"""
        return self.filter(lambda elem: elem.get('category', '') == category)
        
    def connected_nodes(self) -> List[int]:
        """Get all nodes connected to selected elements"""
        if not self._node_manager:
            return []
            
        node_ids = []
        for eleid,elem in self:
            node_ids.extend(elem.get('eleNodes', []))
        return list(node_ids) 