#include <stdio.h>
#include "ina219_app.h"
#include "nvs_flash.h"
#include "wifi_app.h"
#include "mqtt_app.h" 
#include "crypto_app.h"
#include "hardware_control.h"

void app_main(void) {
    hardware_init();
    ina219_app_start();

    test_crypto_engine();

    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
      ESP_ERROR_CHECK(nvs_flash_erase());
      ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    wifi_init_sta();
}
