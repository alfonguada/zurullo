#!/usr/bin/env python3
"""
Reparte 2 sobres estándar gratuitos a todos los usuarios.
Diseñado para ejecutarse como tarea programada en PythonAnywhere a las 12:00.
Idempotente: si se ejecuta varias veces el mismo día, no reparte duplicados.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from app import app
from app import grant_daily_packs

with app.app_context():
    granted = grant_daily_packs()
    print(f'Sobres diarios repartidos: {granted}')
