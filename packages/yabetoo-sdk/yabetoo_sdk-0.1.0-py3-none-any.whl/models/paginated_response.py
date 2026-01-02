from typing import Dict, Optional, List, Any, TypeVar, Generic, Type


T = TypeVar('T')  


class PaginatedResponse(Generic[T]):
 
    
    def __init__(self, data: Dict[str, Any], model_class: Type[T]):
        self._data = data
        self._model_class = model_class
        self._items: Optional[List[T]] = None
    
    @property
    def items(self) -> List[T]:
        if self._items is None:
            raw_items = self._data.get('data', [])
            self._items = [self._model_class(**item) for item in raw_items]
        return self._items
    
    @property
    def has_more(self) -> bool:
        return self._data.get('has_more', False)
    
    @property
    def total_count(self) -> int:
        return self._data.get('total_count', 0)
    
    @property
    def page(self) -> int:
        return self._data.get('page', 1)
    
    @property
    def per_page(self) -> int:
        return self._data.get('per_page', 10)
    
    @property
    def raw_data(self) -> Dict[str, Any]:
        return self._data