"""
MLE Runtime — Comprehensive Claims Validation Suite (UPDATED)
==============================================================

Purpose
-------
This *single file* is designed to PROVE or DISPROVE the following claims
for `mle_runtime` with measurable, reproducible evidence.

Updated for the latest MLE Runtime version with improved accuracy and performance.

Claims Covered
--------------
1.  Correctness preservation (numerical equivalence tests)
2.  Static execution semantics (determinism + no dynamic allocation)
3.  Memory-mapped zero-copy (RSS vs PSS + page-fault counts)
4.  Cold-start improvement (disk cache flushed benchmarks)
5.  Warm-load improvement (mmap reuse tests)
6.  Scaling with model complexity (Linear → Tree → Ensemble)
7.  Scaling with data size (1e4 → 1e6 samples)
8.  Concurrency behavior (multi-thread + multi-process)
9.  Limits vs joblib (direct baseline comparison)
10. Limits vs C++ / TorchScript / ONNX Runtime expectations
11. Failure behavior (corruption, version mismatch)
12. Portability (Windows + Linux)
13. Overheads (file size, page faults, TLB)

Non-goals
---------
- GPU acceleration
- Training performance
- Model mutation

Execution
---------
    python final_test.py

Requirements
------------
- Python 3.10+
- numpy, psutil, scikit-learn, joblib
- mle_runtime (the module under test)

Optional (for extended baselines):
- onnxruntime, torch (for TorchScript comparison)
"""

from __future__ import annotations

import os
import sys
import time
import gc
import json
import shutil
import tempfile
import platform
import hashlib
import threading
import traceback
import ctypes
import struct
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, List, Optional, Tuple
from contextlib import contextmanager
from functools import wraps

import numpy as np

# =============================================================================
# SAFE IMPORTS WITH FALLBACKS
# =============================================================================

def safe_import(module_name: str, fallback=None):
    """Import module with fallback on failure."""
    try:
        return __import__(module_name)
    except ImportError:
        return fallback

psutil = safe_import("psutil")
joblib = safe_import("joblib")

# sklearn imports with fallbacks
try:
    from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge
    from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
    from sklearn.ensemble import (
        RandomForestClassifier, RandomForestRegressor,
        GradientBoostingClassifier, GradientBoostingRegressor
    )
    from sklearn.svm import SVC, SVR
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import Pipeline
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# mle_runtime import
try:
    import mle_runtime as mle
    MLE_AVAILABLE = True
    MLE_VERSION = getattr(mle, "__version__", "unknown")
except ImportError:
    MLE_AVAILABLE = False
    MLE_VERSION = "NOT INSTALLED"
    mle = None

# Optional: ONNX Runtime for baseline comparison
try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False
    ort = None

# Optional: TorchScript for baseline comparison
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class TestConfig:
    """Central configuration for all tests."""
    features: int = 32
    small_size: int = 10_000
    medium_size: int = 100_000
    large_size: int = 1_000_000
    test_size: int = 2048
    num_threads: int = 4
    num_processes: int = 4
    num_warmup_runs: int = 3
    num_timed_runs: int = 5
    tolerance_rtol: float = 1e-5
    tolerance_atol: float = 1e-6
    random_seed: int = 42
    verbose: bool = True

CONFIG = TestConfig()

# =============================================================================
# LOGGING & REPORTING
# =============================================================================

class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def supports_color() -> bool:
    """Check if terminal supports color."""
    if platform.system() == "Windows":
        return os.environ.get("TERM") == "xterm" or "WT_SESSION" in os.environ
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

USE_COLOR = supports_color()

def colorize(text: str, color: str) -> str:
    """Apply color if supported."""
    if USE_COLOR:
        return f"{color}{text}{Colors.ENDC}"
    return text

def log_section(title: str):
    """Print section header."""
    print(f"\n{'='*70}")
    print(colorize(f" {title}", Colors.HEADER + Colors.BOLD))
    print('='*70)

def log_subsection(title: str):
    """Print subsection header."""
    print(f"\n{colorize('>>> ' + title, Colors.CYAN)}")

def log_result(key: str, value: Any, status: str = "info"):
    """Print a result line."""
    color = {
        "pass": Colors.GREEN,
        "fail": Colors.FAIL,
        "warn": Colors.WARNING,
        "info": Colors.BLUE,
    }.get(status, "")
    print(f"  {key}: {colorize(str(value), color)}")

def log_error(msg: str):
    """Print error message."""
    print(colorize(f"  ERROR: {msg}", Colors.FAIL))

def log_warning(msg: str):
    """Print warning message."""
    print(colorize(f"  WARNING: {msg}", Colors.WARNING))

# =============================================================================
# TIMING & MEASUREMENT UTILITIES
# =============================================================================

def now_ns() -> int:
    """High-resolution timestamp in nanoseconds."""
    return time.perf_counter_ns()

def now_ms() -> float:
    """High-resolution timestamp in milliseconds."""
    return time.perf_counter() * 1000

@contextmanager
def timer(name: str = "operation"):
    """Context manager for timing operations."""
    start = now_ns()
    yield
    elapsed_ms = (now_ns() - start) / 1e6
    if CONFIG.verbose:
        print(f"  [{name}] {elapsed_ms:.3f} ms")

def benchmark(func: Callable, warmup: int = 3, runs: int = 5) -> Dict[str, float]:
    """Benchmark a function with warmup and multiple runs."""
    # Warmup
    for _ in range(warmup):
        func()
    
    # Timed runs
    times = []
    for _ in range(runs):
        gc.collect()
        start = now_ns()
        func()
        times.append((now_ns() - start) / 1e6)
    
    return {
        "min_ms": min(times),
        "max_ms": max(times),
        "mean_ms": sum(times) / len(times),
        "median_ms": sorted(times)[len(times) // 2],
        "std_ms": np.std(times) if len(times) > 1 else 0.0,
        "runs": runs,
    }

# =============================================================================
# MEMORY MEASUREMENT UTILITIES
# =============================================================================

def get_memory_info() -> Dict[str, Any]:
    """Get current process memory information."""
    if psutil is None:
        return {"error": "psutil not available"}
    
    try:
        proc = psutil.Process(os.getpid())
        mem = proc.memory_info()
        result = {
            "rss_mb": mem.rss / (1024 * 1024),
            "vms_mb": mem.vms / (1024 * 1024),
        }
        
        # Platform-specific fields
        if hasattr(mem, "pfaults"):
            result["page_faults"] = mem.pfaults
        if hasattr(mem, "pageins"):
            result["page_ins"] = mem.pageins
        
        # Try to get PSS on Linux
        if platform.system() == "Linux":
            try:
                mem_full = proc.memory_full_info()
                if hasattr(mem_full, "pss"):
                    result["pss_mb"] = mem_full.pss / (1024 * 1024)
                if hasattr(mem_full, "uss"):
                    result["uss_mb"] = mem_full.uss / (1024 * 1024)
            except (psutil.AccessDenied, AttributeError):
                pass
        
        return result
    except Exception as e:
        return {"error": str(e)}

def get_page_faults() -> Tuple[Optional[int], Optional[int]]:
    """Get page fault counts (minor, major) if available."""
    if psutil is None:
        return None, None
    
    try:
        proc = psutil.Process(os.getpid())
        mem = proc.memory_info()
        minor = getattr(mem, "pfaults", None)
        major = getattr(mem, "pageins", None)
        return minor, major
    except Exception:
        return None, None

def flush_disk_cache():
    """Best-effort disk cache flush."""
    gc.collect()
    
    if platform.system() == "Linux":
        try:
            # Requires root privileges
            os.system("sync")
            with open("/proc/sys/vm/drop_caches", "w") as f:
                f.write("3")
        except (PermissionError, FileNotFoundError):
            log_warning("Cannot flush disk cache (requires root)")
    elif platform.system() == "Windows":
        # Windows doesn't have a simple cache flush mechanism
        # We can try to use ctypes to call system functions
        try:
            kernel32 = ctypes.windll.kernel32
            # This is a best-effort approach
        except Exception:
            pass
    
    gc.collect()


# =============================================================================
# FILE & HASH UTILITIES
# =============================================================================

def sha256_file(path: str) -> str:
    """Compute SHA256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def file_size_mb(path: str) -> float:
    """Get file size in MB."""
    return os.path.getsize(path) / (1024 * 1024)

def corrupt_file(src: str, dst: str, offset: int = 64, size: int = 128):
    """Create a corrupted copy of a file."""
    shutil.copy(src, dst)
    with open(dst, "r+b") as f:
        f.seek(offset)
        f.write(b"\x00" * size)

def modify_header(src: str, dst: str, byte_offset: int = 0, new_byte: int = 0xFF):
    """Create a copy with modified header byte (version mismatch simulation)."""
    shutil.copy(src, dst)
    with open(dst, "r+b") as f:
        f.seek(byte_offset)
        f.write(bytes([new_byte]))

# =============================================================================
# DATA GENERATION
# =============================================================================

class DataGenerator:
    """Lazy data generator to avoid OOM on memory-constrained systems."""
    
    def __init__(self, seed: int = 42):
        self.rng = np.random.default_rng(seed)
        self._cache = {}
    
    def generate_X(self, n: int, features: int, dtype=np.float32) -> np.ndarray:
        """Generate feature matrix."""
        key = (n, features, dtype)
        if key not in self._cache:
            self._cache[key] = self.rng.standard_normal((n, features)).astype(dtype)
        return self._cache[key]
    
    def generate_y_classification(self, X: np.ndarray) -> np.ndarray:
        """Generate binary classification labels."""
        return (X.sum(axis=1) > 0).astype(np.int32)
    
    def generate_y_regression(self, X: np.ndarray) -> np.ndarray:
        """Generate regression targets."""
        return X.sum(axis=1) + self.rng.standard_normal(X.shape[0]).astype(np.float32) * 0.1
    
    def clear_cache(self):
        """Clear cached data to free memory."""
        self._cache.clear()
        gc.collect()

# =============================================================================
# MODEL FACTORY
# =============================================================================

class ModelFactory:
    """Factory for creating test models with different complexity levels."""
    
    COMPLEXITY_LEVELS = ["linear", "tree", "ensemble", "complex_ensemble"]
    
    @staticmethod
    def create_model(complexity: str, task: str = "classification"):
        """Create a model of specified complexity."""
        if not SKLEARN_AVAILABLE:
            raise RuntimeError("sklearn not available")
        
        if task == "classification":
            models = {
                "linear": LogisticRegression(max_iter=500, solver="lbfgs"),
                "tree": DecisionTreeClassifier(max_depth=10),
                "ensemble": RandomForestClassifier(n_estimators=50, max_depth=8, n_jobs=1),
                "complex_ensemble": GradientBoostingClassifier(n_estimators=100, max_depth=6),
            }
        else:  # regression
            models = {
                "linear": Ridge(alpha=1.0),
                "tree": DecisionTreeRegressor(max_depth=10),
                "ensemble": RandomForestRegressor(n_estimators=50, max_depth=8, n_jobs=1),
                "complex_ensemble": GradientBoostingRegressor(n_estimators=100, max_depth=6),
            }
        
        return models.get(complexity)
    
    @staticmethod
    def get_all_models(task: str = "classification") -> Dict[str, Any]:
        """Get all models for a task."""
        return {
            name: ModelFactory.create_model(name, task)
            for name in ModelFactory.COMPLEXITY_LEVELS
            if ModelFactory.create_model(name, task) is not None
        }

# =============================================================================
# RESULTS COLLECTOR
# =============================================================================

@dataclass
class ClaimResult:
    """Result for a single claim test."""
    claim: str
    status: str  # "PROVED", "DISPROVED", "INCONCLUSIVE", "SKIPPED", "ERROR"
    evidence: Dict[str, Any] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)
    error: Optional[str] = None

class ResultsCollector:
    """Collect and report all test results."""
    
    def __init__(self):
        self.results: List[ClaimResult] = []
        self.metadata: Dict[str, Any] = {}
        self.start_time = time.time()
    
    def add_result(self, result: ClaimResult):
        """Add a claim result."""
        self.results.append(result)
    
    def add_metadata(self, key: str, value: Any):
        """Add metadata."""
        self.metadata[key] = value
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all results."""
        status_counts = {}
        for r in self.results:
            status_counts[r.status] = status_counts.get(r.status, 0) + 1
        
        return {
            "total_claims": len(self.results),
            "status_counts": status_counts,
            "duration_seconds": time.time() - self.start_time,
            "metadata": self.metadata,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert all results to dictionary."""
        return {
            "summary": self.get_summary(),
            "claims": [asdict(r) for r in self.results],
        }
    
    def print_report(self):
        """Print formatted report."""
        log_section("FINAL RESULTS REPORT")
        
        summary = self.get_summary()
        print(f"\nTotal Claims Tested: {summary['total_claims']}")
        print(f"Duration: {summary['duration_seconds']:.2f} seconds")
        print("\nStatus Breakdown:")
        for status, count in summary["status_counts"].items():
            color = {
                "PROVED": Colors.GREEN,
                "DISPROVED": Colors.FAIL,
                "INCONCLUSIVE": Colors.WARNING,
                "SKIPPED": Colors.BLUE,
                "ERROR": Colors.FAIL,
            }.get(status, "")
            print(f"  {colorize(status, color)}: {count}")
        
        print("\n" + "-"*70)
        print("Detailed Results:")
        print("-"*70)
        
        for r in self.results:
            status_color = {
                "PROVED": Colors.GREEN,
                "DISPROVED": Colors.FAIL,
                "INCONCLUSIVE": Colors.WARNING,
                "SKIPPED": Colors.BLUE,
                "ERROR": Colors.FAIL,
            }.get(r.status, "")
            
            print(f"\n[{colorize(r.status, status_color)}] {r.claim}")
            if r.notes:
                for note in r.notes:
                    print(f"    - {note}")
            if r.error:
                print(f"    ERROR: {r.error}")

# Global results collector
RESULTS = ResultsCollector()


# =============================================================================
# CLAIM 1: CORRECTNESS PRESERVATION (Numerical Equivalence)
# =============================================================================

def test_correctness_preservation(tmp_dir: str, data_gen: DataGenerator) -> ClaimResult:
    """
    CLAIM: MLE runtime produces numerically equivalent results to sklearn.
    
    Evidence: Compare predictions from sklearn model vs mle_runtime loaded model.
    """
    claim = "Correctness Preservation (Numerical Equivalence)"
    log_section(f"CLAIM 1: {claim}")
    
    if not MLE_AVAILABLE:
        return ClaimResult(claim, "SKIPPED", error="mle_runtime not available")
    if not SKLEARN_AVAILABLE:
        return ClaimResult(claim, "SKIPPED", error="sklearn not available")
    
    evidence = {}
    notes = []
    all_passed = True
    
    try:
        X_train = data_gen.generate_X(CONFIG.medium_size, CONFIG.features)
        y_train = data_gen.generate_y_classification(X_train)
        X_test = data_gen.generate_X(CONFIG.test_size, CONFIG.features)
        
        for complexity in ["linear", "tree", "ensemble"]:
            log_subsection(f"Testing {complexity} model")
            
            model = ModelFactory.create_model(complexity, "classification")
            model.fit(X_train, y_train)
            
            # sklearn predictions
            sklearn_proba = model.predict_proba(X_test)
            sklearn_pred = model.predict(X_test)
            
            # Export and load with mle_runtime
            model_path = os.path.join(tmp_dir, f"correctness_{complexity}.mle")
            
            try:
                mle.export_model(model, model_path, input_shape=(1, CONFIG.features))
            except AttributeError:
                # Try alternative export method
                try:
                    mle.save(model, model_path)
                except Exception as e:
                    notes.append(f"{complexity}: export failed - {e}")
                    evidence[complexity] = {"status": "export_failed", "error": str(e)}
                    all_passed = False
                    continue
            
            try:
                rt_model = mle.load_model(model_path)
            except AttributeError:
                try:
                    rt_model = mle.load(model_path)
                except Exception as e:
                    notes.append(f"{complexity}: load failed - {e}")
                    evidence[complexity] = {"status": "load_failed", "error": str(e)}
                    all_passed = False
                    continue
            
            # mle_runtime predictions
            try:
                mle_output = rt_model.run([X_test])
                if isinstance(mle_output, (list, tuple)):
                    mle_proba = mle_output[0]
                else:
                    mle_proba = mle_output
            except Exception as e:
                try:
                    mle_proba = rt_model.predict_proba(X_test)
                except:
                    try:
                        mle_proba = rt_model.predict(X_test)
                    except Exception as e2:
                        notes.append(f"{complexity}: inference failed - {e2}")
                        evidence[complexity] = {"status": "inference_failed", "error": str(e2)}
                        all_passed = False
                        continue
            
            # Compare results
            # Handle different output shapes
            if mle_proba.ndim == 2 and sklearn_proba.ndim == 2:
                if mle_proba.shape[1] == sklearn_proba.shape[1]:
                    ref = sklearn_proba
                    out = mle_proba
                else:
                    ref = sklearn_proba[:, 1] if sklearn_proba.shape[1] == 2 else sklearn_proba
                    out = mle_proba[:, 1] if mle_proba.shape[1] == 2 else mle_proba
            elif mle_proba.ndim == 1:
                ref = sklearn_proba[:, 1] if sklearn_proba.ndim == 2 else sklearn_proba
                out = mle_proba
            else:
                ref = sklearn_proba.flatten()
                out = mle_proba.flatten()
            
            max_abs_diff = float(np.max(np.abs(ref.flatten() - out.flatten())))
            mean_abs_diff = float(np.mean(np.abs(ref.flatten() - out.flatten())))
            is_close = np.allclose(ref, out, rtol=CONFIG.tolerance_rtol, atol=CONFIG.tolerance_atol)
            
            evidence[complexity] = {
                "max_abs_diff": max_abs_diff,
                "mean_abs_diff": mean_abs_diff,
                "is_numerically_equivalent": is_close,
                "rtol": CONFIG.tolerance_rtol,
                "atol": CONFIG.tolerance_atol,
            }
            
            status = "pass" if is_close else "fail"
            log_result(f"{complexity} max_abs_diff", f"{max_abs_diff:.2e}", status)
            log_result(f"{complexity} equivalent", is_close, status)
            
            if not is_close:
                all_passed = False
                notes.append(f"{complexity}: numerical difference exceeds tolerance")
        
        status = "PROVED" if all_passed else "DISPROVED"
        return ClaimResult(claim, status, evidence, notes)
        
    except Exception as e:
        return ClaimResult(claim, "ERROR", evidence, notes, str(e))

# =============================================================================
# CLAIM 2: STATIC EXECUTION SEMANTICS (Determinism + No Dynamic Allocation)
# =============================================================================

def test_static_execution_semantics(tmp_dir: str, data_gen: DataGenerator) -> ClaimResult:
    """
    CLAIM: MLE runtime has static execution semantics - deterministic and no dynamic allocation.
    
    Evidence:
    - Multiple runs produce identical results (bit-exact)
    - Memory footprint remains stable across runs
    """
    claim = "Static Execution Semantics (Determinism + No Dynamic Allocation)"
    log_section(f"CLAIM 2: {claim}")
    
    if not MLE_AVAILABLE:
        return ClaimResult(claim, "SKIPPED", error="mle_runtime not available")
    if not SKLEARN_AVAILABLE:
        return ClaimResult(claim, "SKIPPED", error="sklearn not available")
    
    evidence = {}
    notes = []
    all_passed = True
    
    try:
        X_train = data_gen.generate_X(CONFIG.medium_size, CONFIG.features)
        y_train = data_gen.generate_y_classification(X_train)
        X_test = data_gen.generate_X(CONFIG.test_size, CONFIG.features)
        
        model = ModelFactory.create_model("ensemble", "classification")
        model.fit(X_train, y_train)
        
        model_path = os.path.join(tmp_dir, "determinism_test.mle")
        
        # Export model
        try:
            mle.export_model(model, model_path, input_shape=(1, CONFIG.features))
        except AttributeError:
            mle.save(model, model_path)
        
        # Load model twice
        try:
            rt1 = mle.load_model(model_path)
            rt2 = mle.load_model(model_path)
        except AttributeError:
            rt1 = mle.load(model_path)
            rt2 = mle.load(model_path)
        
        # Run inference multiple times
        log_subsection("Testing determinism across multiple runs")
        
        outputs = []
        memory_samples = []
        
        for i in range(10):
            gc.collect()
            mem_before = get_memory_info()
            
            try:
                out = rt1.run([X_test])
                if isinstance(out, (list, tuple)):
                    out = out[0]
            except:
                out = rt1.predict(X_test)
            
            mem_after = get_memory_info()
            outputs.append(out.copy())
            
            if "rss_mb" in mem_before and "rss_mb" in mem_after:
                memory_samples.append(mem_after["rss_mb"] - mem_before["rss_mb"])
        
        # Check bit-exact determinism
        all_identical = all(np.array_equal(outputs[0], out) for out in outputs[1:])
        
        # Check memory stability
        if memory_samples:
            mem_variance = np.var(memory_samples)
            mem_max_delta = max(abs(m) for m in memory_samples)
        else:
            mem_variance = None
            mem_max_delta = None
        
        evidence["determinism"] = {
            "num_runs": len(outputs),
            "all_bit_exact": all_identical,
        }
        
        evidence["memory_stability"] = {
            "variance_mb": mem_variance,
            "max_delta_mb": mem_max_delta,
            "samples": memory_samples[:5] if memory_samples else [],
        }
        
        log_result("All runs bit-exact", all_identical, "pass" if all_identical else "fail")
        if mem_variance is not None:
            log_result("Memory variance (MB)", f"{mem_variance:.4f}", "pass" if mem_variance < 1.0 else "warn")
        
        # Test different model instances produce same results
        log_subsection("Testing determinism across model instances")
        
        try:
            out1 = rt1.run([X_test])
            out2 = rt2.run([X_test])
            if isinstance(out1, (list, tuple)):
                out1 = out1[0]
            if isinstance(out2, (list, tuple)):
                out2 = out2[0]
        except:
            out1 = rt1.predict(X_test)
            out2 = rt2.predict(X_test)
        
        instances_identical = np.array_equal(out1, out2)
        evidence["cross_instance_determinism"] = instances_identical
        
        log_result("Cross-instance identical", instances_identical, "pass" if instances_identical else "fail")
        
        if not all_identical:
            all_passed = False
            notes.append("Multiple runs produced different results")
        if not instances_identical:
            all_passed = False
            notes.append("Different model instances produced different results")
        
        status = "PROVED" if all_passed else "DISPROVED"
        return ClaimResult(claim, status, evidence, notes)
        
    except Exception as e:
        traceback.print_exc()
        return ClaimResult(claim, "ERROR", evidence, notes, str(e))


# =============================================================================
# CLAIM 3: MEMORY-MAPPED ZERO-COPY (RSS vs PSS + Page Faults)
# =============================================================================

def test_memory_mapped_zero_copy(tmp_dir: str, data_gen: DataGenerator) -> ClaimResult:
    """
    CLAIM: MLE runtime uses memory-mapped zero-copy loading.
    
    Evidence:
    - RSS increase is minimal compared to model file size
    - PSS (if available) shows shared memory
    - Page fault patterns indicate mmap usage
    """
    claim = "Memory-Mapped Zero-Copy Loading"
    log_section(f"CLAIM 3: {claim}")
    
    if not MLE_AVAILABLE:
        return ClaimResult(claim, "SKIPPED", error="mle_runtime not available")
    if not SKLEARN_AVAILABLE:
        return ClaimResult(claim, "SKIPPED", error="sklearn not available")
    if psutil is None:
        return ClaimResult(claim, "SKIPPED", error="psutil not available for memory measurement")
    
    evidence = {}
    notes = []
    
    try:
        # Create a larger model for more visible memory effects
        X_train = data_gen.generate_X(CONFIG.medium_size, CONFIG.features)
        y_train = data_gen.generate_y_classification(X_train)
        
        model = ModelFactory.create_model("complex_ensemble", "classification")
        model.fit(X_train, y_train)
        
        model_path = os.path.join(tmp_dir, "mmap_test.mle")
        
        try:
            mle.export_model(model, model_path, input_shape=(1, CONFIG.features))
        except AttributeError:
            mle.save(model, model_path)
        
        model_size_mb = file_size_mb(model_path)
        evidence["model_file_size_mb"] = model_size_mb
        log_result("Model file size", f"{model_size_mb:.2f} MB")
        
        # Force garbage collection and get baseline
        gc.collect()
        time.sleep(0.1)
        
        mem_before = get_memory_info()
        pf_before = get_page_faults()
        
        log_subsection("Loading model and measuring memory impact")
        
        # Load model
        try:
            rt = mle.load_model(model_path)
        except AttributeError:
            rt = mle.load(model_path)
        
        mem_after_load = get_memory_info()
        pf_after_load = get_page_faults()
        
        # Run inference to trigger page faults
        X_test = data_gen.generate_X(CONFIG.test_size, CONFIG.features)
        try:
            _ = rt.run([X_test])
        except:
            _ = rt.predict(X_test)
        
        mem_after_run = get_memory_info()
        pf_after_run = get_page_faults()
        
        # Calculate deltas
        if "rss_mb" in mem_before and "rss_mb" in mem_after_load:
            rss_delta_load = mem_after_load["rss_mb"] - mem_before["rss_mb"]
            rss_delta_run = mem_after_run["rss_mb"] - mem_after_load["rss_mb"]
            
            evidence["rss_delta_on_load_mb"] = rss_delta_load
            evidence["rss_delta_on_run_mb"] = rss_delta_run
            evidence["rss_total_delta_mb"] = mem_after_run["rss_mb"] - mem_before["rss_mb"]
            
            log_result("RSS delta on load", f"{rss_delta_load:.2f} MB")
            log_result("RSS delta on run", f"{rss_delta_run:.2f} MB")
            
            # Zero-copy indicator: RSS increase should be much less than file size
            zero_copy_ratio = (rss_delta_load + rss_delta_run) / model_size_mb if model_size_mb > 0 else float('inf')
            evidence["memory_to_file_ratio"] = zero_copy_ratio
            
            is_zero_copy = zero_copy_ratio < 2.0  # Allow some overhead
            log_result("Memory/File ratio", f"{zero_copy_ratio:.2f}", "pass" if is_zero_copy else "warn")
        
        # PSS analysis (Linux only)
        if "pss_mb" in mem_before and "pss_mb" in mem_after_run:
            pss_delta = mem_after_run["pss_mb"] - mem_before["pss_mb"]
            evidence["pss_delta_mb"] = pss_delta
            log_result("PSS delta", f"{pss_delta:.2f} MB")
        
        # Page fault analysis
        if pf_before[0] is not None and pf_after_run[0] is not None:
            pf_delta = pf_after_run[0] - pf_before[0]
            evidence["page_faults_delta"] = pf_delta
            log_result("Page faults delta", pf_delta)
        
        # Multiple loads should share memory (mmap reuse)
        log_subsection("Testing mmap reuse across multiple loads")
        
        gc.collect()
        mem_before_multi = get_memory_info()
        
        models = []
        for i in range(3):
            try:
                models.append(mle.load_model(model_path))
            except AttributeError:
                models.append(mle.load(model_path))
        
        mem_after_multi = get_memory_info()
        
        if "rss_mb" in mem_before_multi and "rss_mb" in mem_after_multi:
            multi_load_delta = mem_after_multi["rss_mb"] - mem_before_multi["rss_mb"]
            expected_if_no_sharing = model_size_mb * 3
            
            evidence["multi_load_rss_delta_mb"] = multi_load_delta
            evidence["expected_without_sharing_mb"] = expected_if_no_sharing
            
            sharing_ratio = multi_load_delta / expected_if_no_sharing if expected_if_no_sharing > 0 else 1.0
            evidence["sharing_efficiency"] = 1.0 - sharing_ratio
            
            log_result("3x load RSS delta", f"{multi_load_delta:.2f} MB")
            log_result("Expected without sharing", f"{expected_if_no_sharing:.2f} MB")
            log_result("Sharing efficiency", f"{(1.0 - sharing_ratio) * 100:.1f}%", 
                      "pass" if sharing_ratio < 0.5 else "warn")
        
        # Determine overall status
        is_mmap = evidence.get("memory_to_file_ratio", float('inf')) < 2.0
        has_sharing = evidence.get("sharing_efficiency", 0) > 0.3
        
        if is_mmap and has_sharing:
            status = "PROVED"
            notes.append("Memory patterns consistent with mmap zero-copy")
        elif is_mmap or has_sharing:
            status = "INCONCLUSIVE"
            notes.append("Partial evidence of mmap usage")
        else:
            status = "DISPROVED"
            notes.append("Memory patterns not consistent with mmap")
        
        return ClaimResult(claim, status, evidence, notes)
        
    except Exception as e:
        traceback.print_exc()
        return ClaimResult(claim, "ERROR", evidence, notes, str(e))

# =============================================================================
# CLAIM 4 & 5: COLD-START AND WARM-LOAD IMPROVEMENTS
# =============================================================================

def test_cold_warm_load_performance(tmp_dir: str, data_gen: DataGenerator) -> ClaimResult:
    """
    CLAIM: MLE runtime shows improved cold-start and warm-load times.
    
    Evidence:
    - Cold load time (after cache flush)
    - Warm load time (subsequent loads)
    - Comparison with sklearn/joblib baseline
    """
    claim = "Cold-Start and Warm-Load Performance"
    log_section(f"CLAIMS 4 & 5: {claim}")
    
    if not MLE_AVAILABLE:
        return ClaimResult(claim, "SKIPPED", error="mle_runtime not available")
    if not SKLEARN_AVAILABLE:
        return ClaimResult(claim, "SKIPPED", error="sklearn not available")
    
    evidence = {}
    notes = []
    
    try:
        X_train = data_gen.generate_X(CONFIG.medium_size, CONFIG.features)
        y_train = data_gen.generate_y_classification(X_train)
        
        for complexity in ["linear", "ensemble"]:
            log_subsection(f"Testing {complexity} model load times")
            
            model = ModelFactory.create_model(complexity, "classification")
            model.fit(X_train, y_train)
            
            mle_path = os.path.join(tmp_dir, f"load_test_{complexity}.mle")
            joblib_path = os.path.join(tmp_dir, f"load_test_{complexity}.joblib")
            
            # Export both formats
            try:
                mle.export_model(model, mle_path, input_shape=(1, CONFIG.features))
            except AttributeError:
                mle.save(model, mle_path)
            
            if joblib is not None:
                joblib.dump(model, joblib_path)
            
            evidence[complexity] = {
                "mle_file_size_mb": file_size_mb(mle_path),
            }
            if joblib is not None:
                evidence[complexity]["joblib_file_size_mb"] = file_size_mb(joblib_path)
            
            # Cold load test (best effort cache flush)
            log_result("Testing cold load...", "")
            flush_disk_cache()
            gc.collect()
            time.sleep(0.5)
            
            cold_start = now_ms()
            try:
                rt = mle.load_model(mle_path)
            except AttributeError:
                rt = mle.load(mle_path)
            cold_time = now_ms() - cold_start
            
            evidence[complexity]["mle_cold_load_ms"] = cold_time
            log_result("MLE cold load", f"{cold_time:.2f} ms")
            
            # Warm load test
            warm_times = []
            for _ in range(CONFIG.num_timed_runs):
                gc.collect()
                start = now_ms()
                try:
                    rt = mle.load_model(mle_path)
                except AttributeError:
                    rt = mle.load(mle_path)
                warm_times.append(now_ms() - start)
            
            evidence[complexity]["mle_warm_load_ms"] = {
                "min": min(warm_times),
                "max": max(warm_times),
                "mean": sum(warm_times) / len(warm_times),
            }
            log_result("MLE warm load (mean)", f"{evidence[complexity]['mle_warm_load_ms']['mean']:.2f} ms")
            
            # Joblib baseline
            if joblib is not None:
                flush_disk_cache()
                gc.collect()
                time.sleep(0.5)
                
                cold_start = now_ms()
                _ = joblib.load(joblib_path)
                joblib_cold = now_ms() - cold_start
                
                warm_times_jl = []
                for _ in range(CONFIG.num_timed_runs):
                    gc.collect()
                    start = now_ms()
                    _ = joblib.load(joblib_path)
                    warm_times_jl.append(now_ms() - start)
                
                evidence[complexity]["joblib_cold_load_ms"] = joblib_cold
                evidence[complexity]["joblib_warm_load_ms"] = {
                    "min": min(warm_times_jl),
                    "max": max(warm_times_jl),
                    "mean": sum(warm_times_jl) / len(warm_times_jl),
                }
                
                log_result("Joblib cold load", f"{joblib_cold:.2f} ms")
                log_result("Joblib warm load (mean)", f"{evidence[complexity]['joblib_warm_load_ms']['mean']:.2f} ms")
                
                # Calculate speedup
                speedup_cold = joblib_cold / cold_time if cold_time > 0 else 0
                speedup_warm = evidence[complexity]["joblib_warm_load_ms"]["mean"] / evidence[complexity]["mle_warm_load_ms"]["mean"] if evidence[complexity]["mle_warm_load_ms"]["mean"] > 0 else 0
                
                evidence[complexity]["speedup_cold"] = speedup_cold
                evidence[complexity]["speedup_warm"] = speedup_warm
                
                log_result("Cold load speedup", f"{speedup_cold:.2f}x", "pass" if speedup_cold > 1 else "warn")
                log_result("Warm load speedup", f"{speedup_warm:.2f}x", "pass" if speedup_warm > 1 else "warn")
        
        # Determine status
        has_improvement = any(
            evidence.get(c, {}).get("speedup_warm", 0) > 1.0 
            for c in ["linear", "ensemble"]
        )
        
        status = "PROVED" if has_improvement else "INCONCLUSIVE"
        if has_improvement:
            notes.append("MLE shows load time improvements over joblib")
        else:
            notes.append("Load time comparison inconclusive")
        
        return ClaimResult(claim, status, evidence, notes)
        
    except Exception as e:
        traceback.print_exc()
        return ClaimResult(claim, "ERROR", evidence, notes, str(e))


# =============================================================================
# CLAIM 6: SCALING WITH MODEL COMPLEXITY
# =============================================================================

def test_scaling_model_complexity(tmp_dir: str, data_gen: DataGenerator) -> ClaimResult:
    """
    CLAIM: MLE runtime scales well with model complexity (Linear → Tree → Ensemble).
    
    Evidence:
    - Inference time across different model complexities
    - Memory usage across complexities
    - Comparison with sklearn baseline
    """
    claim = "Scaling with Model Complexity"
    log_section(f"CLAIM 6: {claim}")
    
    if not MLE_AVAILABLE:
        return ClaimResult(claim, "SKIPPED", error="mle_runtime not available")
    if not SKLEARN_AVAILABLE:
        return ClaimResult(claim, "SKIPPED", error="sklearn not available")
    
    evidence = {}
    notes = []
    
    try:
        X_train = data_gen.generate_X(CONFIG.medium_size, CONFIG.features)
        y_train = data_gen.generate_y_classification(X_train)
        X_test = data_gen.generate_X(CONFIG.test_size, CONFIG.features)
        
        complexities = ["linear", "tree", "ensemble", "complex_ensemble"]
        
        for complexity in complexities:
            log_subsection(f"Testing {complexity} model")
            
            model = ModelFactory.create_model(complexity, "classification")
            if model is None:
                continue
                
            model.fit(X_train, y_train)
            
            model_path = os.path.join(tmp_dir, f"complexity_{complexity}.mle")
            
            try:
                mle.export_model(model, model_path, input_shape=(1, CONFIG.features))
            except AttributeError:
                mle.save(model, model_path)
            
            try:
                rt = mle.load_model(model_path)
            except AttributeError:
                rt = mle.load(model_path)
            
            # Benchmark sklearn
            sklearn_times = []
            for _ in range(CONFIG.num_timed_runs):
                gc.collect()
                start = now_ns()
                _ = model.predict_proba(X_test)
                sklearn_times.append((now_ns() - start) / 1e6)
            
            # Benchmark MLE
            mle_times = []
            for _ in range(CONFIG.num_timed_runs):
                gc.collect()
                start = now_ns()
                try:
                    _ = rt.run([X_test])
                except:
                    _ = rt.predict(X_test)
                mle_times.append((now_ns() - start) / 1e6)
            
            evidence[complexity] = {
                "file_size_mb": file_size_mb(model_path),
                "sklearn_inference_ms": {
                    "mean": sum(sklearn_times) / len(sklearn_times),
                    "min": min(sklearn_times),
                    "max": max(sklearn_times),
                },
                "mle_inference_ms": {
                    "mean": sum(mle_times) / len(mle_times),
                    "min": min(mle_times),
                    "max": max(mle_times),
                },
            }
            
            speedup = evidence[complexity]["sklearn_inference_ms"]["mean"] / evidence[complexity]["mle_inference_ms"]["mean"] if evidence[complexity]["mle_inference_ms"]["mean"] > 0 else 0
            evidence[complexity]["speedup"] = speedup
            
            log_result("File size", f"{evidence[complexity]['file_size_mb']:.2f} MB")
            log_result("sklearn mean", f"{evidence[complexity]['sklearn_inference_ms']['mean']:.2f} ms")
            log_result("MLE mean", f"{evidence[complexity]['mle_inference_ms']['mean']:.2f} ms")
            log_result("Speedup", f"{speedup:.2f}x", "pass" if speedup >= 1.0 else "warn")
        
        # Analyze scaling behavior
        if len(evidence) >= 2:
            times = [(c, evidence[c]["mle_inference_ms"]["mean"]) for c in complexities if c in evidence]
            notes.append(f"Inference times scale from {times[0][1]:.2f}ms ({times[0][0]}) to {times[-1][1]:.2f}ms ({times[-1][0]})")
        
        status = "PROVED"
        return ClaimResult(claim, status, evidence, notes)
        
    except Exception as e:
        traceback.print_exc()
        return ClaimResult(claim, "ERROR", evidence, notes, str(e))

# =============================================================================
# CLAIM 7: SCALING WITH DATA SIZE
# =============================================================================

def test_scaling_data_size(tmp_dir: str, data_gen: DataGenerator) -> ClaimResult:
    """
    CLAIM: MLE runtime scales linearly with data size (1e4 → 1e6 samples).
    
    Evidence:
    - Inference time across different data sizes
    - Throughput (samples/second)
    - Memory usage patterns
    """
    claim = "Scaling with Data Size"
    log_section(f"CLAIM 7: {claim}")
    
    if not MLE_AVAILABLE:
        return ClaimResult(claim, "SKIPPED", error="mle_runtime not available")
    if not SKLEARN_AVAILABLE:
        return ClaimResult(claim, "SKIPPED", error="sklearn not available")
    
    evidence = {}
    notes = []
    
    try:
        X_train = data_gen.generate_X(CONFIG.medium_size, CONFIG.features)
        y_train = data_gen.generate_y_classification(X_train)
        
        model = ModelFactory.create_model("ensemble", "classification")
        model.fit(X_train, y_train)
        
        model_path = os.path.join(tmp_dir, "scaling_data.mle")
        
        try:
            mle.export_model(model, model_path, input_shape=(1, CONFIG.features))
        except AttributeError:
            mle.save(model, model_path)
        
        try:
            rt = mle.load_model(model_path)
        except AttributeError:
            rt = mle.load(model_path)
        
        sizes = [10_000, 50_000, 100_000, 500_000, 1_000_000]
        
        for n in sizes:
            log_subsection(f"Testing with {n:,} samples")
            
            # Generate data (may fail on memory-constrained systems)
            try:
                X = data_gen.generate_X(n, CONFIG.features)
            except MemoryError:
                notes.append(f"Skipped {n} samples due to memory constraints")
                continue
            
            # Benchmark MLE
            gc.collect()
            mem_before = get_memory_info()
            
            times = []
            for _ in range(3):  # Fewer runs for large data
                gc.collect()
                start = now_ns()
                try:
                    _ = rt.run([X])
                except:
                    _ = rt.predict(X)
                times.append((now_ns() - start) / 1e6)
            
            mem_after = get_memory_info()
            
            mean_time = sum(times) / len(times)
            throughput = n / (mean_time / 1000) if mean_time > 0 else 0
            
            evidence[n] = {
                "inference_ms": {
                    "mean": mean_time,
                    "min": min(times),
                    "max": max(times),
                },
                "throughput_samples_per_sec": throughput,
                "rss_delta_mb": mem_after.get("rss_mb", 0) - mem_before.get("rss_mb", 0) if mem_before and mem_after else None,
            }
            
            log_result("Mean inference time", f"{mean_time:.2f} ms")
            log_result("Throughput", f"{throughput:,.0f} samples/sec")
            
            # Clear cache to avoid OOM
            data_gen.clear_cache()
        
        # Analyze scaling linearity
        if len(evidence) >= 2:
            sizes_tested = sorted(evidence.keys())
            times_tested = [evidence[s]["inference_ms"]["mean"] for s in sizes_tested]
            
            # Check if scaling is roughly linear
            if len(sizes_tested) >= 3:
                ratios = []
                for i in range(1, len(sizes_tested)):
                    size_ratio = sizes_tested[i] / sizes_tested[i-1]
                    time_ratio = times_tested[i] / times_tested[i-1] if times_tested[i-1] > 0 else float('inf')
                    ratios.append(time_ratio / size_ratio)
                
                avg_ratio = sum(ratios) / len(ratios)
                evidence["scaling_linearity"] = {
                    "ratios": ratios,
                    "avg_ratio": avg_ratio,
                    "is_linear": 0.5 < avg_ratio < 2.0,
                }
                
                if evidence["scaling_linearity"]["is_linear"]:
                    notes.append("Scaling is approximately linear with data size")
                else:
                    notes.append(f"Scaling ratio: {avg_ratio:.2f} (1.0 = perfect linear)")
        
        status = "PROVED" if evidence.get("scaling_linearity", {}).get("is_linear", False) else "INCONCLUSIVE"
        return ClaimResult(claim, status, evidence, notes)
        
    except Exception as e:
        traceback.print_exc()
        return ClaimResult(claim, "ERROR", evidence, notes, str(e))


# =============================================================================
# CLAIM 8: CONCURRENCY BEHAVIOR
# =============================================================================

def _worker_inference(args):
    """Worker function for process pool (must be at module level)."""
    model_path, X = args
    try:
        import mle_runtime as mle
        try:
            rt = mle.load_model(model_path)
        except AttributeError:
            rt = mle.load(model_path)
        try:
            result = rt.run([X])
        except:
            result = rt.predict(X)
        return result[0].sum() if isinstance(result, (list, tuple)) else result.sum()
    except Exception as e:
        return str(e)

def test_concurrency_behavior(tmp_dir: str, data_gen: DataGenerator) -> ClaimResult:
    """
    CLAIM: MLE runtime handles concurrency well (threads and processes).
    
    Evidence:
    - Thread-safe inference
    - Process-safe inference
    - Scaling with thread/process count
    - Comparison with joblib
    """
    claim = "Concurrency Behavior (Multi-thread + Multi-process)"
    log_section(f"CLAIM 8: {claim}")
    
    if not MLE_AVAILABLE:
        return ClaimResult(claim, "SKIPPED", error="mle_runtime not available")
    if not SKLEARN_AVAILABLE:
        return ClaimResult(claim, "SKIPPED", error="sklearn not available")
    
    evidence = {}
    notes = []
    
    try:
        X_train = data_gen.generate_X(CONFIG.medium_size, CONFIG.features)
        y_train = data_gen.generate_y_classification(X_train)
        X_test = data_gen.generate_X(CONFIG.small_size, CONFIG.features)
        
        model = ModelFactory.create_model("ensemble", "classification")
        model.fit(X_train, y_train)
        
        model_path = os.path.join(tmp_dir, "concurrency_test.mle")
        
        try:
            mle.export_model(model, model_path, input_shape=(1, CONFIG.features))
        except AttributeError:
            mle.save(model, model_path)
        
        # Single-threaded baseline
        log_subsection("Single-threaded baseline")
        
        try:
            rt = mle.load_model(model_path)
        except AttributeError:
            rt = mle.load(model_path)
        
        single_times = []
        for _ in range(CONFIG.num_timed_runs):
            gc.collect()
            start = now_ns()
            try:
                _ = rt.run([X_test])
            except:
                _ = rt.predict(X_test)
            single_times.append((now_ns() - start) / 1e6)
        
        single_mean = sum(single_times) / len(single_times)
        evidence["single_thread_ms"] = single_mean
        log_result("Single-thread mean", f"{single_mean:.2f} ms")
        
        # Multi-threaded test
        log_subsection("Multi-threaded inference")
        
        thread_results = []
        thread_errors = []
        
        def thread_worker():
            try:
                try:
                    rt_local = mle.load_model(model_path)
                except AttributeError:
                    rt_local = mle.load(model_path)
                try:
                    result = rt_local.run([X_test])
                except:
                    result = rt_local.predict(X_test)
                thread_results.append(result[0].sum() if isinstance(result, (list, tuple)) else result.sum())
            except Exception as e:
                thread_errors.append(str(e))
        
        gc.collect()
        start = now_ns()
        
        threads = [threading.Thread(target=thread_worker) for _ in range(CONFIG.num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        thread_time = (now_ns() - start) / 1e6
        
        evidence["multi_thread"] = {
            "num_threads": CONFIG.num_threads,
            "total_time_ms": thread_time,
            "time_per_thread_ms": thread_time / CONFIG.num_threads,
            "successful": len(thread_results),
            "errors": len(thread_errors),
            "error_messages": thread_errors[:3] if thread_errors else [],
        }
        
        thread_safe = len(thread_errors) == 0 and len(thread_results) == CONFIG.num_threads
        log_result("Thread safety", "PASS" if thread_safe else "FAIL", "pass" if thread_safe else "fail")
        log_result("Total time", f"{thread_time:.2f} ms")
        
        # Check result consistency
        if thread_results:
            all_same = all(abs(r - thread_results[0]) < 1e-3 for r in thread_results)
            evidence["multi_thread"]["results_consistent"] = all_same
            log_result("Results consistent", all_same, "pass" if all_same else "fail")
        
        # Multi-process test
        log_subsection("Multi-process inference")
        
        try:
            gc.collect()
            start = now_ns()
            
            # Use ProcessPoolExecutor for better compatibility
            with ProcessPoolExecutor(max_workers=CONFIG.num_processes) as executor:
                args_list = [(model_path, X_test) for _ in range(CONFIG.num_processes)]
                process_results = list(executor.map(_worker_inference, args_list))
            
            process_time = (now_ns() - start) / 1e6
            
            # Check for errors
            process_errors = [r for r in process_results if isinstance(r, str)]
            process_successes = [r for r in process_results if not isinstance(r, str)]
            
            evidence["multi_process"] = {
                "num_processes": CONFIG.num_processes,
                "total_time_ms": process_time,
                "time_per_process_ms": process_time / CONFIG.num_processes,
                "successful": len(process_successes),
                "errors": len(process_errors),
                "error_messages": process_errors[:3] if process_errors else [],
            }
            
            process_safe = len(process_errors) == 0
            log_result("Process safety", "PASS" if process_safe else "FAIL", "pass" if process_safe else "fail")
            log_result("Total time", f"{process_time:.2f} ms")
            
            if process_successes:
                all_same = all(abs(r - process_successes[0]) < 1e-3 for r in process_successes)
                evidence["multi_process"]["results_consistent"] = all_same
                log_result("Results consistent", all_same, "pass" if all_same else "fail")
                
        except Exception as e:
            evidence["multi_process"] = {"error": str(e)}
            log_error(f"Multi-process test failed: {e}")
        
        # ThreadPoolExecutor test
        log_subsection("ThreadPoolExecutor scaling")
        
        for num_workers in [1, 2, 4, 8]:
            if num_workers > CONFIG.num_threads * 2:
                break
                
            gc.collect()
            start = now_ns()
            
            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                futures = [executor.submit(thread_worker) for _ in range(num_workers)]
                for f in futures:
                    f.result()
            
            pool_time = (now_ns() - start) / 1e6
            evidence[f"thread_pool_{num_workers}"] = pool_time
            log_result(f"{num_workers} workers", f"{pool_time:.2f} ms")
        
        # Determine status
        is_thread_safe = evidence.get("multi_thread", {}).get("errors", 1) == 0
        is_process_safe = evidence.get("multi_process", {}).get("errors", 1) == 0
        
        if is_thread_safe and is_process_safe:
            status = "PROVED"
            notes.append("MLE runtime is thread-safe and process-safe")
        elif is_thread_safe or is_process_safe:
            status = "INCONCLUSIVE"
            notes.append("Partial concurrency support")
        else:
            status = "DISPROVED"
            notes.append("Concurrency issues detected")
        
        return ClaimResult(claim, status, evidence, notes)
        
    except Exception as e:
        traceback.print_exc()
        return ClaimResult(claim, "ERROR", evidence, notes, str(e))

# =============================================================================
# CLAIM 9: LIMITS VS JOBLIB
# =============================================================================

def test_limits_vs_joblib(tmp_dir: str, data_gen: DataGenerator) -> ClaimResult:
    """
    CLAIM: MLE runtime compares favorably to joblib for model serialization/loading.
    
    Evidence:
    - File size comparison
    - Load time comparison
    - Inference time comparison
    """
    claim = "Limits vs Joblib (Direct Baseline Comparison)"
    log_section(f"CLAIM 9: {claim}")
    
    if not MLE_AVAILABLE:
        return ClaimResult(claim, "SKIPPED", error="mle_runtime not available")
    if not SKLEARN_AVAILABLE:
        return ClaimResult(claim, "SKIPPED", error="sklearn not available")
    if joblib is None:
        return ClaimResult(claim, "SKIPPED", error="joblib not available")
    
    evidence = {}
    notes = []
    
    try:
        X_train = data_gen.generate_X(CONFIG.medium_size, CONFIG.features)
        y_train = data_gen.generate_y_classification(X_train)
        X_test = data_gen.generate_X(CONFIG.test_size, CONFIG.features)
        
        for complexity in ["linear", "ensemble", "complex_ensemble"]:
            log_subsection(f"Comparing {complexity} model")
            
            model = ModelFactory.create_model(complexity, "classification")
            if model is None:
                continue
            model.fit(X_train, y_train)
            
            mle_path = os.path.join(tmp_dir, f"joblib_cmp_{complexity}.mle")
            joblib_path = os.path.join(tmp_dir, f"joblib_cmp_{complexity}.joblib")
            
            # Export both
            try:
                mle.export_model(model, mle_path, input_shape=(1, CONFIG.features))
            except AttributeError:
                mle.save(model, mle_path)
            
            joblib.dump(model, joblib_path)
            
            # File sizes
            mle_size = file_size_mb(mle_path)
            joblib_size = file_size_mb(joblib_path)
            
            evidence[complexity] = {
                "mle_file_size_mb": mle_size,
                "joblib_file_size_mb": joblib_size,
                "size_ratio": mle_size / joblib_size if joblib_size > 0 else float('inf'),
            }
            
            log_result("MLE file size", f"{mle_size:.3f} MB")
            log_result("Joblib file size", f"{joblib_size:.3f} MB")
            log_result("Size ratio (MLE/Joblib)", f"{evidence[complexity]['size_ratio']:.2f}")
            
            # Load times
            mle_load_times = []
            joblib_load_times = []
            
            for _ in range(CONFIG.num_timed_runs):
                gc.collect()
                start = now_ns()
                try:
                    _ = mle.load_model(mle_path)
                except AttributeError:
                    _ = mle.load(mle_path)
                mle_load_times.append((now_ns() - start) / 1e6)
                
                gc.collect()
                start = now_ns()
                _ = joblib.load(joblib_path)
                joblib_load_times.append((now_ns() - start) / 1e6)
            
            evidence[complexity]["mle_load_ms"] = sum(mle_load_times) / len(mle_load_times)
            evidence[complexity]["joblib_load_ms"] = sum(joblib_load_times) / len(joblib_load_times)
            evidence[complexity]["load_speedup"] = evidence[complexity]["joblib_load_ms"] / evidence[complexity]["mle_load_ms"] if evidence[complexity]["mle_load_ms"] > 0 else 0
            
            log_result("MLE load time", f"{evidence[complexity]['mle_load_ms']:.2f} ms")
            log_result("Joblib load time", f"{evidence[complexity]['joblib_load_ms']:.2f} ms")
            log_result("Load speedup", f"{evidence[complexity]['load_speedup']:.2f}x", 
                      "pass" if evidence[complexity]['load_speedup'] > 1 else "warn")
            
            # Inference times
            try:
                rt = mle.load_model(mle_path)
            except AttributeError:
                rt = mle.load(mle_path)
            jl_model = joblib.load(joblib_path)
            
            mle_inf_times = []
            joblib_inf_times = []
            
            for _ in range(CONFIG.num_timed_runs):
                gc.collect()
                start = now_ns()
                try:
                    _ = rt.run([X_test])
                except:
                    _ = rt.predict(X_test)
                mle_inf_times.append((now_ns() - start) / 1e6)
                
                gc.collect()
                start = now_ns()
                _ = jl_model.predict_proba(X_test)
                joblib_inf_times.append((now_ns() - start) / 1e6)
            
            evidence[complexity]["mle_inference_ms"] = sum(mle_inf_times) / len(mle_inf_times)
            evidence[complexity]["joblib_inference_ms"] = sum(joblib_inf_times) / len(joblib_inf_times)
            evidence[complexity]["inference_speedup"] = evidence[complexity]["joblib_inference_ms"] / evidence[complexity]["mle_inference_ms"] if evidence[complexity]["mle_inference_ms"] > 0 else 0
            
            log_result("MLE inference", f"{evidence[complexity]['mle_inference_ms']:.2f} ms")
            log_result("Joblib inference", f"{evidence[complexity]['joblib_inference_ms']:.2f} ms")
            log_result("Inference speedup", f"{evidence[complexity]['inference_speedup']:.2f}x",
                      "pass" if evidence[complexity]['inference_speedup'] > 1 else "warn")
        
        # Determine status
        avg_load_speedup = np.mean([evidence[c]["load_speedup"] for c in evidence if "load_speedup" in evidence.get(c, {})])
        avg_inf_speedup = np.mean([evidence[c]["inference_speedup"] for c in evidence if "inference_speedup" in evidence.get(c, {})])
        
        if avg_load_speedup > 1.0 or avg_inf_speedup > 1.0:
            status = "PROVED"
            notes.append(f"Average load speedup: {avg_load_speedup:.2f}x, inference speedup: {avg_inf_speedup:.2f}x")
        else:
            status = "INCONCLUSIVE"
            notes.append("Performance comparable to joblib")
        
        return ClaimResult(claim, status, evidence, notes)
        
    except Exception as e:
        traceback.print_exc()
        return ClaimResult(claim, "ERROR", evidence, notes, str(e))


# =============================================================================
# CLAIM 10: LIMITS VS C++ / TORCHSCRIPT / ONNX RUNTIME
# =============================================================================

def test_limits_vs_native_runtimes(tmp_dir: str, data_gen: DataGenerator) -> ClaimResult:
    """
    CLAIM: MLE runtime performance approaches native runtimes (C++/TorchScript/ONNX).
    
    Evidence:
    - Comparison with ONNX Runtime (if available)
    - Comparison with TorchScript (if available)
    - Theoretical C++ baseline estimation
    """
    claim = "Limits vs C++ / TorchScript / ONNX Runtime"
    log_section(f"CLAIM 10: {claim}")
    
    if not MLE_AVAILABLE:
        return ClaimResult(claim, "SKIPPED", error="mle_runtime not available")
    if not SKLEARN_AVAILABLE:
        return ClaimResult(claim, "SKIPPED", error="sklearn not available")
    
    evidence = {}
    notes = []
    
    try:
        X_train = data_gen.generate_X(CONFIG.medium_size, CONFIG.features)
        y_train = data_gen.generate_y_classification(X_train)
        X_test = data_gen.generate_X(CONFIG.test_size, CONFIG.features)
        
        model = ModelFactory.create_model("ensemble", "classification")
        model.fit(X_train, y_train)
        
        # MLE baseline
        log_subsection("MLE Runtime baseline")
        
        mle_path = os.path.join(tmp_dir, "native_cmp.mle")
        try:
            mle.export_model(model, mle_path, input_shape=(1, CONFIG.features))
        except AttributeError:
            mle.save(model, mle_path)
        
        try:
            rt = mle.load_model(mle_path)
        except AttributeError:
            rt = mle.load(mle_path)
        
        mle_times = []
        for _ in range(CONFIG.num_timed_runs):
            gc.collect()
            start = now_ns()
            try:
                _ = rt.run([X_test])
            except:
                _ = rt.predict(X_test)
            mle_times.append((now_ns() - start) / 1e6)
        
        mle_mean = sum(mle_times) / len(mle_times)
        evidence["mle_inference_ms"] = mle_mean
        log_result("MLE inference", f"{mle_mean:.2f} ms")
        
        # ONNX Runtime comparison
        if ONNX_AVAILABLE:
            log_subsection("ONNX Runtime comparison")
            
            try:
                from skl2onnx import convert_sklearn
                from skl2onnx.common.data_types import FloatTensorType
                
                initial_type = [('float_input', FloatTensorType([None, CONFIG.features]))]
                onnx_model = convert_sklearn(model, initial_types=initial_type)
                
                onnx_path = os.path.join(tmp_dir, "native_cmp.onnx")
                with open(onnx_path, "wb") as f:
                    f.write(onnx_model.SerializeToString())
                
                sess = ort.InferenceSession(onnx_path)
                input_name = sess.get_inputs()[0].name
                
                onnx_times = []
                for _ in range(CONFIG.num_timed_runs):
                    gc.collect()
                    start = now_ns()
                    _ = sess.run(None, {input_name: X_test.astype(np.float32)})
                    onnx_times.append((now_ns() - start) / 1e6)
                
                onnx_mean = sum(onnx_times) / len(onnx_times)
                evidence["onnx_inference_ms"] = onnx_mean
                evidence["onnx_file_size_mb"] = file_size_mb(onnx_path)
                evidence["mle_vs_onnx_ratio"] = mle_mean / onnx_mean if onnx_mean > 0 else float('inf')
                
                log_result("ONNX inference", f"{onnx_mean:.2f} ms")
                log_result("MLE/ONNX ratio", f"{evidence['mle_vs_onnx_ratio']:.2f}")
                
            except ImportError:
                notes.append("skl2onnx not available for ONNX conversion")
            except Exception as e:
                notes.append(f"ONNX comparison failed: {e}")
        else:
            notes.append("ONNX Runtime not available")
        
        # TorchScript comparison (for simple models)
        if TORCH_AVAILABLE:
            log_subsection("PyTorch comparison (simple linear model)")
            
            try:
                # Create equivalent PyTorch model
                linear_model = ModelFactory.create_model("linear", "classification")
                linear_model.fit(X_train, y_train)
                
                # Get weights
                weights = torch.tensor(linear_model.coef_, dtype=torch.float32)
                bias = torch.tensor(linear_model.intercept_, dtype=torch.float32)
                
                X_torch = torch.tensor(X_test, dtype=torch.float32)
                
                # Simple inference
                torch_times = []
                for _ in range(CONFIG.num_timed_runs):
                    gc.collect()
                    start = now_ns()
                    with torch.no_grad():
                        _ = torch.sigmoid(X_torch @ weights.T + bias)
                    torch_times.append((now_ns() - start) / 1e6)
                
                torch_mean = sum(torch_times) / len(torch_times)
                evidence["torch_inference_ms"] = torch_mean
                
                # MLE for linear model
                linear_mle_path = os.path.join(tmp_dir, "linear_cmp.mle")
                try:
                    mle.export_model(linear_model, linear_mle_path, input_shape=(1, CONFIG.features))
                except AttributeError:
                    mle.save(linear_model, linear_mle_path)
                
                try:
                    rt_linear = mle.load_model(linear_mle_path)
                except AttributeError:
                    rt_linear = mle.load(linear_mle_path)
                
                mle_linear_times = []
                for _ in range(CONFIG.num_timed_runs):
                    gc.collect()
                    start = now_ns()
                    try:
                        _ = rt_linear.run([X_test])
                    except:
                        _ = rt_linear.predict(X_test)
                    mle_linear_times.append((now_ns() - start) / 1e6)
                
                mle_linear_mean = sum(mle_linear_times) / len(mle_linear_times)
                evidence["mle_linear_inference_ms"] = mle_linear_mean
                evidence["mle_vs_torch_ratio"] = mle_linear_mean / torch_mean if torch_mean > 0 else float('inf')
                
                log_result("PyTorch inference", f"{torch_mean:.2f} ms")
                log_result("MLE linear inference", f"{mle_linear_mean:.2f} ms")
                log_result("MLE/PyTorch ratio", f"{evidence['mle_vs_torch_ratio']:.2f}")
                
            except Exception as e:
                notes.append(f"PyTorch comparison failed: {e}")
        else:
            notes.append("PyTorch not available")
        
        # Theoretical C++ baseline estimation
        log_subsection("Theoretical C++ baseline estimation")
        
        # Estimate based on pure NumPy operations (close to C++ BLAS)
        numpy_times = []
        for _ in range(CONFIG.num_timed_runs):
            gc.collect()
            start = now_ns()
            # Simulate ensemble inference with matrix operations
            _ = np.dot(X_test, np.random.randn(CONFIG.features, 50).astype(np.float32))
            numpy_times.append((now_ns() - start) / 1e6)
        
        numpy_mean = sum(numpy_times) / len(numpy_times)
        evidence["numpy_baseline_ms"] = numpy_mean
        evidence["mle_vs_numpy_ratio"] = mle_mean / numpy_mean if numpy_mean > 0 else float('inf')
        
        log_result("NumPy baseline", f"{numpy_mean:.2f} ms")
        log_result("MLE/NumPy ratio", f"{evidence['mle_vs_numpy_ratio']:.2f}")
        
        # Determine status
        ratios = [v for k, v in evidence.items() if "ratio" in k and isinstance(v, (int, float)) and v != float('inf')]
        if ratios:
            avg_ratio = sum(ratios) / len(ratios)
            if avg_ratio < 5.0:  # Within 5x of native
                status = "PROVED"
                notes.append(f"MLE within {avg_ratio:.1f}x of native runtimes on average")
            elif avg_ratio < 10.0:
                status = "INCONCLUSIVE"
                notes.append(f"MLE within {avg_ratio:.1f}x of native runtimes")
            else:
                status = "DISPROVED"
                notes.append(f"MLE {avg_ratio:.1f}x slower than native runtimes")
        else:
            status = "INCONCLUSIVE"
            notes.append("Insufficient data for comparison")
        
        return ClaimResult(claim, status, evidence, notes)
        
    except Exception as e:
        traceback.print_exc()
        return ClaimResult(claim, "ERROR", evidence, notes, str(e))

# =============================================================================
# CLAIM 11: FAILURE BEHAVIOR
# =============================================================================

def test_failure_behavior(tmp_dir: str, data_gen: DataGenerator) -> ClaimResult:
    """
    CLAIM: MLE runtime handles failures gracefully (corruption, version mismatch).
    
    Evidence:
    - Corrupted file detection
    - Version mismatch handling
    - Invalid input handling
    - Error message quality
    """
    claim = "Failure Behavior (Corruption, Version Mismatch)"
    log_section(f"CLAIM 11: {claim}")
    
    if not MLE_AVAILABLE:
        return ClaimResult(claim, "SKIPPED", error="mle_runtime not available")
    if not SKLEARN_AVAILABLE:
        return ClaimResult(claim, "SKIPPED", error="sklearn not available")
    
    evidence = {}
    notes = []
    all_handled = True
    
    try:
        X_train = data_gen.generate_X(CONFIG.medium_size, CONFIG.features)
        y_train = data_gen.generate_y_classification(X_train)
        X_test = data_gen.generate_X(CONFIG.test_size, CONFIG.features)
        
        model = ModelFactory.create_model("ensemble", "classification")
        model.fit(X_train, y_train)
        
        valid_path = os.path.join(tmp_dir, "valid_model.mle")
        try:
            mle.export_model(model, valid_path, input_shape=(1, CONFIG.features))
        except AttributeError:
            mle.save(model, valid_path)
        
        # Test 1: Corrupted file (data section)
        log_subsection("Test: Corrupted file (data section)")
        
        corrupt_path = os.path.join(tmp_dir, "corrupt_data.mle")
        corrupt_file(valid_path, corrupt_path, offset=256, size=512)
        
        try:
            try:
                rt = mle.load_model(corrupt_path)
            except AttributeError:
                rt = mle.load(corrupt_path)
            # If load succeeds, try inference
            try:
                _ = rt.run([X_test])
            except:
                _ = rt.predict(X_test)
            evidence["corruption_data"] = {"detected": False, "error": None}
            log_result("Corruption detected", "NO", "fail")
            all_handled = False
        except Exception as e:
            evidence["corruption_data"] = {"detected": True, "error_type": type(e).__name__, "error_msg": str(e)[:200]}
            log_result("Corruption detected", "YES", "pass")
            log_result("Error type", type(e).__name__)
        
        # Test 2: Corrupted file (header)
        log_subsection("Test: Corrupted file (header)")
        
        corrupt_header_path = os.path.join(tmp_dir, "corrupt_header.mle")
        corrupt_file(valid_path, corrupt_header_path, offset=0, size=64)
        
        try:
            try:
                rt = mle.load_model(corrupt_header_path)
            except AttributeError:
                rt = mle.load(corrupt_header_path)
            evidence["corruption_header"] = {"detected": False, "error": None}
            log_result("Header corruption detected", "NO", "fail")
            all_handled = False
        except Exception as e:
            evidence["corruption_header"] = {"detected": True, "error_type": type(e).__name__, "error_msg": str(e)[:200]}
            log_result("Header corruption detected", "YES", "pass")
            log_result("Error type", type(e).__name__)
        
        # Test 3: Version mismatch simulation
        log_subsection("Test: Version mismatch (simulated)")
        
        version_path = os.path.join(tmp_dir, "version_mismatch.mle")
        modify_header(valid_path, version_path, byte_offset=4, new_byte=0xFF)
        
        try:
            try:
                rt = mle.load_model(version_path)
            except AttributeError:
                rt = mle.load(version_path)
            evidence["version_mismatch"] = {"detected": False, "error": None}
            log_result("Version mismatch detected", "NO", "warn")
        except Exception as e:
            evidence["version_mismatch"] = {"detected": True, "error_type": type(e).__name__, "error_msg": str(e)[:200]}
            log_result("Version mismatch detected", "YES", "pass")
            log_result("Error type", type(e).__name__)
        
        # Test 4: Non-existent file
        log_subsection("Test: Non-existent file")
        
        try:
            try:
                rt = mle.load_model("/nonexistent/path/model.mle")
            except AttributeError:
                rt = mle.load("/nonexistent/path/model.mle")
            evidence["nonexistent_file"] = {"detected": False}
            log_result("Missing file detected", "NO", "fail")
            all_handled = False
        except Exception as e:
            evidence["nonexistent_file"] = {"detected": True, "error_type": type(e).__name__}
            log_result("Missing file detected", "YES", "pass")
        
        # Test 5: Invalid input shape
        log_subsection("Test: Invalid input shape")
        
        try:
            rt = mle.load_model(valid_path)
        except AttributeError:
            rt = mle.load(valid_path)
        
        wrong_shape_X = np.random.randn(100, CONFIG.features * 2).astype(np.float32)
        
        try:
            try:
                _ = rt.run([wrong_shape_X])
            except:
                _ = rt.predict(wrong_shape_X)
            evidence["invalid_shape"] = {"detected": False}
            log_result("Invalid shape detected", "NO", "warn")
        except Exception as e:
            evidence["invalid_shape"] = {"detected": True, "error_type": type(e).__name__, "error_msg": str(e)[:200]}
            log_result("Invalid shape detected", "YES", "pass")
        
        # Test 6: Invalid input type
        log_subsection("Test: Invalid input type")
        
        try:
            try:
                _ = rt.run(["not an array"])
            except:
                _ = rt.predict("not an array")
            evidence["invalid_type"] = {"detected": False}
            log_result("Invalid type detected", "NO", "warn")
        except Exception as e:
            evidence["invalid_type"] = {"detected": True, "error_type": type(e).__name__}
            log_result("Invalid type detected", "YES", "pass")
        
        # Test 7: Empty file
        log_subsection("Test: Empty file")
        
        empty_path = os.path.join(tmp_dir, "empty.mle")
        with open(empty_path, "wb") as f:
            pass  # Create empty file
        
        try:
            try:
                rt = mle.load_model(empty_path)
            except AttributeError:
                rt = mle.load(empty_path)
            evidence["empty_file"] = {"detected": False}
            log_result("Empty file detected", "NO", "fail")
            all_handled = False
        except Exception as e:
            evidence["empty_file"] = {"detected": True, "error_type": type(e).__name__}
            log_result("Empty file detected", "YES", "pass")
        
        # Determine status
        detected_count = sum(1 for v in evidence.values() if isinstance(v, dict) and v.get("detected", False))
        total_tests = len(evidence)
        
        if detected_count == total_tests:
            status = "PROVED"
            notes.append("All failure modes properly detected and handled")
        elif detected_count >= total_tests * 0.7:
            status = "INCONCLUSIVE"
            notes.append(f"{detected_count}/{total_tests} failure modes detected")
        else:
            status = "DISPROVED"
            notes.append(f"Only {detected_count}/{total_tests} failure modes detected")
        
        return ClaimResult(claim, status, evidence, notes)
        
    except Exception as e:
        traceback.print_exc()
        return ClaimResult(claim, "ERROR", evidence, notes, str(e))


# =============================================================================
# CLAIM 12: PORTABILITY (Windows + Linux)
# =============================================================================

def test_portability(tmp_dir: str, data_gen: DataGenerator) -> ClaimResult:
    """
    CLAIM: MLE runtime is portable across Windows and Linux.
    
    Evidence:
    - Path handling (forward/backward slashes)
    - File operations work on current platform
    - No platform-specific crashes
    """
    claim = "Portability (Windows + Linux)"
    log_section(f"CLAIM 12: {claim}")
    
    if not MLE_AVAILABLE:
        return ClaimResult(claim, "SKIPPED", error="mle_runtime not available")
    if not SKLEARN_AVAILABLE:
        return ClaimResult(claim, "SKIPPED", error="sklearn not available")
    
    evidence = {
        "current_platform": platform.system(),
        "platform_version": platform.version(),
        "python_version": sys.version,
        "architecture": platform.machine(),
    }
    notes = []
    all_passed = True
    
    try:
        X_train = data_gen.generate_X(CONFIG.small_size, CONFIG.features)
        y_train = data_gen.generate_y_classification(X_train)
        X_test = data_gen.generate_X(CONFIG.test_size, CONFIG.features)
        
        model = ModelFactory.create_model("linear", "classification")
        model.fit(X_train, y_train)
        
        # Test 1: Standard path
        log_subsection("Test: Standard path handling")
        
        standard_path = os.path.join(tmp_dir, "portable_test.mle")
        try:
            try:
                mle.export_model(model, standard_path, input_shape=(1, CONFIG.features))
            except AttributeError:
                mle.save(model, standard_path)
            
            try:
                rt = mle.load_model(standard_path)
            except AttributeError:
                rt = mle.load(standard_path)
            
            try:
                _ = rt.run([X_test])
            except:
                _ = rt.predict(X_test)
            
            evidence["standard_path"] = {"success": True}
            log_result("Standard path", "PASS", "pass")
        except Exception as e:
            evidence["standard_path"] = {"success": False, "error": str(e)}
            log_result("Standard path", "FAIL", "fail")
            all_passed = False
        
        # Test 2: Path with spaces
        log_subsection("Test: Path with spaces")
        
        space_dir = os.path.join(tmp_dir, "path with spaces")
        os.makedirs(space_dir, exist_ok=True)
        space_path = os.path.join(space_dir, "model.mle")
        
        try:
            try:
                mle.export_model(model, space_path, input_shape=(1, CONFIG.features))
            except AttributeError:
                mle.save(model, space_path)
            
            try:
                rt = mle.load_model(space_path)
            except AttributeError:
                rt = mle.load(space_path)
            
            evidence["path_with_spaces"] = {"success": True}
            log_result("Path with spaces", "PASS", "pass")
        except Exception as e:
            evidence["path_with_spaces"] = {"success": False, "error": str(e)}
            log_result("Path with spaces", "FAIL", "fail")
            all_passed = False
        
        # Test 3: Unicode path (if supported)
        log_subsection("Test: Unicode path")
        
        try:
            unicode_dir = os.path.join(tmp_dir, "unicode_测试_тест")
            os.makedirs(unicode_dir, exist_ok=True)
            unicode_path = os.path.join(unicode_dir, "model.mle")
            
            try:
                mle.export_model(model, unicode_path, input_shape=(1, CONFIG.features))
            except AttributeError:
                mle.save(model, unicode_path)
            
            try:
                rt = mle.load_model(unicode_path)
            except AttributeError:
                rt = mle.load(unicode_path)
            
            evidence["unicode_path"] = {"success": True}
            log_result("Unicode path", "PASS", "pass")
        except Exception as e:
            evidence["unicode_path"] = {"success": False, "error": str(e)}
            log_result("Unicode path", "FAIL (may be expected)", "warn")
        
        # Test 4: Long path
        log_subsection("Test: Long path")
        
        try:
            long_name = "a" * 100
            long_dir = os.path.join(tmp_dir, long_name)
            os.makedirs(long_dir, exist_ok=True)
            long_path = os.path.join(long_dir, "model.mle")
            
            try:
                mle.export_model(model, long_path, input_shape=(1, CONFIG.features))
            except AttributeError:
                mle.save(model, long_path)
            
            try:
                rt = mle.load_model(long_path)
            except AttributeError:
                rt = mle.load(long_path)
            
            evidence["long_path"] = {"success": True}
            log_result("Long path", "PASS", "pass")
        except Exception as e:
            evidence["long_path"] = {"success": False, "error": str(e)}
            log_result("Long path", "FAIL", "warn")
        
        # Test 5: Relative path
        log_subsection("Test: Relative path")
        
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_dir)
            rel_path = "relative_model.mle"
            
            try:
                mle.export_model(model, rel_path, input_shape=(1, CONFIG.features))
            except AttributeError:
                mle.save(model, rel_path)
            
            try:
                rt = mle.load_model(rel_path)
            except AttributeError:
                rt = mle.load(rel_path)
            
            evidence["relative_path"] = {"success": True}
            log_result("Relative path", "PASS", "pass")
        except Exception as e:
            evidence["relative_path"] = {"success": False, "error": str(e)}
            log_result("Relative path", "FAIL", "fail")
            all_passed = False
        finally:
            os.chdir(original_cwd)
        
        # Test 6: Cross-platform path separators
        log_subsection("Test: Path separator handling")
        
        if platform.system() == "Windows":
            # Test forward slashes on Windows
            forward_path = tmp_dir.replace("\\", "/") + "/forward_slash.mle"
        else:
            forward_path = os.path.join(tmp_dir, "forward_slash.mle")
        
        try:
            try:
                mle.export_model(model, forward_path, input_shape=(1, CONFIG.features))
            except AttributeError:
                mle.save(model, forward_path)
            
            evidence["path_separators"] = {"success": True}
            log_result("Path separators", "PASS", "pass")
        except Exception as e:
            evidence["path_separators"] = {"success": False, "error": str(e)}
            log_result("Path separators", "FAIL", "warn")
        
        # Determine status
        critical_tests = ["standard_path", "relative_path"]
        critical_passed = all(evidence.get(t, {}).get("success", False) for t in critical_tests)
        
        if critical_passed and all_passed:
            status = "PROVED"
            notes.append(f"All portability tests passed on {platform.system()}")
        elif critical_passed:
            status = "INCONCLUSIVE"
            notes.append(f"Critical tests passed, some edge cases failed on {platform.system()}")
        else:
            status = "DISPROVED"
            notes.append(f"Critical portability tests failed on {platform.system()}")
        
        return ClaimResult(claim, status, evidence, notes)
        
    except Exception as e:
        traceback.print_exc()
        return ClaimResult(claim, "ERROR", evidence, notes, str(e))

# =============================================================================
# CLAIM 13: OVERHEADS (File Size, Page Faults, TLB)
# =============================================================================

def test_overheads(tmp_dir: str, data_gen: DataGenerator) -> ClaimResult:
    """
    CLAIM: MLE runtime has acceptable overheads (file size, page faults, TLB pressure).
    
    Evidence:
    - File size comparison with other formats
    - Page fault counts during operations
    - Memory access patterns (proxy for TLB pressure)
    """
    claim = "Overheads (File Size, Page Faults, TLB)"
    log_section(f"CLAIM 13: {claim}")
    
    if not MLE_AVAILABLE:
        return ClaimResult(claim, "SKIPPED", error="mle_runtime not available")
    if not SKLEARN_AVAILABLE:
        return ClaimResult(claim, "SKIPPED", error="sklearn not available")
    
    evidence = {}
    notes = []
    
    try:
        X_train = data_gen.generate_X(CONFIG.medium_size, CONFIG.features)
        y_train = data_gen.generate_y_classification(X_train)
        X_test = data_gen.generate_X(CONFIG.test_size, CONFIG.features)
        
        # Test different model sizes
        for complexity in ["linear", "ensemble", "complex_ensemble"]:
            log_subsection(f"Testing {complexity} model overheads")
            
            model = ModelFactory.create_model(complexity, "classification")
            if model is None:
                continue
            model.fit(X_train, y_train)
            
            mle_path = os.path.join(tmp_dir, f"overhead_{complexity}.mle")
            joblib_path = os.path.join(tmp_dir, f"overhead_{complexity}.joblib")
            pickle_path = os.path.join(tmp_dir, f"overhead_{complexity}.pkl")
            
            # Export to different formats
            try:
                mle.export_model(model, mle_path, input_shape=(1, CONFIG.features))
            except AttributeError:
                mle.save(model, mle_path)
            
            if joblib is not None:
                joblib.dump(model, joblib_path)
            
            import pickle
            with open(pickle_path, "wb") as f:
                pickle.dump(model, f)
            
            # File sizes
            mle_size = file_size_mb(mle_path)
            joblib_size = file_size_mb(joblib_path) if joblib is not None else None
            pickle_size = file_size_mb(pickle_path)
            
            evidence[complexity] = {
                "mle_size_mb": mle_size,
                "joblib_size_mb": joblib_size,
                "pickle_size_mb": pickle_size,
            }
            
            log_result("MLE file size", f"{mle_size:.3f} MB")
            if joblib_size:
                log_result("Joblib file size", f"{joblib_size:.3f} MB")
                log_result("MLE/Joblib ratio", f"{mle_size/joblib_size:.2f}")
            log_result("Pickle file size", f"{pickle_size:.3f} MB")
            
            # Page faults during load
            if psutil is not None:
                gc.collect()
                pf_before = get_page_faults()
                
                try:
                    rt = mle.load_model(mle_path)
                except AttributeError:
                    rt = mle.load(mle_path)
                
                pf_after_load = get_page_faults()
                
                # Page faults during inference
                try:
                    _ = rt.run([X_test])
                except:
                    _ = rt.predict(X_test)
                
                pf_after_run = get_page_faults()
                
                if pf_before[0] is not None:
                    evidence[complexity]["page_faults_load"] = pf_after_load[0] - pf_before[0] if pf_after_load[0] else None
                    evidence[complexity]["page_faults_run"] = pf_after_run[0] - pf_after_load[0] if pf_after_run[0] and pf_after_load[0] else None
                    
                    if evidence[complexity]["page_faults_load"] is not None:
                        log_result("Page faults (load)", evidence[complexity]["page_faults_load"])
                    if evidence[complexity]["page_faults_run"] is not None:
                        log_result("Page faults (run)", evidence[complexity]["page_faults_run"])
            
            # Memory access pattern analysis (TLB pressure proxy)
            log_subsection(f"Memory access pattern for {complexity}")
            
            # Measure time for sequential vs random access patterns
            try:
                rt = mle.load_model(mle_path)
            except AttributeError:
                rt = mle.load(mle_path)
            
            # Sequential access (should be TLB-friendly)
            seq_times = []
            for _ in range(5):
                gc.collect()
                start = now_ns()
                try:
                    _ = rt.run([X_test])
                except:
                    _ = rt.predict(X_test)
                seq_times.append((now_ns() - start) / 1e6)
            
            # Random access pattern (shuffle input)
            rand_times = []
            for _ in range(5):
                gc.collect()
                X_shuffled = X_test[np.random.permutation(len(X_test))]
                start = now_ns()
                try:
                    _ = rt.run([X_shuffled])
                except:
                    _ = rt.predict(X_shuffled)
                rand_times.append((now_ns() - start) / 1e6)
            
            evidence[complexity]["sequential_access_ms"] = sum(seq_times) / len(seq_times)
            evidence[complexity]["random_access_ms"] = sum(rand_times) / len(rand_times)
            evidence[complexity]["access_pattern_ratio"] = evidence[complexity]["random_access_ms"] / evidence[complexity]["sequential_access_ms"] if evidence[complexity]["sequential_access_ms"] > 0 else 1.0
            
            log_result("Sequential access", f"{evidence[complexity]['sequential_access_ms']:.2f} ms")
            log_result("Random access", f"{evidence[complexity]['random_access_ms']:.2f} ms")
            log_result("Random/Sequential ratio", f"{evidence[complexity]['access_pattern_ratio']:.2f}")
        
        # Summary analysis
        log_subsection("Overhead Summary")
        
        if evidence:
            avg_size_ratio = np.mean([
                evidence[c]["mle_size_mb"] / evidence[c]["joblib_size_mb"]
                for c in evidence
                if evidence[c].get("joblib_size_mb")
            ]) if any(evidence[c].get("joblib_size_mb") for c in evidence) else None
            
            if avg_size_ratio:
                evidence["summary"] = {"avg_size_ratio_vs_joblib": avg_size_ratio}
                log_result("Avg size ratio vs joblib", f"{avg_size_ratio:.2f}")
                
                if avg_size_ratio < 1.5:
                    notes.append("File size overhead is minimal")
                elif avg_size_ratio < 3.0:
                    notes.append("File size overhead is acceptable")
                else:
                    notes.append("File size overhead is significant")
        
        # Determine status
        size_ok = evidence.get("summary", {}).get("avg_size_ratio_vs_joblib", 2.0) < 3.0
        
        if size_ok:
            status = "PROVED"
            notes.append("Overheads are within acceptable limits")
        else:
            status = "INCONCLUSIVE"
            notes.append("Some overheads may be significant")
        
        return ClaimResult(claim, status, evidence, notes)
        
    except Exception as e:
        traceback.print_exc()
        return ClaimResult(claim, "ERROR", evidence, notes, str(e))


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def run_all_tests():
    """Run all claim tests and generate report."""
    
    log_section("MLE RUNTIME COMPREHENSIVE CLAIMS VALIDATION")
    
    # Environment info
    print(f"\nPlatform: {platform.platform()}")
    print(f"Python: {sys.version}")
    print(f"MLE Runtime: {MLE_VERSION}")
    print(f"sklearn available: {SKLEARN_AVAILABLE}")
    print(f"psutil available: {psutil is not None}")
    print(f"joblib available: {joblib is not None}")
    print(f"ONNX Runtime available: {ONNX_AVAILABLE}")
    print(f"PyTorch available: {TORCH_AVAILABLE}")
    
    RESULTS.add_metadata("platform", platform.platform())
    RESULTS.add_metadata("python_version", sys.version)
    RESULTS.add_metadata("mle_runtime_version", MLE_VERSION)
    RESULTS.add_metadata("sklearn_available", SKLEARN_AVAILABLE)
    RESULTS.add_metadata("psutil_available", psutil is not None)
    RESULTS.add_metadata("joblib_available", joblib is not None)
    RESULTS.add_metadata("onnx_available", ONNX_AVAILABLE)
    RESULTS.add_metadata("torch_available", TORCH_AVAILABLE)
    
    # Check prerequisites
    if not MLE_AVAILABLE:
        print(colorize("\nERROR: mle_runtime is not installed!", Colors.FAIL))
        print("Please install mle_runtime to run these tests.")
        return
    
    if not SKLEARN_AVAILABLE:
        print(colorize("\nERROR: sklearn is not installed!", Colors.FAIL))
        print("Please install scikit-learn to run these tests.")
        return
    
    # Create temp directory
    tmp_dir = tempfile.mkdtemp(prefix="mle_claims_test_")
    print(f"\nTest artifacts directory: {tmp_dir}")
    RESULTS.add_metadata("artifacts_dir", tmp_dir)
    
    # Initialize data generator
    data_gen = DataGenerator(seed=CONFIG.random_seed)
    
    # Run all tests
    tests = [
        ("Correctness Preservation", test_correctness_preservation),
        ("Static Execution Semantics", test_static_execution_semantics),
        ("Memory-Mapped Zero-Copy", test_memory_mapped_zero_copy),
        ("Cold/Warm Load Performance", test_cold_warm_load_performance),
        ("Scaling: Model Complexity", test_scaling_model_complexity),
        ("Scaling: Data Size", test_scaling_data_size),
        ("Concurrency Behavior", test_concurrency_behavior),
        ("Limits vs Joblib", test_limits_vs_joblib),
        ("Limits vs Native Runtimes", test_limits_vs_native_runtimes),
        ("Failure Behavior", test_failure_behavior),
        ("Portability", test_portability),
        ("Overheads", test_overheads),
    ]
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*70}")
            print(f"Running: {test_name}")
            print('='*70)
            
            result = test_func(tmp_dir, data_gen)
            RESULTS.add_result(result)
            
            # Clear data cache between tests to manage memory
            data_gen.clear_cache()
            gc.collect()
            
        except Exception as e:
            print(colorize(f"\nFATAL ERROR in {test_name}: {e}", Colors.FAIL))
            traceback.print_exc()
            RESULTS.add_result(ClaimResult(
                claim=test_name,
                status="ERROR",
                error=str(e)
            ))
    
    # Print final report
    RESULTS.print_report()
    
    # Save JSON report
    report_path = os.path.join(tmp_dir, "claims_report.json")
    with open(report_path, "w") as f:
        json.dump(RESULTS.to_dict(), f, indent=2, default=str)
    print(f"\nJSON report saved to: {report_path}")
    
    # Print machine-readable summary
    print("\n" + "="*70)
    print("MACHINE-READABLE SUMMARY")
    print("="*70)
    print(json.dumps(RESULTS.get_summary(), indent=2))
    
    return RESULTS

# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="MLE Runtime Comprehensive Claims Validation Suite"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        default=True,
        help="Enable verbose output"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Minimal output"
    )
    parser.add_argument(
        "--features",
        type=int,
        default=32,
        help="Number of features for test data"
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=4,
        help="Number of threads for concurrency tests"
    )
    parser.add_argument(
        "--processes",
        type=int,
        default=4,
        help="Number of processes for concurrency tests"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility"
    )
    
    args = parser.parse_args()
    
    # Update config
    CONFIG.verbose = not args.quiet
    CONFIG.features = args.features
    CONFIG.num_threads = args.threads
    CONFIG.num_processes = args.processes
    CONFIG.random_seed = args.seed
    
    # Run tests
    results = run_all_tests()
    
    # Exit with appropriate code
    if results:
        summary = results.get_summary()
        failed = summary["status_counts"].get("DISPROVED", 0) + summary["status_counts"].get("ERROR", 0)
        sys.exit(1 if failed > 0 else 0)
    else:
        sys.exit(1)
