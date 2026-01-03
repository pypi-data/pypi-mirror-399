from __future__ import annotations
import io
import sys
import traceback
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, List, Callable, Tuple, Any, Optional
import os
import html as _html
import threading
import time
import re
import requests
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML, Javascript, FileLink
from IPython import get_ipython
from IPython.utils.capture import capture_output
from .auth import get_current_user, logout, get_auth_manager
import subprocess
import shlex
from .agent_action import create_agent_processor
import types
class MiniCell:
    def __init__(self, idx: int, shared_ns: Dict[str, object], *, on_add_below, on_delete, parent=None):
        self.idx = idx
        self.shared_ns = shared_ns
        self._on_add_below = on_add_below
        self._on_delete = on_delete
        self.parent = parent
        self._suppress_auto_add = False
        self.last_output_text: str = ''
        self._last_had_exception: bool = False
        self._agent_processor = None
        self._last_agent_comment: str = ''
        self.code = widgets.Textarea(value='', placeholder='Write Python Manually', layout=widgets.Layout(width='100%', height='84px', margin='0'), style={'description_width': '0'}, continuous_update=True)
        self.code.add_class('epic-code-editor')
        self.code.add_class('epic-main-editor')
        self._min_code_height = 80
        self._max_code_height = 5000
        self._line_px = 18
        self.code.layout.height = '84px'
        self.play_btn = widgets.Button(icon='play', tooltip='Run this cell', button_style='', layout=widgets.Layout(width='28px', height='28px'))
        self.ai_btn = widgets.Button(
            description='Mode',
            tooltip='Switch between manual programming and autonomous agents',
            layout=widgets.Layout(width='auto', height='28px'),
            button_style=''
        )
        self._agents_text = widgets.Textarea(placeholder='Ask Agents To Complete A Project', layout=widgets.Layout(width='100%', height='84px', margin='0'), style={'description_width': '0'}, continuous_update=True)
        self._agents_text.add_class('epic-code-editor')
        self._agents_text.add_class('epic-agents-prompt')
        self._agents_send_btn = widgets.Button(description='Send', icon='', tooltip='Send', layout=widgets.Layout(width='96px', height='32px'), button_style='')
        try:
            self._agents_send_btn.remove_class('epic-send-circle')
        except Exception:
            pass
        self._agents_cancel_btn = widgets.Button(description='Cancel', icon='', tooltip='Cancel current AI run', layout=widgets.Layout(width='96px', height='32px', display='none'), button_style='')
        self._agents_status = widgets.HTML(value='', layout=widgets.Layout(margin='8px 0 0 0', padding='0', display='none', justify_content='flex-start', width='100%'))
        try:
            self._agents_text.layout.width = 'auto'
            self._agents_text.layout.flex = '1 1 auto'
        except Exception:
            pass
        self._agents_loading = widgets.HTML(value=(
            "<div class='epic-dots-loading' style='display:flex;align-items:center;height:32px'>"
            "<span style='font-size:12px;color:#9ca3af;margin-right:8px'>Thinking</span>"
            "<span class='dot'></span><span class='dot'></span><span class='dot'></span>"
            "<style>"
            ".epic-dots-loading .dot{width:6px;height:6px;background:#666;border-radius:50%;display:inline-block;margin-right:4px;animation:epicPulse 1.2s infinite ease-in-out;}"
            ".epic-dots-loading .dot:nth-child(2){animation-delay:0.2s}"
            ".epic-dots-loading .dot:nth-child(3){animation-delay:0.4s}"
            "@keyframes epicPulse{0%,80%,100%{opacity:.3;transform:translateY(0)}40%{opacity:1;transform:translateY(-2px)}}"
            "</style>"
            "</div>"
        ), layout=widgets.Layout(display='none'))
        self._agents_compact_css = widgets.HTML(
            value=(
                "<style>"
                ".epic-agents-prompt textarea{"
                "padding:8px 10px !important;"
                "white-space:pre-wrap !important;"
                "overflow-wrap:anywhere !important;"
                "word-break:break-word !important;"
                "overflow-x:hidden !important;"
                "}"
                ".epic-main-editor textarea{"
                "padding:10px 12px !important;"
                "white-space:pre-wrap !important;"
                "overflow-wrap:anywhere !important;"
                "word-break:break-word !important;"
                "overflow-x:hidden !important;"
                "}"
                "</style>"
            )
        )
        agents_buttons = widgets.HBox([self._agents_loading, self._agents_send_btn, self._agents_cancel_btn], layout=widgets.Layout(justify_content='flex-start', align_items='center', gap='8px', width='auto', margin='4px 0 0 0'))
        self.agents_ui = widgets.VBox([self._agents_compact_css, self._agents_text, agents_buttons, self._agents_status], layout=widgets.Layout(display='none', padding='0', margin='0', width='100%'))
        self._last_autosize_ts_code = 0.0
        self._last_autosize_ts_agents = 0.0
        def _autosize_textarea(_ta: widgets.Textarea, *, min_px: int, max_px: int, line_px: int, pad_px: int = 28):
            try:
                txt = (_ta.value or '')
                lines = txt.splitlines() or ['']
                target = min(max_px, max(min_px, (len(lines) * line_px) + pad_px))
                h = f'{int(target)}px'
                if getattr(_ta.layout, 'height', None) != h:
                    _ta.layout.height = h
            except Exception:
                pass
        def _on_code_change(_change=None):
            _autosize_textarea(self.code, min_px=84, max_px=self._max_code_height, line_px=self._line_px, pad_px=32)
        def _on_agents_change(_change=None):
            _autosize_textarea(self._agents_text, min_px=84, max_px=2000, line_px=self._line_px, pad_px=28)
        try:
            self.code.observe(_on_code_change, names='value')
        except Exception:
            pass
        try:
            self._agents_text.observe(_on_agents_change, names='value')
        except Exception:
            pass
        _on_code_change()
        _on_agents_change()
        def _toggle_agents_panel(_btn=None):
            try:
                if self.editor_container.children == (self.code,):
                    self._agents_text.value = ''
                    self.editor_container.children = (self.agents_ui,)
                    self.agents_ui.layout.display = 'block'
                    try:
                        if hasattr(self, 'ai_hint_overlay'):
                            self.ai_hint_overlay.layout.display = 'none'
                    except Exception:
                        pass
                else:
                    self.editor_container.children = (self.code,)
                    self.agents_ui.layout.display = 'none'
                    try:
                        if hasattr(self, 'ai_hint_overlay') and (not (self.code.value or '').strip()):
                            self.ai_hint_overlay.layout.display = 'flex'
                    except Exception:
                        pass
            except Exception:
                pass
        self._ai_processing = False
        self._ai_cancel_requested = False
        def on_send_click(_btn=None):
            try:
                task = (self._agents_text.value or '').strip()
                if not task:
                    return
                try:
                    if self.parent is not None:
                        try:
                            _suppress = bool(getattr(self.parent, '_suppress_unfinished_reset', False))
                        except Exception:
                            _suppress = False
                        try:
                            if not _suppress and bool(getattr(self.parent, '_project_completed_flag', False)):
                                setattr(self.parent, '_original_goal_prompt', task)
                                setattr(self.parent, '_project_completed_flag', False)
                        except Exception:
                            pass
                        try:
                            existing_goal = getattr(self.parent, '_original_goal_prompt', '') or ''
                        except Exception:
                            existing_goal = ''
                        if not existing_goal:
                            try:
                                setattr(self.parent, '_original_goal_prompt', task)
                            except Exception:
                                pass
                        try:
                            setattr(self.parent, '_current_prompt', task)
                        except Exception:
                            pass
                except Exception:
                    pass
                try:
                    if self.parent is not None:
                        suppress = bool(getattr(self.parent, '_suppress_unfinished_reset', False))
                        if not suppress:
                            setattr(self.parent, '_master_unfinished_count', 0)
                        setattr(self.parent, '_suppress_unfinished_reset', False)
                except Exception:
                    pass
                self._ai_processing = True
                self._ai_cancel_requested = False
                try:
                    if self.parent is not None:
                        if getattr(self.parent, '_hil_cancelled', False):
                            try:
                                setattr(self.parent, '_hil_cancelled', False)
                            except Exception:
                                pass
                            try:
                                setattr(self.parent, '_hil_active', True)
                            except Exception:
                                pass
                            try:
                                if hasattr(self.parent, '_update_hil_bars'):
                                    self.parent._update_hil_bars()
                            except Exception:
                                pass
                        else:
                            setattr(self.parent, '_hil_active', True)
                            if hasattr(self.parent, '_update_hil_bars'):
                                self.parent._update_hil_bars()
                        try:
                            self._update_send_button_mode()
                        except Exception:
                            pass
                except Exception:
                    pass
                try:
                    self._agents_send_btn.disabled = True
                except Exception:
                    pass
                try:
                    self._agents_status.value = ''
                    self._agents_status.layout.display = 'none'
                except Exception:
                    pass
                def _worker():
                    txt = ''
                    try:
                        try:
                            if self.parent is not None and getattr(self.parent, '_hil_cancelled', False):
                                self._ai_cancel_requested = True
                        except Exception:
                            pass
                        if self._ai_cancel_requested:
                            txt = '# Request cancelled by user'
                        else:
                            base = get_auth_manager().api_base_url.rstrip('/')
                            try:
                                _am = get_auth_manager()
                                _tok = _am.get_stored_token()
                            except Exception:
                                _tok = None
                            url = f'{base}/api/ai'
                            headers = {"User-Agent": "sagebow-client/0.1"}
                            if _tok:
                                headers['Authorization'] = f'Bearer {_tok}'
                            try:
                                selected_files = list(self.selected_context_files or [])
                            except Exception:
                                selected_files = []
                            cwd = os.getcwd()
                            rel_paths = []
                            base_names = []
                            dir_hints = set()
                            for fname in selected_files:
                                try:
                                    abs_path = os.path.abspath(fname)
                                    bn = os.path.basename(abs_path)
                                    base_names.append(bn)
                                    try:
                                        rel = os.path.relpath(abs_path, cwd)
                                    except Exception:
                                        rel = bn
                                    if rel.startswith('..'):
                                        rel = bn
                                    rel_paths.append(rel)
                                    d = os.path.dirname(rel) if rel and rel != bn else ''
                                    if d:
                                        dir_hints.add(d)
                                except Exception:
                                    pass
                            payload = {
                                'prompt': task,
                                'context_files': base_names,
                                'context_paths': rel_paths,
                                'context_dirs': list(dir_hints),
                                'cwd': cwd,
                                'api_token': _tok,
                            }
                            try:
                                comments_block = self._gather_agent_comment_context()
                                if comments_block:
                                    payload['previous_explanation'] = comments_block[:8000]
                            except Exception:
                                pass
                            try:
                                schema = self._build_import_schema()
                                if schema:
                                    payload['import_schema'] = schema
                            except Exception:
                                pass
                            try:
                                recent_inputs = []
                                recent_outputs = []
                                if self.parent and hasattr(self.parent, 'cells'):
                                    cells_list = list(self.parent.cells)
                                    try:
                                        cur_index = cells_list.index(self)
                                        subset = cells_list[:cur_index]
                                    except Exception:
                                        subset = cells_list
                                    tail = subset[-4:]
                                    for c in tail:
                                        try:
                                            code_txt = (getattr(c, 'code', None).value if getattr(c, 'code', None) else '') or ''
                                        except Exception:
                                            code_txt = ''
                                        try:
                                            out_txt = getattr(c, 'last_output_text', '') or ''
                                        except Exception:
                                            out_txt = ''
                                        if code_txt:
                                            recent_inputs.append(code_txt[:2000])
                                        else:
                                            recent_inputs.append('')
                                        if out_txt:
                                            recent_outputs.append(out_txt[:2000])
                                        else:
                                            recent_outputs.append('')
                                if recent_inputs:
                                    payload['recent_inputs'] = recent_inputs
                                if recent_outputs:
                                    payload['recent_outputs'] = recent_outputs
                            except Exception:
                                pass
                            last_exc = None
                            for attempt in range(3):
                                try:
                                    resp = requests.post(url, json=payload, headers=headers, timeout=60)
                                    break
                                except Exception as e:
                                    last_exc = e
                                    time.sleep(min(2 ** attempt, 4))
                            else:
                                raise last_exc if last_exc else RuntimeError('Request failed')
                            if self._ai_cancel_requested:
                                txt = '# Request cancelled by user'
                            elif resp.status_code == 200:
                                data = resp.json()
                                txt = data.get('text') or data.get('output') or ''
                                if not isinstance(txt, str):
                                    txt = str(txt)
                            else:
                                txt = f'# Error {resp.status_code}: {resp.text}'
                    except Exception as e:
                        if self._ai_cancel_requested:
                            txt = '# Request cancelled by user'
                        else:
                            txt = f'# Request failed: {e}'
                    finally:
                        self._ai_processing = False
                        self._ai_cancel_requested = False
                        try:
                            self._update_send_button_mode()
                        except Exception:
                            pass
                        try:
                            self.code.value = txt or '# No response received'
                            self.editor_container.children = (self.code,)
                            self.agents_ui.layout.display = 'none'
                            self._agents_send_btn.disabled = False
                            self._agents_text.disabled = False
                            self._agents_text.value = ''
                            self._agents_status.layout.display = 'none'
                            if txt and (not txt.strip().startswith('#')):
                                try:
                                    try:
                                        _nb_allow = True
                                        if self.parent is not None:
                                            _nb_allow = bool(getattr(self.parent, 'agent_comments_enabled', True))
                                        if _nb_allow:
                                            self._force_show_explain_once = True
                                    except Exception:
                                        pass
                                    self._on_run(None)
                                except Exception as e:
                                    print(f'Auto-execution failed: {e}')
                        except Exception:
                            pass
                        try:
                            if self.parent is not None and (not getattr(self.parent, '_hil_cancelled', False)):
                                pass
                        except Exception:
                            pass
                threading.Thread(target=_worker, daemon=True).start()
            except Exception:
                pass
        def _on_main_send_button(_b=None):
            try:
                active = False
                try:
                    if self.parent is not None:
                        active = bool(getattr(self.parent, '_hil_active', False))
                except Exception:
                    active = False
                if active:
                    try:
                        if self.parent is not None and hasattr(self.parent, 'cancel_hil'):
                            self.parent.cancel_hil()
                    except Exception:
                        pass
                else:
                    on_send_click(_b)
            except Exception:
                pass
        self._agents_send_btn.on_click(_on_main_send_button)
        def _on_ai_bar_send_button(_b=None):
            try:
                active = False
                try:
                    if self.parent is not None:
                        active = bool(getattr(self.parent, '_hil_active', False))
                except Exception:
                    active = False
                if active:
                    try:
                        if self.parent is not None and hasattr(self.parent, 'cancel_hil'):
                            self.parent.cancel_hil()
                    except Exception:
                        pass
                else:
                    self._on_ai_send(_b)
            except Exception:
                pass
        self._agents_do_send = on_send_click
        def _update_send_button_mode():
            try:
                active = False
                try:
                    if self.parent is not None:
                        active = bool(getattr(self.parent, '_hil_active', False))
                except Exception:
                    active = False
                try:
                    if bool(getattr(self, '_ai_processing', False)):
                        active = True
                except Exception:
                    pass
                if active:
                    try:
                        self.hil_bar.layout.display = 'none'
                    except Exception:
                        pass
                    try:
                        self.controls.layout.display = 'none'
                    except Exception:
                        pass
                    try:
                        self.ai_input.layout.display = 'none'
                    except Exception:
                        pass
                    try:
                        self.ai_status.layout.display = 'none'
                    except Exception:
                        pass
                    try:
                        self._agents_text.layout.display = 'none'
                    except Exception:
                        pass
                    try:
                        self._agents_status.layout.display = 'none'
                    except Exception:
                        pass
                    try:
                        self._agents_send_btn.layout.display = 'none'
                    except Exception:
                        pass
                    try:
                        self._agents_cancel_btn.layout.display = 'inline-flex'
                    except Exception:
                        pass
                    try:
                        self.ai_cancel_btn.layout.display = 'inline-flex'
                    except Exception:
                        pass
                    try:
                        self._agents_loading.layout.display = 'inline-flex'
                    except Exception:
                        pass
                    try:
                        self.ai_loading.layout.display = 'inline-flex'
                    except Exception:
                        pass
                else:
                    try:
                        self.hil_bar.layout.display = 'none'
                    except Exception:
                        pass
                    try:
                        self.controls.layout.display = 'flex'
                    except Exception:
                        pass
                    try:
                        self.ai_input.layout.display = 'block'
                    except Exception:
                        pass
                    try:
                        self.ai_status.layout.display = ''
                    except Exception:
                        pass
                    try:
                        self._agents_text.layout.display = ''
                        self._agents_text.layout.width = '100%'
                        self._agents_text.layout.height = '80px'
                    except Exception:
                        pass
                    try:
                        self._agents_send_btn.layout.display = 'inline-flex'
                    except Exception:
                        pass
                    try:
                        self._agents_cancel_btn.layout.display = 'none'
                    except Exception:
                        pass
                    try:
                        self.ai_cancel_btn.layout.display = 'none'
                    except Exception:
                        pass
                    try:
                        self._agents_loading.layout.display = 'none'
                    except Exception:
                        pass
                    try:
                        self.ai_loading.layout.display = 'none'
                    except Exception:
                        pass
            except Exception:
                pass
        self._update_send_button_mode = _update_send_button_mode
        self.context_btn = widgets.Button(description='Context', tooltip='Select files to reference in AI context', layout=widgets.Layout(width='auto', height='28px'), button_style='')
        self.context_btn.add_class('epic-ghost')
        try:
            self.context_btn.layout.padding = '0 8px'
            self.context_btn.layout.min_width = '64px'
            self.context_btn.layout.overflow = 'visible'
        except Exception:
            pass
        self.selected_context_files: List[str] = []
        self._context_checkboxes: List[widgets.Checkbox] = []
        self.context_menu = widgets.VBox([], layout=widgets.Layout(display='none', width='260px'))
        self.context_menu.add_class('epic-export-dropdown')
        self._ctx_apply_btn = widgets.Button(description='Apply', button_style='info', layout=widgets.Layout(width='80px', height='24px'))
        self._ctx_cancel_btn = widgets.Button(description='Close', button_style='', layout=widgets.Layout(width='80px', height='24px'))
        self._ctx_footer = widgets.HBox([self._ctx_apply_btn, self._ctx_cancel_btn], layout=widgets.Layout(justify_content='space-between'))
        self._ctx_list_box = widgets.VBox([], layout=widgets.Layout(max_height='240px', overflow_y='auto'))
        self.context_menu.children = (self._ctx_list_box, self._ctx_footer)
        try:
            prev_cell = None
            if self.parent and hasattr(self.parent, 'cells'):
                if isinstance(self.idx, int) and self.idx > 0 and (len(self.parent.cells) >= 1):
                    try:
                        prev_cell = self.parent.cells[self.idx - 1]
                    except Exception:
                        prev_cell = self.parent.cells[-1]
                elif len(self.parent.cells) >= 1:
                    prev_cell = self.parent.cells[-1]
                if prev_cell and hasattr(prev_cell, 'selected_context_files'):
                    self.selected_context_files = list(prev_cell.selected_context_files)
                elif hasattr(self.parent, 'default_selected_context_files'):
                    self.selected_context_files = list(getattr(self.parent, 'default_selected_context_files') or [])
            if self.selected_context_files:
                self.context_btn.description = f'Context ({len(self.selected_context_files)})'
        except Exception:
            pass
        self.export_btn = widgets.Button(icon='download', tooltip='Export all cells', button_style='', layout=widgets.Layout(width='28px', height='28px'))
        self.export_py_btn = widgets.Button(description=' Python (.py)', icon='code', tooltip='Download as Python script', button_style='info', layout=widgets.Layout(width='130px', height='24px'))
        self.export_ipynb_btn = widgets.Button(description=' Notebook (.ipynb)', icon='book', tooltip='Download as Jupyter notebook', button_style='info', layout=widgets.Layout(width='130px', height='24px'))
        self.export_txt_btn = widgets.Button(description=' Plain Text (.txt)', icon='file-text-o', tooltip='Download as text file', button_style='info', layout=widgets.Layout(width='130px', height='24px'))
        self.export_menu = widgets.VBox([self.export_py_btn, self.export_ipynb_btn, self.export_txt_btn], layout=widgets.Layout(display='none', width='140px'))
        self.export_menu.add_class('epic-export-dropdown')
        self.add_below_btn = widgets.Button(icon='plus', tooltip='Add cell below', button_style='')
        self.delete_btn = widgets.Button(icon='trash', tooltip='Delete cell', button_style='')
        for b in (self.play_btn, self.export_btn, self.add_below_btn, self.delete_btn):
            b.layout.width = '28px'
            b.layout.height = '28px'
            b.add_class('epic-ghost')
        self.ai_btn.add_class('epic-ghost')
        try:
            self.ai_btn.layout.padding = '0 8px'
            self.ai_btn.layout.min_width = '56px'
            self.ai_btn.layout.overflow = 'visible'
        except Exception:
            pass
        for export_btn in (self.export_py_btn, self.export_ipynb_btn, self.export_txt_btn):
            export_btn.add_class('epic-export-menu-btn')
        self.context_section = widgets.VBox([self.context_menu, self.context_btn], layout=widgets.Layout(align_items='center', position='relative'))
        self.context_section.add_class('epic-export-section')
        left_controls = widgets.HBox([self.play_btn, self.ai_btn, self.context_section], layout=widgets.Layout(align_items='center', gap='4px'))
        self.export_section = widgets.VBox([self.export_menu, self.export_btn], layout=widgets.Layout(align_items='center', position='relative'))
        self.export_section.add_class('epic-export-section')
        right_controls = widgets.HBox([self.export_section, self.add_below_btn, self.delete_btn])
        self.controls = widgets.HBox([left_controls, widgets.HBox([], layout=widgets.Layout(flex='1')), right_controls], layout=widgets.Layout(align_items='center', justify_content='space-between'))
        self.controls.add_class('epic-controls')
        self.ai_input = widgets.Textarea(placeholder='Ask Agents to write code...', layout=widgets.Layout(width='100%', height='48px'), continuous_update=False)
        self.ai_input.add_class('ai_input')
        self.ai_send = widgets.Button(description='Send', icon='', button_style='', layout=widgets.Layout(width='96px', height='32px'))
        try:
            self.ai_send.remove_class('epic-send-circle')
        except Exception:
            pass
        self.ai_cancel_btn = widgets.Button(description='Cancel', icon='', button_style='', layout=widgets.Layout(width='96px', height='32px', display='none'))
        self.ai_status = widgets.HTML(value='')
        self.ai_loading = widgets.HTML(value=(
            "<div class='epic-dots-loading' style='display:flex;align-items:center;height:32px'>"
            "<span style='font-size:12px;color:#9ca3af;margin-right:8px'>Thinking</span>"
            "<span class='dot'></span><span class='dot'></span><span class='dot'></span>"
            "<style>"
            ".epic-dots-loading .dot{width:6px;height:6px;background:#666;border-radius:50%;display:inline-block;margin-right:4px;animation:epicPulse 1.2s infinite ease-in-out;}"
            ".epic-dots-loading .dot:nth-child(2){animation-delay:0.2s}"
            ".epic-dots-loading .dot:nth-child(3){animation-delay:0.4s}"
            "@keyframes epicPulse{0%,80%,100%{opacity:.3;transform:translateY(0)}40%{opacity:1;transform:translateY(-2px)}}"
            "</style>"
            "</div>"
        ), layout=widgets.Layout(display='none'))
        self.ai_bar = widgets.HBox([self.ai_loading, self.ai_send, self.ai_cancel_btn, self.ai_status], layout=widgets.Layout(justify_content='flex-start', gap='6px'))
        self.ai_box = widgets.VBox([self.ai_input, self.ai_bar], layout=widgets.Layout(border='1px solid #3c3c3c', padding='8px', width='100%', background_color='#1e1e1e'))
        self.ai_box.add_class('epic-ai-in-cell')
        self.ai_hint_overlay = widgets.HTML('')
        self.editor_container = widgets.VBox([self.code], layout=widgets.Layout(position='relative'))
        self.editor_container.add_class('epic-editor-container')
        self.code_wrap = widgets.VBox([self.editor_container, self.ai_hint_overlay], layout=widgets.Layout(position='relative'))
        self.code_wrap.add_class('epic-code-wrap')
        self.in_label = widgets.HTML(value=f"<div class='epic-prompt epic-prompt-in'>In&nbsp;[{self.idx}]:</div>", layout=widgets.Layout(width='72px', align_self='flex-start'))
        self.out_label = widgets.HTML(value=f"<div class='epic-prompt epic-prompt-out'>Out&nbsp;[{self.idx}]:</div>", layout=widgets.Layout(width='72px', align_self='flex-start'))
        self.out = widgets.HTML(value='', layout={'width': '100%', 'min_height': '150px', 'display': 'none', 'border': '1px solid #ddd', 'padding': '10px', 'background_color': '#f8f9fa'})
        self.out.add_class('epic-output')
        self._out_spinner = widgets.HTML(
            value=(
                "<div class='epic-out-spinner-wrap' style='display:flex;align-items:center;padding:4px 0 8px 0'>"
                "<div class='epic-out-spinner-circle'></div>"
                "<style>"
                ".epic-out-spinner-circle{width:16px;height:16px;border:3px solid rgba(107,114,128,0.22);border-top-color:#6b7280;border-radius:50%;animation:epicOutSpin 0.8s linear infinite;}"
                "@keyframes epicOutSpin{to{transform:rotate(360deg)}}"
                "</style>"
                "</div>"
            ),
            layout=widgets.Layout(display='none')
        )
        self._out_spinner.add_class('epic-out-spinner-widget')
        self.out_container = widgets.VBox([self._out_spinner, self.out], layout=widgets.Layout(width='100%'))
        self.hil_status = widgets.HTML(value="", layout=widgets.Layout(margin='0', display='none'))
        self.hil_stop_btn = widgets.Button(description='', icon='stop', tooltip='Cancel', layout=widgets.Layout(width='28px', height='28px', display='none'))
        try:
            self.hil_stop_btn.add_class('epic-stop-square')
        except Exception:
            pass
        def _on_hil_stop(_b=None):
            try:
                if self.parent is not None and hasattr(self.parent, 'cancel_hil'):
                    self.parent.cancel_hil()
                try:
                    self._update_send_button_mode()
                except Exception:
                    pass
            except Exception:
                pass
        self.hil_stop_btn.on_click(_on_hil_stop)
        try:
            self._agents_cancel_btn.on_click(_on_hil_stop)
        except Exception:
            pass
        try:
            self.ai_cancel_btn.on_click(_on_hil_stop)
        except Exception:
            pass
        self.hil_bar = widgets.HBox([self.hil_status], layout=widgets.Layout(display='none', align_items='center', justify_content='center', gap='12px', width='100%'))
        self.input_row = widgets.HBox([self.in_label, widgets.VBox([self.controls, self.code_wrap], layout=widgets.Layout(width='100%'))], layout=widgets.Layout(width='100%'))
        self.output_row = widgets.HBox([self.out_label, self.out_container], layout=widgets.Layout(width='100%', display='none'))
        self.widget = widgets.VBox([self.input_row, self.output_row, self.hil_bar], layout=widgets.Layout(border='0', padding='0', margin='10px 0', position='relative'))
        self.widget.add_class('epic-cell')
        try:
            self._update_send_button_mode()
        except Exception:
            pass
        self.play_btn.on_click(self._on_run)
        self.export_btn.on_click(self._toggle_export_menu)
        self.export_py_btn.on_click(lambda _: self._on_export_all('py'))
        self.export_ipynb_btn.on_click(lambda _: self._on_export_all('ipynb'))
        self.export_txt_btn.on_click(lambda _: self._on_export_all('txt'))
        self.add_below_btn.on_click(lambda _btn: self._on_add_below(self))
        self.delete_btn.on_click(lambda _btn: self._on_delete(self))
        self.ai_send.on_click(_on_ai_bar_send_button)
        self.context_btn.on_click(self._toggle_context_menu)
        self._ctx_apply_btn.on_click(self._on_context_apply)
        self._ctx_cancel_btn.on_click(lambda _btn: self._hide_context_menu())
        def _toggle_hint_on_code_change(_chg=None):
            try:
                val = (self.code.value or '').strip()
                should_show = (not val) and (self.editor_container.children == (self.code,))
                new_disp = 'block' if should_show else 'none'
                if self.ai_hint_overlay.layout.display != new_disp:
                    self.ai_hint_overlay.layout.display = new_disp
            except Exception:
                pass
        def _on_ai_btn_click(btn):
            try:
                self.output_row.layout.display = 'flex'
                self.out.layout.display = 'block'
                self.out.value = "<div style='padding:8px;border:1px solid #e5e7eb;background:#fff;'                    >\ud83d\udd12 AI functionality is disabled. Only auth and UI are available.</div>"
            except Exception:
                pass
        try:
            self.ai_btn.on_click(_toggle_agents_panel)
        except Exception:
            pass
    def _get_current_dir_files(self) -> List[str]:
        try:
            entries = []
            for name in os.listdir('.'):
                if name.startswith('.'):
                    continue
                if os.path.isfile(name):
                    entries.append(name)
            entries.sort()
            return entries
        except Exception:
            return []
    def _build_import_schema(self, max_items: int = 80) -> Dict[str, str]:
        """
        Collect a snapshot of imported modules/aliases from the shared namespace.
        Returns a mapping alias -> module_name so the backend can stay environment-aware.
        """
        schema: Dict[str, str] = {}
        try:
            for alias, value in list(self.shared_ns.items()):
                if not isinstance(alias, str) or not alias or alias.startswith('__'):
                    continue
                module_name = None
                if isinstance(value, types.ModuleType):
                    module_name = value.__name__
                else:
                    module_name = getattr(value, '__module__', None)
                if not module_name:
                    continue
                schema[alias] = module_name
                if len(schema) >= max_items:
                    break
        except Exception:
            return schema
        return schema
    def _rebuild_context_file_list(self):
        files = self._get_current_dir_files()
        self._context_checkboxes = []
        items: List[widgets.Widget] = []
        if not files:
            items.append(widgets.HTML("<div style='padding:6px;color:#555'>No files found in current directory.</div>"))
        else:
            for f in files:
                cb = widgets.Checkbox(value=f in self.selected_context_files, description=f, indent=False, layout=widgets.Layout(width='100%'))
                self._context_checkboxes.append(cb)
                items.append(cb)
        self._ctx_list_box.children = tuple(items)
    def _toggle_context_menu(self, _btn=None):
        try:
            if self.parent and hasattr(self.parent, 'cells'):
                for c in self.parent.cells:
                    if c is not self:
                        try:
                            c._hide_context_menu()
                        except Exception:
                            pass
        except Exception:
            pass
        if self.context_menu.layout.display == 'none' or not self.context_menu.layout.display:
            self._rebuild_context_file_list()
            try:
                self.context_menu.add_class('open')
            except Exception:
                pass
            self.context_menu.layout.display = 'block'
        else:
            self._hide_context_menu()
    def _hide_context_menu(self):
        try:
            self.context_menu.remove_class('open')
        except Exception:
            pass
        self.context_menu.layout.display = 'none'
    def _on_context_apply(self, _btn=None):
        try:
            selected = []
            for cb in self._context_checkboxes:
                try:
                    if cb.value:
                        selected.append(cb.description)
                except Exception:
                    pass
            self.selected_context_files = selected
            count = len(selected)
            base_label = 'Context'
            self.context_btn.description = f'{base_label} ({count})' if count else base_label
            try:
                if self.parent is not None:
                    setattr(self.parent, 'default_selected_context_files', list(self.selected_context_files))
            except Exception:
                pass
        except Exception:
            pass
        finally:
            self._hide_context_menu()
    def _remember_agent_comment(self, comment: str):
        """Persist the latest agent comment so future AI calls can learn from it."""
        try:
            text = (comment or '').strip()
            self._last_agent_comment = text
            if not text:
                return
            history = []
            if self.parent is not None:
                try:
                    history = list(getattr(self.parent, '_agent_comment_history', []))
                except Exception:
                    history = []
                history.append(text)
                setattr(self.parent, '_agent_comment_history', history[-7:])
                setattr(self.parent, '_latest_agent_comment', text)
        except Exception:
            pass
    def _gather_agent_comment_context(self, max_items: int = 4) -> str:
        """Return the latest agent suggestions concatenated for backend context."""
        try:
            comments: List[str] = []
            if self.parent is not None:
                try:
                    raw = getattr(self.parent, '_agent_comment_history', [])
                    if isinstance(raw, (list, tuple)):
                        comments.extend(str(c) for c in raw if isinstance(c, str))
                except Exception:
                    pass
            if self._last_agent_comment:
                comments.append(self._last_agent_comment)
            trimmed = [c.strip() for c in comments if isinstance(c, str) and c.strip()]
            if not trimmed:
                return ''
            joined = '\n\n'.join(trimmed[-max_items:])
            if len(joined) > 8000:
                joined = joined[-8000:]
            return joined
        except Exception:
            return ''
    def _get_agent_processor(self):
        if self._agent_processor is None:
            self._agent_processor = create_agent_processor(self.shared_ns)
        return self._agent_processor
    def _on_run(self, _):
        try:
            transient = bool(getattr(self, '_force_show_explain_once', False))
        except Exception:
            transient = False
        if transient:
            self._execute_like_ai(show_explanation=True)
        else:
            self._execute_like_ai(show_explanation=False)
    def _toggle_export_menu(self, _btn=None):
        try:
            if self.parent and hasattr(self.parent, 'cells'):
                for c in self.parent.cells:
                    if c is not self:
                        try:
                            c._hide_export_menu()
                        except Exception:
                            pass
        except Exception:
            pass
        if 'open' in getattr(self.export_menu, '_dom_classes', set()):
            try:
                self.export_menu.remove_class('open')
            except Exception:
                pass
            self.export_menu.layout.display = 'none'
        else:
            try:
                self.export_menu.add_class('open')
            except Exception:
                pass
            self.export_menu.layout.display = 'block'
    def _hide_export_menu(self):
        try:
            self.export_menu.remove_class('open')
        except Exception:
            pass
        self.export_menu.layout.display = 'none'
    def _on_export_all(self, export_format):
        if not self.parent:
            self.out.value = (self.out.value or '') + "<div style='color:#b91c1c'>⚠️ Cannot access notebook cells</div>"
            return
        all_cells_code = []
        for cell in self.parent.cells:
            code = (cell.code.value or '').strip()
            if code:
                all_cells_code.append(code)
        if not all_cells_code:
            self.out.value = (self.out.value or '') + '<div>⚠️ No code to export from any cells</div>'
            return
        if export_format == 'py':
            parts = []
            for i, code in enumerate(all_cells_code, 1):
                parts.append(f'# In [{i}]:\n{code}')
            content = '\n\n'.join(parts)
            filename = 'notebook_export.py'
            mime_type = 'text/x-python'
        elif export_format == 'txt':
            parts = []
            for i, code in enumerate(all_cells_code, 1):
                parts.append(f'In [{i}]:\n{code}')
            content = '\n\n'.join(parts)
            filename = 'notebook_export.txt'
            mime_type = 'text/plain'
        elif export_format == 'ipynb':
            import json
            cells = []
            for code in all_cells_code:
                source_lines = [line + '\n' for line in code.splitlines()] or ['']
                cells.append({'cell_type': 'code', 'execution_count': None, 'metadata': {}, 'outputs': [], 'source': source_lines})
            notebook_content = {'cells': cells, 'metadata': {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python', 'version': sys.version.split()[0], 'mimetype': 'text/x-python', 'codemirror_mode': {'name': 'ipython', 'version': 3}, 'pygments_lexer': 'ipython3', 'nbconvert_exporter': 'python', 'file_extension': '.py'}}, 'nbformat': 4, 'nbformat_minor': 5}
            content = json.dumps(notebook_content, indent=2)
            filename = 'notebook_export.ipynb'
            mime_type = 'application/json'
        else:
            with self.out:
                print(f'⚠️ Unsupported export format: {export_format}')
            return
        try:
            escaped_content = content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
            js_code = f'''\n            // Create downloadable file\n            const content = "{escaped_content}";\n            const blob = new Blob([content], {type: \'{mime_type}\'} );\n            const url = URL.createObjectURL(blob);\n            \n            // Create temporary download link\n            const a = document.createElement('a');\n            a.href = url;\n            a.download = "{filename}";\n            document.body.appendChild(a);\n            a.click();\n            document.body.removeChild(a);\n            URL.revokeObjectURL(url);\n            \n            // Show success message\n            console.log("Exported all cells as {filename}");\n            '''
            display(Javascript(js_code))
        except Exception:
            pass
        try:
            mode = 'w'
            with open(filename, mode, encoding='utf-8') as f:
                f.write(content)
            try:
                link = FileLink(filename, result_html_prefix='Saved locally. Click to download: ')
                link_html = link._repr_html_()
            except Exception:
                link_html = f"<a href='{filename}' download>{filename}</a>"
            self.out.value = (self.out.value or '') + f'<div>📁 Exported {len(all_cells_code)} cells as: {filename}</div>' + link_html
        except Exception as e:
            self.out.value = (self.out.value or '') + f"<div style='color:#b91c1c'>⚠️ Failed to write file to disk: {e}</div>"
        self._hide_export_menu()
    def execute(self):
        src = self.code.value
        if not src.strip():
            return
        try:
            self.out.value = ''
        except Exception:
            pass
        self.out.layout.display = 'block'
        try:
            self._out_spinner.layout.display = 'flex'
        except Exception:
            pass
        try:
            if hasattr(self, 'output_row'):
                self.output_row.layout.display = 'flex'
        except Exception:
            pass
        cap = None
        self._set_running(True)
        self._last_had_exception = False
        self.last_output_text = ''
        try:
            import sys as _sys
            import matplotlib
            if 'matplotlib.pyplot' not in _sys.modules:
                try:
                    matplotlib.use('module://matplotlib_inline.backend_inline')
                except Exception:
                    pass
            import matplotlib.pyplot as plt
            try:
                plt.ioff()
            except Exception:
                pass
        except ImportError:
            pass
        try:
            import ast
            with self.out:
                with capture_output(display=True) as cap:
                    src = self._process_pip_commands(src)
                    try:
                        tree = ast.parse(src, mode='exec')
                        body = tree.body if hasattr(tree, 'body') else []
                    except Exception:
                        body = []
                    if body and hasattr(body[-1], 'value') and isinstance(body[-1], ast.Expr):
                        last_expr = body[-1]
                        pre_nodes = body[:-1]
                        pre_tree = ast.Module(body=pre_nodes, type_ignores=[]) if hasattr(ast, 'Module') else None
                        if pre_nodes:
                            pre_code = compile(pre_tree, f'<MiniCell {self.idx} pre>', 'exec')
                            exec(pre_code, self.shared_ns, self.shared_ns)
                        handled_html_print = False
                        try:
                            call_node = last_expr.value if isinstance(last_expr.value, ast.Call) else None
                            if call_node is not None and (getattr(call_node.func, 'id', '') == 'print' or getattr(call_node.func, 'attr', '') == 'print'):
                                args_list = list(getattr(call_node, 'args', []))
                                kws_list = list(getattr(call_node, 'keywords', []))
                                if len(args_list) == 1 and len(kws_list) == 0:
                                    try:
                                        arg_expr = ast.Expression(args_list[0])
                                        arg_val = eval(compile(arg_expr, f'<MiniCell {self.idx} print-arg>', 'eval'), self.shared_ns, self.shared_ns)
                                        if isinstance(arg_val, str):
                                            s = arg_val.strip()
                                            if s.startswith('<') and ('</' in s or '<table' in s or '<div' in s or ('<style' in s) or ('<html' in s) or ('<body' in s)):
                                                display(HTML(arg_val))
                                                handled_html_print = True
                                    except Exception:
                                        pass
                        except Exception:
                            pass
                        if not handled_html_print:
                            expr_code = compile(ast.Expression(last_expr.value), f'<MiniCell {self.idx} expr>', 'eval')
                            result = eval(expr_code, self.shared_ns, self.shared_ns)
                            try:
                                try:
                                    import pandas as _pd_local
                                    if isinstance(result, (_pd_local.DataFrame, _pd_local.Series)):
                                        pass
                                    elif isinstance(result, str):
                                        s = result.strip()
                                        if s.startswith('<') and ('</' in s or '<table' in s or '<div' in s or ('<style' in s) or ('<html' in s) or ('<body' in s)):
                                            display(HTML(result))
                                        else:
                                            display(result)
                                    else:
                                        display(result)
                                except ImportError:
                                    if isinstance(result, str):
                                        s = result.strip()
                                        if s.startswith('<') and ('</' in s or '<table' in s or '<div' in s or ('<style' in s) or ('<html' in s) or ('<body' in s)):
                                            display(HTML(result))
                                        else:
                                            display(result)
                                    else:
                                        display(result)
                            except Exception:
                                print(result)
                    else:
                        exec(compile(src, f'<MiniCell {self.idx}>', 'exec'), self.shared_ns, self.shared_ns)
        except Exception:
            err = traceback.format_exc()
            with self.out:
                print(err)
            self._last_had_exception = True
        finally:
            pass
            with self.out:
                try:
                    if cap is not None:
                        cap.show()
                except Exception:
                    pass
        combined = ((getattr(cap, 'stdout', '') if cap is not None else '') or '') + ('\n' + getattr(cap, 'stderr', '') if cap is not None and getattr(cap, 'stderr', '') else '')
        self.last_output_text = combined if (combined and combined.strip()) else '[no output]'
        self._set_running(False)
        try:
            self._out_spinner.layout.display = 'none'
        except Exception:
            pass
        try:
            if src.strip() and (not self._suppress_auto_add):
                self._on_add_below(self)
        except Exception:
            pass
    def _toggle_ai_box(self, _btn=None):
        self.ai_box.layout.display = 'block' if self.ai_box.layout.display == 'none' or not self.ai_box.layout.display else 'none'
        if self.ai_box.layout.display == 'block':
            self.ai_hint_overlay.layout.display = 'none'
        elif not (self.code.value or '').strip():
            self.ai_hint_overlay.layout.display = 'flex'
    def _open_ai_box(self):
        self.editor_container.children = [self.ai_box]
        self.ai_hint_overlay.layout.display = 'none'
    def _on_ai_cancel(self, _btn=None):
        self.ai_status.value = "<span style='color:#ef4444'>Canceled</span>"
        self.ai_send.disabled = False
        self._hide_ai()
    def _hide_ai(self):
        self.editor_container.children = (self.code,)
        self.ai_input.value = ''
        if not (self.code.value or '').strip():
            self.ai_hint_overlay.layout.display = 'flex'
    def _schedule_execute(self, delay_s: float=0.0):
        def _execute_with_output_setup():
            try:
                self.out.value = ''
            except Exception:
                pass
            self.out.layout.display = 'block'
            if hasattr(self, 'output_row'):
                self.output_row.layout.display = 'flex'
            self.execute()
        try:
            ip = get_ipython()
            if ip is not None and hasattr(ip, 'kernel') and hasattr(ip.kernel, 'io_loop') and (ip.kernel.io_loop is not None):
                if delay_s and delay_s > 0:
                    ip.kernel.io_loop.call_later(delay_s, _execute_with_output_setup)
                else:
                    ip.kernel.io_loop.add_callback(_execute_with_output_setup)
                return
        except Exception:
            pass
        try:
            from tornado.ioloop import IOLoop
            loop = IOLoop.current()
            if delay_s and delay_s > 0:
                loop.call_later(delay_s, _execute_with_output_setup)
            else:
                loop.add_callback(_execute_with_output_setup)
            return
        except Exception:
            pass
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            if delay_s and delay_s > 0:
                loop.call_later(delay_s, _execute_with_output_setup)
            else:
                loop.call_soon_threadsafe(_execute_with_output_setup)
            return
        except Exception:
            pass
        _execute_with_output_setup()
    def _simulate_human_play_click(self, delay_s: float=0.0):
        def _human_like_click():
            self._on_run(None)
        try:
            ip = get_ipython()
            if ip is not None and hasattr(ip, 'kernel') and hasattr(ip.kernel, 'io_loop') and (ip.kernel.io_loop is not None):
                if delay_s and delay_s > 0:
                    ip.kernel.io_loop.call_later(delay_s, _human_like_click)
                else:
                    ip.kernel.io_loop.add_callback(_human_like_click)
                return
        except Exception:
            pass
        try:
            from tornado.ioloop import IOLoop
            loop = IOLoop.current()
            if delay_s and delay_s > 0:
                loop.call_later(delay_s, _human_like_click)
            else:
                loop.add_callback(_human_like_click)
            return
        except Exception:
            pass
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            if delay_s and delay_s > 0:
                loop.call_later(delay_s, _human_like_click)
            else:
                loop.call_soon_threadsafe(_human_like_click)
            return
        except Exception:
            pass
        _human_like_click()
    def _execute_like_ai(self, *, show_explanation: Optional[bool]=None):
        src = self.code.value
        if not src.strip():
            return
        self.output_row.layout.display = 'flex'
        self.out.layout.display = 'block'
        try:
            self._out_spinner.layout.display = 'flex'
        except Exception:
            pass
        self._last_had_exception = False
        self.last_output_text = ''
        processor = self._get_agent_processor()
        result = processor.execute_code_with_visuals(src)
        if result['success']:
            self.out.value = result['html_output']
            self._last_had_exception = result['had_error']
            self.last_output_text = result['output_text'] if (result.get('output_text') and result['output_text'].strip()) else '[no output]'
        else:
            self.out.value = result['html_output']
            self._last_had_exception = True
            self.last_output_text = (result.get('output_text', '') or '').strip() or '[no output]'
        try:
            self._out_spinner.layout.display = 'none'
        except Exception:
            pass
        try:
            transient = bool(getattr(self, '_force_show_explain_once', False))
        except Exception:
            transient = False
        try:
            if hasattr(self, '_force_show_explain_once'):
                self._force_show_explain_once = False
        except Exception:
            pass
        if show_explanation is None:
            if transient:
                _should_explain = True
            else:
                try:
                    cell_enabled = getattr(self, '_agent_comment_enabled', None)
                    if cell_enabled is None and self.parent is not None:
                        cell_enabled = bool(getattr(self.parent, 'agent_comments_enabled', True))
                    _should_explain = bool(True if cell_enabled is None else cell_enabled)
                except Exception:
                    _should_explain = True
        else:
            _should_explain = bool(show_explanation or False) or transient
        try:
            if not _should_explain:
                raise RuntimeError('skip_explain')
            base = get_auth_manager().api_base_url.rstrip('/')
            try:
                _am = get_auth_manager()
                _tok = _am.get_stored_token()
            except Exception:
                _tok = None
            explain_url = f'{base}/api/ai'
            headers = {'Content-Type': 'application/json'}
            if _tok:
                headers['Authorization'] = f'Bearer {_tok}'
            payload = {'mode': 'explain', 'code': src, 'output': self.last_output_text or '', 'had_error': bool(self._last_had_exception)}
            def _explain_worker():
                try:
                    try:
                        if self.parent is not None and getattr(self.parent, '_hil_cancelled', False):
                            return
                    except Exception:
                        pass
                    resp = requests.post(explain_url, json=payload, headers=headers, timeout=30)
                    if resp.status_code == 200:
                        data = resp.json()
                        explanation = data.get('explanation') or ''
                        if explanation:
                            try:
                                self._remember_agent_comment(explanation)
                            except Exception:
                                pass
                            try:
                                safe = _html.escape(explanation)
                                box = f"<div class='epic-agent-comment' style='margin-top:10px;border:1px solid #e5e7eb;background:#f9fafb;padding:10px'><div style='font-weight:600;margin-bottom:6px'>Agent Comment</div><div style='white-space:pre-wrap'>{safe}</div></div>"
                                self.out.value = (self.out.value or '') + box
                            except Exception:
                                pass
                            try:
                                base2 = get_auth_manager().api_base_url.rstrip('/')
                                master_url = f'{base2}/api/master-agent'
                                headers2 = {'Content-Type': 'application/json'}
                                if _tok:
                                    headers2['Authorization'] = f'Bearer {_tok}'
                                recent_inputs: List[str] = []
                                recent_outputs: List[str] = []
                                recent_comments: List[str] = []
                                recent_errors: List[str] = []
                                try:
                                    if self.parent and hasattr(self.parent, 'cells'):
                                        cells_list = list(self.parent.cells)
                                        try:
                                            cur_index = cells_list.index(self)
                                            subset = cells_list[:cur_index + 1]
                                        except Exception:
                                            subset = cells_list
                                        tail = subset[-7:]
                                        for c in tail:
                                            try:
                                                code_txt = (getattr(c, 'code', None).value if getattr(c, 'code', None) else '') or ''
                                            except Exception:
                                                code_txt = ''
                                            try:
                                                out_txt = getattr(c, 'last_output_text', '') or ''
                                            except Exception:
                                                out_txt = ''
                                            try:
                                                had_err = bool(getattr(c, '_last_had_exception', False))
                                            except Exception:
                                                had_err = False
                                            recent_inputs.append((code_txt or '')[:2000])
                                            recent_outputs.append((out_txt or '')[:2000])
                                            if had_err and out_txt:
                                                recent_errors.append(out_txt[:1000])
                                        if explanation:
                                            recent_comments.append(explanation[:1000])
                                except Exception:
                                    pass
                                try:
                                    selected_files = list(self.selected_context_files or [])
                                except Exception:
                                    selected_files = []
                                cwd2 = os.getcwd()
                                abs_paths2 = []
                                dirs2 = set()
                                for fname in selected_files:
                                    try:
                                        abs_path = os.path.abspath(fname)
                                        abs_paths2.append(abs_path)
                                        dirs2.add(os.path.dirname(abs_path) or cwd2)
                                    except Exception:
                                        pass
                                master_payload = {'goal_prompt': (getattr(self.parent, '_original_goal_prompt', '') if self.parent is not None else '') or '', 'current_prompt': (getattr(self.parent, '_current_prompt', '') if self.parent is not None else '') or '', 'prompt': '', 'agent_explanation': explanation, 'recent_inputs': recent_inputs, 'recent_outputs': recent_outputs, 'recent_comments': recent_comments, 'recent_errors': recent_errors, 'context_files': selected_files, 'context_paths': abs_paths2, 'context_dirs': list(dirs2), 'cwd': cwd2}
                                try:
                                    mresp = requests.post(master_url, json=master_payload, headers=headers2, timeout=30)
                                    if mresp.status_code == 200:
                                        mdata = mresp.json()
                                        status = (mdata.get('status') or 'unfinished').lower()
                                        message = mdata.get('message') or ('Project completed' if status == 'completed' else 'Project unfinished')
                                        rationale_and_prompt = mdata.get('rationale_and_prompt') or mdata.get('rationale') or ''
                                        if status == 'completed':
                                            try:
                                                if self.parent is not None:
                                                    setattr(self.parent, '_master_unfinished_count', 0)
                                                    setattr(self.parent, '_project_completed_flag', True)
                                                    setattr(self.parent, '_hil_active', False)
                                                    setattr(self.parent, '_hil_cancelled', False)
                                                    if hasattr(self.parent, '_update_hil_bars'):
                                                        self.parent._update_hil_bars()
                                            except Exception:
                                                pass
                                        elif status == 'unfinished':
                                            try:
                                                cnt = int(getattr(self.parent, '_master_unfinished_count', 0) or 0) + 1
                                                setattr(self.parent, '_master_unfinished_count', cnt)
                                            except Exception:
                                                cnt = 1
                                            if cnt >= 11:
                                                try:
                                                    _safe_msg = _html.escape('Guardrail reached: To prevent excessive API usage, please enter a new query to the AI to continue the project(s)')
                                                    _safe_rat = _html.escape(rationale_and_prompt or '')
                                                    stop_box = f"<div class='epic-agent-comment' style='margin-top:10px;border:1px solid #e5e7eb;background:#fffdf5;padding:10px'><div style='font-weight:600;margin-bottom:6px'>Guardrail Reached</div><div style='white-space:pre-wrap'>{_safe_msg}\n{_safe_rat}</div></div>"
                                                    self.out.value = (self.out.value or '') + stop_box
                                                except Exception:
                                                    pass
                                                try:
                                                    if self.parent is not None:
                                                        setattr(self.parent, '_hil_active', False)
                                                        setattr(self.parent, '_hil_cancelled', False)
                                                        if hasattr(self.parent, '_update_hil_bars'):
                                                            self.parent._update_hil_bars()
                                                except Exception:
                                                    pass
                                                return
                                            try:
                                                try:
                                                    if self.parent is not None and getattr(self.parent, '_hil_cancelled', False):
                                                        setattr(self.parent, '_hil_active', False)
                                                        if hasattr(self.parent, '_update_hil_bars'):
                                                            self.parent._update_hil_bars()
                                                        return
                                                except Exception:
                                                    pass
                                                _txt = message or ''
                                                if rationale_and_prompt:
                                                    _txt = f'{_txt}\n{rationale_and_prompt}'
                                                base3 = get_auth_manager().api_base_url.rstrip('/')
                                                try:
                                                    _am3 = get_auth_manager()
                                                    _tok3 = _am3.get_stored_token()
                                                except Exception:
                                                    _tok3 = None
                                                url3 = f'{base3}/api/ai'
                                                headers3 = {"User-Agent": "sagebow-client/0.1"}
                                                if _tok3:
                                                    headers3['Authorization'] = f'Bearer {_tok3}'
                                                try:
                                                    selected_files3 = list(self.selected_context_files or [])
                                                except Exception:
                                                    selected_files3 = []
                                                cwd3 = os.getcwd()
                                                rel_paths3 = []
                                                base_names3 = []
                                                dir_hints3 = set()
                                                for fname in selected_files3:
                                                    try:
                                                        abs_path3 = os.path.abspath(fname)
                                                        bn3 = os.path.basename(abs_path3)
                                                        base_names3.append(bn3)
                                                        try:
                                                            rel3 = os.path.relpath(abs_path3, cwd3)
                                                        except Exception:
                                                            rel3 = bn3
                                                        if rel3.startswith('..'):
                                                            rel3 = bn3
                                                        rel_paths3.append(rel3)
                                                        d3 = os.path.dirname(rel3) if rel3 and rel3 != bn3 else ''
                                                        if d3:
                                                            dir_hints3.add(d3)
                                                    except Exception:
                                                        pass
                                                payload3 = {
                                                    'prompt': _txt,
                                                    'context_files': base_names3,
                                                    'context_paths': rel_paths3,
                                                    'context_dirs': list(dir_hints3),
                                                    'cwd': cwd3,
                                                }
                                                try:
                                                    schema3 = self._build_import_schema()
                                                    if schema3:
                                                        payload3['import_schema'] = schema3
                                                except Exception:
                                                    pass
                                                try:
                                                    recent_inputs3 = []
                                                    recent_outputs3 = []
                                                    if self.parent and hasattr(self.parent, 'cells'):
                                                        cells_list3 = list(self.parent.cells)
                                                        try:
                                                            cur_index3 = cells_list3.index(self)
                                                            subset3 = cells_list3[:cur_index3 + 1]
                                                        except Exception:
                                                            subset3 = cells_list3
                                                        tail3 = subset3[-4:]
                                                        for c3 in tail3:
                                                            try:
                                                                code_txt3 = (getattr(c3, 'code', None).value if getattr(c3, 'code', None) else '') or ''
                                                            except Exception:
                                                                code_txt3 = ''
                                                            try:
                                                                out_txt3 = getattr(c3, 'last_output_text', '') or ''
                                                            except Exception:
                                                                out_txt3 = ''
                                                            recent_inputs3.append((code_txt3 or '')[:2000])
                                                            recent_outputs3.append((out_txt3 or '')[:2000])
                                                    if recent_inputs3:
                                                        payload3['recent_inputs'] = recent_inputs3
                                                    if recent_outputs3:
                                                        payload3['recent_outputs'] = recent_outputs3
                                                except Exception:
                                                    pass
                                                resp3 = requests.post(url3, json=payload3, headers=headers3, timeout=60)
                                                if resp3.status_code == 200:
                                                    data3 = resp3.json()
                                                    code3 = data3.get('text') or data3.get('output') or ''
                                                    if not isinstance(code3, str):
                                                        code3 = str(code3)
                                                else:
                                                    code3 = f'# Error {resp3.status_code}: {resp3.text}'
                                                try:
                                                    if self.parent is not None and getattr(self.parent, '_hil_cancelled', False):
                                                        setattr(self.parent, '_hil_active', False)
                                                        if hasattr(self.parent, '_update_hil_bars'):
                                                            self.parent._update_hil_bars()
                                                        return
                                                except Exception:
                                                    pass
                                                new_cell = None
                                                if self.parent:
                                                    new_cell = self.parent.add_cell_below(self)
                                                if new_cell:
                                                    try:
                                                        new_cell.editor_container.children = (new_cell.code,)
                                                        new_cell.agents_ui.layout.display = 'none'
                                                    except Exception:
                                                        pass
                                                    try:
                                                        new_cell.code.value = code3 or '# No response received'
                                                    except Exception:
                                                        pass
                                                    try:
                                                        if code3 and (not (str(code3).strip().startswith('#'))):
                                                            try:
                                                                _nb_allow3 = True
                                                                if self.parent is not None:
                                                                    _nb_allow3 = bool(getattr(self.parent, 'agent_comments_enabled', True))
                                                                if _nb_allow3:
                                                                    new_cell._force_show_explain_once = True
                                                            except Exception:
                                                                pass
                                                            new_cell._on_run(None)
                                                    except Exception:
                                                        pass
                                            except Exception:
                                                pass
                                    else:
                                        pass
                                except Exception:
                                    pass
                            except Exception:
                                pass
                except Exception:
                    pass
            threading.Thread(target=_explain_worker, daemon=True).start()
        except Exception:
            pass
        try:
            if self.parent and (not self._suppress_auto_add):
                is_last = bool(self.parent.cells) and self.parent.cells[-1] is self
                if is_last:
                    self.parent.add_cell_below(self)
        except Exception:
            pass
    def _on_ai_send(self, _btn=None):
        try:
            task = (self.ai_input.value or '').strip()
            if not task:
                return
            try:
                if self.parent is not None:
                    try:
                        _suppress = bool(getattr(self.parent, '_suppress_unfinished_reset', False))
                    except Exception:
                        _suppress = False
                    try:
                        if not _suppress and bool(getattr(self.parent, '_project_completed_flag', False)):
                            setattr(self.parent, '_original_goal_prompt', task)
                            setattr(self.parent, '_project_completed_flag', False)
                    except Exception:
                        pass
                    try:
                        existing_goal = getattr(self.parent, '_original_goal_prompt', '') or ''
                    except Exception:
                        existing_goal = ''
                    if not existing_goal:
                        try:
                            setattr(self.parent, '_original_goal_prompt', task)
                        except Exception:
                            pass
                    try:
                        setattr(self.parent, '_current_prompt', task)
                    except Exception:
                        pass
                    try:
                        suppress = bool(getattr(self.parent, '_suppress_unfinished_reset', False))
                        if not suppress:
                            setattr(self.parent, '_master_unfinished_count', 0)
                        setattr(self.parent, '_suppress_unfinished_reset', False)
                    except Exception:
                        pass
            except Exception:
                pass
            self._ai_processing = True
            self._ai_cancel_requested = False
            try:
                if self.parent is not None:
                    if getattr(self.parent, '_hil_cancelled', False):
                        try:
                            setattr(self.parent, '_hil_cancelled', False)
                        except Exception:
                            pass
                        try:
                            setattr(self.parent, '_hil_active', True)
                        except Exception:
                            pass
                        try:
                            if hasattr(self.parent, '_update_hil_bars'):
                                self.parent._update_hil_bars()
                        except Exception:
                            pass
                    else:
                        setattr(self.parent, '_hil_active', True)
                        if hasattr(self.parent, '_update_hil_bars'):
                            self.parent._update_hil_bars()
            except Exception:
                pass
            try:
                self._update_send_button_mode()
            except Exception:
                pass
            try:
                self.ai_send.disabled = True
                self.ai_input.disabled = True
                self.ai_status.value = ''
            except Exception:
                pass
            def _worker():
                txt = ''
                try:
                    try:
                        if self.parent is not None and getattr(self.parent, '_hil_cancelled', False):
                            self._ai_cancel_requested = True
                    except Exception:
                        pass
                    if self._ai_cancel_requested:
                        txt = '# Request cancelled by user'
                    else:
                        base = get_auth_manager().api_base_url.rstrip('/')
                        try:
                            _am = get_auth_manager()
                            _tok = _am.get_stored_token()
                        except Exception:
                            _tok = None
                        url = f'{base}/api/ai'
                        headers = {"User-Agent": "sagebow-client/0.1"}
                        if _tok:
                            headers['Authorization'] = f'Bearer {_tok}'
                        try:
                            selected_files = list(self.selected_context_files or [])
                        except Exception:
                            selected_files = []
                        cwd = os.getcwd()
                        rel_paths = []
                        base_names = []
                        dir_hints = set()
                        for fname in selected_files:
                            try:
                                abs_path = os.path.abspath(fname)
                                bn = os.path.basename(abs_path)
                                base_names.append(bn)
                                try:
                                    rel = os.path.relpath(abs_path, cwd)
                                except Exception:
                                    rel = bn
                                if rel.startswith('..'):
                                    rel = bn
                                rel_paths.append(rel)
                                d = os.path.dirname(rel) if rel and rel != bn else ''
                                if d:
                                    dir_hints.add(d)
                            except Exception:
                                pass
                        payload = {
                            'prompt': task,
                            'context_files': base_names,
                            'context_paths': rel_paths,
                            'context_dirs': list(dir_hints),
                            'cwd': cwd,
                        }
                        try:
                            comments_block = self._gather_agent_comment_context()
                            if comments_block:
                                payload['previous_explanation'] = comments_block[:8000]
                        except Exception:
                            pass
                        try:
                            schema = self._build_import_schema()
                            if schema:
                                payload['import_schema'] = schema
                        except Exception:
                            pass
                        try:
                            recent_inputs = []
                            recent_outputs = []
                            if self.parent and hasattr(self.parent, 'cells'):
                                cells_list = list(self.parent.cells)
                                try:
                                    cur_index = cells_list.index(self)
                                    subset = cells_list[:cur_index]
                                except Exception:
                                    subset = cells_list
                                tail = subset[-4:]
                                for c in tail:
                                    try:
                                        code_txt = (getattr(c, 'code', None).value if getattr(c, 'code', None) else '') or ''
                                    except Exception:
                                        code_txt = ''
                                    try:
                                        out_txt = getattr(c, 'last_output_text', '') or ''
                                    except Exception:
                                        out_txt = ''
                                    if code_txt:
                                        recent_inputs.append(code_txt[:2000])
                                    else:
                                        recent_inputs.append('')
                                    if out_txt:
                                        recent_outputs.append(out_txt[:2000])
                                    else:
                                        recent_outputs.append('')
                            if recent_inputs:
                                payload['recent_inputs'] = recent_inputs
                            if recent_outputs:
                                payload['recent_outputs'] = recent_outputs
                        except Exception:
                            pass
                        last_exc = None
                        for attempt in range(3):
                            try:
                                resp = requests.post(url, json=payload, headers=headers, timeout=60)
                                break
                            except Exception as e:
                                last_exc = e
                                time.sleep(min(2 ** attempt, 4))
                        else:
                            raise last_exc if last_exc else RuntimeError('Request failed')
                        if self._ai_cancel_requested:
                            txt = '# Request cancelled by user'
                        elif resp.status_code == 200:
                            data = resp.json()
                            txt = data.get('text') or data.get('output') or ''
                            if not isinstance(txt, str):
                                txt = str(txt)
                        else:
                            txt = f'# Error {resp.status_code}: {resp.text}'
                except Exception as e:
                    if self._ai_cancel_requested:
                        txt = '# Request cancelled by user'
                    else:
                        txt = f'# Request failed: {e}'
                finally:
                    self._ai_processing = False
                    self._ai_cancel_requested = False
                    try:
                        self._update_send_button_mode()
                    except Exception:
                        pass
                    try:
                        self.ai_send.disabled = False
                        self.ai_input.disabled = False
                    except Exception:
                        pass
                    try:
                        self.code.value = txt or '# No response received'
                        self._hide_ai()
                        if txt and (not txt.strip().startswith('#')):
                            try:
                                try:
                                    _nb_allow = True
                                    if self.parent is not None:
                                        _nb_allow = bool(getattr(self.parent, 'agent_comments_enabled', True))
                                    if _nb_allow:
                                        self._force_show_explain_once = True
                                except Exception:
                                    pass
                                self._on_run(None)
                            except Exception as e:
                                print(f'Auto-execution failed: {e}')
                    except Exception:
                        pass
            threading.Thread(target=_worker, daemon=True).start()
        except Exception:
            pass
    def _set_running(self, running: bool):
        if running:
            self.play_btn.icon = 'circle-notch'
            self.play_btn.add_class('epic-spin')
            self.play_btn.disabled = True
            self.add_below_btn.disabled = True
            self.delete_btn.disabled = True
        else:
            self.play_btn.icon = 'play'
            try:
                self.play_btn.remove_class('epic-spin')
            except Exception:
                pass
            self.play_btn.disabled = False
            self.add_below_btn.disabled = False
            self.delete_btn.disabled = False
    def update_index_display(self):
        try:
            if hasattr(self, 'in_label'):
                self.in_label.value = f"<div class='epic-prompt epic-prompt-in'>In&nbsp;[{self.idx}]:</div>"
            if hasattr(self, 'out_label'):
                self.out_label.value = f"<div class='epic-prompt epic-prompt-out'>Out&nbsp;[{self.idx}]:</div>"
        except Exception:
            pass
class MiniNotebook:
    def __init__(self, title: str='SageBow mini-notebook'):
        self.shared_ns: Dict[str, object] = {}
        self.cells: List[MiniCell] = []
        self._master_unfinished_count: int = 0
        self._hil_active: bool = False
        self._hil_cancelled: bool = False
        self.title_html = widgets.HTML('')
        self.cells_box = widgets.VBox([])
        self.agent_comments_enabled: bool = True
        self.container = widgets.VBox([self.cells_box], layout=widgets.Layout(width='100%', padding='0', margin='0'))
        self.add_cell()
    def widget(self):
        return self.container
    def _reindex(self):
        for i, c in enumerate(self.cells, start=1):
            c.idx = i
            try:
                c.update_index_display()
            except Exception:
                pass
    def add_cell(self):
        cell = MiniCell(len(self.cells) + 1, self.shared_ns, on_add_below=self.add_cell_below, on_delete=self.delete_cell, parent=self)
        try:
            cell._agents_text.value = ''
            cell.editor_container.children = (cell.agents_ui,)
            cell.agents_ui.layout.display = 'block'
            try:
                if hasattr(cell, 'ai_hint_overlay'):
                    cell.ai_hint_overlay.layout.display = 'none'
            except Exception:
                pass
        except Exception:
            pass
        self.cells.append(cell)
        self.cells_box.children = tuple(list(self.cells_box.children) + [cell.widget])
        try:
            if self._hil_active:
                cell.hil_bar.layout.display = 'flex'
                if self._hil_cancelled:
                    cell.hil_status.value = "<span style='color:#ef4444'>Canceled</span>"
                if hasattr(cell, '_update_send_button_mode'):
                    cell._update_send_button_mode()
            else:
                cell.hil_bar.layout.display = 'none'
                if hasattr(cell, '_update_send_button_mode'):
                    cell._update_send_button_mode()
        except Exception:
            pass
        try:
            display(HTML("\n            <script>\n            window.requestAnimationFrame(()=>{\n              const el = document.scrollingElement || document.documentElement;\n              el.scrollTo({top: el.scrollHeight, behavior: 'smooth'});\n            });\n            </script>\n            "))
        except Exception:
            pass
    def add_cell_below(self, cell: MiniCell):
        idx = self.cells.index(cell) + 1
        new_cell = MiniCell(idx + 0, self.shared_ns, on_add_below=self.add_cell_below, on_delete=self.delete_cell, parent=self)
        try:
            new_cell._agents_text.value = ''
            new_cell.editor_container.children = (new_cell.agents_ui,)
            new_cell.agents_ui.layout.display = 'block'
            try:
                if hasattr(new_cell, 'ai_hint_overlay'):
                    new_cell.ai_hint_overlay.layout.display = 'none'
            except Exception:
                pass
        except Exception:
            pass
        self.cells.insert(idx, new_cell)
        self.cells_box.children = tuple([c.widget for c in self.cells])
        self._reindex()
        try:
            if self._hil_active:
                new_cell.hil_bar.layout.display = 'flex'
                if self._hil_cancelled:
                    new_cell.hil_status.value = "<span style='color:#ef4444'>Canceled</span>"
                if hasattr(new_cell, '_update_send_button_mode'):
                    new_cell._update_send_button_mode()
            else:
                new_cell.hil_bar.layout.display = 'none'
                if hasattr(new_cell, '_update_send_button_mode'):
                    new_cell._update_send_button_mode()
        except Exception:
            pass
        try:
            display(HTML("\n            <script>\n            window.requestAnimationFrame(()=>{\n              const el = document.scrollingElement || document.documentElement;\n              el.scrollTo({top: el.scrollHeight, behavior: 'smooth'});\n            });\n            </script>\n            "))
        except Exception:
            pass
        return new_cell
    def delete_cell(self, cell: MiniCell):
        if cell in self.cells:
            idx = self.cells.index(cell)
            self.cells.pop(idx)
            self.cells_box.children = tuple([c.widget for c in self.cells])
            self._reindex()
    def set_agent_comments_enabled(self, enabled: bool):
        try:
            self.agent_comments_enabled = bool(enabled)
        except Exception:
            self.agent_comments_enabled = True
    def _update_hil_bars(self):
        try:
            for c in self.cells:
                try:
                    if self._hil_active and (not self._hil_cancelled):
                        c.hil_bar.layout.display = 'flex'
                        c.hil_status.value = "<div style='display:flex;align-items:center;justify-content:center;width:100%;text-align:center'><svg class='epic-ai-logo' width='16' height='16' viewBox='0 0 24 24' aria-label='Working' role='img' xmlns='http://www.w3.org/2000/svg'><circle cx='5' cy='12' r='2' fill='#111'><animate attributeName='opacity' values='0.3;1;0.3' dur='1.2s' repeatCount='indefinite' begin='0s'/></circle><circle cx='12' cy='12' r='2' fill='#111'><animate attributeName='opacity' values='0.3;1;0.3' dur='1.2s' repeatCount='indefinite' begin='0.2s'/></circle><circle cx='19' cy='12' r='2' fill='#111'><animate attributeName='opacity' values='0.3;1;0.3' dur='1.2s' repeatCount='indefinite' begin='0.4s'/></circle></svg></div>"
                        try:
                            c.hil_stop_btn.layout.display = 'inline-flex'
                            c.hil_stop_btn.disabled = False
                        except Exception:
                            pass
                        try:
                            if hasattr(c, '_update_send_button_mode'):
                                c._update_send_button_mode()
                        except Exception:
                            pass
                    elif self._hil_cancelled:
                        c.hil_bar.layout.display = 'flex'
                        c.hil_status.value = "<span style='color:#ef4444'>Canceled</span>"
                        try:
                            c.hil_stop_btn.layout.display = 'none'
                            c.hil_stop_btn.disabled = True
                        except Exception:
                            pass
                        try:
                            if hasattr(c, '_update_send_button_mode'):
                                c._update_send_button_mode()
                        except Exception:
                            pass
                    else:
                        c.hil_bar.layout.display = 'none'
                        try:
                            c.hil_stop_btn.layout.display = 'none'
                            c.hil_stop_btn.disabled = True
                        except Exception:
                            pass
                        try:
                            if hasattr(c, '_update_send_button_mode'):
                                c._update_send_button_mode()
                        except Exception:
                            pass
                except Exception:
                    pass
        except Exception:
            pass
    def start_hil(self):
        try:
            self._hil_cancelled = False
            self._hil_active = True
            self._update_hil_bars()
        except Exception:
            pass
    def cancel_hil(self):
        try:
            self._hil_cancelled = True
            self._hil_active = False
            for c in self.cells:
                try:
                    setattr(c, '_ai_cancel_requested', True)
                except Exception:
                    pass
            self._update_hil_bars()
        except Exception:
            pass
    def _repr_html_(self):
        return ''
    def _repr_mimebundle_(self, include=None, exclude=None):
        return ({}, {})
def run(title: str='SageBow mini-notebook', *, return_instance: bool=False):
    nb = MiniNotebook(title=title)
    box = nb.container
    auth_mgr = get_auth_manager()
    base_url = getattr(auth_mgr, 'api_base_url', os.environ.get('SAGEBOW_API_URL', os.environ.get('EPICAI_API_URL', 'https://sagebow.com'))).rstrip('/')
    status_html = widgets.HTML('')
    open_dashboard_btn = widgets.Button(description='Open Dashboard', tooltip='Get your token', layout=widgets.Layout(height='28px'))
    open_dashboard_btn.add_class('epic-primary-btn')
    enter_token_btn = widgets.Button(description='Enter Token', layout=widgets.Layout(height='28px'))
    enter_token_btn.add_class('epic-secondary-btn')
    token_input = widgets.Password(placeholder='Paste access token', layout=widgets.Layout(width='320px', height='28px'))
    save_token_btn = widgets.Button(description='Verify', layout=widgets.Layout(height='28px'))
    cancel_token_btn = widgets.Button(description='Cancel', layout=widgets.Layout(height='28px'))
    cancel_token_btn.add_class('epic-link-btn')
    token_row = widgets.HBox([token_input, save_token_btn], layout=widgets.Layout(gap='6px', display='none'))
    header_text = widgets.HTML('<b>SageBow requires access token. Enter it below.</b>')
    auth_bar = widgets.HBox([header_text], layout=widgets.Layout(align_items='center', justify_content='flex-start', padding='8px 10px', margin='0 0 8px 0'))
    auth_bar.add_class('epic-auth-bar')
    minimal_auth = widgets.VBox([auth_bar, widgets.HBox([token_input, save_token_btn], layout=widgets.Layout(gap='6px')), status_html], layout=widgets.Layout(gap='8px'))
    top_stack = widgets.VBox([auth_bar, token_row])
    display(HTML("\n    <style>\n    /* Container similar to classic notebook page (transparent to blend) */\n    .epic-container {\n        background: transparent !important;\n        color: #111 !important;\n        padding: 0 0 8px 0 !important;\n        font-family: 'Helvetica Neue', Arial, sans-serif;\n        border: none !important;\n    }\n\n    /* Each cell block */\n    .epic-container .epic-cell {\n        background: #ffffff !important;\n        border: 1px solid #000000 !important; /* clear black border for perfect separation */\n        border-radius: 8px !important;\n        padding: 10px 12px !important;\n        margin: 12px 0 !important;\n        box-shadow: 0 1px 0 rgba(0,0,0,0.02) inset !important; /* subtle depth, optional */\n    }\n    .epic-container .epic-cell:first-child { }\n\n    /* Input row: prompt gutter + editor */\n    .epic-container .epic-prompt { \n        font-family: 'Menlo', 'Consolas', 'Courier New', monospace !important; \n        font-size: 13px !important; \n        color: #303f9f !important; /* blue-ish like classic */\n        min-width: 72px; text-align: right; padding: 2px 8px 0 0; box-sizing: border-box;\n    }\n    .epic-container .epic-prompt-out { color: #d84315 !important; } /* reddish like classic out */\n\n    /* Controls bar similar to toolbar inside input area */\n    .epic-container .epic-controls {\n        border: none !important;\n        padding: 0 0 6px 0 !important;\n        margin: 0 0 4px 0 !important;\n        background: transparent !important;\n    }\n\n    /* Textarea like CodeMirror light */\n    .epic-container .widget-textarea textarea {\n        background: #ffffff !important;\n        color: #111111 !important;\n        border: 1px solid #cfcfcf !important;\n        border-radius: 2px !important;\n        font-family: 'Menlo', 'Consolas', 'Courier New', monospace !important;\n        font-size: 14px !important;\n        line-height: 1.4 !important;\n        caret-color: #111 !important;\n        padding: 8px !important;\n        box-shadow: inset 0 1px 2px rgba(0,0,0,0.05) !important;\n    }\n    .epic-container .widget-textarea textarea:focus {\n        outline: none !important;\n        border-color: #111111 !important; /* neutral dark */\n        box-shadow: 0 0 0 2px rgba(0,0,0,0.25) !important;\n    }\n\n    /* Autonomous AI Agent aesthetic */\n    /* Subtle gradient accents and modern buttons */\n    .epic-container .widget-button {\n        background: linear-gradient(180deg, #f7fafc 0%, #eef2f7 100%) !important;\n        color: #0f172a !important;\n        border: 1px solid #cfd8e3 !important;\n        border-radius: 8px !important;\n        font-size: 12px !important;\n        font-weight: 600 !important;\n        letter-spacing: 0.2px !important;\n        box-shadow: 0 1px 2px rgba(15,23,42,0.06), 0 0 0 0 rgba(14,165,233,0) !important;\n        transition: box-shadow 120ms ease, transform 80ms ease, background 120ms ease, border-color 120ms ease !important;\n    }\n    .epic-container .widget-button:hover {\n        background: linear-gradient(180deg, #ffffff 0%, #f3f6fb 100%) !important;\n        border-color: #94a3b8 !important;\n        box-shadow: 0 2px 6px rgba(15,23,42,0.12) !important;\n    }\n    .epic-container .widget-button:active {\n        transform: translateY(0.5px) !important;\n        box-shadow: 0 1px 2px rgba(15,23,42,0.08) inset !important;\n    }\n    /* Ghost buttons (icon-only) */\n    .epic-container .epic-ghost {\n        background: transparent !important;\n        border: 1px solid transparent !important;\n        border-radius: 8px !important;\n    }\n    .epic-container .epic-ghost:hover {\n        background: rgba(0,0,0,0.05) !important; /* subtle black tint */\n        border-color: rgba(0,0,0,0.20) !important;\n        box-shadow: 0 0 0 2px rgba(0,0,0,0.10) inset !important;\n    }\n\n    /* Send button: white square with black border and black arrow */\n    .epic-container .epic-send-circle {\n        --send-size: 40px;\n        width: var(--send-size) !important;\n        height: var(--send-size) !important;\n        min-width: var(--send-size) !important;\n        padding: 0 !important;\n        border-radius: 2px !important; /* square corners */\n        background: #ffffff !important;\n        color: #0a0a0a !important;\n        border: 2px solid #000000 !important; /* stronger, true black */\n        display: inline-flex !important;\n        align-items: center !important;\n        justify-content: center !important;\n        box-shadow: none !important;\n    }\n    .epic-container .epic-send-circle:hover {\n        background: #f7f7f7 !important;\n        border-color: #000000 !important;\n    }\n    .epic-container .epic-send-circle:disabled {\n        filter: grayscale(0.05) opacity(0.9) !important;\n    }\n    /* Ensure the icon inside is black */\n    .epic-container .epic-send-circle .fa,\n    .epic-container .epic-send-circle .widget-label {\n        color: #0a0a0a !important;\n    }\n\n    /* Stop button in HIL bar: simple square with black border */\n    .epic-container .epic-stop-square {\n        width: 28px !important;\n        height: 28px !important;\n        min-width: 28px !important;\n        padding: 0 !important;\n        border-radius: 2px !important;\n        background: #ffffff !important;\n        color: #0a0a0a !important;\n        border: 2px solid #000000 !important;\n        display: inline-flex !important;\n        align-items: center !important;\n        justify-content: center !important;\n        box-shadow: none !important;\n    }\n    .epic-container .epic-stop-square .fa,\n    .epic-container .epic-stop-square .widget-label {\n        color: #0a0a0a !important;\n    }\n\n    /* AI in-cell chat area */\n    .epic-container .epic-ai-in-cell {\n        background: linear-gradient(180deg, rgba(245,245,245,0.65), rgba(255,255,255,0.9)) !important;\n        border: 1px solid rgba(0,0,0,0.15) !important;\n        border-radius: 10px !important;\n        box-shadow: 0 8px 24px rgba(0,0,0,0.10), 0 1px 0 rgba(255,255,255,0.6) inset !important;\n        position: relative;\n        overflow: hidden;\n    }\n    .epic-container .ai_input textarea {\n        background: #ffffff !important;\n        color: #0f172a !important;\n        border: 1px solid #cfe8f5 !important;\n        border-radius: 8px !important;\n        box-shadow: inset 0 1px 2px rgba(2,132,199,0.10) !important;\n    }\n    .epic-container .ai_input textarea:focus {\n        border-color: #111111 !important;\n        box-shadow: 0 0 0 2px rgba(0,0,0,0.25) !important;\n        outline: none !important;\n    }\n    /* AI action bar */\n    .epic-container .epic-ai-in-cell .widget-hbox {\n        padding: 4px 2px 8px 2px !important;\n    }\n    .epic-container .epic-ai-in-cell .widget-button.info {\n        background: linear-gradient(180deg, #2a2a2a 0%, #111111 100%) !important;\n        color: #ffffff !important;\n        border: 1px solid #0a0a0a !important;\n        box-shadow: 0 6px 16px rgba(0,0,0,0.25) !important;\n    }\n    .epic-container .epic-ai-in-cell .widget-button.info:hover {\n        filter: brightness(1.05) !important;\n    }\n    .epic-container .epic-ai-in-cell .widget-button:disabled {\n        filter: grayscale(0.1) opacity(0.85) !important;\n    }\n\n    /* Buttons styled like minimal classic */\n    .epic-container .widget-button {\n        background: #f5f5f5 !important;\n        color: #111 !important;\n        border: 1px solid #cfcfcf !important;\n        border-radius: 2px !important;\n        font-size: 12px !important;\n        box-shadow: none !important;\n    }\n    .epic-container .widget-button:hover {\n        background: #eaeaea !important;\n        border-color: #bdbdbd !important;\n    }\n    .epic-container .epic-ghost { background: transparent !important; border: none !important; }\n\n    /* Output area */\n    .epic-container .widget-output,\n    .epic-container .output_area,\n    .epic-container .output_subarea {\n        background: #ffffff !important;\n        color: #111111 !important;\n        border: 1px solid #e0e0e0 !important;\n        border-radius: 2px !important;\n        padding: 6px 8px !important;\n        font-family: 'Menlo', 'Consolas', 'Courier New', monospace !important;\n    }\n    .epic-container .output_area pre { background: transparent !important; color: #111 !important; }\n    .epic-container .rendered_html, .epic-container .rendered_text { background: #fff !important; color: #111 !important; }\n    .epic-container table, .epic-container th, .epic-container td { color: #111 !important; border-color: #ddd !important; }\n    .epic-container .dataframe thead th { background: #f8f8f8 !important; }\n\n    /* Export dropdown */\n    /* Use inline positioning for compatibility with VS Code and some Jupyter renderers\n       where absolutely-positioned widget children can be clipped by ancestors. */\n    .epic-container .epic-export-section { position: static; }\n    .epic-container .epic-export-dropdown { \n        background: #ffffff !important; \n        border: 1px solid #e2e8f0 !important; \n        border-radius: 10px !important;\n        box-shadow: 0 12px 28px rgba(15,23,42,0.18) !important;\n        padding: 6px !important;\n        /* Previously absolute with top/right; now inline to avoid clipping */\n        position: static !important;\n        margin-top: 4px !important;\n        z-index: 1;\n    }\n    .epic-container .epic-export-dropdown.open { display: block !important; }\n    .epic-container .epic-export-menu-btn { \n        background: #ffffff !important; \n        color: #0f172a !important; \n        border: 1px solid transparent !important; \n        border-radius: 8px !important;\n        text-align: left !important;\n    }\n    .epic-container .epic-export-menu-btn:hover { \n        background: rgba(0,0,0,0.05) !important; \n        border-color: rgba(0,0,0,0.20) !important; \n    }\n\n    /* Auth bar */\n    .epic-container .epic-auth-bar { \n        background: linear-gradient(180deg, rgba(245,245,245,0.45), rgba(255,255,255,0)) !important; \n        border-bottom: 1px solid #e2e8f0 !important; \n    }\n    .epic-container b { color: #111 !important; }\n\n    /* AI overlay hint */\n    .epic-container .epic-ai-hint-overlay { \n        background: rgba(255,255,255,0.95) !important; \n        color: #0f172a !important; \n        border: 1px solid #e2e8f0 !important; \n        border-radius: 10px !important;\n        box-shadow: 0 10px 24px rgba(0,0,0,0.12) !important;\n    }\n\n    /* Thinking indicator */\n    .epic-container .epic-thinking { color: #111111 !important; }\n    .epic-container .epic-buffer::before, .epic-container .epic-buffer::after { \n        border-top-color: #111111; \n        border-right-color: rgba(0,0,0,0.45); \n    }\n    /* Animated AI logo alignment */\n    .epic-container .epic-ai-logo { margin-left: 6px; vertical-align: middle; }\n    @keyframes epic-buffer-spin { to { transform: rotate(360deg); } }\n\n\n    </style>\n    "))
    saved_token = auth_mgr.get_stored_token()
    init_text = widgets.HTML("""
    <div class='epic-init-wrap' style='display:flex;align-items:center;gap:8px'>
      <span class='epic-thinking-text'>Initializing</span>
      <span class='epic-dots-loading'>
        <span class='dot'></span><span class='dot'></span><span class='dot'></span>
      </span>
      <style>
        .epic-dots-loading .dot{width:6px;height:6px;background:#666;border-radius:50%;display:inline-block;margin-right:4px;animation:epicPulse 1.2s infinite ease-in-out;}
        .epic-dots-loading .dot:nth-child(2){animation-delay:0.2s}
        .epic-dots-loading .dot:nth-child(3){animation-delay:0.4s}
        @keyframes epicPulse{0%,80%,100%{opacity:.3;transform:translateY(0)}40%{opacity:1;transform:translateY(-2px)}}
      </style>
    </div>
    """)
    init_stack = widgets.VBox([init_text])
    def _open_dashboard(_):
        from IPython.display import Javascript
        display(Javascript(f"window.open('{base_url}/dashboard','_blank')"))
    def _show_token_row(_):
        token_row.layout.display = 'flex'
    def _cancel_token_row(_):
        token_input.value = ''
        token_row.layout.display = 'none'
    def _save_token(_):
        tok = (token_input.value or '').strip()
        if not tok:
            status_html.value = "<span style='color:#ffb4b4'>Enter a token.</span>"
            return
        save_token_btn.disabled = True
        status_html.value = """
        <span class='epic-thinking' style='display:inline-flex;align-items:center;gap:8px'>
          <span class='epic-thinking-text'>Validating</span>
          <span class='epic-dots-loading'>
            <span class='dot'></span><span class='dot'></span><span class='dot'></span>
          </span>
          <style>
            .epic-dots-loading .dot{width:6px;height:6px;background:#666;border-radius:50%;display:inline-block;margin-right:4px;animation:epicPulse 1.2s infinite ease-in-out;}
            .epic-dots-loading .dot:nth-child(2){animation-delay:0.2s}
            .epic-dots-loading .dot:nth-child(3){animation-delay:0.4s}
            @keyframes epicPulse{0%,80%,100%{opacity:.3;transform:translateY(0)}40%{opacity:1;transform:translateY(-2px)}}
          </style>
        </span>
        """
        def _validate_and_store():
            ok, data = auth_mgr.validate_token(tok)
            if ok:
                auth_mgr.store_token(tok, data)
                status_html.value = "<span style='color:#b9ffce'>Authenticated.</span>"
                wrapper.children = (box,)
            else:
                status_html.value = "<span style='color:#ffb4b4'>Invalid token.</span>"
            save_token_btn.disabled = False
        threading.Thread(target=_validate_and_store, daemon=True).start()
    open_dashboard_btn.on_click(_open_dashboard)
    enter_token_btn.on_click(_show_token_row)
    cancel_token_btn.on_click(_cancel_token_row)
    save_token_btn.on_click(_save_token)
    wrapper = widgets.VBox([])
    if saved_token:
        wrapper.children = (init_stack,)
        auth_bar.layout.display = 'none'
        token_row.layout.display = 'none'
        def _validate_saved():
            ok, data = auth_mgr.validate_token(saved_token)
            if ok:
                time.sleep(0.4)
                auth_bar.layout.display = 'none'
                token_row.layout.display = 'none'
                wrapper.children = (box,)
            else:
                auth_mgr.clear_token()
                time.sleep(0.1)
                auth_bar.layout.display = 'flex'
                token_row.layout.display = 'none'
                wrapper.children = (minimal_auth,)
        threading.Thread(target=_validate_saved, daemon=True).start()
    else:
        wrapper.children = (minimal_auth,)
    wrapper.add_class('epic-container')
    display(Javascript("""
    (function() {
        console.log("SageBow: Initializing keyboard protection...");
        const EPIC_SCOPE = '.epic-container';
        function isInsideEpicArea(el) {
            if (!el) return false;
            if (el.closest) {
                return Boolean(el.closest(EPIC_SCOPE));
            }
            while (el) {
                if (el.classList && el.classList.contains('epic-container')) {
                    return true;
                }
                el = el.parentElement;
            }
            return false;
        }
        if (!window.__sagebowKeyboardGuard) {
            window.__sagebowKeyboardGuard = true;
            const intercept = (e) => {
                if (!isInsideEpicArea(e.target)) {
                    return;
                }
                e.stopImmediatePropagation();
                e.stopPropagation();
            };
            ['keydown', 'keypress', 'keyup'].forEach(evt => {
                window.addEventListener(evt, intercept, true);
            });
        }
        function protectInput(el) {
            // Forcefully stop event propagation
            const stop = (e) => { e.stopPropagation(); };
            el.removeEventListener('keydown', stop, true);
            el.addEventListener('keydown', stop, true);
            el.removeEventListener('keypress', stop, true);
            el.addEventListener('keypress', stop, true);
            el.removeEventListener('keyup', stop, true);
            el.addEventListener('keyup', stop, true);
            // Explicitly disable Jupyter keyboard manager
            el.addEventListener('focus', function() {
                if (window.Jupyter && window.Jupyter.keyboard_manager) {
                    console.log("SageBow: Disabling Jupyter shortcuts");
                    window.Jupyter.keyboard_manager.disable();
                }
            }, true);
            el.addEventListener('blur', function() {
                if (window.Jupyter && window.Jupyter.keyboard_manager) {
                    console.log("SageBow: Enabling Jupyter shortcuts");
                    window.Jupyter.keyboard_manager.enable();
                }
            }, true);
        }
        function preventJupyterShortcuts() {
            const selectors = [
                '.epic-code-editor textarea', 
                '.ai_input textarea', 
                '.widget-textarea textarea',
                // Fallback for standard widget textareas just in case class is missing
                '.jupyter-widgets textarea' 
            ];
            const inputs = document.querySelectorAll(selectors.join(', '));
            inputs.forEach(el => {
                if (!el.dataset.epicProtected) {
                    protectInput(el);
                    el.dataset.epicProtected = "true";
                }
            });
        }
        // Polling to catch dynamically created or re-rendered widgets
        const checkInterval = setInterval(preventJupyterShortcuts, 800);
        // Initial run
        preventJupyterShortcuts();
    })();
    """))
    display(wrapper)
    if return_instance:
        return nb
    return None