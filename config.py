"""
Simple configuration management for TLDR Agent
"""
import json
from pathlib import Path
from typing import Dict, List, Optional


class Config:
    """Simple configuration handler following tiny agents pattern."""
    
    DEFAULT = {
        "model": "Qwen/Qwen2.5-72B-Instruct",
        "provider": "nebius", 
        "servers": [
            {
                "type": "stdio",
                "config": {
                    "command": "npx",
                    "args": ["@playwright/mcp@latest"]
                }
            }
        ],
        "output_dir": "./summaries"
    }
    
    def __init__(self, config_path: str = "agent.json"):
        self.config_path = Path(config_path)
        self.data = self._load()
        self.prompt = self._load_prompt()
    
    def _load(self) -> Dict:
        """Load config from agent.json or create default."""
        if not self.config_path.exists():
            self._save(self.DEFAULT)
            return self.DEFAULT.copy()
        
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️  Config error: {e}, using defaults")
            return self.DEFAULT.copy()
    
    def _load_prompt(self) -> Optional[str]:
        """Load system prompt from PROMPT.md if it exists."""
        prompt_path = self.config_path.parent / "PROMPT.md"
        
        if prompt_path.exists():
            try:
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            except IOError as e:
                print(f"⚠️  Could not load PROMPT.md: {e}")
        
        return None
    
    def _save(self, data: Dict) -> None:
        """Save config to file."""
        self.config_path.parent.mkdir(exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    @property
    def model(self) -> str:
        return self.data.get("model", self.DEFAULT["model"])
    
    @property
    def provider(self) -> str:
        return self.data.get("provider", self.DEFAULT["provider"])
    
    @property
    def servers(self) -> List[Dict]:
        return self.data.get("servers", self.DEFAULT["servers"])
    
    @property
    def output_dir(self) -> Path:
        return Path(self.data.get("output_dir", self.DEFAULT["output_dir"]))
    
    def update(self, **kwargs) -> None:
        """Update config values."""
        self.data.update(kwargs)
        self._save(self.data)