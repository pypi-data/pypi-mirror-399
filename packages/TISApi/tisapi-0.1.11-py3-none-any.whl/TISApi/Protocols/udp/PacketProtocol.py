import socket as Socket

from TISApi.api import TISApi

# Import all the necessary components for the TIS protocol.
from TISApi.Protocols.udp.AckCoordinator import AckCoordinator
from TISApi.Protocols.udp.PacketReceiver import PacketReceiver
from TISApi.Protocols.udp.PacketSender import PacketSender

# Import the specific handler functions for different types of received packets.
from .PacketHandlers.ControlResponseHandler import handle_control_response
from .PacketHandlers.DiscoveryFeedbackHandler import handle_discovery_feedback
from .PacketHandlers.UpdateResponseHandler import handle_update_response

# --- Packet Routing Table ---
# This dictionary is the core of the packet dispatching logic. It maps a packet's
# operation code (as a tuple) to the specific function that should handle it.
# This makes the system easy to extend with new packet types.
OPERATIONS_DICT = {
    # Response to a control command (on/off).
    (0x00, 0x32): handle_control_response,
    # A device responding to a discovery broadcast.
    (0x00, 0x0F): handle_discovery_feedback,
    # Response to a status update request.
    (0x00, 0x34): handle_update_response,
}


class PacketProtocol:
    """
    The main protocol class that orchestrates the entire communication system.

    This class assembles the sender, receiver, and acknowledgement coordinator.
    It's the top-level object that asyncio's datagram endpoint interacts with,
    delegating the actual protocol logic to its specialized components.
    """

    def __init__(self, socket: Socket.socket, udp_ip, udp_port, tis_api: TISApi):
        """Initializes and wires together all protocol components."""
        self.udp_ip = udp_ip
        self.udp_port = udp_port
        self.socket = socket
        self.tis_api = tis_api

        # --- Instantiate the core components of the protocol ---

        # The coordinator manages asyncio.Events for matching sent packets with received acks.
        self.coordinator = AckCoordinator()

        # The sender handles the logic for sending packets, including retries and debouncing.
        self.sender = PacketSender(
            sock=self.socket,
            coordinator=self.coordinator,
            udp_ip=self.udp_ip,
            udp_port=self.udp_port,
        )

        # The receiver handles the logic for listening and parsing incoming packets.
        # It's given the OPERATIONS_DICT to know how to dispatch them.
        self.receiver = PacketReceiver(self.socket, OPERATIONS_DICT, self.tis_api)

        # --- Delegate asyncio's protocol methods to the receiver ---
        # This is a clean design pattern. When asyncio calls `connection_made` or
        # `datagram_received` on this PacketProtocol instance, the calls are
        # forwarded directly to the PacketReceiver, which contains the actual implementation.
        self.connection_made = self.receiver.connection_made
        self.datagram_received = self.receiver.datagram_received
