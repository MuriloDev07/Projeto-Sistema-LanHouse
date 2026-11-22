# Front-end & UI/UX - Taciana Variedades (v4.1.0)

Documentação da arquitetura de interface, estilização responsiva e camada de comunicação cliente-servidor da aplicação **Taciana Variedades**.

> Para visão geral do sistema Full-Stack e instruções de execução, consulte o [README principal](../README.md).

## Filosofia de Design e Usabilidade

A interface foi projetada com foco em **clareza visual, velocidade de operação no balcão e zero dependência de frameworks pesados**, utilizando recursos nativos modernos dos navegadores (HTML5, CSS3 e ES6+ Modules):

* **Paleta Baseada na Identidade da Marca:** Cores extraídas diretamente do logotipo oficial (`#002B80` azul-marinho institucional, `#0099E5` ciano para ações primárias e `#2ECC71` verde-esmeralda para criação e indicadores positivos), garantindo alto contraste e leitura confortável durante todo o expediente.
* **Navegação Unificada por Abas (Produtos e Serviços):** Alternância instantânea no topo da área de trabalho entre o catálogo de **Produtos** (com controle de estoque) e a tabela de **Serviços** da lan house (impressões, documentos, Detran, boletos e observações operacionais), adaptando dinamicamente o placeholder da busca, os filtros rápidos e o botão principal de cadastro administrativo.
* **Sinalização Semântica de Estoque:** Etiquetas visuais automáticas na aba de Produtos que alertam o operador sobre a necessidade de reposição sem precisar ler números detalhados:
  * **Normal (`> 5 un.`):** Etiqueta verde suave.
  * **Estoque Baixo (`1 a 5 un.`):** Etiqueta amarela de alerta (`Baixo`).
  * **Esgotado (`0 un.`):** Etiqueta vermelha de atenção (`Esgotado`).
* **Experiência Sem Recarregamento (SPA-like):** Todas as operações de busca em tempo real, filtro por categoria ou grupo de atendimento, login e CRUD de produtos, categorias e serviços ocorrem de forma assíncrona com feedback imediato por notificações *toast*.

## Responsividade (*Mobile-First*)

O layout adapta-se automaticamente ao tamanho da tela sem duplicação de HTML:
* **Desktop (`>= 768px`):** Exibição em tabela estruturada de alta densidade para leitura rápida em monitores de balcão (4 colunas na visão pública e 5 colunas com ações no modo administrador).
* **Dispositivos Móveis (`< 768px`):** Via CSS Media Queries (`layout.css`), tanto as linhas de produtos quanto as de serviços (`<tr>`) transformam-se em **cartões individuais (*cards*)** com rótulos contextualizados via atributos `data-label`, permitindo que os operadores consultem e atualizem o catálogo diretamente pelo celular.

## Arquitetura Modular (`frontend/`)

```bash
frontend/
├── index.html          # Estrutura semântica, abas (Produtos/Serviços) e modais nativos (<dialog>)
├── css/
│   ├── variables.css   # Design Tokens (cores, espaçamentos, sombras e bordas)
│   ├── layout.css      # Cabeçalho, navegação por abas, busca, tabela responsiva e cards mobile
│   └── modals.css      # Estilização dos modais <dialog> e notificações toast
├── images/
│   ├── logo-tv-full.jpeg             # Logotipo oficial exibido no cabeçalho
│   └── logo-taciana-variedades.jpeg  # Ícone da aba do navegador (favicon)
└── js/
    ├── api.js          # Camada de serviço HTTP (Fetch API + credentials: 'include')
    ├── ui.js           # Manipulação segura do DOM, renderização e toasts
    └── main.js         # Orquestrador de estado, eventos e regras de validação
```

### Separação de Responsabilidades no JavaScript
1. **`js/api.js` (Comunicação):** Centraliza todas as chamadas `fetch` para os endpoints REST (`/auth`, `/produtos`, `/categorias` e `/servicos`) usando caminhos relativos (mesma origem) e `credentials: 'include'` para envio automático dos cookies JWT `HttpOnly`.
2. **`js/ui.js` (Apresentação):** Responsável exclusivamente por construir os elementos da interface (linhas/cards de produtos e serviços, abas de categorias e grupos de atendimento, fallback `—` para observações vazias, alternância entre modo consulta de balcão e modo administrativo e alertas *toast*), prevenindo XSS através de `textContent`.
3. **`js/main.js` (Controle & Estado):** Mantém o estado local em memória (`produtos`, `categorias`, `servicos` e `abaAtiva`), aplica filtros combinados de texto e categoria/grupo instantaneamente no cliente e coordena o ciclo de vida dos formulários nos modais `<dialog>`.