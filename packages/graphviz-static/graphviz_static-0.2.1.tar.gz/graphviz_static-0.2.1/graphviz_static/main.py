import os
import sys
import platform
import subprocess
import stat
import shutil
import tempfile

def load_paths():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    os_sys = platform.system()
    machine = platform.machine().lower()

    if os_sys == "Windows":
        arch = "x64" if "64" in machine else "x86"
        folder_name = os.path.join("win", arch)
    elif os_sys == "Linux":
        if "aarch64" in machine or "arm64" in machine:
            folder_name = os.path.join("linux", "arm64")
        else:
            folder_name = os.path.join("linux", "x64")
    else:
        return

    binary_path = os.path.join(current_directory, "bin", folder_name)

    if os.path.exists(binary_path):
        os.environ["PATH"] = binary_path + os.pathsep + os.environ.get("PATH", "")

        if os_sys == "Linux":
            os.environ["LD_LIBRARY_PATH"] = binary_path + os.pathsep + os.environ.get("LD_LIBRARY_PATH", "")
            dot_file = os.path.join(binary_path, "dot")
            if os.path.exists(dot_file):
                st = os.stat(dot_file)
                os.chmod(dot_file, st.st_mode | stat.S_IEXEC)

        try:
            dot_cmd = "dot.exe" if os_sys == "Windows" else "dot"
            subprocess.run([dot_cmd, "-c"], check=True, capture_output=True)
        except:
            pass

def get_dot_path():
    return shutil.which("dot")

def render_to_bytes(dot_content, file_type="png", dpi=300):
    temp_fd = None
    temp_path = None
    try:
        temp_fd, temp_path = tempfile.mkstemp(suffix='.dot', text=True)
        with os.fdopen(temp_fd, 'w', encoding='utf-8') as tf:
            tf.write(dot_content)
            temp_fd = None

        dot_cmd = "dot.exe" if platform.system() == "Windows" else "dot"
        command = [dot_cmd, f"-T{file_type}", f"-Gdpi={dpi}", temp_path]
        result = subprocess.run(command, check=True, capture_output=True)
        return result.stdout
    finally:
        if temp_fd is not None:
            try:
                os.close(temp_fd)
            except OSError:
                pass
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass

def export_to_image(dot_content, file_type="png", file_name="output", dpi=300):
    if os.path.isfile(str(dot_content)):
        try:
            with open(dot_content, 'r', encoding='utf-8') as f:
                content = f.read()
        except IOError as e:
            raise IOError(f"ERROR: Failed to read DOT file '{dot_content}': {e}")
    elif isinstance(dot_content, str) and dot_content.strip():
        content = dot_content
    else:
        raise ValueError("ERROR: dot_content must be a non-empty string or a valid file path")

    data = render_to_bytes(content, file_type, dpi)
    if not data:
        raise RuntimeError("ERROR: Failed to generate image data from DOT content")

    output_file = f"{file_name}.{file_type}"
    try:
        with open(output_file, "wb") as f:
            f.write(data)
    except IOError as e:
        raise IOError(f"ERROR: Failed to write output file '{output_file}': {e}")

    return os.path.abspath(output_file)
