"""
Bazaar-AI Simulator

A web-based interface for visualizing and testing Bazaar-AI agents.
"""

from . import server

__all__ = ['server']


def run_simulator():
    """
    Convenience function to start the simulator.
    Can be called programmatically instead of using the CLI.
    
    Example:
        >>> from bazaar_ai.simulator import run_simulator
        >>> run_simulator()
    """
    import subprocess
    import webbrowser
    import time
    import sys
    from pathlib import Path
    
    print("🐪 Starting Bazaar-AI Simulator...")
    
    # Start server
    server_path = Path(server.__file__)
    server_process = subprocess.Popen([sys.executable, str(server_path)])
    
    time.sleep(2)
    
    # Open browser
    html_path = Path(__file__).parent / "static" / "index.html"
    webbrowser.open(f"file://{html_path.absolute()}")
    
    print("✅ Simulator running at ws://localhost:8765")
    print("   Press Ctrl+C to stop")
    
    try:
        server_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping simulator...")
        server_process.terminate()
        server_process.wait()
        print("Goodbye! 🐪")
