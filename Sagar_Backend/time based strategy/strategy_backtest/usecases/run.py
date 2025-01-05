import os
import subprocess

def run_python_files(start_with="Use", folder_path="."):
    files = os.listdir(folder_path)
    
    python_files = [file for file in files if file.startswith(start_with) and file.endswith('.py')]    
    for file in python_files:
        file_path = os.path.join(folder_path, file)
        print(f"Running {file_path}...")
        try:
            subprocess.run(["python", file_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while running {file}: {e}")

run_python_files(start_with="Use", folder_path=".")
