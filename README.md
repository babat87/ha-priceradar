# PriceRadar for Home Assistant

[![HACS Default](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/user/ha-priceradar.svg)](https://github.com/user/ha-priceradar/releases)

**PriceRadar** ist eine Home Assistant Integration, die lokale Supermarkt-Angebote aus [Marktguru](https://www.marktguru.de) abruft und als übersichtliches Dashboard anzeigt. Für jedes konfigurierte Produkt werden die günstigsten aktuellen Angebote in deiner Region gefunden – inklusive Preis, Geschäft und Gültigkeitsdauer.

## Features

- 🔍 Sucht automatisch nach Angeboten für beliebige Produkte
- 📍 Lokale Suche per Postleitzahl
- 💰 Zeigt Preise, Rabatte und günstigstes Geschäft
- 📅 Gültigkeitsdaten mit Ablaufwarnung
- 🗂️ Sortierbar nach Preis, Rabatt oder Gültigkeit
- 🔎 Filterfunktion im Dashboard
- ⚙️ Vollständig über die HACS & UI konfigurierbar

## Installation via HACS

1. Öffne **HACS** in Home Assistant
2. Gehe zu **Integrationen** → Klicke auf das **+** Symbol
3. Suche nach **PriceRadar**
4. Klicke auf **Herunterladen**
5. Starte Home Assistant neu

### Manuelle HACS-Installation (Custom Repository)

1. HACS → Integrationen → ⋮ Menü → **Custom repositories**
2. URL: `https://github.com/user/ha-priceradar`
3. Kategorie: **Integration**
4. Klicke **Add** → dann wie oben weiter

## Einrichtung

1. Gehe zu **Einstellungen** → **Geräte & Dienste** → **Integration hinzufügen**
2. Suche nach **PriceRadar**
3. Gib deine **Postleitzahl** (5-stellig) ein
4. Gib **Produkte** kommagetrennt ein, z.B.: `Milch, Butter, Eier, Brot, Käse`
5. Optional: Maximale Angebote pro Produkt & Aktualisierungsintervall anpassen

## Dashboard-Karte einrichten

Nach der Integration musst du die Lovelace-Ressource einmalig hinzufügen:

### Schritt 1: Lovelace-Ressource hinzufügen

Gehe zu **Einstellungen** → **Dashboards** → ⋮ Menü → **Ressourcen** → **Ressource hinzufügen**

- URL: `/priceradar/priceradar-card.js`
- Ressourcentyp: **JavaScript-Modul**

### Schritt 2: Karte zum Dashboard hinzufügen

Füge folgendes in die Lovelace YAML-Konfiguration ein:

```yaml
type: custom:priceradar-card
title: Lokale Angebote
show_images: true
columns: 3
entities:
  - sensor.priceradar_milch
  - sensor.priceradar_butter
  - sensor.priceradar_eier
  - sensor.priceradar_brot
```

Die Entity-Namen entsprechen dem Muster `sensor.priceradar_<produktname>` (Leerzeichen werden zu `_`).

## Karten-Konfiguration

| Option        | Typ     | Standard     | Beschreibung                      |
| ------------- | ------- | ------------ | --------------------------------- |
| `entities`    | Liste   | _Pflicht_    | HA Sensor-Entity-IDs der Produkte |
| `title`       | String  | `PriceRadar` | Kartentitel                       |
| `show_images` | Boolean | `true`       | Produktbilder anzeigen            |
| `columns`     | Zahl    | `3`          | Spaltenanzahl im Grid             |

## Sensoren

Für jedes konfigurierte Produkt wird ein Sensor erstellt:

| Attribut      | Beschreibung                       |
| ------------- | ---------------------------------- |
| `state`       | Bester aktueller Preis (€)         |
| `offers`      | Alle gefundenen Angebote als Liste |
| `best_price`  | Günstigster Preis                  |
| `best_store`  | Geschäft mit bestem Preis          |
| `valid_until` | Gültig bis (bestes Angebot)        |
| `offer_count` | Anzahl gefundener Angebote         |
| `postal_code` | Konfigurierte Postleitzahl         |

## Datenschutz

Diese Integration sendet Anfragen an die öffentliche Marktguru-API (`marktguru.de`). Es werden keine persönlichen Daten übertragen – lediglich Postleitzahl und Suchbegriff.

## Lizenz

MIT License
