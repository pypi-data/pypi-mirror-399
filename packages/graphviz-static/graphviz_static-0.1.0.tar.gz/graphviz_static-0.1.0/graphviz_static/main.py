import os
import sys
import platform
import subprocess
def load_paths():
    "prepare the files for grpahviz operation"

    #get current path of innit
    current_directory = os.path.dirname(os.path.abspath(__file__))
    os_sys = platform.system()


    folder_name = ""

    if os_sys == "Windows":
        arch = "x64" if platform.machine().endswith('64') else "x86"
        folder_name = os.path.join("win", arch)

        

    elif os_sys == "Linux":
        folder_name = "linux"
    else: return print("ERROR: Your OS platform is not supported. You can contribute to the project or ask for support :( ")

    binary_path = os.path.join(current_directory, "bin", folder_name)


    #check if bin path exist or not
    if os.path.exists(binary_path):
        os.environ["PATH"] =  binary_path + os.pathsep + os.environ["PATH"] 
        try:
            dot_exe = os.path.join(binary_path, "dot.exe" if os_sys == "Windows" else "dot")
            subprocess.run([dot_exe, "-c"], check=True, capture_output=True)
            print(f"Graphviz activated at: {binary_path}")
        except Exception as e:
            print(f"WARNING: Error while loading: {e}")
      
    else:
        print(f"WARNING :  Graphviz is not found on bin folder")

def get_dot_path():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    ext = ".exe" if sys.platform == "win32" else ""
    return os.path.join(current_directory, "bin", f"dot{ext}")


def export_to_image(dot_file, file_type="png", file_name="output"):
    
    output_file = f"{file_name}.{file_type}"
    try:
        command = [
            "dot", 
            f"-T{file_type}", 
            "-Gcharset=utf8", 
            dot_file, 
            "-o", 
            output_file
        ]
        subprocess.run(command, check=True, capture_output=True, text=True)
        
        print(f" Export completed. Check {os.path.abspath(output_file)} for results")
        return os.path.abspath(output_file)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Graphviz error: {e.stderr}")
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")





