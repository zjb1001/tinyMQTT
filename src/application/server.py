import socket
import threading
import time
from typing import Optional, Dict
from ..protocol.flow import MessageFlow
from ..protocol.packet import MQTTPacket, PacketType

class MQTTServer:
    def __init__(self, port: int, host: str = ''):
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.running = False
        self.accept_thread: Optional[threading.Thread] = None
        self.client_flows: Dict[socket.socket, MessageFlow] = {}
        self.client_threads: Dict[socket.socket, threading.Thread] = {}
        self._lock = threading.Lock()

    def start(self):
        """启动MQTT服务器"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.running = True
            
            self.accept_thread = threading.Thread(target=self._accept_connections)
            self.accept_thread.daemon = True
            self.accept_thread.start()
            
            print(f"MQTT Server started on port {self.port}")
            
            # 保持主线程运行
            try:
                while self.running:
                    threading.Event().wait(1)
            except KeyboardInterrupt:
                self.stop()
                
        except Exception as e:
            print(f"Failed to start server: {e}")
            self.stop()

    def stop(self):
        """改进的停止方法"""
        print("\nShutting down server...")
        self.running = False
        
        # 关闭服务器socket以中断accept循环
        if self.socket:
            try:
                self.socket.close()
            except:
                pass

        # 停止所有客户端flow
        with self._lock:
            for client_socket, flow in self.client_flows.items():
                try:
                    flow.stop()
                except:
                    pass
                try:
                    client_socket.close()
                except:
                    pass

        # 等待所有客户端线程结束
        for thread in self.client_threads.values():
            if thread.is_alive():
                thread.join(timeout=1)

        # 清理资源
        self.client_flows.clear()
        self.client_threads.clear()
        
        if self.accept_thread and self.accept_thread.is_alive():
            self.accept_thread.join(timeout=1)
        
        print("Server stopped")

    def _accept_connections(self):
        """接受新的客户端连接"""
        while self.running:
            try:
                client_socket, address = self.socket.accept()
                print(f"New connection from {address}")
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket,)
                )
                client_thread.daemon = True
                with self._lock:
                    self.client_threads[client_socket] = client_thread
                client_thread.start()
            except:
                if self.running:
                    print("Accept error, server stopping...")
                break

    def handle_client(self, client_socket):
        """改进的客户端处理方法"""
        try:
            flow = MessageFlow(client_socket)
            with self._lock:
                self.client_flows[client_socket] = flow
            flow.start()
            
            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                packet = MQTTPacket.decode(data)
                if packet.packet_type == PacketType.CONNECT:
                    response = flow.handle_connect(packet)
                    if response:
                        client_socket.send(response.encode())
                elif packet.packet_type == PacketType.SUBSCRIBE:
                    # 发送订阅确认
                    ack = MQTTPacket(PacketType.SUBACK)
                    client_socket.send(ack.encode())
        except Exception as e:
            if self.running:
                print(f"Client handling error: {e}")
        finally:
            with self._lock:
                if client_socket in self.client_flows:
                    self.client_flows[client_socket].stop()
                    del self.client_flows[client_socket]
                if client_socket in self.client_threads:
                    del self.client_threads[client_socket]
            try:
                client_socket.close()
            except:
                pass