from beet import Context as Context
from beet.core.utils import JsonDict as JsonDict

class Mem:
    ctx: Context
    definitions: dict[str, JsonDict]
    external_definitions: dict[str, JsonDict]
