from ._utils import StMapping as StMapping
from beet.core.utils import JsonDict as JsonDict
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any, Literal, Self

@dataclass(kw_only=True)
class RecipeBase(StMapping):
    """ Base class for all recipe types. """
    type: str = ...
    result_count: int = ...
    category: str | None = ...
    group: str | None = ...
    result: JsonDict | None = ...
    manual_priority: int | None = ...
    smithed_crafter_command: str | None = ...
    def __post_init__(self) -> None: ...
    def __getitem__(self, key: str) -> Any:
        """Get item from recipe data as if it were a dictionary."""
    def __setitem__(self, key: str, value: Any) -> None: ...
    def __iter__(self) -> Iterator[str]:
        """Iterate over recipe keys."""
    def __len__(self) -> int:
        """Return the number of non-None fields."""
    @classmethod
    def from_dict(cls, data: JsonDict | StMapping, item_id: str = '') -> Self:
        """ Create an object based on a dictionary. """
    @staticmethod
    def _validate_ingredient(ingredient: JsonDict, name: str = 'Ingredient') -> None:
        """Validate a single ingredient dictionary."""
    @staticmethod
    def _validate_ingredients_list(ingredients: list[JsonDict]) -> None:
        """Validate a list of ingredients."""
    @staticmethod
    def _validate_numeric_fields(experience: Any, cookingtime: Any) -> None:
        """Validate experience and cookingtime fields for furnace recipes."""

@dataclass
class CraftingShapedRecipe(RecipeBase):
    ''' Recipe for shaped crafting.

    >>> from stewbeet import *
    >>> recipe = CraftingShapedRecipe(
    ...     shape=["II", "CC", "CC"],
    ...     ingredients={"I":ingr_repr("minecraft:iron_ingot"), "C": ingr_repr("simplunium_ingot")}
    ... )
    >>> recipe.shape
    [\'II\', \'CC\', \'CC\']
    >>> recipe.ingredients[\'I\']
    {\'item\': \'minecraft:iron_ingot\'}
    >>> recipe.ingredients[\'C\']
    {\'components\': {\'minecraft:custom_data\': {\'detected_namespace\': {\'simplunium_ingot\': True}}}}
    '''
    shape: list[str]
    ingredients: dict[str, JsonDict]
    type = ...
    def __post_init__(self) -> None: ...

@dataclass
class CraftingShapelessRecipe(RecipeBase):
    ''' Recipe for shapeless crafting.

    >>> from stewbeet import *
    >>> recipe = CraftingShapelessRecipe(ingredients=[ingr_repr("minecraft:iron_ingot"), ingr_repr("minecraft:copper_ingot")])
    >>> len(recipe.ingredients)
    2
    >>> recipe.type
    \'crafting_shapeless\'
    '''
    ingredients: list[JsonDict]
    type = ...
    def __post_init__(self) -> None: ...

@dataclass
class SmeltingRecipe(RecipeBase):
    ''' Recipe for smelting in a furnace.

    >>> from stewbeet import *
    >>> recipe = SmeltingRecipe(ingredient=ingr_repr("minecraft:iron_ore"), experience=0.7, cookingtime=200)
    >>> recipe.experience
    0.7
    >>> recipe.cookingtime
    200
    '''
    ingredient: JsonDict
    experience: float = ...
    cookingtime: int = ...
    type = ...
    def __post_init__(self) -> None: ...

@dataclass
class BlastingRecipe(RecipeBase):
    ''' Recipe for blasting in a blast furnace.

    >>> from stewbeet import *
    >>> recipe = BlastingRecipe(ingredient=ingr_repr("minecraft:iron_ore"), experience=0.7, cookingtime=100)
    >>> recipe.experience
    0.7
    >>> recipe.cookingtime
    100
    '''
    ingredient: JsonDict
    experience: float = ...
    cookingtime: int = ...
    type = ...
    def __post_init__(self) -> None: ...

@dataclass
class SmokingRecipe(RecipeBase):
    ''' Recipe for smoking in a smoker.

    >>> from stewbeet import *
    >>> recipe = SmokingRecipe(ingredient=ingr_repr("minecraft:chicken"), experience=0.35, cookingtime=100)
    >>> recipe.experience
    0.35
    >>> recipe.cookingtime
    100
    '''
    ingredient: JsonDict
    experience: float = ...
    cookingtime: int = ...
    type = ...
    def __post_init__(self) -> None: ...

@dataclass
class CampfireCookingRecipe(RecipeBase):
    ''' Recipe for cooking on a campfire.

    >>> from stewbeet import *
    >>> recipe = CampfireCookingRecipe(ingredient=ingr_repr("minecraft:chicken"), experience=0.35, cookingtime=600)
    >>> recipe.experience
    0.35
    >>> recipe.cookingtime
    600
    '''
    ingredient: JsonDict
    experience: float
    cookingtime: int
    type = ...
    def __post_init__(self) -> None: ...

@dataclass
class SmithingTransformRecipe(RecipeBase):
    ''' Recipe for smithing table transformation.

    >>> from stewbeet import *
    >>> recipe = SmithingTransformRecipe(
    ...     template=ingr_repr("minecraft:netherite_upgrade_smithing_template"),
    ...     base=ingr_repr("minecraft:diamond_sword"),
    ...     addition=ingr_repr("minecraft:netherite_ingot")
    ... )
    >>> recipe.template[\'item\']
    \'minecraft:netherite_upgrade_smithing_template\'
    '''
    template: JsonDict
    base: JsonDict
    addition: JsonDict
    type = ...
    def __post_init__(self) -> None: ...

@dataclass
class SmithingTrimRecipe(RecipeBase):
    ''' Recipe for applying armor trims.

    >>> from stewbeet import *
    >>> recipe = SmithingTrimRecipe(
    ...     template=ingr_repr("minecraft:spire_armor_trim_smithing_template"),
    ...     base=ingr_repr("minecraft:netherite_chestplate"),
    ...     addition=ingr_repr("minecraft:diamond"),
    ...     pattern=ingr_repr("minecraft:spire_armor_trim_smithing_template")
    ... )
    >>> recipe.addition[\'item\']
    \'minecraft:diamond\'
    '''
    template: JsonDict
    base: JsonDict
    addition: JsonDict
    pattern: JsonDict
    type = ...
    def __post_init__(self) -> None: ...

@dataclass
class StonecuttingRecipe(RecipeBase):
    ''' Recipe for stonecutting.

    >>> from stewbeet import *
    >>> recipe = StonecuttingRecipe(ingredient=ingr_repr("minecraft:stone"))
    >>> recipe.ingredient[\'item\']
    \'minecraft:stone\'
    '''
    ingredient: JsonDict
    type = ...
    def __post_init__(self) -> None: ...

@dataclass
class PulverizingRecipe(RecipeBase):
    ''' Custom recipe for SimplEnergy pulverizing.

    >>> from stewbeet import *
    >>> recipe = PulverizingRecipe(ingredient=ingr_repr("minecraft:iron_ore"))
    >>> recipe.ingredient[\'item\']
    \'minecraft:iron_ore\'
    '''
    ingredient: JsonDict
    type = ...
    def __post_init__(self) -> None: ...

@dataclass
class AwakenedForgeRecipe(RecipeBase):
    ''' Custom recipe for Stardust awakened forge.

    >>> from stewbeet import *
    >>> recipe = AwakenedForgeRecipe(ingredients=[ingr_repr("stardust_fragment"), ingr_repr("minecraft:iron_ingot")])
    >>> len(recipe.ingredients)
    2
    '''
    ingredients: list[JsonDict]
    particle: str | None = ...
    type = ...
    def __post_init__(self) -> None: ...

@dataclass
class HardcodedRecipe(RecipeBase):
    '''Recipe for special/hardcoded crafting types.

    >>> recipe = HardcodedRecipe(type="crafting_special_armordye")
    >>> recipe.type
    \'crafting_special_armordye\'
    '''
    type: Literal['crafting_decorated_pot', 'crafting_special_armordye', 'crafting_special_bannerduplicate', 'crafting_special_bookcloning', 'crafting_special_firework_rocket', 'crafting_special_firework_star', 'crafting_special_firework_star_fade', 'crafting_special_mapcloning', 'crafting_special_mapextending', 'crafting_special_repairitem', 'crafting_special_shielddecoration', 'crafting_special_tippedarrow', 'crafting_transmute']
Recipe = CraftingShapedRecipe | CraftingShapelessRecipe | SmeltingRecipe | BlastingRecipe | SmokingRecipe | CampfireCookingRecipe | SmithingTransformRecipe | SmithingTrimRecipe | StonecuttingRecipe | PulverizingRecipe | AwakenedForgeRecipe | HardcodedRecipe
