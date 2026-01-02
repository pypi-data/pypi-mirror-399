"""
Rich Terminal Output for NetworkDoctor
"""
from typing import Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from networkdoctor.utils.helpers import get_severity_color, get_severity_icon


class TerminalDisplay:
    """Terminal output display using Rich"""
    
    def __init__(self):
        """Initialize terminal display"""
        self.console = Console()
    
    def show_results(self, results: Dict[str, Any], verbose: bool = False):
        """
        Display diagnosis results.
        
        Args:
            results: Diagnosis results
            verbose: Enable verbose output
        """
        # Header
        self.console.print("\n")
        self.console.print(Panel.fit(
            "🩺 N E T W O R K D O C T O R 🩺",
            style="bold cyan"
        ))
        self.console.print("\n")
        
        # Summary
        analysis = results.get("analysis", {})
        summary = analysis.get("summary", {})
        
        # Health score
        health_score = summary.get("health_score", 0)
        score_color = "green" if health_score >= 80 else "yellow" if health_score >= 50 else "red"
        
        self.console.print(f"📋 Health Score: [{score_color}]{health_score}/100[/{score_color}]")
        self.console.print(f"   Critical Issues: {summary.get('critical_count', 0)}")
        self.console.print(f"   Total Issues: {summary.get('total_issues', 0)}")
        self.console.print(f"   Estimated Fix Time: {summary.get('estimated_fix_time', 'N/A')}")
        self.console.print("\n")
        
        # Issues table
        issues = analysis.get("issues", [])
        if issues:
            table = Table(title="Detected Issues", box=box.ROUNDED)
            table.add_column("Severity", style="cyan")
            table.add_column("Type", style="magenta")
            table.add_column("Title", style="white")
            table.add_column("Impact", style="yellow")
            
            for issue in issues[:10]:  # Show first 10
                severity = issue.get("severity", "info")
                icon = get_severity_icon(severity)
                table.add_row(
                    f"{icon} {severity.upper()}",
                    issue.get("type", "unknown"),
                    issue.get("title", ""),
                    issue.get("impact", "")[:50] + "..." if len(issue.get("impact", "")) > 50 else issue.get("impact", ""),
                )
            
            self.console.print(table)
            self.console.print("\n")
        
        # Recommendations
        recommendations = analysis.get("recommendations", [])
        if recommendations:
            self.console.print("[bold]🛠️ Action Plan:[/bold]\n")
            for rec in recommendations[:5]:  # Show first 5
                priority = rec.get("priority", "normal").upper()
                self.console.print(f"[bold]{priority}:[/bold] {rec.get('issue', '')}")
                solutions = rec.get("solutions", [])
                if solutions:
                    sol = solutions[0]
                    self.console.print(f"  Command: [cyan]{sol.get('command', '')}[/cyan]")
            self.console.print("\n")


