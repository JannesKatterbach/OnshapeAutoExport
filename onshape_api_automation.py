#!/usr/bin/env python3
"""
Onshape API Automation Script
Ändert Variablen in Onshape und exportiert CAD/STEP-Dateien in einer Schleife
"""

import requests
import json
import time
import os
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


def main():
    """
    Hauptfunktion - HIER KANNST DU ALLE EINSTELLUNGEN ANPASSEN
    """
    
    # ==================== KONFIGURATION ====================
    
    # API Zugangsdaten (Erstelle diese unter: https://cad.onshape.com/appstore/dev-portal)
    ACCESS_KEY = "DEIN_ACCESS_KEY_HIER"
    SECRET_KEY = "DEIN_SECRET_KEY_HIER"
    
    # Document-Informationen (aus der Onshape URL)
    DOCUMENT_ID = "deine_document_id"      # 24 Zeichen nach /documents/
    WORKSPACE_ID = "deine_workspace_id"    # 24 Zeichen nach /w/
    ELEMENT_ID = "deine_element_id"        # 24 Zeichen nach /e/
    
    # Variable die geändert werden soll
    VARIABLE_NAME = "length"  # Name der Variable in Onshape
    
    # Bereich für die Schleife
    START_VALUE = 10.0        # Startwert
    END_VALUE = 50.0          # Endwert
    STEP_SIZE = 5.0           # Schrittweite
    
    # Export-Einstellungen
    OUTPUT_FOLDER = "output"  # Ordner für exportierte Dateien
    EXPORT_STEP = True        # STEP-Dateien exportieren?
    EXPORT_PARASOLID = False  # Parasolid (.x_t) Dateien exportieren?
    
    # Wartezeit zwischen Änderungen (Sekunden)
    DELAY_BETWEEN_ITERATIONS = 2
    
    # ======================================================
    
    # Erstelle Output-Ordner
    Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)
    
    # Initialisiere API
    api = OnshapeAPI(ACCESS_KEY, SECRET_KEY)
    
    # Berechne Anzahl der Iterationen
    values = []
    current = START_VALUE
    while current <= END_VALUE:
        values.append(current)
        current += STEP_SIZE
    
    print(f"\n{'='*60}")
    print(f"Starte Onshape API Automation")
    print(f"{'='*60}")
    print(f"Variable: {VARIABLE_NAME}")
    print(f"Werte: {START_VALUE} bis {END_VALUE} (Schritt: {STEP_SIZE})")
    print(f"Anzahl Iterationen: {len(values)}")
    print(f"{'='*60}\n")
    
    # Durchlaufe alle Werte
    for i, value in enumerate(values, 1):
        print(f"\n--- Iteration {i}/{len(values)}: {VARIABLE_NAME} = {value} ---")
        
        # 1. Variable ändern
        success = api.update_variable(
            document_id=DOCUMENT_ID,
            workspace_id=WORKSPACE_ID,
            element_id=ELEMENT_ID,
            variable_name=VARIABLE_NAME,
            new_value=value
        )
        
        if not success:
            print(f"⚠ Überspringe Export für Wert {value}")
            continue
        
        # Kurze Pause für Regenerierung
        time.sleep(1)
        
        # 2. Exportiere Dateien
        base_filename = f"{VARIABLE_NAME}_{value:g}"
        
        if EXPORT_STEP:
            step_path = os.path.join(OUTPUT_FOLDER, f"{base_filename}.step")
            api.export_step(
                document_id=DOCUMENT_ID,
                workspace_id=WORKSPACE_ID,
                element_id=ELEMENT_ID,
                output_path=step_path
            )
        
        if EXPORT_PARASOLID:
            parasolid_path = os.path.join(OUTPUT_FOLDER, f"{base_filename}.x_t")
            api.export_parasolid(
                document_id=DOCUMENT_ID,
                workspace_id=WORKSPACE_ID,
                element_id=ELEMENT_ID,
                output_path=parasolid_path
            )
        
        # Pause zwischen Iterationen
        if i < len(values):
            time.sleep(DELAY_BETWEEN_ITERATIONS)
    
    print(f"\n{'='*60}")
    print(f"✓ Fertig! {len(values)} Iterationen abgeschlossen")
    print(f"Dateien gespeichert in: {os.path.abspath(OUTPUT_FOLDER)}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
