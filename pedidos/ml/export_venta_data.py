import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_ecommerce.settings')  # Ajustá si tu settings.py tiene otro nombre
django.setup()

import pandas as pd
from pedidos.models import Detalle_Venta, Venta

def export_data():
    data = []

    ventas = Venta.objects.prefetch_related('detalles')
    for venta in ventas:
        productos = venta.detalles.all()
        for producto in productos:
            data.append({
                'venta_id': venta.id,
                'producto_id': producto.producto.id
            })

    df = pd.DataFrame(data)
    df.to_csv('ventas_productos.csv', index= False)
    print("Datos correctamente exportados")

if __name__ == "__main__":
    export_data()