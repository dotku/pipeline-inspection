"""
Performance Benchmark Script
Compare different deployment configurations:
- Intel CPU (FP32)
- ARM CPU (FP32)
- ARM CPU (INT8)
- ARM NPU (INT8)
"""
import argparse
import time
import platform
import psutil
import numpy as np
from pathlib import Path


def get_system_info():
    """Get system information"""
    info = {
        'platform': platform.system(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'cpu_count': psutil.cpu_count(logical=False),
        'cpu_threads': psutil.cpu_count(logical=True),
        'ram_gb': round(psutil.virtual_memory().total / (1024**3), 2)
    }
    return info


def benchmark_cpu_baseline(duration: int = 60):
    """Benchmark CPU baseline (matrix multiplication)"""
    print("🔧 Running CPU baseline benchmark...")

    iterations = 0
    start_time = time.time()
    end_time = start_time + duration

    # Matrix size
    size = 1000

    while time.time() < end_time:
        a = np.random.rand(size, size)
        b = np.random.rand(size, size)
        c = np.dot(a, b)
        iterations += 1

    elapsed = time.time() - start_time
    ops_per_sec = iterations / elapsed

    return {
        'iterations': iterations,
        'duration': elapsed,
        'ops_per_sec': ops_per_sec
    }


def benchmark_model(
    model_path: str,
    backend: str,
    duration: int = 60,
    warmup: int = 10
):
    """
    Benchmark model inference

    Args:
        model_path: Path to model file
        backend: Backend type ('pytorch', 'tflite', 'tflite_npu')
        duration: Test duration in seconds
        warmup: Number of warmup iterations

    Returns:
        dict: Benchmark results
    """
    print(f"\n⚡ Benchmarking: {backend}")
    print(f"   Model: {model_path}")
    print(f"   Duration: {duration}s")

    # Load model based on backend
    if backend == 'pytorch':
        # Intel/PC deployment
        try:
            from ultralytics import YOLO
            model = YOLO(model_path)
            print("   ✓ PyTorch YOLO loaded")
        except ImportError:
            print("   ✗ ultralytics not installed")
            return None

    elif backend in ['tflite', 'tflite_npu']:
        # ARM deployment
        try:
            from tflite_runtime.interpreter import Interpreter
        except ImportError:
            from tensorflow.lite.python.interpreter import Interpreter

        interpreter = Interpreter(model_path=model_path)
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        print("   ✓ TFLite model loaded")

    else:
        print(f"   ✗ Unknown backend: {backend}")
        return None

    # Create dummy input
    dummy_input = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)

    # Warmup
    print(f"   Warming up ({warmup} iterations)...")
    for _ in range(warmup):
        if backend == 'pytorch':
            model(dummy_input, verbose=False)
        elif backend in ['tflite', 'tflite_npu']:
            input_data = np.expand_dims(dummy_input, axis=0).astype(np.float32) / 255.0
            interpreter.set_tensor(input_details[0]['index'], input_data)
            interpreter.invoke()

    # Benchmark
    print(f"   Running benchmark...")
    latencies = []
    cpu_usage = []

    start_time = time.time()
    iterations = 0

    while time.time() - start_time < duration:
        # Measure CPU usage before
        cpu_before = psutil.cpu_percent(interval=None)

        # Run inference
        inf_start = time.time()

        if backend == 'pytorch':
            model(dummy_input, verbose=False)
        elif backend in ['tflite', 'tflite_npu']:
            input_data = np.expand_dims(dummy_input, axis=0).astype(np.float32) / 255.0
            interpreter.set_tensor(input_details[0]['index'], input_data)
            interpreter.invoke()

        inf_time = (time.time() - inf_start) * 1000  # ms
        latencies.append(inf_time)

        # Measure CPU usage after
        cpu_after = psutil.cpu_percent(interval=None)
        cpu_usage.append((cpu_before + cpu_after) / 2)

        iterations += 1

    elapsed = time.time() - start_time

    # Calculate statistics
    latencies = np.array(latencies)

    results = {
        'backend': backend,
        'iterations': iterations,
        'duration': elapsed,
        'fps': iterations / elapsed,
        'latency_avg': np.mean(latencies),
        'latency_std': np.std(latencies),
        'latency_min': np.min(latencies),
        'latency_max': np.max(latencies),
        'latency_p50': np.percentile(latencies, 50),
        'latency_p95': np.percentile(latencies, 95),
        'latency_p99': np.percentile(latencies, 99),
        'cpu_usage_avg': np.mean(cpu_usage) if cpu_usage else 0,
    }

    return results


def print_results(results_list):
    """Print benchmark results in table format"""
    print("\n" + "=" * 80)
    print("  BENCHMARK RESULTS")
    print("=" * 80)

    # Header
    print(f"\n{'Backend':<20} {'FPS':<10} {'Latency (ms)':<15} {'CPU %':<10}")
    print(f"{'':<20} {'':<10} {'Avg / P95 / P99':<15} {'':<10}")
    print("-" * 80)

    # Results
    for r in results_list:
        if r is None:
            continue

        backend = r['backend']
        fps = f"{r['fps']:.1f}"
        latency = f"{r['latency_avg']:.1f}/{r['latency_p95']:.1f}/{r['latency_p99']:.1f}"
        cpu = f"{r['cpu_usage_avg']:.1f}%"

        print(f"{backend:<20} {fps:<10} {latency:<15} {cpu:<10}")

    print("-" * 80)

    # Performance comparison
    if len(results_list) >= 2:
        baseline = results_list[0]
        print(f"\n📊 Performance Comparison (vs {baseline['backend']}):")

        for r in results_list[1:]:
            if r is None:
                continue

            speedup = r['fps'] / baseline['fps']
            latency_improvement = (baseline['latency_avg'] - r['latency_avg']) / baseline['latency_avg'] * 100

            print(f"   {r['backend']:<20}: {speedup:.2f}x faster, {latency_improvement:+.1f}% latency")


def main():
    parser = argparse.ArgumentParser(
        description='Benchmark Pipeline Inspection System Performance'
    )

    parser.add_argument(
        '--model-pytorch',
        type=str,
        help='Path to PyTorch YOLO model (.pt)'
    )
    parser.add_argument(
        '--model-tflite',
        type=str,
        help='Path to TFLite model (.tflite)'
    )
    parser.add_argument(
        '--use-npu',
        action='store_true',
        help='Test NPU acceleration (ARM only)'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=60,
        help='Test duration in seconds (default: 60)'
    )
    parser.add_argument(
        '--warmup',
        type=int,
        default=10,
        help='Warmup iterations (default: 10)'
    )

    args = parser.parse_args()

    print("=" * 80)
    print("  PIPELINE INSPECTION SYSTEM - PERFORMANCE BENCHMARK")
    print("=" * 80)

    # System info
    info = get_system_info()
    print(f"\n🖥️  System Information:")
    print(f"   Platform: {info['platform']} {info['machine']}")
    print(f"   CPU: {info['cpu_count']} cores / {info['cpu_threads']} threads")
    print(f"   RAM: {info['ram_gb']} GB")

    # Run benchmarks
    results = []

    if args.model_pytorch:
        result = benchmark_model(
            args.model_pytorch,
            'pytorch',
            args.duration,
            args.warmup
        )
        if result:
            results.append(result)

    if args.model_tflite:
        result = benchmark_model(
            args.model_tflite,
            'tflite',
            args.duration,
            args.warmup
        )
        if result:
            results.append(result)

        if args.use_npu:
            result = benchmark_model(
                args.model_tflite,
                'tflite_npu',
                args.duration,
                args.warmup
            )
            if result:
                results.append(result)

    # Print results
    if results:
        print_results(results)
    else:
        print("\n⚠️  No benchmarks run. Provide model paths:")
        print("   --model-pytorch path/to/model.pt")
        print("   --model-tflite path/to/model.tflite")
        print("\nExample:")
        print("   python benchmark.py \\")
        print("     --model-pytorch ../models/yolov8n.pt \\")
        print("     --model-tflite ../models/yolov8n_fp32.tflite \\")
        print("     --duration 60")


if __name__ == "__main__":
    main()
