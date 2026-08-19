#pragma once

struct SensorReadings {
    float soilMoisture;
    float pitch;
    float roll;
    float waterDistance;
};

void initializeSensors();

SensorReadings readSensors();