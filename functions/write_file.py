import os


def write_file(working_directory, file_path, content):
    abs_joined_path = os.path.abspath(os.path.join(os.path.abspath(working_directory), file_path))
    try:
        if abs_joined_path.startswith(os.path.abspath(working_directory)):
            if not os.path.exists(os.path.dirname(abs_joined_path)):
                os.makedirs(os.path.dirname(abs_joined_path)) 
            with open(abs_joined_path, "w") as f:
                f.write(content)
            return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
        else:
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    except Exception as e:
        return f"Error: {e}"
    

