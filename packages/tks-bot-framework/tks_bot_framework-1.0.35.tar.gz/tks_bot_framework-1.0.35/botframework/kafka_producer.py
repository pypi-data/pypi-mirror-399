from aiokafka import AIOKafkaProducer
import asyncio
import logging
import json

logger = logging.getLogger(__name__)

class KafkaProducerManager:
    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None

    async def start(self):
        """Start the Kafka producer."""
        if self.producer is None:
            self.producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers)
            await self.producer.start()
            logger.info("Kafka producer started.")

    async def stop(self):
        """Stop the Kafka producer."""
        if self.producer is not None:
            await self.producer.flush()  # Ensure all pending messages are sent
            await self.producer.stop()
            self.producer = None
            logger.info("Kafka producer stopped.")

    async def produce_message(self, topic_name: str, key: str, value: dict):
        """Send a message to the specified Kafka topic."""
        if self.producer is None:
            raise RuntimeError("Kafka producer is not started.")
        try:
            # Ensure the key and value are bytes
            key_bytes = key.encode("utf-8") if isinstance(key, str) else key
            value_bytes = json.dumps(value).encode("utf-8")
            await self.producer.send_and_wait(topic=topic_name, key=key_bytes, value=value_bytes)
            logger.info(f"Produced message to topic {topic_name}: {value}")
        except Exception as e:
            logger.error(f"Failed to produce message to topic {topic_name}: {e}")
            raise
