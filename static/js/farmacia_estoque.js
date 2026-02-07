document.addEventListener('DOMContentLoaded', () => {

    const tableBody = document.getElementById('tableBody');
    const searchInput = document.getElementById('searchInput');
    const btnBuscar = document.getElementById('btnBuscar');
    const btnNovo = document.getElementById('btnNovo');
    const btnEditar = document.getElementById('btnEditar');

    let idSelecionado = null;

    // --- Carregar estoque da API ---
    async function carregarEstoque(termo = '') {
        try {
            const url = termo ? `/estoque/api/listar?q=${encodeURIComponent(termo)}` : '/estoque/api/listar';
            console.log('Requisição GET para:', url);

            const response = await fetch(url);
            if (!response.ok) {
                console.error('Erro HTTP:', response.status);
                alert('Erro ao carregar dados da API.');
                return;
            }

            const dados = await response.json();
            console.log('Dados recebidos da API:', dados);

            if (!Array.isArray(dados) || dados.length === 0) {
                tableBody.innerHTML = `<tr><td colspan="5" style="text-align:center;">Nenhum medicamento encontrado.</td></tr>`;
                return;
            }

            renderizarTabela(dados);

        } catch (error) {
            console.error('Erro ao carregar estoque:', error);
            alert('Erro ao carregar estoque. Veja o console para mais detalhes.');
        }
    }

    // --- Renderizar tabela ---
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

    // --- Selecionar linha ---
    function selecionarLinha(tr, id) {
        document.querySelectorAll('tbody tr').forEach(row => row.classList.remove('selected-row'));
        tr.classList.add('selected-row');
        tr.style.backgroundColor = '#d0e1e9';
        idSelecionado = id;
        atualizarBotoes();
    }

    // --- Atualizar botões ---
    function atualizarBotoes() {
        btnEditar.disabled = !idSelecionado;
        btnEditar.style.opacity = idSelecionado ? '1' : '0.5';
    }

    // --- Eventos ---
    btnBuscar.addEventListener('click', () => carregarEstoque(searchInput.value));
    searchInput.addEventListener('keyup', e => {
        if (e.key === 'Enter') carregarEstoque(searchInput.value);
    });

    btnNovo.addEventListener('click', () => {
        window.location.href = '/estoque/novo';
    });

    btnEditar.addEventListener('click', () => {
        if (idSelecionado) window.location.href = `/estoque/editar/${idSelecionado}`;
    });

    // --- Carregar estoque inicialmente ---
    carregarEstoque();
});
