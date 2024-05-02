import math
import random
import streamlit as st


def update_elo_2v2(team1_ratings, team2_ratings, result, K=32, ratio = 400, base = 50):
    """
    Calcula los nuevos puntajes Elo de los jugadores después de un partido 2 vs 2.

    Args:
        team1_ratings (list): Lista de puntajes Elo de los jugadores en el equipo 1.
        team2_ratings (list): Lista de puntajes Elo de los jugadores en el equipo 2.
        result (list): Resultado del partido [puntos anotados por equipo 1, puntos anotados por equipo 2].
        K (int): Factor de ajuste Elo (por defecto, K = -32 para aumentar la sensibilidad).

    Returns:
        tuple: Tupla con los nuevos puntajes Elo de los jugadores en cada equipo.
    """
    # Calcula la probabilidad de que el equipo 1 gane
    team1_avg = sum(team1_ratings) / len(team1_ratings)
    team2_avg = sum(team2_ratings) / len(team2_ratings)
    
    # Calcula los nuevos puntajes Elo de los jugadores en cada equipo
    team1_new_ratings = []
    team2_new_ratings = []
    game_result = result[0] / (result[0] + result[1])
    game_result = (game_result*0.8)+0.1

    if result[0] > result[1]:
        if (team1_avg - team2_avg) > 1000:
            base = base - 15
        elif (team1_avg - team2_avg) > 700:
            base = base - 10
        elif (team1_avg - team2_avg) > 400:
            base = base - 5
        for rating in team1_ratings:
            team1_P = 1/ (1 + 1 * math.pow(10, 1 * (team2_avg - rating) / ratio))
            team1_new_ratings.append(int(round(base+K * (game_result - team1_P))))  # Equipo 1
        for rating in team2_ratings:
            team2_P = 1/ (1 + 1 * math.pow(10, 1 * (team1_avg - rating) / ratio))
            team2_new_ratings.append(int(round(-base + K * (1-game_result - team2_P))))
    else:
        if (team2_avg - team1_avg) > 1000:
            base = base - 15
        elif (team2_avg - team1_avg) > 700:
            base = base - 10
        elif (team2_avg - team1_avg) > 400:
            base = base - 5
        for rating in team1_ratings:
            team1_P = 1/ (1 + 1 * math.pow(10, 1 * (team2_avg - rating) / ratio))
            team1_new_ratings.append(int(round(-base+K * (game_result - team1_P))))  # Equipo 1
        for rating in team2_ratings:
            team2_P = 1/ (1 + 1 * math.pow(10, 1 * (team1_avg - rating) / ratio))
            team2_new_ratings.append(int(round(base+K * (1-game_result - team2_P))))
    
    return team1_new_ratings, team2_new_ratings
   
   
def page1():
    # Ejemplo de uso
    
    st.subheader("Calculadora de Puntajes Elo Partidos Normales")
    with st.expander("Parámetros de Elo"):
        ratio = st.slider("Importancia de Diferencia de Ratings", min_value=100, max_value=6000, value=400, step=50)
        k = st.slider("Factor de Ajuste Elo", min_value=0, max_value=100, value=20, step=5)
    
    rating1 = 1200
    rating2 = 1210
    rating3 = 1220
    rating4 = 1230
    result = [7, 5]
    
    
    st.subheader("Generar Ratings Aleatorios")
    with st.expander("Parámetros de Aleatoriedad"):
        min_rating = st.number_input("Rating Mínimo", value=1000)
        max_rating = st.number_input("Rating Máximo", value=1500)
    generate_button = st.button("Generar Ratings Aleatorios")
    if generate_button:
        rating1 = random.randint(min_rating, max_rating)
        rating2 = random.randint(min_rating, max_rating)
        rating3 = random.randint(min_rating, max_rating)
        rating4 = random.randint(min_rating, max_rating)
        
        result1 = random.randint(0, 1)
        if result1 == 0:
            result1 = random.randint(0, 6)
            result2 = 7
        else:
            result1 = 7
            result2 = random.randint(0, 6)
        
        result = [result1, result2]

    col1, col2 = st.columns(2)
    with col1:
        
        st.write("Equipo 1:")
        team1_elo = [int(st.text_input("jugador 1: ", rating1)), int(st.text_input("jugador 2: ", rating2))]  # Puntajes Elo de los jugadores en el equipo 1
    with col2:
        
        st.write("Equipo 2:")
        team2_elo = [int(st.text_input("jugador 3: ", rating3)), int(st.text_input("jugador 4: ", rating4))]  # Puntajes Elo de los jugadores en el equipo 2
    result = st.text_input("Result: ", str(result[0]) +"-"+ str(result[1])).split("-")
    result = [int(result[0]), int(result[1])]


    new_elo_team1, new_elo_team2 = update_elo_2v2(team1_elo, team2_elo, result, k, ratio)
    st.write("Nuevos puntajes Elo:")
    col1, col2 = st.columns(2)
    with col1:
        st.write("Equipo 1:")
        for i, elo in enumerate(new_elo_team1):
            st.write(f"Jugador {i+1}: {team1_elo[i]} -> {elo}")
    with col2:
        st.write("Equipo 2:")
        for i, elo in enumerate(new_elo_team2):
            st.write(f"Jugador {i+3}: {team2_elo[i]} -> {elo}")
            
def page2():
    # Ejemplo de uso
    st.subheader("Calculadora de Puntajes Elo Partidos Americana")
    with st.expander("Parámetros de Elo"):
        ratio = st.slider("Importancia de Diferencia de Ratings", min_value=100, max_value=6000, value=400, step=50)
        k = st.slider("Factor de Ajuste Elo", min_value=0, max_value=100, value=20, step=5)
        puntuacionBase = st.slider("Puntuación Base", min_value=0, max_value=100, value=20, step=5)
    
    rating1 = 1200
    rating2 = 1210
    rating3 = 1220
    rating4 = 1230
    result = [7, 5]
    
    
    st.subheader("Generar Ratings Aleatorios")
    with st.expander("Parámetros de Aleatoriedad"):
        min_rating = st.number_input("Rating Mínimo", value=1000)
        max_rating = st.number_input("Rating Máximo", value=1500)
    generate_button = st.button("Generar Ratings Aleatorios")
    if generate_button:
        rating1 = random.randint(min_rating, max_rating)
        rating2 = random.randint(min_rating, max_rating)
        rating3 = random.randint(min_rating, max_rating)
        rating4 = random.randint(min_rating, max_rating)
        
        result1 = random.randint(0, 1)
        if result1 == 0:
            result1 = random.randint(0, 6)
            result2 = 7
        else:
            result1 = 7
            result2 = random.randint(0, 6)
        
        result = [result1, result2]

    col1, col2 = st.columns(2)
    with col1:
        
        st.write("Equipo 1:")
        team1_elo = [int(st.text_input("jugador 1: ", rating1)), int(st.text_input("jugador 2: ", rating2))]  # Puntajes Elo de los jugadores en el equipo 1
    with col2:
        
        st.write("Equipo 2:")
        team2_elo = [int(st.text_input("jugador 3: ", rating3)), int(st.text_input("jugador 4: ", rating4))]  # Puntajes Elo de los jugadores en el equipo 2
    result = st.text_input("Result: ", str(result[0]) +"-"+ str(result[1])).split("-")
    result = [int(result[0]), int(result[1])]



    new_elo_team1, new_elo_team2 = update_elo_2v2(team1_elo, team2_elo, result, k, ratio, base = puntuacionBase)
    st.write("Nuevos puntajes Elo:")
    col1, col2 = st.columns(2)
    with col1:
        st.write("Equipo 1:")
        for i, elo in enumerate(new_elo_team1):
            st.write(f"Jugador {i+1}: {team1_elo[i]} -> {elo}")
    with col2:
        st.write("Equipo 2:")
        for i, elo in enumerate(new_elo_team2):
            st.write(f"Jugador {i+3}: {team2_elo[i]} -> {elo}")
            
menu = st.sidebar.radio("Menu", ["Partido Normal", "Americana"])

if menu == "Partido Normal":
    page1()
elif menu == "Americana":
    page2()