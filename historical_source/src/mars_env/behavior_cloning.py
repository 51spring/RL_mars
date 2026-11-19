"""Behaviour-cloning start for PPO (proposal p.10 alternative; decision_project.md 34).

1. Roll the rule policy through the same training environments PPO uses (ChannelCycler, train split, shaped and
   scaled reward). For the learned channels the expert action is the rule's own action; the other channels come
   from the rule or the frozen networks exactly as during PPO training.
2. Fit the policy head to the rule's actions with label smoothing over the feasible (unmasked) actions, so the
   start keeps a small exploration mass instead of a deterministic copy, and fit the value head to the rule's
   Monte Carlo returns (gamma = 1) so the first PPO updates do not start from a random critic.
PPO then continues from this network.
"""
import numpy as np

from .policies import CHANNEL_SIZES


def smoothed_targets(expert, masks, sizes, smoothing):
    """Per-channel target distributions: 1 - smoothing on the expert action, the rest spread over the other
    feasible actions of that channel (all of it on the expert when it is the only feasible action)."""
    masks = np.asarray(masks, dtype=bool)
    expert = np.asarray(expert, dtype=np.int64).reshape(len(masks), -1)
    if not 0 <= smoothing < 1:
        raise ValueError("Label smoothing must be in [0, 1)")
    targets, offset = [], 0
    for index, size in enumerate(sizes):
        mask = masks[:, offset:offset + size]
        chosen = expert[:, index]
        if not mask[np.arange(len(chosen)), chosen].all():
            raise ValueError("Expert action outside the feasible mask")
        others = mask.copy()
        others[np.arange(len(chosen)), chosen] = False
        count = others.sum(axis=1, keepdims=True)
        spread = np.where(count > 0, smoothing / np.maximum(count, 1), 0.0)
        target = others * spread
        target[np.arange(len(chosen)), chosen] = np.where(count[:, 0] > 0, 1 - smoothing, 1.0)
        targets.append(target)
        offset += size
    return targets


def returns_to_go(rewards, dones):
    """Undiscounted reward-to-go within each episode (gamma = 1, as in training)."""
    out, running = np.zeros(len(rewards)), 0.0
    for i in range(len(rewards) - 1, -1, -1):
        running = rewards[i] + (0.0 if dones[i] else running)
        out[i] = running
    return out


def collect_worker(job):
    """One worker: complete seasons of the rule policy in a ChannelCycler at the given rank."""
    config, learn, frozen, rank, n_envs, seasons, reduction_probability = job
    from .training_env import ChannelCycler
    env = ChannelCycler(config, learn=learn, frozen=frozen, rank=rank, n_envs=n_envs,
                        reduction_probability=reduction_probability)
    obs_list, mask_list, expert_list, reward_list, done_list = [], [], [], [], []
    try:
        for _ in range(seasons):
            observation, _ = env.reset()
            while True:
                full_mask = super(ChannelCycler, env).action_masks()
                combined = env._policy().action(observation, full_mask, env.rules)
                expert = [int(combined[channel]) for channel in learn]
                obs_list.append(np.asarray(observation, dtype=np.float32))
                mask_list.append(env.action_masks().astype(bool))
                expert_list.append(expert)
                observation, reward, terminated, truncated, _ = env.step(expert if len(expert) > 1 else expert[0])
                reward_list.append(float(reward))
                done_list.append(bool(terminated or truncated))
                if terminated or truncated:
                    break
    finally:
        env.close()
    return (np.asarray(obs_list), np.asarray(mask_list), np.asarray(expert_list, dtype=np.int64),
            np.asarray(reward_list), np.asarray(done_list))


def collect(config, learn, frozen, *, seasons, n_envs, reduction_probability, pool):
    per_worker = -(-seasons // n_envs)
    jobs = [(config, tuple(learn), tuple(frozen), rank, n_envs, per_worker, reduction_probability)
            for rank in range(n_envs)]
    parts = list(pool.map(collect_worker, jobs))
    obs, masks, expert, rewards, dones = (np.concatenate([p[i] for p in parts]) for i in range(5))
    returns = np.concatenate([returns_to_go(p[3], p[4]) for p in parts])
    return {"obs": obs, "masks": masks, "expert": expert, "returns": returns,
            "seasons": per_worker * n_envs, "steps": len(obs)}


def class_weights(expert, sizes, cap):
    """Per-sample weights per channel, inverse to the frequency of the expert's action (the rule's non-zero
    actions are rare: about 2 fertilisations in 133 days), normalised to mean 1 and capped."""
    expert = np.asarray(expert, dtype=np.int64).reshape(len(expert), -1)
    weights = []
    for index, size in enumerate(sizes):
        counts = np.bincount(expert[:, index], minlength=size).astype(float)
        present = counts > 0
        raw = np.where(present, len(expert) / (present.sum() * np.maximum(counts, 1)), 0.0)
        w = np.minimum(raw[expert[:, index]], cap)
        weights.append(w / w.mean())
    return weights


def pretrain(model, data, learn, *, epochs, smoothing, batch_size=512, learning_rate=1e-3, seed=0, weight_cap=20.0):
    """Fit the policy head (class-weighted, smoothed cross-entropy over feasible actions) and the value head
    (MSE to returns)."""
    import torch
    sizes = [CHANNEL_SIZES[c] for c in learn]
    targets = [torch.as_tensor(t, dtype=torch.float32)
               for t in smoothed_targets(data["expert"], data["masks"], sizes, smoothing)]
    obs = torch.as_tensor(data["obs"], dtype=torch.float32)
    masks = np.asarray(data["masks"], dtype=bool)
    returns = torch.as_tensor(data["returns"], dtype=torch.float32)
    weights = [torch.as_tensor(w, dtype=torch.float32) for w in class_weights(data["expert"], sizes, weight_cap)]
    policy = model.policy
    optimizer = torch.optim.Adam(policy.parameters(), lr=learning_rate)
    rng = np.random.default_rng(seed)
    history = []
    for epoch in range(epochs):
        order = rng.permutation(len(obs))
        policy_losses, value_losses = [], []
        for start in range(0, len(order), batch_size):
            index = order[start:start + batch_size]
            distribution = policy.get_distribution(obs[index], action_masks=masks[index])
            parts = getattr(distribution, "distributions", None) or [distribution.distribution]
            policy_loss = 0.0
            for part, target, weight in zip(parts, targets, weights, strict=True):
                logp = torch.log_softmax(part.logits, dim=-1)
                tgt = target[index]
                per_sample = -torch.where(tgt > 0, tgt * logp, torch.zeros_like(logp)).sum(-1)
                policy_loss = policy_loss + (weight[index] * per_sample).mean()
            value_loss = torch.nn.functional.mse_loss(policy.predict_values(obs[index]).flatten(), returns[index])
            loss = policy_loss + 0.5 * value_loss
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(policy.parameters(), 0.5)
            optimizer.step()
            policy_losses.append(float(policy_loss))
            value_losses.append(float(value_loss))
        history.append({"epoch": epoch, "policy_loss": float(np.mean(policy_losses)),
                        "value_loss": float(np.mean(value_losses))})
    with torch.no_grad():
        distribution = policy.get_distribution(obs, action_masks=masks)
        greedy = distribution.get_actions(deterministic=True).cpu().numpy().reshape(len(obs), -1)
    expert = np.asarray(data["expert"]).reshape(len(obs), -1)
    agreement = (greedy == expert).mean(axis=0)
    nonzero = expert > 0
    recall = [float((greedy[nonzero[:, i], i] == expert[nonzero[:, i], i]).mean()) if nonzero[:, i].any() else None
              for i in range(expert.shape[1])]
    false_positive = [float((greedy[~nonzero[:, i], i] > 0).mean()) for i in range(expert.shape[1])]
    return {"history": history, "agreement_by_channel": [float(a) for a in agreement],
            "nonzero_recall_by_channel": recall, "false_nonzero_rate_by_channel": false_positive,
            "expert_nonzero_rate_by_channel": [float(x) for x in nonzero.mean(axis=0)]}
