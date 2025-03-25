import pathlib
import subprocess
import tempfile
import warnings

TSC_PATH = pathlib.Path(__file__).parent / "node_modules" / ".bin" / "tsc"


class TypeScriptFailed(Exception):
    pass


def check_with_tsc(code):
    if not TSC_PATH.exists():  # pragma: no cover
        warnings.warn("tsc not found, skipping TypeScript compilation check")
        return True
    with tempfile.NamedTemporaryFile(suffix=".ts") as ts_file:
        ts_file.write(code.encode("utf-8"))
        ts_file.flush()
        result = subprocess.run([TSC_PATH, "--noEmit", ts_file.name], capture_output=True, encoding="utf-8")
        if result.returncode != 0:  # pragma: no cover
            raise TypeScriptFailed(result.stdout + result.stderr)
        return True
