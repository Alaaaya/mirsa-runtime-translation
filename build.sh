#!/bin/bash
set -euo pipefail
mkdir -p out
python3 - <<'PY'
from pathlib import Path
data=Path('runtime-table.json').read_bytes()
Path('Table.h').write_text('static const unsigned char runtime_table[] = {'+','.join(str(b) for b in data)+'};\nstatic const unsigned long runtime_table_len = sizeof(runtime_table);\n')
PY
SDK=$(xcrun --sdk iphoneos --show-sdk-path)
xcrun --sdk iphoneos clang -arch arm64 -isysroot "$SDK" -miphoneos-version-min=15.0 -fobjc-arc -fblocks -O2 -Wall -Wextra -Werror=implicit-function-declaration -dynamiclib RuntimeTranslate.m fishhook.c -framework UIKit -framework Foundation -framework CoreText -install_name @rpath/MirsaTranslate.dylib -o out/MirsaTranslate.dylib
codesign -s - --force out/MirsaTranslate.dylib
lipo -info out/MirsaTranslate.dylib
otool -L out/MirsaTranslate.dylib
codesign --verify --strict out/MirsaTranslate.dylib
cp runtime-table.json out/MirsaTranslations.json
shasum -a 256 out/* > out/SHA256SUMS
