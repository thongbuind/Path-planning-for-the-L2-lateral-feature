"""Kiểm nhẹ pipeline MLP luồng C (không chạy simulator): python3 -m pytest research/generators/mlp/tests -q"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import common  # noqa: E402
import model as mlp  # noqa: E402
import scenarios  # noqa: E402


def _random_features(rng, n=200):
    x = rng.normal(size=(n, common.F))
    half = rng.uniform(0.1, 1.5, n)
    for a, b in common.PAIRS:
        x[:, a], x[:, b] = -half, half
    x[:, 27] = 2.5
    return x


def test_mirror_is_involution_and_model_is_odd():
    rng = np.random.default_rng(1)
    x = _random_features(rng)
    assert np.array_equal(common.mirror(common.mirror(x)), x)
    norm = mlp.normaliser(x)
    assert np.all(norm["mean"][common.ODD] == 0.0) and norm["inv_std"][27] == 0.0
    p = mlp.init(rng)
    scale = np.ones(common.N)
    j = mlp.forward(p, norm, x, scale)
    assert np.array_equal(mlp.forward(p, norm, common.mirror(x), scale), -j)
    sym = x.copy()
    sym[:, common.ODD] = 0.0
    assert np.all(mlp.forward(p, norm, sym, scale) == 0.0)


def test_c_style_export_matches_float64():
    rng = np.random.default_rng(2)
    x = _random_features(rng)
    norm = mlp.normaliser(x)
    p = mlp.init(rng)
    we, wo = mlp.even_odd_weights(p)
    arrays = dict(mean=norm["mean"], inv_std=norm["inv_std"], w_even=we, w_odd=wo, b1=p["b1"], w2=p["w2"],
                  b2=p["b2"], w3=p["w3"], out_scale=np.ones(common.N))
    assert np.abs(mlp.forward_c(arrays, x) - mlp.forward(p, norm, x, np.ones(common.N))).max() < 1e-4


def test_gradient_matches_finite_difference():
    rng = np.random.default_rng(3)
    x = _random_features(rng, 20)
    y = rng.normal(size=(20, common.N))
    norm = mlp.normaliser(x)
    p = mlp.init(rng)
    w = np.ones(common.N)
    loss, grads = mlp.loss_and_grad(p, norm, x, y, w, 1e-3)
    for key in p:
        idx = tuple(int(rng.integers(s)) for s in p[key].shape)
        q = {k: v.copy() for k, v in p.items()}
        q[key][idx] += 1e-6
        assert abs((mlp.loss_and_grad(q, norm, x, y, w, 1e-3)[0] - loss) / 1e-6 - grads[key][idx]) < 1e-4


def test_pp_t7_geometry_is_excluded():
    from eval import sweep
    sigs = scenarios.pp_t7_signatures()
    s1d = sweep.load_run(["S1", "d"])
    spec = dict(id="t", family="single_curve", noise="N0", split="train", seed=100, speed_mps=s1d.speed_mps,
                profile="VP-0", lane_width=s1d.lane_width, acc="off", loop="closed", overrides=[],
                segments=[(s.kind, s.length, s.curvature_end) for s in s1d.segments])
    assert scenarios.excluded(spec, sigs)
    spec["speed_mps"] = s1d.speed_mps + 3.0
    assert not scenarios.excluded(spec, sigs)


def test_split_cells_cover_every_family_and_noise():
    cells = scenarios.VALIDATION_CELLS
    assert {f for f, _ in cells} == set(scenarios.FAMILIES)
    assert {n for _, n in cells} == set(scenarios.NOISE_NAMES)


def test_integrate_matches_constant_jerk():
    jerk = np.full(common.N, 0.6)
    d = common.integrate(np.array([0.1, 0.2, 0.0]), jerk)
    t = np.arange(1, common.N + 1) * common.DT
    assert np.allclose(d, 0.1 + 0.2 * t + 0.6 * t ** 3 / 6.0)
