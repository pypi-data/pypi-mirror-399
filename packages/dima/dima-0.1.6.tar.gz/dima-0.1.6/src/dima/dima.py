# src/dima/dima.py
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional, Tuple, Union

import numpy as np

import jax
import jax.numpy as jnp
from jax import random

from flax import serialization as flax_ser

from .ann import ANNBackend, make_ann
from .ddpm import DDPM
from .dmap import DMAP
from .gplm import GPLM


# ----------------------------
# Optional: Hugging Face Hub
# ----------------------------
try:
    from huggingface_hub import HfApi, HfFolder, upload_file, hf_hub_download  # type: ignore
    _HAS_HF = True
except Exception:
    _HAS_HF = False


_UNSET = object()


def _select_device(prefer: str = "auto"):
    """
    Safe JAX device selection.
    prefer: "auto" | "gpu" | "cpu"
    """
    prefer = (prefer or "auto").lower()
    devs = jax.devices()
    gpu = [d for d in devs if d.platform == "gpu"]
    cpu = [d for d in devs if d.platform == "cpu"]

    if prefer in ("auto", "gpu"):
        return gpu[0] if gpu else (cpu[0] if cpu else devs[0])
    if prefer == "cpu":
        return cpu[0] if cpu else devs[0]
    return gpu[0] if gpu else (cpu[0] if cpu else devs[0])


def _np_dtype_str(x) -> str:
    try:
        return str(np.dtype(x))
    except Exception:
        return "float32"


# ----------------------------
# Frozen inference-only models
# ----------------------------
class FrozenDMAP:
    """
    Inference-only Nyström DMAP embedder built from saved DMAP state.
    Uses kNN in ambient space against reference points.
    """

    def __init__(
        self,
        state: Dict[str, Any],
        *,
        ann_backend: ANNBackend = "auto",
        ann_params: Optional[Dict[str, Any]] = None,
        n_jobs: int = -1,
    ):
        self.k = int(state["k"])
        self.beta = float(state["beta"])
        self.β = self.beta
        self.alpha = float(state["alpha"])
        self.α = self.alpha
        self.eps = float(state["eps"])
        self.ε = self.eps
        self.dtype = np.dtype(state.get("dtype", "float32"))

        self.R_iX = np.ascontiguousarray(np.asarray(state["R_iX"]).astype(self.dtype, copy=False))
        self.qalpha_i = np.asarray(state["qalpha_i"], dtype=np.float64)
        self.qα_i = self.qalpha_i  # alias
        self.R_over_lam_ix = np.asarray(state["R_over_lam_ix"], dtype=np.float64)  # (Nref,d)
        self.R_over_λ_ix = self.R_over_lam_ix  # alias

        self.ann, self.ann_backend = make_ann(ann_backend, ann_params=ann_params, n_jobs=n_jobs)
        self.ann.build(self.R_iX)

    def __call__(self, R_aX: Union[np.ndarray, list], *, batch_size: Optional[int] = None) -> np.ndarray:
        R_aX = np.asarray(R_aX)
        single = (R_aX.ndim == 1)
        if single:
            R_aX = R_aX[None, :]

        R_aX = np.ascontiguousarray(R_aX.astype(self.dtype, copy=False))

        if batch_size is None:
            Z = self._embed(R_aX)
        else:
            out = []
            bs = int(batch_size)
            for s in range(0, R_aX.shape[0], bs):
                out.append(self._embed(R_aX[s : s + bs]))
            Z = np.vstack(out)

        return Z[0] if single else Z

    def _embed(self, R_aX: np.ndarray) -> np.ndarray:
        j_aK, D2_aK = self.ann.search(R_aX, self.k)  # (a,k)
        K_ai = np.exp(-self.beta * (D2_aK.astype(np.float64) / self.eps))  # (a,k)

        q_a = np.maximum(K_ai.sum(axis=1), 1e-30)
        qalpha_a = np.maximum(np.power(q_a, self.alpha), 1e-30)

        qalpha_i = np.maximum(self.qalpha_i[j_aK], 1e-30)
        Kalpha_ai = K_ai / (qalpha_a[:, None] * qalpha_i)

        d_a = np.maximum(Kalpha_ai.sum(axis=1), 1e-30)
        P_ai = Kalpha_ai / d_a[:, None]

        R_over = self.R_over_lam_ix[j_aK, :]              # (a,k,d)
        Z_ax = (P_ai[:, :, None] * R_over).sum(axis=1)    # (a,d)
        return Z_ax


def _restore_gplm_as_object(
    state: Dict[str, Any],
    *,
    ann_backend: ANNBackend = "auto",
    ann_params: Optional[Dict[str, Any]] = None,
    n_jobs: int = -1,
) -> GPLM:
    """
    Rehydrate a GPLM instance from saved state WITHOUT retraining.
    This is deliberately done as a true GPLM instance so you also get GPLM.flow(...)
    (assuming your GPLM class implements .flow()).
    """
    obj = GPLM.__new__(GPLM)  # type: ignore

    obj.beta = float(state["beta"])
    obj.β = obj.beta
    obj.eps = float(state["eps"])
    obj.ε = obj.eps
    obj.pred_k = None if state.get("pred_k", None) is None else int(state["pred_k"])
    obj.pred_κ = obj.pred_k
    obj.dtype = np.dtype(state.get("dtype", "float32"))

    obj.mean_X = np.asarray(state["mean_X"], dtype=np.float64)
    obj.M_mX = np.asarray(state["M_mX"], dtype=np.float64)

    obj.lat_mean_x = np.asarray(state["lat_mean_x"], dtype=np.float64)
    obj.lat_std_x = np.asarray(state["lat_std_x"], dtype=np.float64)

    obj.Z_mx_w = np.ascontiguousarray(np.asarray(state["Z_mx_w"]).astype(np.float64, copy=False))
    obj.m = int(obj.Z_mx_w.shape[0])

    obj.ann_Z, _ = make_ann(ann_backend, ann_params=ann_params, n_jobs=n_jobs)
    obj.ann_Z.build(obj.Z_mx_w.astype(obj.dtype, copy=False))

    return obj


# ----------------------------
# Config
# ----------------------------
@dataclass
class DIMAConfig:
    d: int = 32
    beta: float = 1.0
    ddpm_device: str = "auto"   # "auto" | "cpu" | "gpu"
    version: str = "0.2.0"


# ----------------------------
# Main wrapper
# ----------------------------
class DIMA:
    """
    DIMA: DMAP encoder + (latent DDPM) + GPLM decoder.

    Public “user-facing” convention in this wrapper:

      - Raw DMAP coordinates are the *public latent* (np.ndarray): R_ax (a,d)
      - Normalized latents are the DDPM coordinates (jax/np):      Z_ax (a,d)

    Minimal user API (what you asked for):

        dima = DIMA(R_iX, d=20, beta=2.0)
        R_ax = dima(R_aX)        # encode ambient -> raw latents
        Q_aX = dima(R_ax)        # decode raw latents -> ambient

    You can still pass full dict overrides for any submodule:
        dima = DIMA(..., dmap_kwargs={...}, gplm_kwargs={...}, ddpm_kwargs={...})
    and you can also tweak the “headline” DDPM knobs directly in __init__ (below).
    """

    def __init__(
        self,
        R_iX: np.ndarray,
        *,
        # main knobs
        d: int = 32,
        beta: float = 1.0,

        # allow per-module override (if None -> uses global beta)
        dmap_beta: Optional[float] = None,
        gplm_beta: Optional[float] = None,

        # DMAP headline knobs (everything else via dmap_kwargs)
        dmap_alpha: float = 0.0,
        dmap_t: float = 1.0,
        dmap_k: Optional[int] = None,

        # GPLM headline knobs (everything else via gplm_kwargs)
        gplm_m: int = 1024,
        gplm_pred_k: Optional[int] = None,

        # DDPM headline knobs (the ones worth surfacing)
        ddpm_T: int = 200,
        ddpm_hidden_dim: int = 128,
        ddpm_t_embed_dim: int = 64,
        ddpm_learning_rate: float = 3e-4,
        ddpm_n_iter: int = 200_000,
        ddpm_ema_decay: float = 0.999,
        ddpm_beta_max: float = 0.02,
        ddpm_batch_size: int = 256,
        ddpm_verbose_every: int = 0,
        ddpm_eps: float = 1e-5,

        # runtime
        ddpm_device: str = "auto",
        key: Optional[jax.Array] = None,

        # ann
        ann_backend: ANNBackend = "auto",
        ann_params: Optional[Dict[str, Any]] = None,
        n_jobs: int = -1,

        # “escape hatches”
        dmap_kwargs: Optional[Dict[str, Any]] = None,
        gplm_kwargs: Optional[Dict[str, Any]] = None,
        ddpm_kwargs: Optional[Dict[str, Any]] = None,

        # unicode aliases (β)
        **kwargs: Any,
    ):
        # ---- unicode aliases ----
        if "β" in kwargs:
            beta = float(kwargs.pop("β"))
        if "β_dmap" in kwargs:
            dmap_beta = float(kwargs.pop("β_dmap"))
        if "β_gplm" in kwargs:
            gplm_beta = float(kwargs.pop("β_gplm"))
        if kwargs:
            raise TypeError(f"Unexpected kwargs: {sorted(kwargs.keys())}")

        self.config = DIMAConfig(d=int(d), beta=float(beta), ddpm_device=str(ddpm_device))

        # devices + rng
        self.ddpm_device = _select_device(ddpm_device)
        self.cpu_device = _select_device("cpu")
        self.rng = random.PRNGKey(0) if key is None else key

        # training data
        self.R_iX = np.asarray(R_iX)
        if self.R_iX.ndim != 2:
            raise ValueError("R_iX must be 2D (N,D).")
        self.N, self.D = self.R_iX.shape
        self.d = int(d)

        # betas
        self.beta = float(beta)
        self.β = self.beta

        self.dmap_beta = float(self.beta if dmap_beta is None else dmap_beta)
        self.gplm_beta = float(self.beta if gplm_beta is None else gplm_beta)

        t0 = time.time()

        # -------------------------
        # 1) Train DMAP (CPU)
        # -------------------------
        dmap_init = dict(
            d=self.d,
            beta=self.dmap_beta,
            alpha=float(dmap_alpha),
            t=float(dmap_t),
            k=dmap_k,
            ann_backend=ann_backend,
            ann_params=ann_params,
            n_jobs=n_jobs,
        )
        if dmap_kwargs:
            dmap_init.update(dict(dmap_kwargs))
        # enforce headline knobs
        dmap_init["d"] = self.d
        dmap_init["beta"] = self.dmap_beta
        dmap_init["alpha"] = float(dmap_alpha)
        dmap_init["t"] = float(dmap_t)
        dmap_init["k"] = dmap_k

        self.enc = DMAP(self.R_iX, **dmap_init)

        # raw DMAP coordinates for *all* training points (Nyström OOS on training set)
        R_ix = np.asarray(self.enc(self.R_iX), dtype=np.float64)  # (N,d)

        # -------------------------
        # 2) Latent normalization for DDPM
        # -------------------------
        self.lat_mean_np = R_ix.mean(axis=0)
        self.lat_std_np = np.maximum(R_ix.std(axis=0), 1e-12)

        self.lat_mean_j = jax.device_put(jnp.asarray(self.lat_mean_np, dtype=jnp.float32), self.ddpm_device)
        self.lat_std_j = jax.device_put(jnp.asarray(self.lat_std_np, dtype=jnp.float32), self.ddpm_device)

        Z_ix = (R_ix - self.lat_mean_np) / self.lat_std_np  # (N,d)

        # -------------------------
        # 3) Train GPLM (CPU)
        # -------------------------
        gplm_init = dict(
            beta=self.gplm_beta,
            m=int(gplm_m),
            pred_k=gplm_pred_k,
            ann_backend=ann_backend,
            ann_params=ann_params,
            n_jobs=n_jobs,
        )
        if gplm_kwargs:
            gplm_init.update(dict(gplm_kwargs))
        # enforce headline knobs
        gplm_init["beta"] = self.gplm_beta
        gplm_init["m"] = int(gplm_m)
        gplm_init["pred_k"] = gplm_pred_k

        self.dec = GPLM(R_ix.astype(np.float32, copy=False), self.R_iX, **gplm_init)

        # -------------------------
        # 4) Train DDPM on normalized latents (DDPM device)
        # -------------------------
        Z_ix_j = jax.device_put(jnp.asarray(Z_ix, dtype=jnp.float32), self.ddpm_device)

        ddpm_init = dict(
            T=int(ddpm_T),
            hidden_dim=int(ddpm_hidden_dim),
            t_embed_dim=int(ddpm_t_embed_dim),
            learning_rate=float(ddpm_learning_rate),
            n_iter=int(ddpm_n_iter),
            ema_decay=float(ddpm_ema_decay),
            beta_max=float(ddpm_beta_max),
            batch_size=int(ddpm_batch_size),
            key=self.rng,
            verbose_every=int(ddpm_verbose_every),
            eps=float(ddpm_eps),
        )
        if ddpm_kwargs:
            ddpm_init.update(dict(ddpm_kwargs))
        # enforce headline knobs
        ddpm_init["T"] = int(ddpm_T)
        ddpm_init["hidden_dim"] = int(ddpm_hidden_dim)
        ddpm_init["t_embed_dim"] = int(ddpm_t_embed_dim)
        ddpm_init["learning_rate"] = float(ddpm_learning_rate)
        ddpm_init["n_iter"] = int(ddpm_n_iter)
        ddpm_init["ema_decay"] = float(ddpm_ema_decay)
        ddpm_init["beta_max"] = float(ddpm_beta_max)
        ddpm_init["batch_size"] = int(ddpm_batch_size)
        ddpm_init["verbose_every"] = int(ddpm_verbose_every)
        ddpm_init["eps"] = float(ddpm_eps)

        with jax.default_device(self.ddpm_device):
            self.dm = DDPM(Z_ix_j, **ddpm_init)

        self.training_time = time.time() - t0

    # -------------------------
    # Latent conversions
    # -------------------------
    def normalize(self, R_ax: Union[np.ndarray, jnp.ndarray]) -> jnp.ndarray:
        """raw latents (R) -> normalized latents (Z) on ddpm_device."""
        R = np.asarray(R_ax, dtype=np.float64)
        if R.ndim == 1:
            R = R[None, :]
        Z = (R - self.lat_mean_np) / self.lat_std_np
        Zj = jnp.asarray(Z, dtype=jnp.float32)
        return jax.device_put(Zj, self.ddpm_device)

    def unnormalize(self, Z_ax: Union[np.ndarray, jnp.ndarray]) -> np.ndarray:
        """normalized latents (Z) -> raw latents (R) on CPU (np)."""
        if isinstance(Z_ax, jax.Array):
            Z_np = np.asarray(jax.device_get(Z_ax))
        else:
            Z_np = np.asarray(Z_ax)
        if Z_np.ndim == 1:
            Z_np = Z_np[None, :]
        R = Z_np * self.lat_std_np + self.lat_mean_np
        return np.asarray(R)

    # -------------------------
    # Encode / Decode (public: raw latents)
    # -------------------------
    def encode(self, R_aX: Union[np.ndarray, jnp.ndarray], *, normalize: bool = False) -> Union[np.ndarray, jnp.ndarray]:
        """
        ambient -> raw DMAP latents (np) by default.
        If normalize=True, returns normalized latents (jnp) on ddpm_device.
        """
        X = np.asarray(R_aX)
        R_raw = np.asarray(self.enc(X))  # CPU, (a,d)
        if not normalize:
            return R_raw
        return self.normalize(R_raw)

    def decode(
        self,
        R_ax: Union[np.ndarray, jnp.ndarray],
        *,
        refine: bool = False,
        t_start: int = 10,
        add_noise: bool = True,
        key: Optional[jax.Array] = None,
        batch_size: Optional[int] = None,
    ) -> np.ndarray:
        """
        raw latent -> (optional DDPM refine in normalized coords) -> raw latent -> ambient.
        Returns ambient np.ndarray on CPU.
        """
        R_raw = np.asarray(R_ax, dtype=np.float64)
        single = (R_raw.ndim == 1)
        if single:
            R_raw = R_raw[None, :]

        if refine:
            Z = self.normalize(R_raw)  # on device
            Z = self.dm.refine_latents(Z, t_start=int(t_start), key=key, add_noise=bool(add_noise))
            R_raw = self.unnormalize(Z)  # back to CPU raw

        X_hat = self.dec(R_raw.astype(np.float32, copy=False), batch_size=batch_size)
        X_hat = np.asarray(X_hat)
        return X_hat[0] if single else X_hat

    def reconstruct(
        self,
        R_aX: Union[np.ndarray, jnp.ndarray],
        *,
        refine: bool = False,
        t_start: int = 10,
        add_noise: bool = True,
        key: Optional[jax.Array] = None,
        batch_size: Optional[int] = None,
    ) -> np.ndarray:
        """decode(encode(X))."""
        R_raw = self.encode(R_aX, normalize=False)
        return self.decode(R_raw, refine=refine, t_start=t_start, add_noise=add_noise, key=key, batch_size=batch_size)

    def sample(
        self,
        n: int,
        *,
        decode: bool = True,
        batch_size: Optional[int] = None,
    ) -> Union[np.ndarray, np.ndarray]:
        """
        Unconditional samples from latent DDPM.
        If decode=True: returns ambient samples (np) on CPU.
        If decode=False: returns raw latents (np) on CPU.
        """
        with jax.default_device(self.ddpm_device):
            Z = self.dm.sample(int(n))
        R = self.unnormalize(Z)  # raw (np)
        if not decode:
            return R
        return self.dec(R.astype(np.float32, copy=False), batch_size=batch_size)

    # -------------------------
    # Geodesic-ish flow wrapper (delegates to GPLM.flow)
    # -------------------------
    def flow(
        self,
        R_ax: Union[np.ndarray, jnp.ndarray],
        v_ax: Union[np.ndarray, jnp.ndarray],
        *,
        dt: float = 0.05,
        reg: float = 1e-8,
        keep_speed: bool = True,
        # optional DDPM projection step (in normalized coords)
        refine: bool = False,
        t_start: int = 10,
        add_noise: bool = True,
        key: Optional[jax.Array] = None,
        # decode return
        decode: bool = False,
        batch_size: Optional[int] = None,
    ) -> Union[Tuple[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray, np.ndarray]]:
        """
        One step of latent flow in *raw* coordinates.

        Requires: your GPLM class implements:
            R_next, v_next = gplm.flow(R, v, dt=..., reg=..., keep_speed=...)

        If refine=True, we project the *position* through DDPM in normalized coords after the step.
        (Velocity after projection is left unchanged—projection isn’t a deterministic diffeo.)

        Returns:
          if decode=False:
            (R_next, v_next)        both np arrays
          if decode=True:
            (X_next, R_next, v_next)
        """
        R = np.asarray(R_ax, dtype=np.float64)
        v = np.asarray(v_ax, dtype=np.float64)
        single = (R.ndim == 1)
        if single:
            R = R[None, :]
            v = v[None, :]

        if not hasattr(self.dec, "flow"):
            raise AttributeError(
                "Decoder does not have .flow(). Make sure you updated GPLM to include flow()."
            )

        Rn, vn = self.dec.flow(R, v, dt=float(dt), reg=float(reg), keep_speed=bool(keep_speed))

        if refine:
            Z = self.normalize(Rn)  # device
            Z = self.dm.refine_latents(Z, t_start=int(t_start), key=key, add_noise=bool(add_noise))
            Rn = self.unnormalize(Z)

        if not decode:
            if single:
                return np.asarray(Rn[0]), np.asarray(vn[0])
            return np.asarray(Rn), np.asarray(vn)

        Xn = self.dec(Rn.astype(np.float32, copy=False), batch_size=batch_size)
        Xn = np.asarray(Xn)
        if single:
            return Xn[0], np.asarray(Rn[0]), np.asarray(vn[0])
        return Xn, np.asarray(Rn), np.asarray(vn)

    # -------------------------
    # Convenience __call__
    # -------------------------
    def __call__(
        self,
        A: Union[np.ndarray, jnp.ndarray],
        *,
        refine: bool = False,
        t_start: int = 10,
        add_noise: bool = True,
        key: Optional[jax.Array] = None,
        batch_size: Optional[int] = None,
        normalize_latent: bool = False,
    ) -> Union[np.ndarray, jnp.ndarray]:
        """
        Dispatch by last dimension:

          - if A is (a,D): encode -> raw latents (np) by default
          - if A is (a,d): decode -> ambient (np)

        Options:
          - normalize_latent=True only affects encoding (returns Z on device)
          - refine/t_start/add_noise/key only affect decoding
        """
        A_np = np.asarray(A)
        if A_np.ndim == 1:
            A_np = A_np[None, :]

        if A_np.shape[1] == self.D:
            return self.encode(A_np, normalize=bool(normalize_latent))

        if A_np.shape[1] == self.d:
            return self.decode(
                A_np,
                refine=bool(refine),
                t_start=int(t_start),
                add_noise=bool(add_noise),
                key=key,
                batch_size=batch_size,
            )

        raise ValueError(f"Input has last-dim {A_np.shape[1]}, expected D={self.D} or d={self.d}.")

    # -------------------------
    # Save / Load
    # -------------------------
    def _pack_encoder(self) -> Dict[str, Any]:
        return dict(
            R_iX=np.asarray(self.enc.R_iX),
            qalpha_i=np.asarray(getattr(self.enc, "qalpha_i", getattr(self.enc, "qα_i"))),
            R_over_lam_ix=np.asarray(getattr(self.enc, "R_over_λ_ix", getattr(self.enc, "R_over_lam_ix"))),
            k=int(self.enc.k),
            beta=float(getattr(self.enc, "beta", getattr(self.enc, "β"))),
            alpha=float(getattr(self.enc, "alpha", getattr(self.enc, "α"))),
            eps=float(getattr(self.enc, "eps", getattr(self.enc, "ε"))),
            dtype=_np_dtype_str(getattr(self.enc, "dtype", np.float32)),
        )

    def _pack_decoder(self) -> Dict[str, Any]:
        return dict(
            Z_mx_w=np.asarray(getattr(self.dec, "Z_mx_w", None)),
            M_mX=np.asarray(self.dec.M_mX),
            mean_X=np.asarray(getattr(self.dec, "mean_X", np.zeros((self.D,), dtype=np.float64))),
            lat_mean_x=np.asarray(getattr(self.dec, "lat_mean_x", np.zeros((self.d,), dtype=np.float64))),
            lat_std_x=np.asarray(getattr(self.dec, "lat_std_x", np.ones((self.d,), dtype=np.float64))),
            beta=float(getattr(self.dec, "beta", getattr(self.dec, "β"))),
            eps=float(getattr(self.dec, "eps", getattr(self.dec, "ε"))),
            pred_k=getattr(self.dec, "pred_k", getattr(self.dec, "pred_κ", None)),
            dtype=_np_dtype_str(getattr(self.dec, "dtype", np.float32)),
        )

    def state_dict(self) -> Dict[str, Any]:
        dd = dict(
            T=int(self.dm.T),
            D=int(self.dm.D),
            hidden_dim=int(getattr(self.dm.model, "hidden", 128)),
            t_embed_dim=int(getattr(self.dm.model, "t_dim", 64)),
            ema_decay=float(getattr(self.dm, "ema_decay", 0.999)),
            beta_max=float(getattr(self.dm, "beta_max", 0.02)),
            eps=float(getattr(self.dm, "eps", 1e-5)),
            params=self.dm.state.params,
            ema_params=self.dm.state.ema_params,
        )

        state = dict(
            meta=dict(
                N=int(self.N),
                D=int(self.D),
                d=int(self.d),
                training_time=float(getattr(self, "training_time", 0.0)),
            ),
            config=asdict(self.config),
            latent_norm=dict(
                mean=np.asarray(self.lat_mean_np, dtype=np.float64),
                std=np.asarray(self.lat_std_np, dtype=np.float64),
            ),
            encoder=self._pack_encoder(),
            decoder=self._pack_decoder(),
            ddpm=dd,
        )
        return state

    def save_local(self, weights_file: str = "dima.msgpack", config_file: str = "config.json") -> None:
        state = self.state_dict()
        blob = flax_ser.msgpack_serialize(state)
        with open(weights_file, "wb") as f:
            f.write(blob)
        with open(config_file, "w") as f:
            json.dump(state["config"], f, indent=2)
        return None

    @classmethod
    def load_local(
        cls,
        weights_file: str = "dima.msgpack",
        *,
        ddpm_device: str = "auto",
        ann_backend: ANNBackend = "auto",
        ann_params: Optional[Dict[str, Any]] = None,
        n_jobs: int = -1,
        key: Optional[jax.Array] = None,
    ) -> "DIMA":
        with open(weights_file, "rb") as f:
            state = flax_ser.msgpack_restore(f.read())

        obj = cls.__new__(cls)  # bypass __init__

        obj.config = DIMAConfig(**state["config"])
        obj.ddpm_device = _select_device(ddpm_device)
        obj.cpu_device = _select_device("cpu")
        obj.training_time = float(state["meta"].get("training_time", 0.0))

        obj.N = int(state["meta"]["N"])
        obj.D = int(state["meta"]["D"])
        obj.d = int(state["meta"]["d"])

        # RNG
        obj.rng = random.PRNGKey(0) if key is None else key

        # beta (for display / convenience)
        obj.beta = float(obj.config.beta)
        obj.β = obj.beta

        # latent norm
        obj.lat_mean_np = np.asarray(state["latent_norm"]["mean"], dtype=np.float64)
        obj.lat_std_np = np.asarray(state["latent_norm"]["std"], dtype=np.float64)

        obj.lat_mean_j = jax.device_put(jnp.asarray(obj.lat_mean_np, dtype=jnp.float32), obj.ddpm_device)
        obj.lat_std_j = jax.device_put(jnp.asarray(obj.lat_std_np, dtype=jnp.float32), obj.ddpm_device)

        # frozen encoder + rehydrated decoder-as-GPLM (so flow works if GPLM.flow exists)
        obj.enc = FrozenDMAP(state["encoder"], ann_backend=ann_backend, ann_params=ann_params, n_jobs=n_jobs)
        obj.dec = _restore_gplm_as_object(state["decoder"], ann_backend=ann_backend, ann_params=ann_params, n_jobs=n_jobs)

        # rebuild DDPM skeleton with dummy data, then load params
        dd = state["ddpm"]
        T = int(dd["T"])
        D = int(dd["D"])
        hidden_dim = int(dd["hidden_dim"])
        t_embed_dim = int(dd["t_embed_dim"])
        ema_decay = float(dd.get("ema_decay", 0.999))
        beta_max = float(dd.get("beta_max", 0.02))
        eps = float(dd.get("eps", 1e-5))

        dummy = jnp.zeros((1, D), dtype=jnp.float32)
        with jax.default_device(obj.ddpm_device):
            obj.dm = DDPM(
                dummy,
                T=T,
                hidden_dim=hidden_dim,
                t_embed_dim=t_embed_dim,
                learning_rate=1e-3,
                n_iter=0,               # skip training on load
                ema_decay=ema_decay,
                beta_max=beta_max,
                batch_size=1,
                key=obj.rng,
                verbose_every=0,
                eps=eps,
            )
            obj.dm.state = obj.dm.state.replace(params=dd["params"], ema_params=dd["ema_params"])

        obj.R_iX = None  # training data not stored by default
        return obj

    # -------------------------
    # (Optional) HF helpers
    # -------------------------
    def save_hf(self, repo_id: str, weights_file: str = "dima.msgpack", config_file: str = "config.json") -> None:
        if not _HAS_HF:
            raise RuntimeError("huggingface_hub not installed.")
        self.save_local(weights_file=weights_file, config_file=config_file)
        token = HfFolder.get_token()
        if token is None:
            raise RuntimeError("No HF token found. Run `huggingface-cli login`.")
        api = HfApi()
        api.create_repo(repo_id=repo_id, repo_type="model", exist_ok=True, token=token)
        upload_file(path_or_fileobj=weights_file, path_in_repo=weights_file, repo_id=repo_id, token=token)
        upload_file(path_or_fileobj=config_file, path_in_repo=config_file, repo_id=repo_id, token=token)

    @classmethod
    def load_hf(
        cls,
        repo_id: str,
        *,
        weights_file: str = "dima.msgpack",
        ddpm_device: str = "auto",
        ann_backend: ANNBackend = "auto",
        ann_params: Optional[Dict[str, Any]] = None,
        n_jobs: int = -1,
        key: Optional[jax.Array] = None,
    ) -> "DIMA":
        if not _HAS_HF:
            raise RuntimeError("huggingface_hub not installed.")
        path = hf_hub_download(repo_id=repo_id, filename=weights_file)
        return cls.load_local(
            path,
            ddpm_device=ddpm_device,
            ann_backend=ann_backend,
            ann_params=ann_params,
            n_jobs=n_jobs,
            key=key,
        )


__all__ = ["DIMA", "DIMAConfig"]
