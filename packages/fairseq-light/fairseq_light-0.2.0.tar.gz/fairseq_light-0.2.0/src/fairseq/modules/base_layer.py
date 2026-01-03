# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import torch.nn as nn
import torch
import sys
from fairseq import utils
from fairseq.modules.layer_norm import LayerNorm


class BaseLayer(nn.Module):
    def __init__(self, args):
        super().__init__()
        self.num_workers = 1  # Single GPU
        expert_centroids = torch.empty(self.num_workers, args.decoder_embed_dim)
        torch.nn.init.orthogonal_(expert_centroids, gain=0.1)
        self.register_parameter(
            "expert_centroids", torch.nn.Parameter(expert_centroids)
        )
        self.expert_network = nn.Sequential(
            *([BaseSublayer(args) for _ in range(args.base_sublayers)])
        )
        self.expert_id = 0  # Single GPU, always rank 0
        self.shuffle = args.base_shuffle
        self.cpp = self.load_assignment()

        # Add a special attribute to the expert parameters, so we know not to sync their gradients
        for param in self.expert_network.parameters():
            param.expert = True

    def forward(self, input_features, *args, **kwargs):
        features = input_features.reshape(-1, input_features.size(-1))
        is_training = input_features.requires_grad

        if self.shuffle and is_training:
            # Shuffle tokens to break correlations within the batch
            shuffle_sort = torch.randperm(features.size(0), device=features.device)
            features = features[shuffle_sort]

        with torch.no_grad():
            # Compute similarity of each token to each expert, for routing
            token_expert_affinities = features.matmul(
                self.expert_centroids.transpose(0, 1)
            )

        # In single GPU mode, all tokens stay on the same device
        # No need for complex assignment since there's only one expert
        sort_by_expert = torch.arange(features.size(0), device=features.device)
        routed_features = features

        if routed_features.size(0) > 0:
            # Mix in the expert network based on how appropriate it is for these tokens
            alpha = torch.sigmoid(
                routed_features.mv(self.expert_centroids[self.expert_id])
            ).unsqueeze(1)
            routed_features = (
                alpha * self.expert_network(routed_features)
                + (1 - alpha) * routed_features
            )
        
        result = routed_features

        if self.shuffle and is_training:
            # Undo shuffling
            result = result[self.inverse_sort(shuffle_sort)]

        # Return additional Nones for compatibility with TransformerDecoderLayer
        return result.view(input_features.size()), None, None

    def inverse_sort(self, order):
        # Creates an index that undoes a sort: xs==xs[order][inverse_sort(order)]
        return torch.empty_like(order).scatter_(
            0, order, torch.arange(0, order.size(0), device=order.device)
        )

    def balanced_assignment(self, scores):
        # In single GPU mode, simply return identity mapping
        return torch.arange(scores.size(0), device=scores.device), None, None

    # Assigns each token to the top k experts
    def greedy_assignment(self, scores, k=1):
        # In single GPU mode, all tokens go to the single expert (expert 0)
        sort_ordering = torch.arange(scores.size(0), device=scores.device)
        return sort_ordering, None, None

    def load_assignment(self):
        try:
            from fairseq import libbase

            return libbase

        except ImportError as e:
            sys.stderr.write(
                "ERROR: missing libbase. run `python setup.py build_ext --inplace`\n"
            )
            raise e


class BaseSublayer(nn.Module):
    def __init__(self, args):
        super().__init__()
        self.activation_fn = utils.get_activation_fn(
            activation=getattr(args, "activation_fn", "relu") or "relu"
        )
        self.norm = LayerNorm(args.decoder_embed_dim, export=False)
        self.ff1 = torch.nn.Linear(args.decoder_embed_dim, args.decoder_ffn_embed_dim)
        self.ff2 = torch.nn.Linear(args.decoder_ffn_embed_dim, args.decoder_embed_dim)
        self.ff2.weight.data.zero_()

    def forward(self, xs):
        return xs + self.ff2(self.activation_fn(self.ff1(self.norm(xs))))
