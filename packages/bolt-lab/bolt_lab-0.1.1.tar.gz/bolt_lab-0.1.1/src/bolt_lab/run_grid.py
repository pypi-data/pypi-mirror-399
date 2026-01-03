# src/bolt_lab/run_grid.py
from __future__ import annotations

import argparse
import os
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from queue import Queue

import yaml

from .paths import Paths
from .workspace import prepare_workspace
from .utils import run_combo, set_paths


def main():
    ap = argparse.ArgumentParser(description="Run grid experiments (YAML-only).")

    ap.add_argument("--config", type=str, default="grid_openset.yaml",
                    help="config file under package configs/ (or absolute path)")

    ap.add_argument("--data-dir", type=str, default=os.environ.get("BOLT_DATA_DIR", ""),
                    help="dataset root dir (required unless BOLT_DATA_DIR set)")
    ap.add_argument("--model-dir", type=str, default=os.environ.get("BOLT_MODEL_DIR", str(Path.home() / ".cache/bolt-lab/models")),
                    help="model/cache root dir")
    ap.add_argument("--output-dir", type=str, default=os.environ.get("BOLT_OUTPUT_DIR", str(Path.cwd() / "bolt_runs")),
                    help="work/output root dir (all outputs/results/logs live here)")
    ap.add_argument("--init-only", action="store_true",
                    help="Only prepare workspace under --output-dir and exit.")
    ap.add_argument("--overwrite-configs", action="store_true",
                    help="When initializing workspace, overwrite output-dir/configs.")

    args = ap.parse_args()

    paths = Paths.from_cli(data_dir=args.data_dir, model_dir=args.model_dir, output_dir=args.output_dir)
    # prepare_workspace(paths)
    prepare_workspace(paths, overwrite_configs=args.overwrite_configs)

    if args.init_only:
        print(f"[INIT] workspace prepared at: {paths.output_dir}")
        print(f"[INIT] editable configs at: {paths.output_dir / 'configs'}")
        return

    cfg_path = paths.resolve_config(args.config)
    if not cfg_path.exists():
        print(f"[ERR] YAML 配置文件不存在：{cfg_path}")
        sys.exit(1)

    with cfg_path.open("r", encoding="utf-8") as f:
        y = yaml.safe_load(f) or {}

    try:
        maps = y["maps"]
        methods = y["methods"]
        datasets = y["datasets"]
        grid = y["grid"]
        run = y["run"]
        result_file = y["result_file"]
        method_specs = y["per_method_extra"]
    except KeyError as e:
        print(f"[ERR] YAML 缺少必要字段：{e}")
        sys.exit(1)

    # 注意：YAML 里的 paths: results_dir/logs_dir 仍可保留，但解释为 output_dir 下的相对路径
    y_paths = y.get("paths", {}) or {}
    results_dir = (paths.output_dir / str(y_paths.get("results_dir", "results"))).resolve()
    logs_dir = (paths.output_dir / str(y_paths.get("logs_dir", "logs"))).resolve()
    set_paths(results_dir=str(results_dir), logs_dir=str(logs_dir), result_file=result_file, workdir=str(paths.output_dir),
              data_dir=str(paths.data_dir), model_dir=str(paths.model_dir))

    knowns = grid["known_cls_ratio"]
    labeleds = grid["labeled_ratio"]
    fold_idxs = grid["fold_idxs"]
    fold_nums = grid["fold_nums"]
    fold_types = grid["fold_types"]
    seeds = grid["seeds"]
    cfs = grid["cluster_num_factor"]

    num_pretrain_epochs = int(run["num_pretrain_epochs"])
    num_train_epochs = int(run["num_train_epochs"])

    gpus = run["gpus"]
    max_workers = int(run["max_workers"])
    dry_run = bool(run.get("dry_run", False))
    only_collect = bool(run.get("only_collect", False))

    method2task = {m: t for t, ms in maps.items() for m in ms}
    final_methods = [m for m in methods if m in method2task]
    if not final_methods:
        print("[ERR] methods 为空或不在 maps 中。")
        sys.exit(1)
    if not datasets:
        print("[ERR] datasets 为空。")
        sys.exit(1)

    slots_per_gpu = int(run.get("slots_per_gpu", 1))
    retry_on_oom = bool(run.get("retry_on_oom", True))
    max_retries = int(run.get("max_retries", 2))
    backoff_sec = float(run.get("retry_backoff_sec", 15.0))

    gpu_pool = Queue()
    if gpus:
        for gid in gpus:
            for _ in range(slots_per_gpu):
                gpu_pool.put(gid)
        pool_size = len(gpus) * slots_per_gpu
    else:
        gpu_pool.put(None)
        pool_size = 1

    print(f"[SCHED] GPU tokens: {pool_size} | gpus={gpus or ['CPU']} | slots_per_gpu={slots_per_gpu}")
    print(f"[PATHS] workdir={paths.output_dir} | data_dir={paths.data_dir} | model_dir={paths.model_dir}")
    print(f"[PATHS] code={paths.code_root} | configs={paths.configs_root}")

    combos = []
    for cf in cfs:
        for sd in seeds:
            for ft in fold_types:
                for fi in fold_idxs:
                    for fn in fold_nums:
                        for lr in labeleds:
                            for kr in knowns:
                                for d in datasets:
                                    for m in final_methods:
                                        combos.append((m, d, kr, lr, ft, fn, fi, sd, cf, method_specs))

    print(f"[INFO] 组合数={len(combos)} | methods={final_methods} | datasets={datasets}")

    def worker(task):
        m, d, kr, lr, ft, fn, fi, sd, cf, method_specs = task
        tries = 0
        while True:
            gpu_id = gpu_pool.get()
            try:
                return run_combo(
                    method=m, dataset=d, known=kr, labeled=lr,
                    fold_type=ft, fold_num=fn, fold_idx=fi, seed=sd, c_factor=cf,
                    gpu_id=gpu_id,
                    num_pretrain_epochs=num_pretrain_epochs,
                    num_train_epochs=num_train_epochs,
                    dry_run=dry_run,
                    only_collect=only_collect,
                    method_specs=method_specs,
                )
            except RuntimeError as e:
                msg = str(e)
                is_oom = ("CUDA out of memory" in msg) or ("out of memory" in msg)
                print(f"[ERR ] {m}@{d} fold={fi} seed={sd} on gpu={gpu_id} | {e.__class__.__name__}: {msg}")
                if retry_on_oom and is_oom and tries < max_retries:
                    tries += 1
                    print(f"[RETRY] OOM detected. Retry {tries}/{max_retries} after {backoff_sec}s.")
                    time.sleep(backoff_sec)
                    gpu_pool.put(gpu_id)
                    continue
                raise
            except Exception:
                print(f"[FATAL] Unexpected error in task {task} on gpu={gpu_id}")
                traceback.print_exc()
                raise
            finally:
                try:
                    gpu_pool.put(gpu_id)
                except Exception:
                    pass

    max_workers_eff = max(1, min(max_workers, pool_size, len(combos)))
    with ThreadPoolExecutor(max_workers=max_workers_eff) as ex:
        futures = [ex.submit(worker, task) for task in combos]
        for fu in as_completed(futures):
            _ = fu.result()

    from .utils import SUMMARY_CSV
    print("[DONE] 汇总文件：", SUMMARY_CSV)


if __name__ == "__main__":
    main()
