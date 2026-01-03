"""
_quiet.py – final version
Silences:
  • oneDNN / TF banners
  • Torch/LightGlue FutureWarnings
  • glog “Unable to register cuDNN|cuBLAS …” + pre‑absl WARNING
It works by temporarily redirecting *the real* file‑descriptor 2 to /dev/null.
"""

from __future__ import annotations

import contextlib
import importlib
import logging
import os
import warnings

from absl import logging as absl_logging

# Env switches
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
os.environ.setdefault("GLOG_minloglevel", "3")
os.environ.setdefault("FLAGS_minloglevel", "3")

# Logger levels
absl_logging.set_verbosity(absl_logging.ERROR)
absl_logging.set_stderrthreshold("error")
logging.getLogger("tensorflow").setLevel(logging.ERROR)

# Warning filters
warnings.filterwarnings("ignore", category=FutureWarning, module=r"torch(\.|$)")
warnings.filterwarnings("ignore", message=r"The secret HF_TOKEN", category=UserWarning)
warnings.filterwarnings(
    "ignore", message=r".*custom_fwd.*deprecated", category=FutureWarning
)
warnings.filterwarnings(
    "ignore",
    message=r"^No matching points found$",
    category=UserWarning,
    module=r"satalign\.lgm",
)
warnings.filterwarnings(
    "ignore",
    message=r"^Estimated translation is too large$",
    category=UserWarning,
    module=r"satalign\.main",
)


# Mute low‑level CUDA banners during first TF import
class _MuteFD2(contextlib.AbstractContextManager):
    def __enter__(self):
        import os

        self._null = os.open(os.devnull, os.O_WRONLY)
        self._saved = os.dup(2)
        os.dup2(self._null, 2)

    def __exit__(self, *exc):
        import os

        os.dup2(self._saved, 2)
        os.close(self._null)
        os.close(self._saved)


with _MuteFD2():
    importlib.import_module("tensorflow")
