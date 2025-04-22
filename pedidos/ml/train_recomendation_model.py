import pandas as pd
import joblib
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix

def entrenar_modelo_knn():
    df = pd.read_csv('usuarios_productos.csv')
    df['valor'] = 1

    matriz = df.pivot_table(index='usuario_id', columns='producto_id', values='valor', fill_value=0)
    matriz_sparse = csr_matrix(matriz.values)

    modelo_knn = NearestNeighbors(metric='cosine', algorithm='brute')
    modelo_knn.fit(matriz_sparse.T)

    joblib.dump({
        'modelo': modelo_knn,
        'matriz': matriz,
        'productos': list(matriz.columns)
    }, 'modelo_knn_recomendaciones.pkl')

    print("Modelo KNN entrenado y guardado correctamente")

if __name__ == '__main__':
    entrenar_modelo_knn()