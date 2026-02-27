# Research: Filtro de Séries NIfTI Axiais

**Feature**: 001-filter-axial-series  
**Date**: 2026-02-26

## Decisões Técnicas

### 1. Leitura de Headers NIfTI

**Decisão**: Usar biblioteca `nibabel` para leitura de headers NIfTI

**Racional**:
- Biblioteca padrão para NIfTI em Python, bem mantida
- Dependências mínimas (apenas numpy)
- Lê apenas header sem carregar imagem em memória (`nib.load()` usa array proxy)
- Suporta .nii.gz nativamente

**Alternativas consideradas**:
- SimpleITK: Pesada (~50-100MB), inclui binários ITK compilados
- nilearn: Wrapper sobre nibabel com dependências adicionais
- Leitura manual do header: Complexo, propenso a erros

**Código de referência**:
```python
import nibabel as nib

def get_nifti_info(path: str) -> tuple[int, float]:
    """Retorna (num_slices, slice_thickness) do header NIfTI."""
    img = nib.load(path)
    shape = img.header.get_data_shape()
    pixdim = img.header['pixdim']
    return shape[2], pixdim[3]  # slices axiais, espessura em Z
```

### 2. Classificação de Kernel por Fabricante

**Decisão**: Usar tabela de padrões de kernel baseada em pesquisa de repositórios públicos

**Racional**:
- Padrões variam significativamente entre fabricantes
- Nomenclatura não é padronizada no DICOM
- Tabela baseada em pydicom, dcm2niix, OHIF Viewers

**Padrões identificados**:

| Fabricante | Partes Moles | Pulmão | Osso |
|------------|--------------|--------|------|
| Siemens | B10-B31, Br, I30s | B50-B70, I70f | B60-B80, I70h |
| GE | STANDARD, SOFT, FC01-FC13 | LUNG, FC50-FC56 | BONE, FC80-FC86 |
| Philips | A, B, C | L, LA, LB | Y, YA, YB |
| Canon/Toshiba | FC01-FC18, SOFT | FC50-FC56, LUNG | FC80-FC86, BONE |

### 3. WindowCenter/WindowWidth como Critério Complementar

**Decisão**: Usar ranges de janela como score adicional, não como critério eliminatório

**Racional**:
- Janela pode não estar presente em todos os JSONs
- É indicador secundário, kernel é mais confiável
- Ajuda a diferenciar quando kernel é ambíguo

**Ranges**:
- Partes Moles: WC=40-60, WW=300-450 → +3 score
- Pulmão: WC=-600 a -400, WW=1500-2000 → -5 score
- Osso: WC=300-500, WW=1500-3000 → -5 score

### 4. Threshold de Score

**Decisão**: Threshold configurável via CLI com valor padrão 0

**Racional**:
- Permite ajuste fino pelo usuário
- Score ≤ 0 indica série provavelmente não relevante
- Evita rigidez em casos de borda

### 5. Processamento de Diretórios

**Decisão**: Não-recursivo por padrão, flag --recursive para ativar

**Racional**:
- Mais seguro como padrão
- Evita processamento acidental de subdiretórios
- Comportamento previsível

### 6. Conflitos de Arquivo

**Decisão**: Sobrescrever arquivo existente no diretório de descarte

**Racional**:
- Simplifica lógica
- Arquivos descartados são menos importantes
- Evita acúmulo de versões duplicadas

### 7. Fallback para Dados Ausentes

**Decisão**: Obter SliceThickness e contagem de slices do header NIfTI quando ausentes no JSON

**Racional**:
- Mantém funcionalidade mesmo com JSONs incompletos
- nibabel sempre tem acesso ao header
- Garante critérios de espessura e quantidade de imagens

## Código Existente para Reutilização

Do arquivo `nifti-identify-axial.py`:

| Função | Reutilização |
|--------|--------------|
| `_as_text()` | ✅ Mover para `scoring.py` |
| `_normalizar_lista_strings()` | ✅ Mover para `scoring.py` |
| `_is_axial_por_orientacao()` | ✅ Mover para `classifier.py` |
| `_pontuar_serie_json()` | ✅ Expandir em `scoring.py` (adicionar WindowCenter/Width) |
| `identificar_serie_local()` | ❌ Reescrever em `file_ops.py` (adicionar recursividade, movimentação) |

## Dependências Finais

```text
# requirements.txt
nibabel>=4.0.0
```

Bibliotecas padrão utilizadas:
- argparse (CLI)
- json (leitura de metadados)
- os, shutil (operações de arquivo)
- glob (descoberta de arquivos)
