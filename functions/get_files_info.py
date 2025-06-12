import os

def _format_entry(abs_dir_path, name):
    path = os.path.join(abs_dir_path, name)
    return (f"- {name}: "
            f"file_size={os.path.getsize(path)} bytes, "
            f"is_dir={os.path.isdir(path)}")

def get_files_info(working_directory, directory="."):
    try:
        abs_working_dir = os.path.abspath(working_directory)
        target_dir = directory or "."
        abs_dir_path = os.path.abspath(os.path.join(abs_working_dir, target_dir))

        if os.path.commonpath([abs_working_dir, abs_dir_path]) != abs_working_dir:
            return (f'Error: Cannot list "{directory}" as it is outside the '
                    f'permitted working directory')

        if not os.path.isdir(abs_dir_path):
            return f'Error: "{directory}" is not a directory'

        entries = list(map(
            lambda name: _format_entry(abs_dir_path, name),
            os.listdir(abs_dir_path)
        ))

        return "\n".join(entries) if entries else "(directory is empty)"
    except Exception as exc:
        return f"Error: {exc}"
