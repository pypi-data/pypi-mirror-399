TorchOpViz
=======

A small package to create visualizations of PyTorch operation execution.

## Install

Install PyTorch with CUDA support like:

```
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu126
```

Required torch>=2.1.0.

Install torchopviz:

```
pip3 install torchopviz
```

## Usage

Offline mode:

```
"""
complex_graph.json is a list of tensors, torch operations and modules. Each element consist of: 
    id                  identity number for tensors and torch operations
    start_time          start timestamp(us)
    end_time            end timestamp(us)
    is_tensor           True for tensor
    is_leaf             True for tensor and torch operation
    label               module name/torch operation name/tensor shape
    parent              parent of torch op
    children            a children list of module, used to build trees of modules and torch ops
    next_nodes          a list of next nodes id, used to build graphs of tensors and torch ops
    info                lifetime, and metadata for tensors
You can generate your json file which can be displayed by "torchopviz".
"""
from torchopviz import offline_viz
offline_viz(file="./complex_graph.json")
```

Online mode:

```
import torch
from torch import nn
from torchopviz import online_viz
model = nn.Sequential()
model.add_module('W0', nn.Linear(8, 16))
model.add_module('tanh', nn.Tanh())
model.add_module('W1', nn.Linear(16, 1))
data = torch.randn(1,8)
online_viz(model, data, save_dir="./sample_data")
```

![example](example.png)

## TODO

1.Display distributed computation

2.Combine memory usage info