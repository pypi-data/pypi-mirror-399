"""
Autograd-enabled wrappers for core ops.
"""

from __future__ import annotations

import numpy as np
from typing import Optional, Tuple

from netcl.autograd.engine import Node, apply_op
from netcl.core.tensor import Tensor, reshape as tensor_reshape
from netcl.amp import autocast, maybe_cast_tensor
from netcl.ops import (
    matmul,
    elementwise_binary,
    relu as relu_op,
    bias_add as bias_add_op,
    sigmoid as sigmoid_op,
    tanh as tanh_op,
    leaky_relu as leaky_relu_op,
    prelu as prelu_op,
    gelu as gelu_op,
    swish as swish_op,
    elu as elu_op,
    softplus as softplus_op,
    hard_sigmoid as hard_sigmoid_op,
    hard_swish as hard_swish_op,
    clamp as clamp_op,
    hard_tanh as hard_tanh_op,
    depthwise_conv2d as dw_conv2d_op,
    depthwise_conv2d_backward as dw_conv2d_bwd,
    softmax as softmax_op,
    max_pool2d as max_pool2d_op,
    max_pool2d_backward as max_pool2d_bwd,
    dropout as dropout_op,
    avg_pool2d as avg_pool2d_op,
    avg_pool2d_backward as avg_pool2d_bwd,
    transpose2d,
    broadcast_binary as bcast_bin,
    conv_transpose2d as conv_transpose2d_op,
)
from netcl.core.backend import get_backend
import pyopencl as cl  # type: ignore


def tensor(x: Tensor, requires_grad: bool = False) -> Node:
    return Node(value=maybe_cast_tensor(x), requires_grad=requires_grad)


def add(a: Node, b: Node, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        # broadcast-aware: grad for broadcasted arg needs reduction; for now rely on broadcast kernel producing full shape for both
        return [grad_out, grad_out]

    # If shapes match, use elementwise; else broadcast kernel
    if a.value.shape == b.value.shape:
        return apply_op(lambda x, y: elementwise_binary(x, y, expression="ADD(v0, v1)"), grad_fn, a, b, tape=tape)
    else:
        return apply_op(lambda x, y: bcast_bin(x, y, op="ADD"), grad_fn, a, b, tape=tape)


def relu(x: Node, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        # grad = grad_out * (x > 0)
        from netcl.ops.elementwise import elementwise_binary
        mask = elementwise_binary(x.value, x.value, expression="(v0 > 0 ? 1 : 0)")
        return [elementwise_binary(grad_out, mask, expression="MUL(v0, v1)")]

    return apply_op(lambda t: relu_op(t), grad_fn, x, tape=tape)


def bias_add(x: Node, bias: Node, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        # dL/dx = grad_out ; dL/db = reduce over rows
        from netcl.ops.reduction import reduce_sum

        db = reduce_sum(grad_out, axis=0)
        return [grad_out, db]

    return apply_op(lambda a, b: bias_add_op(a, b), grad_fn, x, bias, tape=tape)


def matmul_op(a: Node, b: Node, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        # dA = grad_out @ B^T ; dB = A^T @ grad_out (all device-side)
        from netcl.ops.matmul import matmul as mm

        a_shape = a.value.shape
        b_shape = b.value.shape
        if len(a_shape) != 2 or len(b_shape) != 2:
            raise ValueError("matmul grad expects 2D tensors")
        b_T = transpose2d(b.value)
        a_T = transpose2d(a.value)
        dA = mm(grad_out, b_T)
        dB = mm(a_T, grad_out)
        return [dA, dB]

    return apply_op(lambda x, y: matmul(x, y), grad_fn, a, b, tape=tape)


def conv2d(x: Node, w: Node, bias: Optional[Node] = None, stride: int = 1, pad: int = 0, algo: Optional[str] = None, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        from netcl.ops.conv2d import conv2d_backward

        grad_x, grad_w, grad_b = conv2d_backward(
            x.value, w.value, grad_out, bias.value if bias else None, stride=stride, pad=pad, algo=algo
        )
        return [grad_x, grad_w, grad_b] if bias is not None else [grad_x, grad_w]

    from netcl.ops.conv2d import conv2d as conv2d_fwd

    fn = lambda a, b, c=None: conv2d_fwd(a, b, c, stride=stride, pad=pad, algo=algo)
    args = (x, w, bias) if bias is not None else (x, w)
    return apply_op(fn, grad_fn, *args, tape=tape)


def flatten(x: Node, shape: Tuple[int, ...], tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        # reshape back to input shape
        return [tensor_reshape(grad_out, x.value.shape)]

    return apply_op(lambda t: tensor_reshape(t, shape), grad_fn, x, tape=tape)


def max_pool2d(x: Node, kernel_size: int = 2, stride: int = 2, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        grad_x = max_pool2d_bwd(x.value, grad_out, kernel_size=kernel_size, stride=stride)
        return [grad_x]

    return apply_op(lambda t: max_pool2d_op(t, kernel_size=kernel_size, stride=stride), grad_fn, x, tape=tape)


def avg_pool2d(x: Node, kernel_size: int = 2, stride: int = 2, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        grad_x = avg_pool2d_bwd(x.value, grad_out, kernel_size=kernel_size, stride=stride)
        return [grad_x]

    return apply_op(lambda t: avg_pool2d_op(t, kernel_size=kernel_size, stride=stride), grad_fn, x, tape=tape)


def dropout(x: Node, p: float = 0.5, seed: Optional[int] = None, tape=None) -> Node:
    """
    Dropout with saved mask for backward: grad = grad_out * mask / (1-p).
    """
    mask_holder: dict = {}

    def forward(t: Tensor) -> Tensor:
        out, mask = dropout_op(t, p=p, seed=seed, return_mask=True)
        mask_holder["mask"] = mask
        return out

    def grad_fn(grad_out: Tensor):
        mask = mask_holder.get("mask")
        if mask is None:
            raise RuntimeError("dropout mask missing for backward")
        scale = 1.0 / (1.0 - p) if p < 1 else 0.0
        grad = elementwise_binary(grad_out, mask, expression=f"MUL(v0, {scale})")
        return [grad]

    return apply_op(forward, grad_fn, x, tape=tape)


def sigmoid(x: Node, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        y = sigmoid_op(x.value)
        y1 = elementwise_binary(y, y, expression="MUL(v0, (1.0f - v1))")  # y * (1 - y)
        grad = elementwise_binary(grad_out, y1, expression="MUL(v0, v1)")
        return [grad]

    return apply_op(lambda t: sigmoid_op(t), grad_fn, x, tape=tape)


def tanh(x: Node, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        y = tanh_op(x.value)
        y_sq = elementwise_binary(y, y, expression="MUL(v0, v1)")
        one_minus = elementwise_binary(y_sq, y_sq, expression="SUB(1.0f, v0)")
        grad = elementwise_binary(grad_out, one_minus, expression="MUL(v0, v1)")
        return [grad]

    return apply_op(lambda t: tanh_op(t), grad_fn, x, tape=tape)

def gelu(x: Node, approximate: bool = True, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        x_val = x.value
        if approximate:
            x_sq = elementwise_binary(x_val, x_val, expression="MUL(v0, v1)")
            x_cu = elementwise_binary(x_sq, x_val, expression="MUL(v0, v1)")
            x_cu_scaled = elementwise_binary(x_cu, x_cu, expression="MUL(v0, 0.044715f)")
            inner = elementwise_binary(x_val, x_cu_scaled, expression="ADD(v0, v1)")
            t = elementwise_binary(inner, inner, expression="MUL(v0, 0.79788456f)")
            tanh_t = tanh_op(t)
            tanh_sq = elementwise_binary(tanh_t, tanh_t, expression="MUL(v0, v1)")
            one_minus = elementwise_binary(tanh_sq, tanh_sq, expression="SUB(1.0f, v0)")
            one_plus = elementwise_binary(tanh_t, tanh_t, expression="ADD(v0, 1.0f)")
            term1 = elementwise_binary(one_plus, one_plus, expression="MUL(v0, 0.5f)")
            x_sq_scaled = elementwise_binary(x_sq, x_sq, expression="MUL(v0, 0.134145f)")
            one_plus_x = elementwise_binary(x_sq_scaled, x_sq_scaled, expression="ADD(v0, 1.0f)")
            term2 = elementwise_binary(x_val, one_minus, expression="MUL(v0, v1)")
            term2 = elementwise_binary(term2, term2, expression="MUL(v0, 0.5f)")
            term2 = elementwise_binary(term2, term2, expression="MUL(v0, 0.79788456f)")
            term2 = elementwise_binary(term2, one_plus_x, expression="MUL(v0, v1)")
            dy = elementwise_binary(term1, term2, expression="ADD(v0, v1)")
        else:
            x_sq = elementwise_binary(x_val, x_val, expression="MUL(v0, v1)")
            x_sq_half = elementwise_binary(x_sq, x_sq, expression="MUL(v0, -0.5f)")
            exp_term = elementwise_binary(x_sq_half, x_sq_half, expression="EXP(v0)")
            erf_term = elementwise_binary(x_val, x_val, expression="erf(v0 * 0.70710678f)")
            term1 = elementwise_binary(erf_term, erf_term, expression="ADD(v0, 1.0f)")
            term1 = elementwise_binary(term1, term1, expression="MUL(v0, 0.5f)")
            term2 = elementwise_binary(exp_term, exp_term, expression="MUL(v0, 0.39894228f)")
            term2 = elementwise_binary(term2, x_val, expression="MUL(v0, v1)")
            dy = elementwise_binary(term1, term2, expression="ADD(v0, v1)")
        grad = elementwise_binary(grad_out, dy, expression="MUL(v0, v1)")
        return [grad]

    return apply_op(lambda t: gelu_op(t, approximate=approximate), grad_fn, x, tape=tape)


def swish(x: Node, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        sig = sigmoid_op(x.value)
        term = elementwise_binary(sig, x.value, expression="ADD(v0, MUL(v1, SUB(1.0f, v0)))")  # sig + x*sig*(1-sig)
        grad = elementwise_binary(grad_out, term, expression="MUL(v0, v1)")
        return [grad]

    return apply_op(lambda t: swish_op(t), grad_fn, x, tape=tape)


def elu(x: Node, alpha: float = 1.0, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        from netcl.ops.elementwise import elementwise_binary
        expx = elementwise_binary(x.value, x.value, expression="EXP(v0)")
        mask = elementwise_binary(x.value, x.value, expression="(v0 > 0 ? 1.0f : 0.0f)")
        neg_mask = elementwise_binary(x.value, x.value, expression="(v0 <= 0 ? 1.0f : 0.0f)")
        left = mask
        right = elementwise_binary(expx, expx, expression=f"MUL(v0, {alpha}f)")
        right = elementwise_binary(right, neg_mask, expression="MUL(v0, v1)")
        grad = elementwise_binary(left, right, expression="ADD(v0, v1)")
        grad = elementwise_binary(grad_out, grad, expression="MUL(v0, v1)")
        return [grad]

    return apply_op(lambda t: elu_op(t, alpha=alpha), grad_fn, x, tape=tape)


def softplus(x: Node, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        sig = sigmoid_op(x.value)
        grad = elementwise_binary(grad_out, sig, expression="MUL(v0, v1)")
        return [grad]

    return apply_op(lambda t: softplus_op(t), grad_fn, x, tape=tape)


def hard_sigmoid(x: Node, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        mask = elementwise_binary(x.value, x.value, expression="(v0 > -2.5f && v0 < 2.5f ? 0.2f : 0.0f)")
        grad = elementwise_binary(grad_out, mask, expression="MUL(v0, v1)")
        return [grad]

    return apply_op(lambda t: hard_sigmoid_op(t), grad_fn, x, tape=tape)


def hard_swish(x: Node, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        # derivative of x * relu6(x+3)/6
        mask = elementwise_binary(x.value, x.value, expression="(v0 > -3 && v0 < 3 ? 1.0f : 0.0f)")
        relu6 = elementwise_binary(x.value, x.value, expression="fmax(0.0f, fmin(6.0f, v0 + 3.0f))")
        term = elementwise_binary(relu6, mask, expression="MUL(v0, v1)")
        term = elementwise_binary(term, term, expression="MUL(v0, 1.0f/6.0f)")
        add = elementwise_binary(mask, relu6, expression="MUL(v0, v1)")
        add = elementwise_binary(add, add, expression="MUL(v0, 1.0f/6.0f)")
        grad = elementwise_binary(term, add, expression="ADD(v0, v1)")
        grad = elementwise_binary(grad_out, grad, expression="MUL(v0, v1)")
        return [grad]

    return apply_op(lambda t: hard_swish_op(t), grad_fn, x, tape=tape)


def clamp(x: Node, min_val: float, max_val: float, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        mask = elementwise_binary(x.value, x.value, expression=f"(v0 >= {min_val}f && v0 <= {max_val}f ? 1.0f : 0.0f)")
        grad = elementwise_binary(grad_out, mask, expression="MUL(v0, v1)")
        return [grad]

    return apply_op(lambda t: clamp_op(t, min_val, max_val), grad_fn, x, tape=tape)


def hard_tanh(x: Node, min_val: float = -1.0, max_val: float = 1.0, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        mask = elementwise_binary(x.value, x.value, expression=f"(v0 >= {min_val}f && v0 <= {max_val}f ? 1.0f : 0.0f)")
        grad = elementwise_binary(grad_out, mask, expression="MUL(v0, v1)")
        return [grad]

    return apply_op(lambda t: hard_tanh_op(t, min_val=min_val, max_val=max_val), grad_fn, x, tape=tape)


def depthwise_conv2d(x: Node, w: Node, bias: Optional[Node] = None, stride: int = 1, pad: int = 0, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        gx, gw, gb = dw_conv2d_bwd(x.value, w.value, grad_out, bias.value if bias else None, stride=stride, pad=pad)
        return [gx, gw, gb] if bias is not None else [gx, gw]

    fn = lambda a, b, c=None: dw_conv2d_op(a, b, c, stride=stride, pad=pad)
    args = (x, w, bias) if bias is not None else (x, w)
    return apply_op(fn, grad_fn, *args, tape=tape)


def conv_transpose2d(x: Node, w: Node, bias: Optional[Node] = None, stride: int = 1, pad: int = 0, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        from netcl.ops.conv_transpose2d import conv_transpose2d_backward as ct_bwd

        gx, gw, gb = ct_bwd(x.value, w.value, grad_out, bias.value if bias else None, stride=stride, pad=pad)
        return [gx, gw, gb] if bias is not None else [gx, gw]

    fn = lambda a, b, c=None: conv_transpose2d_op(a, b, c, stride=stride, pad=pad)
    args = (x, w, bias) if bias is not None else (x, w)
    return apply_op(fn, grad_fn, *args, tape=tape)


def prelu(x: Node, alpha: Node, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        from netcl.ops.elementwise import prelu_backward
        grad_x, grad_alpha = prelu_backward(x.value, alpha.value, grad_out)
        return [grad_x, grad_alpha]

    return apply_op(lambda t, a: prelu_op(t, a), grad_fn, x, alpha, tape=tape)


def batch_norm2d(x: Node, gamma: Node, beta: Node, running_mean: Tensor, running_var: Tensor, momentum: float = 0.1, eps: float = 1e-5, training: bool = True, tape=None) -> Node:
    """
    BatchNorm2d autograd wrapper. running_mean/var are Tensors (no grad). Returns normalized output; saves mean/var for backward.
    """
    cache: dict = {}

    def forward(x_t: Tensor, g_t: Tensor, b_t: Tensor) -> Tensor:
        out, mean, var = bn2d_fwd(x_t, g_t, b_t, running_mean, running_var, momentum=momentum, eps=eps, training=training)
        cache["mean"] = mean
        cache["var"] = var
        return out

    def grad_fn(grad_out: Tensor):
        mean = cache.get("mean")
        var = cache.get("var")
        if mean is None or var is None:
            raise RuntimeError("batch_norm2d backward missing mean/var")
        gx, ggamma, gbeta = bn2d_bwd(x.value, gamma.value, grad_out, mean, var, eps=eps)
        return [gx, ggamma, gbeta]

    return apply_op(forward, grad_fn, x, gamma, beta, tape=tape)


def layer_norm(x: Node, gamma: Node, beta: Node, eps: float = 1e-5, tape=None) -> Node:
    cache: dict = {}

    def forward(x_t: Tensor, g_t: Tensor, b_t: Tensor) -> Tensor:
        out, mean, var = ln_fwd(x_t, g_t, b_t, eps=eps)
        cache["mean"] = mean
        cache["var"] = var
        return out

    def grad_fn(grad_out: Tensor):
        mean = cache.get("mean")
        var = cache.get("var")
        gx, ggamma, gbeta = ln_bwd(x.value, gamma.value, grad_out, mean, var, eps=eps)
        return [gx, ggamma, gbeta]

    return apply_op(forward, grad_fn, x, gamma, beta, tape=tape)


def pad2d(x: Node, pad: int = 1, mode: str = "zero", tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        grad_x = pad2d_bwd(grad_out, pad=pad, mode=mode, in_shape=x.value.shape)
        return [grad_x]

    return apply_op(lambda t: pad2d_op(t, pad=pad, mode=mode), grad_fn, x, tape=tape)


def group_norm(x: Node, gamma: Node, beta: Node, groups: int, eps: float = 1e-5, tape=None) -> Node:
    cache: dict = {}

    def forward(x_t: Tensor, g_t: Tensor, b_t: Tensor) -> Tensor:
        out, mean, var = gn_fwd(x_t, g_t, b_t, groups=groups, eps=eps)
        cache["mean"] = mean
        cache["var"] = var
        return out

    def grad_fn(grad_out: Tensor):
        mean = cache.get("mean")
        var = cache.get("var")
        gx, ggamma, gbeta = gn_bwd(x.value, gamma.value, grad_out, mean, var, groups=groups, eps=eps)
        return [gx, ggamma, gbeta]

    return apply_op(forward, grad_fn, x, gamma, beta, tape=tape)


def global_avg_pool2d(x: Node, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        grad_x = gap2d_bwd(x.value, grad_out)
        return [grad_x]

    return apply_op(lambda t: gap2d_op(t), grad_fn, x, tape=tape)

def leaky_relu(x: Node, negative_slope: float = 0.01, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        expr = f"(v0 > 0 ? 1.0f : {negative_slope}f)"
        mask = elementwise_binary(x.value, x.value, expression=expr)
        return [elementwise_binary(grad_out, mask, expression="MUL(v0, v1)")]

    return apply_op(lambda t: leaky_relu_op(t, negative_slope=negative_slope), grad_fn, x, tape=tape)


def sub(a: Node, b: Node, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        return [grad_out, elementwise_binary(grad_out, grad_out, expression="MUL(v0, -1)")]

    if a.value.shape == b.value.shape:
        return apply_op(lambda x, y: elementwise_binary(x, y, expression="SUB(v0, v1)"), grad_fn, a, b, tape=tape)
    else:
        return apply_op(lambda x, y: bcast_bin(x, y, op="SUB"), grad_fn, a, b, tape=tape)


def mse_loss(pred: Node, target: Node, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        diff = elementwise_binary(pred.value, target.value, expression="SUB(v0, v1)")
        scale = 2.0
        grad_pred = elementwise_binary(diff, diff, expression=f"MUL(v0, {scale})")  # 2*diff
        grad_target = elementwise_binary(grad_pred, grad_pred, expression="MUL(v0, -1)")
        return [grad_pred, grad_target]

    def forward(x: Tensor, y: Tensor) -> Tensor:
        diff = elementwise_binary(x, y, expression="SUB(v0, v1)")
        sq = elementwise_binary(diff, diff, expression="MUL(v0, v1)")
        # reduce all
        from netcl.ops.reduction import reduce_sum

        return reduce_sum(sq, axis=None)

    return apply_op(lambda x, y: forward(x, y), grad_fn, pred, target, tape=tape)


def l1_loss(pred: Node, target: Node, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        sign = elementwise_binary(pred.value, target.value, expression="(v0 > v1 ? 1.0f : (v0 < v1 ? -1.0f : 0.0f))")
        grad = elementwise_binary(grad_out, sign, expression="MUL(v0, v1)")
        return [grad, elementwise_binary(grad, grad, expression="MUL(v0, -1)")]

    def forward(x: Tensor, y: Tensor) -> Tensor:
        diff = elementwise_binary(x, y, expression="SUB(v0, v1)")
        absd = elementwise_binary(diff, diff, expression="ABS(v0)")
        from netcl.ops.reduction import reduce_sum

        return reduce_sum(absd, axis=None)

    return apply_op(lambda x, y: forward(x, y), grad_fn, pred, target, tape=tape)


def l2_loss(pred: Node, target: Node, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        diff = elementwise_binary(pred.value, target.value, expression="SUB(v0, v1)")
        grad = elementwise_binary(diff, grad_out, expression="MUL(v0, v1)")
        return [grad, elementwise_binary(grad, grad, expression="MUL(v0, -1)")]

    def forward(x: Tensor, y: Tensor) -> Tensor:
        diff = elementwise_binary(x, y, expression="SUB(v0, v1)")
        sq = elementwise_binary(diff, diff, expression="MUL(v0, v1)")
        from netcl.ops.reduction import reduce_sum

        return reduce_sum(sq, axis=None)

    return apply_op(lambda x, y: forward(x, y), grad_fn, pred, target, tape=tape)


def hinge_loss(logits: Node, targets: Node, margin: float = 1.0, tape=None) -> Node:
    """
    Multi-class hinge: assumes targets are one-hot.
    """
    hinge_kcache = {}

    def forward(l: Tensor, t: Tensor) -> Tensor:
        backend = get_backend(l)
        if backend == "cpu":
            l_host = l.to_host()
            t_host = t.to_host()
            true_scores = (l_host * t_host).sum(axis=1, keepdims=True)
            margins = np.maximum(0.0, margin - true_scores + l_host)
            margins[t_host.astype(bool)] = 0.0
            loss = margins.sum() / l_host.shape[0]
            return Tensor.from_host(l.queue, np.array([loss], dtype=np.float32))
        # device-side: compute per-sample loss and reduce on host
        N, C = l.shape
        loss_vec = Tensor.from_shape(l.queue, (N,), dtype="float32")
        kkey = (l.context.int_ptr, "hinge_fwd")
        if kkey not in hinge_kcache:
            ksrc = """
            __kernel void hinge_loss(__global const float* logits, __global const float* targets, __global float* loss,
                                     const int N, const int C, const float margin) {
                int n = get_global_id(0);
                if (n >= N) return;
                int base = n * C;
                float true_score = 0.0f;
                int y = -1;
                for (int c = 0; c < C; ++c) {
                    float t = targets[base + c];
                    if (t != 0.0f) {
                        true_score = logits[base + c];
                        y = c;
                        break;
                    }
                }
                float acc = 0.0f;
                for (int c = 0; c < C; ++c) {
                    if (c == y) continue;
                    float m = margin - true_score + logits[base + c];
                    if (m > 0.0f) acc += m;
                }
                loss[n] = acc;
            }
            """
            hinge_kcache[kkey] = cl.Program(l.context, ksrc).build().hinge_loss
        kernel = hinge_kcache[kkey]
        gsize = (int(np.ceil(N / 256.0)) * 256,)
        kernel(l.queue, gsize, (256,), l.buffer, t.buffer, loss_vec.buffer, np.int32(N), np.int32(C), np.float32(margin))
        loss_host = loss_vec.to_host()
        loss_scalar = float(loss_host.sum() / max(1, N))
        return Tensor.from_host(l.queue, np.array([loss_scalar], dtype=np.float32))

    def grad_fn(grad_out: Tensor):
        backend = get_backend(logits.value)
        if backend == "cpu":
            l_host = logits.value.to_host()
            t_host = targets.value.to_host()
            batch = l_host.shape[0]
            true_scores = (l_host * t_host).sum(axis=1, keepdims=True)
            margins = margin - true_scores + l_host
            mask = (margins > 0).astype(np.float32)
            mask[t_host.astype(bool)] = 0.0
            row_sum = mask.sum(axis=1, keepdims=True)
            grad = mask
            grad[t_host.astype(bool)] = -row_sum[:, 0]
            grad = grad / batch
            g = Tensor.from_host(logits.value.queue, grad.astype(np.float32))
            if grad_out.shape == (1,):
                scale = float(grad_out.to_host()[0])
                if scale != 1.0:
                    g = elementwise_binary(g, g, expression=f"MUL(v0, {scale})")
            return [g, None]
        N, C = logits.value.shape
        grad = Tensor.from_shape(logits.value.queue, (N, C), dtype="float32")
        kkey = (logits.value.context.int_ptr, "hinge_bwd")
        if kkey not in hinge_kcache:
            ksrc = """
            __kernel void hinge_grad(__global const float* logits, __global const float* targets, __global float* grad,
                                     const int N, const int C, const float margin, const float scale) {
                int gid = get_global_id(0);
                int total = N * C;
                if (gid >= total) return;
                int n = gid / C;
                int c = gid % C;
                int base = n * C;
                float true_score = 0.0f;
                int y = -1;
                for (int i = 0; i < C; ++i) {
                    float t = targets[base + i];
                    if (t != 0.0f) {
                        true_score = logits[base + i];
                        y = i;
                        break;
                    }
                }
                int count = 0;
                for (int i = 0; i < C; ++i) {
                    if (i == y) continue;
                    float m = margin - true_score + logits[base + i];
                    if (m > 0.0f) count += 1;
                }
                float g = 0.0f;
                if (c == y) {
                    g = -((float)count);
                } else {
                    float m = margin - true_score + logits[base + c];
                    g = (m > 0.0f) ? 1.0f : 0.0f;
                }
                grad[gid] = g * scale;
            }
            """
            hinge_kcache[kkey] = cl.Program(logits.value.context, ksrc).build().hinge_grad
        kernel = hinge_kcache[kkey]
        scale = np.float32(float(grad_out.to_host()[0]) / float(N) if grad_out.shape == (1,) else 1.0 / float(N))
        total = N * C
        gsize = (int(np.ceil(total / 256.0)) * 256,)
        kernel(logits.value.queue, gsize, (256,), logits.value.buffer, targets.value.buffer, grad.buffer, np.int32(N), np.int32(C), np.float32(margin), scale)
        return [grad, None]

    return apply_op(lambda l, t: forward(l, t), grad_fn, logits, targets, tape=tape)


def cross_entropy(logits: Node, targets: Node, tape=None) -> Node:
    """
    Cross-entropy with softmax; targets expected as one-hot float tensor.
    Gradients are computed analytically: grad_logits = (softmax - targets) / N.
    """
    ce_kcache = {}
    ctx = getattr(logits.value, "context", None) if hasattr(logits, "value") else None

    def forward(logit_t: Tensor, target_t: Tensor) -> Tensor:
        backend = get_backend(logit_t)
        if backend == "cpu":
            probs = softmax_op(logit_t)
            probs_host = probs.to_host()
            targets_host = target_t.to_host()
            eps = 1e-8
            loss = -np.sum(targets_host * np.log(probs_host + eps)) / targets_host.shape[0]
            return Tensor.from_host(logit_t.queue, np.array([loss], dtype=np.float32))
        # device-side CE: compute per-sample loss on GPU and reduce on host (N floats)
        probs = softmax_op(logit_t)
        N, C = probs.shape
        loss_vec = Tensor.from_shape(logit_t.queue, (N,), dtype="float32")
        kkey = (logit_t.context.int_ptr, "ce_fwd")
        if kkey not in ce_kcache:
            ksrc = """
            __kernel void ce_loss(__global const float* probs, __global const float* targets, __global float* loss, const int N, const int C) {
                int n = get_global_id(0);
                if (n >= N) return;
                float acc = 0.0f;
                int base = n * C;
                for (int c = 0; c < C; ++c) {
                    float t = targets[base + c];
                    if (t != 0.0f) {
                        acc -= t * log(probs[base + c] + 1e-8f);
                    }
                }
                loss[n] = acc;
            }
            """
            ce_kcache[kkey] = cl.Program(logit_t.context, ksrc).build().ce_loss
        kernel = ce_kcache[kkey]
        gsize = (int(np.ceil(N / 256.0)) * 256,)
        kernel(logit_t.queue, gsize, (256,), probs.buffer, target_t.buffer, loss_vec.buffer, np.int32(N), np.int32(C))
        loss_host = loss_vec.to_host()
        loss_scalar = float(loss_host.sum() / max(1, N))
        forward.probs_saved = probs  # type: ignore[attr-defined]
        forward.N = N  # type: ignore[attr-defined]
        return Tensor.from_host(logit_t.queue, np.array([loss_scalar], dtype=np.float32))

    def grad_fn(grad_out: Tensor):
        backend = get_backend(logits.value)
        if backend == "cpu":
            probs = softmax_op(logits.value)
            probs_host = probs.to_host()
            targets_host = targets.value.to_host()
            batch = targets_host.shape[0]
            grad_logits = (probs_host - targets_host) / batch
            grad_tensor = Tensor.from_host(logits.value.queue, grad_logits.astype(np.float32))
            if grad_out.shape == (1,):
                scale = float(grad_out.to_host()[0])
                if scale != 1.0:
                    grad_tensor = elementwise_binary(grad_tensor, grad_tensor, expression=f"MUL(v0, {scale})")
            else:
                grad_tensor = elementwise_binary(grad_tensor, grad_out, expression="MUL(v0, v1)")
            return [grad_tensor, None]
        probs = getattr(forward, "probs_saved", None)  # type: ignore[attr-defined]
        N = getattr(forward, "N", None)  # type: ignore[attr-defined]
        if probs is None or N is None:
            probs = softmax_op(logits.value)
            N = probs.shape[0]
        C = probs.shape[1]
        grad = Tensor.from_shape(logits.value.queue, probs.shape, dtype="float32")
        kkey = (logits.value.context.int_ptr, "ce_bwd")
        if kkey not in ce_kcache:
            ksrc = """
            __kernel void ce_grad(__global const float* probs, __global const float* targets, __global float* grad, const int N, const int C, const float scale) {
                int gid = get_global_id(0);
                int total = N * C;
                if (gid >= total) return;
                int n = gid / C;
                float g = (probs[gid] - targets[gid]) / (float)N;
                grad[gid] = g * scale;
            }
            """
            ce_kcache[kkey] = cl.Program(logits.value.context, ksrc).build().ce_grad
        kernel = ce_kcache[kkey]
        scale = np.float32(float(grad_out.to_host()[0]) if grad_out.shape == (1,) else 1.0)
        total = N * C
        gsize = (int(np.ceil(total / 256.0)) * 256,)
        kernel(logits.value.queue, gsize, (256,), probs.buffer, targets.value.buffer, grad.buffer, np.int32(N), np.int32(C), scale)
        return [grad, None]

    return apply_op(lambda l, t: forward(l, t), grad_fn, logits, targets, tape=tape)
from netcl.nn.batchnorm import batch_norm2d as bn2d_fwd, batch_norm2d_backward as bn2d_bwd
from netcl.nn.layernorm import layer_norm as ln_fwd, layer_norm_backward as ln_bwd
from netcl.nn.padding import pad2d as pad2d_op, pad2d_backward as pad2d_bwd
from netcl.nn.groupnorm import group_norm as gn_fwd, group_norm_backward as gn_bwd
from netcl.nn.pooling import global_avg_pool2d as gap2d_op, global_avg_pool2d_backward as gap2d_bwd
