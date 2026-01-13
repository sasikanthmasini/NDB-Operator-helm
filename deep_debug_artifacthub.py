#!/usr/bin/env python3
"""Deep debug Artifact Hub repository validation - simulate Artifact Hub behavior"""
import json
import sys
import urllib.request
import urllib.error
import yaml
from datetime import datetime

LOG_PATH = "/Users/sasikanth.masini/sample-helm/.cursor/debug.log"

def log(hypothesis_id, location, message, data):
    """Write debug log entry"""
    entry = {
        "sessionId": "debug-session",
        "runId": "deep-debug",
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(datetime.now().timestamp() * 1000)
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

def fetch_and_parse_index(repo_url, hypothesis_id):
    """Simulate Artifact Hub fetching and parsing index.yaml"""
    index_url = f"{repo_url}/index.yaml"
    
    # #region agent log
    log(hypothesis_id, "deep_debug_artifacthub.py:fetch_and_parse_index", "Fetching index.yaml", {"url": index_url})
    # #endregion
    
    try:
        req = urllib.request.Request(index_url)
        req.add_header('User-Agent', 'ArtifactHub/1.0')
        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.getcode()
            content = response.read()
            headers = dict(response.headers)
            
            # #region agent log
            log(hypothesis_id, "deep_debug_artifacthub.py:fetch_and_parse_index", "index.yaml fetched", {
                "status": status,
                "contentLength": len(content),
                "contentType": headers.get('Content-Type'),
                "contentEncoding": headers.get('Content-Encoding', 'none')
            })
            # #endregion
            
            # Parse YAML
            try:
                content_str = content.decode('utf-8')
                index_data = yaml.safe_load(content_str)
                
                # #region agent log
                log(hypothesis_id, "deep_debug_artifacthub.py:fetch_and_parse_index", "index.yaml parsed successfully", {
                    "hasEntries": "entries" in index_data if index_data else False,
                    "entryCount": len(index_data.get("entries", {})) if index_data else 0
                })
                # #endregion
                
                return True, index_data, content_str
            except yaml.YAMLError as e:
                # #region agent log
                log(hypothesis_id, "deep_debug_artifacthub.py:fetch_and_parse_index", "YAML parse error", {"error": str(e)})
                # #endregion
                return False, None, None
                
    except Exception as e:
        # #region agent log
        log(hypothesis_id, "deep_debug_artifacthub.py:fetch_and_parse_index", "Fetch error", {"error": str(e)})
        # #endregion
        return False, None, None

def validate_chart_urls(index_data, repo_url, hypothesis_id):
    """Validate all chart URLs in index.yaml"""
    if not index_data or "entries" not in index_data:
        # #region agent log
        log(hypothesis_id, "deep_debug_artifacthub.py:validate_chart_urls", "No entries found", {})
        # #endregion
        return False, []
    
    chart_urls = []
    for chart_name, versions in index_data["entries"].items():
        for version in versions:
            if "urls" in version:
                chart_urls.extend(version["urls"])
    
    # #region agent log
    log(hypothesis_id, "deep_debug_artifacthub.py:validate_chart_urls", "Found chart URLs", {
        "urls": chart_urls,
        "count": len(chart_urls)
    })
    # #endregion
    
    all_valid = True
    for chart_url in chart_urls:
        # #region agent log
        log(hypothesis_id, "deep_debug_artifacthub.py:validate_chart_urls", "Validating chart URL", {"url": chart_url})
        # #endregion
        
        # Handle relative URLs
        if not chart_url.startswith('http'):
            chart_url = f"{repo_url}/{chart_url}"
            # #region agent log
            log(hypothesis_id, "deep_debug_artifacthub.py:validate_chart_urls", "Converted relative to absolute", {"absoluteUrl": chart_url})
            # #endregion
        
        try:
            req = urllib.request.Request(chart_url)
            req.add_header('User-Agent', 'ArtifactHub/1.0')
            with urllib.request.urlopen(req, timeout=10) as response:
                status = response.getcode()
                # #region agent log
                log(hypothesis_id, "deep_debug_artifacthub.py:validate_chart_urls", "Chart URL accessible", {
                    "url": chart_url,
                    "status": status
                })
                # #endregion
                if status != 200:
                    all_valid = False
        except Exception as e:
            # #region agent log
            log(hypothesis_id, "deep_debug_artifacthub.py:validate_chart_urls", "Chart URL not accessible", {
                "url": chart_url,
                "error": str(e)
            })
            # #endregion
            all_valid = False
    
    return all_valid, chart_urls

def main():
    repo_url = "https://sasikanthmasini.github.io/NDB-Operator-helm"
    
    # #region agent log
    log("H1", "deep_debug_artifacthub.py:main", "Starting deep debug", {"repoUrl": repo_url})
    # #endregion
    
    # Hypothesis 1: Artifact Hub can fetch and parse index.yaml
    # #region agent log
    log("H1", "deep_debug_artifacthub.py:main", "Testing H1: Artifact Hub can fetch index.yaml", {})
    # #endregion
    success, index_data, content_str = fetch_and_parse_index(repo_url, "H1")
    
    if not success or not index_data:
        # #region agent log
        log("H1", "deep_debug_artifacthub.py:main", "H1 REJECTED: Cannot fetch/parse index.yaml", {})
        # #endregion
        print("❌ H1 FAILED: Cannot fetch or parse index.yaml")
        return 1
    else:
        # #region agent log
        log("H1", "deep_debug_artifacthub.py:main", "H1 CONFIRMED: index.yaml fetched and parsed", {})
        # #endregion
        print("✓ H1 PASSED: index.yaml fetched and parsed successfully")
    
    # Hypothesis 2: index.yaml has valid structure (entries, apiVersion, etc.)
    # #region agent log
    log("H2", "deep_debug_artifacthub.py:main", "Testing H2: index.yaml structure validation", {})
    # #endregion
    
    required_fields = ["apiVersion", "entries"]
    missing_fields = [field for field in required_fields if field not in index_data]
    
    # #region agent log
    log("H2", "deep_debug_artifacthub.py:main", "H2 structure check", {
        "hasApiVersion": "apiVersion" in index_data,
        "hasEntries": "entries" in index_data,
        "missingFields": missing_fields,
        "entryCount": len(index_data.get("entries", {}))
    })
    # #endregion
    
    if missing_fields:
        # #region agent log
        log("H2", "deep_debug_artifacthub.py:main", "H2 REJECTED: Missing required fields", {"missing": missing_fields})
        # #endregion
        print(f"❌ H2 FAILED: Missing required fields: {missing_fields}")
        return 1
    else:
        # #region agent log
        log("H2", "deep_debug_artifacthub.py:main", "H2 CONFIRMED: All required fields present", {})
        # #endregion
        print("✓ H2 PASSED: index.yaml has valid structure")
    
    # Hypothesis 3: Chart URLs are accessible (Artifact Hub validates these)
    # #region agent log
    log("H3", "deep_debug_artifacthub.py:main", "Testing H3: Chart URLs are accessible", {})
    # #endregion
    all_valid, chart_urls = validate_chart_urls(index_data, repo_url, "H3")
    
    if not all_valid:
        # #region agent log
        log("H3", "deep_debug_artifacthub.py:main", "H3 REJECTED: Some chart URLs not accessible", {})
        # #endregion
        print("❌ H3 FAILED: Some chart URLs are not accessible")
        return 1
    else:
        # #region agent log
        log("H3", "deep_debug_artifacthub.py:main", "H3 CONFIRMED: All chart URLs accessible", {})
        # #endregion
        print("✓ H3 PASSED: All chart URLs are accessible")
    
    # Hypothesis 4: Check if URLs are relative vs absolute (Artifact Hub preference)
    # #region agent log
    log("H4", "deep_debug_artifacthub.py:main", "Testing H4: URL format (relative vs absolute)", {})
    # #endregion
    
    has_absolute = any(url.startswith('http') for url in chart_urls)
    has_relative = any(not url.startswith('http') for url in chart_urls)
    
    # #region agent log
    log("H4", "deep_debug_artifacthub.py:main", "H4 URL format analysis", {
        "hasAbsolute": has_absolute,
        "hasRelative": has_relative,
        "chartUrls": chart_urls
    })
    # #endregion
    
    if has_relative:
        # #region agent log
        log("H4", "deep_debug_artifacthub.py:main", "H4 WARNING: Using relative URLs", {})
        # #endregion
        print("⚠️  H4 WARNING: Using relative URLs (Artifact Hub prefers absolute)")
    else:
        # #region agent log
        log("H4", "deep_debug_artifacthub.py:main", "H4 CONFIRMED: Using absolute URLs", {})
        # #endregion
        print("✓ H4 PASSED: Using absolute URLs")
    
    # Hypothesis 5: Check if repository URL format matches Artifact Hub expectations
    # #region agent log
    log("H5", "deep_debug_artifacthub.py:main", "Testing H5: Repository URL format", {})
    # #endregion
    
    # Artifact Hub might expect the base URL without trailing slash
    repo_url_clean = repo_url.rstrip('/')
    
    # #region agent log
    log("H5", "deep_debug_artifacthub.py:main", "H5 CONFIRMED: Repository URL format", {
        "repoUrl": repo_url_clean,
        "note": "Use this exact URL in Artifact Hub"
    })
    # #endregion
    
    print(f"\n📋 Summary:")
    print(f"   Repository URL: {repo_url_clean}")
    print(f"   Index YAML: {repo_url_clean}/index.yaml")
    print(f"   Chart URLs: {chart_urls}")
    
    print(f"\n💡 If still failing, check:")
    print(f"   1. Repository visibility (must be public)")
    print(f"   2. GitHub Pages deployment status")
    print(f"   3. Exact error message from Artifact Hub")
    print(f"   4. Try without trailing slash: {repo_url_clean}")
    
    return 0

if __name__ == "__main__":
    try:
        import yaml
    except ImportError:
        print("ERROR: PyYAML not installed. Install with: pip install pyyaml")
        sys.exit(1)
    
    sys.exit(main())

