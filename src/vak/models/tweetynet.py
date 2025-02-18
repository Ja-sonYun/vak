"""TweetyNet model

as described in
https://elifesciences.org/articles/63853
https://github.com/yardencsGitHub/tweetynet

Cohen, Y., Nicholson, D. A., Sanchioni, A., Mallaber, E. K., Skidanova, V., & Gardner, T. J. (2022).
Automated annotation of birdsong with a neural network that segments spectrograms. Elife, 11, e63853.
"""
from __future__ import annotations

import torch

from .. import (
    metrics,
    nets
)
from .windowed_frame_classification_model import WindowedFrameClassificationModel
from .decorator import model


@model(family=WindowedFrameClassificationModel)
class TweetyNet:
    """TweetyNet model, as described in
    Cohen, Y., Nicholson, D. A., Sanchioni, A., Mallaber, E. K., Skidanova, V., & Gardner, T. J. (2022).
    Automated annotation of birdsong with a neural network that segments spectrograms. Elife, 11, e63853.
    https://elifesciences.org/articles/63853.

    Code adapted from
    https://github.com/yardencsGitHub/tweetynet.

    Attributes
    ----------
    network : vak.nets.TweetyNet
        Convolutional-bidirectional LSTM neural network architecture.
    loss: torch.nn.CrossEntropyLoss
        Standard cross-entropy loss
    optimizer: torch.optim.Adam
        Adam optimizer.
    metrics: dict
        Mapping string names to the following metrics:
        ``vak.metrics.Accuracy``, ``vak.metrics.Levenshtein``,
        ``vak.metrics.SegmentErrorRate``, ``torch.nn.CrossEntropyLoss``.

    Notes
    -----
    ``TweetyNet`` is a type of windowed frame classification model,
    and this version built into ``vak`` relies on the
    ``WindowedFrameClassificationModel`` class.
    """
    network = nets.TweetyNet
    loss = torch.nn.CrossEntropyLoss
    optimizer = torch.optim.Adam
    metrics = {'acc': metrics.Accuracy,
               'levenshtein': metrics.Levenshtein,
               'segment_error_rate': metrics.SegmentErrorRate,
               'loss': torch.nn.CrossEntropyLoss}
    default_config = {
        'optimizer':
            {'lr': 0.003}
    }
