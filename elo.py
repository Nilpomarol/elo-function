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
   
def update_elo_american(ratings, results, K=100, ratio = 800,numpistas = 6):
    """
    Calcula los nuevos puntajes Elo de los jugadores después de un torneo de sistema americano.

    Args:
        results (list): Lista de resultados de los partidos en el torneo.
        ratings (list): Lista de puntajes Elo de los jugadores.
        K (int): Factor de ajuste Elo (por defecto, K = -32 para aumentar la sensibilidad).

    Returns:
        list: Lista con los nuevos puntajes Elo de los jugadores.
    """
    # Calcula los nuevos puntajes Elo de los jugadores
    new_ratings = []
    avg = 0
    for pareja in ratings: 
        avg += pareja[0] + pareja[1]
    avg = avg / (len(ratings)*2)
    
    i = 0
    
    for result in results:
        pistainicial = result[0]
        pistafinal = result[1]
        gained = pistainicial - pistafinal 
        
        americana_result = (gained / numpistas)/2+0.5
        
        new_ratings_pareja = []
        
        for jugador in ratings[i]:
            P = 1/ (1 + 1 * math.pow(10, 1 * (avg - jugador) / ratio))
            new_elo = int(round(K * (americana_result - P)))
            if new_elo >= 0:
                elodiff = jugador - avg
                if elodiff < -200:
                    new_elo += 20
                elif elodiff < -100:
                    new_elo += 15
                else:
                    new_elo += 10
            new_ratings_pareja.append(new_elo)
            
        new_ratings.append((new_ratings_pareja[0],new_ratings_pareja[1]))
        i += 1

    return new_ratings

    
def page1():
    # Ejemplo de uso
    col1, col2 = st.columns(2)

    with col1:
        ratio = int(st.text_input("Importancia diferencia de ratings: ", "400"))  # Ratio de diferencia de puntajes Elo
        st.write("Equipo 1:")
        team1_elo = [int(st.text_input("jugador 1: ", "1349")), int(st.text_input("jugador 2: ", "1270"))]  # Puntajes Elo de los jugadores en el equipo 1
    with col2:
        k = int(st.text_input("Factor de ajuste Elo: ", "20"))  # Factor de ajuste Elo
        st.write("Equipo 2:")
        team2_elo = [int(st.text_input("jugador 3: ", "1406")), int(st.text_input("jugador 4: ", "1402"))]  # Puntajes Elo de los jugadores en el equipo 2
    result = st.text_input("Result: ", "3-7").split("-")
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
    col1, col2 = st.columns(2)

    with col1:
        ratio = int(st.text_input("Importancia diferencia de ratings: ", "400"))  # Ratio de diferencia de puntajes Elo
        st.write("Equipo 1:")
        team1_elo = [int(st.text_input("jugador 1: ", "1349")), int(st.text_input("jugador 2: ", "1270"))]  # Puntajes Elo de los jugadores en el equipo 1
    with col2:
        k = int(st.text_input("Factor de ajuste Elo: ", "20"))  # Factor de ajuste Elo
        st.write("Equipo 2:")
        team2_elo = [int(st.text_input("jugador 3: ", "1406")), int(st.text_input("jugador 4: ", "1402"))]  # Puntajes Elo de los jugadores en el equipo 2
    result = st.text_input("Result: ", "3-7").split("-")
    result = [int(result[0]), int(result[1])]


    new_elo_team1, new_elo_team2 = update_elo_2v2(team1_elo, team2_elo, result, k, ratio, base = 25)
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

def page3():
    st.title("Configuración de Parámetros")

    with st.expander("Parámetros de Elo"):
        ratio = st.slider("Importancia de Diferencia de Ratings", min_value=100, max_value=1000, value=800, step=50)
        k = st.slider("Factor de Ajuste Elo", min_value=10, max_value=200, value=100, step=5)

    # Sección para generar Ratings aleatorios
    st.subheader("Generar Ratings Aleatorios")
    with st.expander("Configuración de Ratings Aleatorios"):
        min_rating = st.number_input("Rating Mínimo", value=1000)
        max_rating = st.number_input("Rating Máximo", value=1500)
    generate_button = st.button("Generar Ratings Aleatorios")
    
    ratings = [(1000, 1270), (1349, 1270),(1349, 1270),(1349, 1270),(1349, 1270),(1349, 1270),(1349, 1270),(1349, 1270),(1349, 1270),(1349, 1270),(1349, 1270),(1349, 1270)]
    
    if generate_button:
        # Generar los pares de ratings aleatorios
        num_pairs = 12  # Número de pares de ratings que deseas generar (6 parejas)
        ratings = [(random.randint(min_rating, max_rating), random.randint(min_rating, max_rating)) for _ in range(num_pairs)]

    # Sección de Entrada de Ratings y Resultados
    st.subheader("Entrada de Ratings y Resultados")

    
    results = [(1, 1), (1,1), (2,2), (2,2), (3,3), (3,3), (4,4), (4,4), (5,5), (5,5), (6,6), (6,6)]
    colR = {}
    exp = True
    col1, col2 = st.columns(2)
    for i in range(0, 24, 2):
        if i > 2:
            exp = False
        with (col1 if i % 4 == 0 else col2):
            with st.expander(f"Pareja {(i+2)//2}", expanded = exp):
                col3, colR[i], col5 = st.columns(3)
                with col3:
                    ratings[i//2] = ((st.number_input(f"Jugador {i+1}", value=ratings[i//2][0]), st.number_input(f"Jugador {i+2}", value=ratings[i//2][1])))
                with col5:
                    results[i//2] = ((st.number_input(f"Pista Inicial Parella {(i+2)//2}", min_value=1, max_value = 6, value=results[i//2][0]), st.number_input(f"Pista Final Parella {(i+2)//2}", min_value=1, max_value = 6, value=results[i//2][0])))

    # Procesamiento y Mostrar Resultados

    new_elo_team1 = update_elo_american(ratings, results, k, ratio)
    # Aquí iría tu lógica de procesamiento con update_elo_american() y cálculos de new_elo_team1
    print (len(ratings))
    for i in range(0,24,2):
        with colR[i]:
            st.text_input(f"Canvio elo Jugador {i+1}", str(new_elo_team1[i//2][0]), disabled=True)
            st.text_input(f"Canvio elo Jugador {i+1}", new_elo_team1[i//2][1], disabled=True)


def page4():
    st.title("Configuración de Parámetros")

    with st.expander("Parámetros de Elo"):
        ratio = st.slider("Importancia de Diferencia de Ratings", min_value=100, max_value=3000, value=800, step=50)
        k = st.slider("Factor de Ajuste Elo", min_value=10, max_value=200, value=100, step=5)
    
    st.subheader("Entrada de Ratings y Resultados")
    
    with st.expander("Configuración de Ratings Aleatorios", expanded=True):
        variability = st.number_input("Variabilitat respecte la mitjana", value=200)
        average = st.number_input("mitjana", value=1500)

    generate_ratings = st.button("Ratings Aleatorios")


    ratings = [(1500, 1500), (average, average),(average, average),(average, average),(average, average),(average, average),(average, average),(average, average),(average, average),(average, average),(average, average),(average, average),]
    results = [(1, 1), (1,1), (2,2), (2,2), (3,3), (3,3), (4,4), (4,4), (5,5), (5,5), (6,6), (6,6)]

    if generate_ratings == True:
        randratings = (random.randint(average-variability, average+variability), random.randint(average-variability, average+variability))
        ratings[0] = randratings
        result = (random.randint(1,6), random.randint(1,6))
        results[0] = result
    
    with st.expander("Pareja 0: ", expanded = True):
        col1, col2 = st.columns(2)
        with col1:
            ratings[0] = (st.number_input("Jugador 1: ", value=ratings[0][0]), st.number_input("Jugador 2: ", value=ratings[0][1]))
        with col2:
            results[0] = (st.number_input("Pista Inicial: ", min_value=1, max_value = 6, value=results[0][0]), st.number_input("Pista Final: ", min_value=1, max_value = 6, value=results[0][1]))

    new_elo_team1 = update_elo_american(ratings, results, k, ratio)

    st.write("Nuevos puntajes Elo:")
    st.write("Pareja 0:")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"Jugador 1: {ratings[0][0]} -> {new_elo_team1[0][0]}")
    with col2:
        st.write(f"Jugador 2: {ratings[0][1]} -> {new_elo_team1[0][1]}")


st.set_page_config(layout="wide")
            
menu = st.sidebar.radio("Menu", ["Partido Normal", "Americana", "Americana Sube-Baja", "Americana Sube-baja prueba"])


if menu == "Partido Normal":
    page1()
elif menu == "Americana":
    page2()
elif menu == "Americana Sube-Baja":
    page3()
elif menu == "Americana Sube-baja prueba":
    page4()
else:
    st.error("Opción no válida")
