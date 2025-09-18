import pathlib
import subprocess
import tempfile
import warnings

TSC_PATH = pathlib.Path(__file__).parent / "node_modules" / ".bin" / "tsc"


class TypeScriptFailed(Exception):
    pass


def check_with_tsc(code, *, extra_files: dict[str, str] | None = None):
    if not TSC_PATH.exists():  # pragma: no cover
        warnings.warn("tsc not found, skipping TypeScript compilation check")
        return True
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = pathlib.Path(tmpdir)
        ts_file = tmp_path / "_typtyp_test.ts"
        ts_file.write_text(code)
        for filename, content in (extra_files or {}).items():
            extra_file = tmp_path / filename
            extra_file.write_text(content)
        result = subprocess.run(
            [TSC_PATH, "--noEmit", ts_file.name],
            capture_output=True,
            encoding="utf-8",
            cwd=tmp_path,
        )
        if result.returncode != 0:  # pragma: no cover
            raise TypeScriptFailed(result.stdout + result.stderr)
        return True
