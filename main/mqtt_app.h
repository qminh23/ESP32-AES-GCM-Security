#ifndef MQTT_APP_H
#define MQTT_APP_H
#include <stdbool.h>
#include <stdint.h>
#include "esp_err.h"

#if __has_include("mqtt_config.local.h")
#include "mqtt_config.local.h"
#endif

#ifndef MQTT_BROKER_URI
#define MQTT_BROKER_URI "mqtts://i9509b90.ala.asia-southeast1.emqxsl.com:8883"
#endif
#if !defined(MQTT_USERNAME) || !defined(MQTT_PASSWORD)
#error "Dien tai khoan MQTT trong main/mqtt_config.local.h (xem file .example)."
#endif

void mqtt_app_start(void);
void mqtt_app_publish_cycle(const char *json);
void mqtt_app_publish_command_ack(const char *command_id, int state,
                                  int64_t decrypt_us, int64_t execution_us, bool applied,
                                  bool aes_enabled);
// Được hardware_control.c gọi cho UNLOCKED và LOCKED.
void mqtt_app_publish_status(const char *status, const char *msg);

void mqtt_app_publish_telemetry(bool valid, float voltage, float current_ma, float power_w, esp_err_t error,
                                const char *sensor_stage, int bus_raw, int shunt_raw);
void mqtt_app_publish_decrypt_time(int64_t elapsed_us);

#endif
