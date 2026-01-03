"""
Reporters for Hallucination Detection.

This module provides various output formats for detection results.
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from .types import DetectionResult, HallucinationInstance


class DetectionReport:
    """
    Comprehensive report for hallucination detection results.
    
    Aggregates multiple detection results and provides summary statistics.
    
    Examples:
        >>> report = DetectionReport()
        >>> report.add_result(result1)
        >>> report.add_result(result2)
        >>> print(report.summary())
    """
    
    def __init__(self, title: str = "Hallucination Detection Report"):
        """
        Initialize report.
        
        Args:
            title: Report title.
        """
        self.title = title
        self.results: List[DetectionResult] = []
        self.created_at = datetime.now()
        self.metadata: Dict[str, Any] = {}
    
    def add_result(self, result: DetectionResult) -> None:
        """Add a detection result to the report."""
        self.results.append(result)
    
    def add_results(self, results: List[DetectionResult]) -> None:
        """Add multiple detection results to the report."""
        self.results.extend(results)
    
    @property
    def total_checks(self) -> int:
        """Total number of checks performed."""
        return len(self.results)
    
    @property
    def hallucination_count(self) -> int:
        """Total number of responses with hallucinations."""
        return sum(1 for r in self.results if r.is_hallucination)
    
    @property
    def total_hallucinations(self) -> int:
        """Total number of individual hallucinations found."""
        return sum(len(r.hallucinations) for r in self.results)
    
    @property
    def average_confidence(self) -> float:
        """Average confidence score across all hallucinations."""
        all_confidences = [
            h.confidence
            for r in self.results
            for h in r.hallucinations
        ]
        return sum(all_confidences) / len(all_confidences) if all_confidences else 0.0
    
    @property
    def hallucination_rate(self) -> float:
        """Percentage of responses containing hallucinations."""
        if not self.results:
            return 0.0
        return (self.hallucination_count / len(self.results)) * 100
    
    def summary(self) -> str:
        """Generate a human-readable summary."""
        lines = [
            f"═══════════════════════════════════════════════════════",
            f"  {self.title}",
            f"  Generated: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"═══════════════════════════════════════════════════════",
            f"",
            f"📊 Overall Statistics:",
            f"   • Total responses checked: {self.total_checks}",
            f"   • Responses with hallucinations: {self.hallucination_count}",
            f"   • Hallucination rate: {self.hallucination_rate:.1f}%",
            f"   • Total hallucinations found: {self.total_hallucinations}",
            f"   • Average confidence: {self.average_confidence:.1%}",
            f"",
        ]
        
        # Add severity breakdown
        severity_counts = self._get_severity_breakdown()
        lines.append("📈 Severity Breakdown:")
        for severity, count in severity_counts.items():
            if count > 0:
                lines.append(f"   • {severity}: {count}")
        lines.append("")
        
        # Add type breakdown
        type_counts = self._get_type_breakdown()
        lines.append("🏷️  Type Breakdown:")
        for htype, count in type_counts.items():
            if count > 0:
                lines.append(f"   • {htype}: {count}")
        
        lines.append("")
        lines.append("═══════════════════════════════════════════════════════")
        
        return "\n".join(lines)
    
    def _get_severity_breakdown(self) -> Dict[str, int]:
        """Get count of hallucinations by severity."""
        counts: Dict[str, int] = {}
        for result in self.results:
            for severity, count in result.severity_breakdown.items():
                counts[severity] = counts.get(severity, 0) + count
        return counts
    
    def _get_type_breakdown(self) -> Dict[str, int]:
        """Get count of hallucinations by type."""
        counts: Dict[str, int] = {}
        for result in self.results:
            for htype, count in result.type_breakdown.items():
                counts[htype] = counts.get(htype, 0) + count
        return counts
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "title": self.title,
            "created_at": self.created_at.isoformat(),
            "total_checks": self.total_checks,
            "hallucination_count": self.hallucination_count,
            "total_hallucinations": self.total_hallucinations,
            "hallucination_rate": self.hallucination_rate,
            "average_confidence": self.average_confidence,
            "severity_breakdown": self._get_severity_breakdown(),
            "type_breakdown": self._get_type_breakdown(),
            "results": [r.to_dict() for r in self.results],
            "metadata": self.metadata,
        }


class JSONReporter:
    """
    JSON output reporter.
    
    Exports detection results and reports to JSON format.
    
    Examples:
        >>> reporter = JSONReporter()
        >>> json_str = reporter.format(result)
        >>> reporter.save(result, "output.json")
    """
    
    def __init__(self, pretty: bool = True):
        """
        Initialize JSON reporter.
        
        Args:
            pretty: Whether to use pretty formatting.
        """
        self.pretty = pretty
    
    def format(self, data: Any) -> str:
        """
        Format data as JSON string.
        
        Args:
            data: DetectionResult, DetectionReport, or dict to format.
        
        Returns:
            JSON string.
        """
        if isinstance(data, (DetectionResult, DetectionReport)):
            data = data.to_dict()
        
        if self.pretty:
            return json.dumps(data, indent=2, default=str)
        else:
            return json.dumps(data, default=str)
    
    def save(self, data: Any, filepath: str) -> None:
        """
        Save data to JSON file.
        
        Args:
            data: Data to save.
            filepath: Output file path.
        """
        json_str = self.format(data)
        Path(filepath).write_text(json_str)
    
    def format_result(self, result: DetectionResult) -> str:
        """Format a single detection result."""
        return self.format(result.to_dict())
    
    def format_report(self, report: DetectionReport) -> str:
        """Format a full detection report."""
        return self.format(report.to_dict())


class HTMLReporter:
    """
    HTML output reporter.
    
    Generates interactive HTML reports for detection results.
    
    Examples:
        >>> reporter = HTMLReporter()
        >>> html = reporter.generate(report)
        >>> reporter.save(report, "report.html")
    """
    
    def __init__(self, theme: str = "light"):
        """
        Initialize HTML reporter.
        
        Args:
            theme: Color theme ("light" or "dark").
        """
        self.theme = theme
    
    def generate(self, report: DetectionReport) -> str:
        """
        Generate HTML report.
        
        Args:
            report: DetectionReport to convert.
        
        Returns:
            HTML string.
        """
        severity_breakdown = report._get_severity_breakdown()
        type_breakdown = report._get_type_breakdown()
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report.title}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: {"#1a1a2e" if self.theme == "dark" else "#f5f7fa"};
            color: {"#eee" if self.theme == "dark" else "#333"};
            padding: 2rem;
            line-height: 1.6;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            text-align: center;
            margin-bottom: 2rem;
            padding: 2rem;
            background: {"#16213e" if self.theme == "dark" else "white"};
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        h1 {{ font-size: 2rem; margin-bottom: 0.5rem; }}
        .timestamp {{ color: #888; font-size: 0.9rem; }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .stat-card {{
            background: {"#16213e" if self.theme == "dark" else "white"};
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .stat-value {{ font-size: 2rem; font-weight: bold; color: #667eea; }}
        .stat-label {{ color: #888; font-size: 0.85rem; margin-top: 0.5rem; }}
        .section {{
            background: {"#16213e" if self.theme == "dark" else "white"};
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 1rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .section h2 {{ margin-bottom: 1rem; font-size: 1.25rem; }}
        .hallucination {{
            background: {"#1a1a2e" if self.theme == "dark" else "#fef3f3"};
            border-left: 4px solid #e74c3c;
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 0 8px 8px 0;
        }}
        .severity-low {{ border-color: #f1c40f; }}
        .severity-medium {{ border-color: #e67e22; }}
        .severity-high {{ border-color: #e74c3c; }}
        .severity-critical {{ border-color: #9b59b6; }}
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: bold;
            margin-right: 0.5rem;
        }}
        .badge-type {{ background: #667eea; color: white; }}
        .badge-severity {{ background: #e74c3c; color: white; }}
        .verified {{ color: #27ae60; }}
        .progress-bar {{
            height: 8px;
            background: #ddd;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 0.5rem;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.3s ease;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 {report.title}</h1>
            <p class="timestamp">Generated: {report.created_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{report.total_checks}</div>
                <div class="stat-label">Responses Checked</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{report.hallucination_count}</div>
                <div class="stat-label">With Hallucinations</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{report.hallucination_rate:.1f}%</div>
                <div class="stat-label">Hallucination Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{report.average_confidence:.0%}</div>
                <div class="stat-label">Avg Confidence</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Severity Distribution</h2>
            {self._generate_breakdown_html(severity_breakdown)}
        </div>
        
        <div class="section">
            <h2>🏷️ Type Distribution</h2>
            {self._generate_breakdown_html(type_breakdown)}
        </div>
        
        <div class="section">
            <h2>📋 Detailed Results</h2>
            {self._generate_results_html(report.results)}
        </div>
    </div>
</body>
</html>'''
        
        return html
    
    def _generate_breakdown_html(self, breakdown: Dict[str, int]) -> str:
        """Generate HTML for breakdown section."""
        total = sum(breakdown.values()) or 1
        lines = []
        
        for name, count in sorted(breakdown.items(), key=lambda x: -x[1]):
            if count > 0:
                pct = (count / total) * 100
                lines.append(f'''
                    <div style="margin: 0.5rem 0;">
                        <div style="display: flex; justify-content: space-between;">
                            <span>{name}</span>
                            <span>{count} ({pct:.1f}%)</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {pct}%"></div>
                        </div>
                    </div>
                ''')
        
        return "".join(lines) if lines else "<p>No data available</p>"
    
    def _generate_results_html(self, results: List[DetectionResult]) -> str:
        """Generate HTML for individual results."""
        lines = []
        
        for i, result in enumerate(results, 1):
            status = "⚠️" if result.is_hallucination else "✅"
            
            lines.append(f'''
                <div style="margin: 1rem 0; padding: 1rem; background: {"#1a1a2e" if self.theme == "dark" else "#f8f9fa"}; border-radius: 8px;">
                    <h3>{status} Response #{i}</h3>
                    <p>Claims: {result.verified_claims}/{result.total_claims} verified | 
                       Confidence: {result.confidence:.0%} | 
                       Time: {result.processing_time_ms:.0f}ms</p>
            ''')
            
            for h in result.hallucinations:
                severity_class = f"severity-{h.severity.name.lower()}"
                lines.append(f'''
                    <div class="hallucination {severity_class}">
                        <span class="badge badge-type">{h.hallucination_type.name}</span>
                        <span class="badge badge-severity">{h.severity.name}</span>
                        <p><strong>Text:</strong> {h.text[:200]}...</p>
                        <p><strong>Explanation:</strong> {h.explanation}</p>
                        {"<p><strong>Suggestion:</strong> " + h.suggested_correction + "</p>" if h.suggested_correction else ""}
                    </div>
                ''')
            
            lines.append("</div>")
        
        return "".join(lines) if lines else "<p>No results to display</p>"
    
    def save(self, report: DetectionReport, filepath: str) -> None:
        """
        Save report to HTML file.
        
        Args:
            report: Report to save.
            filepath: Output file path.
        """
        html = self.generate(report)
        Path(filepath).write_text(html)


class MarkdownReporter:
    """
    Markdown output reporter.
    
    Generates Markdown reports suitable for documentation.
    """
    
    def generate(self, report: DetectionReport) -> str:
        """Generate Markdown report."""
        lines = [
            f"# {report.title}",
            f"",
            f"*Generated: {report.created_at.strftime('%Y-%m-%d %H:%M:%S')}*",
            f"",
            f"## Summary",
            f"",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Total Responses | {report.total_checks} |",
            f"| With Hallucinations | {report.hallucination_count} |",
            f"| Hallucination Rate | {report.hallucination_rate:.1f}% |",
            f"| Total Hallucinations | {report.total_hallucinations} |",
            f"| Average Confidence | {report.average_confidence:.0%} |",
            f"",
            f"## Severity Breakdown",
            f"",
        ]
        
        for severity, count in report._get_severity_breakdown().items():
            if count > 0:
                lines.append(f"- **{severity}**: {count}")
        
        lines.extend([
            f"",
            f"## Type Breakdown",
            f"",
        ])
        
        for htype, count in report._get_type_breakdown().items():
            if count > 0:
                lines.append(f"- **{htype}**: {count}")
        
        lines.extend([
            f"",
            f"## Detailed Results",
            f"",
        ])
        
        for i, result in enumerate(report.results, 1):
            status = "⚠️" if result.is_hallucination else "✅"
            lines.append(f"### {status} Response #{i}")
            lines.append(f"")
            lines.append(f"- Confidence: {result.confidence:.0%}")
            lines.append(f"- Claims: {result.verified_claims}/{result.total_claims} verified")
            lines.append(f"")
            
            for h in result.hallucinations:
                lines.append(f"#### {h.hallucination_type.name} ({h.severity.name})")
                lines.append(f"")
                lines.append(f"> {h.text[:200]}...")
                lines.append(f"")
                lines.append(f"**Explanation:** {h.explanation}")
                if h.suggested_correction:
                    lines.append(f"")
                    lines.append(f"**Suggestion:** {h.suggested_correction}")
                lines.append(f"")
        
        return "\n".join(lines)
    
    def save(self, report: DetectionReport, filepath: str) -> None:
        """Save report to Markdown file."""
        md = self.generate(report)
        Path(filepath).write_text(md)
