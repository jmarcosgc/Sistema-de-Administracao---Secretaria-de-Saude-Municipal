document.addEventListener('DOMContentLoaded', () => {
    
    const tableBody = document.getElementById('tableBody');
    const searchInput = document.getElementById('searchInput');
    const btnBuscar = document.getElementById('btnBuscar');
    const btnNovo = document.getElementById('btnNovo');
    const btnEditar = document.getElementById('btnEditar');
    const btnRemover = document.getElementById('btnRemover');

    let idSelecionado = null;

    // --- 1. Carregar Tabela ---
    async function carregarEstoque(termo = '') {
        try {
            const url = termo ? `/estoque/api/listar?q=${termo}` : '/estoque/api/listar';
            const response = await fetch(url);
            const dados = await response.json();
            
            renderizarTabela(dados);
        } catch (error) {
            console.error('Erro ao carregar:', error);
        }
    }

    function renderizarTabela(dados) {
        tableBody.innerHTML = '';
        idSelecionado = null;
        atualizarBotoes();

        dados.forEach(item => {
            const tr = document.createElement('tr');
            tr.dataset.id = item.id;
            
            const classeCor = item.qtde <= 0 ? 'text-danger' : '';

            tr.innerHTML = `
                <td>${item.nome}</td>
                <td>${item.tipo}</td>
                <td class="${classeCor}">${item.qtde}</td>
                <td>${item.min}</td>
                <td>${item.validade}</td>
            `;

            tr.addEventListener('click', () => selecionarLinha(tr, item.id));
            
            tableBody.appendChild(tr);
        });
    }

    function selecionarLinha(tr, id) {
        document.querySelectorAll('tbody tr').forEach(row => row.classList.remove('selected-row'));
        
        tr.classList.add('selected-row');
        tr.style.backgroundColor = '#d0e1e9';
        
        idSelecionado = id;
        atualizarBotoes();
    }

    function atualizarBotoes() {
        btnEditar.disabled = !idSelecionado;
        btnRemover.disabled = !idSelecionado;
        
        btnEditar.style.opacity = idSelecionado ? '1' : '0.5';
        btnRemover.style.opacity = idSelecionado ? '1' : '0.5';
    }


    btnBuscar.addEventListener('click', () => carregarEstoque(searchInput.value));
    searchInput.addEventListener('keyup', (e) => {
        if(e.key === 'Enter') carregarEstoque(searchInput.value);
    });

    // Novo
    btnNovo.addEventListener('click', () => {
        window.location.href = '/estoque/novo';
    });

    // Editar
    btnEditar.addEventListener('click', () => {
        if(idSelecionado) {
            window.location.href = `/estoque/editar/${idSelecionado}`;
        }
    });

    // Remover
    btnRemover.addEventListener('click', async () => {
        if(!idSelecionado) return;

        if(confirm("Tem certeza que deseja remover este medicamento?")) {
            try {
                const resp = await fetch(`/estoque/api/remover/${idSelecionado}`, { method: 'DELETE' });
                if(resp.ok) {
                    alert('Medicamento removido.');
                    carregarEstoque();
                } else {
                    alert('Erro ao remover.');
                }
            } catch (e) {
                console.error(e);
            }
        }
    });

    carregarEstoque();
});