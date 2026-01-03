import envpool
import jax
import numpy as np

import gxm

num_envs = 8
id = "Breakout-v5"

env_gxm = gxm.make("Envpool/" + id)

key = jax.random.key(0)
keys = jax.random.split(key, num_envs)

env_envpool = envpool.make(id, env_type="gym", num_envs=num_envs)

env_states, timesteps = jax.vmap(env_gxm.init)(keys)
obs, _ = env_envpool.reset()

for _ in range(10000):
    actions = np.random.randint(0, 2, num_envs)
    env_states, timesteps = jax.vmap(env_gxm.step)(keys, env_states, actions)
    obs, rewards, dones, truncations, infos = env_envpool.step(actions)

    print(dones, timesteps.done)
    assert np.allclose(rewards, timesteps.reward)
    assert np.allclose(dones, timesteps.done)
    assert np.allclose(truncations, timesteps.truncated)
    assert np.allclose(obs, timesteps.obs)
