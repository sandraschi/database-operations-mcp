# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for database-operations-mcp backend sidecar."""

a = Analysis(
    ['run_server.py'], pathex=['src', '.'],
    datas=[('src/database_operations_mcp', 'database_operations_mcp')],
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.asyncio',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.httptools_impl',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        '_strptime',
    ],
    excludes=['tkinter', 'setuptools', 'pip', 'wheel', 'test', 'tests', 'unittest', '_distutils_hack'],
    noarchive=True,
)

# Strip all .dist-info from all TOC lists except mcp, opentelemetry, and email-validator (needed at runtime)
_keep_dist = ['mcp-', 'opentelemetry', 'email-validator', 'email_validator']
_saved = [e for e in a.datas if isinstance(e, tuple) and any(k in str(e[0]) for k in _keep_dist) and '.dist-info' in str(e[0])]
for _list in [a.datas, a.binaries, a.zipfiles, a.scripts]:
    _list[:] = [e for e in _list if not (isinstance(e, tuple) and '.dist-info' in str(e[0]))]
a.datas.extend(_saved)

SKIP = ['torch', 'playwright', 'bitsandbytes', 'llvmlite', 'pyarrow', 'pymupdf', 'grpc', 'numba', 'Cython', 'google', 'azure', 'boto3', 'botocore', 'matplotlib', 'PIL', 'pandas', 'scipy', 'sklearn', 'onnxruntime']
a.binaries = [b for b in a.binaries if not any(s in b[0].lower() for s in SKIP)]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='database-operations-mcp-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
)
