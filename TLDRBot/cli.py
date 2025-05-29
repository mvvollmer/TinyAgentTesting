#!/usr/bin/env python3
"""
TLDR Tiny Agent - Command Line Interface
"""
import argparse
import asyncio
from agent import TLDRAgent


async def main():
    parser = argparse.ArgumentParser(description="TLDR Newsletter Tiny Agent")
    parser.add_argument("--config", default="agent.json", help="Config file path")
    
    # Action arguments
    parser.add_argument("--daily", action="store_true", help="Generate daily summary")
    parser.add_argument("--multi", action="store_true", help="Generate multi-source summary") 
    parser.add_argument("--ai", action="store_true", help="Generate AI-focused summary")
    parser.add_argument("--schedule", type=int, metavar="HOUR", help="Schedule daily runs at hour (0-23)")
    parser.add_argument("--list", action="store_true", help="List existing summaries")
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = TLDRAgent(args.config)
    
    # Handle commands
    if args.list:
        summaries = agent.list_summaries()
        print(f"📄 Found {len(summaries)} summaries:")
        for summary in summaries:
            print(f"  - {summary.name}")
        return
    
    if args.daily:
        await agent.daily_summary()
    elif args.multi:
        await agent.multi_source_summary()
    elif args.ai:
        await agent.ai_summary()
    elif args.schedule is not None:
        await agent.schedule_daily(args.schedule)
    else:
        await interactive_mode(agent)


async def interactive_mode(agent: TLDRAgent):
    """Interactive command mode."""
    print("🚀 TLDR Tiny Agent - Interactive Mode")
    print("Commands: daily, multi, ai, list, quit")
    
    while True:
        try:
            command = input("\n> ").strip().lower()
            
            if command in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            elif command in ['daily', 'd']:
                await agent.daily_summary()
                
            elif command in ['multi', 'm']:
                await agent.multi_source_summary()
                
            elif command in ['ai', 'a']:
                await agent.ai_summary()
                
            elif command in ['list', 'l']:
                summaries = agent.list_summaries()
                print(f"📄 {len(summaries)} summaries:")
                for summary in summaries[-5:]:  # Show last 5
                    print(f"  - {summary.name}")
                    
            elif command in ['help', 'h']:
                print("Commands:")
                print("  daily (d) - Generate daily summary")
                print("  multi (m) - Generate multi-source summary") 
                print("  ai (a)    - Generate AI-focused summary")
                print("  list (l)  - List summaries")
                print("  quit (q)  - Exit")
                
            else:
                print("❓ Unknown command. Type 'help' for options.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())