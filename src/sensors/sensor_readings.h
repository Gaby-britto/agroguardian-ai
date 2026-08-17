#pragma once

struct SensorReadings {
    float soilMoisture;
    float pitch;
    float roll;
    float proximityDistance;
};

void initializeSensors();

SensorReadings readSensors();

void printSensorReadings(const SensorReadings& readings);