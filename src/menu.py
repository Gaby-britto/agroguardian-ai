import os

while True:

    print("\n" + "="*50)
    print("🌱 AGROGUARDIAN AI")
    print("="*50)

    print("1 - Gerar Dataset")
    print("2 - Popular Banco de Dados")
    print("3 - Treinar Modelo")
    print("4 - Executar Fluxo Completo")
    print("5 - Abrir Dashboard")
    print("0 - Sair")

    opcao = input("\nEscolha uma opção: ")

    if opcao == "1":
        os.system("python src/dataset_generator.py")

    elif opcao == "2":
        os.system("python src/database_setup.py")

    elif opcao == "3":
        os.system("python src/model.py")

    elif opcao == "4":

        print("\n Executando fluxo completo...")

        os.system("python src/dataset_generator.py")
        os.system("python src/database_setup.py")
        os.system("python src/model.py")

        print("\n Processo concluído!")

    elif opcao == "5":
        os.system("streamlit run dashboard/app.py")

    elif opcao == "0":

        print("\n Encerrando sistema...")
        break

    else:
        print("\n Opção inválida.")