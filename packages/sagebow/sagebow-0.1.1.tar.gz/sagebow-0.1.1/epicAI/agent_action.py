"""
Agent Action Module - Minimal Execution Layer
This module handles only code execution. All AI logic is on the Next.js backend.
"""
from __future__ import annotations
import os
import sys
import io
import traceback
import base64
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, List, Callable, Tuple, Any, Optional
import re
try:
    from IPython.utils.capture import capture_output
    from IPython import get_ipython
except ImportError:
    capture_output = None
    get_ipython = None
load_dotenv = None  # kept for backward compatibility markers
class AgentActionProcessor:
    def __init__(self, shared_namespace: Dict[str, Any]):
        self.shared_ns = shared_namespace
        self._cancel_requested = False
    def execute_code_with_visuals(self, code: str) -> Dict[str, Any]:
        try:
            if not code.strip():
                return {
                    "success": True,
                    "html_output": '<pre style="margin:0; color:#666; font-style:italic;">No code to execute</pre>',
                    "had_error": False,
                    "output_text": ""
                }
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            visual_html = ""
            try:
                sys.stdout = stdout_capture
                sys.stderr = stderr_capture
                processed_code = self._process_pip_commands(code)
                exec(compile(processed_code, "<cell_execution>", "exec"), self.shared_ns, self.shared_ns)
                visual_html = self._capture_matplotlib_figures()
            except Exception as e:
                stderr_capture.write(f"Error: {e}\n")
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
            stdout_text = stdout_capture.getvalue()
            stderr_text = stderr_capture.getvalue()
            html_output = self._build_html_output(stdout_text, stderr_text, visual_html)
            combined_text = (stdout_text + ("\n" + stderr_text if stderr_text else ""))
            if not combined_text.strip():
                combined_text = "[no output]"
            return {
                "success": True,
                "html_output": html_output,
                "had_error": bool(stderr_text.strip()),
                "output_text": combined_text
            }
        except Exception as e:
            return {
                "success": False,
                "html_output": f'<pre style="margin:0; color:#d32f2f;">Execution error: {e}</pre>',
                "had_error": True,
                "output_text": f"Error: {e}"
            }
    def _process_pip_commands(self, src: str) -> str:
        """Handle pip install commands."""
        lines = src.splitlines()
        remaining = []
        def _run_install(arg_tail: str):
            arg_tail = (arg_tail or "").strip()
            if not arg_tail:
                return
            try:
                if get_ipython:
                    ip = get_ipython()
                    if ip is not None:
                        ip.run_line_magic('pip', f"install {arg_tail}")
                        return
            except Exception:
                pass
            try:
                import subprocess
                import shlex
                cmd = [sys.executable, '-m', 'pip', 'install'] + shlex.split(arg_tail)
                subprocess.run(cmd, check=True, capture_output=True, text=True)
            except Exception:
                pass
        for line in lines:
            s = line.strip()
            handled = False
            if s.startswith('%pip') and 'install' in s:
                rest = s[len('%pip'):].strip()
                if rest.startswith('install'):
                    _run_install(rest[len('install'):].strip())
                    handled = True
            elif s.startswith('!pip') and 'install' in s:
                rest = s[len('!pip'):].strip()
                if rest.startswith('install'):
                    _run_install(rest[len('install'):].strip())
                    handled = True
            elif re.match(r'^(pip\s+install\b)', s):
                _run_install(re.sub(r'^pip\s+install\s+', '', s))
                handled = True
            elif re.match(r'^python(3)?\s+-m\s+pip\s+install\b', s):
                m = re.search(r'\binstall\b(.*)$', s)
                if m:
                    _run_install(m.group(1).strip())
                    handled = True
            if not handled:
                remaining.append(line)
        return "\n".join(remaining)
    def _capture_matplotlib_figures(self) -> str:
        """Capture matplotlib figures."""
        visual_html = ""
        try:
            import sys as _sys
            import matplotlib
            if 'matplotlib.pyplot' not in _sys.modules:
                try:
                    matplotlib.use('Agg')  # safe non-interactive backend
                except Exception:
                    pass
            import matplotlib.pyplot as plt
            figures = [plt.figure(i) for i in plt.get_fignums()]
            if figures:
                for fig in figures:
                    img_buffer = io.BytesIO()
                    fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=100)
                    img_buffer.seek(0)
                    img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
                    visual_html += f'<img src="data:image/png;base64,{img_base64}" style="max-width:100%; height:auto; margin:10px 0;"/>'
                    plt.close(fig)
        except ImportError:
            pass
        return visual_html
    def _build_html_output(self, stdout_text: str, stderr_text: str, visual_html: str) -> str:
        """Build HTML output."""
        html_output = ""
        if stdout_text:
            html_output += f'<pre style="margin:0; color:#333;">{stdout_text}</pre>'
        if visual_html:
            html_output += visual_html
        if stderr_text:
            html_output += f'<pre style="margin:0; color:#d32f2f;">{stderr_text}</pre>'
        if not html_output:
            html_output = '<pre style="margin:0; color:#666; font-style:italic;">Code executed successfully (no output)</pre>'
        return html_output
def create_agent_processor(shared_namespace: Dict[str, Any]) -> AgentActionProcessor:
    """Create a new AgentActionProcessor instance."""
    return AgentActionProcessor(shared_namespace)
