#!/usr/bin/env python3
"""
Vibe-Spec Certification Suite

This script supports the Agent certification workflow:
1. Agent generates individual answer_key_{item_id}.md files (per H2 spec section)
2. Script combines all answer_key files and strips answers to produce question_paper.md

Usage:
  python3 certify.py --combine    # Combine answer_keys -> question_paper.md
"""
import argparse
import re
from pathlib import Path
from datetime import datetime


def combine_and_strip(agent_dir: Path):
    """
    Combine all answer_key_*.md files and generate question_paper.md with stripped answers.
    """
    answer_keys = sorted(agent_dir.glob("answer_key_*.md"))
    
    if not answer_keys:
        print(f"❌ No answer_key_*.md files found in {agent_dir}")
        print("📝 Agent should generate answer_key_{{item_id}}.md files first.")
        return
    
    print(f"📂 Found {len(answer_keys)} answer key files:")
    for ak in answer_keys:
        print(f"   - {ak.name}")
    
    # Combine all answer keys
    combined_content = []
    combined_content.append(f"# Vibe-Spec Certification Exam\n")
    combined_content.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    combined_content.append("> Fill in the 'Student Answer' sections below.\n\n")
    combined_content.append("---\n\n")
    
    for ak_file in answer_keys:
        content = ak_file.read_text()
        
        # Strip answers - replace reference answers with blank sections
        stripped = re.sub(
            r'\*\*Reference Answer\*\*:\s*\n```[^\n]*\n.*?\n```',
            '**Student Answer**:\n```text\n\n\n\n```',
            content,
            flags=re.DOTALL
        )
        
        # Also handle alternative answer formats
        stripped = re.sub(
            r'\*\*Answer\*\*:\s*\n```[^\n]*\n.*?\n```',
            '**Student Answer**:\n```text\n\n\n\n```',
            stripped,
            flags=re.DOTALL
        )
        
        combined_content.append(stripped)
        combined_content.append("\n---\n\n")
    
    # Write question_paper.md
    question_paper = agent_dir / "question_paper.md"
    question_paper.write_text("".join(combined_content))
    print(f"✅ Generated: {question_paper}")


def list_answer_keys(agent_dir: Path):
    """List current answer_key files for reference."""
    answer_keys = sorted(agent_dir.glob("answer_key_*.md"))
    if answer_keys:
        print(f"📋 Current answer keys in {agent_dir}:")
        for ak in answer_keys:
            print(f"   - {ak.name}")
    else:
        print(f"📭 No answer_key_*.md files in {agent_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Vibe-Spec Certification Suite",
        epilog="""
Workflow:
  1. Agent generates: answer_key_{item_id}.md (one per H2 spec section)
  2. Script combines: python3 certify.py --combine
        """
    )
    parser.add_argument("--combine", action="store_true", 
                        help="Combine answer_key_*.md files into question_paper.md")
    parser.add_argument("--list", action="store_true",
                        help="List current answer_key files")
    
    args = parser.parse_args()
    
    agent_dir = Path("tests/specs/agent")
    agent_dir.mkdir(parents=True, exist_ok=True)
    
    if args.combine:
        combine_and_strip(agent_dir)
    elif args.list:
        list_answer_keys(agent_dir)
    else:
        print("Usage: certify.py --combine | --list")
        print("\nAgent Workflow:")
        print("  1. Generate answer_key_{item_id}.md for each H2 spec section")
        print("  2. Run: python3 certify.py --combine")
