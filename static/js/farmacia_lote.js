// --- Seletores ---
const inputBusca = document.getElementById('inputBusca');
const btnBuscarMedicamento = document.getElementById('btnBuscarMedicamento');
const msgBusca = document.getElementById('msgBusca');

const selectTipo = document.getElementById('selectTipo');
const inputUnidade = document.getElementById('inputUnidade');
const inputQtd = document.getElementById('inputQtd');
const inputValidade = document.getElementById('inputValidade');

const btnSalvarLote = document.getElementById('btnSalvarLote');

let medicamentoSelecionado = null;
let tiposDisponiveis = [];

// --- Função para buscar medicamentos pelo nome ---
btnBuscarMedicamento.addEventListener('click', async () => {
    const termo = inputBusca.value.trim();
    if (!termo) {
        msgBusca.textContent = 'Digite um nome para buscar.';
        return;
    }

    msgBusca.textContent = 'Buscando...';
    selectTipo.innerHTML = '<option value="">Selecione...</option>';
    selectTipo.disabled = true;
    inputUnidade.value = '';

    try {
        const resultados = await fetch(`/estoque/api/listar?q=${encodeURIComponent(termo)}`)
            .then(r => r.json());

        if (resultados.length === 0) {
            msgBusca.textContent = 'Nenhum medicamento encontrado.';
            medicamentoSelecionado = null;
            return;
        }

        // Pegamos o primeiro resultado para simplificar
        medicamentoSelecionado = resultados[0];

        // Carrega os tipos disponíveis
        const tiposResponse = await fetch(`/estoque/api/obter/${medicamentoSelecionado.id}`)
            .then(r => r.json());

        tiposDisponiveis = tiposResponse.tipo ? [tiposResponse] : [];

        // Preenche o select de tipos
        selectTipo.innerHTML = '<option value="">Selecione...</option>';
        tiposDisponiveis.forEach(t => {
            const opt = document.createElement('option');
            opt.value = t.id;
            opt.textContent = t.tipo;
            selectTipo.appendChild(opt);
        });

        selectTipo.disabled = false;
        msgBusca.textContent = `Medicamento encontrado: ${medicamentoSelecionado.nome}`;

    } catch (err) {
        console.error(err);
        msgBusca.textContent = 'Erro ao buscar medicamento.';
    }
});

// --- Preencher unidade ao selecionar tipo ---
selectTipo.addEventListener('change', () => {
    const tipoId = selectTipo.value;
    const tipoSelecionado = tiposDisponiveis.find(t => t.id == tipoId);
    inputUnidade.value = tipoSelecionado ? tipoSelecionado.unidade : '';
});

// --- Salvar lote ---
btnSalvarLote.addEventListener('click', async () => {
    const tipoId = selectTipo.value;
    const qtd = parseInt(inputQtd.value);
    const validade = inputValidade.value;

    if (!medicamentoSelecionado || !tipoId) {
        alert('Selecione um medicamento e tipo.');
        return;
    }

    if (!qtd || qtd <= 0) {
        alert('Informe a quantidade do lote.');
        return;
    }

    if (!validade) {
        alert('Informe a data de validade.');
        return;
    }

    const dados = {
        fk_tipo_medicamento: tipoId,
        quantidade_entrada: qtd,
        quantidade_estoque: qtd,
        data_validade: validade,
        status: 'DISPONIVEL'
    };

    try {
        const resultado = await enviarJson('/estoque/api/salvar_lote', dados);
        alert(resultado.msg);
        // Limpar formulário
        inputBusca.value = '';
        selectTipo.innerHTML = '<option value="">Selecione...</option>';
        selectTipo.disabled = true;
        inputUnidade.value = '';
        inputQtd.value = '';
        inputValidade.value = '';
        msgBusca.textContent = '';
    } catch (err) {
        console.error(err);
        alert('Erro ao salvar lote: ' + err.message);
    }
});
