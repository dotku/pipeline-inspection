"""
Convert YOLO model to TensorFlow Lite for ARM deployment
Supports: YOLOv5, YOLOv8
Output: FP32 or INT8 quantized TFLite model
"""
import argparse
import sys
from pathlib import Path

try:
    from ultralytics import YOLO
except ImportError:
    print("Error: ultralytics not installed. Run: pip install ultralytics")
    sys.exit(1)


def convert_yolo_to_tflite(
    model_path: str,
    output_path: str,
    img_size: int = 640,
    quantize: str = "fp32",
    calibration_data: str = None
):
    """
    Convert YOLO model to TensorFlow Lite

    Args:
        model_path: Path to YOLO .pt model
        output_path: Output .tflite file path
        img_size: Input image size (default 640)
        quantize: Quantization type ('fp32', 'fp16', 'int8')
        calibration_data: Path to calibration images for INT8 (optional)
    """
    print(f"🔄 Converting YOLO model to TensorFlow Lite...")
    print(f"   Input: {model_path}")
    print(f"   Output: {output_path}")
    print(f"   Image size: {img_size}")
    print(f"   Quantization: {quantize}")

    # Load YOLO model
    print("\n📦 Loading YOLO model...")
    try:
        model = YOLO(model_path)
        print(f"   ✓ Model loaded: {model_path}")
    except Exception as e:
        print(f"   ✗ Failed to load model: {e}")
        return False

    # Export to TensorFlow Lite
    print(f"\n🚀 Exporting to TFLite ({quantize})...")

    try:
        export_args = {
            'format': 'tflite',
            'imgsz': img_size,
        }

        # Add quantization settings
        if quantize == 'int8':
            export_args['int8'] = True
            if calibration_data:
                export_args['data'] = calibration_data
                print(f"   ℹ️  Using calibration data: {calibration_data}")
            else:
                print("   ⚠️  Warning: INT8 without calibration data (lower accuracy)")
        elif quantize == 'fp16':
            export_args['half'] = True

        # Perform export
        export_path = model.export(**export_args)

        print(f"   ✓ Export successful!")
        print(f"   ✓ Model saved to: {export_path}")

        # Move to desired output path if different
        if str(export_path) != output_path:
            import shutil
            shutil.move(str(export_path), output_path)
            print(f"   ✓ Moved to: {output_path}")

        # Print model info
        import os
        model_size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"\n📊 Model Information:")
        print(f"   Size: {model_size:.2f} MB")
        print(f"   Format: TensorFlow Lite")
        print(f"   Quantization: {quantize.upper()}")
        print(f"   Input size: {img_size}x{img_size}")

        print(f"\n✅ Conversion complete!")
        print(f"\n💡 Next steps:")
        print(f"   1. Test on ARM device:")
        print(f"      python deployment/arm/test_tflite_inference.py --model {output_path}")
        print(f"   2. Benchmark performance:")
        print(f"      python scripts/benchmark.py --model {output_path}")

        return True

    except Exception as e:
        print(f"   ✗ Export failed: {e}")
        print(f"\n💡 Troubleshooting:")
        print(f"   - Ensure ultralytics is up to date: pip install -U ultralytics")
        print(f"   - Try exporting to ONNX first: format='onnx'")
        print(f"   - Check model compatibility")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Convert YOLO model to TensorFlow Lite for ARM deployment'
    )
    parser.add_argument(
        '--model',
        type=str,
        required=True,
        help='Path to YOLO model (.pt file)'
    )
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Output TFLite model path (.tflite file)'
    )
    parser.add_argument(
        '--img-size',
        type=int,
        default=640,
        help='Input image size (default: 640)'
    )
    parser.add_argument(
        '--quantize',
        type=str,
        choices=['fp32', 'fp16', 'int8'],
        default='fp32',
        help='Quantization type (default: fp32)'
    )
    parser.add_argument(
        '--calibration-data',
        type=str,
        help='Path to calibration images for INT8 quantization (YAML config or folder)'
    )

    args = parser.parse_args()

    # Validate inputs
    if not Path(args.model).exists():
        print(f"❌ Error: Model file not found: {args.model}")
        sys.exit(1)

    if args.quantize == 'int8' and not args.calibration_data:
        print("⚠️  Warning: INT8 quantization without calibration data")
        print("   This may result in reduced accuracy.")
        print("   Recommend: Provide --calibration-data for best results")
        response = input("   Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)

    # Create output directory if needed
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)

    # Convert
    success = convert_yolo_to_tflite(
        model_path=args.model,
        output_path=args.output,
        img_size=args.img_size,
        quantize=args.quantize,
        calibration_data=args.calibration_data
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
