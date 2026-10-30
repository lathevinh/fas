"""Source-balanced hard-attack ranking candidate; not a novel pAUC algorithm."""

from __future__ import annotations

from fractions import Fraction

import torch
from torch import Tensor
from torch.nn.functional import softplus


def upper_tail_mean(values: Tensor, fraction: Fraction) -> Tensor:
    if (values.ndim != 1 or not values.numel() or not values.is_floating_point()
            or not torch.isfinite(values).all()
            or not isinstance(fraction, Fraction) or not 0 < fraction <= 1):
        raise ValueError("finite nonempty floating values and exact tail fraction in (0,1] required")
    ranked = torch.sort(values, descending=True, stable=True).values
    mass = len(values)*fraction.numerator
    whole, remainder = divmod(mass, fraction.denominator)
    total = ranked[:whole].sum()*fraction.denominator
    if remainder:
        total = total + ranked[whole]*remainder
    return total/mass


def attack_tail_ranking(logits: Tensor, attacks: Tensor, domains: Tensor, *,
                        fraction: Fraction = Fraction(1, 20), margin: float = 1.0) -> Tensor:
    if (logits.ndim != 1 or not logits.numel() or not logits.is_floating_point()
            or attacks.shape != logits.shape or domains.shape != logits.shape
            or attacks.dtype not in (torch.bool, torch.int64) or domains.dtype != torch.int64
            or attacks.device != logits.device or domains.device != logits.device
            or not torch.isfinite(logits).all() or not ((attacks == 0) | (attacks == 1)).all()
            or (domains < 0).any() or not isinstance(margin, (int, float))
            or not 0 <= margin < float("inf")):
        raise ValueError("finite attack-high logits, binary labels, source IDs and nonnegative margin required")
    sources = torch.unique(domains, sorted=True)
    if len(sources) < 2:
        raise ValueError("at least two source domains required")
    positives, negatives = [], []
    for source in sources:
        mask = domains == source
        attack = logits[mask & (attacks == 1)]
        real = logits[mask & (attacks == 0)]
        if not len(attack) or not len(real):
            raise ValueError("both post-augmentation classes required in every source batch")
        positives.append(attack)
        negatives.append(real)
    terms = []
    for attack in positives:
        hardness = torch.stack([
            softplus(margin + real[None, :] - attack[:, None]).mean(dim=1) for real in negatives
        ]).mean(dim=0)
        terms.append(upper_tail_mean(hardness, fraction))
    return torch.stack(terms).mean()
