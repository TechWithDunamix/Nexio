
from typing import Any


class BaseConfig:

    debug :bool  = False

    

    


    def __getattribute__(self, name: str) -> Any:
        try:
            return super().__getattribute__(name)
            
        except AttributeError:
            return None


