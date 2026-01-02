#!/usr/bin/env python3
"""
CLI entry point for janus-remote

Usage:
    claude-janus                # Start new Claude session with voice paste
    claude-janus --resume       # Resume previous session
    claude-janus -r             # Short form resume
    claude-janus --setup        # Configure VSCode settings for tab title
    claude-janus --setup-claude # Configure Claude Code for voice integration
"""

import sys
import os
import shutil
import json
import random
import subprocess
import re


def print_banner(is_resume=False):
    """Print the sexy Janus terminal banner"""
    print()
    print("  \033[1;38;5;141m█▀▀ █   ▄▀█ █ █ █▀▄ █▀▀\033[0m  \033[38;5;208m+\033[0m  \033[1;38;5;208m  █ ▄▀█ █▄ █ █ █ █▀▀\033[0m  \033[38;5;245m<*>\033[0m")
    print("  \033[1;38;5;141m█▄▄ █▄▄ █▀█ █▄█ █▄▀ ██▄\033[0m     \033[1;38;5;208m█▄█ █▀█ █ ▀█ █▄█ ▄██\033[0m")

    if is_resume:
        print("  \033[38;5;245m────────────────────────────────────────────\033[0m")
        print("  \033[38;5;141m<< Resume Session\033[0m")

    print()


# Session title pool - randomly picked if user skips
SESSION_TITLES = [
    "DeepThroat", "WetSocket", "RawDog", "TightLoop", "HardFork",
    "ThiccStack", "JuicyPipe", "MoistHeap", "GapedAPI", "DripMode",
    "SwollenBuf", "HungThread", "LeakyMem", "StiffPtr", "SloppyIO",
    "EdgeLord", "PoundTown", "CreamPie", "SpitRoast", "BackShot",
    "ThrobBit", "EngorgedQ", "BreedCode", "NakedCall", "RawPush",
    "WideOpen", "SpreadBit", "FullStack", "DeepCopy", "HotSwap",
]

def get_existing_sessions():
    """Get list of existing session titles from running processes"""
    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True, text=True, timeout=5
        )
        titles = set()
        for line in result.stdout.split('\n'):
            if 'JANUS_TITLE=' in line:
                match = re.search(r'JANUS_TITLE=([^ ]+)', line)
                if match:
                    titles.add(match.group(1))
        return titles
    except:
        return set()

def get_session_title():
    """Ask user for optional session title"""
    print("  \033[38;5;245mSession title (Enter to skip): \033[0m", end='', flush=True)
    try:
        title = input().strip()
        if title:
            print(f"  Session: {title}")
            return title

        # Pick a random title that's not already in use
        existing = get_existing_sessions()
        available = [t for t in SESSION_TITLES if t not in existing]
        if not available:
            available = SESSION_TITLES  # All in use, just pick any

        title = random.choice(available)
        print(f"  \033[38;5;208mSession: {title}\033[0m")
        return title
    except (EOFError, KeyboardInterrupt):
        return random.choice(SESSION_TITLES)


def find_claude():
    """Find the claude binary location"""
    # Check PATH first
    claude_path = shutil.which('claude')
    if claude_path:
        return claude_path

    # Common locations
    common_paths = [
        '/usr/local/bin/claude',
        '/opt/homebrew/bin/claude',
        os.path.expanduser('~/.local/bin/claude'),
        os.path.expanduser('~/bin/claude'),
        '/usr/bin/claude',
        os.path.expanduser('~/.npm-global/bin/claude'),
    ]

    for path in common_paths:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path

    return None


def get_vscode_settings_paths():
    """Get possible VSCode settings.json paths for different platforms"""
    home = os.path.expanduser('~')
    paths = []

    # macOS
    paths.append(os.path.join(home, 'Library/Application Support/Code/User/settings.json'))
    paths.append(os.path.join(home, 'Library/Application Support/Code - Insiders/User/settings.json'))
    paths.append(os.path.join(home, 'Library/Application Support/Cursor/User/settings.json'))

    # Linux
    paths.append(os.path.join(home, '.config/Code/User/settings.json'))
    paths.append(os.path.join(home, '.config/Code - Insiders/User/settings.json'))
    paths.append(os.path.join(home, '.config/Cursor/User/settings.json'))

    # WSL / Windows (if running in WSL)
    paths.append(os.path.join(home, '.vscode-server/data/Machine/settings.json'))

    return paths


def setup_vscode_settings(silent=False):
    """Configure VSCode terminal tab settings for Janus title display"""
    required_settings = {
        'terminal.integrated.tabs.title': '${sequence}',
        'terminal.integrated.tabs.description': '${process}'
    }

    paths = get_vscode_settings_paths()
    configured = False

    for settings_path in paths:
        if not os.path.exists(settings_path):
            continue

        try:
            # Read existing settings
            with open(settings_path, 'r') as f:
                content = f.read()
                # Handle empty file
                settings = json.loads(content) if content.strip() else {}

            # Check if already configured
            needs_update = False
            for key, value in required_settings.items():
                if settings.get(key) != value:
                    needs_update = True
                    break

            if not needs_update:
                if not silent:
                    print(f"  \033[38;5;82m+\033[0m VSCode already configured: {settings_path}")
                configured = True
                continue

            # Update settings
            settings.update(required_settings)

            # Write back
            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=4)

            if not silent:
                print(f"  \033[38;5;82m+\033[0m VSCode configured: {settings_path}")
                print(f"    \033[38;5;245mAdded: terminal.integrated.tabs.title = ${{sequence}}\033[0m")
            configured = True

        except (json.JSONDecodeError, PermissionError, OSError) as e:
            if not silent:
                print(f"  \033[38;5;208m⚠\033[0m Could not update {settings_path}: {e}")

    return configured


def get_claude_config_dir():
    """Get Claude Code config directory"""
    return os.path.expanduser('~/.claude')


def get_janus_claude_md_content():
    """Return the CLAUDE.md content for Janus voice integration"""
    return '''# Janus Voice Integration

## Speech Output Format
When responding to voice input from Janus, wrap any text that should be spoken aloud in speech tags:

[SpeechStart]
This text will be spoken aloud by Janus.
[SpeechEnd]

**Important rules:**
- Use speech tags for conversational responses, confirmations, and explanations
- Keep spoken text concise and natural - avoid code blocks, file paths, or technical details in speech
- You can have multiple [SpeechStart]...[SpeechEnd] blocks in one response
- Text outside speech tags will be displayed but not spoken
- For code output, show it normally WITHOUT speech tags

**Example response:**
[SpeechStart]
I've created the new function. Let me explain what it does.
[SpeechEnd]

```python
def hello():
    print("Hello World")
```

[SpeechStart]
The function is ready. Want me to add tests?
[SpeechEnd]
'''


def get_janus_settings_content():
    """Return the settings.json hook configuration for Janus"""
    return {
        "hooks": {
            "UserPromptSubmit": [
                {
                    "matcher": "",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "cat ~/.claude/CLAUDE.md 2>/dev/null | head -50 || true"
                        }
                    ]
                }
            ]
        }
    }


def setup_claude_code(silent=False):
    """Configure Claude Code for Janus voice integration"""
    claude_dir = get_claude_config_dir()
    claude_md_path = os.path.join(claude_dir, 'CLAUDE.md')
    settings_path = os.path.join(claude_dir, 'settings.json')

    # Content to add
    janus_md_content = get_janus_claude_md_content()
    janus_marker = '# Janus Voice Integration'

    changes = []

    # Check what needs to be done
    claude_md_exists = os.path.exists(claude_md_path)
    claude_md_has_janus = False
    if claude_md_exists:
        try:
            with open(claude_md_path, 'r') as f:
                claude_md_has_janus = janus_marker in f.read()
        except:
            pass

    settings_exists = os.path.exists(settings_path)
    settings_has_hook = False
    existing_settings = {}
    if settings_exists:
        try:
            with open(settings_path, 'r') as f:
                existing_settings = json.load(f)
                hooks = existing_settings.get('hooks', {})
                user_prompt_hooks = hooks.get('UserPromptSubmit', [])
                for hook_group in user_prompt_hooks:
                    for hook in hook_group.get('hooks', []):
                        if 'CLAUDE.md' in hook.get('command', ''):
                            settings_has_hook = True
                            break
        except:
            pass

    # Determine what to show user
    if not claude_md_has_janus:
        if claude_md_exists:
            changes.append(('append', claude_md_path, 'Janus voice integration instructions'))
        else:
            changes.append(('create', claude_md_path, 'Janus voice integration instructions'))

    if not settings_has_hook:
        if settings_exists:
            changes.append(('update', settings_path, 'UserPromptSubmit hook to read CLAUDE.md'))
        else:
            changes.append(('create', settings_path, 'UserPromptSubmit hook to read CLAUDE.md'))

    if not changes:
        if not silent:
            print("  \033[38;5;82m+\033[0m Claude Code already configured for Janus")
        return True

    # Show user what will be changed
    print()
    print("  \033[1;38;5;141m[>] Janus Claude Code Integration Setup\033[0m")
    print()
    print("  This will configure Claude Code to work with Janus voice control.")
    print()
    print("  \033[38;5;245mFiles to be modified:\033[0m")
    print("  \033[38;5;245m" + "─" * 50 + "\033[0m")

    for action, path, desc in changes:
        action_color = {'create': '38;5;82', 'append': '38;5;208', 'update': '38;5;208'}[action]
        action_symbol = {'create': '+', 'append': '+', 'update': '~'}[action]
        print(f"  \033[{action_color}m{action_symbol}\033[0m {path}")
        print(f"    \033[38;5;245m{desc}\033[0m")

    print()
    print("  \033[38;5;245mWhat this does:\033[0m")
    print("  • Adds [SpeechStart]...[SpeechEnd] format instructions to CLAUDE.md")
    print("  • Adds hook to remind Claude of these instructions on each message")
    print()

    # Ask for confirmation
    print("  \033[38;5;141mProceed with setup? [y/N]:\033[0m ", end='', flush=True)
    try:
        response = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False

    if response not in ('y', 'yes'):
        print("  \033[38;5;245mSetup cancelled.\033[0m")
        return False

    # Create ~/.claude directory if needed
    os.makedirs(claude_dir, exist_ok=True)

    # Apply changes
    success = True

    # Update CLAUDE.md
    if not claude_md_has_janus:
        try:
            if claude_md_exists:
                with open(claude_md_path, 'a') as f:
                    f.write('\n\n' + janus_md_content)
                print(f"  \033[38;5;82m+\033[0m Appended to {claude_md_path}")
            else:
                with open(claude_md_path, 'w') as f:
                    f.write(janus_md_content)
                print(f"  \033[38;5;82m+\033[0m Created {claude_md_path}")
        except Exception as e:
            print(f"  \033[38;5;196m✗\033[0m Failed to update CLAUDE.md: {e}")
            success = False

    # Update settings.json
    if not settings_has_hook:
        try:
            janus_hooks = get_janus_settings_content()

            if settings_exists:
                # Merge hooks
                if 'hooks' not in existing_settings:
                    existing_settings['hooks'] = {}
                if 'UserPromptSubmit' not in existing_settings['hooks']:
                    existing_settings['hooks']['UserPromptSubmit'] = []
                existing_settings['hooks']['UserPromptSubmit'].extend(janus_hooks['hooks']['UserPromptSubmit'])
            else:
                existing_settings = janus_hooks

            with open(settings_path, 'w') as f:
                json.dump(existing_settings, f, indent=2)

            action = 'Updated' if settings_exists else 'Created'
            print(f"  \033[38;5;82m+\033[0m {action} {settings_path}")
        except Exception as e:
            print(f"  \033[38;5;196m✗\033[0m Failed to update settings.json: {e}")
            success = False

    print()
    if success:
        print("  \033[38;5;82m✓ Claude Code configured for Janus voice integration!\033[0m")

    return success


def check_first_run():
    """Check if this is the first run and offer to setup VSCode"""
    marker_file = os.path.expanduser('~/.janus-remote-configured')

    if os.path.exists(marker_file):
        return  # Already configured

    # Check if any VSCode settings exist (only try on machines with VSCode)
    paths = get_vscode_settings_paths()
    has_vscode = any(os.path.exists(p) for p in paths)

    if not has_vscode:
        # No VSCode on this machine (probably a remote server)
        # Just create marker and skip silently
        try:
            with open(marker_file, 'w') as f:
                f.write('configured-no-vscode')
        except:
            pass
        return

    # First run on machine with VSCode - try to auto-configure
    print("  \033[38;5;141m[>] First run detected - configuring VSCode...\033[0m")
    configured = setup_vscode_settings(silent=False)

    if configured:
        # Create marker file
        try:
            with open(marker_file, 'w') as f:
                f.write('configured')
            print("  \033[38;5;245mReload VSCode window to apply settings\033[0m")
        except:
            pass

    print()


def main():
    """Main entry point"""
    # Parse arguments
    args = sys.argv[1:]
    is_resume = False
    ssh_host_alias = None
    claude_args = []

    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ('--setup', '--configure'):
            # Just setup VSCode and exit
            print()
            print("  \033[38;5;141m[>] Configuring VSCode for Janus...\033[0m")
            print()
            setup_vscode_settings(silent=False)
            print()
            print("  \033[38;5;245mReload VSCode window to apply settings (Cmd+Shift+P → Reload Window)\033[0m")
            print()
            sys.exit(0)
        elif arg in ('--setup-claude', '--configure-claude'):
            # Setup Claude Code integration and exit
            setup_claude_code(silent=False)
            print()
            sys.exit(0)
        elif arg in ('--resume', '-r', 'resume'):
            is_resume = True
            claude_args.append('--resume')
        elif arg == '--host':
            if i + 1 < len(args):
                ssh_host_alias = args[i + 1]
                i += 1
            else:
                print("\033[31mError: --host requires a value\033[0m", file=sys.stderr)
                sys.exit(1)
        elif arg.startswith('--host='):
            ssh_host_alias = arg[7:]
        else:
            claude_args.append(arg)
        i += 1

    # Print sexy banner
    print_banner(is_resume)

    # Check first run and auto-configure VSCode
    check_first_run()

    # Set SSH host alias for bridge matching
    # This should match VSCode's [SSH: xxx] in window title
    if ssh_host_alias:
        os.environ['JANUS_SSH_HOST'] = ssh_host_alias
        print(f"  \033[38;5;245mSSH host alias: \033[38;5;208m{ssh_host_alias}\033[0m")

    # Get optional session title
    title = get_session_title()
    if title:
        os.environ['JANUS_TITLE'] = title
        # Set terminal title
        print(f"\033]0;{title}\007", end='', flush=True)
        print(f"  \033[38;5;245mSession: \033[38;5;141m{title}\033[0m")

    print()

    args = claude_args

    # Find claude
    claude_path = find_claude()

    if not claude_path:
        print("\033[31mError: Could not find 'claude' binary.\033[0m", file=sys.stderr)
        print("Please ensure Claude CLI is installed and in your PATH.", file=sys.stderr)
        print("Install: npm install -g @anthropic-ai/claude-cli", file=sys.stderr)
        sys.exit(1)

    # Import and run the PTY capture
    from .pty_capture import run_claude_session

    try:
        run_claude_session(claude_path, args)
    except KeyboardInterrupt:
        print("\n\033[38;5;245mSession interrupted.\033[0m")
        sys.exit(0)
    except Exception as e:
        print(f"\033[31mError: {e}\033[0m", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
