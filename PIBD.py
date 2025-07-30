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

def atualizar_status_ocorrencia(id_ocorrencia, new_status):
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
            msg = str(e)
            if "ocorrencia_status_check" in msg:
                print("Erro: O status informado não é permitido pela regra de transição de status da ocorrência.")
                print("Verifique se a mudança de status está de acordo com as regras do sistema.")
            elif "Status inválido:" in msg:
                # Extrai a transição inválida da mensagem de erro
                inicio = msg.find("Status inválido:")
                fim = msg.find("\n", inicio)
                detalhe = msg[inicio:fim] if fim > -1 else msg[inicio:]
                print("Erro de transição de status:", detalhe)
                print("Transições permitidas:")
                print("- Aberta → Em Andamento ou Cancelada")
                print("- Em Andamento → Concluída ou Cancelada")
                print("- Concluída/Cancelada não podem ser alteradas")
            else:
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

def criar_tecnico(cpf, nome, fone, email):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 FROM tecnico WHERE cpf = %s", (cpf,))
                if cursor.fetchone():
                    print(f"Erro: CPF já cadastrado na tabela técnico para {nome}.")
                    return
                cursor.execute(
                    "INSERT INTO tecnico (cpf, nome, fone, email) VALUES (%s, %s, %s, %s)",
                    (cpf, nome, fone, email)
                )
                conn.commit()
                print("Técnico criado com sucesso!")
        except Exception as e:
            print(f"Erro ao criar técnico: {e}")
            conn.rollback()
        finally:
            conn.close()   

def listar_tecnicos():
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM tecnico;")
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]  # Obter nomes das colunas

                if rows:
                    print("\nDados da Tabela 'tecnico':")
                    print("-" * 50)
                    print(" | ".join(columns))
                    print("-" * 50)
                    for row in rows:
                        print(" | ".join(map(str, row)))
                    print("-" * 50)
                else:
                    print("Nenhum dado encontrado na tabela 'tecnico'.")
        except Error as e:
            print(f"Erro ao listar dados da tabela 'tecnico': {e}")
        finally:
            conn.close()  

def listar_ocorrencias_por_cpf():
    cpf = input("Digite o CPF do solicitante: ")
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM ocorrencia WHERE id_solicitante = (SELECT id_solicitante FROM solicitante WHERE cpf = %s)",
                    (cpf,)
                )
                ocorrencias = cursor.fetchall()
                if ocorrencias:
                    print(f"Ocorrências para o CPF {cpf}:")
                    for ocorrencia in ocorrencias:
                        print("Ocorrencia:",ocorrencia)
                else:
                    print(f"Nenhuma ocorrência encontrada para o CPF {cpf}.")
        except Error as e:
            print(f"Erro ao buscar ocorrências: {e}")
        finally:
            conn.close()

def vincular_tecnico_ocorrencia(id_ocorrencia, id_tecnico):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT status FROM ocorrencia WHERE id_ocorrencia = %s", (id_ocorrencia,))
                result = cursor.fetchone()
                if not result:
                    print(f"Nenhuma ocorrência encontrada com o ID {id_ocorrencia}.")
                    return
                status = result[0]
                if status in ('Concluída', 'Cancelada'):
                    print(f"Não é possível vincular técnico: ocorrência já está '{status}'.")
                    return
                cursor.execute("SELECT fn_vincular_tecnico_ocorrencia(%s, %s)", (id_ocorrencia, id_tecnico))
                print(f"Técnico {id_tecnico} vinculado à ocorrência {id_ocorrencia}.")
            conn.commit()
        except Error as e:
            print(f"Erro ao vincular técnico à ocorrência: {e}")
            conn.rollback()
        finally:
            conn.close()

def main():
    while True:
        print("\nMenu Inicial:")
        print("1. Cidadão")
        print("2. Tecnico")  
        print("3. Sair")


        choice = input("Tipo de Usuário: ")

        if choice == '1':
            while True:
                print("\nMenu Cidadão:")
                print("1. Criar Usuário")
                print("2. Criar Ocorrência")
                print("3. Listar Tabelas")
                print("4. Consultar Ocorrências por CPF")
                print("5. Sair")
            
                choice = input("Opção: ")

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
                    table_name = input("Nome da Tabela: ")
                elif choice == '4':
                    listar_ocorrencias_por_cpf()
                    cpf = input("Digite o CPF do solicitante: ")
                    listar_ocorrencias_por_cpf(cpf_solicitante, cep, numero)
                elif choice == '5':
                    break
        elif choice == '2': 
            while True: 
                print("\nMenu Técnico:")
                print("1. Criar Usuário")
                print("2. Criar Ocorrência")
                print("3. Criar Técnico")
                print("4. Atualizar Status da Ocorrência")
                print("5. Listar Ocorrências por Técnico")
                print("6. Vincular Técnico a Ocorrência")
                print("7. Listar Técnicos")
                print("8. Listar Tabelas")
                print("9. Sair")

                choice = input("Opção: ")

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
                    cpf = input("CPF do Técnico: ")
                    nome = input("Nome do Técnico: ")
                    fone = input("Telefone do Técnico: ")
                    email = input("E-mail do Técnico: ")
                    criar_tecnico(cpf, nome, fone, email)    
                elif choice == '4':
                    id_ocorrencia = int(input("ID da Ocorrência: "))
                    new_status = input("Novo Status: ")
                    atualizar_status_ocorrencia(id_ocorrencia, new_status)
                elif choice == '5':
                    id_tecnico = int(input("ID do Técnico: "))
                    ocorrencias_por_tecnico(id_tecnico)
                elif choice == '6':
                    id_ocorrencia = int(input("ID da Ocorrência: "))
                    id_tecnico = int(input("ID do Técnico: "))
                    vincular_tecnico_ocorrencia(id_ocorrencia, id_tecnico)
                elif choice == '7':
                    listar_tecnicos()  
                elif choice == '8':
                    table_name = input("Nome da Tabela: ")
                    listar_tabelas(table_name)
                elif choice == '9':
                    break
                else:
                    print("Opção inválida. Tente novamente.")
        elif choice == '3':
            print("Saindo do programa, até mais...")
            break            
        else:
            print("Opção de usuário inválida. Tente novamente.")
        
if __name__ == "__main__":
    main()
