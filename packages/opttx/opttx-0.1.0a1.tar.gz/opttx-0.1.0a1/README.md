# OptTx

> **Research Code**: Co-developed with Claude Code, Gemini CLI, Codex CLI, and Cursor. No guarantees provided. Use at your own risk.

JAX/Flax/Optax optimizer library for PINNs and second-order methods.

## Features

- **Multi-term objectives**: `Objective` with `TermSpec` for PINNs (PDE, BC, IC terms)
- **First-order optimizers**: Adam, SGD, AdamW, SOAP, MUON, Shampoo, L-BFGS
- **Second-order optimizers**: CGOptimizer (Fisher/GGN), CROptimizer (Hessian)
- **Acceleration methods**: TGS, NLTGCR, Anderson Acceleration (AA)
- **Graph neural networks**: GCN, GAT layers for node classification
- **Matrix-free curvature**: `build_hessian_matvec`, `build_fisher_matvec`
- **JIT-stable**: Works with `jax.jit` and `jax.lax.scan`

## Install

```bash
pip install opttx
```

For development:
```bash
pip install -e .[dev]
```

## Quickstart

### First-order optimizer

```python
import jax
import jax.numpy as jnp
from flax import linen as nn

from opttx import Adam, Objective, TermSpec, TrainState

# Define model
class MLP(nn.Module):
    @nn.compact
    def __call__(self, x):
        x = nn.Dense(32)(x)
        x = nn.relu(x)
        x = nn.Dense(1)(x)
        return x

# Define loss
def mse_loss(pred, batch):
    x, y = batch
    return jnp.mean((pred - y) ** 2)

# Create objective
term = TermSpec(name="mse", batch_key="data", loss_fn=mse_loss)
objective = Objective(terms=[term])

# Initialize
model = MLP()
params = model.init(jax.random.PRNGKey(0), jnp.ones((1, 3)))["params"]

state = TrainState(
    step=jnp.array(0),
    params=params,
    opt_state=None,
    apply_fn=lambda v, b: model.apply({"params": v["params"]}, b[0]),
)

# Create optimizer and train
optimizer = Adam(objective, learning_rate=1e-3)
state = optimizer.init(state)

batch = {"data": (jnp.ones((8, 3)), jnp.zeros((8, 1)))}
state, metrics = optimizer.step(state, batch)
print(f"Loss: {metrics['loss']}")
```

### Second-order optimizer (CR + Hessian)

```python
from opttx import CROptimizer

optimizer = CROptimizer(
    objective,
    learning_rate=1.0,
    damping=1e-3,
    cr_iters=10,
    curvature_type="hessian",  # or "fisher"
)
state = optimizer.init(state)
state, metrics = optimizer.step(state, batch)
```

### Multi-term objective (PINNs)

```python
def pde_loss(pred, batch):
    return jnp.mean(pred ** 2)

def bc_loss(pred, batch):
    return jnp.mean(pred ** 2)

pde_term = TermSpec(name="pde", batch_key="x_pde", loss_fn=pde_loss)
bc_term = TermSpec(name="bc", batch_key="x_bc", loss_fn=bc_loss)

objective = Objective(
    terms=[pde_term, bc_term],
    loss_weights={"pde": 1.0, "bc": 0.1},
)

batch = {
    "x_pde": jnp.ones((100, 2)),
    "x_bc": jnp.ones((20, 2)),
}
```

## API Reference

### Optimizers

| Optimizer | Description |
|-----------|-------------|
| `Adam` | Adam optimizer |
| `SGD` | SGD with momentum |
| `AdamW` | Adam with weight decay |
| `SOAP` | Second-order approximation |
| `MUON` | Momentum with orthogonalization |
| `Shampoo` | Shampoo preconditioner |
| `LBFGSOptimizer` | L-BFGS quasi-Newton |
| `CGOptimizer` | Conjugate Gradient (Fisher/GGN) |
| `CROptimizer` | Conjugate Residual (Hessian) |
| `TGSOptimizer` | TGS acceleration |
| `TGSAccelerator` | TGS wrapper for any optimizer |
| `AAAccelerator` | Anderson Acceleration wrapper |
| `NLTGCROptimizer` | Nonlinear truncated GCR |

### Curvature

| Function | Description |
|----------|-------------|
| `build_hessian_matvec` | Matrix-free Hessian-vector product |
| `build_fisher_matvec` | Matrix-free Fisher/GGN-vector product |
| `build_damped_matvec` | Add damping: (H + λI)v |

### Solvers

| Function | Description |
|----------|-------------|
| `cg_solve` | Conjugate Gradient solver |
| `cr_solve` | Conjugate Residual solver |
| `tgs_solve_fori` | TGS solver (JIT-compatible) |
| `nltgcr_solve_fori` | NLTGCR solver (JIT-compatible) |

### Models

| Model | Description |
|-------|-------------|
| `GCN` | Graph Convolutional Network |
| `GCNLayer` | Single GCN layer |
| `GAT` | Graph Attention Network |
| `GATLayer` | Single GAT layer |
| `normalize_adjacency` | Symmetric adjacency normalization |

## Design Constraints

- `state.step` must be a scalar `jax.Array` (never Python int)
- Metrics have static string keys and scalar values
- Must include `"loss"` key in metrics
- Multi-term + `batch_stats` is not supported

## License

MIT
