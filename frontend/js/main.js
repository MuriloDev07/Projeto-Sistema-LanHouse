import { api } from './api.js';
import { ui } from './ui.js';

const state = {
    produtos: [],
    categorias: [],
    categoriasMap: {},
    filtroCategoria: 'todas',
    termoBusca: '',
    isAdmin: false,
    username: ''
};

document.addEventListener('DOMContentLoaded', async () => {
    const savedUser = sessionStorage.getItem('admin_user');
    if (savedUser) {
        state.isAdmin = true;
        state.username = savedUser;
        ui.setAdminMode(true, savedUser);
    }

    setupEventListeners();
    await carregarDadosIniciais();
});

async function carregarDadosIniciais() {
    try {
        const [resCat, resProd] = await Promise.all([
            api.getCategorias(),
            api.getProdutos()
        ]);

        state.categorias = resCat.categorias || [];
        state.produtos = resProd.produtos || [];

        state.categoriasMap = {};
        state.categorias.forEach(c => {
            state.categoriasMap[c.id] = c.nome;
        });

        ui.renderCategorias(state.categorias, state.filtroCategoria);
        aplicarFiltrosERenderizar();
    } catch (err) {
        document.getElementById('estado-carregamento').textContent =
            'Erro ao conectar com a API. Verifique se o servidor Flask está rodando.';
        ui.showToast(err.message, 'error');
    }
}

function aplicarFiltrosERenderizar() {
    const filtrados = state.produtos.filter(prod => {
        const bateCategoria = state.filtroCategoria === 'todas' ||
            String(prod.categoria_id) === String(state.filtroCategoria);
        const bateNome = prod.nome.toLowerCase().includes(state.termoBusca.toLowerCase());
        return bateCategoria && bateNome;
    });

    ui.renderProdutos(filtrados, state.categoriasMap, state.isAdmin);
}

function setupEventListeners() {
    // 10. Registrar Novo Usuário (Restrito ao Admin logado)
    document.getElementById('btn-abrir-registro').addEventListener('click', () => {
        document.getElementById('form-registro').reset();
        document.getElementById('modal-registro').showModal();
    });

    document.getElementById('form-registro').addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('reg-username').value.trim();
        const password = document.getElementById('reg-password').value;
        const confirm = document.getElementById('reg-password-confirm').value;

        if (password !== confirm) {
            ui.showToast('As senhas não coincidem!', 'error');
            return;
        }

        try {
            await api.registrar(username, password);
            document.getElementById('modal-registro').close();
            ui.showToast(`Usuário "${username}" cadastrado com sucesso!`);
        } catch (err) {
            ui.showToast(err.message, 'error');
        }
    });

    document.getElementById('lista-filtros').addEventListener('click', (e) => {
        const btn = e.target.closest('.filter-pill');
        if (!btn) return;

        state.filtroCategoria = btn.dataset.categoria;
        ui.renderCategorias(state.categorias, state.filtroCategoria);
        aplicarFiltrosERenderizar();
    });

    document.querySelectorAll('[data-close]').forEach(btn => {
        btn.addEventListener('click', () => {
            document.getElementById(btn.dataset.close).close();
        });
    });

    document.getElementById('btn-auth').addEventListener('click', async () => {
        if (!state.isAdmin) {
            document.getElementById('form-login').reset();
            document.getElementById('modal-login').showModal();
        } else {
            try {
                await api.logout();
            } catch (_) {}
            state.isAdmin = false;
            state.username = '';
            sessionStorage.removeItem('admin_user');
            ui.setAdminMode(false);
            aplicarFiltrosERenderizar();
            ui.showToast('Sessão encerrada.');
        }
    });

    document.getElementById('form-login').addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('login-username').value.trim();
        const password = document.getElementById('login-password').value;

        try {
            const res = await api.login(username, password);
            state.isAdmin = true;
            state.username = res.user;
            sessionStorage.setItem('admin_user', res.user);

            ui.setAdminMode(true, res.user);
            aplicarFiltrosERenderizar();
            document.getElementById('modal-login').close();
            ui.showToast(`Bem-vindo, ${res.user}!`);
        } catch (err) {
            ui.showToast(err.message, 'error');
        }
    });

    document.getElementById('btn-novo-produto').addEventListener('click', () => {
        document.getElementById('form-produto').reset();
        document.getElementById('produto-id').value = '';
        document.getElementById('titulo-modal-produto').textContent = 'Novo Produto';
        document.getElementById('modal-produto').showModal();
    });

    document.getElementById('form-produto').addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = document.getElementById('produto-id').value;
        const payload = {
            nome: document.getElementById('produto-nome').value.trim(),
            categoria_id: Number(document.getElementById('produto-categoria').value),
            preco: parseFloat(document.getElementById('produto-preco').value),
            quantidade: parseInt(document.getElementById('produto-quantidade').value, 10)
        };

        try {
            if (id) {
                await api.updateProduto(id, payload);
                ui.showToast('Produto atualizado com sucesso!');
            } else {
                await api.createProduto(payload);
                ui.showToast('Produto cadastrado com sucesso!');
            }
            document.getElementById('modal-produto').close();
            await carregarDadosIniciais();
        } catch (err) {
            if (err.status === 401 || err.status === 403) {
                ui.showToast('Sessão expirada ou sem permissão. Faça login novamente.', 'error');
            } else {
                ui.showToast(err.message, 'error');
            }
        }
    });

    document.getElementById('lista-produtos').addEventListener('click', async (e) => {
        const btnEdit = e.target.closest('[data-edit-prod]');
        const btnDel = e.target.closest('[data-del-prod]');

        if (btnEdit) {
            const prod = state.produtos.find(p => String(p.id) === btnEdit.dataset.editProd);
            if (!prod) return;

            document.getElementById('produto-id').value = prod.id;
            document.getElementById('produto-nome').value = prod.nome;
            document.getElementById('produto-categoria').value = prod.categoria_id;
            document.getElementById('produto-preco').value = prod.preco;
            document.getElementById('produto-quantidade').value = prod.quantidade;
            document.getElementById('titulo-modal-produto').textContent = 'Editar Produto';
            document.getElementById('modal-produto').showModal();
        }

        if (btnDel) {
            const { delProd: id, nome } = btnDel.dataset;
            if (!confirm(`Tem certeza que deseja excluir "${nome}"?`)) return;

            try {
                await api.deleteProduto(id);
                ui.showToast('Produto removido!');
                await carregarDadosIniciais();
            } catch (err) {
                ui.showToast(err.message, 'error');
            }
        }
    });

    document.getElementById('btn-abrir-categorias').addEventListener('click', () => {
        document.getElementById('modal-categorias').showModal();
    });

    document.getElementById('form-nova-categoria').addEventListener('submit', async (e) => {
        e.preventDefault();
        const input = document.getElementById('nova-categoria-nome');
        const nome = input.value.trim();
        if (!nome) return;

        try {
            await api.createCategoria(nome);
            input.value = '';
            ui.showToast('Categoria criada!');
            await carregarDadosIniciais();
        } catch (err) {
            ui.showToast(err.message, 'error');
        }
    });

    document.getElementById('lista-categorias-crud').addEventListener('click', async (e) => {
        const btnEdit = e.target.closest('[data-edit-cat]');
        const btnDel = e.target.closest('[data-del-cat]');

        if (btnEdit) {
            const id = btnEdit.dataset.editCat;
            const novoNome = prompt('Novo nome para a categoria:', btnEdit.dataset.nome);
            if (!novoNome || novoNome.trim() === btnEdit.dataset.nome) return;

            try {
                await api.updateCategoria(id, novoNome.trim());
                ui.showToast('Categoria renomeada!');
                await carregarDadosIniciais();
            } catch (err) {
                ui.showToast(err.message, 'error');
            }
        }

        if (btnDel) {
            const id = btnDel.dataset.delCat;
            if (!confirm('Deseja excluir esta categoria?')) return;

            try {
                await api.deleteCategoria(id);
                ui.showToast('Categoria excluída!');
                await carregarDadosIniciais();
            } catch (err) {
                ui.showToast(err.message, 'error');
            }
        }
    });
}