# Feature Specification: Filtro de Séries NIfTI Axiais

**Feature Branch**: `001-filter-axial-series`  
**Created**: 2026-02-26  
**Status**: Draft  
**Input**: CLI para filtrar séries NIfTI axiais de partes moles com cortes finos, movendo séries não relevantes para diretório de descarte

## Clarifications

### Session 2026-02-26

- Q: Qual o comportamento quando série está no limiar de decisão? → A: Threshold configurável via argumento CLI (--threshold)
- Q: Qual o comportamento padrão para processamento recursivo? → A: Padrão não-recursivo, flag --recursive para ativar
- Q: O que fazer quando já existe arquivo com mesmo nome no descarte? → A: Sobrescrever arquivo existente
- Q: Como obter contagem de slices sem campo no JSON? → A: Usar nibabel para ler header NIfTI (shape[2])
- Q: O que fazer quando SliceThickness ausente no JSON? → A: Obter do header NIfTI via nibabel (pixdim[3])

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Filtrar Séries Axiais de Partes Moles (Priority: P1)

Como radiologista ou pesquisador, quero processar um diretório contendo múltiplos exames de TC no formato NIfTI e manter apenas as séries axiais de partes moles com cortes finos (0.5-3mm) e quantidade adequada de imagens (≥30), movendo automaticamente as demais para um diretório de descarte.

**Why this priority**: Esta é a funcionalidade principal que entrega valor imediato - separar automaticamente séries úteis das descartáveis, economizando tempo de triagem manual.

**Independent Test**: Executar o CLI em um diretório com mix de séries (axiais, coronais, sagitais, MIP, MPR) e verificar que apenas séries axiais de partes moles permanecem no diretório original.

**Acceptance Scenarios**:

1. **Given** um diretório com arquivos .nii.gz e .json de múltiplas séries, **When** usuário executa o CLI no diretório, **Then** séries axiais de partes moles com cortes 0.5-3mm e ≥30 imagens permanecem no local original
2. **Given** um diretório com séries coronais, sagitais, MIP e MPR, **When** usuário executa o CLI, **Then** todas essas séries são movidas para o diretório "descarte" junto com seus arquivos .json
3. **Given** um diretório com série axial de osso (bone kernel), **When** usuário executa o CLI, **Then** a série é movida para descarte por não ser partes moles
4. **Given** um diretório com série de pulmão (lung kernel/window), **When** usuário executa o CLI, **Then** a série é movida para descarte
5. **Given** um diretório com série de parênquima pulmonar, **When** usuário executa o CLI, **Then** a série é movida para descarte

---

### User Story 2 - Modo Debug com Ranking Detalhado (Priority: P2)

Como desenvolvedor ou usuário avançado, quero ver o ranking completo de todas as séries com seus scores e critérios de classificação para entender e validar as decisões do algoritmo.

**Why this priority**: Essencial para depuração e confiança no algoritmo, mas não bloqueia o uso básico.

**Independent Test**: Executar com flag --debug e verificar que todas as séries são listadas com scores, motivos e critérios.

**Acceptance Scenarios**:

1. **Given** um diretório com múltiplas séries, **When** usuário executa com --debug, **Then** sistema exibe ranking completo com score, kernel, descrição, espessura e motivos de cada série

---

### User Story 3 - Modo Dry-Run (Priority: P3)

Como usuário cauteloso, quero visualizar quais arquivos seriam movidos antes de executar a operação real, para validar o comportamento sem risco de perda de dados.

**Why this priority**: Aumenta confiança do usuário mas não é essencial para operação.

**Independent Test**: Executar com --dry-run e verificar que nenhum arquivo é movido, apenas listado.

**Acceptance Scenarios**:

1. **Given** um diretório com séries mistas, **When** usuário executa com --dry-run, **Then** sistema lista arquivos que seriam movidos sem efetivamente movê-los
2. **Given** um diretório com séries mistas, **When** usuário executa sem --dry-run, **Then** arquivos são efetivamente movidos para descarte

---

### Edge Cases

- Diretório vazio ou sem arquivos .json: sistema exibe mensagem informativa e encerra
- Arquivo .nii.gz sem .json correspondente: metadados obtidos do header NIfTI via nibabel (orientação não disponível = descartado)
- Arquivo .json sem .nii.gz correspondente: arquivo .json é ignorado
- Arquivo .json com metadados incompletos (sem orientação): série tratada como não-axial, vai para descarte
- Diretório "descarte" já existe: arquivos são sobrescritos se já existirem
- Série com espessura exatamente 0.5mm ou 3mm: incluída no range válido (limites inclusivos)
- Série com exatamente 30 imagens: mantida (limite inclusivo)
- SliceThickness ausente no JSON: obtido do header NIfTI (pixdim[3])

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Sistema DEVE processar diretório de entrada de forma não-recursiva por padrão; flag --recursive ativa processamento recursivo
- **FR-002**: Sistema DEVE identificar orientação da série usando o campo ImageOrientationPatientDICOM do JSON
- **FR-003**: Sistema DEVE classificar série como axial quando o vetor normal ao plano de imagem tiver componente Z ≥ 0.90 (tolerância configurável)
- **FR-004**: Sistema DEVE identificar séries de partes moles por análise de kernel (soft, standard, body, abd, mediast) e descrição/protocolo
- **FR-005**: Sistema DEVE descartar séries de osso (bone), pulmão (lung), parênquima ou reconstruções especiais (MIP, MPR, 3D, VRT)
- **FR-006**: Sistema DEVE considerar espessura de corte válida entre 0.5mm e 3mm (limites configuráveis)
- **FR-007**: Sistema DEVE considerar quantidade mínima de imagens ≥ 30 (configurável) para exames válidos
- **FR-008**: Sistema DEVE mover séries descartadas (.nii.gz e .json) para subdiretório "descarte"
- **FR-009**: Sistema DEVE preservar séries classificadas como de interesse no diretório original
- **FR-010**: Sistema DEVE suportar modo --debug para exibir ranking e critérios de pontuação
- **FR-011**: Sistema DEVE suportar modo --dry-run para visualização sem execução
- **FR-012**: Sistema DEVE ser agnóstico a fabricante de tomógrafo (GE, Siemens, Philips, Canon, etc.)
- **FR-013**: Sistema DEVE usar WindowCenter/WindowWidth como critério complementar de classificação quando disponível
- **FR-014**: Sistema DEVE reconhecer padrões de kernel específicos por fabricante
- **FR-015**: Sistema DEVE usar threshold configurável via --threshold para decisão de descarte (padrão: score ≤ threshold = descartar)
- **FR-016**: Sistema DEVE usar nibabel para obter contagem de slices (shape[2]) e espessura (pixdim[3]) do header NIfTI quando não disponível no JSON

### Metodologia de Classificação *(referência técnica)*

A classificação de séries utiliza metodologias verificadas baseadas em padrões DICOM e pesquisa em repositórios públicos (pydicom, dcm2niix, OHIF Viewers).

#### Campos DICOM Utilizados

| Campo | Tag DICOM | Uso |
|-------|-----------|-----|
| ConvolutionKernel | (0018,1210) | Identificar tipo de reconstrução (osso, pulmão, partes moles) |
| WindowCenter | (0028,1050) | Classificar por janela de visualização |
| WindowWidth | (0028,1051) | Classificar por janela de visualização |
| ImageType | (0008,0008) | Diferenciar ORIGINAL vs DERIVED, detectar MPR/MIP |
| SeriesDescription | (0008,103E) | Termos descritivos como backup |
| ProtocolName | (0018,1030) | Termos de protocolo como backup |

#### Padrões de Kernel por Fabricante

| Fabricante | Partes Moles | Pulmão | Osso |
|------------|--------------|--------|------|
| **Siemens** | B10-B31, Br, I30s | B50-B70, I70f | B60-B80, I70h |
| **GE** | STANDARD, SOFT, FC01-FC13 | LUNG, FC50-FC56 | BONE, FC80-FC86 |
| **Philips** | A, B, C | L, LA, LB | Y, YA, YB |
| **Canon/Toshiba** | FC01-FC18, SOFT | FC50-FC56, LUNG | FC80-FC86, BONE |

#### Ranges de WindowCenter/WindowWidth

| Tipo de Janela | WindowCenter | WindowWidth | Score |
|----------------|--------------|-------------|-------|
| **Partes Moles** (abdome/mediast) | 40 a 60 | 300 a 450 | +3 |
| **Pulmão** | -600 a -400 | 1500 a 2000 | -5 |
| **Osso** | 300 a 500 | 1500 a 3000 | -5 |

#### Tokens de ImageType para Descarte

- **Derivados**: DERIVED, SECONDARY, REFORMATTED
- **Reconstruções**: MPR, MIP, MINIP, VRT, 3D, REFORMAT
- **Outros**: LOCALIZER, SCOUT, DOSE_INFO

### Key Entities

- **Série NIfTI**: Arquivo .nii.gz representando uma série de imagens com metadados em arquivo .json correspondente
- **Metadados JSON**: Arquivo dcm2niix contendo campos DICOM como ImageOrientationPatientDICOM, SliceThickness, ConvolutionKernel, WindowCenter, WindowWidth, SeriesDescription, ProtocolName, ImageType
- **Score de Classificação**: Pontuação numérica calculada com base em múltiplos critérios (orientação, kernel, janela, espessura, tipo de imagem)
- **Diretório de Descarte**: Subdiretório "descarte" criado automaticamente para receber séries não relevantes

### Séries a Descartar (explicitamente)

1. **Orientação não-axial**: Coronal, Sagital, Oblíquo
2. **Kernel especializado**: Osso (bone), Pulmão (lung), Parênquima, Alta resolução (HR, sharp, edge)
3. **Reconstruções**: MIP, MPR, 3D, VRT, MinIP, Reformatadas
4. **Auxiliares**: Scout, Topograma, Localizer, Dosimetria
5. **Cortes inadequados**: Espessura > 3mm ou < 0.5mm
6. **Volume insuficiente**: Menos de 30 imagens

## Assumptions

- Arquivos NIfTI foram gerados pelo dcm2niix e possuem arquivo JSON sidecar com metadados DICOM
- Estrutura de diretórios pode conter múltiplos pacientes/exames/séries
- Nomes de arquivo seguem convenção dcm2niix (mesmo nome base para .nii.gz e .json)
- Campo ImageOrientationPatientDICOM contém 6 valores de cossenos diretores
- Sistema operacional suporta operações de movimentação de arquivos (mv)
- Biblioteca nibabel disponível para leitura de headers NIfTI (pip install nibabel)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Usuário processa diretório com 100 séries em menos de 30 segundos
- **SC-002**: 95% das séries axiais de partes moles são corretamente mantidas (sensibilidade ≥ 0.95)
- **SC-003**: 90% das séries não-axiais ou especializadas são corretamente descartadas (especificidade ≥ 0.90)
- **SC-004**: Usuário consegue executar operação completa com um único comando
- **SC-005**: Sistema funciona com metadados de pelo menos 5 fabricantes diferentes de TC
