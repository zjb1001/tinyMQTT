import threading
import logging
from .server import MQTTServer
from ..protocol.packet import PacketType, MQTTPacket

class MQTTBroker(MQTTServer):
    def __init__(self, port: int, host: str = '', log_level=logging.INFO):
        super().__init__(port, host)
        self.topics = {}
        self.client_topics = {}
        self.topics_lock = threading.Lock()
        self.running = False  # 添加running状态变量
        
        # Configure logger
        self.logger = logging.getLogger('MQTTBroker')
        self.set_log_level(log_level)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def set_log_level(self, level):
        """Set the logger level
        Args:
            level: logging level (e.g., logging.DEBUG, logging.INFO)
        """
        self.logger.setLevel(level)

    def start(self):
        self.running = True
        super().start()
        self.logger.info("MQTT Broker started")

    def stop(self):
        self.running = False
        super().stop()
        self.logger.info("MQTT Broker stopped")

    def handle_client(self, client_socket):
        try:
            client_address = client_socket.getpeername()
            self.logger.info(f"New client connected from {client_address}")
            
            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                packet = MQTTPacket.decode(data)
                if packet.packet_type == PacketType.PUBLISH:
                    self.handle_publish(packet)
                    ack = MQTTPacket(PacketType.PUBACK)
                    client_socket.send(ack.encode())
                elif packet.packet_type == PacketType.SUBSCRIBE:
                    self.handle_subscribe(client_socket, packet)
                elif packet.packet_type == PacketType.PINGREQ:
                    resp = MQTTPacket(PacketType.PINGRESP)
                    client_socket.send(resp.encode())
                elif packet.packet_type == PacketType.DISCONNECT:
                    self.logger.info(f"Client {client_address} disconnected gracefully")
                    break
        except Exception as e:
            self.logger.error(f"Client handling error: {e}")
        finally:
            self.remove_client(client_socket)
            self.logger.info(f"Connection closed for client {client_address}")

    def handle_publish(self, packet):
        with self.topics_lock:
            self.logger.debug(f"Publishing to topic: {packet.topic}")
            self.logger.debug(f"Active topics: {list(self.topics.keys())}")
            
            if packet.topic in self.topics:
                # 直接使用原始数据转发，避免重新编码
                raw_data = packet.raw_data if hasattr(packet, 'raw_data') else packet.encode()
                
                for client in list(self.topics[packet.topic]):
                    try:
                        client.send(raw_data)
                        self.logger.debug(f"Raw message forwarded to subscriber for topic {packet.topic}")
                    except Exception as e:
                        self.logger.error(f"Failed to send to subscriber: {e}")
                        self.remove_client(client)

    def handle_subscribe(self, client_socket, packet):
        with self.topics_lock:
            try:
                if not packet.topic:
                    self.logger.warning("Invalid subscription: no topic specified")
                    return

                if packet.topic not in self.topics:
                    self.topics[packet.topic] = set()
                
                self.topics[packet.topic].add(client_socket)
                if client_socket not in self.client_topics:
                    self.client_topics[client_socket] = set()
                self.client_topics[client_socket].add(packet.topic)
                
                self.logger.debug(f"Client subscribed to {packet.topic}")
                self.logger.debug(f"Current topics: {list(self.topics.keys())}")
                self.logger.debug(f"Number of subscribers for {packet.topic}: {len(self.topics[packet.topic])}")
                
                ack = MQTTPacket(PacketType.SUBACK)
                client_socket.send(ack.encode())
            except Exception as e:
                self.logger.error(f"Subscription error: {e}")

    def remove_client(self, client_socket):
        with self.topics_lock:
            if client_socket in self.client_topics:
                for topic in self.client_topics[client_socket]:
                    if topic in self.topics:
                        self.topics[topic].discard(client_socket)
                del self.client_topics[client_socket]
        try:
            client_socket.close()
        except Exception as e:
            self.logger.error(f"Error closing client socket: {e}")