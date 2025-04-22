import joblib
import numpy as np

#carga de modelo ya entrenado
modelo_data = joblib.load('modelo_knn_recomendaciones.pkl')
modelo_knn = modelo_data['modelo']
matriz = modelo_data['matriz']
productos = modelo_data['productos']

#mapeo de indice a producto
producto_idx_map = {producto: idx for idx, producto in enumerate(productos)}

def recomendar(productos_en_carrito, top_n=5):
    recomendaciones = {}

    for producto_id in productos_en_carrito:
        if producto_id not in producto_idx_map:
            continue
        
        idx = producto_idx_map[producto_id]
        vector_producto = matriz.iloc[:, idx].values.reshape(1, -1)

        distancias, indices = modelo_knn.kneighbors(vector_producto, n_neighbors=top_n + 1)

        for dist, idx_vecino in zip(distancias[0], indices[0]):
            producto_vecino = productos[idx_vecino]
            if producto_vecino not in productos_en_carrito and producto_vecino not in recomendaciones:
                recomendaciones[producto_vecino] = 1 - dist # a menor dsitancia, mas similitud
        
    recomendaciones_ordenadas = sorted(recomendaciones.items(), key=lambda x: x[1], reverse=True)
    return [prod_id for prod_id, _ in recomendaciones_ordenadas[:top_n]]