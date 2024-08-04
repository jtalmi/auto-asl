import subprocess
import time
import streamlit as st
from streamlit_app import main  # Import the main function from streamlit_app.py

# Start the Streamlit app as a subprocess
port = 8502
streamlit_process = subprocess.Popen(["streamlit", "run", "streamlit_app.py", f"--server.port={port}"])

# Wait a bit for Streamlit to start
time.sleep(5)

# Use ngrok to create a public URL
print(f"You can now view your Streamlit app in your browser.")
print(f"Local URL: http://localhost:{port}")

# Run the main function in the notebook
main()

# Keep the notebook running and clean up when interrupted
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Shutting down...")
    streamlit_process.terminate()
