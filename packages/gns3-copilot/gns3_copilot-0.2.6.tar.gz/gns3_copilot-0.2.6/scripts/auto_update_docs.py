#!/usr/bin/env python3
"""
Automatic Documentation Update Script using Zhipu GLM-4.5-X API

This script has two modes:
1. Local mode: Creates PR with AI-generated title and description (no doc updates)
2. GitHub Actions mode: Updates documentation and creates PR comment

Usage:
    # Local mode - create PR
    export ZHIPU_API_KEY="your-api-key"
    export GITHUB_TOKEN="your-github-token"
    export REPO_OWNER="yueguobin"
    export REPO_NAME="gns3-copilot"
    python scripts/auto_update_docs.py
    
    # GitHub Actions mode - update docs and comment
    # Automatically triggered by PR to Development branch
"""

import os
import sys
import subprocess
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import re

# Configuration
ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY')
ZHIPU_MODEL = os.getenv('ZHIPU_MODEL', 'GLM-4.5-X')
PR_NUMBER = os.getenv('PR_NUMBER')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_OWNER = os.getenv('REPO_OWNER')
REPO_NAME = os.getenv('REPO_NAME')


def get_changed_files(base_ref: str = 'origin/Development') -> List[str]:
    """Get list of changed files in the PR"""
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only', f'{base_ref}...HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return [f for f in result.stdout.split('\n') if f]
    except subprocess.CalledProcessError as e:
        print(f"Error getting changed files: {e}")
        return []


def get_relevant_files(changed_files: List[str]) -> Tuple[List[str], str]:
    """Get relevant files based on mode"""
    if PR_NUMBER:
        # GitHub Actions mode: only source code changes
        relevant = [f for f in changed_files if f.startswith('src/')]
        change_type = "source code"
    else:
        # Local mode: all project files
        supported_dirs = [
            'src/',
            'docs/',
            'scripts/',
            '.github/',
            'tests/',
        ]
        supported_files = ['pyproject.toml', 'Makefile', 'LICENSE']
        
        relevant = []
        for f in changed_files:
            if f.startswith(tuple(supported_dirs)) or f in supported_files:
                relevant.append(f)
        change_type = "project changes"
    
    return relevant, change_type


def get_diff_content(base_ref: str = 'origin/Development') -> str:
    """Get git diff content"""
    try:
        result = subprocess.run(
            ['git', 'diff', f'{base_ref}...HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error getting diff: {e}")
        return ""


def call_zhipu_api_for_pr(prompt: str) -> Optional[Dict]:
    """Call Zhipu API for PR generation (local mode)"""
    if not ZHIPU_API_KEY:
        print("ERROR: ZHIPU_API_KEY not found")
        return None
    
    import urllib.request
    import urllib.error
    
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {ZHIPU_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": ZHIPU_MODEL,
        "messages": [
            {
                "role": "system",
                "content": """You are creating a GitHub Pull Request for the GNS3 Copilot project.
Analyze the code changes and generate a PR title and description following this exact template:

## 🚀 Change Type
- [x] ✨ New Feature
- [ ] 🐞 Bug Fix
- [ ] 🔧 Refactor/Maintenance
- [ ] 📚 Documentation

## 📝 Description of Changes
[Write a detailed description here, explaining what changes were made and why]

## 🧪 Testing Verification
- [ ] Verified in local environment (Local GNS3/Nornir Test)
- [ ] Run pytest and passed
- [ ] mypy and ruff checks passed

## 🔗 Related Issues
Fixes #

Rules:
1. Automatically select and mark the appropriate Change Type with [x]
2. Keep the Testing Verification and Related Issues sections exactly as shown
3. Write a clear, detailed Description of Changes
4. PR title should be concise (max 72 characters)

Output ONLY valid JSON:
{
    "pr_title": "Concise PR title",
    "pr_description": "Full description following the template format"
}"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 2000
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            content = result['choices'][0]['message']['content']
            
            # Parse JSON from content
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                return json.loads(json_match.group())
            return None
            
    except urllib.error.HTTPError as e:
        print(f"API Error {e.code}: {e.read().decode('utf-8')}")
        return None
    except Exception as e:
        print(f"Error calling Zhipu API: {e}")
        return None


def call_zhipu_api_for_docs(prompt: str) -> Optional[Dict]:
    """Call Zhipu API for documentation updates (GitHub Actions mode)"""
    if not ZHIPU_API_KEY:
        print("ERROR: ZHIPU_API_KEY not found")
        return None
    
    import urllib.request
    import urllib.error
    
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {ZHIPU_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": ZHIPU_MODEL,
        "messages": [
            {
                "role": "system",
                "content": """You are a documentation assistant for GNS3 Copilot project. 
Analyze code changes and provide:
1. English change summary for PR comment
2. Chinese change summary for README_ZH.md
3. Documentation updates for README.md and README_ZH.md

IMPORTANT: Use the EXACT section names:
- For README.md: use "Core Features" (NOT "Features")
- For README_ZH.md: use "核心功能" (NOT "功能列表")

Output in JSON format:
{
    "english_summary": "English change summary for PR comment",
    "chinese_summary": "Chinese change summary",
    "doc_updates": {
        "README.md": {"section": "Core Features", "content": "new content to add"},
        "README_ZH.md": {"section": "核心功能", "content": "新功能内容"}
    }
}"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 4000
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            content = result['choices'][0]['message']['content']
            
            # Parse JSON from content
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                return json.loads(json_match.group())
            return None
            
    except urllib.error.HTTPError as e:
        print(f"API Error {e.code}: {e.read().decode('utf-8')}")
        return None
    except Exception as e:
        print(f"Error calling Zhipu API: {e}")
        return None


def update_documentation(doc_updates: Dict) -> Dict[str, str]:
    """Update documentation files"""
    updated_files = {}
    
    for doc_file, update_info in doc_updates.items():
        doc_path = Path(doc_file)
        
        if not doc_path.exists():
            print(f"Warning: {doc_file} not found, skipping")
            continue
        
        content = doc_path.read_text(encoding='utf-8')
        section = update_info.get('section', '')
        new_content = update_info.get('content', '')
        
        # Find and update section
        if section:
            # Define common section name mappings for README files
            # Map canonical section name to possible variations (without markdown prefixes)
            section_mappings = {
                "Core Features": [
                    "Core Features", 
                    "Features"
                ],
                "核心功能": [
                    "核心功能", 
                    "功能列表"
                ],
            }
            
            # Get possible section names
            possible_sections = section_mappings.get(section, [section])
            
            # Try each possible section name
            match = None
            for possible_section in possible_sections:
                # Look for section header (e.g., "## Core Features" or "### Core Features")
                # More flexible pattern that handles various markdown heading formats
                pattern = rf'(#{1,6}\s+{re.escape(possible_section)}\s*$)'
                match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
                if match:
                    break
            
            if match:
                # Insert new content after the section header
                insert_pos = match.end()
                updated_content = content[:insert_pos] + new_content + '\n' + content[insert_pos:]
                doc_path.write_text(updated_content, encoding='utf-8')
                updated_files[doc_file] = "Section updated"
                print(f"✓ Updated {doc_file}")
            else:
                print(f"✗ Section '{section}' not found in {doc_file}")
                updated_files[doc_file] = "Section not found"
    
    return updated_files


def commit_changes(message: str) -> bool:
    """Commit changes to git (note: push is handled by GitHub Actions workflow)"""
    try:
        subprocess.run(['git', 'add', '.'], check=True)
        result = subprocess.run(
            ['git', 'commit', '-m', message],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print("✓ Changes committed successfully")
            # Note: git push is handled by GitHub Actions workflow
            return True
        elif 'nothing to commit' in result.stdout.lower():
            print("No changes to commit")
            return True
        else:
            print(f"Commit failed: {result.stdout}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"Error committing changes: {e}")
        return False


def create_pr_comment(summary: str) -> bool:
    """Create PR comment using GitHub API"""
    if not GITHUB_TOKEN or not PR_NUMBER:
        print("Missing GITHUB_TOKEN or PR_NUMBER, skipping PR comment")
        return False
    
    import urllib.request
    
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{PR_NUMBER}/comments"
    
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    
    data = {
        "body": f"""## 📝 Documentation Update Summary

{summary}

---
*This comment was automatically generated by Zhipu GLM-4.5-X API*"""
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"✓ PR comment created (#{PR_NUMBER})")
            return True
            
    except Exception as e:
        print(f"Error creating PR comment: {e}")
        return False


def create_pull_request(title: str, description: str, base_branch: str = 'Development') -> Optional[int]:
    """Create Pull Request using GitHub API"""
    if not GITHUB_TOKEN:
        print("Missing GITHUB_TOKEN, skipping PR creation")
        return None
    
    # Get current branch name
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        head_branch = result.stdout.strip()
    except subprocess.CalledProcessError:
        print("Failed to get current branch name")
        return None
    
    import urllib.request
    
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls"
    
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    
    data = {
        "title": title,
        "body": description,
        "head": head_branch,
        "base": base_branch
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            pr_number = result.get('number')
            print(f"✓ Pull Request created: #{pr_number}")
            print(f"  URL: {result.get('html_url')}")
            return pr_number
            
    except Exception as e:
        print(f"Error creating Pull Request: {e}")
        return None


def main():
    """Main execution"""
    print("=" * 60)
    print("GNS3 Copilot - Automatic Documentation Update")
    print("=" * 60)
    print()
    
    # Get code changes
    print("📋 Analyzing code changes...")
    changed_files = get_changed_files()
    diff_content = get_diff_content()
    
    if not changed_files:
        print("No changed files detected. Exiting.")
        return 0
    
    print(f"✓ Found {len(changed_files)} changed files")
    print(f"  Files: {', '.join(changed_files[:5])}...")
    print()
    
    # Filter relevant files based on mode
    relevant_files, change_type = get_relevant_files(changed_files)
    if not relevant_files:
        print(f"No {change_type} detected. Exiting.")
        return 0
    
    print(f"✓ Found {len(relevant_files)} {change_type}")
    print()
    
    # Two modes: Local (create PR) vs GitHub Actions (update docs)
    if PR_NUMBER:
        # GitHub Actions mode: Update documentation and create comment
        print(f"🤖 GitHub Actions mode detected (PR #{PR_NUMBER})")
        print(f"🤖 Calling Zhipu {ZHIPU_MODEL} API for documentation updates...")
        
        prompt = f"""Analyze the following code changes in the GNS3 Copilot project:

Changed files: {', '.join(relevant_files)}

Git diff:
{diff_content[:5000]}

Provide:
1. English summary of changes for PR comment
2. Chinese summary for README_ZH.md
3. Suggested documentation updates for README.md and README_ZH.md
"""
        
        api_response = call_zhipu_api_for_docs(prompt)
        
        if not api_response:
            print("✗ Failed to get response from Zhipu API")
            return 1
        
        print("✓ Received response from Zhipu API")
        print()
        
        english_summary = api_response.get('english_summary', 'No summary available')
        chinese_summary = api_response.get('chinese_summary', '')
        doc_updates = api_response.get('doc_updates', {})
        
        print("📄 English Summary:")
        print(english_summary)
        print()
        
        if chinese_summary:
            print("📝 Chinese Summary:")
            print(chinese_summary)
            print()
        
        # Update documentation
        if doc_updates:
            print("📚 Updating documentation...")
            updated_files = update_documentation(doc_updates)
            print()
            
            if updated_files:
                # Commit changes
                commit_msg = f"docs: auto-update documentation\n\n[skip ci]\nSummary: {english_summary[:100]}"
                commit_changes(commit_msg)
            else:
                print("No documentation updates applied")
        else:
            print("No documentation updates suggested")
        
        # Create PR comment
        print("💬 Creating PR comment...")
        create_pr_comment(english_summary)
        print()
        
    else:
        # Local mode: Create PR only (no documentation updates)
        print("🤖 Local mode detected (creating PR)")
        print(f"🤖 Calling Zhipu {ZHIPU_MODEL} API for PR generation...")
        
        prompt = f"""Analyze the following code changes in the GNS3 Copilot project:

Changed files: {', '.join(relevant_files)}

Git diff:
{diff_content[:5000]}

Generate a PR title and description following the provided template format.
"""
        
        api_response = call_zhipu_api_for_pr(prompt)
        
        if not api_response:
            print("✗ Failed to get response from Zhipu API")
            return 1
        
        print("✓ Received response from Zhipu API")
        print()
        
        pr_title = api_response.get('pr_title', 'Documentation update')
        pr_description = api_response.get('pr_description', 'See description in PR')
        
        print("📄 PR Title:")
        print(f"  {pr_title}")
        print()
        
        print("📄 PR Description (first 500 chars):")
        print("  " + pr_description[:500].replace('\n', '\n  '))
        if len(pr_description) > 500:
            print("  ...")
        print()
        
        # Create PR
        print("🔀 Creating Pull Request...")
        pr_num = create_pull_request(pr_title, pr_description)
        if pr_num:
            print()
            print(f"✓ PR #{pr_num} created successfully!")
            print("  Documentation will be updated by GitHub Actions when PR is opened.")
        else:
            print()
            print("⚠ Could not create PR automatically.")
            print(f"  Please create PR manually with:")
            print(f"    Title: {pr_title}")
            print(f"    Description: {pr_description[:200]}...")
        print()
    
    print("=" * 60)
    print("✓ Operation completed successfully")
    print("=" * 60)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
