import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.run_python_file import run_python_file
from functions.write_file import write_file

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description=(
                    "The directory to list files from, relative to the working "
                    "directory. If not provided, lists files in the working "
                    "directory itself."
                ),
            ),
        },
    ),
)

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads the content of a specified file",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The name of the file whose contents should be read",
            ),
        },
    ),
)

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python file and returns the output",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the Python file to be executed, relative to the working directory",
            ),
        },
    ),
)

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes content to a specified file",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file where content will be written, relative to the working directory",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to be written to the file",
            ),
        },
    ),
)

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_write_file,
        schema_run_python_file,
        schema_get_file_content,
    ]
)

config = types.GenerateContentConfig(
    tools=[available_functions], system_instruction=system_prompt
)

function_mapping = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "run_python_file": run_python_file,
    "write_file": write_file,
}

def call_function(function_call_part: types.FunctionCall, verbose: bool = False):
    function_name = function_call_part.name
    kwargs = dict(function_call_part.args)
    kwargs["working_directory"] = "./calculator"

    if verbose:
        print(f"Calling function: {function_name}({kwargs})")
    else:
        print(f" - Calling function: {function_name}")

    if function_name not in function_mapping:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )

    result = function_mapping[function_name](**kwargs)

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": result},
            )
        ],
    )

def main():
    if len(sys.argv) < 2:
        print("Error: no prompt provided")
        sys.exit(1)

    prompt = sys.argv[1]
    verbose = len(sys.argv) > 2 and sys.argv[2] == "--verbose"
    model_name = "gemini-2.0-flash-001"

    messages = [types.Content(role="user", parts=[types.Part(text=prompt)])]
    res = client.models.generate_content(
        model=model_name,
        contents=messages,
        config=config,
    )

    if res.function_calls:
        for fc_part in res.function_calls:
            call_result = call_function(fc_part, verbose=verbose)

            if (
                not call_result.parts
                or not call_result.parts[0].function_response
                or call_result.parts[0].function_response.response is None
            ):
                raise RuntimeError("Fatal: function call produced no response")

            if verbose:
                print(f"-> {call_result.parts[0].function_response.response}")
    else:
        print(res.text)

    if verbose:
        print(f"User prompt: {prompt}")
        print(f"Prompt tokens: {res.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {res.usage_metadata.candidates_token_count}")

if __name__ == "__main__":
    main()
