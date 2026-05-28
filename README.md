# Projekt FOTOPAST - Detekce pohybu

Tento projekt se zabývá návrhem a realizací jednoduché IoT fotopasti pro monitorování pohybu lesní zvěře na hranici lesní a obydlené oblasti.

## Cíle

Cílem projektu je naprogramovat a zprovoznit jednoduché zařízení, které bude schopné:

- simulovat detekci pohybu pomocí tlačítka
- uložit záznam o pořízení fotografie na SD kartu
- načíst předem uložený obrázek z SD karty
- odeslat informace o obrázku na vzdálený server
- odeslat obrázek na vzdálený server
- periodicky odesílat telemetrické informace
- kontrolovat rádiové podmínky před přenosem dat
- dlouhého fungování díky vhodně implementovaných módů pro úsporu energie

## Použité technologie

Zařízení využívá mikrokontrolér Raspberry pi pico jako hlavní řídicí jednotku a komunikační modul BG77 pro připojení do mobilní sítě pomocí technologie LTE Cat-M. Pro přenos dat je použit transportní protokol UDP. Nad UDP je vytvořen jednoduchý aplikační protokol, který využívá JSON zprávy pro přenos telemetrie a řídicích informací a HEX kódování pro přenos obrazových dat.

### Raspberry pi pico

Mezi hlavní funkce Raspberry pi pico patří:

- inicializace systému
- obsluha tlačítka
- práce se soubory na SD kartě
- vytvoření telemetrických a informačních zpráv JSON
- čtení obrázku po částech
- převod obrazových dat do HEX formátu
- odesílání dat přes BG77
- řízení hlavní smyčky programu

### BG77

Mezi hlavní funkce BG77 patří:

- kontrola SIM karty
- registrace do sítě operátora
- otevření UDP socketu
- odesílání JSON zpráv
- odesílání obrázku
- příjem potvrzení ze serveru

### SD karta

SD karta slouží jako uložiště pro záznamy o pořízení fotografie a pro samotné úkládání pořízených fotek. V tomto projektu se fotky neukládají na SD kartu, ale jsou na SD kartu nahrány předem. Výhodou použití SD karty je, že se fotky nemusí posílat hned, když nejsou dostatečně dobré rádiové podmínky pro spolehlivý přenos, což by mohlo způsobit velkou ztrátovost.

### Tlačítko

Tlačítko v projektu nahrazuje senzor a slouží k simulaci pořízení fotografie a záznamu.

### LTE Cat-M

Pro přenos dat byla zvolena technologie LTE Cat-M. Jedná se technologii vhodnou pro zařízení s nižší spotřebou energie, která potřebují komunikovat v místech bez dostupné Wi-Fi sítě.

Technologie spadá do licenčních technologií, kde nemusíme u přenosu řešit například duty cycle nebo maximální velikost zprávy. Z důvodu posílání telemetrie každých 30 minut a zasílání informací o obrázku a obrázku samotného by zařízení nesplňovalo duty cycle, který býva zpravidla 1% nebo méně. Z pohledu maximální velikosti zprávy by zařízení nemohlo pracovat s bezlicenční technologií. Zařízení posílá kousky obrázku po 512B a po zakódování do HEX po 1024B.

Technologie je vhodná pro zařízení umístěných v odlehlejších částech. Pro tento projekt se předpokládá že zařízení bude umístěno na hranici lesní a obydlené oblasti, kde nelze předpokládat například připojení na síť Wi-Fi. Díky svému maximálnímu povolenému vysílacímu výkonu a možnosti pracovat v nižších frekvencích (pod 1GHz) může technologie poměrně spolehlivě pracovat i v odlehlých místech, kde nemusí být vhodné rádiové podmínky.

Technologie NB-IoT a LTE Cat-M jsou pro tento projekt a účel dost podobné. LTE Cat-M oproti NB-Iot nabízí větší přenosovou rychlost a nižší latenci, zatímco NB-Iot dokáže přenášet data v trochu horších podmínkách s větší latencí. Z důvodu přenášení někdy i velkých obrázku byla zvolena technologie LTE Cat-M pro rychlejší posílání jednotlivých částí obrázku.

### UDP

Jako transportní protokol byl zvolen protokol UDP. Hlavními důvody jsou například:

- jednoduchá implementace
- nízká režie
- rychlé odesílání dat
- bez nutnosti navazovat spojení
- stále s možností vlastního potvrzování

Protokol UDP je jednoduchý protokol, který nevyžaduje navazování spojení, ale nezajišťuje potvrzení doručených dat. Potvrzování dat v tomto projektu bylo zajištěno přes vlastní server, který posílá po každé části obrázku zprávu "OK", na kterou zařízení čeká a neposílá další části obrázku dokud nepříjde potvrzení. Pokud ji do časového limitu neobdrží, tak bude zařízení posílat část obrázku znovu. Protokol TCP by pro projekt nebyl vhodný z důvodu velké režie, nutnosti navazování spojení, pomalejšímu posílání dat a těžší implementaci. Výhodou TCP by mohlo být již integrované potvrzování zprávy, ale nevýhody TCP protokolu by ve výsledku převažovaly výhody.

### Aplikační protokol

Nad protokolem UDP byl vytvořen jednoduchý aplikační protokol, který definuje jakým způsobem budou data posílána na server.
Pro telemetrii se posílá zpráva ve formátu JSON, která obsahuje (RSSI a RSRP).
Pro informaci o obrázku, která se posílá před samotným posíláním částí obrázků, se používá zpráva ve formátu JSON, která obsahuje (type, id, size a encoding).
Pro samotné kousky obrázku se posílají data zakódovaná ve formátu hex, které jsou dále ještě zakódovaná do formátu ASCII.

Důvodem použití formátu JSON je jednoduchá implementace, přehlednost zpráv, možnost a jednoduchost rozšíření zpráv například pro více zařízení, snadné zpracování a výbrání dat na straně serveru, což zahrnuje rozlišení telemetrie a informaci o obrázku. 

Důvodem posílání částí obrázku pomocí zakódovaných dat do HEX formátnu je jednodušší posílání, menší riziko chyb oproti posílání dat v binární podobě, znadné ladění a jednoduchý převod zpět na čistá data. Nevýhodou je ale zdvojnásobení objemu dat na dvojnásobek.

## Základní princip přenosu obrázku

1) při stisku tlačítka se uloží záznam o pořízení na SD kartu.
2) zkontrolují se rádiové podmínky
3) zařízení vybere náhodný obrázek a odešle JSON zprávu typu image_info
4) po přijetí zprávy typu image_info se server přepne na příjem obrázku
5) zařízení začne posílat zakódované části obrázku na server a po každé části čeká na zprávu "OK" od serveru než pošle další část
6) server příjme část obrázku a dekóduje ji.
7) server uloží část obrázku do složky images a pošle zprávu "OK"
8) zařízení pošle další část obrázku
9) po přijetí celého obrázku se zastaví na serveru přijímání obrázku

## Princip fungování serveru

Server běži na adrese 147.229.148.105 a na portu 7001. Server je nastaven tak, aby naslouchal od všech příchozých adres.

V první části serveru se inicialuzují proměnné, které slouží ke správnému fungování serveru. První funkce serveru (run_server) zajišťuje nastavení stavových proměnných a vytvoření UDP socketu. 
Funkce reset_server_state slouží k vrácení a restartování serveru v případě chyby nebo v případě, že se přeruší posílání obrázku.

Dále následuje hlavní smyčka serveru, ve které server pracuje ve dvou hlavních režimech. V prvním režimu server přijímá obrázek, který dekóduje a uloží do složky images a pošle odesílateli zprávu "OK".
V druhém režimu server čeká na běžnou zprávu, podle které určí, zda se jedná o telemetrii nebo o informaci o obrázku. Tuto informaci vyčte z JSON zprávy z hodnoty type. 

V případě telemetrie server jen telemetrii příjme a neposílá nic zpět. 
V případě informace o obrázku server přepíše stavovou proměnnou receiving_image a začne přijímat části obrázku. 
Na konci kódu je server ošetřen a je nastaven na automatický restart při chybě pomocí funkce reset_server_state.

## Stavový automat

## Struktura kódu

- main.py
- bg77.py
- uart_if.py
- file_manager.py
- sdcard.py
- server.py
- README.md

### main.py
Hlavní program zařízení. Zajišťuje inicializaci systému, obsluhu přerušení, hlavní smyčku programu a volání funkcí pro odesílání telemetrie a obrázků.

### BG77.py
Soubor pro práci s komunikačním modulem BG77. Obsahuje funkce pro odesílání AT příkazů, kontrolu SIM karty, registraci do sítě, aktivaci datového připojení a odesílání dat.

### uart_if.py
Komunikační vrstva pro UART. Zajišťuje inicializaci UART rozhraní, odesílání textových příkazů a čtení odpovědí z modulu BG77.

### file_manager.py
Soubor pro práci se soubory. Obsluhuje zásobník záznamů

### sdcard.py
Knihovna nebo modul pro práci s SD kartou v MicroPythonu.

### server.py
Python UDP server pro příjem telemetrie a obrázků.




































