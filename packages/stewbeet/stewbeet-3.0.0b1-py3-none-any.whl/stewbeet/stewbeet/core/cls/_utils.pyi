from ..constants import NOT_COMPONENTS as NOT_COMPONENTS
from beet.core.utils import JsonDict as JsonDict
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Self

@dataclass
class StMapping(Mapping[str, Any]):
    def __getitem__(self, key: str) -> Any: ...
    def __setitem__(self, key: str, value: Any) -> None: ...
    def get(self, key: str, default: Any = None) -> Any: ...
    def setdefault(self, key: str, default: Any = None) -> Any:
        """ Set a default value if key doesn't exist, like dict.setdefault(). """
    def to_dict(self) -> JsonDict:
        """ Convert the object to a dictionary for JSON serialization """
    @classmethod
    def from_dict(cls, data: JsonDict | StMapping, item_id: str) -> Self:
        """ Create an object based on items """
    @classmethod
    def from_id(cls, item_id: str, strict: bool = True) -> Self:
        """ Create an object based of definitions. If ':' is in item_id, it's in external_definitions

        Args:
            item_id\t(str):\t\tThe item ID to create the object from.
            strict\t(bool):\t\tWhether to raise an error if the item is not found.
        """
    def copy(self) -> JsonDict:
        """ Return a shallow copy as a dictionary. """
    def __len__(self) -> int: ...
    def __iter__(self): ...
