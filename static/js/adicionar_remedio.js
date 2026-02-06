document.addEventListener('DOMContentLoaded', async () => {
    
    const btnCadastrar = document.getElementById('btnCadastrar');
    const pageTitle = document.querySelector('.page-title');
    
    // Pega o ID da URL se existir (ex: /estoque/editar/15)
    const urlParts = window.location.pathname.split('/');
    const isEditing = urlParts.includes('editar');
    const editId = isEditing ? urlParts[urlParts.length - 1] : null;

    // Get de elementos do Form
    const inputNome = document.getElementById('inputNome');
    const selectTipo = document.getElementById('selectTipo');
    const selectUnidade = document.getElementById('selectUnidade');
    const inputQtdMin = document.getElementById('inputQtdMin');
    const inputQtdCaixa = document.getElementById('inputQtdCaixa');

    // --- CONFIGURAÇÃO INICIAL ---
    if (isEditing) {
        pageTitle.innerText = "Atualizar Medicamento";
        btnCadastrar.innerHTML = '<i class="fas fa-save"></i> Salvar Alterações';
        await carregarDadosEdicao(editId);
    }

    // --- FUNÇÃO PARA CARREGAR DADOS ---
    async function carregarDadosEdicao(id) {
        try {
            const res = await fetch(`/estoque/api/obter/${id}`);
            if(!res.ok) throw new Error('Erro ao buscar dados');
            
            const dados = await res.json();
            
            // Preenche o formulário
            inputNome.value = dados.nome;
            selectTipo.value = dados.tipo;
            selectUnidade.value = dados.unidade;
            inputQtdMin.value = dados.min;
            inputQtdCaixa.value = dados.caixa;

        } catch (error) {
            console.error(error);
            alert("Erro ao carregar medicamento.");
        }
    }

    // --- ENVIO DO FORMULÁRIO ---
    btnCadastrar.addEventListener('click', async () => {
        
        const payload = {
            nome: inputNome.value,
            tipo: selectTipo.value,
            unidade: selectUnidade.value,
            qtd_minima: parseInt(inputQtdMin.value) || 0,
            qtd_por_caixa: parseInt(inputQtdCaixa.value) || 0
        };
        console.log(payload)
        if (!payload.nome || !payload.tipo) {
            alert("Preencha Nome e Tipo.");
            return;
        }

        try {
            let url, method;

            if (isEditing) {
                url = `/estoque/api/atualizar/${editId}`;
                method = 'PUT';
            } else {
                url = '/estoque/api/salvar';
                method = 'POST';
            }

            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                alert(isEditing ? 'Atualizado com sucesso!' : 'Cadastrado com sucesso!');
                window.location.href = '/estoque';
            } else {
                alert('Erro na operação.');
            }

        } catch (error) {
            console.error('Erro:', error);
            alert('Erro de conexão.');
        }
    });
});