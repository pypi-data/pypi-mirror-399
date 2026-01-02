from dataclasses import dataclass, field
from typing import Optional

from dataclasses_json import dataclass_json

from notify_tls_client.tls_client.settings import ClientIdentifiers


@dataclass_json
@dataclass
class ClientIdentifiersManager:
    _items: list[ClientIdentifiers] = field(default_factory=list)
    _current_index: int = 0
    _current_item: Optional[ClientIdentifiers] = None

    def get_next(self) -> ClientIdentifiers:
        if not self._items:
            raise Exception('No items available')

        if self._current_index < len(self._items):
            _item = self._items[self._current_index]
            self._current_index += 1
        else:
            self._current_index = 0
            _item = self._items[self._current_index]

        return _item

    def get_current_item(self) -> Optional[ClientIdentifiers]:
        if not self._items:
            return None

        return self._items[0] if self._current_index == 0 else self._items[self._current_index - 1]


    def set_items(self, items: list[ClientIdentifiers]):
        self._items = items
        self._current_proxy_index = 0
        self._current_proxy = None

    def get_item(self) -> list[ClientIdentifiers]:
        return self._items

    def get_total_items(self) -> int:
        return len(self._items)
