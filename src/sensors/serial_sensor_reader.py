import serial

from .sensor_data_service import (
    save_sensor_readings
)


SERIAL_URL = "rfc2217://localhost:4000"

SERIAL_BAUD_RATE = 115200

SERIAL_TIMEOUT = 5


def parse_sensor_line(
    line: str
) -> dict | None:
    """
    Converte a mensagem enviada pelo ESP32
    para um dicionário Python.

    Exemplo:

    soil_moisture=62.4;
    pitch=13.7;
    roll=2.8;
    proximity_distance=185.3;
    """

    try:

        readings = {}

        fields = line.split(";")

        for field in fields:

            if not field:
                continue

            if "=" not in field:
                continue

            key, value = field.split(
                "=",
                1
            )

            readings[key] = float(value)

        required_fields = {
            "soil_moisture",
            "pitch",
            "roll",
            "proximity_distance"
        }

        if not required_fields.issubset(
            readings.keys()
        ):
            return None

        return readings

    except ValueError:
        return None


def read_sensor_data() -> dict:
    """
    Aguarda uma leitura válida enviada
    pelo ESP32 e retorna os valores.
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

            raw_line = (
                serial_connection
                .readline()
                .decode(
                    "utf-8",
                    errors="ignore"
                )
                .strip()
            )

            if not raw_line:
                continue

            readings = parse_sensor_line(
                raw_line
            )

            if readings is None:
                continue

            save_sensor_readings(
                readings
            )

            return readings