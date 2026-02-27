<!--
SYNC IMPACT REPORT
==================
Version: 1.0.0 → 1.1.0 (MINOR - Adição de princípio)

Princípios Modificados:
- Adicionado V. Sincronização de Artefatos SDD

Templates Verificados:
✅ plan-template.md - Compatível
✅ spec-template.md - Compatível
✅ tasks-template.md - Compatível

TODOs Pendentes: Nenhum
-->

# Constituição do Projeto NIfTI Identify Axial

## Princípios Fundamentais

### I. Simplicidade

O código DEVE ser simples, pequeno e direto ao ponto. Aplicar rigorosamente o princípio YAGNI (You Aren't Gonna Need It): não implementar funcionalidades "por precaução" ou "para o futuro".

- Cada função DEVE ter uma responsabilidade clara e única
- Evitar abstrações prematuras e camadas desnecessárias
- Preferir soluções explícitas sobre implícitas
- Complexidade adicional DEVE ser justificada com caso de uso concreto

**Racional**: Código simples é mais fácil de manter, testar e entender. Over-engineering aumenta tempo de desenvolvimento e dificulta manutenção.

### II. Reutilização de Código

Antes de implementar nova funcionalidade, DEVE-SE verificar se já existe código reutilizável no projeto ou em bibliotecas padrão.

- Funções utilitárias DEVEM ser extraídas quando há padrão repetido
- Preferir bibliotecas padrão do Python sobre dependências externas
- Duplicação de código DEVE ser eliminada mediante refatoração

**Racional**: Reutilização reduz bugs, melhora consistência e diminui a superfície de manutenção.

### III. Testes Equilibrados

Testes DEVEM validar funcionalidades críticas sem excessos. Focar em cenários de uso real e casos de borda relevantes.

- Testes unitários para funções de lógica de negócio (pontuação, classificação)
- Testes de integração apenas quando necessário para validar fluxo completo
- Evitar testes redundantes ou que testam implementação ao invés de comportamento
- Cobertura deve ser pragmática, não um objetivo em si

**Racional**: Testes demais são tão problemáticos quanto testes de menos - tornam refatorações custosas e podem dar falsa sensação de segurança.

### IV. Documentação Essencial

Documentação DEVE seguir o conjunto mínimo de artefatos previstos na metodologia SDD (Specification-Driven Development).

- README.md com propósito, instalação e uso básico
- Docstrings apenas em funções públicas ou complexas
- Comentários inline apenas para lógica não-óbvia
- Especificações e planos somente quando feature justificar

**Racional**: Documentação excessiva desatualiza rapidamente e compete com código como fonte de verdade.

### V. Sincronização de Artefatos SDD

Os artefatos da metodologia SDD DEVEM ser mantidos sempre atualizados. A cada novo prompt ou alteração no projeto:

- `spec.md` DEVE refletir requisitos e cenários de usuário atuais
- `plan.md` DEVE ser atualizado com mudanças de contexto técnico ou estrutura
- `tasks.md` DEVE refletir o estado atual das tarefas (concluídas, pendentes, novas)

Atualizações DEVEM ser incrementais e focadas apenas nas seções afetadas pela mudança. Não reescrever documentos inteiros desnecessariamente.

**Racional**: Artefatos desatualizados levam a decisões incorretas e retrabalho. Manter sincronia entre código e documentação é essencial para a metodologia SDD.

## Stack Técnica

- **Linguagem**: Python 3.8+
- **Tipo de Projeto**: CLI (Command Line Interface)
- **Dependências**: Mínimas (bibliotecas padrão sempre que possível)
- **Entrada/Saída**: Arquivos JSON (dcm2niix) → Texto formatado no terminal
- **Plataforma Alvo**: Linux, macOS, Windows

## Fluxo de Trabalho

1. **Entender** o problema antes de implementar
2. **Verificar** código existente para reutilização
3. **Implementar** solução mínima viável
4. **Testar** cenários relevantes
5. **Documentar** apenas o necessário

Alterações DEVEM ser incrementais e verificáveis. Commits devem ser atômicos e com mensagens descritivas em português.

## Governança

Esta constituição tem precedência sobre outras práticas do projeto. Emendas requerem:

1. Justificativa documentada para a mudança
2. Incremento de versão seguindo versionamento semântico:
   - MAJOR: Remoção ou redefinição de princípio
   - MINOR: Adição de princípio ou seção
   - PATCH: Clarificações e correções textuais
3. Atualização da data de emenda

Toda contribuição DEVE verificar conformidade com os princípios acima. Desvios DEVEM ser explicitamente justificados.

**Versão**: 1.1.0 | **Ratificado**: 2026-02-26 | **Última Emenda**: 2026-02-26
