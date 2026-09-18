# ── Imports ──────────────────────────────────────────────────────
import random
import json
import time
from datetime import datetime, timezone
from pathlib import Path

# ── Konfiguration ─────────────────────────────────────────────────
LOG_FILE = Path('logs/app.log')
INTERVAL_SEKUNDEN = 2

# ── Testdaten ─────────────────────────────────────────────────────
BENUTZERNAMEN = [
    'admin', 'root', 'user1', 'testuser',
    'administrator', 'guest', 'service_account',
]
IP_ADRESSEN = [
    '203.0.113.42', '198.51.100.7', '192.0.2.188',
    '185.220.101.5', '45.142.212.100', '192.168.1.100',
    '10.0.0.55', '172.16.0.23',
]
HOSTNAMEN = [
    'webserver-01', 'db-server-02', 'mail-server',
    'vpn-gateway', 'fileserver-01',
]
EREIGNISTYPEN = [
    ('failed_login', 'high', 0.50),
    ('successful_login', 'low', 0.20),
    ('port_scan', 'high', 0.10),
    ('sudo_command', 'medium', 0.10),
    ('file_access', 'low', 0.10),
]

# ── Ereignistyp wählen ────────────────────────────────────────────
def ereignis_wählen():
    typen = [e[0] for e in EREIGNISTYPEN]
    gewichte = [e[2] for e in EREIGNISTYPEN]
    index = random.choices(range(len(typen)), weights=gewichte)[0]
    return EREIGNISTYPEN[index]

# ── Nachricht erstellen ───────────────────────────────────────────
def nachricht_erstellen(ereignis, benutzer, ip):
    nachrichten = {
        'failed_login': f'Failed login for {benutzer} from {ip}',
        'successful_login': f'Successful login for {benutzer} from {ip}',
        'port_scan': f'Port scan detected from {ip}',
        'sudo_command': f'Sudo command executed by {benutzer}',
        'file_access': f'Sensitive file accessed by {benutzer}',
    }
    return nachrichten.get(ereignis, 'Unknown event')

# ── Log-Eintrag erzeugen ──────────────────────────────────────────
def log_erzeugen():
    ereignis, schwere, _ = ereignis_wählen()
    benutzer = random.choice(BENUTZERNAMEN)
    ip = random.choice(IP_ADRESSEN)
    host = random.choice(HOSTNAMEN)
    return {
        '@timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'event_type': ereignis,
        'source_ip': ip,
        'username': benutzer,
        'hostname': host,
        'severity': schwere,
        'message': nachricht_erstellen(ereignis, benutzer, ip),
    }

# ── In Datei schreiben ────────────────────────────────────────────
def log_schreiben(eintrag):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(eintrag, ensure_ascii=False) + '\n')

# ── Hauptprogramm ─────────────────────────────────────────────────
def main():
    print(f'Log-Generator gestartet. Schreibe nach: {LOG_FILE}')
    print('Beenden mit Strg+C')
    print('-' * 50)
    zähler = 0
    while True:
        eintrag = log_erzeugen()
        log_schreiben(eintrag)
        zähler += 1
        print(f'[{zähler:04d}] {eintrag["@timestamp"]} | '
              f'{eintrag["event_type"]:20s} | '
              f'{eintrag["source_ip"]:15s} | '
              f'{eintrag["username"]}')
        time.sleep(INTERVAL_SEKUNDEN)

if __name__ == '__main__':
    main()