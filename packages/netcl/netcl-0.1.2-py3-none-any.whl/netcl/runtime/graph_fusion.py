"""
Graph-Level Fusion for automatic kernel optimization.

This module analyzes computation graphs and fuses compatible operations
to reduce kernel launch overhead and improve memory bandwidth utilization.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Dict, List, Tuple, Callable, Any, Set
import weakref

try:
    import numpy as np
except ImportError:
    np = None


class OpType(Enum):
    """Operation types for fusion analysis."""
    CONV2D = auto()
    MATMUL = auto()
    BATCHNORM = auto()
    RELU = auto()
    SIGMOID = auto()
    TANH = auto()
    ADD = auto()
    MUL = auto()
    BIAS_ADD = auto()
    POOL = auto()
    DROPOUT = auto()
    SOFTMAX = auto()
    UNKNOWN = auto()


# Fusible operation patterns
FUSION_PATTERNS = [
    # Conv2D + BatchNorm + ReLU (most common CNN pattern)
    (OpType.CONV2D, OpType.BATCHNORM, OpType.RELU),
    # Conv2D + ReLU
    (OpType.CONV2D, OpType.RELU),
    # Conv2D + BiasAdd + ReLU
    (OpType.CONV2D, OpType.BIAS_ADD, OpType.RELU),
    # MatMul + BiasAdd + ReLU
    (OpType.MATMUL, OpType.BIAS_ADD, OpType.RELU),
    # MatMul + BiasAdd
    (OpType.MATMUL, OpType.BIAS_ADD),
    # BatchNorm + ReLU
    (OpType.BATCHNORM, OpType.RELU),
    # Add + ReLU (residual connections)
    (OpType.ADD, OpType.RELU),
]


@dataclass
class GraphNode:
    """A node in the computation graph."""
    id: int
    op_type: OpType
    name: str
    inputs: List[int] = field(default_factory=list)
    outputs: List[int] = field(default_factory=list)
    params: Dict[str, Any] = field(default_factory=dict)
    fused_with: Optional[int] = None  # ID of fusion group
    
    def __hash__(self):
        return hash(self.id)


@dataclass
class FusionGroup:
    """A group of operations that can be fused together."""
    id: int
    nodes: List[int]
    pattern: Tuple[OpType, ...]
    fused_kernel: Optional[Callable] = None
    

class ComputationGraph:
    """
    Represents a computation graph for fusion analysis.
    """
    
    def __init__(self):
        self._nodes: Dict[int, GraphNode] = {}
        self._next_id = 0
        self._fusion_groups: Dict[int, FusionGroup] = {}
        self._next_group_id = 0
        self._analyzed = False
    
    def add_node(
        self,
        op_type: OpType,
        name: str = "",
        inputs: Optional[List[int]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> int:
        """Add a node to the graph and return its ID."""
        node_id = self._next_id
        self._next_id += 1
        
        node = GraphNode(
            id=node_id,
            op_type=op_type,
            name=name or f"op_{node_id}",
            inputs=inputs or [],
            params=params or {}
        )
        self._nodes[node_id] = node
        
        # Update output connections
        for inp_id in node.inputs:
            if inp_id in self._nodes:
                self._nodes[inp_id].outputs.append(node_id)
        
        self._analyzed = False
        return node_id
    
    def analyze_and_fuse(self) -> List[FusionGroup]:
        """
        Analyze the graph and identify fusible patterns.
        Returns list of fusion groups.
        """
        if self._analyzed:
            return list(self._fusion_groups.values())
        
        fusion_groups = []
        visited: Set[int] = set()
        
        # Sort nodes topologically
        topo_order = self._topological_sort()
        
        for node_id in topo_order:
            if node_id in visited:
                continue
            
            node = self._nodes[node_id]
            
            # Try to match each pattern starting from this node
            for pattern in FUSION_PATTERNS:
                if node.op_type == pattern[0]:
                    matched_nodes = self._try_match_pattern(node_id, pattern)
                    if matched_nodes:
                        # Check if any node is already fused
                        if any(n in visited for n in matched_nodes):
                            continue
                        
                        # Create fusion group
                        group = FusionGroup(
                            id=self._next_group_id,
                            nodes=matched_nodes,
                            pattern=pattern
                        )
                        self._next_group_id += 1
                        
                        # Mark nodes as fused
                        for n_id in matched_nodes:
                            self._nodes[n_id].fused_with = group.id
                            visited.add(n_id)
                        
                        self._fusion_groups[group.id] = group
                        fusion_groups.append(group)
                        break
        
        self._analyzed = True
        return fusion_groups
    
    def _try_match_pattern(
        self,
        start_node_id: int,
        pattern: Tuple[OpType, ...]
    ) -> Optional[List[int]]:
        """Try to match a fusion pattern starting from a node."""
        matched = [start_node_id]
        current_id = start_node_id
        
        for i in range(1, len(pattern)):
            node = self._nodes[current_id]
            
            # Must have exactly one output for fusion
            if len(node.outputs) != 1:
                return None
            
            next_id = node.outputs[0]
            next_node = self._nodes.get(next_id)
            
            if next_node is None:
                return None
            
            # Check if type matches
            if next_node.op_type != pattern[i]:
                return None
            
            # Check if next node has only one input (from current)
            if len(next_node.inputs) != 1 or next_node.inputs[0] != current_id:
                # Special case: Add can have 2 inputs (for residual)
                if next_node.op_type == OpType.ADD and current_id in next_node.inputs:
                    pass
                else:
                    return None
            
            matched.append(next_id)
            current_id = next_id
        
        return matched
    
    def _topological_sort(self) -> List[int]:
        """Return nodes in topological order."""
        visited = set()
        order = []
        
        def dfs(node_id):
            if node_id in visited:
                return
            visited.add(node_id)
            
            node = self._nodes[node_id]
            for inp_id in node.inputs:
                if inp_id in self._nodes:
                    dfs(inp_id)
            
            order.append(node_id)
        
        for node_id in self._nodes:
            dfs(node_id)
        
        return order
    
    def get_fused_kernel(self, group_id: int) -> Optional[Callable]:
        """Get or create the fused kernel for a fusion group."""
        group = self._fusion_groups.get(group_id)
        if group is None:
            return None
        
        if group.fused_kernel is not None:
            return group.fused_kernel
        
        # Create fused kernel based on pattern
        group.fused_kernel = self._create_fused_kernel(group)
        return group.fused_kernel
    
    def _create_fused_kernel(self, group: FusionGroup) -> Optional[Callable]:
        """Create a fused kernel for the given pattern."""
        pattern = group.pattern
        
        if pattern == (OpType.CONV2D, OpType.BATCHNORM, OpType.RELU):
            try:
                from netcl.ops.fused_ops import conv_bn_relu_fused
                return conv_bn_relu_fused
            except ImportError:
                return None
        
        elif pattern == (OpType.CONV2D, OpType.RELU):
            try:
                from netcl.ops.fused_ops import conv_relu_fused
                return conv_relu_fused
            except ImportError:
                return None
        
        elif pattern == (OpType.MATMUL, OpType.BIAS_ADD, OpType.RELU):
            try:
                from netcl.ops.fused_ops import matmul_bias_relu_fused
                return matmul_bias_relu_fused
            except ImportError:
                return None
        
        elif pattern == (OpType.ADD, OpType.RELU):
            try:
                from netcl.ops.elementwise_optimized import add_relu_fused
                return add_relu_fused
            except ImportError:
                return None
        
        return None


class GraphOptimizer:
    """
    Optimizes computation graphs for inference.
    """
    
    def __init__(self, enable_fusion: bool = True):
        self.enable_fusion = enable_fusion
        self._graph: Optional[ComputationGraph] = None
    
    def optimize_sequential(self, layers: List) -> List:
        """
        Optimize a sequence of layers by fusing compatible operations.
        Returns optimized layer list.
        """
        if not self.enable_fusion:
            return layers
        
        # Build computation graph
        self._graph = ComputationGraph()
        layer_to_node: Dict[int, int] = {}
        
        prev_node_id = None
        for i, layer in enumerate(layers):
            op_type = self._layer_to_op_type(layer)
            inputs = [prev_node_id] if prev_node_id is not None else []
            node_id = self._graph.add_node(
                op_type=op_type,
                name=f"layer_{i}",
                inputs=inputs,
                params={"layer_idx": i}
            )
            layer_to_node[i] = node_id
            prev_node_id = node_id
        
        # Analyze and fuse
        fusion_groups = self._graph.analyze_and_fuse()
        
        # Rebuild optimized layer list
        optimized = []
        fused_indices: Set[int] = set()
        
        for group in fusion_groups:
            for node_id in group.nodes:
                node = self._graph._nodes[node_id]
                fused_indices.add(node.params["layer_idx"])
        
        i = 0
        while i < len(layers):
            if i in fused_indices:
                # Find the fusion group for this layer
                node_id = layer_to_node[i]
                node = self._graph._nodes[node_id]
                if node.fused_with is not None:
                    group = self._graph._fusion_groups[node.fused_with]
                    # Create fused layer
                    fused_layer = self._create_fused_layer(
                        [layers[self._graph._nodes[n].params["layer_idx"]] for n in group.nodes],
                        group.pattern
                    )
                    if fused_layer is not None:
                        optimized.append(fused_layer)
                    else:
                        # Fallback: keep original layers
                        for n in group.nodes:
                            optimized.append(layers[self._graph._nodes[n].params["layer_idx"]])
                    i += len(group.nodes)
                    continue
            
            optimized.append(layers[i])
            i += 1
        
        return optimized
    
    def _layer_to_op_type(self, layer) -> OpType:
        """Map layer class to OpType."""
        class_name = layer.__class__.__name__.lower()
        
        mapping = {
            "conv2d": OpType.CONV2D,
            "linear": OpType.MATMUL,
            "batchnorm2d": OpType.BATCHNORM,
            "batchnorm": OpType.BATCHNORM,
            "relu": OpType.RELU,
            "sigmoid": OpType.SIGMOID,
            "tanh": OpType.TANH,
            "maxpool2d": OpType.POOL,
            "avgpool2d": OpType.POOL,
            "dropout": OpType.DROPOUT,
            "softmax": OpType.SOFTMAX,
        }
        
        return mapping.get(class_name, OpType.UNKNOWN)
    
    def _create_fused_layer(self, layers: List, pattern: Tuple[OpType, ...]):
        """Create a fused layer from component layers."""
        if pattern == (OpType.CONV2D, OpType.RELU):
            from netcl.nn.layers import _FusedConvReLU
            return _FusedConvReLU(layers[0])
        
        elif pattern == (OpType.CONV2D, OpType.BATCHNORM, OpType.RELU):
            from netcl.nn.layers import _FusedConvBNReLU
            return _FusedConvBNReLU(layers[0], layers[1])
        
        return None


# Global optimizer instance
_global_optimizer: Optional[GraphOptimizer] = None


def get_graph_optimizer() -> GraphOptimizer:
    """Get or create the global graph optimizer."""
    global _global_optimizer
    if _global_optimizer is None:
        _global_optimizer = GraphOptimizer()
    return _global_optimizer


def optimize_model(model) -> None:
    """
    Optimize a model for inference by fusing compatible layers.
    Modifies the model in-place.
    """
    optimizer = get_graph_optimizer()
    
    if hasattr(model, 'layers'):
        model.layers = optimizer.optimize_sequential(model.layers)
    
    # Recursively optimize nested modules
    if hasattr(model, '__dict__'):
        for name, attr in model.__dict__.items():
            if hasattr(attr, 'layers'):
                optimize_model(attr)


__all__ = [
    'OpType',
    'GraphNode',
    'FusionGroup',
    'ComputationGraph',
    'GraphOptimizer',
    'get_graph_optimizer',
    'optimize_model',
]
