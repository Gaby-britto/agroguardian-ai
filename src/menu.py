import subprocess
import sys
from pathlib import Path

from sensors.serial_sensor_reader import (
    read_sensor_data
)

from ml.prediction_service import (
    get_prediction
)

from sensors.sensor_data_service import (
    save_sensor_readings
)


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)


# ==========================================================
# Execução de scripts Python
# ==========================================================

def run_python_script(
    script_path: str
) -> None:
    """
    Executa um script Python utilizando o mesmo
    interpretador usado pelo menu.

    O diretório de execução é mantido na raiz do projeto
    para garantir que caminhos relativos como data/ e
    database/ funcionem corretamente.
    """

    subprocess.run(
        [
            sys.executable,
            script_path
        ],
        cwd=PROJECT_ROOT,
        check=True
    )


# ==========================================================
# Leitura dos sensores
# ==========================================================

def show_sensor_readings() -> None:
    """
    Realiza uma leitura do ESP32, complementa os dados
    com informações climáticas, calcula o risco operacional
    e executa a previsão do modelo de Machine Learning.
    """

    print(
        "\nAguardando leitura dos sensores..."
    )

    readings = read_sensor_data()

    # ======================================================
    # Previsão por Machine Learning
    # ======================================================

    prediction = get_prediction(
        readings
    )

    readings["predicted_risk"] = (
        prediction["predicted_risk"]
    )

    readings["predictive_risk_score"] = (
        prediction[
            "predictive_risk_score"
        ]
    )

    readings["risk_probabilities"] = (
        prediction["risk_probabilities"]
    )

    # ======================================================
    # Persistência do snapshot completo
    # ======================================================

    # A leitura somente é salva depois que todas as
    # informações foram consolidadas:
    #
    # - sensores;
    # - clima;
    # - riscos determinísticos;
    # - previsão de Machine Learning;
    # - probabilidades das classes.

    save_sensor_readings(
        readings
    )

    print(
        "\nLeitura recebida com sucesso!"
    )

    # ======================================================
    # Dados dos sensores
    # ======================================================

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
        f"{readings['water_distance']:.1f} m"
    )

    # ======================================================
    # Dados climáticos
    # ======================================================

    print(
        "\n"
        + "=" * 50
    )

    print(
        "DADOS CLIMÁTICOS"
    )

    print(
        "=" * 50
    )

    print(
        "Precipitação acumulada: "
        f"{readings['precipitation_mm']:.1f} mm"
    )

    # ======================================================
    # Análise determinística
    # ======================================================

    print(
        "\n"
        + "=" * 50
    )

    print(
        "ANÁLISE DE RISCO"
    )

    print(
        "=" * 50
    )

    print(
        "Risco - Umidade do solo: "
        f"{readings['soil_risk']}"
    )

    print(
        "Risco - Pitch: "
        f"{readings['pitch_risk']}"
    )

    print(
        "Risco - Roll: "
        f"{readings['roll_risk']}"
    )

    print(
        "Risco - Corpo d'água: "
        f"{readings['water_risk']}"
    )

    print(
        "Risco - Precipitação: "
        f"{readings['precipitation_risk']}"
    )

    print(
        "\nRisco operacional: "
        f"{readings['operational_risk']}"
    )

    # ======================================================
    # Previsão por Machine Learning
    # ======================================================

    print(
        "\n"
        + "=" * 50
    )

    print(
        "PREVISÃO MACHINE LEARNING"
    )

    print(
        "=" * 50
    )

    print(
        "Risco previsto: "
        f"{readings['predicted_risk']}"
    )

    print(
        "Score preditivo: "
        f"{readings['predictive_risk_score']:.2f}/100"
    )

    print(
        "\nProbabilidades:"
    )

    probabilities = (
        readings["risk_probabilities"]
    )

    for risk_level in [
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL"
    ]:

        probability = (
            probabilities.get(
                risk_level,
                0.0
            )
        )

        print(
            f"- {risk_level}: "
            f"{probability:.2%}"
        )


# ==========================================================
# Menu principal
# ==========================================================

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
            "3 - Treinar Modelo"
        )

        print(
            "4 - Popular Banco de Dados"
        )

        print(
            "5 - Abrir Dashboard"
        )

        print(
            "0 - Sair"
        )

        option = input(
            "\nEscolha uma opção: "
        )

        try:

            # ------------------------------------------------
            # Leitura dos sensores
            # ------------------------------------------------

            if option == "1":

                show_sensor_readings()

            # ------------------------------------------------
            # Geração do dataset
            # ------------------------------------------------

            elif option == "2":

                print(
                    "\nGerando dataset..."
                )

                run_python_script(
                    "src/dataset_generator.py"
                )

            # ------------------------------------------------
            # Treinamento do modelo
            # ------------------------------------------------

            elif option == "3":

                run_python_script(
                    "src/model.py"
                )

            # ------------------------------------------------
            # Banco de dados
            # ------------------------------------------------

            elif option == "4":

                run_python_script(
                    "src/database_setup.py"
                )

            # ------------------------------------------------
            # Dashboard
            # ------------------------------------------------

            elif option == "5":

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

            # ------------------------------------------------
            # Encerramento
            # ------------------------------------------------

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
                "\nNão foi possível concluir a operação "
                f"(código {error.returncode})."
            )

        except Exception as error:

            print(
                "\nErro ao realizar operação:"
            )

            print(error)