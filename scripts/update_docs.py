#!/usr/bin/env python3
"""
Auto-update documentation with current project structure.

This script generates the file tree for the README based on the actual codebase.
Run manually or as part of pre-commit/CI.
"""

import os
from pathlib import Path
from typing import List, Set


def should_ignore(path: Path, ignore_patterns: Set[str]) -> bool:
    """Check if path should be ignored."""
    parts = path.parts
    for pattern in ignore_patterns:
        if pattern in parts or path.name == pattern:
            return True
    return False


def generate_tree(
    root_dir: Path,
    prefix: str = "",
    is_last: bool = True,
    ignore_patterns: Set[str] = None,
    max_depth: int = 3,
    current_depth: int = 0,
) -> List[str]:
    """
    Generate a tree structure of the directory.

    Args:
        root_dir: Root directory to scan
        prefix: Prefix for tree formatting
        is_last: Whether this is the last item in current level
        ignore_patterns: Patterns to ignore
        max_depth: Maximum depth to traverse
        current_depth: Current depth level

    Returns:
        List of formatted tree lines
    """
    if ignore_patterns is None:
        ignore_patterns = {
            "__pycache__",
            ".pytest_cache",
            ".git",
            ".gitignore",
            "__init__.py",  # Skip empty __init__ files in tree
            ".pyc",
            "results",
            ".DS_Store",
        }

    if current_depth >= max_depth:
        return []

    lines = []

    try:
        # Get all items, sorted (directories first, then files)
        items = sorted(root_dir.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))

        # Filter out ignored patterns
        items = [item for item in items if not should_ignore(item, ignore_patterns)]

        for i, item in enumerate(items):
            is_last_item = i == len(items) - 1

            # Determine the connector
            connector = "└── " if is_last_item else "├── "

            # Add description comment for key directories/files
            description = get_description(item)
            name_with_desc = f"{item.name}{description}"

            lines.append(f"{prefix}{connector}{name_with_desc}")

            # Recurse into directories
            if item.is_dir() and current_depth < max_depth - 1:
                extension = "    " if is_last_item else "│   "
                lines.extend(
                    generate_tree(
                        item,
                        prefix=prefix + extension,
                        is_last=is_last_item,
                        ignore_patterns=ignore_patterns,
                        max_depth=max_depth,
                        current_depth=current_depth + 1,
                    )
                )

    except PermissionError:
        pass

    return lines


def get_description(path: Path) -> str:
    """Get description comment for a file or directory."""
    descriptions = {
        # Directories
        "scenarios": "              # Evaluation scenarios",
        "school_age": "        # Ages 7-12",
        "teenage": "           # Ages 13-18",
        "evaluators": "            # Scoring logic",
        "models": "                # LLM provider adapters",
        "utils": "                 # Helper utilities",
        # Files
        "base.py": "           # Abstract base class",
        "litellm_adapter.py": "   # 100+ providers via LiteLLM",
        "sglang_adapter.py": "    # High-performance local inference",
        "llm_judge.py": "      # LLM-as-judge evaluator",
        "scenario_loader.py": "",
        "results_writer.py": "",
        "schemas.py": "            # Data structures",
        "evaluate.py": "           # Single model evaluation",
        "compare.py": "            # Multi-model comparison",
    }

    return descriptions.get(path.name, "")


def update_readme_tree(readme_path: Path, project_root: Path):
    """Update the project structure in README.md."""

    # Generate the tree
    tree_lines = [f"{project_root.name}/"]
    tree_lines.extend(generate_tree(project_root / "parentingbench", max_depth=3))

    tree_content = "\n".join(tree_lines)

    # Read current README
    readme_content = readme_path.read_text(encoding="utf-8")

    # Find the project structure section
    start_marker = "## Project Structure\n\n```"
    end_marker = "```\n\n---\n\n## Example Scenario"

    if start_marker not in readme_content or end_marker not in readme_content:
        print("⚠️  Could not find project structure markers in README")
        return False

    # Replace the tree
    start_idx = readme_content.index(start_marker) + len(start_marker)
    end_idx = readme_content.index(end_marker)

    new_content = readme_content[:start_idx] + "\n" + tree_content + "\n" + readme_content[end_idx:]

    # Write back
    readme_path.write_text(new_content, encoding="utf-8")
    print(f"✅ Updated project structure in {readme_path}")
    return True


def main():
    """Main function."""
    # Get project root (assuming script is in scripts/)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    readme_path = project_root / "README.md"

    if not readme_path.exists():
        print(f"❌ README.md not found at {readme_path}")
        return 1

    # Update the tree
    success = update_readme_tree(readme_path, project_root)

    if success:
        print("\n📝 Project structure updated successfully!")
        print("   Review the changes and commit if they look good.")
        return 0
    else:
        print("\n❌ Failed to update project structure")
        return 1


if __name__ == "__main__":
    exit(main())
