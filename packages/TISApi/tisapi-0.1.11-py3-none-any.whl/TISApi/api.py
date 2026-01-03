# Import necessary libraries and modules.
import asyncio
import logging
import socket

from TISApi.DiscoveryHelpers import DEVICE_APPLIANCES

# Import TIS API protocol setup and handlers.
from TISApi.Protocols import setup_udp_protocol
from TISApi.Protocols.udp.ProtocolHandler import (
    TISPacket,
    TISProtocolHandler,
)

_LOGGER = logging.getLogger(__name__)


class TISApi:
    """Manages communication with TIS devices over UDP for Home Assistant."""

    def __init__(
        self,
        port: int,
        domain: str,
        devices_dict: dict,
        host: str = "0.0.0.0",  # Default to listen on all available network interfaces.
    ):
        """Initialize the TIS API handler."""
        # Network configuration.
        self.host = host
        self.port = port
        self.event_queue = asyncio.Queue()
        self.data = {
            "discovered_devices": [],
            "devices": [],
        }

        # Create a UDP socket.
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Will hold the asyncio transport and protocol instances after connection.
        self.protocol = None
        self.transport = None

        self.domain = domain  # The integration's domain (e.g., 'tis_control').

        # Dictionaries to hold device information.
        self.config_entries = {}
        self.devices_dict = devices_dict  # Maps device type codes to names.

        # Pre-generate the discovery packet to be broadcasted for finding devices.
        self.discovery_packet: TISPacket = (
            TISProtocolHandler.generate_discovery_packet()
        )

    async def consume_events(self):
        """A generator that yields events as they arrive."""
        while True:
            # Wait until an item is available
            event = await self.event_queue.get()
            try:
                yield event
            finally:
                self.event_queue.task_done()

    async def connect(self):
        """Establish the UDP connection and start listening for devices."""
        try:
            # Set up the asyncio UDP protocol endpoint. This starts listening for incoming packets.
            self.transport, self.protocol = await setup_udp_protocol(
                sock=self.sock,
                udp_ip=self.host,
                udp_port=self.port,
                tis_api=self,
            )
        except Exception as e:
            # Log and raise an error if the connection fails.
            _LOGGER.error("Error connecting to TIS API %s", e)
            raise ConnectionError from e

    async def scan_devices(self, broadcast_attempts=10):
        """Scan the network for TIS devices by broadcasting a discovery packet."""

        # Broadcast the discovery packet multiple times for reliability, as UDP is connectionless.
        for _ in range(broadcast_attempts):
            await self.protocol.sender.broadcast_packet(self.discovery_packet)
            # Wait for a short period to allow devices on the network time to respond.
            await asyncio.sleep(1)

        # Process the raw data from devices that responded to the discovery broadcast.
        for device in self.data["discovered_devices"]:
            self.data["devices"].append(
                {
                    "device_id": device["device_id"],
                    "device_type_code": device["device_type"],
                    # Look up the human-readable device name using the device type code.
                    "device_type_name": self.devices_dict.get(
                        tuple(device["device_type"]), tuple(device["device_type"])
                    ),
                    # Format the source IP address into a standard string format (e.g., "192.168.1.10").
                    "gateway": ".".join(map(str, device["source_ip"])),
                }
            )

    async def get_entities(self, platform: str):
        """Get a list of appliances (entities) for a specific Home Assistant platform (e.g., 'light', 'switch')."""
        # Load the list of devices discovered during the scan.
        devices = self.data["devices"]

        # Parse the device list to generate a structured dictionary of appliances.
        appliances = self.parse_saved_devices(devices)
        _LOGGER.warning(
            "appliances for platform %s: %s",
            str(platform),
            str(appliances.get(platform, [])),
        )

        # Return only the appliances that match the requested platform.
        return appliances.get(platform, [])

    def parse_saved_devices(self, devices: list[dict]):
        """Convert the saved device list into a structured format usable by Home Assistant."""
        # This dictionary will be structured by platform: {'light': [...], 'switch': [...]}.
        appliances = {}

        # Iterate over each discovered device.
        for device in devices:
            # Look up what kind of entities (appliances) this device type supports.
            device_appliances = DEVICE_APPLIANCES.get(
                tuple(device["device_type_code"]), None
            )

            # If the device type is known and supports appliances...
            if device_appliances:
                # Iterate over the platforms (e.g., 'light', 'climate') supported by this device.
                for platform, count in device_appliances["appliances"].items():
                    # If this is the first time we've seen this platform, initialize an empty list.
                    if platform not in appliances:
                        appliances[platform] = []

                    # Create an entity for each channel the device has for this platform.
                    for i in range(1, count + 1):
                        appliance = {
                            "name": f"{str(device['device_id'])} {platform} channel{i}",
                            "device_id": device["device_id"],
                            "device_type_name": device["device_type_name"],
                            "gateway": device["gateway"],
                            "channels": [
                                {
                                    "Output": i,  # The specific channel number for this entity.
                                }
                            ],
                            "is_protected": False,
                        }
                        # Add the fully-formed appliance dictionary to the list for its platform.
                        appliances[platform].append(appliance)

        return appliances
