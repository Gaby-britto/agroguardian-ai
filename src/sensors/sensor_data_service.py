import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIRECTORY = PROJECT_ROOT / "data"

SENSOR_DATA_FILE = (
    DATA_DIRECTORY
    / "sensor_readings.json"
)


def save_sensor_readings(
    readings: dict
) -> None:

    DATA_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        SENSOR_DATA_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            readings,
            file,
            indent=4,
            ensure_ascii=False
        )


def load_sensor_readings() -> dict | None:

    if not SENSOR_DATA_FILE.exists():
        return None

    with open(
        SENSOR_DATA_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)