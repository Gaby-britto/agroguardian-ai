import serial

from weather.weather_data_service import (
    get_precipitation_mm
)

from risk.risk_service import (
    evaluate_precipitation_risk,
    evaluate_operational_risk
)


# ==========================================================
# Configuração da comunicação Serial
# ==========================================================

# Endereço RFC2217 disponibilizado pelo Wokwi.
SERIAL_URL = "rfc2217://localhost:4000"

# Deve utilizar o mesmo baud rate configurado no ESP32.
SERIAL_BAUD_RATE = 115200

# Tempo máximo de espera por uma leitura da Serial.
SERIAL_TIMEOUT = 5


# ==========================================================
# Campos recebidos dos sensores
# ==========================================================

# Valores físicos/simulados enviados pelo ESP32.
SENSOR_FIELDS = {
    "soil_moisture",
    "pitch",
    "roll",
    "water_distance"
}


# ==========================================================
# Campos de risco recebidos do ESP32
# ==========================================================

# O ESP32 realiza a primeira avaliação de risco utilizando
# exclusivamente as informações disponíveis localmente
# pelos sensores conectados à placa.
#
# sensor_operational_risk representa o risco consolidado
# calculado apenas com:
#
# - umidade do solo;
# - pitch;
# - roll;
# - distância do corpo d'água.

RISK_FIELDS = {
    "soil_risk",
    "pitch_risk",
    "roll_risk",
    "water_risk",
    "sensor_operational_risk"
}


# ==========================================================
# Campos obrigatórios
# ==========================================================

# Uma mensagem da Serial somente será considerada válida
# quando possuir todos os valores dos sensores e todos os
# riscos calculados pelo ESP32.

REQUIRED_FIELDS = (
    SENSOR_FIELDS
    | RISK_FIELDS
)


# ==========================================================
# Conversão da mensagem Serial
# ==========================================================

def parse_line(
    line: str
) -> dict | None:
    """
    Converte uma linha enviada pelo ESP32 em um
    dicionário Python.

    Exemplo de entrada:

    soil_moisture=62.4;
    pitch=13.7;
    roll=2.8;
    water_distance=185.3;
    soil_risk=MEDIUM;
    pitch_risk=HIGH;
    roll_risk=LOW;
    water_risk=LOW;
    sensor_operational_risk=HIGH;

    A mensagem é recebida em uma única linha pela Serial.
    """

    data = {}

    # Divide os campos utilizando ";" como separador.
    fields = line.split(";")

    for field in fields:

        # Ignora campos vazios, incluindo o último elemento
        # produzido pelo ";" final da mensagem.
        if not field:
            continue

        # Ignora qualquer conteúdo que não esteja no padrão:
        # chave=valor
        if "=" not in field:
            continue

        key, value = field.split(
            "=",
            1
        )

        key = key.strip()
        value = value.strip()

        # --------------------------------------------------
        # Valores numéricos dos sensores
        # --------------------------------------------------

        if key in SENSOR_FIELDS:

            try:
                data[key] = float(value)

            except ValueError:
                # Caso algum valor que deveria ser numérico
                # seja inválido, descarta toda a leitura.
                return None

        # --------------------------------------------------
        # Classificações de risco
        # --------------------------------------------------

        elif key in RISK_FIELDS:

            data[key] = value

    # ------------------------------------------------------
    # Validação da leitura
    # ------------------------------------------------------

    # Somente aceita a mensagem quando todos os campos
    # obrigatórios estiverem presentes.
    if not REQUIRED_FIELDS.issubset(
        data.keys()
    ):
        return None

    return data


# ==========================================================
# Inclusão dos dados climáticos
# ==========================================================

def add_weather_data(
    readings: dict
) -> dict:
    """
    Complementa a leitura proveniente do ESP32 com
    informações climáticas.

    Atualmente a precipitação utiliza um valor fixo através
    do weather_data_service.

    Futuramente esta mesma função continuará sendo utilizada,
    porém o valor será obtido através da API climática.
    """

    # Obtém a precipitação acumulada em milímetros.
    precipitation_mm = (
        get_precipitation_mm()
    )

    # Classifica individualmente o risco associado
    # à precipitação.
    precipitation_risk = (
        evaluate_precipitation_risk(
            precipitation_mm
        )
    )

    # Adiciona as informações climáticas ao snapshot.
    readings["precipitation_mm"] = (
        precipitation_mm
    )

    readings["precipitation_risk"] = (
        precipitation_risk
    )

    return readings


# ==========================================================
# Avaliação final do risco operacional
# ==========================================================

def add_operational_risk(
    readings: dict
) -> dict:
    """
    Calcula o risco operacional final da aplicação.

    O ESP32 já fornece sensor_operational_risk, que considera
    somente os sensores locais.

    Nesta etapa, o Python combina esse resultado com o risco
    climático para produzir operational_risk.
    """

    operational_risk = (
        evaluate_operational_risk(
            sensor_operational_risk=readings[
                "sensor_operational_risk"
            ],
            precipitation_risk=readings[
                "precipitation_risk"
            ],
            soil_risk=readings[
                "soil_risk"
            ],
            pitch_risk=readings[
                "pitch_risk"
            ],
            roll_risk=readings[
                "roll_risk"
            ],
            water_risk=readings[
                "water_risk"
            ]
        )
    )

    readings["operational_risk"] = (
        operational_risk
    )

    return readings


# ==========================================================
# Leitura dos dados do ESP32
# ==========================================================

def read_sensor_data() -> dict:
    """
    Aguarda uma leitura completa enviada pelo ESP32.

    Após receber os dados:

    1. interpreta a mensagem da Serial;
    2. adiciona os dados climáticos;
    3. calcula o risco operacional final;
    4. salva o snapshot localmente;
    5. retorna os dados para o menu.
    """

    print(
        "\nConectando ao ESP32..."
    )

    with serial.serial_for_url(
        SERIAL_URL,
        baudrate=SERIAL_BAUD_RATE,
        timeout=SERIAL_TIMEOUT
    ) as serial_connection:

        while True:

            # ------------------------------------------------
            # Leitura da mensagem Serial
            # ------------------------------------------------

            raw_line = (
                serial_connection
                .readline()
                .decode(
                    "utf-8",
                    errors="ignore"
                )
                .strip()
            )

            # Ignora ciclos sem conteúdo recebido.
            if not raw_line:
                continue

            # ------------------------------------------------
            # Conversão e validação
            # ------------------------------------------------

            readings = parse_line(
                raw_line
            )

            # Caso a mensagem esteja incompleta ou inválida,
            # aguarda a próxima leitura do ESP32.
            if readings is None:
                continue

            # ------------------------------------------------
            # Dados climáticos
            # ------------------------------------------------

            readings = add_weather_data(
                readings
            )

            # ------------------------------------------------
            # Risco operacional final
            # ------------------------------------------------

            readings = add_operational_risk(
                readings
            )

            # ------------------------------------------------
            # Retorno para o menu
            # ------------------------------------------------

            return readings