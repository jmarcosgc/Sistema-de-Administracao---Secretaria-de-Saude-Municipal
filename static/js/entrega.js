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
        med.nome.toLowerCase().includes(query)
    );

    resultados.forEach(med => {
        const div = document.createElement('div');
        div.classList.add('autocomplete-item');
        div.textContent = med.nome;
        div.addEventListener('click', () => {
            inputMedicamento.value = med.nome;
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
        m.nome.toLowerCase() === nomeBusca
    );

    if (!medEncontrado) {
        alert('Medicamento não encontrado no estoque.');
        return;
    }

    msgBuscaContainer.innerHTML = `
        <span><strong>${medEncontrado.nome}</strong> encontrado.</span>
        <button id="btnAdicionarMedicamento">Adicionar à Lista</button>
    `;

    document.getElementById('btnAdicionarMedicamento').addEventListener('click', () => {
        adicionarNaTabela(medEncontrado);
        inputMedicamento.value = '';
        msgBuscaContainer.innerHTML = '';
    });
});

function configurarCastataElementos(elementoPai, elementoFilho, elementoNeto, elementoBisneto, med){

    // Função para resetar os elementos
    const reset = (elemento) => {
        elemento.innerHTML = '<option value=0 >0</option>';
        elemento.disabled = true;
    }

    const resetarInput = (elemento) => {
        elemento.max = 0;
        elemento.value = 0;
        elemento.disabled = true;
    }

    // Evento do select Tipo comprimido
    elementoPai.addEventListener('change', () => {
        reset(elementoFilho);
        reset(elementoNeto);
        resetarInput(elementoBisneto);

        if(elementoPai.value){
            const medFiltro = med.tipos_medicamento.filter(tipoMed => tipoMed.tipo === elementoPai.value);
            //console.log(medFiltro);

            // Preencher o selectQtdComprimido
            medFiltro.forEach(t => {
                const opt = document.createElement('option');
                opt.textContent = t.quantidade_caixa + " unidade";
                opt.value = t.quantidade_caixa;
                if(!Array.from(elementoFilho.options).some(qtd => qtd.value == t.quantidade_caixa))
                    elementoFilho.appendChild(opt);
            });
        elementoFilho.disabled = false;
        }
    });

    // Evento do select da unidades que vem na caixa
    elementoFilho.addEventListener('change', () => {
        reset(elementoNeto);
        resetarInput(elementoBisneto);

        if(elementoFilho.value){
            const medFiltro = med.tipos_medicamento.find(
                 tipoMed => tipoMed.tipo === elementoPai.value &&
                 tipoMed.quantidade_caixa === parseInt(elementoFilho.value,10)
            );
            console.log("Tipo medicamento selecionado: "+medFiltro);
            medFiltro.lotes_medicamento.sort((a, b) => new Date(a.data_validade) - new Date(b.validade));
            medFiltro.lotes_medicamento.forEach(l => {

                if(!l.data_validade){
                    console.log("Erro: Lote sem data "+l);
                    return;
                }

                const dataValidade = new Date(l.data_validade);
                
                if(isNaN(dataValidade.getTime())){
                    console.log("Erro: Data inválida "+ dataValidade)
                }

                const opt = document.createElement('option');
                opt.textContent = new Intl.DateTimeFormat('pt-BR').format(dataValidade);
                opt.value = l.id;
                if(!Array.from(elementoNeto.options).some(data => data.value === l.value))
                    elementoNeto.appendChild(opt);
            });
            elementoNeto.disabled = false;
        }
    });

    // Evento do select da data-validade
    elementoNeto.addEventListener('change',() => {
        resetarInput(elementoBisneto);

        if(elementoNeto.value){
            const medFiltro = med.tipos_medicamento.find(
                 tipoMed => tipoMed.tipo === elementoPai.value &&
                 tipoMed.quantidade_caixa === parseInt(elementoFilho.value,10)
            );
            const medFiltroLote = medFiltro.lotes_medicamento.find(lote => lote.id === parseInt(elementoNeto.value));
            console.log("Lote selecionado: "+medFiltroLote);
            elementoBisneto.max = medFiltroLote.quantidade_estoque;
            elementoBisneto.disabled = false;
        }

    });

}

// --- Gerenciar Tabela ---
function adicionarNaTabela(med) {
    const row = document.createElement('tr');

    row.innerHTML = `
        <td>${med.nome}</td>
        <td><select class="select-tipo"><option value="">Selecione...</option></select></td>
        <td><select class="select-qtd-comprimido" disabled><option value="">0</option></select></td>
        <td><select class="select-lote-validade" disabled><option value="">Selecione...</option></select></td>
        <td><input type="number" class="input-qtd" min="0" value="0" disabled></td>
    `;

    tabelaBody.appendChild(row);
    emptyMessage.style.display = 'none';

    const selectTipo = row.querySelector('.select-tipo');
    const selectQtdComprimido = row.querySelector('.select-qtd-comprimido');
    const selectLoteValidade = row.querySelector('.select-lote-validade');
    const inputQtdMin = row.querySelector('.input-qtd');

    // Preencher tipos
    med.tipos_medicamento.forEach(t => {
        const opt = document.createElement('option');
        opt.textContent = t.tipo;
        if (!Array.from(selectTipo.options).some(opt => opt.value === t.tipo))
            selectTipo.appendChild(opt);
    });

    configurarCastataElementos(selectTipo, selectQtdComprimido, selectLoteValidade, inputQtdMin, med);
    medicamentosEntrega.push({ loteId: selectLoteValidade, quantidade: inputQtdMin});
}

// --- Finalizar ---
btnFinalizar.addEventListener('click', async () => {
    if (medicamentosEntrega.length === 0) return alert('Adicione medicamentos primeiro.');

    const itens = medicamentosEntrega.map(item => ({
        lote_id: parseInt(item.loteId.value, 10),
        quantidade: parseInt(item.quantidade.value)
    }));
    console.log(itens);

    if (itens.some(i => !i.quantidade || !i.lote_id)) {
        return alert('Preencha todos os campos da tabela.');
    }

    const payload = {
        tipo_entrega: 'RECEITA_PARTICULAR',
        fk_paciente: null,
        fk_farmaceutico: 2,
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