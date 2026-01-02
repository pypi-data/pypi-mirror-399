from .__memory__ import Mem as Mem
from .constants import AWAKENED_FORGE as AWAKENED_FORGE, NOT_COMPONENTS as NOT_COMPONENTS, PULVERIZING as PULVERIZING
from beet.core.utils import JsonDict, TextComponent as TextComponent

FURNACES_RECIPES_TYPES: tuple[str, ...]
CRAFTING_RECIPES_TYPES: tuple[str, ...]
OTHER_RECIPES_TYPES: tuple[str, ...]
UNUSED_RECIPES_TYPES: tuple[str, ...]
SPECIAL_RECIPES_TYPES: tuple[str, ...]
ALL_RECIPES_TYPES: tuple[str, ...]

def ingr_repr(id: str, ns: str | None = None, count: int | None = None) -> JsonDict:
    ''' Get the identity of the ingredient from its id for custom crafts
\tArgs:
\t\tid\t\t(str):\t\tThe id of the ingredient, ex: adamantium_fragment
\t\tns\t\t(str|None):\tThe namespace of the ingredient (optional if \'id\' argument is a vanilla item), ex: iyc (default: current project id)
\t\tcount\t(int|None):\tThe count of the ingredient (optional, used only when this ingredient format is a result item) (or use a special type of recipe that supports counts)
\tReturns:
\t\tstr: The identity of the ingredient for custom crafts,
\t\t\tex: {"components":{"minecraft:custom_data":{"iyc":{"adamantium_fragment":True}}}}
\t\t\tex: {"item": "minecraft:stick"}
\t'''
def item_to_id_ingr_repr(ingr: JsonDict) -> JsonDict:
    ''' Replace the "item" key by "id" in an item ingredient representation
\tArgs:
\t\tingr (dict): The item ingredient, ex: {"item": "minecraft:stick"}
\tReturns:
\t\tdict: The item ingredient representation, ex: {"id": "minecraft:stick"}
\t'''
def ingr_to_id(ingredient: JsonDict, add_namespace: bool = True) -> str:
    ''' Get the id from an ingredient dict
\tArgs:
\t\tingredient (dict): The ingredient dict
\t\t\tex: {"components":{"minecraft:custom_data":{iyc:{adamantium_ingot:True}}}}
\t\t\tex: {"item": "minecraft:stick"}
\t\tadd_namespace (bool): Whether to add the namespace to the id
\tReturns:
\t\tstr: The id of the ingredient, ex: "minecraft:stick" or "iyc:adamantium_ingot"
\t'''
def text_component_to_str(tc: TextComponent) -> str:
    """ Convert a TextComponent to a string
\tArgs:
\t\ttc (TextComponent): The TextComponent to convert
\tReturns:
\t\tstr: The converted string
\t"""
def item_id_to_text_component(item_id: str, use_default: bool = True) -> TextComponent:
    ''' Get the TextComponent from an item id

\tArgs:
\t\titem_id (str): The item id, ex: "minecraft:stick" or "iyc:adamantium_ingot"
\t\tuse_default (bool): Whether to use the default prettified string if no TextComponent is found
\tReturns:
\t\tstr: The TextComponent of the item, ex: "Stick" or {"text":"Adamantium Ingot"}
\t'''
def item_id_to_name(item_id: str) -> str:
    ''' Get the name from an item id
\tArgs:
\t\titem_id (str): The item id, ex: "minecraft:stick" or "iyc:adamantium_ingot"
\tReturns:
\t\tstr: The name of the item, ex: "Stick" or "Adamantium Ingot"
\t'''
def ingr_to_name(ingredient: JsonDict) -> str:
    ''' Get the name from an ingredient dict
\tArgs:
\t\tingredient (dict): The ingredient dict
\t\t\tex: {"components":{"minecraft:custom_data":{iyc:{adamantium_ingot:True}}}}
\t\t\tex: {"item": "minecraft:stick"}
\tReturns:
\t\tstr: The name of the ingredient, ex: "Stick" or "Adamantium Ingot"
\t'''
def get_vanilla_item_id_from_ingredient(ingredient: JsonDict, add_namespace: bool = True) -> str:
    ''' Get the id of the vanilla item from an ingredient dict
\tArgs:
\t\tconfig (dict): The config dict
\t\tingredient (dict): The ingredient dict
\t\t\tex: {"item": "minecraft:stick"}
\t\tadd_namespace (bool): Whether to add the namespace to the id
\tReturns:
\t\tstr: The id of the vanilla item, ex: "minecraft:stick"
\t'''
def get_item_from_ingredient(ingredient: JsonDict) -> JsonDict:
    ''' Get the item dict from an ingredient dict
\tArgs:
\t\tconfig (dict): The config dict
\t\tingredient (dict): The ingredient dict
\t\t\tex: {"item": "minecraft:stick"}
\tReturns:
\t\tdict: The item data dict, ex: {"id": "minecraft:stick", "count": 1}
\t'''
def loot_table_from_ingredient(result_ingredient: JsonDict, result_count: int | JsonDict) -> str:
    ''' Get the loot table for an ingredient dict
\tArgs:
\t\tresult_ingredient (dict): The ingredient dict
\t\t\tex: {"item": "minecraft:stick"}
\t\tresult_count (int|dict): The count of the result item, can be an int or a dict for random counts
\t\t\tex: 1
\t\t\tex: {"type": "minecraft:uniform","min": 4,"max": 6}
\tReturns:
\t\tstr: The loot table path, ex: "my_datapack:i/stick"
\t'''
def get_ingredients_from_recipe(recipe: JsonDict) -> list[str]:
    ''' Get the ingredients from a recipe dict
\tArgs:
\t\trecipe (dict): The final recipe JSON dict, ex:

\t\t{
\t\t\t"type": "minecraft:crafting_shaped",
\t\t\t"pattern": [...],
\t\t\t"key": {...},
\t\t\t"result": {...}
\t\t}
\tReturns:
\t\tlist[str]: The ingredients ids
\t'''
