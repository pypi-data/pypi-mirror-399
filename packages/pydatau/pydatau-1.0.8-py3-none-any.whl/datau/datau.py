import warnings

# Suppress global noise BEFORE anything else runs
warnings.filterwarnings("ignore", category=UserWarning)

from   contextlib import contextmanager
from   os         import chdir, getcwd, name, rename, system, walk, remove
from   re         import match, I
from   datetime   import datetime
from   glob       import glob
from   papermill  import execute_notebook

def redirect_cmd(file, log, use_powershell=False):
    """
    Generate a platform-compatible redirection string.
    Works under POSIX, CMD (default on Windows), and optionally PowerShell.
    """
    if name == 'nt' and use_powershell:
        return f'powershell -Command "& {{ {file} *> \\"{log}\\" }}"'
    else:
        return f'{file} >"{log}" 2>&1'

def autorun(
    path_data :     str  = getcwd(),       pattern:        str        = '',
    date_fmt :      str  ='%Y%m%d_%H%M%S', log_limit:      int | None = None,
    use_powershell: bool = False,          *args, **kwargs
):
    """
    Cross-platform batch runner for statistical and numerical files.

    Parameters:
    -----------
    path_data : str
        Path to the directory with input files. Defaults to the current
        directory.

    pattern : str, optional
        Regex pattern to match filenames (not paths). Case-insensitive.

    date_fmt : str, optional
        Datetime format for `.log` filenames.
        Default is '%Y%m%d_%H%M%S' (e.g., 20250823_192407).

    log_limit : int, optional
        If set, limits the number of log files per script.
        Older logs beyond this limit will be deleted.

    use_powershell : bool, default = False
        If True, redirects via PowerShell on Windows. Ignored on POSIX.
    """
    julia  = 'julia'
    gams   = 'gams'
    ampl   = 'ampl'

    chdir(path_data)
    for root, dirs, files in walk('.'):
        for file in files:
            if not match(pattern, file, I):
                continue
            log = f"{file}.{datetime.now().strftime(date_fmt)}.log"
            def trim_logs(base):
                if log_limit is not None and log_limit >= 0:
                    logs = sorted(glob(f"{base}.*.log"), reverse=True)
                    for old_log in logs[log_limit:]:
                        try:
                            remove(old_log)
                        except Exception:
                            pass

            # 1. Jupyter
            if file.endswith('.ipynb'):
                execute_notebook(file, file, kwargs)
                trim_logs(file)
            # 2. R
            if file.endswith('.R'):
                from rpy2.robjects       import r
                with open(log, 'w')      as f:
                    f.write(str(r.source(file)))
                trim_logs(file)
            # 3. Stata
            if file.endswith('.do'):
                from stata_kernel.config import config as stata_config
                stata = stata_config.get('stata_path')
                system(stata + (' /' if name == 'nt' else ' -') + 'bq ' + file)
                try:
                    rename(file.replace('.do', '.log'), log)
                except Exception:
                    pass
                trim_logs(file)
            # 4. Julia
            if file.endswith('.jl'):
                system(redirect_cmd(f'{julia} {file}', log, use_powershell))
                trim_logs(file)
            # 5. GAMS
            if file.endswith('.gms'):
                system(redirect_cmd(f'{gams} {file}', log, use_powershell))
                trim_logs(file)
            # 6. AMPL
            if file.endswith('.run'):
                system(redirect_cmd(f'{ampl} {file}', log, use_powershell))
                trim_logs(file)
            # 7. MATLAB/Octave
            if file.endswith('.m'):
                try:                                   # MATLAB
                    import matlab.engine
                    M = matlab.engine.start_matlab()
                    M.addpath(path_data, nargout=0)
                    result = M.eval(file.replace('.m', ''), nargout=1)
                    with open(log, 'w')  as f:
                        f.write(str(result))
                    M.quit()
                except ImportError:                    # Octave
                    from oct2py          import Oct2Py
                    octave = Oct2Py()
                    with open(log, 'w')  as f:
                        f.write(str(octave.eval(file.replace('.m', '()'))))
                trim_logs(file)
        break
