#include "sensor_readings.h"
#include "pins.h"
#include "../constants.h"

#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <math.h>

// ==========================================================
// MPU6050
// ==========================================================

Adafruit_MPU6050 mpu;

// ==========================================================
// Funções auxiliares
// ==========================================================

float mapFloat(
    float value,
    float inputMin,
    float inputMax,
    float outputMin,
    float outputMax
) {
    return (
        (value - inputMin)
        * (outputMax - outputMin)
        / (inputMax - inputMin)
    ) + outputMin;
}

// ==========================================================
// Umidade do solo
// ==========================================================

float readSoilMoisture() {

    int rawValue = analogRead(SOIL_MOISTURE_PIN);

    float moisture = mapFloat(
        rawValue,
        SOIL_ADC_DRY,
        SOIL_ADC_WET,
        SOIL_MOISTURE_MIN_PERCENT,
        SOIL_MOISTURE_MAX_PERCENT
    );

    moisture = constrain(
        moisture,
        SOIL_MOISTURE_MIN_PERCENT,
        SOIL_MOISTURE_MAX_PERCENT
    );

    return moisture;
}

// ==========================================================
// HC-SR04
// Simulação do LiDAR
// ==========================================================

float readWaterDistance() {

    digitalWrite(
        ULTRASONIC_TRIG_PIN,
        LOW
    );

    delayMicroseconds(2);

    digitalWrite(
        ULTRASONIC_TRIG_PIN,
        HIGH
    );

    delayMicroseconds(10);

    digitalWrite(
        ULTRASONIC_TRIG_PIN,
        LOW
    );

    unsigned long duration = pulseIn(
        ULTRASONIC_ECHO_PIN,
        HIGH,
        ULTRASONIC_TIMEOUT_US
    );

    if (duration == 0) {
        return LIDAR_SIMULATED_MAX_DISTANCE_M;
    }

    float distanceCm =
        duration
        * SOUND_SPEED_CM_PER_US
        / 2.0f;

    distanceCm = constrain(
        distanceCm,
        ULTRASONIC_MIN_DISTANCE_CM,
        ULTRASONIC_MAX_DISTANCE_CM
    );

    float waterDistance = mapFloat(
        distanceCm,
        ULTRASONIC_MIN_DISTANCE_CM,
        ULTRASONIC_MAX_DISTANCE_CM,
        LIDAR_SIMULATED_MIN_DISTANCE_M,
        LIDAR_SIMULATED_MAX_DISTANCE_M
    );

    return waterDistance;
}

// ==========================================================
// MPU6050
// ==========================================================

void readInclination(
    float& pitch,
    float& roll
) {

    sensors_event_t acceleration;
    sensors_event_t gyro;
    sensors_event_t temperature;

    mpu.getEvent(
        &acceleration,
        &gyro,
        &temperature
    );

    float ax = acceleration.acceleration.x;
    float ay = acceleration.acceleration.y;
    float az = acceleration.acceleration.z;

    // Pitch
    pitch = atan2(
        -ax,
        sqrt(
            (ay * ay) +
            (az * az)
        )
    ) * 180.0f / PI;

    // Roll
    roll = atan2(
        ay,
        az
    ) * 180.0f / PI;
}

// ==========================================================
// Inicialização
// ==========================================================

void initializeSensors() {

    // HC-SR04
    pinMode(
        ULTRASONIC_TRIG_PIN,
        OUTPUT
    );

    pinMode(
        ULTRASONIC_ECHO_PIN,
        INPUT
    );

    // Sensor de umidade
    pinMode(
        SOIL_MOISTURE_PIN,
        INPUT
    );

    // I2C
    Wire.begin(
        MPU6050_SDA_PIN,
        MPU6050_SCL_PIN
    );

    // MPU6050
    if (!mpu.begin()) {
        Serial.println(
            "error=mpu6050_not_found;"
        );

        while (true) {
            delay(1000);
        }
    }

    mpu.setAccelerometerRange(
        MPU6050_RANGE_8_G
    );

    mpu.setGyroRange(
        MPU6050_RANGE_500_DEG
    );

    mpu.setFilterBandwidth(
        MPU6050_BAND_21_HZ
    );
}

// ==========================================================
// Leitura consolidada
// ==========================================================

SensorReadings readSensors() {

    SensorReadings readings;

    readings.soilMoisture =
        readSoilMoisture();

    readInclination(
        readings.pitch,
        readings.roll
    );

    readings.waterDistance =
        readWaterDistance();

    return readings;
}