<<<<<<< HEAD
# tinymqtt
=======
=======
>>>>>>> master
# TinyMQTT Implementation

A lightweight MQTT protocol implementation with layered architecture.

## Architecture

The implementation follows a two-layer architecture:

### Protocol Layer
Handles the core MQTT protocol implementation:

1. Packet Processing
   - CONNECT/CONNACK packet handling
   - PUBLISH/PUBACK packet handling
   - SUBSCRIBE/SUBACK packet handling
   - UNSUBSCRIBE/UNSUBACK packet handling
   - PINGREQ/PINGRESP packet handling
   - DISCONNECT packet handling
   - QoS level support (0, 1, 2)
   - Message encoding/decoding

2. Flow Control
   - Session management
   - Keep-alive monitoring
   - Message queuing
   - Retry mechanism
   - QoS flow handling

### Application Layer
Provides high-level MQTT components:

1. MQTT Client
   - Connection management
   - Topic subscription
   - Message publishing
   - Auto-reconnect
   - Message callback handling

2. MQTT Server/Broker
   - Client connection handling
   - Topic subscription management
   - Message routing
   - Session persistence
   - Access control
   - Message retention

## Component Functions

### Protocol Layer Components

#### Packet Processor (`packet.py`)
```python
class PacketProcessor:
    - encode_packet(type, payload)
    - decode_packet(raw_data)
    - validate_packet(packet)
    - create_connack()
    - create_puback()
    - create_suback()
```

#### Flow Controller (`flow.py`)
```python
class FlowController:
    - handle_connect()
    - handle_publish()
    - handle_subscribe()
    - manage_qos()
    - track_session()
```

### Application Layer Components

#### MQTT Client (`client.py`)
```python
class MQTTClient:
    - connect(host, port)
    - disconnect()
    - publish(topic, message, qos)
    - subscribe(topic, qos)
    - unsubscribe(topic)
    - set_callback(callback_fn)
```

#### MQTT Broker (`broker.py`)
```python
class MQTTBroker:
    - start(port)
    - stop()
    - handle_client(client)
    - route_message(topic, message)
    - manage_subscriptions()
```

## Project Structure

```
tinyMQTT/
├── src/
│   ├── __init__.py
│   ├── protocol/
│   │   ├── __init__.py
│   │   ├── packet.py
│   │   └── flow.py
│   └── application/
│       ├── __init__.py
│       ├── client.py
│       ├── server.py
│       └── broker.py
└── examples/
    ├── broker.py
    ├── publisher.py
    └── subscriber.py
```

## Example Usage

### Using Make Commands
The project provides Make commands for easy service management:

1. Start the broker:
```bash
make broker
# or with specific options
make broker ARGS="--host localhost --port 1883 --log-level DEBUG"
```

2. Start a publisher:
```bash
make publisher
# or with specific options
make publisher ARGS="--host localhost --port 1883 --topic test/topic --message 'Hello MQTT!'"
```

3. Start a subscriber:
```bash
make subscriber
# or with specific options
make subscriber ARGS="--host localhost --port 1883 --topic test/topic"
```

### Available Broker Commands
When broker is running, you can use these commands:
- `help` - Show available commands
- `stop` - Stop the broker and exit
- `Ctrl+C` - Force stop the broker

### Direct Python Execution
Alternatively, you can run the services directly:

1. Start the broker:
```bash
python broker.py --port 1883
```

2. Start the publisher:
```bash
python publisher.py --host localhost --port 1883 --topic "test/topic" --message "Hello from publisher!"
```

3. Start the subscriber:
```bash
python subscriber.py --host localhost --port 1883 --topic "test/topic"
```