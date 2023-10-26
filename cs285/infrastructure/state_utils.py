import torch
import pickle

from State import State
from Trajectory import Trajectory


def create_trajectories(expert_file_path):
    """
    The expert data files are formatted such that each one is a list of demos of length n = 2.
    Each demo has batch_size observations, batch_size actions, batch_size next_observations, etc.
    We define that one demo is one trajectory (which is a standard definition if we assume that
    the expert data files ARE giving us n trajectories).
    Thus the ith state along a trajectory will be made of the obs, action, next_obs, reward, and
    done located at the ith index in their respective arrays.
    """
    with open(expert_file_path, "rb") as f:
        demos = pickle.load(f)
    trajectories = []
    batch_size = demos[0]["observation"].shape[0]
    for demo in demos:
        trajectory = Trajectory()
        for b in range(batch_size):
            state = State(
                demo["observation"][b],
                demo["action"][b],
                demo["next_observation"][b],
                demo["reward"][b],
            )
            trajectory.add_state(state)
        trajectories.append(trajectory)
    return trajectories


# FIXME: don't think this function is necessary now
def get_action(state, next_state):
    """
    TODO: Need to define what a state is lmao

    ideally its just (obs, action, next_obs, reward, done) but idk how trajectories are currently defined
    """
    return 0


def get_similar_states(trajectories):
    """
    params:
        trajectories: initial expert trajectories to aggregate
    returns:
        similar_states: list of states that are similar to each other. This is a list of
        tuples where the first element is the index of the trajectory and the second element is the index of the observation.
    """
    num_traj = len(trajectories)
    similar_states = []
    for i in range(num_traj):
        for j in range(i + 1, num_traj):
            i_states, j_states = trajectories[i].compare(trajectories[j])
            for k in range(len(i_states)):
                similar_states.extend([(i, i_states[k]), (j, j_states[k])])
    return similar_states


def get_state_variance(state, agent, n_iters=100):
    """
    Gets the variance of actions taken by our agent from a given state

    params:
        state: observation of the environment
        agent: provides action for each state
        n_iters: Number of actions to take from the state when determining the variance
    returns:
        variance: average variance of the states
    """
    actions = []
    for _ in range(n_iters):
        action = agent.get_action(state)
        actions.append(action)
    actions = torch.tensor(actions)
    return actions.var()


def get_state_collection_variance(similar_states, agent, n_iters=100):
    """
    Gets the average variance of actions taken by our agent from a list of
    given states that are similar to eachother

    params:
        similar_states: List of states that are similar to each other
        agent: provides action for each state
        n_iters: Number of actions to take from the state when determining the variance
    returns:
        variance: average variance of the states
    """
    total_variance = 0
    for state in similar_states:
        state_variance = get_state_variance(state, agent, n_iters)
        total_variance += state_variance
    average_variance = total_variance / len(similar_states)
    return average_variance
