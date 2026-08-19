#pragma once

// ==========================================================
// Comunicação Serial
// ==========================================================

constexpr unsigned long SERIAL_BAUD_RATE = 115200;
constexpr unsigned long SENSOR_READ_INTERVAL_MS = 2000;

// ==========================================================
// Umidade do solo
// ==========================================================

constexpr int SOIL_ADC_DRY = 0;
constexpr int SOIL_ADC_WET = 4095;

constexpr float SOIL_MOISTURE_MIN_PERCENT = 0.0f;
constexpr float SOIL_MOISTURE_MAX_PERCENT = 100.0f;

// ==========================================================
// HC-SR04 → LiDAR simulado
// ==========================================================

constexpr float ULTRASONIC_MIN_DISTANCE_CM = 2.0f;
constexpr float ULTRASONIC_MAX_DISTANCE_CM = 400.0f;

constexpr float LIDAR_SIMULATED_MIN_DISTANCE_M = 0.0f;
constexpr float LIDAR_SIMULATED_MAX_DISTANCE_M = 1000.0f;

constexpr float SOUND_SPEED_CM_PER_US = 0.0343f;

constexpr unsigned long ULTRASONIC_TIMEOUT_US = 40000;

// ==========================================================
// Limites de risco - Umidade do solo
// ==========================================================

// <= 50%        → Baixo
// > 50% até 70% → Médio
// > 70% até 85% → Alto
// > 85%         → Crítico

constexpr float SOIL_RISK_MEDIUM_THRESHOLD = 50.0f;
constexpr float SOIL_RISK_HIGH_THRESHOLD = 70.0f;
constexpr float SOIL_RISK_CRITICAL_THRESHOLD = 85.0f;

// ==========================================================
// Limites de risco - Inclinação
// ==========================================================

// <= 5°         → Baixo
// > 5° até 10°  → Médio
// > 10° até 15° → Alto
// > 15°         → Crítico

constexpr float INCLINATION_RISK_MEDIUM_THRESHOLD = 5.0f;
constexpr float INCLINATION_RISK_HIGH_THRESHOLD = 10.0f;
constexpr float INCLINATION_RISK_CRITICAL_THRESHOLD = 15.0f;

// ==========================================================
// Limites de risco - Distância do corpo d'água
// ==========================================================

// > 100 m         → Baixo
// 50 até 100 m    → Médio
// 20 até < 50 m   → Alto
// < 20 m          → Crítico

constexpr float WATER_RISK_CRITICAL_DISTANCE_M = 20.0f;
constexpr float WATER_RISK_HIGH_DISTANCE_M = 50.0f;
constexpr float WATER_RISK_MEDIUM_DISTANCE_M = 100.0f;