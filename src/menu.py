import subprocess
import sys
from pathlib import Path

from sensors.serial_sensor_reader import (
    read_sensor_data
)


PROJECT_ROOT = Path(
    __file__
).resolve().parent


def run_python_script(
    script_path: str
) -> None:

    subprocess.run(
        [
            sys.executable,
            script_path
        ],
        cwd=PROJECT_ROOT,
        check=True
    )


def open_dashboard() -> None:

    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "dashboard/app.py"
        ],
        cwd=PROJECT_ROOT,
        check=True
    )


def show_sensor_readings() -> None:

    print(
        "\nAguardando leitura dos sensores..."
    )

    readings = read_sensor_data()

    print(
        "\nLeitura recebida com sucesso!"
    )

    print(
        "\n"
        + "=" * 50
    )

    print(
        "DADOS DOS SENSORES"
    )

    print(
        "=" * 50
    )

    print(
        "Umidade do solo: "
        f"{readings['soil_moisture']:.1f}%"
    )

    print(
        "Inclinação longitudinal (Pitch): "
        f"{readings['pitch']:.1f}°"
    )

    print(
        "Inclinação lateral (Roll): "
        f"{readings['roll']:.1f}°"
    )

    print(
        "Distância do corpo d'água: "
        f"{readings['proximity_distance']:.1f} m"
    )


def start_menu() -> None:

    while True:

        print(
            "\n"
            + "=" * 50
        )

        print(
            "🌱 AGROGUARDIAN AI"
        )

        print(
            "=" * 50
        )

        print(
            "1 - Exibir leitura dos sensores"
        )

        print(
            "2 - Gerar Dataset"
        )

        print(
            "3 - Popular Banco de Dados"
        )

        print(
            "4 - Treinar Modelo"
        )

        print(
            "5 - Executar Fluxo Completo"
        )

        print(
            "6 - Abrir Dashboard"
        )

        print(
            "0 - Sair"
        )

        option = input(
            "\nEscolha uma opção: "
        )

        try:

            if option == "1":

                show_sensor_readings()

            elif option == "2":

                run_python_script(
                    "src/dataset_generator.py"
                )

            elif option == "3":

                run_python_script(
                    "src/database_setup.py"
                )

            elif option == "4":

                run_python_script(
                    "src/model.py"
                )

            elif option == "5":

                print(
                    "\nExecutando fluxo completo..."
                )

                run_python_script(
                    "src/dataset_generator.py"
                )

                run_python_script(
                    "src/database_setup.py"
                )

                run_python_script(
                    "src/model.py"
                )

                print(
                    "\nProcesso concluído!"
                )

            elif option == "6":

                open_dashboard()

            elif option == "0":

                print(
                    "\nEncerrando sistema..."
                )

                break

            else:

                print(
                    "\nOpção inválida."
                )

        except subprocess.CalledProcessError as error:

            print(
                "\nNão foi possível concluir "
                "a operação "
                f"(código {error.returncode})."
            )

        except Exception as error:

            print(
                "\nErro ao realizar operação:"
            )

            print(error)