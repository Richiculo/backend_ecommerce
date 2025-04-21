import pandas as pd
import joblib
from collections import defaultdict
from itertools import combinations

def entrenar_modelo():
    df = pd.read_csv('ventas_productos.csv')
    ventas_productos = df.groupby('venta_id')['producto_id'].apply(list)
    co_ocurrencias = defaultdict(lambda: defaultdict(int))

    for productos in ventas_productos:
        productos_unicos = list(set(productos))
        for prod1, prod2 in combinations(productos_unicos, 2):
            co_ocurrencias[prod1][prod2] += 1
            co_ocurrencias[prod2][prod1] += 1

    joblib.dump(dict(co_ocurrencias), 'modelo_recomendaciones.pkl')

    print("Modelo entrenado y guardado correctamente")

if __name__=='__main__':
    entrenar_modelo()