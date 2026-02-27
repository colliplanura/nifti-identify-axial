# Tasks: Filtro de Séries NIfTI Axiais

**Input**: Design documents from `/specs/001-filter-axial-series/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Testes unitários para lógica de pontuação e classificação (conforme constituição - testes equilibrados).

**Organization**: Tasks organizadas por user story para implementação e teste independentes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode executar em paralelo (arquivos diferentes, sem dependências)
- **[Story]**: User story associada (US1, US2, US3)
- Caminhos de arquivo incluídos nas descrições

---

## Phase 1: Setup

**Purpose**: Inicialização do projeto e estrutura básica

- [X] T001 Criar estrutura de diretórios nifti_filter/ e tests/
- [X] T002 [P] Criar requirements.txt com dependência nibabel>=4.0.0
- [X] T003 [P] Criar nifti_filter/__init__.py com versão e exports

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestrutura compartilhada por todas as user stories

**⚠️ CRÍTICO**: User stories dependem da conclusão desta fase

- [X] T004 Criar nifti_filter/nifti_utils.py com funções get_num_slices() e get_slice_thickness() usando nibabel
- [X] T005 [P] Criar nifti_filter/scoring.py migrando funções _as_text(), _normalizar_lista_strings() de nifti-identify-axial.py
- [X] T006 Expandir nifti_filter/scoring.py com pontuar_serie() incluindo WindowCenter/WindowWidth e padrões de kernel por fabricante
- [X] T007 [P] Criar nifti_filter/classifier.py com função is_axial_por_orientacao() migrada de nifti-identify-axial.py
- [X] T008 Expandir nifti_filter/classifier.py com função classificar_serie() que retorna AvaliacaoSerie
- [X] T009 Criar nifti_filter/file_ops.py com funções descobrir_series() e mover_para_descarte()

**Checkpoint**: Fundação pronta - implementação de user stories pode começar

---

## Phase 3: User Story 1 - Filtrar Séries Axiais de Partes Moles (Priority: P1) 🎯 MVP

**Goal**: Processar diretório e mover séries não relevantes para descarte/

**Independent Test**: Executar CLI em diretório com mix de séries e verificar separação correta

### Tests for User Story 1

- [X] T010 [P] [US1] Criar tests/fixtures/ com JSONs de exemplo (axial partes moles, coronal, MIP, bone, lung)
- [X] T011 [P] [US1] Criar tests/test_scoring.py com testes para pontuar_serie() em diferentes cenários
- [X] T012 [P] [US1] Criar tests/test_classifier.py com testes para is_axial_por_orientacao() e classificar_serie()

### Implementation for User Story 1

- [X] T013 [US1] Criar nifti_filter/cli.py com argparse configurando argumentos conforme contracts/cli-args.md
- [X] T014 [US1] Implementar função principal processar_diretorio() em nifti_filter/cli.py
- [X] T015 [US1] Criar entry point nifti-filter.py que importa e executa nifti_filter.cli.main()
- [X] T016 [US1] Implementar lógica de movimentação de arquivos (.nii.gz e .json) para descarte/
- [X] T017 [US1] Implementar saída formatada com resumo de séries mantidas e descartadas
- [X] T018 [US1] Testar manualmente com diretório /Users/colliplanura/nifti/

**Checkpoint**: User Story 1 funcional - filtragem básica operacional

---

## Phase 4: User Story 2 - Modo Debug com Ranking Detalhado (Priority: P2)

**Goal**: Exibir ranking completo de todas as séries com scores e critérios

**Independent Test**: Executar com --debug e verificar listagem detalhada

### Implementation for User Story 2

- [X] T019 [US2] Adicionar flag --debug em nifti_filter/cli.py
- [X] T020 [US2] Implementar função exibir_ranking_debug() em nifti_filter/cli.py
- [X] T021 [US2] Formatar saída debug com score, kernel, descrição, espessura, slices, motivos e decisão

**Checkpoint**: User Story 2 funcional - modo debug operacional

---

## Phase 5: User Story 3 - Modo Dry-Run (Priority: P3)

**Goal**: Visualizar quais arquivos seriam movidos sem executar operação

**Independent Test**: Executar com --dry-run e verificar que nenhum arquivo é movido

### Implementation for User Story 3

- [X] T022 [US3] Adicionar flag --dry-run em nifti_filter/cli.py
- [X] T023 [US3] Implementar lógica condicional que simula movimentação sem executar
- [X] T024 [US3] Formatar saída dry-run com prefixo [DRY-RUN] e lista de ações simuladas

**Checkpoint**: User Story 3 funcional - modo dry-run operacional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Melhorias que afetam múltiplas user stories

- [X] T025 [P] Atualizar README.md com instruções de uso do nifti-filter.py
- [X] T026 [P] Adicionar docstrings nas funções públicas de todos os módulos
- [X] T027 Implementar processamento recursivo (--recursive) em file_ops.py
- [X] T028 Validar edge cases: diretório vazio, JSON sem NIfTI, NIfTI sem JSON
- [X] T029 Executar quickstart.md para validação final

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Sem dependências - iniciar imediatamente
- **Phase 2 (Foundational)**: Depende de Phase 1 - BLOQUEIA user stories
- **Phase 3-5 (User Stories)**: Dependem de Phase 2
  - US1 → US2 → US3 (sequencial em prioridade)
  - Ou paralelo se múltiplos desenvolvedores
- **Phase 6 (Polish)**: Depende de user stories desejadas completas

### Within Each User Story

- Testes escritos antes da implementação (quando aplicável)
- Módulos base antes de módulos dependentes
- Core antes de integração
- Story completa antes de avançar para próxima

### Parallel Opportunities

**Phase 1-2:**
```
T001 → T002 [P], T003 [P]
     ↘
      T004 → T006
      T005 [P] ────┐
      T007 [P] ────┼─→ T008 → T009
                   │
```

**Phase 3 (US1):**
```
T010 [P], T011 [P], T012 [P]  (testes em paralelo)
            ↓
T013 → T014 → T015 → T016 → T017 → T018
```

**Phase 4-5 (US2, US3):**
```
T019 → T020 → T021  (US2)
       ↓
T022 → T023 → T024  (US3)
```

---

## Summary

| Fase | Tasks | Parallelizable |
|------|-------|----------------|
| Setup | 3 | 2 |
| Foundational | 6 | 3 |
| User Story 1 | 9 | 3 |
| User Story 2 | 3 | 0 |
| User Story 3 | 3 | 0 |
| Polish | 5 | 2 |
| **Total** | **29** | **10** |

### MVP Scope

User Story 1 (P1) é o MVP mínimo viável - após T018, o sistema já entrega valor ao usuário.

### Independent Test Criteria

- **US1**: `python nifti-filter.py /caminho/` move séries não-axiais para descarte/
- **US2**: `python nifti-filter.py --debug` exibe ranking detalhado
- **US3**: `python nifti-filter.py --dry-run` lista sem mover

### Implementation Strategy

1. **Fase 1-2**: Setup + Fundação (estimativa: 2-3 horas)
2. **Fase 3**: MVP funcional (estimativa: 3-4 horas)
3. **Fase 4-5**: Features adicionais (estimativa: 1-2 horas)
4. **Fase 6**: Polish (estimativa: 1 hora)

**Total estimado**: 7-10 horas de desenvolvimento
