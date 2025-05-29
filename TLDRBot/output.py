"""
Simple output management for TLDR Agent
"""
from pathlib import Path
from datetime import datetime
from typing import List


class Output:
    """Simple file output handler."""
    
    def __init__(self, output_dir: str = "./summaries"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def save(self, content: str, filename: str) -> Path:
        """Save content to file."""
        file_path = self.output_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Saved: {file_path}")
            return file_path
        except IOError as e:
            print(f"❌ Save error: {e}")
            raise
    
    def filename(self, prefix: str = "tldr_summary", date: str = None) -> str:
        """Generate filename with date."""
        if not date:
            date = datetime.now().strftime('%Y%m%d')
        return f"{prefix}_{date}.md"
    
    def list_files(self, pattern: str = "tldr_*.md") -> List[Path]:
        """List existing summary files."""
        return sorted(self.output_dir.glob(pattern))
    
    def latest(self) -> Path:
        """Get the most recent summary file."""
        files = self.list_files()
        return files[-1] if files else None