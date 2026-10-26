#ifndef WIFI_APP_H
#define WIFI_APP_H

/* Optional local override, ignored by git. Copy wifi_credentials.local.h.example. */
#if __has_include("wifi_credentials.local.h")
#include "wifi_credentials.local.h"
#endif
#define MAXIMUM_RETRY      5

void wifi_init_sta(void);

#if !defined(ESP_WIFI_SSID) || !defined(ESP_WIFI_PASS)
#error "Dien Wi-Fi trong main/wifi_credentials.local.h (xem file .example)."
#endif

#endif
