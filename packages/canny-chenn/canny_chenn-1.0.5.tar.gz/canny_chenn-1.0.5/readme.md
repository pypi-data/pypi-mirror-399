<h1 align="center" style="margin-top: 0px;">Canny Edges</h1>
<div id="img0" align="center">
    <img src="https://raw.githubusercontent.com/chrishenn/canny/refs/heads/main/packages/canny_chenn/doc/images/img1.png" width=200 alt="img1_in">
    <img src="https://raw.githubusercontent.com/chrishenn/canny/refs/heads/main/packages/canny_chenn/doc/images/img2.png" width=200 alt="img2_in">
    <img src="https://raw.githubusercontent.com/chrishenn/canny/refs/heads/main/packages/canny_chenn/doc/images/img3.png" width=200 alt="img3_in">
</div>
<div id="img0" align="center">
    <img src="https://raw.githubusercontent.com/chrishenn/canny/refs/heads/main/packages/canny_chenn/doc/images/img1_out.png" width=200 alt="img1_out">
    <img src="https://raw.githubusercontent.com/chrishenn/canny/refs/heads/main/packages/canny_chenn/doc/images/img2_out.png" width=200 alt="img2_out">
    <img src="https://raw.githubusercontent.com/chrishenn/canny/refs/heads/main/packages/canny_chenn/doc/images/img3_out.png" width=200 alt="img3_out">
</div>

&emsp;

[![PyPi version](https://badgen.net/pypi/v/canny-chenn/)](https://pypi.org/project/canny-chenn)
[![PyPI download month](https://img.shields.io/pypi/dm/canny-chenn)](https://pypi.org/project/canny-chenn)
[![PyPI format](https://img.shields.io/pypi/format/canny-chenn)](https://pypi.python.org/pypi/canny-chenn)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/canny-chenn)](https://pypi.python.org/pypi/canny-chenn)
[![PyPI status](https://img.shields.io/pypi/status/canny-chenn)](https://pypi.python.org/pypi/canny-chenn/)

A simple `Torch.nn.Module` to return an image mask representing edges found by the
[Canny Edge-Finding algorithm](https://en.wikipedia.org/wiki/Canny_edge_detector).

Supports:

- Linux
- PyTorch Tensor images formatted in image batches [B, C, h, w], with float32 data, and values spanning [0,1]
- Any number of image channels C
- All PyTorch backends  
- TorchScript jit script, as well as the newer, traced torch-export, on the Canny `nn.Module` class

pip install

```bash
pip install canny_chenn
# or,
pixi add --pypi canny_chenn
# or,
uv add canny_chenn
```

then

```python
from torch import Tensor
from canny_chenn import Canny
canny = Canny()
img_batch = Tensor([[[[0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3]],
            [[0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3]],
            [[0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3]],
            [[0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3]]]])
edge_mask = canny(img_batch)
# tensor([[[[0.0000, 0.6333, 0.0000, 0.0000],
#           [0.0000, 0.6333, 0.0000, 0.0000],
#           [0.0000, 0.6333, 0.0000, 0.0000]]]])
```

---

# Dev

I use [mise](https://mise.jdx.dev/getting-started.html) to handle project tools.

```bash
# clone, install tools
git clone https://github.com/chrishenn/canny.git
cd canny
mise i

# list available just recipes
just --list

Available recipes:
    demo   # Show canny detections on a set of test images. Kill with ctrl+c
    lint   # run project formatters/linters [alias: l]
    test   # run basic tests
    unsafe # run ruff with unsafe-fixes
    
# build wheel, sdist pkgs locally
uv build --package canny_chenn

# push tag to trigger github action to build pkgs and publish to pypi
git tag -a v1.0.4 -m v1.0.4 -f && git push --tags -f
```
