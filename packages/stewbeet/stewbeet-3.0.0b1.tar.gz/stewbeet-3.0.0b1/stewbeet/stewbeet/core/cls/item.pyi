from ..constants import CATEGORY as CATEGORY, CUSTOM_ITEM_VANILLA as CUSTOM_ITEM_VANILLA, OVERRIDE_MODEL as OVERRIDE_MODEL, RESULT_OF_CRAFTING as RESULT_OF_CRAFTING, USED_FOR_CRAFTING as USED_FOR_CRAFTING, WIKI_COMPONENT as WIKI_COMPONENT
from ._utils import StMapping as StMapping
from .recipe import RecipeBase as RecipeBase
from .wiki_button import WikiButton as WikiButton
from beet.core.utils import JsonDict as JsonDict, TextComponent as TextComponent
from dataclasses import dataclass, field
from typing import Any

@dataclass(kw_only=True)
class Item(StMapping):
    ''' Represents an item with a unique identifier.

    ## Simple example
    >>> from stewbeet import Mem
    >>> item = Item(id="multimeter", base_item="minecraft:warped_fungus_on_a_stick")
    >>> item.id
    \'multimeter\'
    >>> item.base_item
    \'minecraft:warped_fungus_on_a_stick\'
    >>> item.id in Mem.definitions
    True
    >>> item is Item.from_id("multimeter")
    True

    ## Instance without registration in Mem.definitions
    >>> nonreg_item = Item(id="")   # Item with empty ID won\'t be registered
    >>> nonreg_item.id = "temporary_item"
    >>> "temporary_item" in Mem.definitions
    False
    >>> nonreg_item is Item.from_id("temporary_item", strict=False)
    False

    ## Big example with all fields
    >>> from stewbeet import CraftingShapedRecipe, WikiButton, ingr_repr
    >>> obj = Item(
    ...     id="stardust_ingot",
    ...     base_item="minecraft:raw_iron",
    ...     manual_category="materials",
    ...     recipes=[
    ...         CraftingShapedRecipe(shape=["###","#F#","###"], ingredients={"#":ingr_repr("stardust_fragment"),"F":ingr_repr("minecraft:iron_ingot")})
    ...     ],
    ...     override_model={"parent":"item/generated","textures":{"layer0":"stardust:item/stardust_ingot"}},
    ...     wiki_buttons=[WikiButton({"text":"This is a stardust ingot.","color":"aqua"})],
    ...     components={
    ...         "item_name": {"text":"Stardust Ingot","color":"aqua"},
    ...         "max_stack_size": 99,
    ...     }
    ... )
    >>> also_obj = Item.from_id("stardust_ingot")
    >>> obj is also_obj
    True
    '''
    id: str
    base_item: str = ...
    manual_category: str | None = ...
    recipes: list[RecipeBase] = field(default_factory=list[RecipeBase])
    override_model: JsonDict | None = ...
    hand_model: JsonDict | None = ...
    wiki_buttons: list[WikiButton] | TextComponent | None = ...
    components: JsonDict = field(default_factory=dict[str, Any])
    def __post_init__(self) -> None: ...
    def _get_mapping(self) -> JsonDict: ...
    def __getitem__(self, key: str) -> Any: ...
    def __len__(self) -> int: ...
    def __iter__(self): ...
    def update(self, other: JsonDict) -> None: ...
