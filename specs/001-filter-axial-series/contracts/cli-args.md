# CLI Contract: nifti-filter

**Feature**: 001-filter-axial-series  
**Date**: 2026-02-26

## Comando

```bash
python nifti-filter.py [DIRETÓRIO] [OPÇÕES]
```

## Argumentos Posicionais

| Argumento | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `DIRETÓRIO` | str | `.` (diretório atual) | Diretório contendo arquivos .nii.gz e .json |

## Opções

| Flag | Curto | Tipo | Default | Descrição |
|------|-------|------|---------|-----------|
| `--recursive` | `-r` | bool | False | Processar subdiretórios recursivamente |
| `--dry-run` | `-n` | bool | False | Apenas listar arquivos, não mover |
| `--debug` | `-d` | bool | False | Exibir ranking detalhado de todas as séries |
| `--threshold` | `-t` | int | 0 | Score mínimo para manter série (score ≤ threshold = descartar) |
| `--espessura-min` | | float | 0.5 | Espessura mínima de corte em mm |
| `--espessura-max` | | float | 3.0 | Espessura máxima de corte em mm |
| `--min-slices` | | int | 30 | Quantidade mínima de imagens na série |
| `--tolerancia-axial` | | float | 0.90 | Tolerância para classificar orientação como axial |
| `--help` | `-h` | | | Exibir ajuda e sair |

## Exemplos de Uso

### Uso básico

```bash
# Processar diretório atual
python nifti-filter.py

# Processar diretório específico
python nifti-filter.py /caminho/para/nifti/

# Processar recursivamente
python nifti-filter.py /caminho/para/nifti/ --recursive
```

### Modo dry-run

```bash
# Ver o que seria movido sem executar
python nifti-filter.py --dry-run

# Ver ranking detalhado
python nifti-filter.py --debug --dry-run
```

### Configurações personalizadas

```bash
# Threshold mais rigoroso
python nifti-filter.py --threshold 5

# Aceitar cortes até 5mm
python nifti-filter.py --espessura-max 5.0

# Aceitar séries com pelo menos 20 imagens
python nifti-filter.py --min-slices 20
```

## Saída

### Modo normal

```text
✅ Séries mantidas: 5
   - serie_axial_1.nii.gz (Score: 8)
   - serie_axial_2.nii.gz (Score: 6)
   ...

📦 Séries movidas para descarte/: 12
   - serie_coronal.nii.gz (Score: -2)
   - serie_mip.nii.gz (Score: -5)
   ...
```

### Modo debug

```text
[DEBUG] Ranking completo das séries:
 01. serie_axial_1.nii.gz
     Score: 8
     Kernel: Br40f
     Descrição: CT Abdomen
     Espessura: 3.0mm
     Slices: 120
     Motivos: axial por orientação, kernel partes moles, image type original
     Decisão: MANTER

 02. serie_coronal.nii.gz
     Score: -2
     Kernel: B60f
     Descrição: CT Coronary
     Espessura: 1.5mm
     Slices: 80
     Motivos: orientação não-axial
     Decisão: DESCARTAR
```

### Modo dry-run

```text
[DRY-RUN] Simulação - nenhum arquivo será movido

Seriam mantidos:
   - serie_axial_1.nii.gz (Score: 8)

Seriam movidos para descarte/:
   - serie_coronal.nii.gz (Score: -2)
   - serie_mip.nii.gz (Score: -5)
```

## Códigos de Saída

| Código | Significado |
|--------|-------------|
| 0 | Sucesso |
| 1 | Erro de argumento (diretório inválido, etc.) |
| 2 | Nenhum arquivo .json encontrado |

## Estrutura do Diretório de Descarte

```text
diretorio_entrada/
├── serie_mantida_1.nii.gz
├── serie_mantida_1.json
├── serie_mantida_2.nii.gz
├── serie_mantida_2.json
└── descarte/
    ├── serie_descartada_1.nii.gz
    ├── serie_descartada_1.json
    ├── serie_descartada_2.nii.gz
    └── serie_descartada_2.json
```
