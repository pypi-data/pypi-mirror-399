from ..constants import CUSTOM_BLOCK_ALTERNATIVE as CUSTOM_BLOCK_ALTERNATIVE, CUSTOM_BLOCK_HEAD as CUSTOM_BLOCK_HEAD, CUSTOM_BLOCK_VANILLA as CUSTOM_BLOCK_VANILLA, NO_SILK_TOUCH_DROP as NO_SILK_TOUCH_DROP, VANILLA_BLOCK as VANILLA_BLOCK
from ._utils import StMapping as StMapping
from .item import Item as Item
from _typeshed import Incomplete
from beet.core.utils import JsonDict as JsonDict
from dataclasses import dataclass
from typing import Literal

@dataclass(kw_only=True)
class VanillaBlock(StMapping):
    ''' Represents a vanilla block with optional facing and contents.

    >>> vb = VanillaBlock(id="minecraft:stone")
    >>> vb.id
    \'minecraft:stone\'
    >>> vb.apply_facing
    False
    '''
    id: str = ...
    apply_facing: Literal[False, True, 'entity'] = ...
    contents: bool = ...
    def __post_init__(self) -> None: ...

@dataclass(kw_only=True)
class NoSilkTouchDrop(StMapping):
    ''' Defines the item dropped when the block is broken without silk touch.

    >>> nsd = NoSilkTouchDrop(id="raw_iron")
    >>> nsd.id
    \'raw_iron\'
    >>> nsd.count
    1
    '''
    id: str
    count: dict[str, int] | int = ...
    def __post_init__(self) -> None: ...

@dataclass(kw_only=True)
class GrowingSeedLoot(StMapping):
    ''' Defines a single loot entry for a growing seed.

    >>> gsl = GrowingSeedLoot(id="stardust_fragment", rolls=3)
    >>> gsl.id
    \'stardust_fragment\'
    >>> gsl.rolls
    3
    '''
    id: str
    rolls: JsonDict | int = ...
    fortune: JsonDict | None = ...

@dataclass(kw_only=True)
class GrowingSeed(StMapping):
    ''' Defines a seed that grows over time (Stardust Seed from Stardust Fragment).

    >>> gs = GrowingSeed(texture_basename="stardust", seconds=480, planted_on="diamond_block", loots=[GrowingSeedLoot(id="stardust_fragment")])
    >>> gs.texture_basename
    \'stardust\'
    >>> gs.seconds
    480
    '''
    texture_basename: str
    seconds: int
    planted_on: str
    loots: list[GrowingSeedLoot] | str
    def __post_init__(self) -> None: ...

@dataclass(kw_only=True)
class Block(Item):
    ''' Represents a block item with vanilla block properties.

    ## Simple example
    >>> from stewbeet import Mem
    >>> block = Block(id="machine_block", vanilla_block=VanillaBlock(id="minecraft:stone"))
    >>> block.id
    \'machine_block\'
    >>> block.vanilla_block.id
    \'minecraft:stone\'
    >>> block.id in Mem.definitions
    True
    >>> block is Block.from_id("machine_block")
    True

    ## Big example with all fields
    >>> from stewbeet import CraftingShapelessRecipe, WikiButton, NoSilkTouchDrop, GrowingSeed, GrowingSeedLoot, ingr_repr
    >>> obj = BlockAlternative(
    ...     id="stardust_seed",
    ...     manual_category="miscellaneous",
    ...     recipes=[
    ...         CraftingShapelessRecipe(ingredients=8*[ingr_repr("stardust_fragment")] + [ingr_repr("minecraft:wheat_seeds")])
    ...     ],
    ...     override_model={"parent":"item/generated","textures":{"layer0":"stardust:item/stardust_seed"}},
    ...     wiki_buttons=[WikiButton({"text":"A magical seed that grows stardust.","color":"aqua"})],
    ...     components={
    ...         "item_name": {"text":"Stardust Seed","color":"aqua"},
    ...         "max_stack_size": 64,
    ...     },
    ...     vanilla_block=VanillaBlock(id="minecraft:wheat", apply_facing=False),
    ...     no_silk_touch_drop=NoSilkTouchDrop(id="stardust_fragment", count=1),
    ...     growing_seed=GrowingSeed(
    ...         texture_basename="stardust",
    ...         seconds=480,
    ...         planted_on="diamond_block",
    ...         loots=[GrowingSeedLoot(id="stardust_fragment", rolls=3)]
    ...     )
    ... )
    >>> also_obj = Block.from_id("stardust_seed")
    >>> obj is also_obj
    True
    '''
    base_item: str = ...
    vanilla_block: VanillaBlock
    no_silk_touch_drop: NoSilkTouchDrop | str | None = ...
    growing_seed: GrowingSeed | None = ...
    def __post_init__(self) -> None: ...
    def _get_mapping(self) -> JsonDict: ...

@dataclass(kw_only=True)
class BlockAlternative(Block):
    ''' Represents a block that uses an item frame for placement (e.g., servo inserter/extractor).

    >>> ba = BlockAlternative(id="servo_inserter", vanilla_block=VanillaBlock(contents=True))
    >>> ba.base_item
    \'minecraft:item_frame\'
    '''
    base_item = CUSTOM_BLOCK_ALTERNATIVE
    def __post_init__(self) -> None: ...

@dataclass(kw_only=True)
class BlockHead(Block):
    ''' Represents a block that uses a player head for placement.

    >>> bh = BlockHead(id="custom_head", vanilla_block=VanillaBlock(id="minecraft:player_head"))
    >>> bh.base_item
    \'minecraft:player_head\'
    '''
    base_item = CUSTOM_BLOCK_HEAD
    def __post_init__(self) -> None: ...

VANILLA_BLOCK_FOR_ORES: Incomplete
