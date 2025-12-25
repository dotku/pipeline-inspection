"""
Report generation for pipeline inspection
Generates PDF and JSON reports
"""
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import logging

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from yolo_detector import Detection
from config import settings

logger = logging.getLogger(__name__)


class InspectionReportGenerator:
    """Generate inspection reports in PDF and JSON formats"""

    def __init__(self, reports_dir: str = None):
        """
        Initialize report generator

        Args:
            reports_dir: Directory to save reports
        """
        self.reports_dir = Path(reports_dir or settings.REPORTS_DIR)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(
        self,
        detections: List[Detection],
        inspection_metadata: Dict[str, Any] = None,
        format: str = "both"  # "pdf", "json", or "both"
    ) -> Dict[str, str]:
        """
        Generate inspection report

        Args:
            detections: List of detections
            inspection_metadata: Additional metadata (location, operator, etc.)
            format: Report format ("pdf", "json", or "both")

        Returns:
            Dictionary with paths to generated reports
        """
        timestamp = datetime.now()
        report_id = timestamp.strftime("%Y%m%d_%H%M%S")

        metadata = inspection_metadata or {}
        metadata.update({
            "report_id": report_id,
            "timestamp": timestamp.isoformat(),
            "total_detections": len(detections),
        })

        generated_files = {}

        # Generate PDF report
        if format in ["pdf", "both"] and settings.ENABLE_PDF_REPORT:
            pdf_path = self._generate_pdf(detections, metadata, report_id)
            generated_files["pdf"] = str(pdf_path)

        # Generate JSON report
        if format in ["json", "both"] and settings.ENABLE_JSON_REPORT:
            json_path = self._generate_json(detections, metadata, report_id)
            generated_files["json"] = str(json_path)

        return generated_files

    def _generate_pdf(
        self,
        detections: List[Detection],
        metadata: Dict[str, Any],
        report_id: str
    ) -> Path:
        """Generate PDF report"""
        filename = f"inspection_report_{report_id}.pdf"
        filepath = self.reports_dir / filename

        # Create PDF document
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=1 * inch,
            bottomMargin=0.75 * inch
        )

        # Container for PDF elements
        story = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
            spaceBefore=12
        )

        # Title
        title = Paragraph("Pipeline Inspection Report", title_style)
        story.append(title)
        story.append(Spacer(1, 0.2 * inch))

        # Metadata section
        story.append(Paragraph("Inspection Details", heading_style))

        metadata_data = [
            ["Report ID:", metadata.get("report_id", "N/A")],
            ["Date & Time:", metadata.get("timestamp", "N/A")],
            ["Location:", metadata.get("location", "N/A")],
            ["Inspector:", metadata.get("inspector", "System")],
            ["Total Detections:", str(metadata.get("total_detections", 0))],
        ]

        metadata_table = Table(metadata_data, colWidths=[2 * inch, 4 * inch])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))

        story.append(metadata_table)
        story.append(Spacer(1, 0.3 * inch))

        # Detections summary
        if detections:
            story.append(Paragraph("Detected Defects", heading_style))

            # Group by class
            by_class = {}
            for det in detections:
                by_class[det.class_name] = by_class.get(det.class_name, 0) + 1

            summary_data = [["Defect Type", "Count", "Severity"]]
            severity_map = {
                "leak": "Critical",
                "crack": "High",
                "corrosion": "High",
                "rust": "Medium",
                "foreign_object": "Medium",
                "sediment": "Low"
            }

            for class_name, count in sorted(by_class.items()):
                severity = severity_map.get(class_name.lower(), "Unknown")
                summary_data.append([class_name.replace("_", " ").title(), str(count), severity])

            summary_table = Table(summary_data, colWidths=[2.5 * inch, 1.5 * inch, 2 * inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ]))

            story.append(summary_table)
            story.append(Spacer(1, 0.3 * inch))

            # Detailed detections
            story.append(Paragraph("Detailed Findings", heading_style))

            detail_data = [["#", "Type", "Confidence", "Position", "Time"]]

            for idx, det in enumerate(detections[:50], 1):  # Limit to 50 for PDF
                position = f"{det.frame_position}m" if det.frame_position else "N/A"
                time_str = det.timestamp.strftime("%H:%M:%S")
                detail_data.append([
                    str(idx),
                    det.class_name.replace("_", " ").title(),
                    f"{det.confidence:.2%}",
                    position,
                    time_str
                ])

            detail_table = Table(
                detail_data,
                colWidths=[0.5 * inch, 2 * inch, 1.2 * inch, 1.2 * inch, 1.1 * inch]
            )
            detail_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ]))

            story.append(detail_table)

        else:
            story.append(Paragraph("No defects detected", styles['Normal']))

        # Footer
        story.append(Spacer(1, 0.5 * inch))
        footer_text = f"<para align=center><i>Generated by Pipeline Inspection System | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i></para>"
        story.append(Paragraph(footer_text, styles['Normal']))

        # Build PDF
        doc.build(story)
        logger.info(f"PDF report generated: {filepath}")

        return filepath

    def _generate_json(
        self,
        detections: List[Detection],
        metadata: Dict[str, Any],
        report_id: str
    ) -> Path:
        """Generate JSON report"""
        filename = f"inspection_report_{report_id}.json"
        filepath = self.reports_dir / filename

        # Prepare data
        report_data = {
            "metadata": metadata,
            "detections": [det.to_dict() for det in detections],
            "summary": self._calculate_summary(detections)
        }

        # Write JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        logger.info(f"JSON report generated: {filepath}")

        return filepath

    def _calculate_summary(self, detections: List[Detection]) -> Dict[str, Any]:
        """Calculate summary statistics"""
        if not detections:
            return {
                "total_detections": 0,
                "by_class": {},
                "average_confidence": 0.0,
                "highest_confidence": 0.0,
                "lowest_confidence": 0.0
            }

        by_class = {}
        confidences = []

        for det in detections:
            by_class[det.class_name] = by_class.get(det.class_name, 0) + 1
            confidences.append(det.confidence)

        return {
            "total_detections": len(detections),
            "by_class": by_class,
            "average_confidence": sum(confidences) / len(confidences),
            "highest_confidence": max(confidences),
            "lowest_confidence": min(confidences)
        }
