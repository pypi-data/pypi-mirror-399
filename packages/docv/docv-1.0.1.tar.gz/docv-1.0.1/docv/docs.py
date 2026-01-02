#!/usr/bin/env python3

# File: docs.py - FINAL VERSION with Custom Shortcuts
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-12-29
# Description: Documentation Viewer with Customizable Vim Navigation
# License: MIT

import webview
import sys
import os
import argparse
import json
from pathlib import Path

from .__version__ import version as __version__

try:
    from envdot import load_env  # type: ignore
except:
    print("Error: 'envdot' module not found. Please install it with 'pip install envdot'")
    sys.exit(1)
try:
    from licface import CustomRichHelpFormatter
except:
    CustomRichHelpFormatter = argparse.RawTextHelpFormatter

load_env()

class API:
    def __init__(self):
        self.dark_mode = False
        self._window = None
    
    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        return self.dark_mode
    
    def quit_app(self):
        if self._window:
            self._window.destroy()

def find_html_file(search_path):
    docs_dirs = os.getenv('DOCS_DIR', '').split(',')
    docs_dirs = [d.strip() for d in docs_dirs if d.strip()]
    
    if not docs_dirs:
        print("Error: DOCS_DIR not found in .env")
        sys.exit(1)
    
    if search_path.endswith('.html'):
        for docs_dir in docs_dirs:
            full_path = Path(docs_dir) / search_path
            if full_path.exists():
                return str(full_path.absolute())
    else:
        for docs_dir in docs_dirs:
            full_path = Path(docs_dir) / search_path / 'index.html'
            if full_path.exists():
                return str(full_path.absolute())
    
    return None

def load_shortcuts():
    """Load custom shortcuts from environment variables with defaults"""
    defaults = {
        # Scrolling
        'SCROLL_DOWN': 'j',
        'SCROLL_UP': 'k',
        'SCROLL_LEFT': 'h',
        'SCROLL_RIGHT': 'l',
        'PAGE_DOWN': 'd',
        'PAGE_UP': 'u',
        'TOP': 'gg',
        'BOTTOM': 'G',
        
        # Navigation
        'BACK': 'H',
        'FORWARD': 'L',
        'RELOAD': 'r',
        'QUIT': 'q',
        
        # Links
        'HINTS': 'f',
        'HINTS_NEW_TAB': 'F',
        
        # Actions
        'COPY_URL': 'yy',
        'FOCUS_INPUT': 'gi',
        
        # Settings
        'SCROLL_STEP': '60',
        'HINT_CHARS': 'asdfghjkl',
        'BUFFER_TIMEOUT': '1000',
        'HINT_TIMEOUT': '500',
        'DARK_MODE_TOGGLE': 'D'  # Used with Alt+Shift
    }
    
    config = {}
    for key, default in defaults.items():
        env_key = f'VIM_{key}'
        config[key] = os.getenv(env_key, default)
    
    return config

def get_vim_js(config):
    """Generate Vim JavaScript with custom shortcuts"""
    
    # Separate two-key and single-key commands
    two_key_cmds = {}
    single_key_cmds = {}
    
    for key, shortcut in config.items():
        if key in ['SCROLL_STEP', 'HINT_CHARS', 'BUFFER_TIMEOUT', 'HINT_TIMEOUT', 'DARK_MODE_TOGGLE']:
            continue
        
        if len(shortcut) == 2:
            two_key_cmds[key] = shortcut
        elif len(shortcut) == 1:
            single_key_cmds[key] = shortcut
    
    # Build JavaScript config object
    js_config = {
        'scrollStep': int(config['SCROLL_STEP']),
        'hintChars': config['HINT_CHARS'],
        'bufferTimeout': int(config['BUFFER_TIMEOUT']),
        'hintTimeout': int(config['HINT_TIMEOUT'])
    }
    
    js_shortcuts = {
        'twoKey': {config[k]: k for k in two_key_cmds},
        'singleKey': {config[k]: k for k in single_key_cmds}
    }
    
    return r"""
(function() {
    'use strict';
    
    if (window.__VIMMODE_LOADED) {
        console.log('[Vim] Already loaded');
        return;
    }
    window.__VIMMODE_LOADED = true;
    
    console.log('[Vim] Initializing with custom shortcuts...');
    
    // Configuration from Python
    var cfg = """ + json.dumps(js_config) + r""";
    var shortcuts = """ + json.dumps(js_shortcuts) + r""";
    
    console.log('[Vim] Config:', cfg);
    console.log('[Vim] Shortcuts:', shortcuts);
    
    // State
    var state = {
        buffer: '',
        bufferTimer: null,
        hintMode: false,
        hintBuffer: '',
        hintMarkers: [],
        hintTimeout: null
    };
    
    // Action handlers
    var actions = {
        'TOP': function() { 
            window.scrollTo({ top: 0, behavior: 'smooth' }); 
            msg('⬆️ Top');
        },
        'BOTTOM': function() {
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
            msg('⬇️ Bottom');
        },
        'COPY_URL': function() {
            navigator.clipboard.writeText(location.href)
                .then(function() { msg('📋 Copied: ' + location.href); })
                .catch(function() { msg('❌ Copy failed'); });
        },
        'FOCUS_INPUT': function() {
            var inp = Array.from(document.querySelectorAll('input,textarea'))
                .filter(function(e) { return e.offsetParent && e.type !== 'hidden'; })[0];
            if (inp) { inp.focus(); msg('🔍 Input focused'); }
            else msg('❌ No input');
        },
        'SCROLL_DOWN': function() { scroll(cfg.scrollStep); },
        'SCROLL_UP': function() { scroll(-cfg.scrollStep); },
        'SCROLL_LEFT': function() { window.scrollBy({ left: -cfg.scrollStep, behavior: 'smooth' }); },
        'SCROLL_RIGHT': function() { window.scrollBy({ left: cfg.scrollStep, behavior: 'smooth' }); },
        'PAGE_DOWN': function() { scroll(window.innerHeight / 2); },
        'PAGE_UP': function() { scroll(-window.innerHeight / 2); },
        'BACK': function() { history.back(); msg('⬅️ Back'); },
        'FORWARD': function() { history.forward(); msg('➡️ Forward'); },
        'RELOAD': function() { location.reload(); },
        'HINTS': function() { hintEnter(false); },
        'HINTS_NEW_TAB': function() { hintEnter(true); },
        'QUIT': function() {
            if (typeof pywebview !== 'undefined' && pywebview.api) {
                pywebview.api.quit_app();
            } else {
                msg('❌ Quit unavailable');
            }
        }
    };
    
    // Get start chars for two-key commands
    var startKeys = {};
    for (var k in shortcuts.twoKey) {
        startKeys[k[0]] = true;
    }
    
    // UI
    var bar = document.createElement('div');
    bar.style.cssText = 'position:fixed;bottom:0;left:0;right:0;background:rgba(0,0,0,0.9);color:#fff;padding:8px 12px;font:bold 13px monospace;z-index:2147483647;display:none;border-top:2px solid #4a9eff';
    document.body.appendChild(bar);
    
    var hints = document.createElement('div');
    document.body.appendChild(hints);
    
    function msg(t) {
        bar.textContent = t;
        bar.style.display = 'block';
        setTimeout(function() { bar.style.display = 'none'; }, 1500);
    }
    
    function clearBuf() {
        if (state.bufferTimer) clearTimeout(state.bufferTimer);
        state.buffer = '';
    }
    
    function scroll(y) {
        window.scrollBy({ top: y, behavior: 'smooth' });
    }
    
    // Hint mode
    function hintEnter(newTab) {
        state.hintMode = true;
        state.hintBuffer = '';
        
        var links = Array.from(document.querySelectorAll('a[href],button,[role=button]'))
            .filter(function(el) {
                var r = el.getBoundingClientRect();
                return r.width > 0 && r.height > 0 && r.top >= 0 && r.left >= 0;
            });
        
        state.hintMarkers = [];
        
        links.forEach(function(el, i) {
            var h = '';
            var n = i;
            do {
                h = cfg.hintChars[n % cfg.hintChars.length] + h;
                n = Math.floor(n / cfg.hintChars.length);
            } while (n > 0);
            
            var r = el.getBoundingClientRect();
            var m = document.createElement('div');
            m.textContent = h.toUpperCase();
            m.style.cssText = 'position:fixed;left:' + r.left + 'px;top:' + r.top + 'px;' +
                'background:#ffed00;color:#000;padding:2px 5px;' +
                'font:bold 11px monospace;border:1px solid #000;' +
                'z-index:2147483647;box-shadow:0 2px 4px rgba(0,0,0,0.4)';
            hints.appendChild(m);
            
            state.hintMarkers.push({ el: el, mark: m, hint: h, newTab: newTab });
        });
        
        msg('HINT MODE - Type letters (' + links.length + ' links)');
    }
    
    function hintHandle(key) {
        var k = key.toLowerCase();
        if (state.hintTimeout) clearTimeout(state.hintTimeout);
        
        var test = state.hintBuffer + k;
        var matches = state.hintMarkers.filter(function(h) { 
            return h.hint.indexOf(test) === 0; 
        });
        
        if (matches.length === 0) {
            msg('❌ Invalid: ' + test.toUpperCase());
            return;
        }
        
        state.hintBuffer = test;
        
        var exact = null;
        var longer = false;
        
        state.hintMarkers.forEach(function(h) {
            var match = h.hint.indexOf(state.hintBuffer) === 0;
            if (match) {
                h.mark.style.display = 'block';
                if (h.hint === state.hintBuffer) {
                    h.mark.style.background = '#ff6b6b';
                    h.mark.style.color = '#fff';
                    exact = h;
                } else {
                    h.mark.style.background = '#ffed00';
                    h.mark.style.color = '#000';
                    longer = true;
                }
            } else {
                h.mark.style.display = 'none';
            }
        });
        
        if (exact && !longer) {
            hintActivate(exact);
        } else if (exact && longer) {
            msg('Waiting... [' + state.hintBuffer.toUpperCase() + '] (' + matches.length + ' matches)');
            state.hintTimeout = setTimeout(function() { hintActivate(exact); }, cfg.hintTimeout);
        } else {
            msg('[' + state.hintBuffer.toUpperCase() + '] ' + matches.length + ' matches');
        }
    }
    
    function hintActivate(h) {
        if (h.newTab && h.el.href) {
            window.open(h.el.href, '_blank');
        } else {
            h.el.click();
        }
        hintExit();
    }
    
    function hintExit() {
        state.hintMode = false;
        state.hintBuffer = '';
        if (state.hintTimeout) clearTimeout(state.hintTimeout);
        state.hintMarkers.forEach(function(h) { h.mark.remove(); });
        state.hintMarkers = [];
    }
    
    // Main keydown handler
    document.addEventListener('keydown', function(e) {
        // NEVER intercept modifier combos (allows Ctrl+A/C, etc)
        if (e.ctrlKey || e.metaKey || e.altKey) return;
        
        // Shift+H/L for BACK/FORWARD - check separately
        if (e.shiftKey) {
            var action = shortcuts.singleKey[e.key];
            if (action === 'BACK' || action === 'FORWARD') {
                actions[action]();
                e.preventDefault();
                return;
            }
            // Other Shift combos pass through (for text selection)
            return;
        }
        
        // ESC
        if (e.key === 'Escape') {
            if (state.hintMode) { hintExit(); e.preventDefault(); }
            clearBuf();
            return;
        }
        
        // Hint mode
        if (state.hintMode) {
            if (cfg.hintChars.indexOf(e.key.toLowerCase()) !== -1) {
                hintHandle(e.key);
                e.preventDefault();
            }
            return;
        }
        
        // Skip if in input
        var t = e.target;
        if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable)) return;
        
        // Two-key command completion
        if (state.buffer) {
            var cmd = state.buffer + e.key;
            var action = shortcuts.twoKey[cmd];
            if (action && actions[action]) {
                actions[action]();
                clearBuf();
                e.preventDefault();
                return;
            }
        }
        
        // Start two-key sequence
        if (startKeys[e.key]) {
            state.buffer = e.key;
            state.bufferTimer = setTimeout(clearBuf, cfg.bufferTimeout);
            msg('Buffer: ' + e.key);
            e.preventDefault();
            return;
        }
        
        clearBuf();
        
        // Single-key commands
        var action = shortcuts.singleKey[e.key];
        if (action && actions[action]) {
            actions[action]();
            e.preventDefault();
        }
    });
    
    // Log loaded shortcuts
    console.log('[Vim] ✅ Loaded shortcuts:');
    for (var k in shortcuts.twoKey) {
        console.log('[Vim]   ' + k + ' → ' + shortcuts.twoKey[k]);
    }
    for (var k in shortcuts.singleKey) {
        console.log('[Vim]   ' + k + ' → ' + shortcuts.singleKey[k]);
    }
    
    msg('✅ Vim Ready!');
})();
"""

def print_shortcuts(config):
    """Print current shortcuts configuration"""
    print("\n⌨️  CURRENT VIM SHORTCUTS:")
    print("\n  Scrolling:")
    print(f"    {config['SCROLL_DOWN']:3} - Scroll down")
    print(f"    {config['SCROLL_UP']:3} - Scroll up")
    print(f"    {config['SCROLL_LEFT']:3} - Scroll left")
    print(f"    {config['SCROLL_RIGHT']:3} - Scroll right")
    print(f"    {config['PAGE_DOWN']:3} - Page down")
    print(f"    {config['PAGE_UP']:3} - Page up")
    print(f"    {config['TOP']:3} - Go to top")
    print(f"    {config['BOTTOM']:3} - Go to bottom")
    
    print("\n  Navigation:")
    print(f"    Shift+{config['BACK']:1} - Back")
    print(f"    Shift+{config['FORWARD']:1} - Forward")
    print(f"    {config['RELOAD']:3} - Reload page")
    print(f"    {config['QUIT']:3} - Quit application")
    
    print("\n  Links:")
    print(f"    {config['HINTS']:3} - Show hints (current tab)")
    print(f"    {config['HINTS_NEW_TAB']:3} - Show hints (new tab)")
    
    print("\n  Actions:")
    print(f"    {config['COPY_URL']:3} - Copy current URL")
    print(f"    {config['FOCUS_INPUT']:3} - Focus first input")
    
    print("\n  Other:")
    print(f"    Alt+Shift+{config['DARK_MODE_TOGGLE']} - Toggle dark mode")
    
    print("\n📝 TEXT SELECTION (Always works!):")
    print("    Mouse       - Drag to select")
    print("    Ctrl+A      - Select all")
    print("    Ctrl+C      - Copy")
    print("    Shift+Arrow - Extend selection")
    print("")

def main():
    parser = argparse.ArgumentParser(
        description='Documentation Viewer with Customizable Vim Navigation',
        formatter_class=CustomRichHelpFormatter,
        prog='docs'
    )
    
    parser.add_argument('path', help='Documentation path')
    parser.add_argument('-d', '--debug', action='store_true', help='Debug mode')
    parser.add_argument('-W', '--width', type=int, default=886)
    parser.add_argument('-H', '--height', type=int, default=751)
    parser.add_argument('-X', '--x', type=int, default=413)
    parser.add_argument('-Y', '--y', type=int, default=69)
    parser.add_argument('-nv', '--no-vim', action='store_true', help='Disable Vim mode')
    parser.add_argument('--show-config', action='store_true', help='Show current shortcuts configuration')
    parser.add_argument('-v', '--version', action='version', version=f'docs version {__version__}')
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()
    
    # Load shortcuts configuration
    config = load_shortcuts()
    
    # Show config if requested
    if args.show_config:
        print("\n" + "="*50)
        print("SHORTCUTS CONFIGURATION")
        print("="*50)
        print_shortcuts(config)
        print("\n💡 To customize, add VIM_* variables to your .env file")
        print("   Example: VIM_SCROLL_DOWN=s")
        print("   See README.md for all options")
        print("")
        sys.exit(0)
    
    if not args.path:
        print("Error: path argument required")
        parser.print_help()
        sys.exit(1)
    
    html_file = find_html_file(args.path)
    if not html_file:
        print(f"❌ Not found: '{args.path}'")
        sys.exit(1)
    
    print(f"📄 Loading: {html_file}")
    
    if not args.no_vim:
        print_shortcuts(config)
    
    api = API()
    window = webview.create_window(
        'Documentation Viewer',
        html_file,
        width=args.width,
        height=args.height,
        x=args.x,
        y=args.y,
        js_api=api
    )
    api._window = window  # type: ignore
    
    def on_loaded():
        # Force enable text selection and right-click
        window.evaluate_js("""
            (function() {
                document.addEventListener('selectstart', function(e) { e.stopPropagation(); }, true);
                document.addEventListener('contextmenu', function(e) { e.stopPropagation(); }, true);
                var s = document.createElement('style');
                s.textContent = '*{-webkit-user-select:text!important;user-select:text!important}';
                document.head.appendChild(s);
                console.log('[Selection] ✅ Enabled');
            })();
        """)
        
        # Dark mode toggle
        dark_key = config['DARK_MODE_TOGGLE']
        if not hasattr(on_loaded, 'dark_init'):
            window.evaluate_js(f"""
                (function() {{
                    var dark = false;
                    document.addEventListener('keydown', function(e) {{
                        if (e.altKey && e.shiftKey && e.key === '{dark_key}') {{
                            dark = !dark;
                            document.body.style.filter = dark ? 'invert(1) hue-rotate(180deg)' : '';
                            e.preventDefault();
                        }}
                    }});
                }})();
            """)
            on_loaded.dark_init = True  # type: ignore
        
        # Vim mode
        if not args.no_vim:
            window.evaluate_js(get_vim_js(config))
    
    window.events.loaded += on_loaded
    webview.start(debug=args.debug)

if __name__ == '__main__':
    main()