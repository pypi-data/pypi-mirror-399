"""
SpeedLogger - Fast Colored Logging Module
Version: 6.1.0
License: MIT License
Copyright (c) 2024 SpeedLogger Team
"""

import sys
import time
import os
import re
from datetime import datetime
from typing import Optional, Any, List, Dict, Union, Callable
import getpass
import threading
from collections import deque

# ==================== COLORS ====================
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Symbol colors
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    
    # Pure red gradient colors
    RED_1 = '\033[38;5;196m'  # Bright red
    RED_2 = '\033[38;5;160m'  # Medium red
    RED_3 = '\033[38;5;124m'  # Dark red
    RED_4 = '\033[38;5;88m'   # Very dark red

class SpeedLogger:
    def __init__(self, show_time: bool = True, centered: bool = False):
        self.show_time = show_time
        self.centered = centered
        self._screen_width = self._get_terminal_width()
        self._log_count = 0
        self._rate_limit = 0  # 0 means no rate limit
        self._rate_limit_queue = deque()
        self._lock = threading.Lock()
        
    def _get_terminal_width(self) -> int:
        try:
            return os.get_terminal_size().columns
        except:
            return 80
    
    def _clean_ansi(self, text: str) -> str:
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def _visible_length(self, text: str) -> int:
        return len(self._clean_ansi(text))
    
    def _apply_red_gradient(self, text: str) -> str:
        """Apply enhanced red gradient to text"""
        if not text:
            return ""
        
        result = []
        colors = [Colors.RED_1, Colors.RED_2, Colors.RED_3, Colors.RED_4]
        text_len = len(text)
        
        # Enhanced gradient based on position
        for i, char in enumerate(text):
            if text_len <= 4:
                color_idx = i % len(colors)
            else:
                # Smooth gradient across text
                color_idx = int((i / (text_len - 1)) * (len(colors) - 1)) if text_len > 1 else 0
            result.append(f"{colors[color_idx]}{char}")
        
        return ''.join(result) + Colors.RESET
    
    def _format_time(self) -> str:
        return datetime.now().strftime("%H:%M:%S")
    
    def _center_text(self, text: str) -> str:
        """Center text based on screen width"""
        visible_len = self._visible_length(text)
        padding = max(0, (self._screen_width - visible_len) // 2)
        return ' ' * padding + text
    
    def _print_line(self, text: str):
        """Print line with centering option"""
        if self.centered:
            print(self._center_text(text))
        else:
            print(text)
    
    def _check_rate_limit(self) -> bool:
        """Check if rate limit is exceeded"""
        if self._rate_limit <= 0:
            return True
            
        current_time = time.time()
        with self._lock:
            # Remove old entries
            while self._rate_limit_queue and current_time - self._rate_limit_queue[0] > 1.0:
                self._rate_limit_queue.popleft()
            
            # Check if we can add new entry
            if len(self._rate_limit_queue) < self._rate_limit:
                self._rate_limit_queue.append(current_time)
                return True
            return False
    
    def _log(self, prefix: str, symbol: str, symbol_color: str, message: str):
        """Core logging method - NEW FORMAT with more spacing"""
        # Check rate limit
        if not self._check_rate_limit():
            return
            
        self._log_count += 1
        
        # Build line: [SYMBOL]   [TIME]   [PREFIX]   |   message
        time_part = f"{Colors.CYAN}[{self._format_time()}]{Colors.RESET}" if self.show_time else ""
        prefix_part = self._apply_red_gradient(f"[{prefix}]") if prefix else ""
        symbol_part = f"{symbol_color}{symbol}{Colors.RESET}"
        
        # Create parts with spacing
        parts = []
        parts.append(symbol_part + "   ")
        
        if time_part:
            parts.append(time_part + "   ")
        
        if prefix_part:
            parts.append(prefix_part + "   ")
        
        # Apply red gradient to message
        msg_part = self._apply_red_gradient(message)
        
        # Join parts and add separator
        full_line = ''.join(parts) + f"|   {msg_part}"
        self._print_line(full_line)
    
    # ==================== CORE LOGGING METHODS ====================
    
    def info(self, prefix: str, message: str):
        self._log(prefix.upper(), "[+]", Colors.CYAN, message)
    
    def success(self, prefix: str, message: str):
        self._log(prefix.upper(), "[✓]", Colors.GREEN, message)
    
    def warning(self, prefix: str, message: str):
        self._log(prefix.upper(), "[!]", Colors.YELLOW, message)
    
    def error(self, prefix: str, message: str):
        self._log(prefix.upper(), "[X]", Colors.RED, message)
    
    def debug(self, prefix: str, message: str):
        self._log(prefix.upper(), "[*]", Colors.BLUE, message)
    
    def critical(self, prefix: str, message: str):
        self._log(prefix.upper(), "[!]", Colors.RED + Colors.BOLD, message)
    
    # ==================== CUSTOM LOG TYPES ====================
    
    def boost(self, prefix: str, message: str):
        """Boost log type"""
        self._log(prefix.upper(), "[⚡]", Colors.YELLOW, message)
    
    def join(self, prefix: str, message: str):
        """Join log type"""
        self._log(prefix.upper(), "[+]", Colors.GREEN, message)
    
    def leave(self, prefix: str, message: str):
        """Leave log type"""
        self._log(prefix.upper(), "[-]", Colors.RED, message)
    
    def update(self, prefix: str, message: str):
        """Update log type"""
        self._log(prefix.upper(), "[↻]", Colors.CYAN, message)
    
    def security(self, prefix: str, message: str):
        """Security log type"""
        self._log(prefix.upper(), "[🔒]", Colors.MAGENTA, message)
    
    def network(self, prefix: str, message: str):
        """Network log type"""
        self._log(prefix.upper(), "[🌐]", Colors.BLUE, message)
    
    def thanks(self, prefix: str, message: str):
        """Thanks log type"""
        self._log(prefix.upper(), "[🎉]", Colors.YELLOW, message)
    
    def money(self, prefix: str, message: str):
        """Money log type"""
        self._log(prefix.upper(), "[💰]", Colors.GREEN, message)
    
    def system(self, prefix: str, message: str):
        """System log type"""
        self._log(prefix.upper(), "[⚙]", Colors.CYAN, message)
    
    def user(self, prefix: str, message: str):
        """User log type"""
        self._log(prefix.upper(), "[👤]", Colors.MAGENTA, message)
    
    def status(self, prefix: str, message: str):
        """Status log type"""
        self._log(prefix.upper(), "[●]", Colors.BLUE, message)
    
    def alert(self, prefix: str, message: str):
        """Alert log type"""
        self._log(prefix.upper(), "[!]", Colors.RED, message)
    
    def notify(self, prefix: str, message: str):
        """Notify log type"""
        self._log(prefix.upper(), "[🔔]", Colors.YELLOW, message)
    
    def custom(self, prefix: str, symbol: str, color: str, message: str):
        """Fully custom log"""
        self._log(prefix.upper(), symbol, color, message)
    
    # ==================== SIMPLE LOGS (legacy support) ====================
    
    def simple_info(self, message: str):
        self._log("INFO", "[+]", Colors.CYAN, message)
    
    def simple_success(self, message: str):
        self._log("SUCCESS", "[✓]", Colors.GREEN, message)
    
    def simple_error(self, message: str):
        self._log("ERROR", "[X]", Colors.RED, message)
    
    def simple_warning(self, message: str):
        self._log("WARNING", "[!]", Colors.YELLOW, message)
    
    def simple_debug(self, message: str):
        self._log("DEBUG", "[*]", Colors.BLUE, message)
    
    def simple_critical(self, message: str):
        self._log("CRITICAL", "[!]", Colors.RED + Colors.BOLD, message)
    
    # ==================== INPUT METHODS ====================
    
    def inp(self, prompt: str) -> str:
        """Simple one-line input: [?]   [TIME]   prompt > """
        # Apply rate limit check for input prompt
        if not self._check_rate_limit():
            return ""
            
        time_part = f"{Colors.CYAN}[{self._format_time()}]{Colors.RESET}" if self.show_time else ""
        
        # Build prompt line: [?]   [TIME]   prompt >
        prompt_text = f"{Colors.MAGENTA}[?]{Colors.RESET}   "
        if time_part:
            prompt_text += f"{time_part}   "
            
        prompt_text += f"{self._apply_red_gradient(prompt)}   {Colors.CYAN}> {Colors.RESET}"
        
        if self.centered:
            centered_prompt = self._center_text(prompt_text)
            return input(centered_prompt)
        else:
            return input(prompt_text)
    
    def password(self, prompt: str = "Password") -> str:
        """Password input: [?]   [TIME]   prompt > """
        if not self._check_rate_limit():
            return ""
            
        time_part = f"{Colors.CYAN}[{self._format_time()}]{Colors.RESET}" if self.show_time else ""
        
        prompt_text = f"{Colors.MAGENTA}[?]{Colors.RESET}   "
        if time_part:
            prompt_text += f"{time_part}   "
            
        prompt_text += f"{self._apply_red_gradient(prompt)}   {Colors.CYAN}> {Colors.RESET}"
        
        if self.centered:
            centered_prompt = self._center_text(prompt_text)
            print(centered_prompt, end='', flush=True)
        else:
            print(prompt_text, end='', flush=True)
        
        # Get password
        try:
            import msvcrt
            password_chars = []
            
            while True:
                char = msvcrt.getch()
                
                # Enter key
                if char in [b'\r', b'\n']:
                    print()
                    break
                
                # Backspace
                elif char == b'\x08':
                    if password_chars:
                        password_chars.pop()
                        print('\b \b', end='', flush=True)
                
                # Printable characters
                elif 32 <= ord(char) <= 126:
                    password_chars.append(char.decode('utf-8'))
                    print('*', end='', flush=True)
            
            return ''.join(password_chars)
            
        except (ImportError, Exception):
            # Fallback
            return getpass.getpass('')
    
    def confirm(self, question: str) -> bool:
        """Confirmation: [$]   [TIME]   question > """
        if not self._check_rate_limit():
            return False
            
        time_part = f"{Colors.CYAN}[{self._format_time()}]{Colors.RESET}" if self.show_time else ""
        
        prompt_text = f"{Colors.YELLOW}[$]{Colors.RESET}   "
        if time_part:
            prompt_text += f"{time_part}   "
            
        prompt_text += f"{self._apply_red_gradient(question)}   {Colors.CYAN}> {Colors.RESET}"
        
        if self.centered:
            centered_prompt = self._center_text(prompt_text)
            response = input(centered_prompt).lower()
        else:
            response = input(prompt_text).lower()
        
        return response in ['y', 'yes', '1']
    
    def choice(self, prompt: str, options: List[str]) -> int:
        """Multiple choice input"""
        if not self._check_rate_limit():
            return 0
            
        # Show prompt
        time_part = f"{Colors.CYAN}[{self._format_time()}]{Colors.RESET}" if self.show_time else ""
        
        prompt_text = f"{Colors.MAGENTA}[?]{Colors.RESET}   "
        if time_part:
            prompt_text += f"{time_part}   "
            
        prompt_text += f"{self._apply_red_gradient(prompt)}"
        self._print_line(prompt_text)
        
        # Show options
        for i, option in enumerate(options, 1):
            option_line = f"   {Colors.CYAN}{i}.{Colors.RESET}   {self._apply_red_gradient(option)}"
            self._print_line(option_line)
        
        # Get choice
        while True:
            try:
                choice_prompt = f"{Colors.CYAN}> {Colors.RESET}"
                if self.centered:
                    centered_choice = self._center_text(choice_prompt)
                    choice = input(centered_choice)
                else:
                    choice = input(choice_prompt)
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(options):
                    return choice_num - 1
                else:
                    self.simple_error(f"Enter 1-{len(options)}")
            except ValueError:
                self.simple_error("Enter a valid number")
    
    # ==================== UTILITIES ====================
    
    def separator(self, length: int = 50, char: str = "-"):
        """Simple separator"""
        if not self._check_rate_limit():
            return
            
        line = char * length
        time_part = f"{Colors.CYAN}[{self._format_time()}]{Colors.RESET}" if self.show_time else ""
        
        sep_line = f"{Colors.GRAY}[~]{Colors.RESET}   "
        if time_part:
            sep_line += f"{time_part}   "
        sep_line += f"{self._apply_red_gradient(line)}"
        
        self._print_line(sep_line)
    
    def title(self, text: str):
        """Title with separator"""
        border = "=" * (len(text) + 6)
        self.separator(len(border), "=")
        
        time_part = f"{Colors.CYAN}[{self._format_time()}]{Colors.RESET}" if self.show_time else ""
        
        title_line = f"{Colors.CYAN}[#]{Colors.RESET}   "
        if time_part:
            title_line += f"{time_part}   "
        title_line += f"{self._apply_red_gradient(text.upper())}"
        
        self._print_line(title_line)
        self.separator(len(border), "=")
    
    def section(self, text: str):
        """Section header"""
        self.separator(len(text) + 6, "-")
        self.simple_info(text)
        self.separator(len(text) + 6, "-")
    
    # ==================== VISUALIZATIONS ====================
    
    def progress_bar(self, current: int, total: int, length: int = 40):
        """Simple progress bar"""
        if not self._check_rate_limit():
            return
            
        percent = current / total
        filled = int(length * percent)
        
        # Simple bar
        bar = Colors.RED_1 + "█" * filled + Colors.RESET + Colors.GRAY + "░" * (length - filled) + Colors.RESET
        percent_text = f"{percent*100:6.1f}%"
        
        # Build line
        time_part = f"{Colors.CYAN}[{self._format_time()}]{Colors.RESET}" if self.show_time else ""
        
        symbol = Colors.CYAN + "[▷]" + Colors.RESET
        prefix = self._apply_red_gradient("[PROGRESS]")
        text = f"{bar}   {self._apply_red_gradient(percent_text)}   ({current}/{total})"
        
        line = f"{symbol}   "
        if time_part:
            line += f"{time_part}   "
        line += f"{prefix}   |   {text}"
        
        if self.centered:
            print(self._center_text(line), end='\r')
        else:
            print(line, end='\r')
        
        if current == total:
            print()
            self.success("PROGRESS", "Complete!")
    
    def loading(self, message: str = "Loading", duration: float = 2.0):
        """Loading animation"""
        frames = [">   ", " >  ", "  > ", "   >", "  > ", " >  ", ">   "]
        start_time = time.time()
        
        while time.time() - start_time < duration:
            if not self._check_rate_limit():
                time.sleep(0.1)
                continue
                
            elapsed = time.time() - start_time
            frame_idx = int(elapsed * 4) % len(frames)
            
            time_part = f"{Colors.CYAN}[{self._format_time()}]{Colors.RESET}" if self.show_time else ""
            symbol = Colors.CYAN + "[" + frames[frame_idx] + "]" + Colors.RESET
            prefix = self._apply_red_gradient("[LOADING]")
            
            line = f"{symbol}   "
            if time_part:
                line += f"{time_part}   "
            line += f"{prefix}   |   {self._apply_red_gradient(message)}"
            
            if self.centered:
                print(self._center_text(line), end='\r')
            else:
                print(line, end='\r')
            
            time.sleep(0.1)
        
        print(' ' * self._screen_width, end='\r')
        self.success("LOADING", f"{message} complete")
    
    def countdown(self, seconds: int, message: str = "Starting"):
        """Countdown timer"""
        # Temporarily disable centering for countdown
        original_centered = self.centered
        self.centered = False
        
        for i in range(seconds, 0, -1):
            if not self._check_rate_limit():
                time.sleep(1)
                continue
                
            time_part = f"{Colors.CYAN}[{self._format_time()}]{Colors.RESET}" if self.show_time else ""
            
            # Choose symbol and color based on time
            if i <= 3:
                symbol = Colors.RED + "[!]" + Colors.RESET
            elif i <= 6:
                symbol = Colors.YELLOW + "[!]" + Colors.RESET
            else:
                symbol = Colors.CYAN + "[@]" + Colors.RESET
            
            prefix = self._apply_red_gradient("[COUNTDOWN]")
            text = f"{message} in {i}s"
            
            line = f"{symbol}   "
            if time_part:
                line += f"{time_part}   "
            line += f"{prefix}   |   {self._apply_red_gradient(text)}"
            
            # Clear line and print
            sys.stdout.write('\r' + ' ' * self._screen_width + '\r')
            sys.stdout.write(line)
            sys.stdout.flush()
            
            time.sleep(1)
        
        # Restore centering
        self.centered = original_centered
        
        # Clear and show completion
        sys.stdout.write('\r' + ' ' * self._screen_width + '\r')
        self.success("COUNTDOWN", f"{message} ready!")
    
    def spinner(self, message: str = "Processing", duration: float = 2.0):
        """Simple spinner"""
        frames = [">   ", " >  ", "  > ", "   >"]
        start_time = time.time()
        
        while time.time() - start_time < duration:
            if not self._check_rate_limit():
                time.sleep(0.1)
                continue
                
            elapsed = time.time() - start_time
            frame_idx = int(elapsed * 4) % len(frames)
            
            time_part = f"{Colors.CYAN}[{self._format_time()}]{Colors.RESET}" if self.show_time else ""
            symbol = Colors.CYAN + "[" + frames[frame_idx] + "]" + Colors.RESET
            prefix = self._apply_red_gradient("[PROCESSING]")
            
            line = f"{symbol}   "
            if time_part:
                line += f"{time_part}   "
            line += f"{prefix}   |   {self._apply_red_gradient(message)}"
            
            if self.centered:
                print(self._center_text(line), end='\r')
            else:
                print(line, end='\r')
            
            time.sleep(0.1)
        
        print(' ' * self._screen_width, end='\r')
    
    # ==================== DATA DISPLAY ====================
    
    def table(self, data: List[List[Any]], headers: Optional[List[str]] = None):
        """Simple table"""
        if not data:
            return
            
        if not self._check_rate_limit():
            return
        
        # Calculate column widths
        all_rows = data.copy()
        if headers:
            all_rows.insert(0, headers)
        
        col_count = len(all_rows[0])
        col_widths = [0] * col_count
        
        for row in all_rows:
            for i, cell in enumerate(row):
                visible_len = len(str(cell))
                col_widths[i] = max(col_widths[i], visible_len)
        
        # Display table
        if headers:
            # Headers
            header_parts = []
            for i, header in enumerate(headers):
                header_text = f"{Colors.BOLD}{self._apply_red_gradient(header)}{Colors.RESET}"
                header_parts.append(f"{header_text:<{col_widths[i] + 2}}")  # +2 for extra spacing
            
            header_line = "   |   ".join(header_parts)
            
            if self.centered:
                print(self._center_text(header_line))
                # Separator
                sep_parts = []
                for width in col_widths:
                    sep_parts.append("-" * (width + 2))
                sep_line = "---|--".join(sep_parts)
                print(self._center_text(sep_line))
            else:
                print(header_line)
                sep_parts = []
                for width in col_widths:
                    sep_parts.append("-" * (width + 2))
                print("---|--".join(sep_parts))
        
        # Data rows
        for row in data:
            row_parts = []
            for i, cell in enumerate(row):
                row_parts.append(f"{self._apply_red_gradient(str(cell)):<{col_widths[i] + 2}}")
            
            row_line = "   |   ".join(row_parts)
            
            if self.centered:
                print(self._center_text(row_line))
            else:
                print(row_line)
    
    def list_items(self, items: List[str], title: Optional[str] = None):
        """Display list of items"""
        if not self._check_rate_limit():
            return
            
        if title:
            time_part = f"{Colors.CYAN}[{self._format_time()}]{Colors.RESET}" if self.show_time else ""
            title_line = f"{Colors.CYAN}[•]{Colors.RESET}   "
            if time_part:
                title_line += f"{time_part}   "
            title_line += f"{self._apply_red_gradient(title)}"
            self._print_line(title_line)
        
        for item in items:
            if not self._check_rate_limit():
                continue
                
            time_part = f"{Colors.CYAN}[{self._format_time()}]{Colors.RESET}" if self.show_time else ""
            item_line = f"{Colors.CYAN}[>]{Colors.RESET}   "
            if time_part:
                item_line += f"{time_part}   "
            item_line += f"{self._apply_red_gradient(item)}"
            self._print_line(item_line)
    
    def key_value(self, data: Dict[str, Any], title: Optional[str] = None):
        """Display key-value pairs"""
        if not self._check_rate_limit():
            return
            
        if title:
            self.section(title)
        
        max_key_len = max(len(str(k)) for k in data.keys())
        
        for key, value in data.items():
            if not self._check_rate_limit():
                continue
                
            time_part = f"{Colors.CYAN}[{self._format_time()}]{Colors.RESET}" if self.show_time else ""
            key_part = f"{Colors.CYAN}[{key}]{Colors.RESET}"
            line = f"{Colors.CYAN}[>]{Colors.RESET}   "
            if time_part:
                line += f"{time_part}   "
            line += f"{key_part:<{max_key_len + 4}}   |   {self._apply_red_gradient(str(value))}"
            
            if self.centered:
                print(self._center_text(line))
            else:
                print(line)
    
    # ==================== CONFIGURATION ====================
    
    def set_centered(self, centered: bool):
        """Set centered mode"""
        self.centered = centered
    
    def set_show_time(self, show_time: bool):
        """Set time display"""
        self.show_time = show_time
    
    def set_rate_limit(self, limit: int):
        """Set rate limit (logs per second, 0 = no limit)"""
        self._rate_limit = max(0, limit)
    
    def reset_count(self):
        """Reset log counter"""
        self._log_count = 0
    
    def get_log_count(self):
        """Get total log count"""
        return self._log_count

# ==================== GLOBAL INSTANCE ====================
logger = SpeedLogger()

# ==================== GLOBAL FUNCTIONS ====================

# Configuration
def set_centered(centered: bool):
    logger.set_centered(centered)

def set_show_time(show_time: bool):
    logger.set_show_time(show_time)

def set_rate_limit(limit: int):
    logger.set_rate_limit(limit)

def reset_count():
    logger.reset_count()

def get_log_count():
    return logger.get_log_count()

# Core logging (new format with prefix)
def info(prefix: str, message: str):
    logger.info(prefix, message)

def success(prefix: str, message: str):
    logger.success(prefix, message)

def warning(prefix: str, message: str):
    logger.warning(prefix, message)

def error(prefix: str, message: str):
    logger.error(prefix, message)

def debug(prefix: str, message: str):
    logger.debug(prefix, message)

def critical(prefix: str, message: str):
    logger.critical(prefix, message)

# Custom log types
def boost(prefix: str, message: str):
    logger.boost(prefix, message)

def join(prefix: str, message: str):
    logger.join(prefix, message)

def leave(prefix: str, message: str):
    logger.leave(prefix, message)

def update(prefix: str, message: str):
    logger.update(prefix, message)

def security(prefix: str, message: str):
    logger.security(prefix, message)

def network(prefix: str, message: str):
    logger.network(prefix, message)

def thanks(prefix: str, message: str):
    logger.thanks(prefix, message)

def money(prefix: str, message: str):
    logger.money(prefix, message)

def system(prefix: str, message: str):
    logger.system(prefix, message)

def user(prefix: str, message: str):
    logger.user(prefix, message)

def status(prefix: str, message: str):
    logger.status(prefix, message)

def alert(prefix: str, message: str):
    logger.alert(prefix, message)

def notify(prefix: str, message: str):
    logger.notify(prefix, message)

def custom(prefix: str, symbol: str, color: str, message: str):
    logger.custom(prefix, symbol, color, message)

# Simple logs (legacy format)
def simple_info(message: str):
    logger.simple_info(message)

def simple_success(message: str):
    logger.simple_success(message)

def simple_error(message: str):
    logger.simple_error(message)

def simple_warning(message: str):
    logger.simple_warning(message)

def simple_debug(message: str):
    logger.simple_debug(message)

def simple_critical(message: str):
    logger.simple_critical(message)

# Input methods
def inp(prompt: str) -> str:
    return logger.inp(prompt)

def password(prompt: str = "Password") -> str:
    return logger.password(prompt)

def confirm(question: str) -> bool:
    return logger.confirm(question)

def choice(prompt: str, options: List[str]) -> int:
    return logger.choice(prompt, options)

# Utilities
def separator(length: int = 50, char: str = "-"):
    logger.separator(length, char)

def title(text: str):
    logger.title(text)

def section(text: str):
    logger.section(text)

# Visualizations
def progress_bar(current: int, total: int, length: int = 40):
    logger.progress_bar(current, total, length)

def loading(message: str = "Loading", duration: float = 2.0):
    logger.loading(message, duration)

def countdown(seconds: int, message: str = "Starting"):
    logger.countdown(seconds, message)

def spinner(message: str = "Processing", duration: float = 2.0):
    logger.spinner(message, duration)

# Data display
def table(data: List[List[Any]], headers: Optional[List[str]] = None):
    logger.table(data, headers)

def list_items(items: List[str], title: Optional[str] = None):
    logger.list_items(items, title)

def key_value(data: Dict[str, Any], title: Optional[str] = None):
    logger.key_value(data, title)

# Gradient utility
def red_gradient(text: str) -> str:
    return logger._apply_red_gradient(text)

# ==================== SHOWCASE ====================
if __name__ == "__main__":
    # Show banner
    print(red_gradient("=" * 70))
    print(red_gradient("SPEEDLOGGER v6.1.0 - ENHANCED WITH SPACING"))
    print(red_gradient("=" * 70))
    print()
    
    # Title with normal mode
    title("SHOWCASE - NORMAL MODE")
    
    # All log types with more spacing
    section("LOG TYPES WITH SPACING")
    
    # Core logs with prefixes
    info("SYSTEM", "Initializing server components")
    success("AUTH", "User login successful")
    warning("MEMORY", "High memory usage detected: 85%")
    error("DATABASE", "Connection failed to MySQL server")
    debug("SESSION", "User ID: 12345, Session: ABC123XYZ")
    critical("SYSTEM", "Server crash imminent - emergency shutdown")
    
    # Custom logs with prefixes
    boost("SERVER", "Boosted performance by 200%")
    join("USER", "JohnDoe joined the server")
    leave("USER", "JaneSmith left the server")
    update("SYSTEM", "Applying security patches v2.5")
    security("FIREWALL", "Blocked suspicious IP: 192.168.1.100")
    network("CONNECTION", "Established secure VPN tunnel")
    thanks("COMMUNITY", "Thank you for using our service!")
    money("PAYMENT", "Received $50.00 from user Premium123")
    system("BACKUP", "Completed daily backup to cloud storage")
    user("PROFILE", "Updated profile picture and settings")
    status("MONITOR", "All systems operational and green")
    alert("SECURITY", "Multiple failed login attempts detected")
    notify("UPDATE", "New version available: v6.1.0")
    
    separator()
    
    # Input examples
    section("INPUT EXAMPLES")
    
    # Simple input
    username = inp("Enter your username")
    success("AUTH", f"User {username} authenticated successfully")
    
    # Password
    passwd = password("Enter your secure password")
    success("SECURITY", "Password validated successfully")
    
    # Confirmation
    if confirm("Do you want to enable 2-factor authentication?"):
        success("SECURITY", "2FA enabled for account protection")
    else:
        info("SECURITY", "2FA remains disabled")
    
    # Choice
    themes = ["Dark Mode", "Light Mode", "Blue Theme", "Red Theme", "Custom"]
    theme_idx = choice("Select interface theme", themes)
    system("SETTINGS", f"Theme changed to: {themes[theme_idx]}")
    
    separator()
    
    # Switch to centered mode
    set_centered(True)
    title("SHOWCASE - CENTERED MODE")
    
    # Visualizations in centered mode
    section("VISUALIZATIONS")
    
    # Progress bar
    info("UPLOAD", "Uploading files to cloud storage...")
    for i in range(1, 101):
        progress_bar(i, 100)
        time.sleep(0.02)
    
    # Countdown
    info("LAUNCH", "Preparing system launch...")
    countdown(5, "System launch")
    
    # Loading
    info("ANALYSIS", "Analyzing system logs...")
    loading("Processing data", 1.5)
    
    separator()
    
    # Data display in centered mode
    section("DATA DISPLAY")
    
    # Table
    info("STATS", "Server Statistics Overview")
    server_stats = [
        ["Web Server", "Apache", "Running", "95%", "24/7"],
        ["Database", "MySQL", "Running", "87%", "24/7"],
        ["Cache", "Redis", "Running", "45%", "24/7"],
        ["Load Balancer", "Nginx", "Running", "72%", "24/7"],
        ["Monitoring", "Prometheus", "Running", "31%", "24/7"]
    ]
    headers = ["Service", "Type", "Status", "CPU Usage", "Uptime"]
    table(server_stats, headers)
    
    print()
    
    # Key-Value
    info("SYSTEM INFO", "Detailed System Information")
    system_info = {
        "OS Version": "Windows Server 2022",
        "CPU Model": "Intel Xeon E5-2690",
        "RAM Total": "128GB DDR4",
        "Storage": "2TB NVMe SSD",
        "Network": "10Gbps Ethernet",
        "Uptime": "45 days, 12:30:15",
        "Load Average": "1.2, 1.5, 1.8",
        "Active Users": "247"
    }
    key_value(system_info)
    
    print()
    
    # List
    info("FEATURES", "Available System Features")
    features = [
        "Real-time monitoring dashboard",
        "Automated backup system",
        "Security threat detection",
        "Performance optimization",
        "User activity logging",
        "Resource allocation manager",
        "Network traffic analyzer",
        "Error reporting system"
    ]
    list_items(features)
    
    separator()
    
    # Switch back to normal mode
    set_centered(False)
    
    # Final logs with rate limit test
    title("FINAL TESTS")
    
    # Test rate limiting
    set_rate_limit(5)  # 5 logs per second
    info("TEST", "Testing rate limiting (5 logs/sec)...")
    
    for i in range(1, 11):
        debug("RATE TEST", f"Message {i}/10")
        time.sleep(0.1)  # Should show only 5 messages
    
    # Disable rate limit
    set_rate_limit(0)
    success("TEST", "Rate limit test completed")
    
    # Final message
    separator()
    thanks("SPEEDLOGGER", "Thank you for using SpeedLogger v6.1.0!")
    info("STATS", f"Total logs created in this session: {get_log_count()}")
    
    # Usage tips
    info("TIPS", "Use set_centered(True/False) to toggle center mode")
    info("TIPS", "Use set_show_time(True/False) to toggle time display")
    info("TIPS", "Use set_rate_limit(N) to limit logs per second (0 = no limit)")
    
    print(red_gradient("=" * 70))