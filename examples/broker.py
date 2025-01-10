import argparse
import sys
import os
import signal
import threading
import logging

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.application.broker import MQTTBroker

def command_listener(broker):
    """监听命令行输入"""
    logger = logging.getLogger('CommandListener')
    logger.info("Command listener started. Type 'help' for available commands.")
    
    while True:  # 改为无限循环，不依赖broker.running
        try:
            command = input().strip().lower()
            if command == 'stop':
                logger.info("Stopping broker via command...")
                broker.stop()
                break

            elif command == 'help':
                logger.info("Available commands:")
                logger.info("  stop  - Stop the broker and exit")
                logger.info("  help  - Show this help message")

            elif command:
                logger.warning(f"Unknown command: {command}")
                logger.info("Type 'help' for available commands")
                
        except (EOFError, KeyboardInterrupt):
            logger.info("Received interrupt signal in command listener")
            broker.stop()
            break

def main():
    parser = argparse.ArgumentParser(description='MQTT Broker')
    parser.add_argument('--host', default='',
                        help='Host to bind to')
    parser.add_argument('--port', type=int, default=1883,
                        help='Port to run the broker on')
    parser.add_argument('--log-level', default='INFO',
                        help='Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = getattr(logging, args.log_level.upper(), logging.INFO)
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    broker = MQTTBroker(args.port, args.host, log_level=log_level)
    
    def signal_handler(sig, frame):
        logging.info("Stopping broker...")
        broker.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)

    # 创建命令监听线程
    cmd_thread = threading.Thread(target=command_listener, args=(broker,))
    cmd_thread.daemon = True  # 改为非守护线程
    
    # 启动命令监听线程
    cmd_thread.start()
    
    # 启动broker
    logging.info(f"Starting MQTT broker on {args.host or '*'}:{args.port}")
    
    try:
        broker.start()  # broker启动
    except KeyboardInterrupt:
        logging.info("Received keyboard interrupt")
    finally:
        broker.stop()  # 确保broker停止
        cmd_thread.join(timeout=1)  # 等待命令线程结束，设置超时
        logging.info("Broker shutdown complete")

if __name__ == '__main__':
    main()