import os
from datetime import datetime

import mysql.connector
from flask import Flask, flash, redirect, render_template, request, url_for

from banco import buscar_todos, buscar_um, criar_tabelas, executar

app = Flask(__name__)
# O flash() (mensagens "Cliente salvo!") precisa de uma chave secreta.
app.secret_key = os.environ.get("SECRET_KEY", "chave-de-desenvolvimento")

# Serviços oferecidos e seus preços. Quer mudar? É só editar aqui.
SERVICOS = {
    "Banho": 50.00,
    "Tosa": 70.00,
    "Banho e tosa": 110.00,
    "Consulta veterinária": 150.00,
    "Vacinação": 90.00,
}
ESPECIES = ["Cachorro", "Gato", "Pássaro", "Coelho", "Roedor", "Outro"]


# ---------- Filtros: formatam valores dentro dos templates ----------
@app.template_filter("moeda")
def moeda(valor):
    return "R$ " + f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


@app.template_filter("dataf")
def dataf(valor):
    return valor.strftime("%d/%m/%Y às %H:%M")


# ---------- Se o MySQL estiver desligado, mostra uma página explicando ----------
@app.errorhandler(mysql.connector.Error)
def erro_banco(erro):
    return render_template("erro.html", erro=erro), 500


# ---------- Início ----------
@app.route("/")
def inicio():
    totais = buscar_um(
        """
        SELECT (SELECT COUNT(*) FROM clientes) AS clientes,
               (SELECT COUNT(*) FROM pets) AS pets,
               (SELECT COUNT(*) FROM agendamentos WHERE status = 'Agendado') AS agendados
        """
    )
    proximos = buscar_todos(
        """
        SELECT a.servico, a.data_hora, p.nome AS pet, c.nome AS dono
        FROM agendamentos a
        JOIN pets p ON a.pet_id = p.id
        JOIN clientes c ON p.cliente_id = c.id
        WHERE a.status = 'Agendado'
        ORDER BY a.data_hora
        LIMIT 5
        """
    )
    return render_template("index.html", totais=totais, proximos=proximos)


# ---------- Clientes ----------
@app.route("/clientes")
def clientes():
    busca = request.args.get("q", "").strip()
    termo = f"%{busca}%"
    lista = buscar_todos(
        """
        SELECT c.*, COUNT(p.id) AS total_pets
        FROM clientes c
        LEFT JOIN pets p ON p.cliente_id = c.id
        WHERE c.nome LIKE %s OR c.email LIKE %s OR c.telefone LIKE %s
        GROUP BY c.id
        ORDER BY c.nome
        """,
        (termo, termo, termo),
    )
    return render_template("clientes.html", clientes=lista, busca=busca)


# Uma única função atende "cadastrar" (id=None) e "editar" (id=número).
@app.route("/clientes/cadastrar", methods=["GET", "POST"], defaults={"id": None})
@app.route("/clientes/<int:id>/editar", methods=["GET", "POST"])
def cliente_form(id):
    cliente = buscar_um("SELECT * FROM clientes WHERE id = %s", (id,)) if id else {}
    if id and not cliente:
        flash("Cliente não encontrado.", "erro")
        return redirect(url_for("clientes"))

    if request.method == "POST":
        nome = request.form["nome"].strip()
        telefone = request.form["telefone"].strip()
        email = request.form["email"].strip()

        if not nome:
            flash("Informe o nome do cliente.", "erro")
        else:
            if id:
                executar(
                    "UPDATE clientes SET nome=%s, telefone=%s, email=%s WHERE id=%s",
                    (nome, telefone, email, id),
                )
                flash("Cliente atualizado.", "ok")
            else:
                executar(
                    "INSERT INTO clientes (nome, telefone, email) VALUES (%s, %s, %s)",
                    (nome, telefone, email),
                )
                flash("Cliente cadastrado.", "ok")
            return redirect(url_for("clientes"))
        # nome vazio: mostra o formulário de novo, mantendo o que foi digitado
        cliente = {"nome": nome, "telefone": telefone, "email": email}

    return render_template("cliente_form.html", cliente=cliente, editando=bool(id))


@app.route("/clientes/<int:id>/excluir", methods=["POST"])
def cliente_excluir(id):
    executar("DELETE FROM clientes WHERE id = %s", (id,))
    flash("Cliente excluído (os pets e agendamentos dele também).", "ok")
    return redirect(url_for("clientes"))


# ---------- Pets ----------
@app.route("/pets")
def pets():
    lista = buscar_todos(
        """
        SELECT p.*, c.nome AS dono
        FROM pets p
        JOIN clientes c ON p.cliente_id = c.id
        ORDER BY p.nome
        """
    )
    return render_template("pets.html", pets=lista)


@app.route("/pets/cadastrar", methods=["GET", "POST"], defaults={"id": None})
@app.route("/pets/<int:id>/editar", methods=["GET", "POST"])
def pet_form(id):
    donos = buscar_todos("SELECT id, nome FROM clientes ORDER BY nome")
    if not donos:
        flash("Cadastre um cliente antes de cadastrar um pet.", "erro")
        return redirect(url_for("cliente_form"))

    pet = buscar_um("SELECT * FROM pets WHERE id = %s", (id,)) if id else {}
    if id and not pet:
        flash("Pet não encontrado.", "erro")
        return redirect(url_for("pets"))

    if request.method == "POST":
        nome = request.form["nome"].strip()
        especie = request.form["especie"]
        raca = request.form["raca"].strip()
        cliente_id = request.form["cliente_id"]

        if not nome:
            flash("Informe o nome do pet.", "erro")
            pet = {"nome": nome, "especie": especie, "raca": raca, "cliente_id": int(cliente_id)}
        else:
            if id:
                executar(
                    "UPDATE pets SET nome=%s, especie=%s, raca=%s, cliente_id=%s WHERE id=%s",
                    (nome, especie, raca, cliente_id, id),
                )
                flash("Pet atualizado.", "ok")
            else:
                executar(
                    "INSERT INTO pets (nome, especie, raca, cliente_id) VALUES (%s, %s, %s, %s)",
                    (nome, especie, raca, cliente_id),
                )
                flash("Pet cadastrado.", "ok")
            return redirect(url_for("pets"))

    return render_template(
        "pet_form.html", pet=pet, donos=donos, especies=ESPECIES, editando=bool(id)
    )


@app.route("/pets/<int:id>/excluir", methods=["POST"])
def pet_excluir(id):
    executar("DELETE FROM pets WHERE id = %s", (id,))
    flash("Pet excluído.", "ok")
    return redirect(url_for("pets"))


# ---------- Serviços (agendamentos) ----------
@app.route("/servicos")
def servicos():
    lista = buscar_todos(
        """
        SELECT a.*, p.nome AS pet, c.nome AS dono
        FROM agendamentos a
        JOIN pets p ON a.pet_id = p.id
        JOIN clientes c ON p.cliente_id = c.id
        ORDER BY (a.status = 'Agendado') DESC, a.data_hora
        """
    )
    return render_template("servicos.html", agendamentos=lista, catalogo=SERVICOS)


@app.route("/servicos/agendar", methods=["GET", "POST"])
def agendar():
    meus_pets = buscar_todos(
        """
        SELECT p.id, p.nome, c.nome AS dono
        FROM pets p JOIN clientes c ON p.cliente_id = c.id
        ORDER BY p.nome
        """
    )
    if not meus_pets:
        flash("Cadastre um pet antes de agendar um serviço.", "erro")
        return redirect(url_for("pet_form"))

    if request.method == "POST":
        pet_id = request.form["pet_id"]
        servico = request.form["servico"]
        observacao = request.form["observacao"].strip()
        try:
            data_hora = datetime.fromisoformat(request.form["data_hora"])
        except ValueError:
            flash("Escolha uma data e um horário válidos.", "erro")
            return render_template("agendar.html", pets=meus_pets, catalogo=SERVICOS)

        if servico not in SERVICOS:
            flash("Escolha um serviço da lista.", "erro")
        else:
            executar(
                """
                INSERT INTO agendamentos (pet_id, servico, data_hora, valor, observacao)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (pet_id, servico, data_hora, SERVICOS[servico], observacao),
            )
            flash("Serviço agendado.", "ok")
            return redirect(url_for("servicos"))

    return render_template("agendar.html", pets=meus_pets, catalogo=SERVICOS)


@app.route("/servicos/<int:id>/concluir", methods=["POST"])
def concluir(id):
    executar("UPDATE agendamentos SET status = 'Concluído' WHERE id = %s", (id,))
    flash("Serviço marcado como concluído.", "ok")
    return redirect(url_for("servicos"))


@app.route("/servicos/<int:id>/excluir", methods=["POST"])
def agendamento_excluir(id):
    executar("DELETE FROM agendamentos WHERE id = %s", (id,))
    flash("Agendamento excluído.", "ok")
    return redirect(url_for("servicos"))


if __name__ == "__main__":
    try:
        criar_tabelas()
    except mysql.connector.Error as erro:
        print("\n⚠️  Não consegui conectar ao MySQL:", erro)
        print("   Veja se o MySQL está ligado e se o arquivo .env tem usuário/senha corretos.\n")
    app.run(debug=True)
