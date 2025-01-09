import threading
import time
from typing import Callable, Optional
from .packet import MQTTPacket, PacketType

class MessageFlow:
    def __init__(self, socket=None):
        self.socket = socket
        self.running = False
        self.callbacks = {}
        self.keep_alive_interval = 30
        self._receiver_thread = None
        self._keep_alive_thread = None

    def set_socket(self, socket):
        """设置新的socket连接"""
        self.socket = socket

    def start(self):
        if not self.socket:
            raise RuntimeError("Socket not set")
        self.running = True
        self._receiver_thread = threading.Thread(target=self._receive_loop)
        self._keep_alive_thread = threading.Thread(target=self._keep_alive_loop)
        self._receiver_thread.daemon = True
        self._keep_alive_thread.daemon = True
        self._receiver_thread.start()
        self._keep_alive_thread.start()

    def stop(self):
        self.running = False
        if self._receiver_thread:
            self._receiver_thread.join()
        if self._keep_alive_thread:
            self._keep_alive_thread.join()

    def publish(self, topic: str, payload: bytes) -> bool:
        packet = MQTTPacket(PacketType.PUBLISH, topic=topic, payload=payload)
        self.socket.send(packet.encode())
        # Wait for acknowledgment
        try:
            ack = self._receive_packet()
            return ack and ack.packet_type == PacketType.PUBACK
        except:
            return False

    def handle_connect(self, packet: 'MQTTPacket') -> 'MQTTPacket':
        """处理连接请求"""
        if packet.packet_type == PacketType.CONNECT:
            return MQTTPacket(PacketType.CONNACK)
        return None

    def subscribe(self, topic: str, callback: Callable[[str, bytes], None]) -> bool:
        """修复的订阅方法"""
        try:
            self.callbacks[topic] = callback  # 先注册回调
            packet = MQTTPacket(PacketType.SUBSCRIBE, topic=topic)
            self.socket.send(packet.encode())
            # 等待订阅确认
            for _ in range(3):  # 重试3次
                data = self.socket.recv(1024)
                if data:
                    ack = MQTTPacket.decode(data)
                    if ack.packet_type == PacketType.SUBACK:
                        print(f"Successfully subscribed to {topic}")
                        return True
            return False
        except Exception as e:
            print(f"Subscribe error: {e}")
            if topic in self.callbacks:
                del self.callbacks[topic]
            return False

    def _receive_packet(self) -> Optional[MQTTPacket]:
        try:
            data = self.socket.recv(1024)
            if data:
                return MQTTPacket.decode(data)
        except:
            pass
        return None

    def _receive_loop(self):
        while self.running:
            try:
                packet = self._receive_packet()
                if packet:
                    self._handle_packet(packet)
            except Exception as e:
                print(f"Receive error: {e}")
                break

    def _handle_packet(self, packet: MQTTPacket):
        """改进的包处理方法"""
        try:
            if packet.packet_type == PacketType.PUBLISH and packet.topic and packet.payload:
                print(f"Received PUBLISH for topic: {packet.topic}")
                if packet.topic in self.callbacks:
                    callback = self.callbacks[packet.topic]
                    if callback:
                        try:
                            callback(packet.topic, packet.payload)
                        except Exception as e:
                            print(f"Callback error: {e}")
            elif packet.packet_type == PacketType.PINGREQ:
                self._send_ping_response()
            elif packet.packet_type == PacketType.SUBACK:
                print("Subscription acknowledged by broker")
        except Exception as e:
            print(f"Packet handling error: {e}")

    def _keep_alive_loop(self):
        while self.running:
            try:
                ping = MQTTPacket(PacketType.PINGREQ)
                self.socket.send(ping.encode())
                time.sleep(self.keep_alive_interval)
            except:
                break

    def _send_ping_response(self):
        try:
            resp = MQTTPacket(PacketType.PINGRESP)
            self.socket.send(resp.encode())
        except:
            pass