import psycopg2
from psycopg2 import Error

DB_HOST     = '---------'
DB_NAME     = '---------'
DB_USER     = '---------'
DB_PASSWORD = '---------'
DB_PORT     = '---------'

STATUS = ['Aberta','Em Andamento','Concluída','Cancelada']

def get_db_connection():
    try:
            conn = psycopg2.connect(
                host     = DB_HOST,
                database = DB_NAME,
                user     = DB_USER,
                password = DB_PASSWORD,
                port     = DB_PORT
            )
            return conn
    except Exception as error:
        print(f"Erro ao conectar ao banco de dados: {error}")
        return None
    
    
 ##Funções para checar existencia no Banco   
    
def local_E(cep, nmr):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM Local WHERE cep = %s AND numero = %s",
                    [cep,nmr]
                )
                return cursor.fetchone() is not None
        except Error as e:
            print(f"Error: {e}")
            conn.rollback()
        finally:
            conn.close()
            
def tec_E(cpf):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM Tecnico WHERE cpf = %s",
                    [cpf]
                )
                return cursor.fetchone() is not None
        except Error as e:
            print(f"Error: {e}")
            conn.rollback()
        finally:
            conn.close()
            
def ocorr_E(nmr_ocorrencia):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM Ocorrencia WHERE id_ocorrencia = %s",
                    [nmr_ocorrencia]
                )
                return cursor.fetchone() is not None
        except Error as e:
            print(f"Error: {e}")
            conn.rollback()
        finally:
            conn.close()

def user_E(cpf):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM Usuario WHERE cpf = %s",
                    [cpf]
                )
                return cursor.fetchone() is not None
        except Error as e:
            print(f"Error: {e}")
            conn.rollback()
        finally:
            conn.close()
            
##Funções de inserção no banco

def criar_local(cep,numero):
    print("Local não existe no banco, forneça os seguintes dados")
    bairro = input("Bairro: ")
    logradouro = input("Logradouro: ")
    complemento = input("Complemento: ")
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "CALL criar_local(%s, %s, %s, %s, %s)",
                [cep, numero, complemento, bairro, logradouro]
            )
            conn.commit()
        print("Local Criado com Sucesso!!")
    except Exception as e:
        print(f"Erro ao criar Local: {e}")
        conn.rollback()
    finally:
        conn.close()


def criar_usuario(cpf, nome, fone, email):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "CALL criar_usuario(%s, %s, %s, %s)",
                    [cpf, nome, fone, email]
                )
                conn.commit()
                print("Usuário criado com sucesso!")
        except Exception as e:
            print(f"Erro ao criar usuário: {e}")
            conn.rollback()
        finally:
            conn.close()
                

def criar_ocorrencia(cpf_solicitante, cep, numero):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                if(not local_E(cep,numero)):
                    criar_local(cep,numero)
                cursor.execute("CALL criar_ocorrencia(%s, %s, %s)",
                            [cpf_solicitante, cep, numero]
                )
                conn.commit()
                print("Ocorrência criada com sucesso!")
            conn.commit()
        except Error as e:
            print(f"Erro ao criar ocorrência: {e}")
            conn.rollback()
        finally:
            conn.close()

def criar_tecnico(cpf):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                if(not user_E(cpf)):
                    print("Necessario criar o usuario antes")
                    nome = input("Nome: ")
                    fone = input("Telefone: ")
                    email = input("E-mail: ")
                    criar_usuario(cpf, nome, fone, email)
                cursor.execute("CALL criar_tecnico(%s)",
                            [cpf]
                )
                print("Tecnico criado com sucesso")
                conn.commit()
        except Error as e:
            print(f"Erro ao criar Tecnico: {e}")
            conn.rollback()
        finally:
            conn.close()
            
            
##Funções de interface entre o programa e o banco          

def ocorr_D():
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor as cursor:
                cursor.execute("Select * FROM Ocorrencia WHERE status = %s",STATUS[0])
                tabela = cursor.fetchall()
                for i in tabela:
                    print(i)
            conn.commit()
        except Error as e:
            print(f"Erro ao criar Tecnico: {e}")
            conn.rollback()
        finally:
            conn.close()
 
def ocorrencias_abertas():
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM Ocorrencia WHERE status = %s OR status = %s", [STATUS[0],STATUS[1]])
                ocorrencias = cursor.fetchall()
                if ocorrencias:
                    print(f"Ocorrências Disponíveis")
                    for ocorrencia in ocorrencias:
                        print(ocorrencia)
                else:
                    print("Sem Ocorrências disponíveis")
                    return False
            conn.commit()
            return True
        except Error as e:
            print(f"Erro ao buscar ocorrências do técnico: {e}")
            conn.rollback()
        finally:
            conn.close() 
            
def ocorrencias_por_tecnico(cpf_tecnico):
    conn = get_db_connection()
    if conn:
        try:
            if(not tec_E(cpf_tecnico)):
                print("Tecnico não existe")
                return False
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM fn_get_ocorrencias_por_tecnico(%s)", [cpf_tecnico])
                ocorrencias = cursor.fetchall()
                if ocorrencias:
                    print(f"Ocorrências atribuídas ao técnico {cpf_tecnico}:")
                    for ocorrencia in ocorrencias:
                        print(ocorrencia)
                else:
                    print(f"Nenhuma ocorrência encontrada para o técnico {cpf_tecnico}.")
                    return False
            conn.commit()
            return True
        except Error as e:
            print(f"Erro ao buscar ocorrências do técnico: {e}")
            conn.rollback()
        finally:
            conn.close()
            
def ocorrencias_por_user(cpf_tecnico):
    conn = get_db_connection()
    if conn:
        try:
            if(not user_E(cpf_tecnico)):
                print("Usuario não existe")
                return False
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM vw_ocorrencias_por_usuario WHERE cpf = %s", [cpf_tecnico])
                ocorrencias = cursor.fetchall()
                if ocorrencias:
                    print(f"Ocorrências atribuídas ao Usuario: {cpf_tecnico}:")
                    for ocorrencia in ocorrencias:
                        print(ocorrencia)
                else:
                    print(f"Nenhuma ocorrência encontrada para o Usuario {cpf_tecnico}.")
            conn.commit()
            return True
        except Error as e:
            print(f"Erro ao buscar ocorrências do Usuario: {e}")
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
            
            
##Funções de edição

def definir_tecnico_ocorrencia(id_ocorrencia, cpf_tecnico):
    conn = get_db_connection()
    if conn:
        try:
            if(not ocorr_E(id_ocorrencia)):
                print("Ocorrência não existe")
                return
            elif(not tec_E(cpf_tecnico)):
                print("Tecnico não existe")
                return
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT atribuir_ocorrencia(%s,%s::smallint)",
                    [cpf_tecnico, id_ocorrencia]
                )
                if cursor.rowcount > 0:
                    print(f"Técnico {cpf_tecnico} atribuído à ocorrência {id_ocorrencia}.")
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
            if(STATUS.count(new_status) == 0):
                print("Status inválido.")
                return
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE ocorrencia SET status = %s WHERE id_ocorrencia = %s",
                    [new_status, id_ocorrencia]
                )
                if cursor.rowcount > 0:
                    print(f"Status da ocorrência {id_ocorrencia} atualizado para '{new_status}'.")
            conn.commit()
        except Error as e:
            print(f"Erro ao atualizar status da ocorrência: {e}")
            conn.rollback()
        finally:
            conn.close()
            
def conclui_ocorrencia(id_ocorrencia):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE ocorrencia SET status = %s WHERE id_ocorrencia = %s",
                    [STATUS[2], id_ocorrencia]
                )
                if cursor.rowcount > 0:
                    print(f"Status da ocorrência {id_ocorrencia} atualizado para 'Concluida'.")
            conn.commit()
        except Error as e:
            print(f"Erro ao atualizar status da ocorrência: {e}")
            conn.rollback()
        finally:
            conn.close()


def main():
    while True:
        print("\nMenu:")
        print("1. Criar Usuário")
        print("2. Criar Ocorrência")
        print("3. Criar Técnico")
        print("4. Atribuir uma Ocorrência a um técnico")
        print("5. Concluir uma Ocorrência")
        print("6. Listar Ocorrências de um Técnico")
        print("7. Listar Ocorrências de um Usuário")
        print("8. Sair")
        
        ##Parei aqui, o trigger será sempre que um técnico for adicionado, devemos adicionar uma ocorrencia a ele.

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
            cpf_tecnico = input("CPF do Ténico: ")
            criar_tecnico(cpf_tecnico)
        elif choice == '4':
            cpf_tecnico = input("CPF do Técnico: ")
            if(tec_E(cpf_tecnico)):
                ocorrencias_abertas()
                id_ocorrencia = int(input("Digite o ID da ocorrencia: "))
                definir_tecnico_ocorrencia(id_ocorrencia,cpf_tecnico)
            else:
                print("Tecnico não existe.")
        elif choice == '5':
            cpf_tecnico = input("CPF do Técnico: ")
            if(tec_E(cpf_tecnico)):
                ocorrencias_por_tecnico(cpf_tecnico)
                id_ocorrencia = int(input("Digite o ID da ocorrencia a ser concluída: "))
                conclui_ocorrencia(id_ocorrencia)
            else:
                print("Tecnico não existe.")
        elif choice == '6':
            cpf_tecnico = input("CPF do Técnico: ")
            if(tec_E(cpf_tecnico)):
                ocorrencias_por_tecnico(cpf_tecnico)
            else:
                print("Tecnico não existe.")   
        elif choice == '7':
            cpf_usr = input("CPF do usuario: ")
            ocorrencias_por_user(cpf_usr)
        elif choice == '8':
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()
