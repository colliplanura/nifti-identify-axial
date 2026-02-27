# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [0.1.0] - 2026-02-26

### Adicionado

- CLI `nifti-filter` para filtrar séries NIfTI axiais de partes moles
- Suporte a modo `--dry-run` para simulação sem movimentação de arquivos
- Suporte a modo `--debug` para exibição de ranking detalhado com scores
- Processamento recursivo via flag `--recursive`
- Threshold configurável via `--threshold`
- Parâmetros configuráveis de espessura (`--espessura-min`, `--espessura-max`)
- Parâmetro configurável de quantidade mínima de slices (`--min-slices`)
- Tolerância configurável para classificação axial (`--tolerancia-axial`)
- Classificação por kernel (partes moles, pulmão, osso) com padrões multi-fabricante
- Classificação por WindowCenter/WindowWidth
- Detecção de reconstruções (MIP, MPR, 3D, VRT)
- Fallback para header NIfTI via nibabel quando metadados JSON incompletos
- Testes unitários para módulos de scoring e classificação
- Empacotamento PyPI compatível (pyproject.toml com hatchling)
- Documentação em português

### Técnico

- Python 3.8+ compatível
- Dependência única: nibabel>=4.0.0
- Estrutura modular: `nifti_filter/` com 5 módulos especializados
- 29 testes unitários com pytest

---

## Sobre

Este projeto está sendo desenvolvido no âmbito do **Doutorado em Ciências Médicas** 
pelo **Instituto D'Or de Pesquisa e Ensino (IDOR)**.

**Autor**: Sandro Colli (Citação: Colli, Sandro)

**Orientação**:
- Dr. Alysson Roncally Silva Carvalho
- Dr. Rodrigo Basilio
- Dra. Rosana Souza Rodrigues

**Repositório**: https://github.com/colliplanura/nifti-identify-axial

[0.1.0]: https://github.com/colliplanura/nifti-identify-axial/releases/tag/v0.1.0
