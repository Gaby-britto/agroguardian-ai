#pragma once

// ==========================================================
// Comunicação Serial
// ==========================================================

constexpr unsigned long SERIAL_BAUD_RATE = 115200;

// Intervalo entre leituras dos sensores
constexpr unsigned long SENSOR_READ_INTERVAL_MS = 2000;

// ==========================================================
// Umidade do solo
// ==========================================================

// Valores utilizados para normalizar a leitura do potenciômetro.
//
// No Wokwi:
// ADC mínimo → solo mais seco
// ADC máximo → solo mais úmido.
//
// Esses valores poderão ser ajustados após os primeiros testes.

constexpr int SOIL_ADC_DRY = 0;
constexpr int SOIL_ADC_WET = 4095;

constexpr float SOIL_MOISTURE_MIN_PERCENT = 0.0f;
constexpr float SOIL_MOISTURE_MAX_PERCENT = 100.0f;

// ==========================================================
// HC-SR04 → LiDAR simulado
// ==========================================================

// Faixa aproximada utilizada pelo HC-SR04 no Wokwi.
// Essa distância NÃO representa diretamente a distância real da água.
//
// Ela será convertida para uma escala simulada de LiDAR.

constexpr float ULTRASONIC_MIN_DISTANCE_CM = 2.0f;
constexpr float ULTRASONIC_MAX_DISTANCE_CM = 400.0f;

// Faixa que queremos representar para a distância do
// espelho d'água na aplicação.
//
// Exemplo:
// 2 cm no Wokwi   → 0 m
// 400 cm no Wokwi → 1000 m

constexpr float LIDAR_SIMULATED_MIN_DISTANCE_M = 0.0f;
constexpr float LIDAR_SIMULATED_MAX_DISTANCE_M = 1000.0f;

// Velocidade aproximada do som em cm/us
constexpr float SOUND_SPEED_CM_PER_US = 0.0343f;

// Timeout para leitura do Echo
constexpr unsigned long ULTRASONIC_TIMEOUT_US = 30000;