from . import cryptolith_runtime
import sys as _obs_sys
import os as _obs_os

def _junk_func():
    pass
import base64
nBUWHbczfM = base64.b64decode('/l0RfrimRy6Jo4tTh7uJPaU3sRe+4I79TtUcT+dBjBM=')

def QcPHynfSPv(i):
    d = base64.b64decode(uKdUAOwLuy[i])
    return bytes([b ^ nBUWHbczfM[j % len(nBUWHbczfM)] for j, b in enumerate(d)]).decode('utf-8')
uKdUAOwLuy = ['tzNlG9/ULlrwg9066NfoScxY3y2er/6cP6B5b7cz6XeXPnAK3YYBT+DP7jc=', 'iyl3U4A=', '0C1oGg==', '0C5+', 'rQlVMe3yfQ==', 'rQlVO+r0fQ==', 'vTJ8DtHKJlrgzOVz9M7qXsBS1XLawOyIOvV5N5Mk4mCXMn9e3s8rS6nN5Cen3eZIy1Of']
import os as uIvubdkNku
import sys
import subprocess as RkVwtMnGYl
import shutil as StszSaAZxb

def QvtumKQCgB(tGcluWJXpo, OwOdQGVCqX, output_dir, flnbYeywzE=47 - 47, eaoufuoOnf=None, NzcNXGlJBy=None, KEgzggBUwj=None, WPMiGKqbsi='.c'):
    PkbZJricJQQg = 2
    while PkbZJricJQQg != -1:
        if PkbZJricJQQg == 5:
            import hashlib as ylupjgcbxH
            PkbZJricJQQg = 9
        elif PkbZJricJQQg == 3:
            with xkoaJoSdmZ.TemporaryDirectory() as IWLrqTdPiL:
                zQdDJCXlXq = uIvubdkNku.path.join(IWLrqTdPiL, f'{OwOdQGVCqX}{WPMiGKqbsi}')
                with open(zQdDJCXlXq, 'w') as cmaqZZHNZc:
                    cmaqZZHNZc.write(tGcluWJXpo)
                if not uIvubdkNku.path.exists(output_dir):
                    uIvubdkNku.makedirs(output_dir)
                tYDtGTHZHA = uIvubdkNku.path.join(output_dir, f'{OwOdQGVCqX}.c')
                with open(tYDtGTHZHA, 'w') as cmaqZZHNZc:
                    cmaqZZHNZc.write(tGcluWJXpo)
                print(f'BCC_SOURCE_SAVED: {tYDtGTHZHA}')
                GuKDpflVhT = str(eaoufuoOnf) if eaoufuoOnf else '[]'
                syjuRYMrqK = str(NzcNXGlJBy) if NzcNXGlJBy else '[]'
                yitQdJnkEG = str(KEgzggBUwj) if KEgzggBUwj else '[]'
                FRuGBJQBVg = f"\nfrom setuptools import setup, Extension\nsetup(\n    name='{OwOdQGVCqX}',\n    ext_modules=[Extension('{OwOdQGVCqX}', \n                           sources=['{OwOdQGVCqX}{WPMiGKqbsi}'],\n                           include_dirs={GuKDpflVhT},\n                           library_dirs={syjuRYMrqK},\n                           libraries={yitQdJnkEG},\n                           extra_compile_args=['/std:c++17'] if '{WPMiGKqbsi}' == '.cpp' and {uIvubdkNku.name == 'nt'} else []\n                           )],\n    script_args=['build_ext', '--inplace']\n)\n"
                sfTwhFYbyV = uIvubdkNku.path.join(IWLrqTdPiL, f'setup_{OwOdQGVCqX}.py')
                with open(sfTwhFYbyV, 'w') as cmaqZZHNZc:
                    cmaqZZHNZc.write(FRuGBJQBVg)
                if flnbYeywzE:
                    print(f'Compiling native module {OwOdQGVCqX} in isolated dir {IWLrqTdPiL}...')
                try:
                    pZbswmqIio = RkVwtMnGYl.run([sys.executable, f'setup_{OwOdQGVCqX}.py'], cwd=IWLrqTdPiL, capture_output=82 - 81, text=8 - 7)
                    if pZbswmqIio.returncode != 82 - 82:
                        print(f'--- COMPILER ERROR FOR {OwOdQGVCqX} ---')
                        print(QcPHynfSPv(4), pZbswmqIio.stdout)
                        print(QcPHynfSPv(5), pZbswmqIio.stderr)
                        raise RuntimeError(f'C compilation failed for {OwOdQGVCqX}. Error: {pZbswmqIio.stderr}')
                    eTsyKGWNVe = None
                    for cmaqZZHNZc in uIvubdkNku.listdir(IWLrqTdPiL):
                        if cmaqZZHNZc.startswith(OwOdQGVCqX) and cmaqZZHNZc.endswith(SrxntlqPgE):
                            eTsyKGWNVe = cmaqZZHNZc
                            break
                    if not eTsyKGWNVe:
                        raise RuntimeError(QcPHynfSPv(6))
                    if not uIvubdkNku.path.exists(output_dir):
                        uIvubdkNku.makedirs(output_dir)
                    LzGEVkDmse = uIvubdkNku.path.join(output_dir, eTsyKGWNVe)
                    StszSaAZxb.copy2(uIvubdkNku.path.join(IWLrqTdPiL, eTsyKGWNVe), LzGEVkDmse)
                    with open(qEcWrMJbQa, 'w') as vNXSAZKJXm:
                        vNXSAZKJXm.write(crpPlGEyrK)
                    return LzGEVkDmse
                except Exception as OZfRaQYsgY:
                    raise OZfRaQYsgY
            PkbZJricJQQg = -1
        elif PkbZJricJQQg == 11:
            96 * 0
            crpPlGEyrK = ylupjgcbxH.sha256(jVmxoEmquR.encode(QcPHynfSPv(1))).hexdigest()
            PkbZJricJQQg = 7
        elif PkbZJricJQQg == 7:
            qEcWrMJbQa = uIvubdkNku.path.join(output_dir, f'{OwOdQGVCqX}.hash')
            PkbZJricJQQg = 4
        elif PkbZJricJQQg == 10:
            gBNzuyTROT = None
            PkbZJricJQQg = 1
        elif PkbZJricJQQg == 7235:
            print('...')
        elif PkbZJricJQQg == 2:
            if 49 + 89 + (62 + 157) - ((72 + 66 ^ 46 + 173) + (85 - 83) * (29 + 109 & 36 + 183)) & 44 + 211 == 97 - 97:
                None
            else:
                raise RuntimeError(QcPHynfSPv(0))
            PkbZJricJQQg = 8
        elif PkbZJricJQQg == 1:
            if uIvubdkNku.path.exists(output_dir):
                for cmaqZZHNZc in uIvubdkNku.listdir(output_dir):
                    if cmaqZZHNZc.startswith(OwOdQGVCqX) and cmaqZZHNZc.endswith(SrxntlqPgE):
                        gBNzuyTROT = uIvubdkNku.path.join(output_dir, cmaqZZHNZc)
                        break
            PkbZJricJQQg = 6
        elif PkbZJricJQQg == 8:
            import tempfile as xkoaJoSdmZ
            PkbZJricJQQg = 5
        elif PkbZJricJQQg == 0:
            jVmxoEmquR = tGcluWJXpo + str(eaoufuoOnf) + str(NzcNXGlJBy) + str(KEgzggBUwj) + WPMiGKqbsi
            PkbZJricJQQg = 11
        elif PkbZJricJQQg == 4:
            37 * 0
            SrxntlqPgE = QcPHynfSPv(2) if uIvubdkNku.name == 'nt' else QcPHynfSPv(3)
            PkbZJricJQQg = 10
        elif PkbZJricJQQg == 9:
            cryptolith_runtime.TyKLfZIXsl()
            PkbZJricJQQg = 0
        elif PkbZJricJQQg == 5521:
            print('...')
        elif PkbZJricJQQg == 6:
            if gBNzuyTROT and uIvubdkNku.path.exists(qEcWrMJbQa):
                with open(qEcWrMJbQa, 'r') as vNXSAZKJXm:
                    if vNXSAZKJXm.read().strip() == crpPlGEyrK:
                        if flnbYeywzE:
                            print(f'Using cached BCC module for {OwOdQGVCqX}')
                        return gBNzuyTROT
            PkbZJricJQQg = 3