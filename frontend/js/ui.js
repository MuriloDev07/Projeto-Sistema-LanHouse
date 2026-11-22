export const ui = {
    showToast(message, type = 'success') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        container.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3500);
    },

    setAdminMode(isAdmin, username = '', abaAtiva = 'produtos') {
        const btnAuth = document.getElementById('btn-auth');
        const btnCategorias = document.getElementById('btn-abrir-categorias');
        const btnRegistro = document.getElementById('btn-abrir-registro');
        const btnNovoProduto = document.getElementById('btn-novo-produto');
        const btnNovoServico = document.getElementById('btn-novo-servico');
        const colsAdmin = document.querySelectorAll('.col-admin');

        if (isAdmin) {
            btnAuth.textContent = `Sair (${username})`;
            btnCategorias.classList.remove('hidden');
            btnRegistro.classList.remove('hidden');
            btnNovoProduto.classList.toggle('hidden', abaAtiva !== 'produtos');
            btnNovoServico.classList.toggle('hidden', abaAtiva !== 'servicos');
            colsAdmin.forEach(col => col.classList.remove('hidden'));
        } else {
            btnAuth.textContent = 'Entrar como Admin';
            btnCategorias.classList.add('hidden');
            btnRegistro.classList.add('hidden');
            btnNovoProduto.classList.add('hidden');
            btnNovoServico.classList.add('hidden');
            colsAdmin.forEach(col => col.classList.add('hidden'));
        }
    },

    renderCategorias(categorias, categoriaAtivaId) {
        const filtersBar = document.getElementById('lista-filtros');
        const selectCategoria = document.getElementById('produto-categoria');
        const listaCrud = document.getElementById('lista-categorias-crud');

        filtersBar.innerHTML = `
            <button class="filter-pill ${categoriaAtivaId === 'todas' ? 'active' : ''}" data-categoria="todas">
                Todos
            </button>
        `;
        categorias.forEach(cat => {
            const isActive = String(cat.id) === String(categoriaAtivaId) ? 'active' : '';
            filtersBar.innerHTML += `
                <button class="filter-pill ${isActive}" data-categoria="${cat.id}">
                    ${cat.nome}
                </button>
            `;
        });

        selectCategoria.innerHTML = '<option value="">Selecione uma categoria...</option>';
        categorias.forEach(cat => {
            selectCategoria.innerHTML += `<option value="${cat.id}">${cat.nome}</option>`;
        });

        listaCrud.innerHTML = '';
        categorias.forEach(cat => {
            listaCrud.innerHTML += `
                <li class="category-item">
                    <span><strong>${cat.nome}</strong></span>
                    <div style="display: flex; gap: 6px;">
                        <button type="button" class="btn btn-secondary btn-sm" data-edit-cat="${cat.id}" data-nome="${cat.nome}">
                            Renomear
                        </button>
                        <button type="button" class="btn btn-danger btn-sm" data-del-cat="${cat.id}">
                            Excluir
                        </button>
                    </div>
                </li>
            `;
        });
    },

    renderProdutos(produtos, categoriasMap, isAdmin) {
        const tbody = document.getElementById('lista-produtos');
        const statusMsg = document.getElementById('estado-carregamento');

        if (produtos.length === 0) {
            tbody.innerHTML = '';
            statusMsg.textContent = 'Nenhum produto encontrado.';
            statusMsg.classList.remove('hidden');
            return;
        }

        statusMsg.classList.add('hidden');
        tbody.innerHTML = '';

        produtos.forEach(prod => {
            const nomeCategoria = categoriasMap[prod.categoria_id] || 'Sem categoria';
            const precoFormatado = Number(prod.preco).toLocaleString('pt-BR', {
                style: 'currency',
                currency: 'BRL'
            });

            let stockClass = 'stock-ok';
            let stockLabel = `${prod.quantidade} un.`;
            if (prod.quantidade === 0) {
                stockClass = 'stock-out';
                stockLabel = 'Esgotado (0)';
            } else if (prod.quantidade <= 5) {
                stockClass = 'stock-low';
                stockLabel = `${prod.quantidade} un. (Baixo)`;
            }

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${prod.nome}</td>
                <td data-label="Categoria">${nomeCategoria}</td>
                <td data-label="Preço" class="price-cell">${precoFormatado}</td>
                <td data-label="Estoque">
                    <span class="badge-stock ${stockClass}">${stockLabel}</span>
                </td>
                <td data-label="Ações" class="${isAdmin ? '' : 'hidden'}">
                    <div style="display: flex; gap: 6px;">
                        <button type="button" class="btn btn-secondary btn-sm" data-edit-prod="${prod.id}">
                            Editar
                        </button>
                        <button type="button" class="btn btn-danger btn-sm" data-del-prod="${prod.id}" data-nome="${prod.nome}">
                            Excluir
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
    },

    renderGruposServicos(servicos, grupoAtivo) {
        const filtersBar = document.getElementById('lista-filtros-servicos');
        const gruposBase = ['Impressões', 'Documentos', 'Detran', 'Boletos'];
        const gruposExtras = servicos.map(s => s.grupo).filter(g => !gruposBase.includes(g));
        const todosGrupos = [...gruposBase, ...new Set(gruposExtras)];

        filtersBar.innerHTML = `
            <button class="filter-pill ${grupoAtivo === 'todos' ? 'active' : ''}" data-grupo="todos">
                Todos
            </button>
        `;
        todosGrupos.forEach(grupo => {
            const isActive = grupo === grupoAtivo ? 'active' : '';
            filtersBar.innerHTML += `
                <button class="filter-pill ${isActive}" data-grupo="${grupo}">
                    ${grupo}
                </button>
            `;
        });
    },

    renderServicos(servicos, isAdmin) {
        const tbody = document.getElementById('lista-servicos');
        const statusMsg = document.getElementById('estado-carregamento-servicos');

        if (servicos.length === 0) {
            tbody.innerHTML = '';
            statusMsg.textContent = 'Nenhum serviço encontrado.';
            statusMsg.classList.remove('hidden');
            return;
        }

        statusMsg.classList.add('hidden');
        tbody.innerHTML = '';

        servicos.forEach(serv => {
            const precoFormatado = Number(serv.preco).toLocaleString('pt-BR', {
                style: 'currency',
                currency: 'BRL'
            });

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${serv.nome}</td>
                <td data-label="Grupo">${serv.grupo}</td>
                <td data-label="Preço" class="price-cell">${precoFormatado}</td>
                <td data-label="Observação">${serv.observacao || '—'}</td>
                <td data-label="Ações" class="${isAdmin ? '' : 'hidden'}">
                    <div style="display: flex; gap: 6px;">
                        <button type="button" class="btn btn-secondary btn-sm" data-edit-serv="${serv.id}">
                            Editar
                        </button>
                        <button type="button" class="btn btn-danger btn-sm" data-del-serv="${serv.id}" data-nome="${serv.nome}">
                            Excluir
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }
};