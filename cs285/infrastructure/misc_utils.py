import time
from pathlib import Path

import torch

from constants import *


def from_numpy(data):
    if isinstance(data, dict):
        return {k: from_numpy(v) for k, v in data.items()}
    data = torch.from_numpy(data)
    if data.dtype == torch.float64:
        data = data.float()
    return data.to(DEVICE)


def to_numpy(tensor):
    if isinstance(tensor, dict):
        return {k: to_numpy(v) for k, v in tensor.items()}
    return tensor.to("cpu").detach().numpy()


def get_env(env_name):
    env_mapper = {
        "cartpole": "CartPole-v1",
        "ant": "Ant-v4",
        "pendulum": "Pendulum-v1",
        "inv_pend": "InvertedPendulum-v4",
        "lander": "LunarLander-v2",
        "hopper": "Hopper-v4",
    }
    return env_mapper[env_name]


def save_networks(using_demos, env_name, agent):
    extension = "with_demos" if using_demos else "from_scratch"
    data_path = Path(f"cs285/data/{env_name}/{int(time.time())}_{extension}/")
    data_path.mkdir(parents=True, exist_ok=True)

    agent.q_net.save(data_path / "q_net.pt")
    agent.target_net.save(data_path / "target_net.pt")

    return data_path
