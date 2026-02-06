document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('loginForm');
    const msgErro = document.getElementById('msgErro');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const usuario = document.getElementById('usuario').value;
        const senha = document.getElementById('senha').value;

        msgErro.innerText = "";
        msgErro.style.display = "none";

        try {
            const resposta = await enviarJson('/auth/autenticar', { usuario, senha });

            if (resposta.sucesso) {
                alert("Login realizado! (Aqui redirecionaria para o home)");
            }

        } catch (erro) {
            console.error(erro);
            msgErro.innerText = erro.message;
            msgErro.style.display = "block";
        }
    });
});