from collections import (
    OrderedDict,
)
from typing import (
    TYPE_CHECKING,
)

from nanolib.abc import (
    IHost,
)
from nanolib.host.ping import (
    ID as PingID,
    handle_ping,
)
from nanolib.identity.identify.identify import (
    ID as IdentifyID,
    identify_handler_for,
)

if TYPE_CHECKING:
    from nanolib.custom_types import (
        StreamHandlerFn,
        TProtocol,
    )


def get_default_protocols(host: IHost) -> "OrderedDict[TProtocol, StreamHandlerFn]":
    return OrderedDict(
        (
            (IdentifyID, identify_handler_for(host, use_varint_format=True)),
            (PingID, handle_ping),
        )
    )
