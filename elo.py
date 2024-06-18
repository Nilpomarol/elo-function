import math


def update_elo_2v2(team1_ratings, team2_ratings, result, k=32, ratio=400, base=50, factoravg = 0.5):
    """
    Actualiza las puntuaciones Elo de dos equipos después de un partido.

    Parámetros:
    - team1_ratings (list of ints): Lista de las puntuaciones Elo de los jugadores del primer equipo. 
      Debe contener exactamente dos elementos, que son los ratings de la primera pareja.
        Ejemplo: [1500, 1600]
    - team2_ratings (list of ints): Lista de las puntuaciones Elo de los jugadores del segundo equipo. 
      Debe contener exactamente dos elementos, que son los ratings de la segunda pareja.
        Ejemplo: [1550, 1650]
    - result (list of ints): Lista que contiene el resultado del partido. El primer elemento representa la puntuación 
      del equipo 1 y el segundo elemento representa la puntuación del equipo 2.
        Ejemplo: [1, 0]
    - k (int, optional): Constante K utilizada en la fórmula de actualización del Elo. Por defecto es 32.
        Ejemplo: 32
    - ratio (int, optional): Valor del ratio utilizado en la fórmula para calcular la probabilidad esperada. Por defecto es 400.
        Ejemplo: 400
    - base (int, optional): Base inicial para ajustar las puntuaciones Elo. Por defecto es 50, en partidos normales. Se deberia cambiar a 20 por partidos de        americanas.
        Ejemplo: 50
    - factoravg (float, optional): Factor utilizado para calcular el promedio ponderado de las puntuaciones del equipo. 
      Por defecto es 0.5.
        Ejemplo: 0.5

    Retorna:
    - team1_new_ratings (list of ints): Lista de las nuevas puntuaciones Elo de los jugadores del primer equipo.
    - team2_new_ratings (list of ints): Lista de las nuevas puntuaciones Elo de los jugadores del segundo equipo.
    """
    team1_avg = sum(team1_ratings) / len(team1_ratings)
    team2_avg = sum(team2_ratings) / len(team2_ratings)
    
    game_result = (result[0] / sum(result))*0.9+ 0.05
        
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
   
def update_elo_american(ratings, results, multipistes = 20, compensacio = 0, compensacio2 = 10, bonificacion = 0, k=32, ratio = 600,numpistas = 6, base = 15, factoravg = 0.7):
    """
    Calcula los nuevos puntajes Elo de los jugadores en un formato de torneo americano.

    Parámetros:
    - ratings (list of tuples of ints): Lista de las puntuaciones Elo de las parejas de jugadores. 
      Cada pareja se representa como una tupla con dos elementos que representan los ratings de cada uno de los jugadores.
        Ejemplo: [(1500, 1600), (1550, 1650)]
    - results (list of tuples of ints): Lista que contiene los resultados de las americanas de cada pareja. Cada resultado se representa
      como una tupla donde el primer elemento es la pista inicial y el segundo elemento es la pista final.
        Ejemplo: [(1, 3), (4, 2)]
    - multipistes (float, optional): Factor de multiplicación utilizado para ajustar el factor de ganancia según las pistas.
        Ejemplo: 5.0
    - compensacio (float, optional): Compensación inicial para ajustar las puntuaciones Elo.
        Ejemplo: 10.0
    - compensacio2 (float, optional): Segunda compensación utilizada para ajustes adicionales de las puntuaciones Elo.
        Ejemplo: 5.0
    - bonificacion (float, optional): Bonificación aplicada según el rendimiento en las pistas.
        Ejemplo: 10.0
    - k (int, optional): Constante K utilizada en la fórmula de actualización del Elo. Por defecto es 20.
        Ejemplo: 20
    - ratio (int, optional): Valor del ratio utilizado en la fórmula para calcular la probabilidad esperada. Por defecto es 800.
        Ejemplo: 800
    - numpistas (int, optional): Número de pistas consideradas en el torneo. Por defecto es 6.
        Ejemplo: 6
    - base (int, optional): Base inicial para ajustar las puntuaciones Elo. Por defecto es 10.
        Ejemplo: 10
    - factoravg (float, optional): Factor utilizado para calcular el promedio ponderado de las puntuaciones del equipo. 
      Por defecto es 0.5.
        Ejemplo: 0.5

    Retorna:
    - new_ratings (list of tuples of ints): Lista de las nuevas puntuaciones Elo de las parejas de jugadores.
    """
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
        gainedfactor = 0
        
        if (gained != 0):
            gainedfactor = abs(gained) - 1
            
        factor = (1 + gainedfactor * (multipistes/100))
        if (gained < 0):
            factor *= -1
        
        
        americana_result = (gained / numpistas)/2+0.5
        
        preajuste = 0
        if ((pistainicial == 1 or pistainicial == 2) and pistafinal == 1):
            preajuste = compensacio
        elif ((pistainicial == 5 or pistainicial == 6) and pistafinal == 6):
            preajuste = -compensacio
        
        
        
        new_ratings_pareja = []
        
        for j in range(len(ratings[i])):
            if j == 0:
                weightedavg = ratings[i][j] * factoravg + ratings[i][j+1] * (1-factoravg)
            else:
                weightedavg = ratings[i][j] * factoravg + ratings[i][j-1] * (1-factoravg)


            P = 1/ (1 + math.pow(10, (avg - weightedavg) / ratio))
            new_elo = int(round(factor * base + k * (americana_result - P)))


            ajuste = preajuste
            diff = weightedavg - avg

            if compensacio2 != 0:
                if pistafinal == 6:
                    ajuste -= compensacio2 * (1+(abs(diff)//200)/10 if diff > 0 else 1)
                elif pistafinal == 5:
                    ajuste -= compensacio2*0.5
                elif pistafinal == 1:
                    ajuste += bonificacion * (1+(abs(diff)//200)/10 if diff < 0 else 1)
                elif pistafinal == 2:
                    ajuste += bonificacion*0.5


            new_elo += round(ajuste)
            new_ratings_pareja.append(new_elo)
            
        new_ratings.append((new_ratings_pareja[0],new_ratings_pareja[1]))
        i += 1



    return new_ratings