const API_BASE_URL = ''; 

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

async function request(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (options.method && options.method !== 'GET') {
        const csrfToken = getCookie('csrf_access_token');
        if (csrfToken) {
            headers['X-CSRF-TOKEN'] = csrfToken;
        }
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
        credentials: 'include' 
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        const errorMsg = data.erro || data.msg || Object.values(data).flat().join(', ') || 'Erro na requisição';
        const error = new Error(errorMsg);
        error.status = response.status;
        throw error;
    }

    return data;
}

export const api = {
    login: (username, password) => request('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ username, password })
    }),
    registrar: (username, password) => request('/auth/registro', {
        method: 'POST',
        body: JSON.stringify({ username, password })
    }),
    logout: () => request('/auth/logout', { method: 'POST' }),
    
    getCategorias: () => request('/categorias'),
    createCategoria: (nome) => request('/categorias', {
        method: 'POST',
        body: JSON.stringify({ nome })
    }),
    updateCategoria: (id, nome) => request(`/categorias/${id}`, {
        method: 'PUT',
        body: JSON.stringify({ nome })
    }),
    deleteCategoria: (id) => request(`/categorias/${id}`, { method: 'DELETE' }),

    getProdutos: () => request('/produtos'),
    createProduto: (produto) => request('/produtos', {
        method: 'POST',
        body: JSON.stringify(produto)
    }),
    updateProduto: (id, produto) => request(`/produtos/${id}`, {
        method: 'PUT',
        body: JSON.stringify(produto)
    }),
    deleteProduto: (id) => request(`/produtos/${id}`, { method: 'DELETE' })
};