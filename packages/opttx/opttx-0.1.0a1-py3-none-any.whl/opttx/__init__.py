"""OptTx: JAX/Flax/Optax optimizer library for PINNs and second-order methods."""

from .objective import Objective
from .optimizers import (
    OptaxOptimizer,
    Adam,
    SGD,
    AdamW,
    SOAP,
    Shampoo,
    MUON,
    LBFGSOptimizer,
    CGOptimizer,
    CROptimizer,
    NLTGCROptimizer,
    CrossBatchNLTGCROptimizer,
    TGSOptimizer,
    TGSAccelerator,
    AAAccelerator,
)
from .state import TrainState
from .terms import TermSpec
from .curvature import build_hessian_matvec, build_fisher_matvec, build_damped_matvec
from .solvers.cg import cg_solve
from .solvers.cr import cr_solve
from .solvers.tgs import tgs_solve_fori
from .solvers.nltgcr import nltgcr_solve_fori

__version__ = "0.1.0a1"

__all__ = [
    # First-order optimizers
    "OptaxOptimizer",
    "Adam",
    "SGD",
    "AdamW",
    "SOAP",
    "Shampoo",
    "MUON",
    # Quasi-Newton optimizers
    "LBFGSOptimizer",
    # Second-order optimizers
    "CGOptimizer",
    "CROptimizer",
    "NLTGCROptimizer",
    "CrossBatchNLTGCROptimizer",
    # First-order accelerated
    "TGSOptimizer",
    "TGSAccelerator",
    "AAAccelerator",
    # Curvature matvecs
    "build_hessian_matvec",
    "build_fisher_matvec",
    "build_damped_matvec",
    # Solvers
    "cg_solve",
    "cr_solve",
    "tgs_solve_fori",
    "nltgcr_solve_fori",
    # Core
    "Objective",
    "TermSpec",
    "TrainState",
    "__version__",
]
