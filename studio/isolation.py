"""Fresh estimator directory/process plus a Python file-access guard after bootstrap."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

SOURCE = Path(__file__).resolve().parents[1]
SAFE_MODULES = ['__init__.py','estimate.py','files.py','runtime.py','statistics.py','transforms.py','isolation.py']


def guard(root):
    """Allow data files only in root; runtime package reads remain permitted.

    Trusted imports bootstrap before this guard. This is not an adversarial native-code
    sandbox; it prevents Python data access outside the safe workspace/runtime roots.
    """
    root = root.resolve()
    runtimes = {Path(sys.prefix).resolve(), Path(sys.base_prefix).resolve()}
    reads = set()
    def audit(event, args):
        if event != 'open' or isinstance(args[0], int):
            return
        path = Path(os.fsdecode(args[0])).resolve()
        if path.is_relative_to(root):
            mode = args[1]
            if isinstance(mode, str) and 'r' in mode and path.suffix in ['.csv','.json']:
                reads.add(path.relative_to(root).as_posix())
            return
        if any(path.is_relative_to(prefix) for prefix in runtimes):
            return
        raise PermissionError('Estimator file access outside isolated workspace/runtime is forbidden')
    sys.addaudithook(audit)
    return reads


def stage_workspace(bundle, workspace, manifest):
    shutil.copyfile(SOURCE/'requirements.lock', workspace/'requirements.lock')
    (workspace/'studio').mkdir()
    for filename in SAFE_MODULES:
        shutil.copyfile(SOURCE/'studio'/filename, workspace/'studio'/filename)
    (workspace/'contracts').mkdir()
    shutil.copyfile(SOURCE/'contracts/validate.py', workspace/'contracts/validate.py')
    for schema in (SOURCE/'contracts').glob('*.schema.json'):
        shutil.copyfile(schema, workspace/'contracts'/schema.name)
    (workspace/'safe').mkdir()
    shutil.copyfile(bundle/'safe/data.csv', workspace/'safe/data.csv')
    from contracts import validate as v
    source = v.contained(manifest, bundle)
    destination = v.contained(manifest, workspace)
    shutil.copyfile(source, destination)


def isolated_fit(bundle, manifest):
    with tempfile.TemporaryDirectory(prefix='aas-estimator-') as directory:
        workspace = Path(directory)
        stage_workspace(bundle, workspace, manifest)
        # No inherited credentials/generator configuration or repository PYTHONPATH.
        environment = {name: os.environ[name] for name in ['PATH','LANG','SYSTEMROOT'] if name in os.environ}
        environment.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', PYTHONHASHSEED='0')
        command = [sys.executable, '-I', '-B', '-c',
                   "import sys; sys.path.insert(0, '.'); from studio.estimate import main; main()",
                   '--root', '.', '--manifest', manifest]
        try:
            subprocess.run(command, cwd=workspace, env=environment, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as error:
            raise RuntimeError('Isolated estimator failed:\n' + error.stderr) from error
        name = Path(manifest).name.removesuffix('.manifest.json')
        for suffix in ['result.json', 'result.predictions.csv', 'access.json']:
            relative = f'safe/{name}.{suffix}'
            from .files import write_once
            write_once(bundle/relative, (workspace/relative).read_bytes())
