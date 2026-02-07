const inputMedicamento = document.getElementById('inputMedicamento');
const btnBuscar = document.getElementById('btnBuscar');
const tabelaBody = document.getElementById('tableBody');
const btnFinalizar = document.getElementById('btnFinalizar');
const emptyMessage = document.getElementById('emptyMessage');
const listaMedicamentos = document.getElementById('listaMedicamentos');
const msgBuscaContainer = document.getElementById('msgBuscaContainer');

let medicamentosEntrega = [];
let todosMedicamentos = []; 

// --- Inicialização ---
async function carregarMedicamentos() {
    try {
        const response = await fetch('/estoque/api/medicamentos_com_lotes');
        todosMedicamentos = await response.json();
    } catch (err) {
        console.error('Erro ao carregar medicamentos:', err);
    }
}

// --- Autocomplete ---
inputMedicamento.addEventListener('input', () => {
    const query = inputMedicamento.value.trim().toLowerCase();
    listaMedicamentos.innerHTML = '';

    if (!query) return;

    const resultados = todosMedicamentos.filter(med =>
        med.nome_medicamento.toLowerCase().includes(query)
    );

    resultados.forEach(med => {
        const div = document.createElement('div');
        div.classList.add('autocomplete-item');
        div.textContent = med.nome_medicamento;
        div.addEventListener('click', () => {
            inputMedicamento.value = med.nome_medicamento;
            listaMedicamentos.innerHTML = '';
            btnBuscar.click(); // Já dispara a busca ao selecionar
        });
        listaMedicamentos.appendChild(div);
    });
});

// Fechar lista ao clicar fora
document.addEventListener('click', (e) => {
    if (e.target !== inputMedicamento) {
        listaMedicamentos.innerHTML = '';
    }
});

// --- Buscar e Sugerir Adição ---
btnBuscar.addEventListener('click', () => {
    const nomeBusca = inputMedicamento.value.trim().toLowerCase();
    if (!nomeBusca) return;

    const medEncontrado = todosMedicamentos.find(m => 
        m.nome_medicamento.toLowerCase() === nomeBusca
    );

    if (!medEncontrado) {
        alert('Medicamento não encontrado no estoque.');
        return;
    }

    msgBuscaContainer.innerHTML = `
        <span><strong>${medEncontrado.nome_medicamento}</strong> encontrado.</span>
        <button id="btnAdicionarMedicamento">Adicionar à Lista</button>
    `;

    document.getElementById('btnAdicionarMedicamento').addEventListener('click', () => {
        adicionarNaTabela(medEncontrado);
        inputMedicamento.value = '';
        msgBuscaContainer.innerHTML = '';
    });
});

// --- Gerenciar Tabela ---
function adicionarNaTabela(med) {
    const row = document.createElement('tr');

    row.innerHTML = `
        <td>${med.nome_medicamento}</td>
        <td><select class="select-tipo"><option value="">Selecione...</option></select></td>
        <td><select class="select-qtd" disabled><option value="">0</option></select></td>
        <td><input type="number" class="input-qtd-min" min="0" value="0"></td>
        <td><select class="select-lote" disabled><option value="">Selecione...</option></select></td>
    `;

    tabelaBody.appendChild(row);
    emptyMessage.style.display = 'none';

    const selectTipo = row.querySelector('.select-tipo');
    const selectQtd = row.querySelector('.select-qtd');
    const selectLote = row.querySelector('.select-lote');
    const inputQtdMin = row.querySelector('.input-qtd-min');

    // Preencher tipos
    med.tipo_medicamento.forEach(t => {
        const opt = document.createElement('option');
        opt.value = t.id;
        opt.textContent = t.tipo;
        selectTipo.appendChild(opt);
    });

    selectTipo.addEventListener('change', () => {
        const tipoSel = med.tipo_medicamento.find(t => t.id == selectTipo.value);
        if (!tipoSel) return;

        // Qtd disponível
        selectQtd.innerHTML = '';
        for (let i = 1; i <= tipoSel.quantidade_caixa; i++) {
            const opt = document.createElement('option');
            opt.value = i; opt.textContent = i;
            selectQtd.appendChild(opt);
        }
        selectQtd.disabled = false;

        // Lotes
        const lotesValidos = tipoSel.lotes
            .filter(l => l.quantidade_estoque > 0)
            .sort((a, b) => new Date(a.data_validade) - new Date(b.data_validade));

        selectLote.innerHTML = '';
        lotesValidos.forEach(l => {
            const opt = document.createElement('option');
            opt.value = l.id;
            opt.textContent = `${l.quantidade_estoque} un - Venc: ${l.data_validade}`;
            selectLote.appendChild(opt);
        });
        selectLote.disabled = lotesValidos.length === 0;
    });

    medicamentosEntrega.push({ medId: med.id, selectTipo, selectQtd, selectLote, inputQtdMin });
}

// --- Finalizar ---
btnFinalizar.addEventListener('click', async () => {
    if (medicamentosEntrega.length === 0) return alert('Adicione medicamentos primeiro.');

    const itens = medicamentosEntrega.map(item => ({
        tipo_id: item.selectTipo.value,
        lote_id: item.selectLote.value,
        quantidade: parseInt(item.selectQtd.value)
    }));

    if (itens.some(i => !i.tipo_id || !i.lote_id)) {
        return alert('Preencha todos os campos da tabela.');
    }

    const payload = {
        tipo_entrega: 'RECEITA_PARTICULAR',
        fk_paciente: null,
        fk_farmaceutico: 3,
        justificativa: '',
        itens
    };

    try {
        const res = await enviarJson('/entrega/api/confirmar', payload);
        alert(res.msg);
        location.reload(); 
    } catch (err) {
        alert('Erro: ' + err.message);
    }
});

carregarMedicamentos();