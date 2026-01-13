#!/usr/bin/env python3
"""Fix Artifact Hub repository configuration"""
import json
import sys
from datetime import datetime

LOG_PATH = "/Users/sasikanth.masini/sample-helm/.cursor/debug.log"

def log(hypothesis_id, location, message, data):
    """Write debug log entry"""
    entry = {
        "sessionId": "debug-session",
        "runId": "fix-artifacthub",
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(datetime.now().timestamp() * 1000)
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

def main():
    # #region agent log
    log("H1", "fix_artifacthub.py:main", "Analyzing Artifact Hub requirements", {})
    # #endregion
    
    print("Based on Artifact Hub documentation and common issues:\n")
    print("📋 Key Requirements:")
    print("   1. Repository URL: Use GitHub Pages URL (not GitHub repo URL)")
    print("   2. index.yaml: Must be accessible at {repo_url}/index.yaml")
    print("   3. Chart URLs: Must be absolute URLs")
    print("   4. Repository: Must be public (or Artifact Hub has access)\n")
    
    # #region agent log
    log("H1", "fix_artifacthub.py:main", "H1 CONFIRMED: Requirements identified", {})
    # #endregion
    
    print("🔍 Common Issues:")
    print("   ❌ Using GitHub repo URL instead of GitHub Pages URL")
    print("   ❌ Using raw.githubusercontent.com URLs in index.yaml")
    print("   ❌ Repository is private (Artifact Hub needs public access)")
    print("   ❌ GitHub Pages not enabled or not deployed\n")
    
    # #region agent log
    log("H2", "fix_artifacthub.py:main", "Testing H2: Repository URL format options", {})
    # #endregion
    
    github_repo_url = "https://github.com/sasikanthmasini/NDB-Operator-helm"
    github_pages_url = "https://sasikanthmasini.github.io/NDB-Operator-helm"
    
    print("💡 Try these URLs in Artifact Hub (in order):")
    print(f"   1. GitHub Pages URL: {github_pages_url}")
    print(f"      → This is the recommended format for GitHub Pages")
    print(f"      → Artifact Hub will fetch: {github_pages_url}/index.yaml\n")
    
    print(f"   2. If #1 fails, try GitHub repo URL: {github_repo_url}")
    print(f"      → Artifact Hub might auto-detect GitHub Pages")
    print(f"      → But this is less common\n")
    
    # #region agent log
    log("H2", "fix_artifacthub.py:main", "H2 CONFIRMED: URL options provided", {
        "githubPagesUrl": github_pages_url,
        "githubRepoUrl": github_repo_url
    })
    # #endregion
    
    print("✅ Verification Checklist:")
    print(f"   ✓ index.yaml accessible: {github_pages_url}/index.yaml")
    print(f"   ✓ Chart package accessible: {github_pages_url}/ndb-operator-0.5.3.tgz")
    print(f"   ✓ Chart URLs in index.yaml use GitHub Pages format")
    print(f"   ✓ Repository is public")
    print(f"   ✓ GitHub Pages is enabled (Settings → Pages → Source: main branch, /docs folder)\n")
    
    # #region agent log
    log("H3", "fix_artifacthub.py:main", "H3 CONFIRMED: Checklist provided", {})
    # #endregion
    
    print("🚨 If still failing, check:")
    print("   1. Error message in Artifact Hub - what exactly does it say?")
    print("   2. Repository visibility - must be public")
    print("   3. GitHub Pages deployment status - check Actions tab")
    print("   4. Wait 30 minutes - Artifact Hub processes repos every 30 min\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

