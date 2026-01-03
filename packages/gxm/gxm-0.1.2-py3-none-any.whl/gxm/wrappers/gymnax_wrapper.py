from typing import Any

import gymnax

from gxm.core import Environment


class GymnaxWrapper(gymnax.environments.environment.Environment):
    """A wrapper class for Gymnax environments."""

    env: Environment

    def __init__(self, env: Environment):
        self.env = env

    def reset(self, key: Any) -> Any:
        return None, self.env.reset(key)

    def step(self, key: Any, state: Any, action: Any) -> Any:
        next_state, reward, done, info = self.env.step(state, action)
        return next_state, reward, done, info

    def gxm_to_gymnax_space(self, gxm_space: Any) -> Any:
        """Convert a GXM space to a Gymnax space."""
        if gxm_space.__class__.__name__ == "Discrete":
            return gymnax.spaces.Discrete(gxm_space.n)
        elif gxm_space.__class__.__name__ == "Box":
            return gymnax.spaces.Box(
                low=gxm_space.low,
                high=gxm_space.high,
                shape=gxm_space.shape,
                dtype=gxm_space.dtype,
            )
        else:
            raise NotImplementedError(
                f"Conversion for {gxm_space.__class__.__name__} is not implemented."
            )
