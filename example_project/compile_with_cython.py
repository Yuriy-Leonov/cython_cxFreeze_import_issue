"""python compile_with_cython.py build_ext --inplace"""
# import setuptools  # important
import os
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from Cython.Build import cythonize
import shutil
import multiprocessing


sep = os.path.sep
DISTRIBUTE_DIR_NAME = "dist"
DISTRIBUTE_DIR_PATH = f"..{sep}{DISTRIBUTE_DIR_NAME}"

THREADS = multiprocessing.cpu_count()


module_directories = [
    "some_modules"
]


def reverse_scan_directory_for_files(path_to_dir, files_extensions,
                                     files=None):
    if files is None:
        files = []
    for f in os.listdir(path_to_dir):
        path = os.path.join(path_to_dir, f)
        if os.path.isfile(path) and \
                any([path.endswith(ext) for ext in files_extensions]):
            files.append(path)
        elif os.path.isdir(path):
            reverse_scan_directory_for_files(
                path, files_extensions, files)
    return files


def not_reverse_scan_directory_for_files(path_to_dir, files_extensions):
    files = []
    for f in os.listdir(path_to_dir):
        path = os.path.join(path_to_dir, f)
        if os.path.isfile(path) and \
                any([path.endswith(ext) for ext in files_extensions]):
            files.append(path)
    return files


def reverse_create_modules_name(path_to_dir, files=None):
    if files is None:
        files = []
    for f in os.listdir(path_to_dir):
        if "__init__.py" in f:
            continue
        path = os.path.join(path_to_dir, f)
        if os.path.isfile(path) and path.endswith(".py"):
            fixed_path = path
            if ".." in path:
                fixed_path = path[3:]  # .. and sep
            future_module_name = fixed_path.replace(sep, ".")[:-3]
            files.append(future_module_name)
        elif os.path.isdir(path):
            reverse_create_modules_name(path, files)
    return files


def copy_files_to_dist(files_to_copy):
    os.makedirs(DISTRIBUTE_DIR_NAME, exist_ok=True)
    for path in files_to_copy:
        fixed_path = path
        if ".." in path:
            fixed_path = path[3:]  # .. and sep
        new_path = f"{DISTRIBUTE_DIR_NAME}{sep}{fixed_path}"
        os.makedirs(
            sep.join(new_path.split(sep)[:-1]),
            exist_ok=True)
        shutil.copyfile(path, new_path)


def generate_extension(module_name):
    py_path = module_name.replace(".", sep) + ".py"
    dist_py_file_path = f"{DISTRIBUTE_DIR_NAME}{sep}{py_path}"
    return Extension(
        module_name,
        [dist_py_file_path]
    )


def setup_given_extensions(extension):
    setup(
        name="example",
        ext_modules=[extension],
        cmdclass={'build_ext': build_ext},
    )


def setup_extensions_in_parallel(extensions_list):

    cythonize(extensions_list, nthreads=THREADS,
              compiler_directives={"language_level": "3"})
    pool = multiprocessing.Pool(processes=THREADS)
    pool.map(setup_given_extensions, extensions_list)
    pool.close()
    pool.join()


def cleanup(directory_name):
    files_for_delete = reverse_scan_directory_for_files(directory_name,
                                                        [".c", ".so", ".pyd"])
    for file_path in files_for_delete:
        os.remove(file_path)

    fixed_directory_name = directory_name
    if ".." in directory_name:
        fixed_directory_name = directory_name[3:]
    directory_name = f"{DISTRIBUTE_DIR_NAME}{sep}{fixed_directory_name}"
    files_for_delete = reverse_scan_directory_for_files(directory_name,
                                                        [".c", ".py"])
    for file_path in files_for_delete:
        os.remove(file_path)


def cleanup_root():
    root_cleanup_files = not_reverse_scan_directory_for_files(
        ".",
        [".c", ".so", ".pyd"]
    )
    root_cleanup_files.extend(not_reverse_scan_directory_for_files(
        DISTRIBUTE_DIR_NAME,
        [".c", ".py"])
    )

    for f in root_cleanup_files:
        os.remove(f)


def start():
    extensions = []

    for directory in module_directories:
        files_ = reverse_scan_directory_for_files(
            directory,
            [".py"]
        )
        copy_files_to_dist(files_)

        list_os_modules = reverse_create_modules_name(directory)
        extensions.extend(
            [generate_extension(module) for module in list_os_modules])

    setup_extensions_in_parallel(extensions)
    # at this moments .so or .pyd is generated

    for directory in module_directories:
        files_ = reverse_scan_directory_for_files(directory, [".so", ".pyd"])
        copy_files_to_dist(files_)
        cleanup(directory)

    # hook for root files
    files_ = not_reverse_scan_directory_for_files(".", [".so", ".pyd"])
    copy_files_to_dist(files_)
    cleanup_root()
    copy_files_to_dist([
        "main_script.py"
    ])

    if os.path.exists(DISTRIBUTE_DIR_PATH):
        shutil.rmtree(DISTRIBUTE_DIR_PATH)
    shutil.copytree(DISTRIBUTE_DIR_NAME, DISTRIBUTE_DIR_PATH)
    shutil.rmtree("build")
    shutil.rmtree(DISTRIBUTE_DIR_NAME)


if __name__ == '__main__':
    start()
