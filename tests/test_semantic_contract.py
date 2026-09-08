from data_engine.contracts.constitution import DataConstitution
from evolution.semantic_models import SemanticContract


def test_semantic_contract_serialization():
    contract = SemanticContract(
        column="match_duration_ms",
        meaning="duration of a completed match",
        unit="milliseconds",
        data_type="integer",
        domain="gameplay telemetry",
        expected_range=[1000.0, 3600000.0],
        invariants=["must_be_non_negative"]
    )
    
    const = DataConstitution(
        dataset_id="test_ds",
        version="1.0",
        expected_schema=[],
        baseline_statistics={},
        quality_constraints={},
        semantic_contracts={"match_duration_ms": contract}
    )
    
    dump = const.model_dump()
    assert dump["semantic_contracts"]["match_duration_ms"]["unit"] == "milliseconds"
    assert dump["semantic_contracts"]["match_duration_ms"]["expected_range"] == [1000.0, 3600000.0]
