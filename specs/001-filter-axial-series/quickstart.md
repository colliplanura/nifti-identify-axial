# Quickstart: Filtro de Séries NIfTI Axiais

## Instalação

```bash
# Clonar repositório
git clone <repo-url>
cd nifti-identify-axial

# Instalar dependências
pip install -r requirements.txt
```

## Uso Rápido

```bash
# Processar diretório com arquivos NIfTI
python nifti-filter.py /caminho/para/nifti/

# Ver o que seria filtrado (sem mover arquivos)
python nifti-filter.py /caminho/para/nifti/ --dry-run

# Ver ranking detalhado
python nifti-filter.py /caminho/para/nifti/ --debug
```

## O que o filtro faz

1. **Analisa** todos os arquivos .json no diretório
2. **Pontua** cada série baseado em critérios de classificação
3. **Move** séries não relevantes para subdiretório `descarte/`
4. **Mantém** séries axiais de partes moles no local original

## Séries Mantidas

- Orientação **axial**
- Kernel de **partes moles** (soft, standard, body, abd)
- Espessura entre **0.5mm e 3mm**
- Pelo menos **30 imagens**

## Séries Descartadas

- Coronal, Sagital, Oblíquo
- Kernel de osso (bone) ou pulmão (lung)
- Reconstruções MIP, MPR, 3D
- Scout, Topograma, Localizer
- Cortes muito finos (< 0.5mm) ou grossos (> 3mm)
- Séries com poucas imagens (< 30)

## Estrutura de Saída

```text
seu_diretorio/
├── serie_axial_abdome.nii.gz    # Mantido
├── serie_axial_abdome.json
└── descarte/
    ├── serie_coronal.nii.gz     # Movido
    ├── serie_coronal.json
    ├── serie_mip.nii.gz         # Movido
    └── serie_mip.json
```

## Opções Comuns

| Opção | Descrição |
|-------|-----------|
| `--dry-run` | Simular sem mover arquivos |
| `--debug` | Ver ranking completo |
| `--recursive` | Processar subdiretórios |
| `--threshold N` | Ajustar limiar de score |

## Próximos Passos

- Consulte [contracts/cli-args.md](contracts/cli-args.md) para lista completa de opções
- Consulte [data-model.md](data-model.md) para entender a lógica de pontuação
