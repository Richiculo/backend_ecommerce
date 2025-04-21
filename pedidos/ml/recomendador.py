import joblib

co_ocurrencias = joblib.load('modelo_recomendaciones.pkl')

def recomendar(productos_en_carrito, top_n=5):
    recomendaciones = {}

    for producto_id in productos_en_carrito:
        similares = co_ocurrencias.get(producto_id, {})
        for prod_similar, score in similares.items():
            if prod_similar not in productos_en_carrito:
                if prod_similar in recomendaciones:
                    recomendaciones[prod_similar] += score
                else:
                    recomendaciones[prod_similar] = score
                
    recomendaciones_ordenadas = sorted(
        recomendaciones.items(),
        key=lambda x: x[1],
        reverse=True
    )
    return [prod_id for prod_id, _ in recomendaciones_ordenadas[:top_n]]