from enum import Enum, auto

class PacketType(Enum):
    CONNECT = auto()
    CONNACK = auto()
    PUBLISH = auto()
    PUBACK = auto()
    SUBSCRIBE = auto()
    SUBACK = auto()
    PINGREQ = auto()
    PINGRESP = auto()
    DISCONNECT = auto()

class MQTTPacket:
    def __init__(self, packet_type: PacketType, topic: str = None, payload: bytes = None, keep_alive: int = 60):
        self.packet_type = packet_type
        self.topic = topic
        self.payload = payload
        self.keep_alive = keep_alive

    def encode(self) -> bytes:
        """改进的编码方法"""
        try:
            data = bytearray([self.packet_type.value])
            if self.topic:
                topic_bytes = self.topic.encode('utf-8')
                data.extend(len(topic_bytes).to_bytes(2, 'big'))
                data.extend(topic_bytes)
            if self.payload:
                if isinstance(self.payload, str):
                    payload_bytes = self.payload.encode('utf-8')
                else:
                    payload_bytes = self.payload
                data.extend(len(payload_bytes).to_bytes(2, 'big'))
                data.extend(payload_bytes)
            return bytes(data)
        except Exception as e:
            print(f"Encode error: {e}")
            return bytes([self.packet_type.value])

    @classmethod
    def decode(cls, data: bytes):
        """改进的解码方法"""
        try:
            packet_type = PacketType(data[0])
            pos = 1
            topic = None
            payload = None
            
            if len(data) > pos + 2:
                topic_len = int.from_bytes(data[pos:pos+2], 'big')
                pos += 2
                if topic_len > 0:
                    topic = data[pos:pos+topic_len].decode('utf-8')
                    pos += topic_len
                    
                    if len(data) > pos + 2:
                        payload_len = int.from_bytes(data[pos:pos+2], 'big')
                        pos += 2
                        if payload_len > 0:
                            payload = data[pos:pos+payload_len]
            
            return cls(packet_type, topic, payload)
        except Exception as e:
            print(f"Decode error: {e}")
            return cls(packet_type)