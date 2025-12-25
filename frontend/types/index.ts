export interface Detection {
  class_name: string;
  confidence: number;
  bbox: {
    x1: number;
    y1: number;
    x2: number;
    y2: number;
  };
  timestamp: string;
  frame_position?: number | null;
}

export interface SystemStatus {
  camera: {
    is_opened: boolean;
    index: number;
    resolution: string;
    fps: number;
  };
  detector: {
    is_loaded: boolean;
    model_path: string;
    confidence_threshold: number;
  };
  detections: {
    total: number;
    summary: DetectionSummary;
  };
}

export interface DetectionSummary {
  total_detections: number;
  by_class: Record<string, number>;
  average_confidence: number;
}

export interface InspectionMetadata {
  location: string;
  inspector: string;
  notes: string;
}
