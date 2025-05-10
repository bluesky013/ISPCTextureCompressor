# unzip
import os
import subprocess
import argparse
import shutil

parser = argparse.ArgumentParser(description='')
parser.add_argument('-p', '--platform', type=str, choices=["Win32", "MacOS-x86", "MacOS-arm", "Android"], help='编译平台')

args = parser.parse_args()

version = 'v1.26.0'

zip_suffix = {
    'Win32': '.zip',
    'MacOS-x86': '.tar.gz',
    'MacOS-arm': '.tar.gz',
}

dst_dir = {
    'Win32': 'win',
    'MacOS-x86': 'osx',
    'MacOS-arm': 'osx',
}

current_path = os.getcwd()

def build_vs_project(project_path, configuration="Release", platform="x64"):
    """
    MSBuild
    :param project_path: .vcxproj
    :param configuration: (Debug/Release)
    :param platform: (x86/x64)
    """
    # 查找 MSBuild 路径 (VS 2019/2022)
    msbuild = "MSBuild.exe"
    
    # 构建命令
    cmd = [
        msbuild,
        project_path,
        f"/p:Configuration={configuration}",
        f"/p:Platform={platform}",
        "/t:Build",
        "/m"  # 多核编译
    ]
    
    # 执行构建
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("Successed")
    else:
        print("Failed")
        print(result.stderr)
    # copy
    dst_dir = os.path.join(current_path, "build", "install", "bin")
    os.makedirs(dst_dir, exist_ok=True)
    
    copy_src = os.path.join(current_path, "ispc_texcomp", platform, configuration, "ispc_texcomp.dll")
    copy_dst = os.path.join(dst_dir, "ispc_texcomp.dll")
    
    print(copy_src, copy_dst)
    shutil.copy(copy_src, copy_dst)
    return result.returncode

def build_xcode_project(project_path, configuration="Release", destination="generic/platform=iOS"):
    if project_path.endswith('.xcworkspace'):
        workspace_arg = '-workspace'
    else:
        workspace_arg = '-project'
    
    cmd = [
        'xcodebuild',
        workspace_arg, project_path,
        '-scheme', 'tmpbuild',
        '-configuration', configuration,
        '-destination', destination,
        'build'
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Successed")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Failed: {e.stderr}")
        return e.returncode

proj_fun_map = {
    'Win32': build_vs_project,
    'MacOS-x86': build_xcode_project,
    'MacOS-arm': build_xcode_project,
}

proj_path_map = {
    'Win32': 'ispc_texcomp/ispc_texcomp.vcxproj',
    'MacOS-x86': 'ispc_texcomp.xcodeproj',
    'MacOS-arm': 'ispc_texcomp.xcodeproj',
}

def copy_header():
    src_dir = os.path.join(current_path, "ispc_texcomp")
    dst_dir = os.path.join(current_path, "build", "install", "include", "ispc_texcomp")
    os.makedirs(dst_dir, exist_ok=True)
    
    copy_header_files = [
        'ispc_texcomp.h'
    ]
    
    for file in copy_header_files:
        src = os.path.join(src_dir, file)
        dst = os.path.join(dst_dir, file)
        shutil.copy(src, dst)

def app_main():
    zip_path = f"ispc-{version}-{args.platform}{zip_suffix[args.platform]}"
    
    src = os.path.join(current_path, zip_path)
    dst = os.path.join(current_path, "build", "install", "bin")
    
    if zip_path.endswith('.tar.gz'):
        import tarfile
        
        with tarfile.open(src, 'r:gz') as tar_ref:
            tar_ref.extractall(dst)
            
    elif zip_path.endswith('.zip'):
        import zipfile
        
        with zipfile.ZipFile(src, 'r') as zip_ref:
            zip_ref.extractall(dst)
    
    # proj_path = proj_path_map[args.platform]
    # proj_fun = proj_fun_map[args.platform]
    #
    # copy_header()
    # proj_fun(proj_path)
    

if __name__ == "__main__":
    app_main()