# Environment Setup

**Project:** Spectra Align ML  
**System:** Debian GNU/Linux 13  
**Python:** Virtual Environment  
**PyTorch:** CPU-only  

---

## Create the virtual environment

From the project directory:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

---

## Install PyTorch

This machine uses an integrated Intel GPU and does not support CUDA.

Install the CPU-only build:

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

This avoids downloading unnecessary NVIDIA CUDA and cuDNN dependencies.

---

## Install project dependencies

Install the remaining packages:

```bash
pip install -r requirements.txt
```

The current `requirements.txt` contains:

```text
numpy
rasterio
matplotlib
scikit-image
scikit-learn
```

---

## Verify PyTorch

Run:

```bash
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
```

Expected CUDA result:

```text
False
```