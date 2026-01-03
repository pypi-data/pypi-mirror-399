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
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.dot', encoding='utf-8') as tf:
        tf.write(dot_content)
        temp_path = tf.name

    try:
        command = ["dot", f"-T{file_type}", f"-Gdpi={dpi}", temp_path]
        result = subprocess.run(command, check=True, capture_output=True)
        return result.stdout
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def export_to_image(dot_content, file_type="png", file_name="output", dpi=300):
    output_file = f"{file_name}.{file_type}"
    data = render_to_bytes(dot_content, file_type, dpi)
    with open(output_file, "wb") as f:
        f.write(data)
    return os.path.abspath(output_file)