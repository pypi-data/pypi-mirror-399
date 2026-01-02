# etsi/watchdog/drift/factory.py

from .psi import psi_drift
from .ks import ks_drift
from .shap_drift import shap_drift
from .wasserstein import wasserstein_drift

# Internal registry for drift algorithms
_DRIFT_REGISTRY = {
    "psi": psi_drift,
    "ks": ks_drift,
    "shap": shap_drift,
    "wasserstein": wasserstein_drift
}

def register_drift_algorithm(name: str, func):
    """
    Register a custom drift detection algorithm dynamically.
    
    Args:
        name (str): The name of the algorithm (case-insensitive).
        func (callable): The function to execute.
    """
    _DRIFT_REGISTRY[name.lower()] = func
    print(f"[etsi-watchdog] Registered new algorithm: '{name}'")

def get_drift_function(algo: str):
    """
    Retrieve a drift function by name from the registry.
    """
    algo = algo.lower()
    if algo in _DRIFT_REGISTRY:
        return _DRIFT_REGISTRY[algo]
    else:
        available = ", ".join(_DRIFT_REGISTRY.keys())
        raise ValueError(f"Unsupported drift algorithm: '{algo}'. Available: {available}")
