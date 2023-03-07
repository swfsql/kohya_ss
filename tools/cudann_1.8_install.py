import filecmp
import importlib.util
import os
import shutil
import sys
import sysconfig
import subprocess
from pathlib import Path
if sys.version_info < (3, 8):
    import importlib_metadata
else:
    import importlib.metadata as importlib_metadata

req_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../requirements.txt")

def run(command, desc=None, errdesc=None, custom_env=None):
    if desc is not None:
        print(desc)

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, env=os.environ if custom_env is None else custom_env)

    if result.returncode != 0:

        message = f"""{errdesc or 'Error running command'}.
Command: {command}
Error code: {result.returncode}
stdout: {result.stdout.decode(encoding="utf8", errors="ignore") if len(result.stdout)>0 else '<empty>'}
stderr: {result.stderr.decode(encoding="utf8", errors="ignore") if len(result.stderr)>0 else '<empty>'}
"""
        raise RuntimeError(message)

    return result.stdout.decode(encoding="utf8", errors="ignore")

def check_versions():
    global req_file
    reqs = open(req_file, 'r')
    lines = reqs.readlines()
    reqs_dict = {}
    for line in lines:
        splits = line.split("==")
        if len(splits) == 2:
            key = splits[0]
            if "torch" not in key:
                if "diffusers" in key:
                    key = "diffusers"
                reqs_dict[key] = splits[1].replace("\n", "").strip()
    if os.name == "nt":
        reqs_dict["torch"] = "1.12.1+cu116"
        reqs_dict["torchvision"] = "0.13.1+cu116"

    checks = ["xformers","bitsandbytes", "diffusers", "transformers", "torch", "torchvision"]
    for check in checks:
        check_ver = "N/A"
        status = "[ ]"
        try:
            check_available = importlib.util.find_spec(check) is not None
            if check_available:
                check_ver = importlib_metadata.version(check)
                if check in reqs_dict:
                    req_version = reqs_dict[check]
                    if str(check_ver) == str(req_version):
                        status = "[+]"
                    else:
                        status = "[!]"
        except importlib_metadata.PackageNotFoundError:
            check_available = False
        if not check_available:
            status = "[!]"
            print(f"{status} {check} NOT installed.")

        else:
            print(f"{status} {check} version {check_ver} installed.")

base_dir = os.path.dirname(os.path.realpath(__file__))
check_versions()
