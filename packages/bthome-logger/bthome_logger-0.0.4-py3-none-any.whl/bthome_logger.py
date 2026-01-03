#!/usr/bin/env python3
"""
BThome Logger - Python Edition
Scannt nach BLE-Geräten und zeigt BThome v2 Advertisements an
"""

import asyncio
import struct
from datetime import datetime

from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData


# ANSI Farbcodes für schöne Terminal-Ausgabe
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"


# BThome v2 Object IDs mit Faktoren und Einheiten
BTHOME_OBJECTS = {
    0x00: {"name": "Packet ID", "factor": 1, "unit": "", "size": 1},
    0x01: {"name": "Batterie", "factor": 1, "unit": "%", "size": 1},
    0x02: {
        "name": "Temperatur",
        "factor": 0.01,
        "unit": "°C",
        "signed": True,
        "size": 2,
    },
    0x03: {"name": "Luftfeuchtigkeit", "factor": 0.01, "unit": "%", "size": 2},
    0x04: {"name": "Luftdruck", "factor": 0.01, "unit": "hPa", "size": 3},
    0x05: {"name": "Beleuchtung", "factor": 0.01, "unit": "lux", "size": 3},
    0x06: {"name": "Masse", "factor": 0.01, "unit": "kg", "signed": True, "size": 2},
    0x07: {
        "name": "Masse (lbs)",
        "factor": 0.01,
        "unit": "lbs",
        "signed": True,
        "size": 2,
    },
    0x08: {"name": "Taupunkt", "factor": 0.01, "unit": "°C", "signed": True, "size": 2},
    0x09: {"name": "Anzahl", "factor": 1, "unit": "", "size": 1},
    0x0A: {"name": "Energie", "factor": 0.001, "unit": "kWh", "size": 3},
    0x0B: {"name": "Leistung", "factor": 0.01, "unit": "W", "size": 3},
    0x0C: {"name": "Spannung", "factor": 0.001, "unit": "V", "size": 2},
    0x0D: {"name": "PM2.5", "factor": 1, "unit": "µg/m³", "size": 2},
    0x0E: {"name": "PM10", "factor": 1, "unit": "µg/m³", "size": 2},
    0x0F: {"name": "Boolean", "factor": 1, "unit": "", "size": 1},
    0x10: {"name": "Leistung (On)", "factor": 1, "unit": "", "size": 1},
    0x11: {"name": "Öffnung", "factor": 1, "unit": "", "size": 1},
    0x12: {"name": "CO2", "factor": 1, "unit": "ppm", "size": 2},
    0x13: {"name": "TVOC", "factor": 1, "unit": "µg/m³", "size": 2},
    0x14: {"name": "Feuchte", "factor": 0.01, "unit": "%", "size": 2},
}

# BThome Company ID
BTHOME_COMPANY_ID = 0xFCD2

# Filter für Geräte-Namen (nur MAKE-Geräte)
DEVICE_NAME_PREFIX = "MAKE"


def parse_bthome_packet(data: bytes) -> dict:
    """
    Parst ein BThome v2 Paket und gibt die dekodierten Werte zurück

    Args:
        data: Raw Manufacturer Data ohne Company ID

    Returns:
        Dictionary mit Device Info und dekodierten Werten
    """
    if len(data) < 1:
        return None

    result = {
        "device_info": data[0],
        "encrypted": bool(data[0] & 0x01),
        "version": "v2",
        "values": [],
    }

    index = 1

    # Objects dekodieren
    while index < len(data):
        object_id = data[index]
        index += 1

        if object_id not in BTHOME_OBJECTS:
            # Unbekanntes Object ID - abbrechen
            result["values"].append(
                {
                    "name": f"Unbekannt (0x{object_id:02X})",
                    "raw_value": None,
                    "value": None,
                    "unit": "",
                }
            )
            break

        obj_def = BTHOME_OBJECTS[object_id]
        size = obj_def["size"]

        if index + size > len(data):
            # Nicht genug Daten
            break

        # Wert auslesen
        raw_bytes = data[index : index + size]
        index += size

        # Wert dekodieren (Little Endian)
        if size == 1:
            raw_value = raw_bytes[0]
        elif size == 2:
            raw_value = struct.unpack("<H", raw_bytes)[0]
            # Signed?
            if obj_def.get("signed", False) and raw_value >= 0x8000:
                raw_value = raw_value - 0x10000
        elif size == 3:
            # 3 Bytes zu int (Little Endian)
            raw_value = raw_bytes[0] | (raw_bytes[1] << 8) | (raw_bytes[2] << 16)
            if obj_def.get("signed", False) and raw_value >= 0x800000:
                raw_value = raw_value - 0x1000000
        else:
            raw_value = 0

        # Faktor anwenden
        value = raw_value * obj_def["factor"]

        result["values"].append(
            {
                "name": obj_def["name"],
                "raw_value": raw_value,
                "value": value,
                "unit": obj_def["unit"],
            }
        )

    return result


def format_timestamp() -> str:
    """Gibt einen formatierten Zeitstempel zurück"""
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def print_header():
    """Druckt den Programm-Header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}🔵 BThome Logger - Python Edition{Colors.RESET}")
    print(f"{Colors.CYAN}Scannt nach BLE-Geräten mit BThome v2 Protocol{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")
    print(
        f"{Colors.YELLOW}Filter: Geräte mit '{DEVICE_NAME_PREFIX}' im Namen{Colors.RESET}"
    )
    print(f"{Colors.GRAY}Drücke Ctrl+C zum Beenden{Colors.RESET}\n")


def print_separator():
    """Druckt eine Trennlinie"""
    print(f"{Colors.GRAY}{'-'*70}{Colors.RESET}")


def advertisement_callback(device: BLEDevice, advertisement_data: AdvertisementData):
    """
    Callback-Funktion für empfangene Advertisements

    Args:
        device: BLE Device
        advertisement_data: Advertisement Data
    """
    # Filter: Nur Geräte mit "MAKE" im Namen
    if not device.name or not device.name.startswith(DEVICE_NAME_PREFIX):
        return

    # Prüfe auf Manufacturer Data
    if not advertisement_data.manufacturer_data:
        return

    # Suche nach BThome Company ID
    if BTHOME_COMPANY_ID not in advertisement_data.manufacturer_data:
        # Zeige andere Manufacturer Data
        for company_id, data in advertisement_data.manufacturer_data.items():
            hex_data = " ".join(f"{b:02x}" for b in data)
            print(
                f"{Colors.GRAY}[{format_timestamp()}]{Colors.RESET} "
                f"{Colors.BLUE}{device.name}{Colors.RESET} "
                f"({Colors.GRAY}{device.address}{Colors.RESET}) "
                f"| Company ID: 0x{company_id:04X} | Data: {hex_data} | "
                f"RSSI: {advertisement_data.rssi} dBm"
            )
        return

    # BThome-Daten gefunden!
    raw_data = advertisement_data.manufacturer_data[BTHOME_COMPANY_ID]
    hex_data = " ".join(f"{b:02x}" for b in raw_data)

    # Header mit Gerätename und Zeitstempel
    print_separator()
    print(
        f"{Colors.GRAY}[{format_timestamp()}]{Colors.RESET} "
        f"{Colors.BOLD}{Colors.GREEN}📱 {device.name}{Colors.RESET} "
        f"({Colors.GRAY}{device.address}{Colors.RESET})"
    )

    # RSSI
    if advertisement_data.rssi > -70:
        rssi_color = Colors.GREEN
    elif advertisement_data.rssi > -85:
        rssi_color = Colors.YELLOW
    else:
        rssi_color = Colors.RED

    rssi_text = f"{rssi_color}{advertisement_data.rssi} dBm{Colors.RESET}"
    print(f"  {Colors.GRAY}RSSI:{Colors.RESET} {rssi_text}")

    # Raw Data
    print(f"  {Colors.GRAY}Raw:{Colors.RESET} {Colors.CYAN}{hex_data}{Colors.RESET}")

    # BThome-Paket parsen
    parsed = parse_bthome_packet(raw_data)

    if parsed:
        # Device Info
        encrypted_str = (
            f"{Colors.RED}verschlüsselt{Colors.RESET}"
            if parsed["encrypted"]
            else f"{Colors.GREEN}unverschlüsselt{Colors.RESET}"
        )
        print(
            f"  {Colors.GRAY}BThome:{Colors.RESET} {parsed['version']} ({encrypted_str})"
        )

        # Dekodierte Werte
        if parsed["values"]:
            print(f"  {Colors.GRAY}Werte:{Colors.RESET}")
            for val in parsed["values"]:
                if val["unit"]:
                    value_str = f"{val['value']:.2f} {val['unit']}"
                else:
                    value_str = f"{val['value']}"

                print(
                    f"    {Colors.BOLD}{Colors.MAGENTA}• {val['name']}{Colors.RESET}: "
                    f"{Colors.YELLOW}{value_str}{Colors.RESET}"
                )
        else:
            print(f"    {Colors.GRAY}(Keine dekodierten Werte){Colors.RESET}")
    else:
        print(f"  {Colors.RED}Fehler beim Parsen des BThome-Pakets{Colors.RESET}")

    print()  # Leerzeile


async def scan_forever():
    """Scannt kontinuierlich nach BLE-Geräten"""
    print_header()
    print(f"{Colors.GREEN}✓ Scanner gestartet...{Colors.RESET}\n")

    scanner = BleakScanner(detection_callback=advertisement_callback)

    try:
        await scanner.start()

        # Scanne für immer (oder bis Ctrl+C)
        while True:
            await asyncio.sleep(1.0)

    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Scanner wird gestoppt...{Colors.RESET}")
    finally:
        await scanner.stop()
        print(f"{Colors.GREEN}✓ Scanner gestoppt{Colors.RESET}\n")


def main():
    """Hauptfunktion"""
    try:
        asyncio.run(scan_forever())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
