#!/usr/bin/env python3
"""Test Artifact Hub repository requirements"""
import json
import sys
import urllib.request
import urllib.error
from datetime import datetime

LOG_PATH = "/Users/sasikanth.masini/sample-helm/.cursor/debug.log"

def log(hypothesis_id, location, message, data):
    """Write debug log entry"""
    entry = {
        "sessionId": "debug-session",
        "runId": "artifacthub-test",
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(datetime.now().timestamp() * 1000)
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

def check_url(url, hypothesis_id, check_name):
    """Check if URL is accessible"""
    # #region agent log
    log(hypothesis_id, "test_artifacthub.py:check_url", f"Checking {check_name}", {"url": url})
    # #endregion
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'ArtifactHub/1.0')
        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.getcode()
            content = response.read()
            headers = dict(response.headers)
            # #region agent log
            log(hypothesis_id, "test_artifacthub.py:check_url", f"{check_name} accessible", {
                "url": url,
                "status": status,
                "contentType": headers.get('Content-Type', 'unknown'),
                "contentLength": len(content)
            })
            # #endregion
            return True, status, content, headers
    except urllib.error.HTTPError as e:
        # #region agent log
        log(hypothesis_id, "test_artifacthub.py:check_url", f"{check_name} HTTP error", {
            "url": url,
            "status": e.code,
            "reason": str(e)
        })
        # #endregion
        return False, e.code, None, {}
    except Exception as e:
        # #region agent log
        log(hypothesis_id, "test_artifacthub.py:check_url", f"{check_name} error", {"url": url, "error": str(e)})
        # #endregion
        return False, None, None, {}

def main():
    repo_base = "https://sasikanthmasini.github.io/NDB-Operator-helm"
    
    # #region agent log
    log("H1", "test_artifacthub.py:main", "Starting Artifact Hub validation", {"repoBase": repo_base})
    # #endregion
    
    # Hypothesis 1: index.yaml must be accessible at {repo_url}/index.yaml
    index_url = f"{repo_base}/index.yaml"
    # #region agent log
    log("H1", "test_artifacthub.py:main", "Testing H1: index.yaml accessibility", {"url": index_url})
    # #endregion
    accessible, status, content, headers = check_url(index_url, "H1", "index.yaml")
    
    if not accessible or status != 200:
        # #region agent log
        log("H1", "test_artifacthub.py:main", "H1 REJECTED: index.yaml not accessible", {"status": status})
        # #endregion
        print(f"❌ H1 FAILED: index.yaml not accessible at {index_url} (Status: {status})")
        print(f"   → Fix: Ensure GitHub Pages is enabled and serving from docs/ folder")
        return 1
    else:
        # #region agent log
        log("H1", "test_artifacthub.py:main", "H1 CONFIRMED: index.yaml accessible", {"status": status, "contentType": headers.get('Content-Type')})
        # #endregion
        print(f"✓ H1 PASSED: index.yaml is accessible")
    
    # Hypothesis 2: index.yaml must contain absolute URLs (not relative)
    # #region agent log
    log("H2", "test_artifacthub.py:main", "Testing H2: index.yaml contains absolute URLs", {})
    # #endregion
    try:
        content_str = content.decode('utf-8') if isinstance(content, bytes) else content
        has_absolute_urls = 'https://' in content_str or 'http://' in content_str
        has_relative_urls_only = not has_absolute_urls and ('urls:' in content_str or '- ' in content_str)
        
        # #region agent log
        log("H2", "test_artifacthub.py:main", "H2 URL analysis", {
            "hasAbsoluteUrls": has_absolute_urls,
            "hasRelativeUrlsOnly": has_relative_urls_only,
            "urlsSection": content_str[content_str.find('urls:'):content_str.find('urls:')+200] if 'urls:' in content_str else "not found"
        })
        # #endregion
        
        if not has_absolute_urls:
            # #region agent log
            log("H2", "test_artifacthub.py:main", "H2 REJECTED: No absolute URLs found", {})
            # #endregion
            print(f"❌ H2 FAILED: index.yaml does not contain absolute URLs")
            print(f"   → Fix: Update chart URLs in index.yaml to use absolute URLs")
            return 1
        else:
            # #region agent log
            log("H2", "test_artifacthub.py:main", "H2 CONFIRMED: Absolute URLs found", {})
            # #endregion
            print(f"✓ H2 PASSED: index.yaml contains absolute URLs")
    except Exception as e:
        # #region agent log
        log("H2", "test_artifacthub.py:main", "H2 ERROR: Failed to parse", {"error": str(e)})
        # #endregion
        print(f"❌ H2 ERROR: Failed to parse index.yaml: {e}")
        return 1
    
    # Hypothesis 3: Chart package URLs in index.yaml must be accessible
    # #region agent log
    log("H3", "test_artifacthub.py:main", "Testing H3: Chart package URLs accessible", {})
    # #endregion
    import re
    chart_urls = re.findall(r'https?://[^\s"\']+\.tgz', content_str)
    # #region agent log
    log("H3", "test_artifacthub.py:main", "Found chart URLs", {"urls": chart_urls, "count": len(chart_urls)})
    # #endregion
    
    if not chart_urls:
        # #region agent log
        log("H3", "test_artifacthub.py:main", "H3 REJECTED: No chart URLs found", {})
        # #endregion
        print(f"❌ H3 FAILED: No chart package URLs found in index.yaml")
        return 1
    
    all_accessible = True
    for chart_url in chart_urls:
        # #region agent log
        log("H3", "test_artifacthub.py:main", "Checking chart URL", {"url": chart_url})
        # #endregion
        accessible, status, _, _ = check_url(chart_url, "H3", f"Chart {chart_url}")
        if not accessible or status != 200:
            # #region agent log
            log("H3", "test_artifacthub.py:main", "H3 REJECTED: Chart URL not accessible", {"url": chart_url, "status": status})
            # #endregion
            print(f"❌ H3 FAILED: Chart package not accessible: {chart_url} (Status: {status})")
            all_accessible = False
        else:
            # #region agent log
            log("H3", "test_artifacthub.py:main", "Chart URL accessible", {"url": chart_url, "status": status})
            # #endregion
    
    if not all_accessible:
        return 1
    else:
        # #region agent log
        log("H3", "test_artifacthub.py:main", "H3 CONFIRMED: All chart URLs accessible", {})
        # #endregion
        print(f"✓ H3 PASSED: All chart package URLs are accessible")
    
    # Hypothesis 4: Chart URLs should use GitHub Pages URL, not raw.githubusercontent.com
    # #region agent log
    log("H4", "test_artifacthub.py:main", "Testing H4: Chart URLs use GitHub Pages format", {})
    # #endregion
    uses_raw_github = any('raw.githubusercontent.com' in url for url in chart_urls)
    uses_github_pages = any('github.io' in url for url in chart_urls)
    
    # #region agent log
    log("H4", "test_artifacthub.py:main", "H4 URL format analysis", {
        "usesRawGithub": uses_raw_github,
        "usesGithubPages": uses_github_pages,
        "chartUrls": chart_urls
    })
    # #endregion
    
    if uses_raw_github and not uses_github_pages:
        # #region agent log
        log("H4", "test_artifacthub.py:main", "H4 REJECTED: Using raw.githubusercontent.com instead of GitHub Pages", {})
        # #endregion
        print(f"⚠️  H4 WARNING: Chart URLs use raw.githubusercontent.com instead of GitHub Pages")
        print(f"   → Recommendation: Update to GitHub Pages URLs for consistency")
        print(f"   → Current: {chart_urls[0]}")
        print(f"   → Should be: {repo_base}/ndb-operator-0.5.3.tgz")
    else:
        # #region agent log
        log("H4", "test_artifacthub.py:main", "H4 CONFIRMED: Using GitHub Pages URLs", {})
        # #endregion
        print(f"✓ H4 PASSED: Chart URLs use GitHub Pages format")
    
    # Hypothesis 5: Repository URL format for Artifact Hub
    # #region agent log
    log("H5", "test_artifacthub.py:main", "Testing H5: Repository URL format", {})
    # #endregion
    print(f"\n📋 Summary:")
    print(f"   Repository URL to use in Artifact Hub: {repo_base}")
    print(f"   This URL should point to your GitHub Pages site")
    print(f"\n💡 Next steps:")
    print(f"   1. Ensure index.yaml uses GitHub Pages URLs (not raw.githubusercontent.com)")
    print(f"   2. Add repository in Artifact Hub using: {repo_base}")
    print(f"   3. Artifact Hub will fetch: {repo_base}/index.yaml")
    
    # #region agent log
    log("H5", "test_artifacthub.py:main", "H5 CONFIRMED: Repository URL format correct", {"repoUrl": repo_base})
    # #endregion
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

