from typing import Any, Dict, List, Optional, Set, Union
import math

from ._Selector import Selector, SelectType, MaterialSelectItem, MaterialProperty

class MaterialSelector(Selector):
    """Material selector implementing functionality similar to ANSYS MP command"""
    
    def _select_new(self,
                   item: MaterialSelectItem = None,
                   comp: str = None,
                   vmin: Union[int, float, str] = None,
                   vmax: Union[int, float, str] = None,
                   vinc: int = 1,
                   kabs: int = 0,
                   **kwargs) -> Set[int]:
        """
        Create new material selection based on criteria
        
        Args:
            item: Selection item type
            comp: Component for selection
            vmin: Minimum value
            vmax: Maximum value
            vinc: Value increment
            kabs: Absolute value key (0=Check sign, 1=Use absolute value)
            **kwargs: Additional selection criteria
            
        Returns:
            Set of selected material IDs
        """
        if not item:
            return set()
            
        vmax = vmax if vmax is not None else vmin
        selected = set()
        
        # Select by material ID
        if item == MaterialSelectItem.TAG.value:
            if isinstance(vmin, (int, float)):
                selected = {mid for mid in self._items.keys() 
                          if vmin <= mid <= vmax and (mid - vmin) % vinc == 0}
                          
        # Select by material type
        elif item == MaterialSelectItem.TYPE.value:
            for mid, mat in self._items.items():
                if mat.get('matType', '') == vmin:
                    selected.add(mid)
                    
        # Select by material category
        elif item == MaterialSelectItem.CATEGORY.value:
            if vmin.lower() in "uniaxialMaterial".lower():
                for mid, mat in self._items.items():
                    if mat.get('matType', '') in self._material_manager.uniaxialMaterial_list:
                        selected.add(mid)
            elif vmin.lower() in "nDMaterial".lower():
                for mid, mat in self._items.items():
                    if mat.get('matType', '') in self._material_manager.nDMaterial_list:
                        selected.add(mid)
                    
        # Select by property
        elif item == MaterialSelectItem.PROPERTY.value:
            if not comp:
                return set()
                
            for mid, mat in self._items.items():
                # 检查材料属性，如E值
                if comp == 'E' and 'E' in mat:
                    val = abs(mat['E']) if kabs else mat['E']
                    if vmin <= val <= vmax:
                        selected.add(mid)
                        
 
        return selected
        
    def get_types(self) -> List[int]:
        """Get types of selected materials"""
        return [mat.get('matType', '') for mat in self]
        
    def get_categories(self) -> List[str]:
        """Get categories of selected materials"""
        return [mat.get('materialType', '') for mat in self]
        
    def get_properties(self) -> List[Dict[str, float]]:
        """Get properties of selected materials"""
        return [mat for mat in self]
        
    def used_by_elements(self) -> List[int]:
        """Get elements using selected materials"""
        if not self._element_manager:
            return []
            
        result = []
        for mat_id in self._current_selection:
            elements = self._element_manager.get_elements_by_material(mat_id)
            result.extend(elements)
        return result
        
    def by_type(self, type_name: str) -> 'MaterialSelector':
        """Filter materials by type"""
        return self.filter(lambda mat: mat.get('matType', '') == type_name) 