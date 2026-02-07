const loginForm = document.getElementById('loginForm');
const msgErro = document.getElementById('msgErro');

loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const usuario = document.getElementById('usuario').value;
    const senha = document.getElementById('senha').value;

    try {
        const res = await fetch('/auth/autenticar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ usuario, senha })
        });

        const data = await res.json();

        if (data.sucesso) {
            // Redireciona para a tela de estoque
            window.location.href = data.redirect;
        } else {
            msgErro.textContent = data.mensagem;
        }
    } catch (err) {
        msgErro.textContent = 'Erro no servidor.';
        console.error(err);
    }
});
