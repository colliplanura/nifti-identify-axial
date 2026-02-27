#!/usr/bin/env python3
"""
nifti-filter: Filtro de séries NIfTI axiais de partes moles.

Uso:
    python nifti-filter.py [DIRETÓRIO] [OPÇÕES]
    
Exemplos:
    python nifti-filter.py                    # Processa diretório atual
    python nifti-filter.py /caminho/nifti/    # Processa diretório específico
    python nifti-filter.py --dry-run          # Simula sem mover arquivos
    python nifti-filter.py --debug            # Exibe ranking detalhado

Para ajuda completa:
    python nifti-filter.py --help
"""

import sys

from nifti_filter.cli import main

if __name__ == "__main__":
    sys.exit(main())
