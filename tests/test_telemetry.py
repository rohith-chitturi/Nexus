from data_engine.ingestion.generator import TelemetryGenerator


def test_deterministic_generation():
    """
    Verify that the synthetic generator produces deterministic output given a seed.
    """
    gen1 = TelemetryGenerator(seed=123)
    events1 = gen1.generate_events(5)
    
    gen2 = TelemetryGenerator(seed=123)
    events2 = gen2.generate_events(5)
    
    assert len(events1) == 5
    assert len(events2) == 5
    
    # Assert deterministic output
    for e1, e2 in zip(events1, events2):
        assert e1.event_id == e2.event_id
        assert e1.match_id == e2.match_id
        assert e1.latency_ms == e2.latency_ms

def test_different_seeds_produce_different_events():
    gen1 = TelemetryGenerator(seed=1)
    gen2 = TelemetryGenerator(seed=2)
    
    events1 = gen1.generate_events(1)
    events2 = gen2.generate_events(1)
    
    assert events1[0].event_id != events2[0].event_id

def test_model_serialization():
    gen = TelemetryGenerator(seed=42)
    event = gen.generate_events(1)[0]
    
    json_str = event.model_dump_json()
    assert "event_id" in json_str
    assert "match_id" in json_str
    assert "timestamp" in json_str
