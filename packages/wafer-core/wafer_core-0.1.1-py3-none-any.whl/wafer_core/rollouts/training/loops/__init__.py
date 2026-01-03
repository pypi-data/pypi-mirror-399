"""Training loops for SFT and RL."""

from wafer_core.rollouts.training.loops.rl_loop import run_rl_training
from wafer_core.rollouts.training.loops.sft_loop import run_sft_training

__all__ = [
    "run_sft_training",
    "run_rl_training",
]
