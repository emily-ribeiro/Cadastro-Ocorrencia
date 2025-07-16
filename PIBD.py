import psycopg2
from psycopg2 import Error

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="PIDB_BASE",
            user="postgres",
            password="arthur12*",
            port="5432"
        )
        return conn
    except Exception as error:
        print(f"Erro ao conectar ao banco de dados: {error}")
        return None

def criar_usuario(cpf, nome, fone, email):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO usuario (cpf, nome, fone, email) VALUES (%s, %s, %s, %s)",
                    (cpf, nome, fone, email)
                )
                conn.commit()
                print("Usuário criado com sucesso!")
        except Exception as e:
            if hasattr(e, 'pgcode') and e.pgcode == '23505':  # Código de erro conflito de chave primary
                print(f"Erro: CPF, telefone ou e-mail já cadastrado para {nome}.")
            else:
                print(f"Erro ao criar usuário: {e}")
            conn.rollback()
        finally:
            conn.close()

def criar_ocorrencia(cpf_solicitante, cep, numero):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("CALL sp_criar_ocorrencia(%s, %s, %s, NULL, NULL)",
                            (cpf_solicitante, cep, numero)
                )
                conn.commit()
                print("Ocorrência criada com sucesso!")
                # Recupera os IDs da ocorrência e do solicitante
                cursor.execute("""
                    SELECT id_ocorrencia, id_solicitante
                    FROM Ocorrencia
                    WHERE id_solicitante = (SELECT id_solicitante FROM Solicitante WHERE cpf = %s)
                    ORDER BY id_ocorrencia DESC
                    LIMIT 1;
                """, (cpf_solicitante,))
                result = cursor.fetchone()
                if result:
                    ocorrencia_id, solicitante_id = result
                    print(f"Ocorrência {ocorrencia_id} criada para o solicitante {solicitante_id} (CPF: {cpf_solicitante}).")
                else:
                    print(f"Ocorrência criada, mas não foi possível recuperar os IDs.")
            conn.commit()
        except Error as e:
            print(f"Erro ao criar ocorrência: {e}")
            conn.rollback()
        finally:
            conn.close()

def definir_tecnico_ocorrencia(id_ocorrencia, id_tecnico):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE ocorrencia SET id_tecnico = %s WHERE id_ocorrencia = %s",
                    (id_tecnico, id_ocorrencia)
                )
                if cursor.rowcount > 0:
                    print(f"Técnico {id_tecnico} atribuído à ocorrência {id_ocorrencia}.")
                else:
                    print(f"Nenhuma ocorrência encontrada com o ID {id_ocorrencia}.")
            conn.commit()
        except Error as e:
            print(f"Erro ao atribuir técnico à ocorrência: {e}")
            conn.rollback()
        finally:
            conn.close()

def atualizar_status_ocorrencia(id_ocorrencia,new_status):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE ocorrencia SET status = %s WHERE id_ocorrencia = %s",
                    (new_status, id_ocorrencia)
                )
                if cursor.rowcount > 0:
                    print(f"Status da ocorrência {id_ocorrencia} atualizado para '{new_status}'.")
                else:
                    print(f"Nenhuma ocorrência encontrada com o ID {id_ocorrencia}.")
            conn.commit()
        except Error as e:
            print(f"Erro ao atualizar status da ocorrência: {e}")
            conn.rollback()
        finally:
            conn.close()
def ocorrencias_por_tecnico(id_tecnico):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM fn_get_ocorrencias_por_tecnico(%s)", (id_tecnico,)
                    )
                ocorrencias = cursor.fetchall()
                if ocorrencias:
                    print(f"Ocorrências atribuídas ao técnico {id_tecnico}:")
                    for ocorrencia in ocorrencias:
                        print(ocorrencia)
                else:
                    print(f"Nenhuma ocorrência encontrada para o técnico {id_tecnico}.")
            conn.commit()
        except Error as e:
            print(f"Erro ao buscar ocorrências do técnico: {e}")
            conn.rollback()
        finally:
            conn.close()

def listar_tabelas(tabel_name):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {tabel_name};")
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] # Obter nomes das colunas

                if rows:
                    print(f"\nDados da Tabela '{tabel_name}':")
                    print("-" * 50)
                    print(" | ".join(columns))
                    print("-" * 50)
                    for row in rows:
                        print(" | ".join(map(str, row)))
                    print("-" * 50)
                else:
                    print(f"Nenhum dado encontrado na tabela '{tabel_name}'.")
        except Error as e:
            print(f"Erro ao listar dados da tabela '{tabel_name}': {e}")
        finally:
            conn.close()

def main():
    while True:
        print("\nMenu:")
        print("1. Criar Usuário")
        print("2. Criar Ocorrência")
        print("3. Atualizar Status da Ocorrência")
        print("4. Listar Ocorrências por Técnico")
        print("5. Vincular Técnico a Ocorrência")
        print("6. Listar Tabelas")
        print("7. Sair")

        choice = input("Escolha uma opção: ")

        if choice == '1':
            cpf = input("CPF: ")
            nome = input("Nome: ")
            fone = input("Telefone: ")
            email = input("E-mail: ")
            criar_usuario(cpf, nome, fone, email)
        elif choice == '2':
            cpf_solicitante = input("CPF do Solicitante: ")
            cep = input("CEP: ")
            numero = input("Número da Casa: ")
            criar_ocorrencia(cpf_solicitante, cep, numero)
        elif choice == '3':
            id_ocorrencia = int(input("ID da Ocorrência: "))
            new_status = input("Novo Status: ")
            atualizar_status_ocorrencia(id_ocorrencia, new_status)
        elif choice == '4':
            id_tecnico = int(input("ID do Técnico: "))
            ocorrencias_por_tecnico(id_tecnico)
        elif choice == '5':
            id_ocorrencia = int(input("ID da Ocorrência: "))
            id_tecnico = int(input("ID do Técnico: "))
            definir_tecnico_ocorrencia(id_ocorrencia, id_tecnico)
        elif choice == '6':
            table_name = input("Nome da Tabela: ")
            listar_tabelas(table_name)
        elif choice == '7':
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()
