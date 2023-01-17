from random import randint
from sorsapeli import PUTOAMISKIIHTYVYYS
from sorsapeli import IKKUNAN_KORKEUS
from sorsapeli import IKKUNAN_LEVEYS

def luo_laatikot(maara, raja):
    """
    Luo halutun määrän laatikoita ja asettaa ne satunnaisiin kohtiin määritetyn
    alueen sisälle. Laatikot esitetään sanakirjoilla joissa on seuraavat avaimet:
    x: vasemman alakulman x-koordinaatti
    y: vasemman alakulman y-koordinaatti
    w: laatikon leveys
    h: laatikon korkeus
    vy: laatikon putoamisnopeus
    """
    laatikot = []
    for _ in range(maara):
        laatikko = {
            "x": randint(200, IKKUNAN_LEVEYS - 40),
            "y": randint(raja, IKKUNAN_KORKEUS - 40),
            "w": 40,
            "h": 40,
            "vy": 0
        }
        laatikot.append(laatikko)
    return laatikot

def pudota(laatikot):
    """
    Pudottaa annetussa listassa olevia neliskanttisia objekteja (määritelty
    sanakirjana jossa vasemman alakulman x, y -koordinaatit, leveys, korkeus sekä
    nopeus pystysuuntaan). Funktio pudottaa laatikoita yhtä aikayksikköä
    vastaavan matkan.
    """
    laatikot_sorted = sorted(laatikot, key=lambda i: i['y'])

    for idx, laatikko in enumerate(laatikot_sorted):
        if laatikko["y"] <= 0:
            continue

        # Tarkistetaan, voidaanko käsiteltävä laatikko pudottaa.
        # Jos ei, siirrytään seuraavaan laatikkoon.
        droppable = True
        for i in range(idx - 1, -1, -1):
            current = laatikot_sorted[i]

            l_x = laatikko["x"]
            l_y = laatikko["y"]
            l_max_x = l_x + laatikko["w"]
            l_max_y = l_y + laatikko["h"]

            c_x = current["x"]
            c_y = current["y"]
            c_max_x = c_x + current["w"]
            c_max_y = c_y + current["h"]

            if (c_x < l_max_x <= c_max_x) or (c_x <= l_x < c_max_x) or (l_x < c_x and l_max_x > c_max_x):
                if (c_y < l_max_y <= c_max_y) or (c_y <= l_y < c_max_y) or (l_y < c_y and l_max_y > c_max_y):
                    laatikko["y"] = c_max_y
                    droppable = False
                    break
        if not droppable:
            continue

        # Tarkistetaan, putoaisiko käsiteltävä laatikko alla
        # olevan laatikon sisään. Jos putoaisi, pudotetaan laatikko
        # kyseisen laatikon yläreunaan ja siirrytään seuraavaan.
        for i in range(idx - 1, -1, -1):
            current = laatikot_sorted[i]

            l_x = laatikko["x"]
            l_y = laatikko["y"] - (laatikko["vy"] + PUTOAMISKIIHTYVYYS)
            l_max_x = l_x + laatikko["w"]
            l_max_y = l_y + laatikko["h"]

            c_x = current["x"]
            c_y = current["y"]
            c_max_x = c_x + current["w"]
            c_max_y = c_y + current["h"]

            if (c_x < l_max_x <= c_max_x) or (c_x <= l_x < c_max_x) or (l_x < c_x and l_max_x > c_max_x):
                if (c_y < l_max_y <= c_max_y) or (c_y <= l_y < c_max_y) or (l_y < c_y and l_max_y > c_max_y):
                    laatikko["y"] = c_max_y
                    droppable = False
                    break
        if not droppable:
            continue

        laatikko["vy"] += PUTOAMISKIIHTYVYYS
        laatikko["y"] -= laatikko["vy"]

        if laatikko["y"] < 0:
            laatikko["y"] = 0
            continue
