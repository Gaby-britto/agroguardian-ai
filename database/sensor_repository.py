# ==========================================================
# Campos persistidos no banco
# ==========================================================

PERSISTED_FIELDS = [
    "soil_moisture",
    "pitch",
    "roll",
    "water_distance",
    "precipitation_mm",

    "soil_risk",
    "pitch_risk",
    "roll_risk",
    "water_risk",
    "precipitation_risk",

    "sensor_operational_risk",
    "operational_risk",

    "predicted_risk",
    "predictive_risk_score"
]


# ==========================================================
# Preparação dos dados para persistência
# ==========================================================

def prepare_sensor_record(
    readings: dict
) -> dict:
    """
    Prepara o snapshot operacional para persistência.

    Somente os campos definidos em PERSISTED_FIELDS são
    enviados ao banco.

    Informações utilizadas apenas durante a execução da
    aplicação, como risk_probabilities, permanecem fora
    da estrutura persistida.
    """

    missing_fields = [
        field
        for field in PERSISTED_FIELDS
        if field not in readings
    ]

    if missing_fields:
        raise ValueError(
            "Snapshot incompleto para persistência. "
            "Campos ausentes: "
            + ", ".join(
                missing_fields
            )
        )

    return {
        field: readings[field]
        for field in PERSISTED_FIELDS
    }


# ==========================================================
# Persistência
# ==========================================================

def save_sensor_record(
    readings: dict
) -> None:
    """
    Persiste o snapshot operacional no banco de dados.

    A implementação da conexão e da inserção será realizada
    posteriormente.

    Neste momento, a função já prepara e valida a estrutura
    que será enviada ao banco.
    """

    record = prepare_sensor_record(
        readings
    )

    # ======================================================
    # Integração futura com banco de dados
    # ======================================================

    # Exemplo conceitual:
    #
    # connection = get_database_connection()
    #
    # repository.insert(
    #     connection,
    #     record
    # )
    #
    # connection.commit()

    print(
        "\nRegistro preparado para persistência."
    )

    print(
        record
    )