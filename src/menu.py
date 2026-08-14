import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def run_python_script(script_path: str) -> None:
    """Run a project script using the same Python interpreter as the menu."""
    subprocess.run(
        [sys.executable, script_path],
        cwd=PROJECT_ROOT,
        check=True,
    )


def open_dashboard() -> None:
    """Start the Streamlit dashboard using the active Python environment."""
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", "dashboard/app.py"],
        cwd=PROJECT_ROOT,
        check=True,
    )


def start_menu() -> None:
    while True:
        print("\n" + "=" * 50)
        print("🌱 AGROGUARDIAN AI")
        print("=" * 50)

        print("1 - Gerar Dataset")
        print("2 - Popular Banco de Dados")
        print("3 - Treinar Modelo")
        print("4 - Executar Fluxo Completo")
        print("5 - Abrir Dashboard")
        print("0 - Sair")

        option = input("\nEscolha uma opção: ")

        try:
            if option == "1":
                run_python_script("src/dataset_generator.py")

            elif option == "2":
                run_python_script("src/database_setup.py")

            elif option == "3":
                run_python_script("src/model.py")

            elif option == "4":
                print("\nExecutando fluxo completo...")

                run_python_script("src/dataset_generator.py")
                run_python_script("src/database_setup.py")
                run_python_script("src/model.py")

                print("\nProcesso concluído!")

            elif option == "5":
                open_dashboard()

            elif option == "0":
                print("\nEncerrando sistema...")
                break

            else:
                print("\nOpção inválida.")

        except subprocess.CalledProcessError as error:
            print(
                "\nNão foi possível concluir a operação "
                f"(código {error.returncode})."
            )
