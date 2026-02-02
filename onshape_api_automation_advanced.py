#!/usr/bin/env python3
"""
Onshape API Automation Script (mit JSON-Config Support)
Ändert Variablen in Onshape und exportiert CAD/STEP-Dateien in einer Schleife
"""

import requests
import json
import time
import os
import argparse
from typing import Optional, Dict, Any
from pathlib import Path


class OnshapeAPI:
    """Wrapper für die Onshape REST API"""
    
    def __init__(self, access_key: str, secret_key: str, base_url: str = "https://cad.onshape.com"):
        """
        Initialisierung der Onshape API
        
        Args:
            access_key: Dein Onshape API Access Key
            secret_key: Dein Onshape API Secret Key
            base_url: Basis-URL (Standard: https://cad.onshape.com)
        """
        self.access_key = access_key
        self.secret_key = secret_key
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v6"
        
    def _get_auth(self):
        """Erstellt HTTP Basic Auth aus den API Keys"""
        return (self.access_key, self.secret_key)
    
    def update_variable(self, document_id: str, workspace_id: str, element_id: str, 
                       variable_name: str, new_value: float) -> bool:
        """
        Ändert den Wert einer Variable in einem Part Studio
        
        Args:
            document_id: Die Document ID (24 Zeichen)
            workspace_id: Die Workspace ID (24 Zeichen)
            element_id: Die Element ID des Part Studios
            variable_name: Name der zu ändernden Variable
            new_value: Neuer Wert für die Variable
            
        Returns:
            True wenn erfolgreich, False sonst
        """
        url = f"{self.api_base}/partstudios/d/{document_id}/w/{workspace_id}/e/{element_id}/variables"
        
        # Hole aktuelle Variablen
        response = requests.get(url, auth=self._get_auth())
        
        if response.status_code != 200:
            print(f"Fehler beim Abrufen der Variablen: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        variables = response.json()
        
        # Finde und ändere die gewünschte Variable
        updated = False
        for var in variables:
            if var.get('name') == variable_name:
                var['expression'] = str(new_value)
                updated = True
                break
        
        if not updated:
            print(f"Variable '{variable_name}' nicht gefunden!")
            print(f"Verfügbare Variablen: {[v.get('name') for v in variables]}")
            return False
        
        # Sende Update zurück
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, auth=self._get_auth(), 
                               headers=headers, json=variables)
        
        if response.status_code == 200:
            print(f"✓ Variable '{variable_name}' auf {new_value} gesetzt")
            return True
        else:
            print(f"Fehler beim Setzen der Variable: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    def export_step(self, document_id: str, workspace_id: str, element_id: str, 
                   output_path: str, part_ids: Optional[list] = None) -> bool:
        """
        Exportiert Teile als STEP-Datei
        
        Args:
            document_id: Die Document ID
            workspace_id: Die Workspace ID
            element_id: Die Element ID
            output_path: Pfad für die Output-Datei
            part_ids: Liste von Part IDs (None = alle Teile exportieren)
            
        Returns:
            True wenn erfolgreich, False sonst
        """
        url = f"{self.api_base}/partstudios/d/{document_id}/w/{workspace_id}/e/{element_id}/step"
        
        params = {}
        if part_ids:
            params['partIds'] = ','.join(part_ids)
        
        response = requests.get(url, auth=self._get_auth(), params=params)
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"✓ STEP-Datei exportiert: {output_path}")
            return True
        else:
            print(f"Fehler beim STEP-Export: {response.status_code}")
            return False
    
    def export_parasolid(self, document_id: str, workspace_id: str, element_id: str,
                        output_path: str, part_ids: Optional[list] = None) -> bool:
        """
        Exportiert Teile als Parasolid (X_T) Datei
        
        Args:
            document_id: Die Document ID
            workspace_id: Die Workspace ID
            element_id: Die Element ID
            output_path: Pfad für die Output-Datei
            part_ids: Liste von Part IDs (None = alle Teile exportieren)
            
        Returns:
            True wenn erfolgreich, False sonst
        """
        url = f"{self.api_base}/partstudios/d/{document_id}/w/{workspace_id}/e/{element_id}/parasolid"
        
        params = {}
        if part_ids:
            params['partIds'] = ','.join(part_ids)
        
        response = requests.get(url, auth=self._get_auth(), params=params)
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"✓ Parasolid-Datei exportiert: {output_path}")
            return True
        else:
            print(f"Fehler beim Parasolid-Export: {response.status_code}")
            return False
    
    def list_variables(self, document_id: str, workspace_id: str, element_id: str) -> list:
        """
        Listet alle Variablen in einem Part Studio auf
        
        Returns:
            Liste von Variable-Dictionaries
        """
        url = f"{self.api_base}/partstudios/d/{document_id}/w/{workspace_id}/e/{element_id}/variables"
        response = requests.get(url, auth=self._get_auth())
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Fehler beim Abrufen der Variablen: {response.status_code}")
            return []


def load_config(config_path: str) -> Dict[str, Any]:
    """Lädt Konfiguration aus JSON-Datei"""
    with open(config_path, 'r') as f:
        return json.load(f)


def run_automation(config: Dict[str, Any], list_vars_only: bool = False):
    """
    Führt die Automation aus
    
    Args:
        config: Konfigurations-Dictionary
        list_vars_only: Wenn True, nur Variablen auflisten
    """
    # Extrahiere Konfiguration
    api_config = config['api']
    doc_config = config['document']
    var_config = config['variable']
    export_config = config['export']
    timing_config = config['timing']
    
    # Initialisiere API
    api = OnshapeAPI(
        access_key=api_config['access_key'],
        secret_key=api_config['secret_key'],
        base_url=api_config.get('base_url', 'https://cad.onshape.com')
    )
    
    # Nur Variablen auflisten?
    if list_vars_only:
        print("\nVerfügbare Variablen im Part Studio:")
        print("=" * 60)
        variables = api.list_variables(
            document_id=doc_config['document_id'],
            workspace_id=doc_config['workspace_id'],
            element_id=doc_config['element_id']
        )
        for var in variables:
            print(f"  • {var.get('name')}: {var.get('expression')} {var.get('units', '')}")
        print("=" * 60)
        return
    
    # Erstelle Output-Ordner
    output_folder = export_config['output_folder']
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    # Berechne Anzahl der Iterationen
    values = []
    current = var_config['start_value']
    while current <= var_config['end_value']:
        values.append(current)
        current += var_config['step_size']
    
    print(f"\n{'='*60}")
    print(f"Starte Onshape API Automation")
    print(f"{'='*60}")
    print(f"Variable: {var_config['name']}")
    print(f"Werte: {var_config['start_value']} bis {var_config['end_value']} (Schritt: {var_config['step_size']})")
    print(f"Anzahl Iterationen: {len(values)}")
    print(f"{'='*60}\n")
    
    # Durchlaufe alle Werte
    for i, value in enumerate(values, 1):
        print(f"\n--- Iteration {i}/{len(values)}: {var_config['name']} = {value} ---")
        
        # 1. Variable ändern
        success = api.update_variable(
            document_id=doc_config['document_id'],
            workspace_id=doc_config['workspace_id'],
            element_id=doc_config['element_id'],
            variable_name=var_config['name'],
            new_value=value
        )
        
        if not success:
            print(f"⚠ Überspringe Export für Wert {value}")
            continue
        
        # Kurze Pause für Regenerierung
        time.sleep(1)
        
        # 2. Exportiere Dateien
        base_filename = f"{var_config['name']}_{value:g}"
        
        if export_config.get('export_step', True):
            step_path = os.path.join(output_folder, f"{base_filename}.step")
            api.export_step(
                document_id=doc_config['document_id'],
                workspace_id=doc_config['workspace_id'],
                element_id=doc_config['element_id'],
                output_path=step_path
            )
        
        if export_config.get('export_parasolid', False):
            parasolid_path = os.path.join(output_folder, f"{base_filename}.x_t")
            api.export_parasolid(
                document_id=doc_config['document_id'],
                workspace_id=doc_config['workspace_id'],
                element_id=doc_config['element_id'],
                output_path=parasolid_path
            )
        
        # Pause zwischen Iterationen
        if i < len(values):
            time.sleep(timing_config.get('delay_between_iterations', 2))
    
    print(f"\n{'='*60}")
    print(f"✓ Fertig! {len(values)} Iterationen abgeschlossen")
    print(f"Dateien gespeichert in: {os.path.abspath(output_folder)}")
    print(f"{'='*60}\n")


def main():
    """Hauptfunktion mit Argument-Parsing"""
    parser = argparse.ArgumentParser(
        description='Onshape API Automation - Variablen ändern und Dateien exportieren'
    )
    parser.add_argument(
        '-c', '--config',
        default='config.json',
        help='Pfad zur Konfigurationsdatei (Standard: config.json)'
    )
    parser.add_argument(
        '-l', '--list-variables',
        action='store_true',
        help='Nur verfügbare Variablen auflisten'
    )
    
    args = parser.parse_args()
    
    # Lade Konfiguration
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        print(f"Fehler: Konfigurationsdatei '{args.config}' nicht gefunden!")
        print("Tipp: Kopiere 'config.example.json' zu 'config.json' und passe die Werte an.")
        return
    except json.JSONDecodeError as e:
        print(f"Fehler beim Parsen der Konfigurationsdatei: {e}")
        return
    
    # Führe Automation aus
    run_automation(config, list_vars_only=args.list_variables)


if __name__ == "__main__":
    main()
