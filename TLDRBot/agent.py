"""
TLDR Tiny Agent - Main agent class
"""
import asyncio
from datetime import datetime
from pathlib import Path
from huggingface_hub.inference._mcp import MCPClient

from config import Config
from output import Output


class TLDRAgent:
    """Simple TLDR newsletter summarizer agent."""
    
    def __init__(self, config_path: str = "agent.json"):
        self.config = Config(config_path)
        self.output = Output(self.config.output_dir)
        
        # Initialize MCP client
        self.mcp_client = MCPClient(
            model=self.config.model,
            provider=self.config.provider
        )
        self._initialized = False
    
    async def _ensure_initialized(self):
        """Initialize MCP tools if not already done."""
        if not self._initialized:
            print("🔧 Loading MCP tools...")
            
            # Add MCP servers from config
            for server_config in self.config.servers:
                await self.mcp_client.add_mcp_server(
                    server_config["type"],
                    **server_config["config"]
                )
            
            self._initialized = True
            print("✅ Agent ready!")
    
    async def _run_task(self, user_prompt: str) -> str:
        """Execute a task with the given user prompt."""
        await self._ensure_initialized()
        
        # Create messages with system prompt and user prompt
        messages = []
        
        # Add system prompt if available
        if self.config.prompt:
            messages.append({"role": "system", "content": self.config.prompt})
        
        # Add user prompt
        messages.append({"role": "user", "content": user_prompt})
        
        print("🤖 Generating summary...")
        content_parts = []
        
        async with self.mcp_client:
            async for message in self.mcp_client.process_single_turn_with_tools(messages):
                if hasattr(message, 'choices') and message.choices:
                    # Handle streaming chunks
                    delta = message.choices[0].delta
                    if delta.content:
                        content_parts.append(delta.content)
                        print(delta.content, end='', flush=True)
                elif hasattr(message, 'content'):
                    # Handle tool messages
                    if message.role == "assistant" and message.content:
                        content_parts.append(message.content)
                        print(message.content, end='', flush=True)
        
        print("\n✅ Summary complete!")
        return ''.join(content_parts)
    
    async def daily_summary(self) -> Path:
        """Generate daily TLDR summary."""
        date = datetime.now().strftime('%Y-%m-%d')
        
        user_prompt = f"""
Generate today's TLDR newsletter summary for {date}:

STEPS:
1. Navigate to https://tldr.tech/ 
2. Find and extract today's main newsletter content
3. Also check https://tldr.tech/ai for AI-specific news

OUTPUT:
- Create markdown with date header: "# TLDR Daily Summary - {date}"
- Top 5-7 most important stories
- Each story: title, 2-3 sentence summary, source link
- Save as 'tldr_summary_{date.replace("-", "")}.md'

START: Navigate to TLDR website now.
"""
        
        content = await self._run_task(user_prompt)
        filename = self.output.filename("tldr_summary")
        return self.output.save(content, filename)
    
    async def multi_source_summary(self) -> Path:
        """Generate comprehensive multi-source summary."""
        date = datetime.now().strftime('%Y-%m-%d')
        
        user_prompt = f"""
Generate comprehensive TLDR summary from multiple sources for {date}:

SOURCES:
1. https://tldr.tech/ (Main tech news)
2. https://tldr.tech/ai (AI/ML developments)  
3. https://tldr.tech/crypto (Crypto/Web3)
4. https://tldr.tech/design (Design/UX)

OUTPUT:
- Sections for each source category
- Top 3 stories overall
- Cross-cutting themes
- Save as 'tldr_comprehensive_{date.replace("-", "")}.md'

START: Begin with main TLDR site, then check each source.
"""
        
        content = await self._run_task(user_prompt)
        filename = self.output.filename("tldr_comprehensive")
        return self.output.save(content, filename)
    
    async def ai_summary(self) -> Path:
        """Generate AI-focused summary."""
        date = datetime.now().strftime('%Y-%m-%d')
        
        user_prompt = f"""
Generate AI-focused TLDR summary for {date}:

FOCUS ON:
- Machine learning breakthroughs
- AI startup funding
- New AI tools and models
- Research releases
- Industry AI adoption

SOURCES:
1. https://tldr.tech/ai (primary)
2. https://tldr.tech/ (scan for AI stories)

OUTPUT: Save as 'ai_summary_{date.replace("-", "")}.md'
START: Check TLDR AI newsletter first.
"""
        
        content = await self._run_task(user_prompt)
        filename = self.output.filename("ai_summary")
        return self.output.save(content, filename)
    
    async def custom_summary(self, user_prompt: str, filename_prefix: str) -> Path:
        """Generate summary with custom user prompt."""
        content = await self._run_task(user_prompt)
        filename = self.output.filename(filename_prefix)
        return self.output.save(content, filename)
    
    def list_summaries(self) -> list:
        """List all generated summaries."""
        return self.output.list_files()
    
    async def schedule_daily(self, hour: int = 9):
        """Run daily summary at specified hour."""
        print(f"📅 Scheduling daily summaries at {hour}:00")
        
        while True:
            now = datetime.now()
            if now.hour == hour and now.minute == 0:
                try:
                    await self.daily_summary()
                except Exception as e:
                    print(f"❌ Scheduled run failed: {e}")
                
                # Wait 1 hour to avoid multiple runs
                await asyncio.sleep(3600)
            else:
                # Check every minute
                await asyncio.sleep(60)