import os
import subprocess

def run_python_file(working_directory, file_path):
    abs_working_directory = os.path.abspath(working_directory)
    joined_file_path = os.path.abspath(os.path.join(abs_working_directory, file_path))
    
    if not joined_file_path.startswith(abs_working_directory):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    
    if file_path not in os.listdir(abs_working_directory):
        return f'Error: File "{file_path}" not found.'
    
    if os.path.splitext(file_path)[1] != ".py":
        return f'Error: "{file_path}" is not a Python file.'
    
    try:
        result = subprocess.run(["python3", joined_file_path], timeout=30, capture_output=True, text=True, cwd=abs_working_directory)
        
        output = []
        if result.stdout:
            output.append(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            output.append(f"STDERR:\n{result.stderr}")
        
        if result.returncode != 0:
            output.append(f"Process exited with code {result.returncode}")
        
        return "\n".join(output) if output else "No output produced."
    
    except Exception as e:
        return f"Error: {str(e)}"
