# NIfTI Filter

[![PyPI version](https://badge.fury.io/py/nifti-filter.svg)](https://badge.fury.io/py/nifti-filter)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Filtro de séries NIfTI axiais de partes moles com cortes finos.

## Instalação

### Via PyPI (recomendado)

```bash
pip install nifti-filter
```

### Via repositório

```bash
pip install git+https://github.com/colliplanura/nifti-identify-axial.git
```

### Desenvolvimento local

```bash
git clone https://github.com/colliplanura/nifti-identify-axial.git
cd nifti-identify-axial
pip install -e ".[dev]"
```

## Uso Básico

```bash
# Processar diretório atual
nifti-filter

# Processar diretório específico
nifti-filter /caminho/para/nifti/

# Processar recursivamente
nifti-filter /caminho/ --recursive
```

## Modo Dry-Run

Ver o que seria movido sem executar:

```bash
nifti-filter --dry-run
```

## Modo Debug

Exibir ranking detalhado de todas as séries:

```bash
nifti-filter --debug
```

## Opções Completas

```
usage: nifti-filter [-h] [-r] [-n] [-d] [-t THRESHOLD]
                    [--espessura-min ESPESSURA_MIN]
                    [--espessura-max ESPESSURA_MAX] [--min-slices MIN_SLICES]
                    [--tolerancia-axial TOLERANCIA_AXIAL] [-V]
                    [diretorio]

positional arguments:
  diretorio             Diretório contendo arquivos .nii.gz e .json

options:
  -r, --recursive       Processar subdiretórios recursivamente
  -n, --dry-run         Apenas listar arquivos, não mover
  -d, --debug           Exibir ranking detalhado de todas as séries
  -t, --threshold       Score mínimo para manter série (default: 0)
  --espessura-min       Espessura mínima de corte em mm (default: 0.5)
  --espessura-max       Espessura máxima de corte em mm (default: 3.0)
  --min-slices          Quantidade mínima de imagens na série (default: 30)
  --tolerancia-axial    Tolerância para classificar orientação como axial
  -V, --version         Mostrar versão
```

## Critérios de Classificação

### Séries Mantidas
- Orientação axial (componente Z dominante)
- Kernel de partes moles (soft, stnd, b10-b30, fc01-fc13)
- Espessura entre 0.5mm e 3.0mm
- Mínimo de 30 imagens
- WindowCenter/WindowWidth de partes moles

### Séries Descartadas
- Orientação sagital ou coronal
- Kernel de pulmão ou osso
- Reformatações (MIP, MPR, 3D, VRT)
- Séries derivadas/secundárias
- Localizadores/scouts

## Saída

Arquivos não relevantes são movidos para `descarte/` no mesmo diretório do arquivo original.

## Licença

MIT
