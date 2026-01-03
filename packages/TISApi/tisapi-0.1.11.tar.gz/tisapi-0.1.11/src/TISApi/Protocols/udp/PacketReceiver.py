# Import helper functions, networking components, and Home Assistant core.
import asyncio
import logging
from socket import socket

from TISApi.api import TISApi

from TISApi.BytesHelper import bytes2hex
from TISApi.Protocols.udp.PacketDispatcher import PacketDispatcher
from TISApi.Protocols.udp.PacketExtractor import PacketExtractor

_LOGGER = logging.getLogger(__name__)


class PacketReceiver:
    """
    An asyncio Protocol class for receiving and processing UDP datagrams.

    This class is designed to be used with asyncio's create_datagram_endpoint.
    It listens for incoming packets, extracts their information, and dispatches
    them for further action.
    """

    def __init__(
        self,
        sock: socket,
        operations_dict: dict,
        tis_api: TISApi,
    ):
        """Initialize the PacketReceiver."""
        self.socket = sock
        self.tis_api = tis_api

        # The dispatcher is responsible for acting on the parsed packet information
        # (e.g., firing events, setting ack signals).
        self.dispatcher = PacketDispatcher(self.tis_api, operations_dict)

        # This will hold the asyncio transport object once the connection is made.
        self.transport = None

    def connection_made(self, transport):
        """
        Callback executed by asyncio when the datagram endpoint is set up.
        """
        self.transport = transport
        _LOGGER.info("UDP connection made and listener is active.")

    def datagram_received(self, data, _):
        """
        Callback executed by asyncio every time a UDP datagram is received.

        :param data: The raw bytes of the received packet.
        :param addr: A tuple containing the sender's (IP, port).
        """
        try:
            # Convert the raw bytes into a list of integers.
            hex_list = bytes2hex(data, [])

            # Use the PacketExtractor to parse the byte list into a structured dictionary.
            info = PacketExtractor.extract_info(hex_list)

            # --- Dispatch the packet for processing ---
            # It is crucial to schedule the dispatcher as a new task in the Home Assistant
            # event loop. This prevents the datagram_received method from blocking,
            # ensuring the receiver is always ready for the next incoming packet.
            # TODO: create a task using asyncio instead of hass!
            asyncio.create_task(self.dispatcher.dispatch_packet(info))
            # self._hass.async_create_task(self.dispatcher.dispatch_packet(info))

        except Exception as e:
            # Catch any errors during parsing to prevent a single malformed packet
            # from crashing the entire listener.
            _LOGGER.error("Error processing received datagram: %s", e)
