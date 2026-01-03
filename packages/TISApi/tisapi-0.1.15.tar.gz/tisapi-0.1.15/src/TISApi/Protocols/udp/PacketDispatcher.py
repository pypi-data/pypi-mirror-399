import logging
from typing import Callable

_LOGGER = logging.getLogger(__name__)


class PacketDispatcher:
    """
    Routes parsed packet information to the appropriate handler function.

    This class acts as a central hub after a packet has been received and parsed.
    It uses a dictionary to look up the correct action to take based on the
    packet's operation code.
    """

    def __init__(self, fire_event_callback: Callable, operations_dict: dict):
        """
        Initialize the PacketDispatcher.

        :param fire_event_callback: The fire event callback funciton, passed to handler functions.
        :param operations_dict: A dictionary mapping operation codes to handler functions.
        """
        self.fire_event_callback = fire_event_callback
        self.operations_dict = operations_dict

    async def dispatch_packet(self, info: dict):
        """
        Dispatches a packet based on its operation code.

        :param info: A dictionary containing the parsed information from the packet.
        """
        try:
            # Look up the handler function in the operations dictionary using the packet's operation code.
            # The operation code (a list) is converted to a tuple to be used as a dictionary key.
            packet_handler = self.operations_dict.get(
                tuple(info["operation_code"]), "unknown operation"
            )

            # If a handler function was found, execute it.
            if packet_handler != "unknown operation":
                # The handler itself is an async function, so it must be awaited.
                await packet_handler(self.fire_event_callback, info)
            else:
                # If the operation code is not in our dictionary, log it as an error.
                _LOGGER.error(
                    "Unknown operation code received: %s", str(info["operation_code"])
                )
        except Exception as e:
            # Catch any unexpected errors during the dispatch process to prevent a crash.
            _LOGGER.error("Error dispatching packet: %s , info: %s", e, info)
