# ── Imports ──────────────────────────────────────────────────────
import time
from datetime import datetime, timezone
from elasticsearch import Elasticsearch

# ── Konfiguration ─────────────────────────────────────────────────
ES_HOST = 'http://localhost:9200'
INDEX_PATTERN = 'security-logs-*'
ZEITFENSTER_MIN = 5       # Minuten zurückschauen
SCHWELLWERT = 5           # Max. Fehlversuche vor Alert
PRUEF_INTERVALL = 60      # Sekunden zwischen Prüfungen

# ── Elasticsearch-Abfrage ─────────────────────────────────────────
def brute_force_abfragen(es: Elasticsearch):
    von = f'now-{ZEITFENSTER_MIN}m'
    abfrage = {
        'size': 0,
        'query': {
            'bool': {
                'must': [
                    {'term': {'event_type': 'failed_login'}},
                    {'range': {'@timestamp': {'gte': von, 'lte': 'now'}}}
                ]
            }
        },
        'aggs': {
            'nach_ip': {
                'terms': {
                    'field': 'source_ip',
                    'size': 20,
                    'min_doc_count': SCHWELLWERT
                }
            }
        }
    }
    return es.search(index=INDEX_PATTERN, body=abfrage)

# ── Alert auslösen ────────────────────────────────────────────────
def alert_ausgeben(ip: str, anzahl: int):
    zeitstempel = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    print(f'\n{"="*60}')
    print(f'  !! BRUTE-FORCE ALERT !!')
    print(f'  Zeit:     {zeitstempel}')
    print(f'  Angreifer: {ip}')
    print(f'  Versuche: {anzahl} in {ZEITFENSTER_MIN} Minuten')
    print(f'  Aktion:   IP {ip} blockieren!')
    print(f'{"="*60}\n')

# ── Hauptschleife ─────────────────────────────────────────────────
def main():
    es = Elasticsearch(ES_HOST)
    print(f'Alert-Engine gestartet.')
    print(f'Schwellwert: {SCHWELLWERT} Versuche in {ZEITFENSTER_MIN} Min.')
    print(f'Prüfintervall: alle {PRUEF_INTERVALL} Sekunden')
    print('Beenden mit Strg+C\n')
    while True:
        try:
            ergebnis = brute_force_abfragen(es)
            buckets = ergebnis['aggregations']['nach_ip']['buckets']
            zeitpunkt = datetime.now(timezone.utc).strftime('%H:%M:%S')
            if buckets:
                for bucket in buckets:
                    alert_ausgeben(bucket['key'], bucket['doc_count'])
            else:
                print(f'[{zeitpunkt}] Kein Brute-Force erkannt.')
        except Exception as fehler:
            print(f'Fehler bei Elasticsearch-Abfrage: {fehler}')
        time.sleep(PRUEF_INTERVALL)

if __name__ == '__main__':
    main()