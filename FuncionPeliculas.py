from fastapi import FastAPI, HTTPException, Request
import pandas as pd
import os

# Definir la ruta del archivo CSV para las votaciones y puntuaciones
votes_file_path = os.path.join(os.path.dirname(__file__), 'FuncionVotos.csv')
scores_file_path = os.path.join(os.path.dirname(__file__), 'FuncionScore.csv')

app = FastAPI(
    title="API de Películas",
    description="Esta API permite consultar información sobre películas, sus votaciones y puntuaciones.",
    version="1.0.0",
)

# Cargar los DataFrames una vez al iniciar la aplicación
votes_df = pd.read_csv(votes_file_path)
scores_df = pd.read_csv(scores_file_path)

print(votes_df.head())  # Verifica las primeras filas del DataFrame de votaciones
print(scores_df.head())  # Verifica las primeras filas del DataFrame de puntuaciones

@app.get("/", response_model=dict)
async def read_root(request: Request):
    base_url = str(request.url).rstrip('/')
    return {
        "message": "Bienvenido a la API de Películas!",
        "description": "Utiliza los siguientes endpoints para interactuar con la API:",
        "endpoints": {
            f"{base_url}/votes/?title=<nombre_pelicula>": "Devuelve información sobre la votación de la película especificada.",
            f"{base_url}/score/?title=<nombre_pelicula>": "Devuelve información sobre la popularidad de la película especificada.",
            f"{base_url}/titles/": "Devuelve una lista de todos los títulos de películas disponibles."
        },
        "example": {
            "Buscar votación de una película": f"{base_url}/votes/?title=Inception",
            "Buscar popularidad de una película": f"{base_url}/score/?title=Toy%20Story",
            "Listar títulos": f"{base_url}/titles/"
        }
    }

@app.get("/votes/")
async def get_movie_votes(title: str):
    print(f"Buscando votación para la película: '{title}'")  # Muestra el título buscado
    movie = votes_df[votes_df['title'].str.lower() == title.lower()]
    print(f"Películas encontradas en votaciones: {movie}")  # Muestra el DataFrame encontrado

    if movie.empty:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    movie_data = movie.iloc[0]
    


    # Cambia la condición para verificar si el número de votos es menor a 2000
    if movie_data['vote_count'] < 2000:
        return {
            "title": movie_data['title'],
            "vote_count": "La película cuenta con menos de 2000 valoraciones",
            "vote_average": ""
        }
    else:
        return {
            "title": movie_data['title'],
            "vote_count": int(movie_data['vote_count']),  # Convert to int
            "vote_average": float(movie_data['vote_average'])  # Convert to float
        }


@app.get("/score/")
async def get_movie_score(title: str):
    print(f"Buscando puntuación para la película: '{title}'")  # Muestra el título buscado
    movie = scores_df[scores_df['title'].str.lower() == title.lower()]
    print(f"Películas encontradas en puntuaciones: {movie}")  # Muestra el DataFrame encontrado

    if movie.empty:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    movie_data = movie.iloc[0]
    return {
        "message": f"La película '{movie_data['title']}' fue estrenada en el año {int(movie_data['release_year'])}, con una popularidad de {float(movie_data['popularity']):.2f}."
    }

@app.get("/titles/")
async def get_titles():
    print("Llamando al endpoint /titles/")  # Para diagnóstico
    return votes_df['title'].tolist()  # Asumiendo que ambos DataFrames tienen los mismos títulos

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
