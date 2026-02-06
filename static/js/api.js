async function enviarJson(url, dados, metodo = 'POST') {
    const opcoes = {
        method: metodo,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dados)
    };
    const response = await fetch(url, opcoes);
    const resultado = await response.json();
    
    if (!response.ok) {
        throw new Error(resultado.mensagem || 'Erro na requisição');
    }
    return resultado;
}