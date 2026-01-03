from _typeshed import Incomplete
from beet.core.utils import TextComponent as TextComponent
from typing import Any

class WikiButton:
    ''' Represents a button in the ingame manual that provides additional information about an item.

    >>> content = [{"text": "Hello", "color": "yellow"}]
    >>> button = WikiButton(content)
    >>> button.content
    [{\'text\': \'Hello\', \'color\': \'yellow\'}]
    >>> button.content[0]
    {\'text\': \'Hello\', \'color\': \'yellow\'}
    >>> WikiButton(button.content[0]).content["text"]
    \'Hello\'
    '''
    __slots__: Incomplete
    content: Incomplete
    def __init__(self, content: TextComponent) -> None: ...
    def __repr__(self) -> str: ...
    def to_dict(self) -> str | list[Any] | dict[str, Any]:
        """ Convert to JSON-serializable format (returns the underlying TextComponent). """
