"""
Command-line interface for Bazaar-AI simulator.
"""
import subprocess
import webbrowser
import time
import sys
import os
from pathlib import Path


def main():
    """
    Main entry point for the bazaar-simulate command.
    Starts the WebSocket server and opens the browser.
    """
    print("🐪 Starting Bazaar-AI Simulator...")
    
    # Get the path to the server module
    from . import server
    server_path = Path(server.__file__)
    
    # Start the server in the background
    print("Starting WebSocket server on ws://localhost:8765...")
    server_process = subprocess.Popen(
        [sys.executable, str(server_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Give the server a moment to start up
    time.sleep(2)
    
    # Get the path to the HTML file
    html_path = Path(__file__).parent / "static" / "index.html"
    
    if not html_path.exists():
        print(f"Error: Could not find HTML file at {html_path}")
        server_process.terminate()
        sys.exit(1)
    
    # Open the HTML file in browser
    print(f"Opening simulator in browser...")
    webbrowser.open(f"file://{html_path.absolute()}")
    
    print("\n✅ Simulator is running!")
    print("   WebSocket server: ws://localhost:8765")
    print("   Press Ctrl+C to stop\n")
    
    try:
        # Wait for the server process
        server_process.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping simulator...")
        server_process.terminate()
        server_process.wait()
        print("Goodbye! 🐪")


if __name__ == "__main__":
    main()