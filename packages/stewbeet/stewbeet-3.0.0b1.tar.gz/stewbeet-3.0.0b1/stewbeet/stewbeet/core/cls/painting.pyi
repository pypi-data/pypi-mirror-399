from ._utils import StMapping as StMapping
from .item import Item as Item
from beet.core.utils import TextComponent as TextComponent
from dataclasses import dataclass

@dataclass(kw_only=True)
class PaintingData(StMapping):
    ''' Data class for painting-specific data.

    >>> pd = PaintingData(
    ...     texture="stewbeet_painting_2x2",            # Default to item id if not given (this example links to "assets/textures/stewbeet_painting_2x2.png")
    ...     author={"text":"Stoupy","color":"yellow"},  # Author defaults to ctx.project_author if not given
    ...     title={"text":"Da\' Icon","color":"gray"},   # Title defaults to item name if not given
    ...     width=4,
    ...     height=3
    ... )
    '''
    texture: str | None = ...
    author: TextComponent | None = ...
    title: TextComponent | None = ...
    width: int
    height: int

@dataclass(kw_only=True)
class Painting(Item):
    ''' Represents a custom painting item.

    ### Texture will default to "stewbeet_painting_2x2", author and title will default accordingly
    >>> my_painting = Painting(
    ...     id="stewbeet_painting_2x2",
    ...     painting_data=PaintingData(
    ...         author={"text":"An Artist I would say","color":"yellow"},
    ...         width=2,
    ...         height=2
    ...     ),
    ...     recipes=[],
    ...     components={
    ...         "max_stack_size": 16
    ...     }
    ... )
    >>> my_painting
    Painting(id=\'stewbeet_painting_2x2\', base_item=\'minecraft:painting\', manual_category=None, recipes=[], override_model=None, hand_model=None, wiki_buttons=None, components={\'max_stack_size\': 16, \'painting/variant\': \'your_namespace:stewbeet_painting_2x2\'}, painting_data=PaintingData(texture=\'stewbeet_painting_2x2\', author={\'text\': \'An Artist I would say\', \'color\': \'yellow\'}, title={\'text\': \'Stewbeet Painting 2X2\'}, width=2, height=2))
    '''
    base_item: str = ...
    painting_data: PaintingData
    def __post_init__(self) -> None: ...
