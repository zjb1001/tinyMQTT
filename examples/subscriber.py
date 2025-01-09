import argparse
import sys
import os

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.application.client import MQTTClient

def message_handler(topic: str, payload: bytes):
    print(f"Received message on {topic}: {payload.decode()}")

def main():
    parser = argparse.ArgumentParser(description='MQTT Subscriber')
    parser.add_argument('--host', default='localhost',
                        help='Broker host')
    parser.add_argument('--port', type=int, default=1883,
                        help='Broker port')
    parser.add_argument('--topic', required=True,
                        help='Topic to subscribe to')
    
    args = parser.parse_args()
    client = MQTTClient(args.host, args.port)
    
    if not client.connect():
        print("Failed to connect to broker")
        return

    print(f"Connected to broker at {args.host}:{args.port}")
    
    if client.subscribe(args.topic, message_handler):
        print(f"Subscribed to {args.topic}")
        try:
            input("Press Enter to exit...\n")
        except KeyboardInterrupt:
            pass
    else:
        print("Failed to subscribe")

    client.disconnect()

if __name__ == '__main__':
    main()