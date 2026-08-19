#include <Arduino.h>

#include "constants.h"
#include "sensors/sensor_readings.h"
#include "risk/operational_risk.h"

// ==========================================================
// SETUP
// ==========================================================

void setup() {

    Serial.begin(
        SERIAL_BAUD_RATE
    );

    delay(1000);

    initializeSensors();
}

// ==========================================================
// LOOP
// ==========================================================

void loop() {

    SensorReadings readings =
        readSensors();

    RiskAssessment assessment =
        evaluateOperationalRisk(
            readings
        );

    printOperationalData(
        readings,
        assessment
    );

    delay(
        SENSOR_READ_INTERVAL_MS
    );
}