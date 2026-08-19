#pragma once

#include "../sensors/sensor_readings.h"

// ==========================================================
// Níveis de risco
// ==========================================================

enum class RiskLevel {
    LOW_RISK = 0,
    MEDIUM_RISK = 1,
    HIGH_RISK = 2,
    CRITICAL_RISK = 3
};

// ==========================================================
// Resultado da análise
// ==========================================================

struct RiskAssessment {
    RiskLevel soilRisk;
    RiskLevel pitchRisk;
    RiskLevel rollRisk;
    RiskLevel waterRisk;
    RiskLevel operationalRisk;
};

// ==========================================================
// Funções
// ==========================================================

RiskAssessment evaluateOperationalRisk(
    const SensorReadings& readings
);

const char* riskLevelToString(
    RiskLevel risk
);

void printOperationalData(
    const SensorReadings& readings,
    const RiskAssessment& assessment
);