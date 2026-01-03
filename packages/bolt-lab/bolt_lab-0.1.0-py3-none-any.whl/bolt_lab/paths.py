# src/bolt_lab/paths.py
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _expand(p: str | Path) -> Path:
    return Path(p).expanduser().resolve()


@dataclass(frozen=True)
class Paths:
    data_dir: Path
    model_dir: Path
    output_dir: Path

    pkg_root: Path
    code_root: Path
    configs_root: Path

    @classmethod
    def from_cli(cls, *, data_dir: str | Path, model_dir: str | Path, output_dir: str | Path) -> "Paths":
        pkg_root = Path(__file__).resolve().parent

        dd = str(data_dir).strip() if data_dir is not None else ""
        if not dd:
            dd_path = (pkg_root / "data").resolve()
        else:
            dd_path = _expand(dd)

        return cls(
            data_dir=dd_path,
            model_dir=_expand(model_dir),
            output_dir=_expand(output_dir),
            pkg_root=pkg_root,
            code_root=(pkg_root / "code").resolve(),
            configs_root=(pkg_root / "configs").resolve(),
        )

    def resolve_config(self, p: str | Path) -> Path:
        pp = Path(p)
        if pp.is_absolute():
            return pp

        # 1) 优先：workdir/configs 下（用户可编辑副本）
        # 允许用户传 "grid_gcd.yaml" 或 "configs/grid_gcd.yaml"
        cand = pp
        if cand.parts and cand.parts[0] == "configs":
            cand = Path(*cand.parts[1:])
        local = (self.output_dir / "configs" / cand).resolve()
        if local.exists():
            return local

        # 2) 回退：包内 configs
        return (self.configs_root / cand).resolve()

    @property
    def results_dir(self) -> Path:
        return self.output_dir / "results"

    @property
    def logs_dir(self) -> Path:
        return self.output_dir / "logs"

    @property
    def outputs_dir(self) -> Path:
        return self.output_dir / "outputs"
