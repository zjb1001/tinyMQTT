import socket
from typing import Callable
from ..protocol.flow import MessageFlow
from ..protocol.packet import MQTTPacket, PacketType

class MQTTClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.socket = None
        self.flow = None

    def connect(self) -> bool:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.flow = MessageFlow(self.socket)
            packet = MQTTPacket(PacketType.CONNECT)
            self.socket.send(packet.encode())
            self.flow.start()
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def publish(self, topic: str, message: str) -> bool:
        if not self.flow:
            return False
        return self.flow.publish(topic, message.encode())

    def subscribe(self, topic: str, callback: Callable[[str, bytes], None]) -> bool:
        if not self.flow:
            return False
        return self.flow.subscribe(topic, callback)

    def disconnect(self):
        if self.flow:
            self.flow.stop()
        if self.socket:
            try:
                packet = MQTTPacket(PacketType.DISCONNECT)
                self.socket.send(packet.encode())
                self.socket.close()
            except:
                pass