from typing import Dict, Type, TypeVar, Any, Callable
from fastapi import Depends

T = TypeVar('T')

class Container:
    def __init__(self):
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
        self._deps: Dict[str, Depends] = {}
    
    def register(self, key: str, factory: Callable):
        self._factories[key] = factory
        return self
    
    def get(self, key: str) -> Any:
        if key not in self._factories:
            raise KeyError(f"의존성 '{key}'가 등록되지 않았습니다.")
        return self._factories[key]()
    
    def depends_on(self, key: str) -> Depends:
        if key not in self._deps:
            self._deps[key] = Depends(lambda: self.get(key))
        return self._deps[key]

# 전역 컨테이너 인스턴스
container = Container()