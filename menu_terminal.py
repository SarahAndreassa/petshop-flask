from banco import conectar


def cadastrar_cliente():

    conexao = conectar()
    cursor = conexao.cursor()

    print("\n--- CADASTRAR CLIENTE ---")

    nome = input("Nome: ")
    telefone = input("Telefone: ")
    email = input("E-mail: ")

    sql = """
        INSERT INTO clientes (nome, telefone, email)
        VALUES (%s, %s, %s)
    """

    valores = (nome, telefone, email)

    cursor.execute(sql, valores)

    conexao.commit()

    cursor.close()
    conexao.close()

    print("\nCliente cadastrado com sucesso!")


def listar_clientes():

    conexao = conectar()
    cursor = conexao.cursor()

    print("\n--- CLIENTES ---")

    cursor.execute("SELECT * FROM clientes")

    clientes = cursor.fetchall()

    if len(clientes) == 0:
        print("Nenhum cliente cadastrado.")
    else:
        for cliente in clientes:
            print(
                f"ID: {cliente[0]} | "
                f"Nome: {cliente[1]} | "
                f"Telefone: {cliente[2]} | "
                f"E-mail: {cliente[3]}"
            )

    cursor.close()
    conexao.close()


def cadastrar_pet():

    conexao = conectar()
    cursor = conexao.cursor()

    print("\n--- CADASTRAR PET ---")

    nome = input("Nome do pet: ")
    especie = input("Espécie: ")
    raca = input("Raça: ")
    cliente_id = int(input("ID do dono: "))

    sql = """
        INSERT INTO pets (nome, especie, raca, cliente_id)
        VALUES (%s, %s, %s, %s)
    """

    valores = (nome, especie, raca, cliente_id)

    cursor.execute(sql, valores)

    conexao.commit()

    cursor.close()
    conexao.close()

    print("\nPet cadastrado com sucesso!")


def listar_pets():

    conexao = conectar()
    cursor = conexao.cursor()

    print("\n--- PETS ---")

    sql = """
        SELECT pets.id, pets.nome, pets.especie,
               pets.raca, clientes.nome
        FROM pets
        INNER JOIN clientes
        ON pets.cliente_id = clientes.id
    """

    cursor.execute(sql)

    pets = cursor.fetchall()

    if len(pets) == 0:
        print("Nenhum pet cadastrado.")
    else:
        for pet in pets:
            print(
                f"ID: {pet[0]} | "
                f"Pet: {pet[1]} | "
                f"Espécie: {pet[2]} | "
                f"Raça: {pet[3]} | "
                f"Dono: {pet[4]}"
            )

    cursor.close()
    conexao.close()


def menu():

    while True:

        print("\n====================")
        print("       PETSHOP")
        print("====================")
        print("1 - Cadastrar cliente")
        print("2 - Listar clientes")
        print("3 - Cadastrar pet")
        print("4 - Listar pets")
        print("0 - Sair")
        print("====================")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            cadastrar_cliente()

        elif opcao == "2":
            listar_clientes()

        elif opcao == "3":
            cadastrar_pet()

        elif opcao == "4":
            listar_pets()

        elif opcao == "0":
            print("Encerrando o sistema...")
            break

        else:
            print("Opção inválida!")


if __name__ == "__main__":
    menu()
