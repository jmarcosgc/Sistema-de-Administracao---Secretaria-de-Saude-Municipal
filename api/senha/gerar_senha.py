from werkzeug.security import generate_password_hash

senha_medico_plana = "123"
senha_farmacia_plana = "123"


hash_medico = generate_password_hash(senha_medico_plana)
hash_farmacia = generate_password_hash(senha_farmacia_plana)

print(f"Senha Médico: {hash_medico}")
print(f"Senha Farmácia: {hash_farmacia}")