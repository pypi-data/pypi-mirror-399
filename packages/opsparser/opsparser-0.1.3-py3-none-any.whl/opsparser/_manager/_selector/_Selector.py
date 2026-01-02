from typing import Any, Dict, Generator, List, Optional, Set, Union, Callable, TypeVar, Generic, Type
from abc import ABC, abstractmethod, ABCMeta
from enum import Enum

class SelectType(Enum):
    """Selection type enum"""
    NEW = 'New'      # Select a new set
    ADD = 'Add'      # Additionally select a set
    REMOVE = 'Remove'   # Unselect a set
    RESELECT = 'Reselect' # Reselect a set
    INVERT = 'Invert' # Invert the current set
    ALL = 'All'    # Select all
    NONE = 'Unselect'  # Unselect all
    STATUS = 'Status' # Display current selection status

class NodeSelectItem(Enum):
    """Node selection item enum"""
    TAG = 'Tag'    # Select by node ID
    COORD = 'Coord'      # Select by coordinates
    RADIUS = 'Radius' # Select by radial distance
    NDF = 'NDF'      # Select by number of DOFs

class NodeSelectComp(Enum):
    """Node selection component enum"""
    X = 'X'          # X coordinate
    Y = 'Y'          # Y coordinate
    Z = 'Z'          # Z coordinate

class ElementSelectItem(Enum):
    """Element selection item enum"""
    TAG = 'Tag'    # Select by element ID
    TYPE = 'Type'    # Select by element type
    MAT = 'Material'      # Select by material ID
    SECTION = 'Section' # Select by section number
    NODE = 'Node'    # Select by node

class ElementSelectComp(Enum):
    """Element selection component enum"""
    X = 'X'          # X coordinate
    Y = 'Y'          # Y coordinate
    Z = 'Z'          # Z coordinate

class MaterialSelectItem(Enum):
    """Material selection item enum"""
    TAG = 'Tag'      # Select by material ID
    TYPE = 'Type'    # Select by material type
    CATEGORY = 'Category' # Select by material category
    PROPERTY = 'Property' # Select by material property


class MaterialProperty(Enum):
    """Material property enum"""
    EX = 'EX'        # Young's modulus
    NUXY = 'NUXY'    # Poisson's ratio
    GXY = 'GXY'      # Shear modulus
    ALPX = 'ALPX'    # Thermal expansion coefficient
    DENS = 'DENS'    # Density

class SingletonMeta(ABCMeta):
    """
    A metaclass that implements the Singleton pattern.
    Ensures only one instance of a class is created.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Override the __call__ method to implement Singleton behavior.
        Returns the existing instance if it exists, otherwise creates a new one.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class Selector(metaclass=SingletonMeta):
    """Base selector class that implements selection operations similar to ANSYS commands"""
    
    # Class-level manager references
    _node_manager = None
    _element_manager = None
    _material_manager = None
    _section_manager = None
    _constraint_manager = None
    _load_manager = None
    
    @classmethod
    def set_managers(cls, 
                    node_manager=None,
                    element_manager=None,
                    material_manager=None,
                    section_manager=None,
                    constraint_manager=None,
                    load_manager=None):
        """Set manager references for all selectors"""
        cls._node_manager = node_manager
        cls._element_manager = element_manager
        cls._material_manager = material_manager
        cls._section_manager = section_manager
        cls._constraint_manager = constraint_manager
        cls._load_manager = load_manager
    
    def __init__(self, items: Dict[int, Dict[str, Any]]):
        """
        Initialize selector
        
        Args:
            items: Dictionary of items to select from
        """
        self._items = items
        self._current_selection: Set[int] = set()
        self._selection_history: List[Set[int]] = []
        self._filters: List[Callable[[Dict[str, Any]], bool]] = []
        self._transformations: List[Callable[[Dict[str, Any]], Any]] = []
        
    def sel(self, 
            type: SelectType = SelectType.RESELECT,
            item: str = None,
            comp: str = None,
            vmin: Union[int, float, str] = None,
            vmax: Union[int, float, str] = None,
            vinc: int = 1,
            kabs: int = 0,
            **kwargs) -> 'Selector':
        """
        Select items based on criteria
        
        Args:
            type: Selection type (S=New, A=Add, U=Remove, R=Reselect, INVE=Invert, ALL=All, NONE=None, STAT=Status)
            item: Item to select on
            comp: Component of the item
            vmin: Minimum value
            vmax: Maximum value
            vinc: Value increment
            kabs: Absolute value key (0=Check sign, 1=Use absolute value)
            **kwargs: Additional selection criteria
            
        Returns:
            Self for chaining
        """
        # Handle special selection types
        if type == SelectType.ALL:
            self._current_selection = set(self._items.keys())
            return self
            
        if type == SelectType.NONE:
            self._current_selection.clear()
            return self
            
        if type == SelectType.STATUS:
            print(f"Current selection: {sorted(self._current_selection)}")
            return self
            
        # Save current selection to history
        self._selection_history.append(self._current_selection.copy())
        
        # Get new selection based on criteria
        new_selection = self._select_new(item, comp, vmin, vmax, vinc, kabs, **kwargs)
        
        # Apply selection type
        if type == SelectType.NEW:
            self._current_selection = new_selection
        elif type == SelectType.ADD:
            self._current_selection.update(new_selection)
        elif type == SelectType.REMOVE:
            self._current_selection.difference_update(new_selection)
        elif type == SelectType.RESELECT:
            self._current_selection.intersection_update(new_selection)
        elif type == SelectType.INVERT:
            all_items = set(self._items.keys())
            self._current_selection = all_items - self._current_selection
            
        return self
        
    def _select_new(self, 
                   item: str,
                   comp: str,
                   vmin: Union[int, float, str],
                   vmax: Union[int, float, str],
                   vinc: int,
                   kabs: int,
                   **kwargs) -> Set[int]:
        """
        Create new selection based on criteria
        
        Args:
            item: Item to select on
            comp: Component of the item
            vmin: Minimum value
            vmax: Maximum value
            vinc: Value increment
            kabs: Absolute value key
            **kwargs: Additional selection criteria
            
        Returns:
            Set of selected item IDs
        """
        raise NotImplementedError("Subclasses must implement _select_new")
        
    def undo(self) -> 'Selector':
        """Undo last selection operation"""
        if self._selection_history:
            self._current_selection = self._selection_history.pop()
        return self
        
    def __iter__(self) -> Generator[tuple[int, Dict[str, Any]], None, None]:
        """Iterate over selected items, yielding (id, item) pairs"""
        for item_id in sorted(self._current_selection):
            # 应用所有过滤条件
            item = self._items[item_id]
            if all(predicate(item) for predicate in self._filters):
                # 应用所有转换
                result = item
                for transform in self._transformations:
                    result = transform(result)
                yield item_id, result
            
    def collect(self) -> List[tuple[int, Dict[str, Any]]]:
        """Collect all selected items into a list of (id, item) pairs"""
        return list(self)
    
    def first(self) -> Optional[Dict[str, Any]]:
        """获取当前选择集中的第一个元素"""
        for item in self:
            return item
        return None
    
    def count(self) -> int:
        """获取当前选择集的大小"""
        return len(self._current_selection)
    
    def exists(self) -> bool:
        """检查当前选择集是否为空"""
        return bool(self._current_selection)
    
    def get_selected_keys(self) -> Set[int]:
        """获取当前选择集的键"""
        return self._current_selection.copy()
    
    def get_selected_values(self) -> List[Dict[str, Any]]:
        """获取当前选择集的值"""
        return [self._items[key] for key in self._current_selection]

    def filter(self, predicate: Callable[[Dict[str, Any]], bool]) -> 'Selector':
        """添加过滤条件"""
        self._filters.append(predicate)
        return self
        
    def transform(self, func: Callable[[Dict[str, Any]], Any]) -> 'Selector':
        """添加转换函数"""
        self._transformations.append(func)
        return self

    @property
    def node_manager(self):
        """Get node manager reference"""
        return self._node_manager
        
    @property
    def element_manager(self):
        """Get element manager reference"""
        return self._element_manager
        
    @property
    def material_manager(self):
        """Get material manager reference"""
        return self._material_manager
        
    @property
    def section_manager(self):
        """Get section manager reference"""
        return self._section_manager
        
    @property
    def constraint_manager(self):
        """Get constraint manager reference"""
        return self._constraint_manager
        
    @property
    def load_manager(self):
        """Get load manager reference"""
        return self._load_manager 