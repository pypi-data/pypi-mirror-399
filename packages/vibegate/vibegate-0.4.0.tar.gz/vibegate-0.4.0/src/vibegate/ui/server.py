"""VibeGate UI server using FastAPI."""

from __future__ import annotations

import json
import webbrowser
from pathlib import Path
from typing import Any, Dict, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles


def create_app(repo_root: Path, static_mode: bool = False) -> FastAPI:
    """Create FastAPI application for VibeGate UI.

    Args:
        repo_root: Repository root directory
        static_mode: If True, disable run triggers (read-only mode)

    Returns:
        Configured FastAPI application
    """
    app = FastAPI(title="VibeGate UI", version="0.1.0")

    # Get absolute path to static directory
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def home() -> str:
        """Home page with navigation."""
        # Load state.json if available
        state_path = repo_root / ".vibegate" / "state.json"
        last_run_info = None

        if state_path.exists():
            try:
                with state_path.open("r", encoding="utf-8") as f:
                    state_data = json.load(f)
                    last_run = state_data.get("last_run", {})
                    if last_run:
                        last_run_info = {
                            "timestamp": last_run.get("timestamp", "Unknown"),
                            "status": last_run.get("status", "Unknown"),
                            "evidence_path": last_run.get("evidence_path"),
                        }
            except (json.JSONDecodeError, OSError) as e:
                # State file missing or malformed - this is expected on first run
                logger = __import__("logging").getLogger(__name__)
                logger.debug(f"Could not load state.json: {e}")

        return _render_home(last_run_info, static_mode)

    @app.get("/plain", response_class=HTMLResponse)
    async def plain_report() -> str:
        """View plain report (user-friendly)."""
        report_path = repo_root / ".vibegate" / "plain_report.md"
        if not report_path.exists():
            return _render_missing_artifact(
                "Plain Report",
                "plain_report.md",
                "Run 'vibegate check .' to generate the plain report.",
            )

        content = report_path.read_text(encoding="utf-8")
        return _render_markdown_page("Plain Report", content, show_tech_toggle=True)

    @app.get("/report", response_class=HTMLResponse)
    async def technical_report() -> str:
        """View technical report."""
        report_path = repo_root / "artifacts" / "vibegate_report.md"
        if not report_path.exists():
            return _render_missing_artifact(
                "Technical Report",
                "artifacts/vibegate_report.md",
                "Run 'vibegate check .' to generate the technical report.",
            )

        content = report_path.read_text(encoding="utf-8")
        return _render_markdown_page(
            "Technical Report", content, show_tech_toggle=False
        )

    @app.get("/fixpack", response_class=HTMLResponse)
    async def fixpack() -> str:
        """View fixpack (interactive)."""
        fixpack_path = repo_root / "artifacts" / "fixpack.json"
        if not fixpack_path.exists():
            return _render_missing_artifact(
                "Fix Pack",
                "artifacts/fixpack.json",
                "Run 'vibegate check .' to generate the fix pack.",
            )

        try:
            with fixpack_path.open("r", encoding="utf-8") as f:
                fixpack_data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            raise HTTPException(status_code=500, detail=f"Failed to load fix pack: {e}")

        return _render_fixpack(fixpack_data)

    @app.get("/agent", response_class=HTMLResponse)
    async def agent_prompt() -> str:
        """View agent prompt (for AI assistants)."""
        agent_path = repo_root / ".vibegate" / "agent_prompt.md"
        if not agent_path.exists():
            return _render_missing_artifact(
                "Agent Prompt",
                ".vibegate/agent_prompt.md",
                "Run 'vibegate check .' to generate the agent prompt.",
            )

        content = agent_path.read_text(encoding="utf-8")
        return _render_markdown_page("Agent Prompt", content, show_tech_toggle=False)

    @app.get("/download/{filename}")
    async def download(filename: str) -> FileResponse:
        """Download artifact file.

        Only allows whitelisted files for security.
        """
        # Whitelist of downloadable files
        allowed_files = {
            "plain_report.md": repo_root / ".vibegate" / "plain_report.md",
            "agent_prompt.md": repo_root / ".vibegate" / "agent_prompt.md",
            "vibegate_report.md": repo_root / "artifacts" / "vibegate_report.md",
            "fixpack.json": repo_root / "artifacts" / "fixpack.json",
            "fixpack.md": repo_root / "artifacts" / "fixpack.md",
            "vibegate.jsonl": repo_root / "evidence" / "vibegate.jsonl",
        }

        if filename not in allowed_files:
            raise HTTPException(status_code=404, detail="File not found or not allowed")

        file_path = allowed_files[filename]
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {filename}")

        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="application/octet-stream",
        )

    return app


def _render_home(last_run_info: Optional[Dict[str, Any]], static_mode: bool) -> str:
    """Render home page HTML."""
    last_run_html = ""
    if last_run_info:
        status = last_run_info.get("status", "Unknown")
        status_color = "green" if status == "PASS" else "red"
        last_run_html = f"""
        <div class="last-run">
            <h2>Last Run</h2>
            <p><strong>Status:</strong> <span style="color: {status_color}; font-weight: bold;">{status}</span></p>
            <p><strong>Time:</strong> {last_run_info.get("timestamp", "Unknown")}</p>
        </div>
        """
    else:
        last_run_html = """
        <div class="last-run">
            <h2>No Recent Run</h2>
            <p>Run <code>vibegate check .</code> to generate artifacts.</p>
        </div>
        """

    mode_notice = ""
    if static_mode:
        mode_notice = """
        <div class="notice">
            <p><strong>Static Mode:</strong> Read-only viewer. Cannot run checks from UI.</p>
        </div>
        """

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VibeGate UI - Home</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>VibeGate UI</h1>
            <p class="subtitle">Quality Gate for Your Python Project</p>
        </header>

        {mode_notice}
        {last_run_html}

        <nav class="main-nav">
            <h2>Available Views</h2>
            <ul>
                <li>
                    <a href="/plain" class="nav-link">
                        <strong>Plain Report</strong>
                        <span>User-friendly overview of findings</span>
                    </a>
                </li>
                <li>
                    <a href="/report" class="nav-link">
                        <strong>Technical Report</strong>
                        <span>Detailed technical analysis</span>
                    </a>
                </li>
                <li>
                    <a href="/fixpack" class="nav-link">
                        <strong>Fix Pack</strong>
                        <span>Remediation tasks grouped by category</span>
                    </a>
                </li>
                <li>
                    <a href="/agent" class="nav-link">
                        <strong>Agent Prompt</strong>
                        <span>Instructions for AI coding assistants</span>
                    </a>
                </li>
            </ul>
        </nav>

        <footer>
            <p>VibeGate - Deterministic Production Readiness Gate</p>
        </footer>
    </div>
</body>
</html>
"""


def _render_missing_artifact(title: str, filename: str, instruction: str) -> str:
    """Render page for missing artifact."""
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VibeGate UI - {title}</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>{title}</h1>
            <nav class="breadcrumb">
                <a href="/">Home</a> &gt; {title}
            </nav>
        </header>

        <div class="missing-artifact">
            <h2>Artifact Not Found</h2>
            <p>The file <code>{filename}</code> was not found.</p>
            <p><strong>Next step:</strong> {instruction}</p>
        </div>

        <footer>
            <a href="/">Back to Home</a>
        </footer>
    </div>
</body>
</html>
"""


def _render_markdown_page(title: str, content: str, show_tech_toggle: bool) -> str:
    """Render markdown content as HTML page."""
    # Simple markdown rendering (headings, code blocks, lists, emphasis)
    html_content = _markdown_to_html(content)

    tech_toggle = ""
    if show_tech_toggle:
        tech_toggle = """
        <div class="toggle-container">
            <label>
                <input type="checkbox" id="tech-toggle" onchange="toggleTechnical()">
                Show Technical Details
            </label>
        </div>
        <script>
        function toggleTechnical() {
            const checkbox = document.getElementById('tech-toggle');
            const sections = document.querySelectorAll('.technical-section');
            sections.forEach(section => {
                section.style.display = checkbox.checked ? 'block' : 'none';
            });
        }
        // Hide technical sections by default
        document.addEventListener('DOMContentLoaded', function() {
            const sections = document.querySelectorAll('.technical-section');
            sections.forEach(section => {
                section.style.display = 'none';
            });
        });
        </script>
        """

    download_link = _get_download_filename(title)
    download_html = ""
    if download_link:
        download_html = (
            f'<a href="/download/{download_link}" class="download-btn">Download</a>'
        )

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VibeGate UI - {title}</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>{title}</h1>
            <nav class="breadcrumb">
                <a href="/">Home</a> &gt; {title}
            </nav>
            {download_html}
        </header>

        {tech_toggle}

        <div class="markdown-content">
            {html_content}
        </div>

        <footer>
            <a href="/">Back to Home</a>
        </footer>
    </div>
</body>
</html>
"""


def _render_fixpack(fixpack_data: Dict[str, Any]) -> str:
    """Render fix pack as interactive HTML."""
    groups = fixpack_data.get("groups", [])

    groups_html = ""
    for group in groups:
        category = group.get("category", "Unknown")
        description = group.get("description", "")
        tasks = group.get("tasks", [])

        tasks_html = ""
        for task in tasks:
            task_id = task.get("id", "")
            title = task.get("title", "")
            severity = task.get("severity", "unknown")
            remediation = task.get("remediation", "")

            # Simple markdown rendering for remediation
            remediation_html = _markdown_to_html(remediation)

            tasks_html += f"""
            <div class="task" data-severity="{severity}">
                <div class="task-header">
                    <span class="task-id">{task_id}</span>
                    <span class="severity-badge severity-{severity}">{severity}</span>
                </div>
                <h4>{title}</h4>
                <div class="task-remediation">
                    {remediation_html}
                </div>
            </div>
            """

        groups_html += f"""
        <div class="group">
            <h3>{category}</h3>
            <p class="group-description">{description}</p>
            <div class="tasks">
                {tasks_html}
            </div>
        </div>
        """

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VibeGate UI - Fix Pack</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>Fix Pack</h1>
            <nav class="breadcrumb">
                <a href="/">Home</a> &gt; Fix Pack
            </nav>
            <a href="/download/fixpack.json" class="download-btn">Download JSON</a>
        </header>

        <div class="fixpack">
            {groups_html}
        </div>

        <footer>
            <a href="/">Back to Home</a>
        </footer>
    </div>
</body>
</html>
"""


def _markdown_to_html(md: str) -> str:
    """Convert markdown to HTML (simple implementation).

    Supports:
    - Headings (# ## ###)
    - Code blocks (```)
    - Inline code (`)
    - Lists (- *)
    - Bold (**text**)
    - Italic (*text*)
    - Horizontal rules (---)
    """
    lines = md.split("\n")
    html_lines = []
    in_code_block = False
    in_list = False
    code_lang = ""

    for line in lines:
        # Code blocks
        if line.strip().startswith("```"):
            if in_code_block:
                html_lines.append("</code></pre>")
                in_code_block = False
                code_lang = ""
            else:
                code_lang = line.strip()[3:].strip()
                lang_class = f' class="language-{code_lang}"' if code_lang else ""
                html_lines.append(f"<pre{lang_class}><code>")
                in_code_block = True
            continue

        if in_code_block:
            html_lines.append(_escape_html(line))
            continue

        # Headings
        if line.startswith("# "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h1>{_inline_markdown(line[2:])}</h1>")
            continue
        if line.startswith("## "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            # Mark h2 with "Technical Details" as technical section
            heading_text = line[3:].strip()
            if "technical" in heading_text.lower():
                html_lines.append(
                    f'<h2 class="technical-section">{_inline_markdown(heading_text)}</h2>'
                )
            else:
                html_lines.append(f"<h2>{_inline_markdown(heading_text)}</h2>")
            continue
        if line.startswith("### "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h3>{_inline_markdown(line[4:])}</h3>")
            continue

        # Horizontal rule
        if line.strip() in ("---", "***", "___"):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append("<hr>")
            continue

        # Lists
        if line.strip().startswith(("- ", "* ")):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{_inline_markdown(line.strip()[2:])}</li>")
            continue

        # End list if line doesn't start with list marker
        if in_list and not line.strip().startswith(("- ", "* ")):
            html_lines.append("</ul>")
            in_list = False

        # Empty line
        if not line.strip():
            html_lines.append("<br>")
            continue

        # Regular paragraph
        html_lines.append(f"<p>{_inline_markdown(line)}</p>")

    # Close any open tags
    if in_code_block:
        html_lines.append("</code></pre>")
    if in_list:
        html_lines.append("</ul>")

    return "\n".join(html_lines)


def _inline_markdown(text: str) -> str:
    """Process inline markdown (code, bold, italic)."""
    import re

    # Inline code
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)

    # Bold
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)

    # Italic (avoid matching ** from bold)
    text = re.sub(r"(?<!\*)\*(?!\*)([^*]+)\*(?!\*)", r"<em>\1</em>", text)

    return text


def _escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _get_download_filename(title: str) -> Optional[str]:
    """Map page title to download filename."""
    mapping = {
        "Plain Report": "plain_report.md",
        "Technical Report": "vibegate_report.md",
        "Agent Prompt": "agent_prompt.md",
    }
    return mapping.get(title)


def serve(
    repo_root: Path,
    host: str = "127.0.0.1",
    port: int = 8787,
    open_browser: bool = True,
    static_mode: bool = False,
    runs_dir: Optional[Path] = None,
) -> None:
    """Start the VibeGate UI server.

    Args:
        repo_root: Repository root directory
        host: Host to bind to
        port: Port to bind to
        open_browser: Whether to open browser automatically
        static_mode: If True, disable run triggers (read-only mode)
        runs_dir: Directory for storing UI run sessions (unused in static mode)

    Raises:
        ValueError: If repo_root is invalid
    """
    if not repo_root.exists():
        raise ValueError(f"Repository root does not exist: {repo_root}")

    if not repo_root.is_dir():
        raise ValueError(f"Repository root is not a directory: {repo_root}")

    app = create_app(repo_root, static_mode)

    # Open browser after server starts
    if open_browser:
        url = f"http://{host}:{port}"

        def open_browser_callback() -> None:
            webbrowser.open(url)

        # Schedule browser open after a brief delay
        import threading

        threading.Timer(1.0, open_browser_callback).start()

    # Run server
    uvicorn.run(app, host=host, port=port, log_level="info")
