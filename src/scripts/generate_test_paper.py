#!/usr/bin/env python3
"""
Test Paper Generator - Strips answers from answer_keys to create test papers.

Implements: Answer Key Format Plan (strippable answers)

Usage: python generate_test_paper.py [tests_dir]

Output:
  - tests/specs/agent/test_paper.md     (L1 Agent contracts)
  - tests/specs/decision/test_paper.md  (L3 Decisions)
"""
import re
import sys
from pathlib import Path


def strip_answers(content: str) -> str:
    """Remove content between ANSWER_START and ANSWER_END markers."""
    pattern = r'<!-- ANSWER_START -->.*?<!-- ANSWER_END -->'
    return re.sub(pattern, '<!-- [Answer hidden for testing] -->', content, flags=re.DOTALL)


def generate_test_paper(answer_key_dir: Path, output_file: Path, paper_type: str):
    """Generate a test paper from answer_key files."""
    questions = []
    
    for f in sorted(answer_key_dir.glob("answer_key_*.md")):
        content = f.read_text()
        
        # Extract ID from header
        id_match = re.search(r'^# Answer Key: (.+)$', content, re.MULTILINE)
        if not id_match:
            continue
        spec_id = id_match.group(1)
        
        # Strip answers
        stripped = strip_answers(content)
        
        # Remove the "Answer Key:" header and verify_spec comment
        stripped = re.sub(r'^# Answer Key: .+\n', '', stripped)
        stripped = re.sub(r'<!-- @verify_spec\(.+\) -->\n*', '', stripped)
        
        questions.append({
            'id': spec_id,
            'content': stripped.strip()
        })
    
    # Build test paper
    header = f"""# Test Paper: {paper_type.upper()} Compliance Test

> ⚠️ **IMPORTANT**: Answer based ONLY on `specs/` content.
> Do NOT use external knowledge or infer beyond what is explicitly stated in the spec.
> Your answers will be graded against the exact spec definitions.

---

"""
    
    body = ""
    for i, q in enumerate(questions, 1):
        body += f"## Q{i}: {q['id']}\n\n"
        body += q['content']
        body += "\n\n---\n\n"
    
    output_file.write_text(header + body)
    print(f"✅ Generated {output_file.name} with {len(questions)} questions")
    
    return len(questions)


def main():
    project_root = Path.cwd()
    tests_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else project_root / 'tests'
    specs_dir = tests_dir / 'specs'
    
    total = 0
    
    # Generate L1 Agent test paper
    agent_dir = specs_dir / 'agent'
    if agent_dir.exists():
        total += generate_test_paper(
            agent_dir, 
            agent_dir / 'test_paper.md',
            'L1 Agent Contract'
        )
    
    # Generate L3 Decision test paper
    decision_dir = specs_dir / 'decision'
    if decision_dir.exists():
        total += generate_test_paper(
            decision_dir,
            decision_dir / 'test_paper.md', 
            'L3 Decision'
        )
    
    print(f"\n📝 Total questions generated: {total}")


if __name__ == "__main__":
    main()
