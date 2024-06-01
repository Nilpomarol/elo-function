import math
import random
import streamlit as st
import pandas as pd
from pickle import dumps, loads

def update_elo_2v2(team1_ratings, team2_ratings, result, k=32, ratio=400, base=50, factoravg = 0.5):
    """
    Calculate new Elo ratings for two teams based on the outcome of a match.

    Args:
        team1_ratings (list): List of integers representing the Elo ratings of the first team's players.
        team2_ratings (list): List of integers representing the Elo ratings of the second team's players.
        result (list): List of two integers representing the scores of team 1 and team 2, respectively.
        k (int, optional): The maximum possible adjustment per player per game. Defaults to 32.
        ratio (int, optional): Used to scale the difference in ratings. Defaults to 400.
        base (int, optional): A base adjustment factor that can be modified based on the rating difference. Defaults to 50.

    Returns:
        tuple: Two lists containing the new Elo ratings for the players of team 1 and team 2 respectively.
    """
    team1_avg = sum(team1_ratings) / len(team1_ratings)
    team2_avg = sum(team2_ratings) / len(team2_ratings)
    
    # if (result[0] == 0): result[0] = 1
    # if (result[1] == 0): result[1] = 1
    
    # game_result = (result[0] / sum(result))*0.8 + 0.1
    game_result = (result[0] / sum(result))*0.9+ 0.05
    # game_result = result[0] / sum(result)
        
    rating_diff = abs(team1_avg - team2_avg)
    
    if result[0] > result[1]:
        team1_factor, team2_factor = 1, -1
    else:
        team1_factor, team2_factor = -1, 1
    
    if rating_diff > 1000:
        base -= 15
    elif rating_diff > 700:
        base -= 10
    elif rating_diff > 400:
        base -= 5
    
    def calculate_new_rating(rating, opponent_avg, game_result, factor):
        P = 1 / (1 + math.pow(10, (opponent_avg - rating) / ratio))
        return int(round(factor * base + k * (game_result - P)))
    
    team1_new_ratings = []
    for i in range(len(team1_ratings)):
        if i == 0:
            weightedavg = team1_ratings[i] * factoravg + team1_ratings[i+1] * (1-factoravg)
        else:
            weightedavg = team1_ratings[i] * factoravg + team1_ratings[i-1] * (1-factoravg)

        new_rating = calculate_new_rating(weightedavg, team2_avg, game_result, team1_factor)
        team1_new_ratings.append(new_rating)
    
    team2_new_ratings = []
    for i in range(len(team2_ratings)):
        if i == 0:
            weightedavg = team2_ratings[i] * factoravg + team2_ratings[i+1] * (1-factoravg)
        else:
            weightedavg = team2_ratings[i] * factoravg + team2_ratings[i-1] * (1-factoravg)
        new_rating = calculate_new_rating(weightedavg, team1_avg, 1 - game_result, team2_factor)
        team2_new_ratings.append(new_rating)
    
    return team1_new_ratings, team2_new_ratings
   
def update_elo_american(ratings, results, multipistes, compensacio, compensacio2, k=20, ratio = 800,numpistas = 6, base = 10, factoravg = 0.5):
    # Calcula los nuevos puntajes Elo de los jugadores
    new_ratings = []
    avg = 0
    for pareja in ratings: 
        avg += pareja[0] + pareja[1]
    avg = avg / (len(ratings)*2)
    
    i = 0
    first = True
    for result in results:
        pistainicial = result[0]
        pistafinal = result[1]
        gained = pistainicial - pistafinal
        gainedfactor = 0
        
        if (gained != 0):
            gainedfactor = abs(gained) - 1
            
        factor = (1 + gainedfactor * (multipistes/100))
        if (gained < 0):
            factor *= -1
        
        
        americana_result = (gained / numpistas)/2+0.5
        
        ajuste = 0
        if ((pistainicial == 1 or pistainicial == 2) and pistafinal == 1):
            ajuste = compensacio
        elif ((pistainicial == 5 or pistainicial == 6) and pistafinal == 6):
            ajuste = -compensacio
        


        
        new_ratings_pareja = []
        
        for j in range(len(ratings[i])):
            if j == 0:
                weightedavg = ratings[i][j] * factoravg + ratings[i][j+1] * (1-factoravg)
            else:
                weightedavg = ratings[i][j] * factoravg + ratings[i][j-1] * (1-factoravg)

            P = 1/ (1 + math.pow(10, (avg - weightedavg) / ratio))
            new_elo = int(round(factor * base + k * (americana_result - P)))

            new_elo += ajuste
            new_ratings_pareja.append(new_elo)
            
        new_ratings.append((new_ratings_pareja[0],new_ratings_pareja[1]))
        i += 1
        first = False


    return new_ratings

####################################################################INTERFICIE STREAMLIT####################################################################


def page1():
    st.header("Calculadora de Puntajes Elo Partidos Normales")
    
    col1, col2= st.columns(2)
    with col2:
        st.subheader("Parámetros de Elo")
        with st.expander("Parámetros de Elo", expanded=True,):
            ratio = st.slider("Importancia de Diferencia de Ratings (Ratio)", min_value=100, max_value=2000, value=400, step=50)
            k = st.slider("Factor de Ajuste Elo (k)", min_value=0, max_value=100, value=20, step=2)
            base = st.slider("Valor Base (Base)", min_value=0, max_value=100, value=50, step=1)
            factoravg = st.slider("Peso media pareja", min_value=0, max_value=100, value=70, step=1)

    if "ratings" not in st.session_state:
        st.session_state["ratings"] = [1200, 1210, 1220, 1230]
        st.session_state["result"] = [7, 5]
    
    with col2:
        with st.expander("Parámetros de Aleatoriedad", expanded=True):
            min_rating = st.number_input("Rating Mínimo", value=1000)
            max_rating = st.number_input("Rating Máximo", value=1500)
        
        generate_button = st.button("Generar Ratings Aleatorios")   
        if generate_button:
            st.session_state["ratings"] = [random.randint(min_rating, max_rating) for _ in range(4)]
            result1 = random.randint(0, 7)
            result2 = 7 if result1 != 7 else random.randint(0, 6)
            st.session_state["result"] = [result1, result2]
    
    with col1:
        st.subheader("Entrada de Ratings y Resultados")
        with st.expander("Explicación de Parámetros:"):
            st.write("""
            - **Ratio**: Determina la importancia de la diferencia de ratings entre los equipos. Un valor más alto reduce la influencia de la diferencia de ratings.
            
            - **k**: Controla la velocidad de ajuste del rating Elo. Un valor más alto significa ajustes más rápidos.
        
            - **Base**: Ajuste adicional que puede influir en el cambio de rating, especialmente cuando hay grandes diferencias de rating entre equipos.
                     
            - **Peso media pareja**: Factor que pondera el rating de los jugadores en función de la pareja. Un valor más alto significa que el rating del jugador se basa más en su propio rating que en el de su compañero. Un valor de 50, equivale a una media normal.
            """)

        col3, col4 = st.columns(2)
        with col3:
            st.write("Equipo 1:")
            team1_elo = [int(st.text_input(f"Jugador {i+1}: ", st.session_state["ratings"][i])) for i in range(2)]
        with col4:
            st.write("Equipo 2:")
            team2_elo = [int(st.text_input(f"Jugador {i+3}: ", st.session_state["ratings"][i+2])) for i in range(2)]
            
        result_input = st.text_input("Resultado: ", f"{st.session_state['result'][0]}-{st.session_state['result'][1]}")
        st.session_state["result"] = list(map(int, result_input.split("-")))

        new_elo_team1, new_elo_team2 = update_elo_2v2(team1_elo, team2_elo, st.session_state["result"], k, ratio, base, factoravg/100)

        data = {
            "Jugador": ["Jugador 1", "Jugador 2", "Jugador 3", "Jugador 4"],
            "Equipo": ["Equipo 1", "Equipo 1", "Equipo 2", "Equipo 2"],
            "Rating Anterior": team1_elo + team2_elo,
            "Nuevo Rating": new_elo_team1 + new_elo_team2
        }

        df = pd.DataFrame(data)
        st.table(df)

def page2():
    st.header("Calculadora de Puntajes Elo Partidos Americana")
    
    col1, col2= st.columns(2)
    with col2:
        st.subheader("Parámetros de Elo")
        with st.expander("Parámetros de Elo", expanded=True,):
            ratio = st.slider("Importancia de Diferencia de Ratings (Ratio)", min_value=100, max_value=2000, value=400, step=50)
            k = st.slider("Factor de Ajuste Elo (k)", min_value=0, max_value=100, value=20, step=2)
            base = st.slider("Valor Base (Base)", min_value=0, max_value=100, value=20, step=1)
            factoravg = st.slider("Peso media pareja", min_value=0, max_value=100, value=70, step=1)
            
    if "ratings" not in st.session_state:
        st.session_state["ratings"] = [1200, 1210, 1220, 1230]
        st.session_state["result"] = [7, 5]
    
    with col2:
        with st.expander("Parámetros de Aleatoriedad", expanded=True):
            min_rating = st.number_input("Rating Mínimo", value=1000)
            max_rating = st.number_input("Rating Máximo", value=1500)
        
        generate_button = st.button("Generar Ratings Aleatorios")   
        if generate_button:
            st.session_state["ratings"] = [random.randint(min_rating, max_rating) for _ in range(4)]
            result1 = random.randint(0, 7)
            result2 = 7 if result1 != 7 else random.randint(0, 6)
            st.session_state["result"] = [result1, result2]
    
    with col1:
        st.subheader("Entrada de Ratings y Resultados")
        with st.expander("Explicación de Parámetros:"):
            st.write("""
            - **Ratio**: Determina la importancia de la diferencia de ratings entre los equipos. Un valor más alto reduce la influencia de la diferencia de ratings.
            
            - **k**: Controla la velocidad de ajuste del rating Elo. Un valor más alto significa ajustes más rápidos.
        
            - **Base**: Ajuste adicional que puede influir en el cambio de rating, especialmente cuando hay grandes diferencias de rating entre equipos.
                     
            - **Peso media pareja**: Factor que pondera el rating de los jugadores en función de la pareja. Un valor más alto significa que el rating del jugador se basa más en su propio rating que en el de su compañero. Un valor de 50, equivale a una media normal.
            """)
        col3, col4 = st.columns(2)
        with col3:
            st.write("Equipo 1:")
            team1_elo = [int(st.text_input(f"Jugador {i+1}: ", st.session_state["ratings"][i])) for i in range(2)]
        with col4:
            st.write("Equipo 2:")
            team2_elo = [int(st.text_input(f"Jugador {i+3}: ", st.session_state["ratings"][i+2])) for i in range(2)]
            
        result_input = st.text_input("Resultado: ", f"{st.session_state['result'][0]}-{st.session_state['result'][1]}")
        st.session_state["result"] = list(map(int, result_input.split("-")))

        new_elo_team1, new_elo_team2 = update_elo_2v2(team1_elo, team2_elo, st.session_state["result"], k, ratio, base, factoravg/100)

        data = {
            "Jugador": ["Jugador 1", "Jugador 2", "Jugador 3", "Jugador 4"],
            "Equipo": ["Equipo 1", "Equipo 1", "Equipo 2", "Equipo 2"],
            "Rating Anterior": team1_elo + team2_elo,
            "Nuevo Rating": new_elo_team1 + new_elo_team2
        }

        df = pd.DataFrame(data)
        st.table(df)

def update_ratingsComplets(key, index, isSecond, ratings):
    if isSecond:
        index += 1
    value = st.session_state[key]
    
    if ratings:
        if not isSecond:
            newRating = (value, loads(st.session_state.ratingsComplets)[index][1])
        else:
            newRating = (loads(st.session_state.ratingsComplets)[index][0], value)
        aux = loads(st.session_state.ratingsComplets)
        aux[index] = newRating
        st.session_state.ratingsComplets = dumps(aux)
    else:
        if not isSecond:
            newResult = (value, loads(st.session_state.resultsComplets)[index][1])
        else:
            newResult = (loads(st.session_state.resultsComplets)[index][0], value)
        aux = loads(st.session_state.resultsComplets)
        aux[index] = newResult
        st.session_state.resultsComplets = dumps(aux)    

def page3():
    st.header("Calculadora de Puntajes Elo Partidos Americana Sube-Baja")
    st.write("")
    st.write("")

    if "ratingsComplets" not in st.session_state:
        ratingsComplets = [(1000, 1000)] * 12
        st.session_state.ratingsComplets = dumps(ratingsComplets)

    if "resultsComplets" not in st.session_state:
        resultsComplets = [(1, 1), (1, 1), (2, 2), (2, 2), (3, 3), (3, 3), (4, 4), (4, 4), (5, 5), (5, 5), (6, 6), (6, 6)]
        st.session_state.resultsComplets = dumps(resultsComplets)

    for i in range(0, 12):
        st.session_state[f"rating_{i*2}"] = loads(st.session_state.ratingsComplets)[i][0]
        st.session_state[f"rating_{i*2+1}"] = loads(st.session_state.ratingsComplets)[i][1]
        st.session_state[f"result_INI_{i}"] = loads(st.session_state.resultsComplets)[i][0]
        st.session_state[f"result_FIN_{i}"] = loads(st.session_state.resultsComplets)[i][1]

    with st.expander(r"$\textsf{\Large Explicacion de parametros}$", expanded=True):
        st.markdown("""
            - **Importancia de Diferencia de Ratings:** Determina la sensibilidad del cálculo Elo a la diferencia de ratings entre jugadores. Valores más altos hacen que la diferencia de rating tenga menos impacto.
            - **Factor de Ajuste Elo:** Controla la magnitud del ajuste del rating después de cada partida. Valores más altos resultan en cambios de rating más grandes.
            - **Puntuación Base:** Añade una cantidad fija al ajuste de Elo en cada partida.
            - **Multiplicador de Pistas en %:** Ajusta el impacto de la diferencia de pistas ganadas o perdidas en el cálculo del Elo. Se aplica sobre la puntuación base. Si se suben 5 pistas se ganará (4 * multiplicador * base) como valor base.
            - **Compensación:** Ajusta el Elo de los jugadores que empiezan en la pista 1/2 y terminan en la 1 y de los jugadores que empiezan en la 5/6 y terminan en la 6.
            - **Peso media pareja:** Factor que pondera el rating de los jugadores en función de la pareja. Un valor más alto significa que el rating del jugador se basa más en su propio rating que en el de su compañero. Un valor de 50 equivale a una media normal.
        """)

    st.subheader("Configuración de Parámetros Aleatorios")
    with st.expander(r"$\textsf{\Large Configuración de Ratings Aleatorios}$", expanded=True):
        variability = st.number_input("Variabilidad respecto a la media", value=200)
        average = st.number_input("Media", value=1500)

    st.subheader("Configuración Parámetros")
    with st.expander(r"$\textsf{\Large Parametros de Elo}$", expanded=True):
        col1, col2 = st.columns([1, 1])
        with col1:
            ratio = st.slider("Importancia de Diferencia de Ratings", min_value=100, max_value=3000, value=600, step=20)
            k = st.slider("Factor de Ajuste Elo", min_value=10, max_value=300, value=32, step=1)
            base = st.slider("Puntuación Base", min_value=0, max_value=100, value=20, step=1)
            
        with col2:
            multpistes = st.slider("Multiplicador de Pistas en %", min_value=0, max_value=100, value=20, step=1)
            compensacio = st.slider("Compensación", min_value=0, max_value=100, value=0, step=1)
            factoravg = st.slider("Peso Media Pareja", min_value=0, max_value=100, value=70, step=1)
    
    generate_ratings = st.button("Ratings Aleatorios")

    if generate_ratings:
        num_pairs = 12
        st.session_state.ratingsComplets = dumps([(random.randint(average - variability, average + variability), 
                                                   random.randint(average - variability, average + variability)) for _ in range(num_pairs)])
        aux = []
        pistasInicials = {}
        pistasFinals = {}
        
        for i in range(0, num_pairs):
            pIni = random.randint(1, 6)
            while (pIni in pistasInicials and pistasInicials[pIni] >= 2):
                pIni = random.randint(1, 6)
            pistasInicials[pIni] = pistasInicials.get(pIni, 0) + 1
            pFin = random.randint(1, 6)
            while (pFin in pistasFinals and pistasFinals[pFin] >= 2):
                pFin = random.randint(1, 6)
            pistasFinals[pFin] = pistasFinals.get(pFin, 0) + 1
            aux.append((pIni, pFin))

        for i in range(12):
            st.session_state[f"rating_{i*2}"] = loads(st.session_state.ratingsComplets)[i][0]
            st.session_state[f"rating_{i*2+1}"] = loads(st.session_state.ratingsComplets)[i][1]
            st.session_state[f"result_INI_{i}"] = aux[i][0]
            st.session_state[f"result_FIN_{i}"] = aux[i][1]
        st.session_state.resultsComplets = dumps(aux)

    cola, colb = st.columns([1, 1])
    with cola: 
        st.subheader("Entrada de Ratings y Resultados")
    with colb:
        avg = sum([sum(pair) for pair in loads(st.session_state.ratingsComplets)]) / (len(loads(st.session_state.ratingsComplets)) * 2)
        st.subheader(f"Media del pozo: {round(avg)}")

    colR = {}
    col1, col2 = st.columns(2)
    with col1:
        for i in range(0, 12, 2):
            with st.expander(f"pareja {i}", expanded=True):
                col3, colR[i], col5 = st.columns(3)
                with col3:
                    st.number_input(f"Jugador {i*2}", key=f"rating_{i*2}", step=1, 
                                    on_change=lambda key=f"rating_{i*2}", index=i, isSecond=False: update_ratingsComplets(key, index, isSecond, True))
                    st.number_input(f"Jugador {i*2+1}", key=f"rating_{i*2+1}", step=1, 
                                    on_change=lambda key=f"rating_{i*2+1}", index=i, isSecond=True: update_ratingsComplets(key, index, isSecond, True))
                with col5:
                    st.number_input(f"Pista Inicial Pareja {i}", key=f"result_INI_{i}", min_value=1, max_value=6, step=1, 
                                    on_change=lambda key=f"result_INI_{i}", index=i, isSecond=False: update_ratingsComplets(key, index, isSecond, False))
                    st.number_input(f"Pista Final Pareja {i}", key=f"result_FIN_{i}", min_value=1, max_value=6, step=1, 
                                    on_change=lambda key=f"result_FIN_{i}", index=i, isSecond=True: update_ratingsComplets(key, index, isSecond, False))
    
    with col2:
        for i in range(1, 12, 2):
            with st.expander(f"pareja {i}", expanded=True):
                col3, colR[i], col5 = st.columns(3)
                with col3:
                    st.number_input(f"Jugador {i*2}", key=f"rating_{i*2}", step=1, 
                                    on_change=lambda key=f"rating_{i*2}", index=i, isSecond=False: update_ratingsComplets(key, index, isSecond, True))
                    st.number_input(f"Jugador {i*2+1}", key=f"rating_{i*2+1}", step=1, 
                                    on_change=lambda key=f"rating_{i*2+1}", index=i, isSecond=True: update_ratingsComplets(key, index, isSecond, True))
                with col5:
                    st.number_input(f"Pista Inicial Pareja {i}", key=f"result_INI_{i}", min_value=1, max_value=6, step=1, 
                                    on_change=lambda key=f"result_INI_{i}", index=i, isSecond=False: update_ratingsComplets(key, index, isSecond, False))
                    st.number_input(f"Pista Final Pareja {i}", key=f"result_FIN_{i}", min_value=1, max_value=6, step=1, 
                                    on_change=lambda key=f"result_FIN_{i}", index=i, isSecond=True: update_ratingsComplets(key, index, isSecond, False))

    new_elo_team1 = update_elo_american(loads(st.session_state.ratingsComplets), loads(st.session_state.resultsComplets), multpistes, compensacio, 0, k = k, ratio = ratio, base = base, factoravg = factoravg/100)
    
    for i in range(12):
        with colR[i]:
            st.text_input(f"Cambio Elo Jugador {i*2}", str(new_elo_team1[i][0]), disabled=True)
            st.text_input(f"Cambio Elo Jugador {i*2+1}", str(new_elo_team1[i][1]), disabled=True)



    st.write("")
    st.write("")



def page4():
    st.header("Calculadora de Puntajes Elo Partidos Americana Sube-Baja")
    st.write("")
    st.write("")

    if "ratings" not in st.session_state:
        st.session_state.ratings = (1500, 1500)
    if "results" not in st.session_state:
        st.session_state.results = (1, 1)
    with st.expander(r"$\textsf{\Large Explicacion de parametros}$", expanded = True):
            st.markdown("""
                - **Importancia de Diferencia de Ratings:** Determina la sensibilidad del cálculo Elo a la diferencia de ratings entre jugadores. Valores más altos hacen que la diferencia de rating tenga menos impacto.
                - **Factor de Ajuste Elo:** Controla la magnitud del ajuste del rating después de cada partida. Valores más altos resultan en cambios de rating más grandes.
                - **Puntuación Base:** Añade una cantidad fija al ajuste de Elo en cada partida.
                - **Multiplicador de Pistas en %:** Ajusta el impacto de la diferencia de pistas ganadas o perdidas en el cálculo del Elo. Se aplica sobre la puntuacion base. Si se suben 5 pistas se ganara (4 * multiplcador * base) como valor base.
                - **Compensación:** Ajusta el Elo de los jugadores que empiezan en la pista 1/2 y terminan en la 1 y de los jugadores que empiezan en la 5/6 y terminan en la 6.
                - **Peso media pareja:** Factor que pondera el rating de los jugadores en función de la pareja. Un valor más alto significa que el rating del jugador se basa más en su propio rating que en el de su compañero. un valor de 50, equivale a una media normal.
            """)
    col1, col2 = st.columns([2,1])
    with col2:
        st.subheader("Configuración Parámetros")
        with st.expander(r"$\textsf{\Large Parametros de Elo}$", expanded=True):
            ratio = st.slider("Importancia de Diferencia de Ratings", min_value=100, max_value=3000, value=600, step=20)
            k = st.slider("Factor de Ajuste Elo", min_value=10, max_value=300, value=32, step=1)
            base = st.slider("puntuacion base", min_value=0, max_value=100, value=20, step=1)
            multpistes = st.slider("Multiplicador de pistas en %", min_value=0, max_value=100, value=20, step=1)
            compensacio = st.slider("Compensación", min_value=0, max_value=100, value=0, step=1)
            factoravg = st.slider("Peso media pareja", min_value=0, max_value=100, value=70, step=1)
    
    with col1:
        st.subheader("Configuración de parametros aleatorios")
    
        with st.expander(r"$\textsf{\Large Configuración de Ratings Aleatorios}$", expanded=True):
            variability = st.number_input("Variabilitat respecte la mitjana", value=200)
            average = st.number_input("mitjana", value=1500)

        generate_ratings = st.button("Ratings Aleatorios")

        ratings = [st.session_state.ratings, (average, average),(average, average),(average, average),(average, average),(average, average),(average, average),(average, average),(average, average),(average, average),(average, average),(average, average),]
        results = [st.session_state.results, (1,1), (2,2), (2,2), (3,3), (3,3), (4,4), (4,4), (5,5), (5,5), (6,6), (6,6)]

        if generate_ratings == True:
            randratings = (random.randint(average-variability, average+variability), random.randint(average-variability, average+variability))
            ratings[0] = randratings
            st.session_state.ratings = randratings
            result = (random.randint(1,6), random.randint(1,6))
            results[0] = result
            st.session_state.results = result
       
        st.subheader("Entrada de Ratings y Resultados")
        col3, col4, col5 = st.columns([5,5,6])
        with col3:
            ratings[0] = (st.number_input("Jugador 1: ", value=ratings[0][0]), st.number_input("Jugador 2: ", value=ratings[0][1]))
        with col4:
            results[0] = (st.number_input("Pista Inicial: ", min_value=1, max_value = 6, value=results[0][0]), st.number_input("Pista Final: ", min_value=1, max_value = 6, value=results[0][1]))
            
        new_elo_team1 = update_elo_american(ratings, results, multpistes, compensacio, 0,k = k, ratio = ratio, base = base, factoravg = factoravg/100)

    with col5:
        st.write("Resultados:")
        data = {
            'Jugador': ['Jugador 1', 'Jugador 2'],
            'Rating inicial': [ratings[0][0], ratings[0][1]],
            'Cambio Elo': [new_elo_team1[0][0], new_elo_team1[0][1]]
        }

        df = pd.DataFrame(data)
        st.write(df)

st.set_page_config(layout="wide")
            
menu = st.sidebar.radio("Menu", ["Partido Normal", "Americana", "Americana Sube-Baja Entera", "Americana Sube-Baja"])


if menu == "Partido Normal":
    page1()
elif menu == "Americana":
    page2()
elif menu == "Americana Sube-Baja Entera":
    page3()
elif menu == "Americana Sube-Baja":
    page4()
else:
    st.error("Opción no válida")
