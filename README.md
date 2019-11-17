This repository describes issue which is reproduced on Windows system.

### How to compile:

 1. move to `example_project` directory
 2. execute `python compile_with_cython.py build_ext --inplace`
 <br>It will produce `dist` folder in root directory of repository, which contains compiled files for modules and source code for `main_script.py`
 3. move to `dist` directory in root of repository
 4. execute `python main_script.py`
 
### Issue description:

1. uncomment string `# from some_modules.third_modules import a122` in file `some_modules.source_script`
2. compile project and run `python main_script.py`(from `dist` folder) then following exception will be displayed:<br>
`ImportError: DLL load failed: Произошел сбой в программе инициализации библиотеки динамической компоновки (DLL).`<br>
English version of this exception: `ImportError: DLL load failed: A dynamic link library (DLL) initialization routine failed.`

PS: This issue is not reproduced (even with 200 count of import) on Ubuntu 18.04. On MacOS it wasn't tested.

PSS: related issue in python community - https://bugs.python.org/issue38597 
