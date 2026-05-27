# Projekt FOTOPAST - Detekce pohybu

## Základní popis

Tento projekt se zabývá návrhem a realizací jednoduché IoT fotopasti pro monitorování pohybu lesní zvěře na hranici lesní a obydlené oblasti. Detekce pohybu je v prototypu simulována pomocí tlačítka. Po aktivaci zařízení vytvoří záznam o pořízení snímku, uloží jej na SD kartu a následně odešle informace a data obrázku na vzdálený server.

Zařízení využívá mikrokontrolér ESP32 jako hlavní řídicí jednotku a komunikační modul BG77 pro připojení do mobilní sítě pomocí technologie LTE Cat-M. Pro přenos dat je použit transportní protokol UDP. Nad UDP je vytvořen jednoduchý aplikační protokol, který využívá JSON zprávy pro přenos telemetrie a řídicích informací a HEX kódování pro přenos obrazových dat.
