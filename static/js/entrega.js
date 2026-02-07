// --- Seletores ---
const inputMedicamento = document.getElementById('inputMedicamento');
const btnBuscar = document.getElementById('btnBuscar');
const tabelaBody = document.getElementById('tableBody');
const btnFinalizar = document.getElementById('btnFinalizar');
const emptyMessage = document.getElementById('emptyMessage');

// Dados temporários da entrega
let medicamentosEntrega = [];
let todosMedicamentos = []; // carregados da API

// --- Inicialização: buscar todos medicamentos com lotes ---
async function carregarMedicamentos() {
    try {
        todosMedicamentos = await fetch('/estoque/api/medicamentos_com_lotes')
            .then(r => r.json());
    } catch (err) {
        console.error(err);
        alert('Erro ao carregar medicamentos do estoque.');
    }
}

// --- Buscar medicamento pelo nome ---
btnBuscar.addEventListener('click', () => {
    const nomeBusca = inputMedicamento.value.trim().toLowerCase();
    if (!nomeBusca) {
        alert('Digite o nome do medicamento.');
        return;
    }

    const medEncontrado = todosMedicamentos.find(m => m.nome_medicamento.toLowerCase().includes(nomeBusca));
    if (!medEncontrado) {
        alert('Medicamento não encontrado.');
        return;
    }

    // Criar botão de adicionar
    let msgBusca = document.getElementById('msgBusca');
    if (!msgBusca) {
        msgBusca = document.createElement('small');
        msgBusca.id = 'msgBusca';
        msgBusca.style.fontWeight = 'bold';
        msgBusca.style.display = 'block';
        inputMedicamento.parentNode.appendChild(msgBusca);
    }
    msgBusca.innerHTML = `
        <strong>${medEncontrado.nome_medicamento}</strong> encontrado.
        <button id="btnAdicionarMedicamento">Adicionar</button>
    `;

    const btnAdicionar = document.getElementById('btnAdicionarMedicamento');
    btnAdicionar.addEventListener('click', () => {
        adicionarNaTabela(medEncontrado);
        inputMedicamento.value = '';
        msgBusca.innerHTML = '';
    });
});

// --- Adicionar medicamento na tabela ---
function adicionarNaTabela(med) {
    const row = document.createElement('tr');

    // Nome
    const tdNome = document.createElement('td');
    tdNome.textContent = med.nome_medicamento;
    row.appendChild(tdNome);

    // Tipo
    const tdTipo = document.createElement('td');
    const selectTipo = document.createElement('select');
    selectTipo.innerHTML = '<option value="">Selecione...</option>';
    tdTipo.appendChild(selectTipo);
    row.appendChild(tdTipo);

    // Quantidade
    const tdQtd = document.createElement('td');
    const selectQtd = document.createElement('select');
    selectQtd.innerHTML = '<option value="">0</option>';
    tdQtd.appendChild(selectQtd);
    row.appendChild(tdQtd);

    // Qtde mínima
    const tdQtdMin = document.createElement('td');
    const inputQtdMin = document.createElement('input');
    inputQtdMin.type = 'number';
    inputQtdMin.min = 0;
    inputQtdMin.value = 0;
    tdQtdMin.appendChild(inputQtdMin);
    row.appendChild(tdQtdMin);

    // Validade
    const tdValidade = document.createElement('td');
    const selectLote = document.createElement('select');
    selectLote.innerHTML = '<option value="">Selecione...</option>';
    tdValidade.appendChild(selectLote);
    row.appendChild(tdValidade);

    tabelaBody.appendChild(row);
    emptyMessage.style.display = 'none';

    medicamentosEntrega.push({
        medId: med.id,
        row,
        selectTipo,
        selectQtd,
        selectLote,
        inputQtdMin,
        tipos: med.tipo_medicamento
    });

    preencherTiposETipos(med.id);
}

// --- Preencher tipos, quantidade e lotes ---
function preencherTiposETipos(medId) {
    const item = medicamentosEntrega.find(m => m.medId === medId);
    if (!item) return;

    // Preencher tipos
    item.selectTipo.innerHTML = '<option value="">Selecione...</option>';
    item.tipos.forEach(t => {
        const opt = document.createElement('option');
        opt.value = t.id;
        opt.textContent = t.tipo;
        item.selectTipo.appendChild(opt);
    });
    item.selectTipo.disabled = false;

    // Ao selecionar tipo
    item.selectTipo.addEventListener('change', () => {
        const tipoSelecionado = item.tipos.find(t => t.id == item.selectTipo.value);
        if (!tipoSelecionado) return;

        // Quantidade
        item.selectQtd.innerHTML = '';
        for (let i = 1; i <= tipoSelecionado.quantidade_caixa; i++) {
            const opt = document.createElement('option');
            opt.value = i;
            opt.textContent = i;
            item.selectQtd.appendChild(opt);
        }
        item.selectQtd.disabled = false;

        // Validade: lote mais próximo do vencimento
        const lotesValidos = tipoSelecionado.lotes
            .filter(l => l.quantidade_estoque > 0)
            .sort((a, b) => new Date(a.data_validade) - new Date(b.data_validade));

        item.selectLote.innerHTML = '';
        lotesValidos.forEach(lote => {
            const opt = document.createElement('option');
            opt.value = lote.id;
            opt.textContent = `${lote.quantidade_estoque} un. - Validade: ${lote.data_validade}`;
            item.selectLote.appendChild(opt);
        });
        item.selectLote.disabled = lotesValidos.length === 0;
    });
}

// --- Finalizar entrega ---
btnFinalizar.addEventListener('click', async () => {
    const itens = [];

    for (let item of medicamentosEntrega) {
        const tipoId = item.selectTipo.value;
        const loteId = item.selectLote.value;
        const quantidade = parseInt(item.selectQtd.value);
        const qtdMin = parseInt(item.inputQtdMin.value);

        if (!tipoId || !loteId || !quantidade || quantidade <= 0) {
            alert('Preencha todos os campos corretamente antes de finalizar.');
            return;
        }

        itens.push({
            tipo_id: tipoId,
            lote_id: loteId,
            quantidade
        });
    }

    const payload = {
        tipo_entrega: 'RECEITA_PARTICULAR',
        fk_paciente: null,
        fk_farmaceutico: 3,
        justificativa: '',
        itens
    };

    try {
        const resultado = await enviarJson('/entrega/api/confirmar', payload);
        alert(resultado.msg);
        tabelaBody.innerHTML = '';
        inputMedicamento.value = '';
        medicamentosEntrega = [];
        emptyMessage.style.display = 'block';
    } catch (err) {
        console.error(err);
        alert('Erro ao finalizar entrega: ' + err.message);
    }
});

// --- Inicializar ---
carregarMedicamentos();
