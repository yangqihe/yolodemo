# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['sbert\\whisper_app.py'],
    pathex=[],
    binaries=[],
    datas=[
    ('sbert/sbert_intent', 'sbert/sbert_intent'),
    ('sbert/img', 'sbert/img'), ('model/whisper', 'model/whisper'),
    ('model/huggingface', 'model/huggingface'),
    ('D:/Github/yolodemo/yolodemo/.venv/Lib/site-packages/whisper/assets/mel_filters.npz', 'whisper/assets'),
    ('D:/Github/yolodemo/yolodemo/.venv/Lib/site-packages/whisper/assets/multilingual.tiktoken', 'whisper/assets'),
    ('D:/Github/yolodemo/yolodemo/.venv/Lib/site-packages/whisper/assets/gpt2.tiktoken', 'whisper/assets'),
    ],
    hiddenimports=['transformers.models.deepseek_v3', 'transformers.models.qwen3','transformers.models.qwen3_moe'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='whisper_app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['sbert\\img\\logo\\logo.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='whisper_app',
)
