# Data Model: Filtro de Séries NIfTI Axiais

**Feature**: 001-filter-axial-series  
**Date**: 2026-02-26

## Entidades

### SerieNIfTI

Representa uma série de imagens tomográficas no formato NIfTI.

| Campo | Tipo | Fonte | Descrição |
|-------|------|-------|-----------|
| `arquivo_nii` | str | Sistema de arquivos | Caminho absoluto do arquivo .nii.gz |
| `arquivo_json` | str | Sistema de arquivos | Caminho absoluto do arquivo .json correspondente |
| `orientacao` | list[float] | JSON: ImageOrientationPatientDICOM | 6 valores de cossenos diretores |
| `espessura` | float | JSON: SliceThickness ou NIfTI: pixdim[3] | Espessura do corte em mm |
| `num_slices` | int | NIfTI: shape[2] | Quantidade de imagens na série |
| `kernel` | str | JSON: ConvolutionKernel | Kernel de reconstrução |
| `descricao` | str | JSON: SeriesDescription | Descrição da série |
| `protocolo` | str | JSON: ProtocolName | Nome do protocolo |
| `image_type` | list[str] | JSON: ImageType | Tokens de tipo de imagem |
| `window_center` | float | JSON: WindowCenter | Centro da janela (opcional) |
| `window_width` | float | JSON: WindowWidth | Largura da janela (opcional) |
| `fabricante` | str | JSON: Manufacturer | Fabricante do equipamento |

### AvaliacaoSerie

Resultado da avaliação de uma série com score e critérios.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `serie` | SerieNIfTI | Referência à série avaliada |
| `score` | int | Pontuação calculada |
| `motivos` | list[str] | Lista de critérios que contribuíram para o score |
| `is_axial` | bool | True se orientação é axial |
| `is_partes_moles` | bool | True se kernel indica partes moles |
| `espessura_valida` | bool | True se espessura está no range 0.5-3mm |
| `num_slices_valido` | bool | True se num_slices ≥ 30 |
| `descarte` | bool | True se série deve ser descartada (score ≤ threshold) |

### ConfiguracaoCLI

Parâmetros de configuração do CLI.

| Campo | Tipo | Default | Descrição |
|-------|------|---------|-----------|
| `diretorio` | str | "." | Diretório de entrada |
| `recursive` | bool | False | Processar subdiretórios |
| `dry_run` | bool | False | Apenas listar, não mover |
| `debug` | bool | False | Exibir ranking detalhado |
| `threshold` | int | 0 | Score mínimo para manter série |
| `espessura_min` | float | 0.5 | Espessura mínima em mm |
| `espessura_max` | float | 3.0 | Espessura máxima em mm |
| `min_slices` | int | 30 | Quantidade mínima de imagens |
| `tolerancia_axial` | float | 0.90 | Tolerância para classificar como axial |

## Diagrama de Relacionamentos

```text
ConfiguracaoCLI
      │
      ▼
[Descoberta de Arquivos]
      │
      ▼
SerieNIfTI (1..N)
      │
      ▼
[Avaliação/Pontuação]
      │
      ▼
AvaliacaoSerie (1..N)
      │
      ├── descarte=True ──► mover para /descarte/
      │
      └── descarte=False ──► manter no local
```

## Regras de Validação

### Orientação Axial

```python
# Vetor normal ao plano de imagem
nx = ry * cz - rz * cy
ny = rz * cx - rx * cz
nz = rx * cy - ry * cx

# É axial se componente Z é dominante
is_axial = abs(nz) >= tolerancia_axial  # default 0.90
```

### Score de Classificação

| Critério | Condição | Score |
|----------|----------|-------|
| Orientação axial | abs(nz) ≥ 0.90 | +4 |
| ImageType ORIGINAL | "original" in image_type | +2 |
| ImageType PRIMARY | "primary" in image_type | +1 |
| Kernel partes moles | soft, standard, body, br | +3 |
| Descrição/protocolo compatível | abd, mediast, body | +2 |
| Janela partes moles | WC=40-60, WW=300-450 | +3 |
| Kernel osso/pulmão | bone, lung, sharp, edge | -4 |
| Descrição/protocolo especializado | mip, mpr, 3d, sag, cor | -3 |
| Janela pulmão/osso | WC<0 ou WC>200 | -5 |
| ImageType derivado | derived, secondary | -3 |
| Espessura fina (< 1.5mm) | espessura < 1.5 | -1 |
| Espessura rotina (2-5mm) | 2.0 ≤ espessura ≤ 5.0 | +1 |
| Localizer/Scout | "localizer" ou "scout" em image_type | -10 |

### Decisão de Descarte

```python
descarte = (
    score <= threshold or       # Score abaixo do limiar
    not is_axial or             # Não é axial
    espessura < 0.5 or          # Muito fino
    espessura > 3.0 or          # Muito grosso
    num_slices < 30             # Poucas imagens
)
```
