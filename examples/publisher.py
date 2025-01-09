import argparse
import sys
import os
import time

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.application.client import MQTTClient

def main():
    parser = argparse.ArgumentParser(description='MQTT Publisher')
    parser.add_argument('--host', default='localhost',
                        help='Broker host')
    parser.add_argument('--port', type=int, default=1883,
                        help='Broker port')
    parser.add_argument('--topic', required=True,
                        help='Topic to publish to')
    parser.add_argument('--message', required=True,
                        help='Message to publish')
    parser.add_argument('--interval', type=int, default=5,
                        help='Publishing interval in seconds')

    args = parser.parse_args()
    client = MQTTClient(args.host, args.port)
    
    if not client.connect():
        print("Failed to connect to broker")
        return

    print(f"Connected to broker at {args.host}:{args.port}")

    try:
        while True:
            if client.publish(args.topic, args.message):
                print(f"Published message to {args.topic}")
            else:
                print("Failed to publish message")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        pass

    client.disconnect()

if __name__ == '__main__':
    main()