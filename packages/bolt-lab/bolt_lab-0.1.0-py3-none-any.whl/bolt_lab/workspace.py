# workspace.py
from __future__ import annotations
import os, shutil
from pathlib import Path
from .paths import Paths

def _safe_link(src: Path, dst: Path) -> None:
    src = src.resolve()
    if dst.exists() or dst.is_symlink():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.symlink(src, dst, target_is_directory=src.is_dir())
    except Exception:
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)

def prepare_workspace(paths: Paths, *, overwrite_configs: bool = False) -> None:
    wd = paths.output_dir
    wd.mkdir(parents=True, exist_ok=True)

    paths.outputs_dir.mkdir(parents=True, exist_ok=True)
    paths.results_dir.mkdir(parents=True, exist_ok=True)
    paths.logs_dir.mkdir(parents=True, exist_ok=True)

    # 这些保持链接兼容旧脚本
    _safe_link(paths.code_root, wd / "code")
    _safe_link(paths.data_dir, wd / "data")
    _safe_link(paths.model_dir, wd / "pretrained_models")

    # ✅ configs 改为复制到 workdir（可编辑，不会改到包内）
    cfg_dst = wd / "configs"
    if cfg_dst.exists():
        if overwrite_configs:
            shutil.rmtree(cfg_dst)
        else:
            return  # 已存在就不动
    shutil.copytree(paths.configs_root, cfg_dst)

    # HF cache 子目录（可选）
    (paths.model_dir / "hub").mkdir(parents=True, exist_ok=True)
    (paths.model_dir / "transformers").mkdir(parents=True, exist_ok=True)
    (paths.model_dir / "datasets").mkdir(parents=True, exist_ok=True)
