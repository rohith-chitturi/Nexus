import json
import logging
import os
from typing import List

import pyarrow as pa
import pyarrow.parquet as pq
from confluent_kafka import Consumer, KafkaError, KafkaException

from data_engine.ingestion.models import MatchEvent

logger = logging.getLogger(__name__)

class KafkaTelemetryConsumer:
    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        group_id: str = "nexus_ingestion_group",
        lake_path: str = "datasets/raw/match_events",
    ):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.lake_path = lake_path
        self.consumer = Consumer(
            {
                "bootstrap.servers": self.bootstrap_servers,
                "group.id": self.group_id,
                "auto.offset.reset": "earliest",
            }
        )

    def consume_batch(self, topic: str, batch_size: int = 1000, timeout_ms: int = 5000) -> List[MatchEvent]:
        self.consumer.subscribe([topic])
        events = []
        
        # Pull messages
        messages = self.consumer.consume(num_messages=batch_size, timeout=timeout_ms / 1000.0)
        
        for msg in messages:
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logger.debug(f"Reached end of partition {msg.partition()}")
                else:
                    logger.error(f"Kafka error: {msg.error()}")
                    raise KafkaException(msg.error())
            else:
                try:
                    payload = json.loads(msg.value().decode("utf-8"))
                    events.append(MatchEvent(**payload))
                except Exception as e:
                    logger.error(f"Failed to parse message: {e}")
                    
        return events

    def write_to_parquet(self, events: List[MatchEvent]) -> str:
        """
        Writes a batch of events to the Parquet Data Lake partitioned by event_date.
        """
        if not events:
            return ""

        # Convert to pyarrow table
        data = {
            "event_id": [e.event_id for e in events],
            "timestamp": [e.timestamp for e in events],
            "match_id": [e.match_id for e in events],
            "player_id": [e.player_id for e in events],
            "event_type": [e.event_type for e in events],
            "latency_ms": [e.latency_ms for e in events],
            "region": [e.region for e in events],
            "game_version": [e.game_version for e in events],
            # Add partition column
            "event_date": [e.timestamp.strftime("%Y-%m-%d") for e in events],
        }
        table = pa.Table.from_pydict(data)
        
        os.makedirs(self.lake_path, exist_ok=True)
        
        # Write dataset using pyarrow partitioned writing
        pq.write_to_dataset(
            table,
            root_path=self.lake_path,
            partition_cols=["event_date"],
            existing_data_behavior="overwrite_or_ignore"
        )
        return self.lake_path

    def close(self):
        self.consumer.close()
