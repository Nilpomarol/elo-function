import streamlit as st
import math

avg = 1500
rating1 = st.number_input("Enter the rating1 value: ", min_value=0, max_value=3000, value=1500)
ratign2 = st.number_input("Enter the rating2 value: ", min_value=0, max_value=3000, value=1500)
avg = st.number_input("Enter the avg value: ", min_value=0, max_value=3000, value=1500) 
inicial = st.number_input("Pista inicials: ", min_value=1, max_value=6, value=1)
final = st.number_input("Pista final: ", min_value=1, max_value=6, value=1)


gained = inicial - final 
americana_result = (gained / 5)/2+0.5
st.text(str(americana_result))
P = 1/ (1 + 1 * math.pow(10, 1 * (avg - rating1) / 800))
st.text(str(P))
new_elo = int(round(100 * (americana_result - P)))
if new_elo >= 0:
    elodiff = rating1 - avg
    if elodiff < -200:
        new_elo += 20
    elif elodiff < -100:
        new_elo += 15
    else:
        new_elo += 10
        
st.text(str(new_elo))