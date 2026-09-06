import logging
from typing import List

from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic

from data_engine.ingestion.models import MatchEvent

logger = logging.getLogger(__name__)

class KafkaTelemetryProducer:
    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        self.bootstrap_servers = bootstrap_servers
        self.producer = Producer({"bootstrap.servers": self.bootstrap_servers})
        self.admin = AdminClient({"bootstrap.servers": self.bootstrap_servers})

    def create_topic_if_not_exists(
        self, topic_name: str, partitions: int = 3, replication_factor: int = 1
    ) -> None:
        """
        Creates a Kafka topic if it doesn't already exist.
        """
        metadata = self.admin.list_topics(timeout=10)
        if topic_name not in metadata.topics:
            logger.info(f"Topic {topic_name} does not exist. Creating...")
            new_topic = NewTopic(
                topic_name, num_partitions=partitions, replication_factor=replication_factor
            )
            fs = self.admin.create_topics([new_topic])
            for topic, f in fs.items():
                try:
                    f.result()  # The result itself is None
                    logger.info(f"Topic {topic} created")
                except Exception as e:
                    logger.error(f"Failed to create topic {topic}: {e}")
        else:
            logger.info(f"Topic {topic_name} already exists.")

    def _delivery_report(self, err, msg):
        """Called once for each message produced to indicate delivery result."""
        if err is not None:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")

    def publish_events(self, topic: str, events: List[MatchEvent]) -> int:
        """
        Publishes a list of events to Kafka.
        Returns the number of messages queued.
        """
        count = 0
        for event in events:
            # We use the event_id as the key to ensure consistent hashing to partitions
            payload = event.model_dump_json()
            self.producer.produce(
                topic=topic,
                key=event.event_id.encode('utf-8'),
                value=payload.encode('utf-8'),
                callback=self._delivery_report
            )
            count += 1
            
            # Poll occasionally to handle delivery callbacks
            if count % 1000 == 0:
                self.producer.poll(0)
                
        # Wait for any outstanding messages to be delivered
        self.producer.flush()
        return count
