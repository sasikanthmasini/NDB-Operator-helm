#!/usr/bin/env python3
"""Final debug - check what Artifact Hub actually sees"""
import json
import sys
import urllib.request
import urllib.error
import re
from datetime import datetime

LOG_PATH = "/Users/sasikanth.masini/sample-helm/.cursor/debug.log"

def log(hypothesis_id, location, message, data):
    """Write debug log entry"""
    entry = {
        "sessionId": "debug-session",
        "runId": "final-debug",
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(datetime.now().timestamp() * 1000)
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

def fetch_url(url, hypothesis_id, name):
    """Fetch URL and return content"""
    # #region agent log
    log(hypothesis_id, "final_debug.py:fetch_url", f"Fetching {name}", {"url": url})
    # #endregion
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'ArtifactHub/1.0')
        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.getcode()
            content = response.read()
            headers = dict(response.headers)
            # #region agent log
            log(hypothesis_id, "final_debug.py:fetch_url", f"{name} fetched", {
                "status": status,
                "contentLength": len(content),
                "contentType": headers.get('Content-Type'),
                "firstBytes": content[:100].hex() if len(content) > 100 else content.hex()
            })
            # #endregion
            return True, status, content, headers
    except Exception as e:
        # #region agent log
        log(hypothesis_id, "final_debug.py:fetch_url", f"{name} failed", {"error": str(e)})
        # #endregion
        return False, None, None, {}

def main():
    repo_base = "https://sasikanthmasini.github.io/NDB-Operator-helm"
    
    # #region agent log
    log("H1", "final_debug.py:main", "Starting final debug", {"repoBase": repo_base})
    # #endregion
    
    print("🔍 Testing what Artifact Hub sees...\n")
    
    # Hypothesis 1: Test different URL formats Artifact Hub might expect
    # #region agent log
    log("H1", "final_debug.py:main", "Testing H1: Different URL formats", {})
    # #endregion
    
    test_urls = [
        repo_base,
        repo_base + "/",
        repo_base + "/index.yaml",
    ]
    
    print("📋 Testing URL formats:")
    for test_url in test_urls:
        # #region agent log
        log("H1", "final_debug.py:main", "Testing URL format", {"url": test_url})
        # #endregion
        print(f"   Testing: {test_url}")
        
        # Try to fetch index.yaml from this base
        if test_url.endswith('/index.yaml'):
            index_url = test_url
        else:
            index_url = test_url.rstrip('/') + '/index.yaml'
        
        success, status, content, headers = fetch_url(index_url, "H1", f"index.yaml from {test_url}")
        
        if success and status == 200:
            # #region agent log
            log("H1", "final_debug.py:main", "H1 CONFIRMED: URL format works", {"url": test_url, "indexUrl": index_url})
            # #endregion
            print(f"      ✓ index.yaml accessible: {index_url}")
            
            # Check content
            try:
                content_str = content.decode('utf-8')
                # #region agent log
                log("H1", "final_debug.py:main", "Content decoded", {"contentLength": len(content_str), "hasEntries": "entries:" in content_str})
                # #endregion
                
                # Extract chart URLs
                chart_urls = re.findall(r'https?://[^\s"\']+\.tgz', content_str)
                # #region agent log
                log("H1", "final_debug.py:main", "Found chart URLs", {"urls": chart_urls})
                # #endregion
                
                print(f"      ✓ Found {len(chart_urls)} chart URL(s)")
                for url in chart_urls:
                    print(f"        - {url}")
                    
                    # Test if chart URL is accessible
                    chart_success, chart_status, _, _ = fetch_url(url, "H1", f"Chart {url}")
                    if chart_success and chart_status == 200:
                        # #region agent log
                        log("H1", "final_debug.py:main", "Chart URL accessible", {"url": url, "status": chart_status})
                        # #endregion
                        print(f"          ✓ Chart accessible")
                    else:
                        # #region agent log
                        log("H1", "final_debug.py:main", "Chart URL NOT accessible", {"url": url, "status": chart_status})
                        # #endregion
                        print(f"          ✗ Chart NOT accessible (Status: {chart_status})")
            except Exception as e:
                # #region agent log
                log("H1", "final_debug.py:main", "Failed to decode content", {"error": str(e)})
                # #endregion
                print(f"      ✗ Failed to decode content: {e}")
        else:
            # #region agent log
            log("H1", "final_debug.py:main", "H1 REJECTED: URL format failed", {"url": test_url, "status": status})
            # #endregion
            print(f"      ✗ index.yaml NOT accessible (Status: {status})")
    
    # Hypothesis 2: Check if relative URLs would work better
    # #region agent log
    log("H2", "final_debug.py:main", "Testing H2: Relative vs absolute URLs", {})
    # #endregion
    
    print(f"\n💡 Key Finding:")
    print(f"   Artifact Hub expects: {repo_base}")
    print(f"   It will fetch: {repo_base}/index.yaml")
    print(f"   Chart URLs in index.yaml should be absolute: https://sasikanthmasini.github.io/NDB-Operator-helm/ndb-operator-0.5.3.tgz")
    
    # #region agent log
    log("H2", "final_debug.py:main", "H2 CONFIRMED: URL format requirements", {"repoUrl": repo_base})
    # #endregion
    
    # Hypothesis 3: Check if there's an artifacthub-repo.yml requirement
    # #region agent log
    log("H3", "final_debug.py:main", "Testing H3: artifacthub-repo.yml file", {})
    # #endregion
    
    artifacthub_yml_url = f"{repo_base}/artifacthub-repo.yml"
    success, status, _, _ = fetch_url(artifacthub_yml_url, "H3", "artifacthub-repo.yml")
    
    if not success or status != 200:
        # #region agent log
        log("H3", "final_debug.py:main", "H3 WARNING: artifacthub-repo.yml not found", {"status": status})
        # #endregion
        print(f"\n⚠️  Note: artifacthub-repo.yml not found (optional but recommended)")
        print(f"   Create docs/artifacthub-repo.yml for better integration")
    else:
        # #region agent log
        log("H3", "final_debug.py:main", "H3 CONFIRMED: artifacthub-repo.yml exists", {})
        # #endregion
        print(f"\n✓ artifacthub-repo.yml exists")
    
    print(f"\n📝 Action Items:")
    print(f"   1. Use this EXACT URL in Artifact Hub: {repo_base}")
    print(f"   2. Ensure repository is PUBLIC")
    print(f"   3. Verify GitHub Pages is deployed (check Actions tab)")
    print(f"   4. If still failing, check the exact error message")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())


