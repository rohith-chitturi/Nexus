from pydantic import BaseModel


class DriftPolicy(BaseModel):
    """
    Configurable thresholds for detecting data evolution.
    Defaults represent engineering baselines.
    """
    # Allowed relative change in mean (e.g., 0.10 means 10% change is allowed)
    relative_mean_change_threshold: float = 0.10
    
    # Allowed relative change in variance
    relative_variance_change_threshold: float = 0.20
    
    # Allowed absolute delta in null rate (e.g., 0.05 means +5% nulls)
    null_rate_delta_threshold: float = 0.05
    
    # Allowed absolute delta in cardinality count
    cardinality_delta_threshold: int = 100

    @classmethod
    def default_policy(cls) -> "DriftPolicy":
        return cls()
