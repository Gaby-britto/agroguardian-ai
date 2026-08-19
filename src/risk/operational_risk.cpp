#include "operational_risk.h"

#include "../constants.h"

#include <Arduino.h>
#include <math.h>

// ==========================================================
// Umidade do solo
// ==========================================================

RiskLevel evaluateSoilRisk(
    float soilMoisture
) {

    if (
        soilMoisture >
        SOIL_RISK_CRITICAL_THRESHOLD
    ) {
        return RiskLevel::CRITICAL_RISK;
    }

    if (
        soilMoisture >
        SOIL_RISK_HIGH_THRESHOLD
    ) {
        return RiskLevel::HIGH_RISK;
    }

    if (
        soilMoisture >
        SOIL_RISK_MEDIUM_THRESHOLD
    ) {
        return RiskLevel::MEDIUM_RISK;
    }

    return RiskLevel::LOW_RISK;
}

// ==========================================================
// Inclinação
// ==========================================================

RiskLevel evaluateInclinationRisk(
    float inclination
) {

    float absoluteInclination =
        fabs(inclination);

    if (
        absoluteInclination >
        INCLINATION_RISK_CRITICAL_THRESHOLD
    ) {
        return RiskLevel::CRITICAL_RISK;
    }

    if (
        absoluteInclination >
        INCLINATION_RISK_HIGH_THRESHOLD
    ) {
        return RiskLevel::HIGH_RISK;
    }

    if (
        absoluteInclination >
        INCLINATION_RISK_MEDIUM_THRESHOLD
    ) {
        return RiskLevel::MEDIUM_RISK;
    }

    return RiskLevel::LOW_RISK;
}

// ==========================================================
// Distância do corpo d'água
// ==========================================================

RiskLevel evaluateWaterRisk(
    float waterDistance
) {

    if (
        waterDistance <
        WATER_RISK_CRITICAL_DISTANCE_M
    ) {
        return RiskLevel::CRITICAL_RISK;
    }

    if (
        waterDistance <
        WATER_RISK_HIGH_DISTANCE_M
    ) {
        return RiskLevel::HIGH_RISK;
    }

    if (
        waterDistance <=
        WATER_RISK_MEDIUM_DISTANCE_M
    ) {
        return RiskLevel::MEDIUM_RISK;
    }

    return RiskLevel::LOW_RISK;
}

// ==========================================================
// Maior risco individual
// ==========================================================

RiskLevel getHighestRisk(
    const RiskAssessment& assessment
) {

    RiskLevel highest =
        assessment.soilRisk;

    if (
        static_cast<int>(
            assessment.pitchRisk
        )
        >
        static_cast<int>(highest)
    ) {
        highest = assessment.pitchRisk;
    }

    if (
        static_cast<int>(
            assessment.rollRisk
        )
        >
        static_cast<int>(highest)
    ) {
        highest = assessment.rollRisk;
    }

    if (
        static_cast<int>(
            assessment.waterRisk
        )
        >
        static_cast<int>(highest)
    ) {
        highest = assessment.waterRisk;
    }

    return highest;
}

// ==========================================================
// Regras combinatórias
// ==========================================================

RiskLevel evaluateCombinedRisk(
    const RiskAssessment& assessment
) {

    // ------------------------------------------------------
    // Qualquer condição individual crítica
    // ------------------------------------------------------

    if (
        assessment.soilRisk
            == RiskLevel::CRITICAL_RISK
        ||
        assessment.pitchRisk
            == RiskLevel::CRITICAL_RISK
        ||
        assessment.rollRisk
            == RiskLevel::CRITICAL_RISK
        ||
        assessment.waterRisk
            == RiskLevel::CRITICAL_RISK
    ) {
        return RiskLevel::CRITICAL_RISK;
    }

    // ------------------------------------------------------
    // Inclinação alta próximo à água
    // ------------------------------------------------------

    if (
        assessment.waterRisk
            == RiskLevel::HIGH_RISK
        &&
        (
            assessment.pitchRisk
                == RiskLevel::HIGH_RISK
            ||
            assessment.rollRisk
                == RiskLevel::HIGH_RISK
        )
    ) {
        return RiskLevel::CRITICAL_RISK;
    }

    // ------------------------------------------------------
    // Solo muito úmido + inclinação elevada
    // ------------------------------------------------------

    if (
        assessment.soilRisk
            == RiskLevel::HIGH_RISK
        &&
        (
            assessment.pitchRisk
                == RiskLevel::HIGH_RISK
            ||
            assessment.rollRisk
                == RiskLevel::HIGH_RISK
        )
    ) {
        return RiskLevel::CRITICAL_RISK;
    }

    // ------------------------------------------------------
    // Conta quantas condições estão em risco alto
    // ------------------------------------------------------

    int highRiskCount = 0;

    if (
        assessment.soilRisk
            == RiskLevel::HIGH_RISK
    ) {
        highRiskCount++;
    }

    if (
        assessment.pitchRisk
            == RiskLevel::HIGH_RISK
    ) {
        highRiskCount++;
    }

    if (
        assessment.rollRisk
            == RiskLevel::HIGH_RISK
    ) {
        highRiskCount++;
    }

    if (
        assessment.waterRisk
            == RiskLevel::HIGH_RISK
    ) {
        highRiskCount++;
    }

    // Duas ou mais condições altas
    if (highRiskCount >= 2) {
        return RiskLevel::CRITICAL_RISK;
    }

    // ------------------------------------------------------
    // Duas ou mais condições médias elevam para alto
    // ------------------------------------------------------

    int mediumRiskCount = 0;

    if (
        assessment.soilRisk
            == RiskLevel::MEDIUM_RISK
    ) {
        mediumRiskCount++;
    }

    if (
        assessment.pitchRisk
            == RiskLevel::MEDIUM_RISK
    ) {
        mediumRiskCount++;
    }

    if (
        assessment.rollRisk
            == RiskLevel::MEDIUM_RISK
    ) {
        mediumRiskCount++;
    }

    if (
        assessment.waterRisk
            == RiskLevel::MEDIUM_RISK
    ) {
        mediumRiskCount++;
    }

    if (mediumRiskCount >= 2) {
        return RiskLevel::HIGH_RISK;
    }

    // Caso contrário, utiliza o maior risco individual
    return getHighestRisk(
        assessment
    );
}

// ==========================================================
// Avaliação completa
// ==========================================================

RiskAssessment evaluateOperationalRisk(
    const SensorReadings& readings
) {

    RiskAssessment assessment;

    assessment.soilRisk =
        evaluateSoilRisk(
            readings.soilMoisture
        );

    assessment.pitchRisk =
        evaluateInclinationRisk(
            readings.pitch
        );

    assessment.rollRisk =
        evaluateInclinationRisk(
            readings.roll
        );

    assessment.waterRisk =
        evaluateWaterRisk(
            readings.waterDistance
        );

    assessment.operationalRisk =
        evaluateCombinedRisk(
            assessment
        );

    return assessment;
}

// ==========================================================
// Conversão para texto
// ==========================================================

const char* riskLevelToString(
    RiskLevel risk
) {

    switch (risk) {

        case RiskLevel::LOW_RISK:
            return "LOW";

        case RiskLevel::MEDIUM_RISK:
            return "MEDIUM";

        case RiskLevel::HIGH_RISK:
            return "HIGH";

        case RiskLevel::CRITICAL_RISK:
            return "CRITICAL";

        default:
            return "UNKNOWN";
    }
}

// ==========================================================
// Saída Serial
// ==========================================================

void printOperationalData(
    const SensorReadings& readings,
    const RiskAssessment& assessment
) {

    Serial.print("soil_moisture=");
    Serial.print(
        readings.soilMoisture,
        1
    );

    Serial.print(";pitch=");
    Serial.print(
        readings.pitch,
        1
    );

    Serial.print(";roll=");
    Serial.print(
        readings.roll,
        1
    );

    Serial.print(";water_distance=");
    Serial.print(
        readings.waterDistance,
        1
    );

    Serial.print(";soil_risk=");
    Serial.print(
        riskLevelToString(
            assessment.soilRisk
        )
    );

    Serial.print(";pitch_risk=");
    Serial.print(
        riskLevelToString(
            assessment.pitchRisk
        )
    );

    Serial.print(";roll_risk=");
    Serial.print(
        riskLevelToString(
            assessment.rollRisk
        )
    );

    Serial.print(";water_risk=");
    Serial.print(
        riskLevelToString(
            assessment.waterRisk
        )
    );

    Serial.print(";sensor_operational_risk=");
    Serial.print(
        riskLevelToString(
            assessment.operationalRisk
        )
    );

    Serial.println(";");
}