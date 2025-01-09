
.PHONY: broker subscriber publisher clean help

PYTHON=python3
PORT=1883
HOST=localhost
TOPIC=test/topic
MESSAGE="Hello MQTT"
INTERVAL=5

help:
	@echo "MQTT Example Commands:"
	@echo "  make broker     - Start MQTT broker"
	@echo "  make subscriber - Start MQTT subscriber"
	@echo "  make publisher  - Start MQTT publisher"
	@echo ""
	@echo "Options (can be overridden):"
	@echo "  PORT=$(PORT)"
	@echo "  HOST=$(HOST)"
	@echo "  TOPIC=$(TOPIC)"
	@echo "  MESSAGE=$(MESSAGE)"
	@echo "  INTERVAL=$(INTERVAL)"
	@echo ""
	@echo "Example:"
	@echo "  make broker PORT=8883"
	@echo "  make subscriber TOPIC=my/topic"
	@echo "  make publisher TOPIC=my/topic MESSAGE='Hello World'"

broker:
	$(PYTHON) broker.py --port $(PORT) --host $(HOST)

subscriber:
	$(PYTHON) subscriber.py --host $(HOST) --port $(PORT) --topic $(TOPIC)

publisher:
	$(PYTHON) publisher.py --host $(HOST) --port $(PORT) --topic $(TOPIC) --message $(MESSAGE) --interval $(INTERVAL)

clean:
	find .. -type d -name "__pycache__" -exec rm -r {} +
	find .. -type f -name "*.pyc" -delete