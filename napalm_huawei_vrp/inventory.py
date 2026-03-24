# napalm_huawei_vrp/inventory.py
# -*- coding: utf-8 -*-
"""Inventory parser for Huawei VRP."""

import re

def parse_inventory(output):
    inventory = []
    blocks = re.split(r'\n\s*\n', output.strip())
    for block in blocks:
        lines = block.splitlines()
        if not lines:
            continue
        name = ''
        for line in lines:
            line = line.strip()
            if line.startswith('[') and line.endswith(']'):
                name = line[1:-1]
                break
        if not name:
            continue
        data = {}
        for line in lines:
            line = line.strip()
            if not line or (line.startswith('$') and '/' not in line):
                continue
            if '=' not in line:
                continue
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            key = key.lstrip('$/')
            if key == 'BoardType':
                data['model'] = value
            elif key == 'BarCode':
                data['serial'] = value
            elif key == 'Item':
                data['part_number'] = value
            elif key == 'Description':
                data['description'] = value
            elif key == 'Manufactured':
                data['manufactured'] = value
            elif key == 'VendorName':
                data['vendor'] = value
            elif key == 'Model':
                data['model'] = value

        # Пропускаем блоки без полезных данных
        if not data:
            continue
        if not (data.get('model') or data.get('serial') or data.get('description')):
            continue

        # Улучшаем имена
        if name == 'Board Properties':
            desc = data.get('description', '')
            if 'Assembling Components' in desc:
                name = 'Chassis'
            elif 'Power Module' in desc:
                name = 'Power Supply'
            elif 'Mbps' in desc or data.get('model', '').startswith('ML-'):
                name = 'Transceiver'

        entry = {
            'name': name,
            'description': data.get('description', ''),
            'serial': data.get('serial', ''),
            'part_number': data.get('part_number', ''),
            'model': data.get('model', ''),
            'manufactured': data.get('manufactured', ''),
            'vendor': data.get('vendor', ''),
        }
        inventory.append(entry)

    return inventory
