from evaluation.drift_evaluator import DriftEvaluator


def test_drift_evaluator():
    evaluator = DriftEvaluator()
    results = evaluator.run_all()
    
    tp = 0
    fn = 0
    
    for r in results:
        if r["correct"]:
            tp += 1
        else:
            fn += 1
            
    # Assert deterministic detection of all ground-truth scenarios
    assert fn == 0, f"Missed detection in scenarios: {[r['scenario'] for r in results if not r['correct']]}"
    assert tp == 5
    
    # Calculate Precision and Recall (simplified here as we only inject positive scenarios)
    precision = tp / (tp + 0) # No FP in this specific suite
    recall = tp / (tp + fn)
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    assert precision == 1.0
    assert recall == 1.0
    assert f1 == 1.0
