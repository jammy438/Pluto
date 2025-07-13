#!/usr/bin/env python3
"""
Application runner script to start both backend and frontend servers.
"""

import subprocess
import sys
import os
import time
import signal
import threading

def run_backend():
    """Run the FastAPI backend server"""
    print("Starting backend server...")
    try:
        # Change to backend directory if it exists
        if os.path.exists('backend'):
            os.chdir('backend')
        
        # Initialize database if needed
        if not os.path.exists('cricket_data.db'):
            print("Initializing database...")
            subprocess.run([sys.executable, 'init_db.py'])
        
        # Start FastAPI server
        subprocess.run([sys.executable, 'main.py'])
    except KeyboardInterrupt:
        print("Backend server stopped.")
    except Exception as e:
        print(f"Error running backend: {e}")

def run_frontend():
    """Run the React frontend server"""
    print("Starting frontend server...")
    try:
        # Change to frontend directory
        if os.path.exists('frontend'):
            os.chdir('frontend')
        
        # Check if node_modules exists
        if not os.path.exists('node_modules'):
            print("Installing frontend dependencies...")
            subprocess.run(['npm', 'install'])
        
        # Start React development server
        subprocess.run(['npm', 'start'])
    except KeyboardInterrupt:
        print("Frontend server stopped.")
    except Exception as e:
        print(f"Error running frontend: {e}")

def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")
    
    # Check Python
    try:
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            print("Error: Python 3.8 or higher is required")
            return False
        print(f"✓ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    except Exception as e:
        print(f"Error checking Python: {e}")
        return False
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Node.js {result.stdout.strip()}")
        else:
            print("Error: Node.js is not installed")
            return False
    except FileNotFoundError:
        print("Error: Node.js is not installed")
        return False
    
    # Check npm
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ npm {result.stdout.strip()}")
        else:
            print("Error: npm is not installed")
            return False
    except FileNotFoundError:
        print("Error: npm is not installed")
        return False
    
    return True

def main():
    """Main function to run the application"""
    print("Cricket Data Application Runner")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        print("\nPlease install the required dependencies and try again.")
        sys.exit(1)
    
    print("\nSelect an option:")
    print("1. Run backend only (FastAPI server)")
    print("2. Run frontend only (React dev server)")
    print("3. Run both servers (recommended)")
    print("4. Initialize database only")
    print("5. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            run_backend()
            break
        elif choice == '2':
            run_frontend()
            break
        elif choice == '3':
            print("\nStarting both servers...")
            print("Backend will run on http://localhost:8000")
            print("Frontend will run on http://localhost:3000")
            print("Press Ctrl+C to stop both servers")
            
            # Start backend in a separate thread
            backend_thread = threading.Thread(target=run_backend)
            backend_thread.daemon = True
            backend_thread.start()
            
            # Give backend time to start
            time.sleep(3)
            
            # Start frontend in main thread
            try:
                run_frontend()
            except KeyboardInterrupt:
                print("\nStopping servers...")
                break
            
            break
        elif choice == '4':
            print("Initializing database...")
            try:
                if os.path.exists('backend'):
                    os.chdir('backend')
                subprocess.run([sys.executable, 'init_db.py'])
                print("Database initialized successfully!")
            except Exception as e:
                print(f"Error initializing database: {e}")
            break
        elif choice == '5':
            print("Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please enter 1, 2, 3, 4, or 5.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nApplication stopped.")
        sys.exit(0)