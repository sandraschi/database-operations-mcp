# 🚀 MCP Server in 30 Minutes: From Zero to Hero

> **⚠️ OUTDATED**: This document contains references to DXT packaging which has been replaced by MCPB packaging. The current MCPB packaging system is different from the DXT system described here.

## 📋 Overview

> **⚠️ OUTDATED**: This guide describes DXT packaging which has been replaced by MCPB packaging.

### 🎯 Key Objectives
- Build a fully functional MCP server
- Implement comprehensive testing
- Package for distribution
- Release on GitHub
- Promote to the community

## ⏱️ Timeline Breakdown

### 0:00-5:00 - Setup & Planning
- [ ] **Minute 0-1**: Clone the template
  ```bash
  git clone https://github.com/yourorg/mcp-server-template notepadpp-mcp
  cd notepadpp-mcp
  ```
- [ ] **Minute 1-3**: Update project metadata
  - `pyproject.toml` - Update name, version, description
  - `README.md` - Update project name and description
  - `LICENSE` - Verify/update license

- [ ] **Minute 3-5**: Research Notepad++
  - Document key features to expose via MCP
  - Note any CLI commands or automation interfaces
  - Identify potential challenges (elevation, paths, etc.)

### 5:15-15:00 - Core Implementation
- [ ] **Minute 5-7**: Define your tools in `src/notepadpp_mcp/tools/`
  ```python
  # Example: notepad_tools.py
  from mcp.server import tool
  
  @tool
  def open_file(file_path: str) -> str:
      """Open a file in Notepad++"""
      import subprocess
      subprocess.run([r'C:\Program Files\Notepad++\notepad++.exe', file_path])
      return f"Opened {file_path} in Notepad++"
  ```

- [ ] **Minute 7-12**: Implement 3-5 core tools
  - File operations (open, save, close)
  - Search/replace
  - Plugin management
  - Session handling

- [ ] **Minute 12-15**: Add error handling and logging
  ```python
  def safe_notepad_call(*args):
      try:
          subprocess.run(args, check=True, capture_output=True, text=True)
      except subprocess.CalledProcessError as e:
          logger.error(f"Notepad++ command failed: {e.stderr}")
          raise
  ```

### 15:00-20:00 - Testing & Packaging
- [ ] **Minute 15-17**: Write basic tests
  ```python
  def test_open_file():
      result = open_file("test.txt")
      assert "Opened test.txt" in result
  ```

- [ ] **Minute 17-19**: Build DXT package
  ```powershell
  .\build.ps1
  ```
  
- [ ] **Minute 19-20**: Verify package
  - Check `dist/` for the generated `.dxt` file
  - Test installation locally

### 20:00-25:00 - GitHub Release
- [ ] **Minute 20-21**: Commit changes
  ```bash
  git add .
  git commit -m "Initial Notepad++ MCP implementation"
  git tag v1.0.0
  git push origin main --tags
  ```

- [ ] **Minute 21-23**: Create GitHub Release
  - Go to GitHub → Releases → Draft New Release
  - Tag version: v1.0.0
  - Upload `.dxt` file from `dist/`
  - Auto-generate release notes

- [ ] **Minute 23-25**: Verify release
  - Check GitHub Actions build
  - Verify package download

### 25:00-30:00 - Marketing & Community
- [ ] **Minute 25-27**: Write Reddit post
  ```markdown
  ## 🚀 Notepad++ MCP Server v1.0 Released!
  
  Just shipped a new MCP server for Notepad++! Now you can control Notepad++ programmatically through MCP.
  
  ### Features:
  - Open/edit/save files
  - Search and replace
  - Plugin management
  - Session handling
  
  Get it here: [GitHub Release](your-github-link)
  ```

- [ ] **Minute 27-29**: Post to relevant subreddits
  - r/Notepad++
  r/Python
  r/commandline
  
- [ ] **Minute 29-30**: Celebrate! 🎉
  - Have a sip of your coffee
  - Watch the stars roll in
  - Prepare for issues/PRs

## 🧰 Pro Tips for 30-Minute Success

1. **Template First**
   - Start with the `mcp-server-template`
   - Pre-configure CI/CD with GitHub Actions
   - Include essential testing framework

2. **Minimal Viable Product**
   - Focus on 3-5 core tools
   - Implement the 80% use case first
   - Use `@tool` decorator for all endpoints
   - Add comprehensive error handling

3. **Automation is Key**
   - One-command build with `build.ps1`
   - Automated testing with pytest
   - GitHub Actions for CI/CD
   - Semantic versioning with tags

4. **Documentation as Code**
   - Use Google-style docstrings
   - Keep README.md updated
   - Include usage examples
   - Document environment variables

## 🎯 First-Run Success Blueprint

### 1. Pre-Flight Validation Suite

```python
# tests/test_first_run.py
import pytest
from fastapi.testclient import TestClient
from your_mcp_server import app
from pathlib import Path
import tempfile

@pytest.fixture
def client():
    return TestClient(app)

def test_health_check(client):
    """Verify the server starts and responds to health checks"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_tool_registration(client):
    """Verify all tools are properly registered"""
    response = client.get("/.well-known/tools")
    assert response.status_code == 200
    tools = response.json()
    assert len(tools) >= 1  # At least one tool should be registered

def test_tool_execution(client):
    """Test executing a tool with proper parameters"""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        test_file = tmp.name
    
    try:
        response = client.post(
            "/execute_tool",
            json={
                "tool": "open_file",
                "parameters": {"file_path": test_file}
            }
        )
        assert response.status_code == 200
        assert "success" in response.json()
    finally:
        Path(test_file).unlink(missing_ok=True)

if __name__ == "__main__":
    pytest.main(["-v", "test_first_run.py"])
```

### 2. Environment Validation Script

```python
# scripts/validate_environment.py
import sys
import platform
import subprocess
from pathlib import Path

def check_python_version():
    """Verify Python version meets requirements"""
    required = (3, 8)
    current = sys.version_info
    if current < required:
        print(f"❌ Python {required[0]}.{required[1]}+ required")
        return False
    print(f"✅ Python {current.major}.{current.minor}.{current.micro}")
    return True

def check_dependencies():
    """Check required dependencies are installed"""
    required = ['fastapi', 'uvicorn', 'pydantic']
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg)
            print(f"✅ {pkg} is installed")
        except ImportError:
            missing.append(pkg)
            print(f"❌ {pkg} is missing")
    
    return len(missing) == 0

def main():
    print("🔍 Validating environment...\n")
    
    checks = [
        ("Python Version", check_python_version()),
        ("Dependencies", check_dependencies())
    ]
    
    if all(passed for _, passed in checks):
        print("\n🎉 Environment validation passed!")
        return 0
    else:
        print("\n❌ Environment validation failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

### 2. Common First-Run Issues & Solutions

#### 2.1 Path Issues
```python
# Always use pathlib for cross-platform paths
from pathlib import Path

def get_config_path() -> Path:
    """Get platform-specific config path"""
    if platform.system() == "Windows":
        return Path.home() / "AppData" / "Local" / "your-app"
    elif platform.system() == "Darwin":
        return Path.home() / "Library" / "Application Support" / "your-app"
    else:  # Linux and others
        return Path.home() / ".config" / "your-app"

# Example usage
config_path = get_config_path() / "config.json"
config_path.parent.mkdir(parents=True, exist_ok=True)
```

#### 2.2 Permission Problems
```python
import os
import sys
import ctypes

def ensure_admin():
    """Ensure script runs with admin privileges"""
    if os.name == 'nt':
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    else:
        return os.geteuid() == 0

if not ensure_admin():
    print("This script requires administrator privileges.")
    if os.name == 'nt':
        # Re-run with admin rights on Windows
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit(1)
```

#### 2.3 Port Conflicts
```python
def find_available_port(start_port: int = 8000, max_attempts: int = 100) -> int:
    """Find an available port starting from start_port"""
    import socket
    from contextlib import closing
    
    for port in range(start_port, start_port + max_attempts):
        try:
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"No available ports in range {start_port}-{start_port + max_attempts}")

# In your FastAPI app:
PORT = int(os.getenv("PORT", find_available_port(37485)))  # Start from a less common port
```

## 🚀 Advanced: Smart Port Management

### 1. Port Management Class

```python
# src/your_mcp_server/port_manager.py
import socket
import os
from contextlib import closing
from typing import Optional, List
import random

class PortManager:
    """Advanced port management with fallback and reservation"""
    
    COMMON_PORTS = [8000, 3000, 5000, 8080, 8888, 9000]
    
    def __init__(self, preferred_ports: Optional[List[int]] = None):
        self.preferred_ports = preferred_ports or self.COMMON_PORTS
        self._reserved_ports = set()
    
    def is_port_available(self, port: int) -> bool:
        """Check if a port is available"""
        if port in self._reserved_ports:
            return False
            
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            try:
                sock.bind(('', port))
                return True
            except OSError:
                return False
    
    def reserve_port(self, port: int) -> bool:
        """Reserve a port to prevent conflicts"""
        if self.is_port_available(port):
            self._reserved_ports.add(port)
            return True
        return False
    
    def find_available_port(self, start_port: Optional[int] = None, max_attempts: int = 100) -> int:
        """Find an available port with smart selection"""
        # Try environment variable first
        env_port = os.getenv("PORT")
        if env_port and env_port.isdigit():
            port = int(env_port)
            if self.is_port_available(port):
                self.reserve_port(port)
                return port
        
        # Try preferred ports
        for port in self.preferred_ports:
            if self.is_port_available(port):
                self.reserve_port(port)
                return port
        
        # Try random ports in a range
        start = start_port or random.randint(30000, 60000)
        for port in range(start, start + max_attempts):
            if self.is_port_available(port):
                self.reserve_port(port)
                return port
        
        raise RuntimeError(f"No available ports found after {max_attempts} attempts")

# Usage example:
if __name__ == "__main__":
    pm = PortManager()
    port = pm.find_available_port()
    print(f"Using port: {port}")
```

### 2. Integration with FastAPI

```python
# src/your_mcp_server/main.py
from fastapi import FastAPI
from .port_manager import PortManager
import uvicorn
import os

app = FastAPI(title="Your MCP Server")

# Initialize port manager
port_manager = PortManager()
port = port_manager.find_available_port()

@app.get("/health")
async def health_check():
    return {"status": "ok", "port": port}

def start_server(host: str = "0.0.0.0", port: int = None):
    """Start the server with the specified host and port"""
    port = port or port_manager.find_available_port()
    print(f"🚀 Starting server on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_server()
```

## 🧪 The "It Works on My Machine" Kit

### 1. Development Environment Setup

```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Start development server
uvicorn your_mcp_server.main:app --reload
```

### 2. Production Build Script

```powershell
# build.ps1
param(
    [string]$Version = "0.1.0",
    [string]$OutputDir = "dist"
)

# Ensure output directory exists
if (-not (Test-Path -Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

# Clean previous builds
Remove-Item "$OutputDir/*" -Recurse -Force -ErrorAction SilentlyContinue

# Install build dependencies
pip install --upgrade pip wheel setuptools build

# Build package
python -m build --outdir $OutputDir

# Build DXT package
dxt pack --output "$OutputDir/your_mcp_server-$Version.dxt"

Write-Host "✅ Build complete!" -ForegroundColor Green
Write-Host "📦 Package: $OutputDir/your_mcp_server-$Version.dxt"
```

### 3. GitHub Actions Workflow

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  release:
    types: [created]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]
    
    - name: Run tests
      run: |
        pytest tests/ -v
  
  deploy:
    needs: test
    if: github.event_name == 'push' && contains(github.ref, 'refs/tags/')
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build
    
    - name: Build package
      run: python -m build --outdir dist/
    
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
    
    - name: Create GitHub Release
      uses: softprops/action-gh-release@v1
      with:
        files: |
          dist/*.whl
          dist/*.tar.gz
          dist/*.dxt
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
pytest -v
```

### 4. Client Integration Test
```python
def test_client_integration():
    """Test the full client-server integration"""
    with start_server_in_background():
        client = MCPClient()
        result = client.execute("open_file", {"file_path": "test.txt"})
        assert "success" in result
```

## 🤔 What to Do When Time's Up?

1. **If Done**: Ship it! Don't gold-plate.
2. **If Not Done**: 
   - Ship what you have as v0.1.0
   - Create GitHub issues for next steps
   - Plan another 30-minute session

## 📈 Next Steps

1. Monitor GitHub issues
2. Engage with community feedback
3. Plan the next 30-minute improvement sprint

---

*Challenge yourself to build something amazing in just 30 minutes!* 🚀
