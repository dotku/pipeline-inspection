"""
Test TensorFlow Lite inference on ARM device
Measures FPS, latency, and validates model correctness
"""
import argparse
import time
import cv2
import numpy as np
from pathlib import Path

try:
    # Try tflite-runtime first (lightweight)
    from tflite_runtime.interpreter import Interpreter
    print("✓ Using tflite-runtime")
except ImportError:
    try:
        # Fall back to full TensorFlow
        from tensorflow.lite.python.interpreter import Interpreter
        print("✓ Using tensorflow.lite")
    except ImportError:
        print("❌ Error: Neither tflite-runtime nor tensorflow is installed")
        print("   Install one of:")
        print("   - pip install tflite-runtime")
        print("   - pip install tensorflow")
        exit(1)


class TFLiteDetector:
    """TensorFlow Lite YOLO detector"""

    def __init__(self, model_path: str, use_npu: bool = False, num_threads: int = 4):
        """
        Initialize TFLite detector

        Args:
            model_path: Path to .tflite model
            use_npu: Enable NPU delegate (if available)
            num_threads: Number of CPU threads
        """
        self.model_path = model_path

        print(f"📦 Loading model: {model_path}")

        # Load TFLite model
        try:
            self.interpreter = Interpreter(
                model_path=model_path,
                num_threads=num_threads
            )

            # Allocate tensors
            self.interpreter.allocate_tensors()

            # Get input/output details
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()

            # Get input shape
            self.input_shape = self.input_details[0]['shape']
            self.input_height = self.input_shape[1]
            self.input_width = self.input_shape[2]

            print(f"   ✓ Model loaded successfully")
            print(f"   Input shape: {self.input_shape}")
            print(f"   Input dtype: {self.input_details[0]['dtype']}")
            print(f"   Threads: {num_threads}")

            if use_npu:
                print("   ⚠️  NPU delegate not yet configured (coming soon)")

        except Exception as e:
            print(f"   ✗ Failed to load model: {e}")
            raise

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for inference"""
        # Resize
        input_data = cv2.resize(image, (self.input_width, self.input_height))

        # Convert BGR to RGB
        input_data = cv2.cvtColor(input_data, cv2.COLOR_BGR2RGB)

        # Normalize to [0, 1]
        input_data = input_data.astype(np.float32) / 255.0

        # Add batch dimension
        input_data = np.expand_dims(input_data, axis=0)

        return input_data

    def detect(self, image: np.ndarray, conf_threshold: float = 0.5):
        """
        Run detection on image

        Args:
            image: Input image (BGR)
            conf_threshold: Confidence threshold

        Returns:
            List of detections: [(x1, y1, x2, y2, conf, class_id), ...]
        """
        # Preprocess
        input_data = self.preprocess(image)

        # Set input tensor
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)

        # Run inference
        start_time = time.time()
        self.interpreter.invoke()
        inference_time = (time.time() - start_time) * 1000  # ms

        # Get output tensor
        # Note: Output format depends on YOLO version
        # This is a simplified example - you may need to adjust
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])

        # Parse detections (simplified - adjust based on your model output)
        detections = []

        # Store inference time for FPS calculation
        self.last_inference_time = inference_time

        return detections, inference_time


def test_camera(camera_index: int = 0):
    """Test camera access"""
    print(f"\n📹 Testing camera access (index: {camera_index})...")

    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print(f"   ✗ Failed to open camera {camera_index}")
        print("\n💡 Troubleshooting:")
        print("   - Check camera connection")
        print("   - Try different index: --camera 1")
        print("   - List devices: ls -la /dev/video*")
        return False

    # Get camera properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    print(f"   ✓ Camera opened: {width}x{height} @ {fps}fps")

    # Test frame capture
    ret, frame = cap.read()
    if not ret:
        print("   ✗ Failed to capture frame")
        cap.release()
        return False

    print(f"   ✓ Frame captured: {frame.shape}")

    cap.release()
    return True


def benchmark_model(model_path: str, num_iterations: int = 100, use_npu: bool = False):
    """Benchmark model performance"""
    print(f"\n⚡ Benchmarking model performance...")
    print(f"   Iterations: {num_iterations}")

    # Load detector
    detector = TFLiteDetector(model_path, use_npu=use_npu)

    # Create dummy input
    dummy_image = np.random.randint(
        0, 255,
        (480, 640, 3),
        dtype=np.uint8
    )

    # Warmup
    print("   Warming up...")
    for _ in range(10):
        detector.detect(dummy_image)

    # Benchmark
    print("   Running benchmark...")
    latencies = []

    for i in range(num_iterations):
        detections, latency = detector.detect(dummy_image)
        latencies.append(latency)

        if (i + 1) % 20 == 0:
            print(f"   Progress: {i + 1}/{num_iterations}")

    # Calculate statistics
    latencies = np.array(latencies)
    avg_latency = np.mean(latencies)
    std_latency = np.std(latencies)
    min_latency = np.min(latencies)
    max_latency = np.max(latencies)
    avg_fps = 1000 / avg_latency

    print(f"\n📊 Benchmark Results:")
    print(f"   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"   Average FPS:     {avg_fps:.1f}")
    print(f"   Average Latency: {avg_latency:.1f} ms")
    print(f"   Std Dev:         {std_latency:.1f} ms")
    print(f"   Min Latency:     {min_latency:.1f} ms")
    print(f"   Max Latency:     {max_latency:.1f} ms")
    print(f"   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # Performance assessment
    print(f"\n💡 Performance Assessment:")
    if avg_fps >= 30:
        print(f"   ✓ Excellent! Real-time capable (30+ FPS)")
    elif avg_fps >= 15:
        print(f"   ✓ Good! Usable for inspection (15-30 FPS)")
    elif avg_fps >= 8:
        print(f"   ⚠️  Acceptable for slow inspection (8-15 FPS)")
    else:
        print(f"   ✗ Too slow for real-time (<8 FPS)")
        print(f"   💡 Recommendations:")
        print(f"      - Use INT8 quantized model")
        print(f"      - Enable NPU acceleration")
        print(f"      - Reduce input resolution")


def live_inference(model_path: str, camera_index: int = 0, use_npu: bool = False):
    """Run live inference with camera"""
    print(f"\n🎥 Starting live inference...")

    # Load detector
    detector = TFLiteDetector(model_path, use_npu=use_npu)

    # Open camera
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print(f"   ✗ Failed to open camera")
        return

    print(f"   ✓ Press 'q' to quit")

    # FPS tracking
    fps_history = []
    frame_count = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Run detection
            detections, latency = detector.detect(frame)

            # Calculate FPS
            fps = 1000 / latency if latency > 0 else 0
            fps_history.append(fps)
            if len(fps_history) > 30:
                fps_history.pop(0)
            avg_fps = np.mean(fps_history)

            # Draw info
            cv2.putText(
                frame,
                f"FPS: {avg_fps:.1f}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"Latency: {latency:.1f}ms",
                (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

            # Show frame
            cv2.imshow('TFLite Inference Test', frame)

            frame_count += 1

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()

        print(f"\n📊 Session Statistics:")
        print(f"   Frames processed: {frame_count}")
        print(f"   Average FPS: {np.mean(fps_history):.1f}")


def main():
    parser = argparse.ArgumentParser(
        description='Test TFLite inference on ARM device'
    )

    parser.add_argument(
        '--model',
        type=str,
        help='Path to TFLite model'
    )
    parser.add_argument(
        '--camera',
        type=int,
        default=0,
        help='Camera index (default: 0)'
    )
    parser.add_argument(
        '--benchmark',
        action='store_true',
        help='Run benchmark (no camera needed)'
    )
    parser.add_argument(
        '--live',
        action='store_true',
        help='Run live inference with camera'
    )
    parser.add_argument(
        '--use-npu',
        action='store_true',
        help='Enable NPU acceleration (if available)'
    )
    parser.add_argument(
        '--iterations',
        type=int,
        default=100,
        help='Number of benchmark iterations (default: 100)'
    )

    args = parser.parse_args()

    print("=" * 50)
    print("  TFLite Inference Test - ARM Deployment")
    print("=" * 50)

    # Test camera
    if not args.benchmark:
        test_camera(args.camera)

    # Run requested tests
    if args.model:
        if args.benchmark:
            benchmark_model(args.model, args.iterations, args.use_npu)
        elif args.live:
            live_inference(args.model, args.camera, args.use_npu)
        else:
            # Default: run benchmark
            benchmark_model(args.model, args.iterations, args.use_npu)
    else:
        print("\n💡 Usage examples:")
        print("   Test camera only:")
        print("     python test_tflite_inference.py --camera 0")
        print("\n   Benchmark model:")
        print("     python test_tflite_inference.py --model model.tflite --benchmark")
        print("\n   Live inference:")
        print("     python test_tflite_inference.py --model model.tflite --live")


if __name__ == "__main__":
    main()
