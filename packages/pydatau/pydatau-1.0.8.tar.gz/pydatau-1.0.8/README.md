# DATAU - Batch Statistical Data Utilities

Cross-platform batch runner for statistical and numerical files.

## Installation

```bash
pip install pydatau
```

## Quick example
python:  
```python
from datau import autorun

autorun(path_data="my_project/data", pattern='master', log_limit=1)
```
bash:  
```bash
datau "my_project/data" -p "master" -l 1
```

## Supported Extensions and Execution Method

| Extension | Language/Tool    | Method                      |
|-----------|------------------|-----------------------------|
| `.ipynb`  | Jupyter Notebook | `papermill`                 |
| `.R`      | R                | `rpy2.robjects`             |
| `.do`     | Stata            | Stata batch mode            |
| `.jl`     | Julia            | `julia` (must be in PATH)   |
| `.gms`    | GAMS             | `gams` (must be in PATH)    |
| `.run`    | AMPL             | `ampl` (must be in PATH)    |
| `.m`      | MATLAB/Octave    | `matlab.engine` or `Oct2Py` |

## User Reference

```python
autorun(path_data='...', pattern='...', *args, **kwargs)
```

Automatically runs matching statistical scripts in the given directory. Generates a number of `.log` files with outputs for each executed file.

**Parameters:**  

`path_data` : *str*, default = *current working directory*  
Path to the directory with input files.

`pattern` : *str*, optional  
Regex pattern to match filenames (not paths), such as *'master'*. Case-insensitive.

`date_fmt` : *str*, default = *'%Y%m%d_%H%M%S'*  
Datetime format for *.log* filenames.

`log_limit` : *int*, optional  
If set, limits the number of log files per script. Older logs beyond this limit will be deleted. Please note that you can turn off logging by setting `log_limit` to *0*.

`use_powershell` : *bool*, default = *False*  
If *True*, redirects via PowerShell on Windows. Ignored on POSIX.

## License

MIT License — see the [LICENSE](LICENSE) file.
