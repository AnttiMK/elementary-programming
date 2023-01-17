import math
import sys
import getopt
import haravasto
import laatikosto

IKKUNAN_LEVEYS = 1200
IKKUNAN_KORKEUS = 1200
PUTOAMISKIIHTYVYYS = 1.5
SATUNNAISET_LAATIKOT = 15

# Sorsan oletusasetukset ritsassa
SORSA_X = 60
SORSA_Y = 80
SORSA_H = 40
SORSA_W = 40

# Mahdolliset pelitilat:
# 0 = peli käynnissä
# 1 = voitto
# 2 = häviö
peli = {
    "tila": 0,
    "taso": 0,
    "laatikot": 0,
    "sorsia_jaljella": 0,
    "nyk_sorsa": 0,
    "sorsat": [],
    "tasot": []
}

def alkutila():
    """
    Asettaa pelin "alkutilaan" jokaisen sorsan ampumisen jälkeen.
    """
    sorsat = peli["sorsat"]
    tasot = peli["tasot"]
    nyk_taso = tasot[peli["taso"]]
    sorsa = sorsat[peli["nyk_sorsa"]]

    sorsa["ammuttu"] = True
    peli["sorsia_jaljella"] -= 1

    laatikot = nyk_taso["laatikot"]

    if peli["sorsia_jaljella"] > 0:
        if len(laatikot) == 0:
            if len(tasot) > peli["taso"] + 1:
                peli["taso"] += 1
                peli["sorsia_jaljella"] = nyk_taso["sorsat"]
                peli["nyk_sorsa"] = 0
                peli["sorsat"] = generoi_sorsat(nyk_taso["sorsat"])
                peli["sorsat"][0]["x"] = SORSA_X
                peli["sorsat"][0]["y"] = SORSA_Y
            else:
                peli["tila"] = 1
        else:
            peli["nyk_sorsa"] += 1
            sorsa = sorsat[peli["nyk_sorsa"]]
            sorsa["x"] = SORSA_X
            sorsa["y"] = SORSA_Y
    else:
        if len(laatikot) > 0:
            peli["tila"] = 2
            peli["sorsia_jaljella"] = nyk_taso["sorsat"]
            peli["nyk_sorsa"] = 0
            peli["sorsat"] = generoi_sorsat(nyk_taso["sorsat"])
            peli["sorsat"][0]["x"] = SORSA_X
            peli["sorsat"][0]["y"] = SORSA_Y
        else:
            peli["tila"] = 1
            if len(tasot) > peli["taso"] + 1:
                peli["tila"] = 0
                peli["taso"] += 1
                peli["sorsia_jaljella"] = nyk_taso["sorsat"]
                peli["nyk_sorsa"] = 0
                peli["sorsat"] = generoi_sorsat(nyk_taso["sorsat"])
                peli["sorsat"][0]["x"] = SORSA_X
                peli["sorsat"][0]["y"] = SORSA_Y

def generoi_sorsat(maara):
    """
    Generoi sorsat tasolle.
    """
    sorsalista = []
    for i in range(maara):
        sorsa = {
            "x": 100 + i * 80,
            "y": IKKUNAN_KORKEUS - 100,
            "x_nopeus": 0,
            "y_nopeus": 0,
            "lennossa": False,
            "ammuttu": False,
            "raahataan": False,
        }
        sorsalista.append(sorsa)
    return sorsalista

def piirra():
    """
    Huolehtii pelin piirtämisestä.
    """
    sorsat = peli["sorsat"]
    tasot = peli["tasot"]

    haravasto.tyhjaa_ikkuna()
    haravasto.piirra_tausta()
    haravasto.aloita_ruutujen_piirto()
    haravasto.lisaa_piirrettava_ruutu("ritsa", 40, 0)

    for sorsa in sorsat:
        haravasto.lisaa_piirrettava_ruutu("sorsa", sorsa["x"], sorsa["y"])
    for laatikko in tasot[peli["taso"]]["laatikot"]:
        haravasto.lisaa_piirrettava_ruutu("x", laatikko["x"], laatikko["y"])

    haravasto.piirra_ruudut()
    haravasto.piirra_tekstia(
        f"Sorsia jäljellä: {peli['sorsia_jaljella']}",
        800, IKKUNAN_KORKEUS - 300, koko=22
    )
    
    haravasto.piirra_tekstia(
        f"Taso: {peli['taso'] + 1} / {len(tasot)}",
        800, IKKUNAN_KORKEUS - 200, koko=22
    )

    if peli["tila"] == 1:
        haravasto.piirra_tekstia("Voitit!", 600, 600, koko=30)
        haravasto.piirra_tekstia("Klikkaa hiirellä pelataksesi lisää.", 500, 550, koko=20)
    elif peli["tila"] == 2:
        haravasto.piirra_tekstia("Hävisit! Yritä uudelleen.", 400, 600, koko=30)

def paivita(kulunut_aika):
    """
    Päivityskäsittelijä.
    """
    sorsat = peli["sorsat"]
    tasot = peli["tasot"]

    sorsa = sorsat[peli["nyk_sorsa"]]
    laatikot = tasot[peli["taso"]]["laatikot"]
    laatikosto.pudota(laatikot)
    if not sorsa["lennossa"] or sorsa["ammuttu"]:
        return

    for ammuttu_sorsa in sorsat:
        if not ammuttu_sorsa["ammuttu"]:
            continue
        for laatikko in laatikot:
            if testaa_osuma(ammuttu_sorsa, laatikko):
                laatikot.remove(laatikko)

    if sorsa["lennossa"] and not sorsa["ammuttu"]:
        sorsa["x"] += sorsa["x_nopeus"]
        sorsa["y"] += sorsa["y_nopeus"]

        for laatikko in laatikot:
            if testaa_osuma(sorsa, laatikko):
                laatikot.remove(laatikko)
                sorsa["x_nopeus"] = 0
                sorsa["y_nopeus"] = 0
                alkutila()
                return
                
        sorsa["y_nopeus"] -= 1.5
        if sorsa["y"] <= 0:
            alkutila()

    

def kasittele_klikkaus(x, y, nappi, muokkausnapit):
    """
    Käsittelijä hiiren klikkauksille.
    """
    sorsat = peli["sorsat"]
    tasot = peli["tasot"]

    sorsa = sorsat[peli["nyk_sorsa"]]
    if ((sorsa["x"] < x < sorsa["x"] + SORSA_W) and (sorsa["y"] < y < sorsa["y"] + SORSA_H)):
        sorsa["raahataan"] = True
    
    if peli["tila"] == 2:
        peli["tila"] = 0

    if peli["tila"] == 1:
        peli["tila"] = 0
        sorsa_maara = SATUNNAISET_LAATIKOT + 2

        taso = {
            "sorsat": sorsa_maara,
            "laatikot": laatikosto.luo_laatikot(SATUNNAISET_LAATIKOT, 200)
        }
        tasot.append(taso)
        peli["sorsat"] = generoi_sorsat(sorsa_maara)
        peli["taso"] += 1
        peli["sorsia_jaljella"] = sorsa_maara
        peli["nyk_sorsa"] = 0
        sorsat[0]["x"] = SORSA_X
        sorsat[0]["y"] = SORSA_Y
        

def kasittele_raahaus(x, y, dist_x, dist_y, nappi, muokkausnapit):
    """
    Tätä funktiota kutsutaan kun käyttäjä liikuttaa hiirtä jonkin painikkeen
    ollessa painettuna. Siirtää ruudulla olevaa laatikkoa saman verran kuin kursori
    liikkui.
    """
    sorsat = peli["sorsat"]

    sorsa = sorsat[peli["nyk_sorsa"]]
    if sorsa["raahataan"] is True:
        sorsa["x"] += dist_x
        sorsa["y"] += dist_y


def kasittele_vapautus(x, y, nappi, muokkausnapit):
    """
    Funktio käsittelee hiiren napin vapautuksen, eli tässä tapauksessa jos sorsaa on
    raahattu, laskee sorsalle kulman ja voiman, ja päästää sorsan liikkelle.
    """
    sorsat = peli["sorsat"]

    sorsa = sorsat[peli["nyk_sorsa"]]
    if sorsa["raahataan"] is True:
        sorsa["raahataan"] = False

        voima = math.dist([SORSA_X, SORSA_Y], [sorsa["x"], sorsa["y"]]) / 2
        d_x = SORSA_X - sorsa["x"]
        d_y = SORSA_Y - sorsa["y"]
        kulma = math.atan2(d_y, d_x)

        sorsa["x_nopeus"] = voima * math.cos(kulma)
        sorsa["y_nopeus"] = voima * math.sin(kulma)
        sorsa["lennossa"] = True

def testaa_osuma(sorsa, laatikko):
    """
    Laskee kappaleiden välisen etäisyyden ja palauttaa totuusarvona osuivatko ne toisiinsa.
    """
    s_x, s_y = sorsa["x"], sorsa["y"]
    s_mx, s_my = s_x + SORSA_W, s_x + SORSA_H
    l_x, l_y = laatikko["x"], laatikko["y"]
    l_mx, l_my = l_x + laatikko["w"], l_y + laatikko["h"]

    if s_x < l_x < s_mx or s_x < l_mx < s_mx:
        if s_y < l_y < s_my or s_y < l_my < s_my:
            return True
    return False

def lataa_tasot(tiedosto):
    """
    Lataa tasot tekstitiedostosta. Yksi rivi tiedostossa vastaa yhtä tasoa.
    Rivi on muotoa:
    sorsien_lkm;x,y,w,h,vy;x,y,...
    Käytännössä tämä tarkoittaa, että ensimmäinen numero on tason sorsien lukumäärä,
    ja sen jälkeen tulevat laatikot muodossa x, y, w, h ja vy. 
    Jokainen laatikko ja sorsien lukumäärä erotellaan toisistaan puolipisteellä.
    """
    sorsat = peli["sorsat"]
    tasot = peli["tasot"]

    try:
        with open(tiedosto, encoding="utf-8") as lahde:
            for i, rivi in enumerate(lahde):
                laatikot = rivi.strip().split(";")
                for j, laatikko in enumerate(laatikot):
                    if j == 0:
                        tasot.append({
                            "sorsat": int(laatikko),
                            "laatikot": []
                        })

                        if i == 0:
                            for k in range(int(laatikko)):
                                sorsat.append({
                                    "x": 100 + k * 80,
                                    "y": IKKUNAN_KORKEUS - 100,
                                    "x_nopeus": 0,
                                    "y_nopeus": 0,
                                    "lennossa": False,
                                    "raahataan": False,
                                    "ammuttu": False
                                })
                    else:
                        x, y, l_w, l_h, l_vy = laatikko.split(",")
                        tasot[i]["laatikot"].append({
                            "x": int(x),
                            "y": int(y),
                            "w": int(l_w),
                            "h": int(l_h),
                            "vy": int(l_vy)
                        })

        peli["taso"] = 0
        peli["sorsia_jaljella"] = tasot[0]["sorsat"]
    except IOError:
        print(f"Tiedoston {tiedosto} lukeminen epäonnistui.")
        sys.exit(2)


def main(argv):
    """
    Komentoriviargumenttien hakeminen lainattu osoitteesta
    https://www.tutorialspoint.com/python/python_command_line_arguments.htm
    """
    sorsat = peli["sorsat"]
    tasot = peli["tasot"]

    # Mahdolliset tasotyypit: 
    # 0 = generoitu
    # 1 = tiedostosta
    tasotyyppi = 0

    try:
        opts, _ = getopt.getopt(argv, "t:", ["tiedosto="])
    except getopt.GetoptError:
        print("sorsapeli.py -t <tiedosto>")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-t", "--tiedosto"):
            tasotyyppi = 1
            lataa_tasot(arg)
    
    if tasotyyppi == 0:
        sorsa_maara = SATUNNAISET_LAATIKOT + 2
        taso = {
            "sorsat": sorsa_maara,
            "laatikot": laatikosto.luo_laatikot(SATUNNAISET_LAATIKOT, 200)
        }
        tasot.append(taso)
        for i in range(sorsa_maara):
            sorsat.append({
                "x": 100 + i * 80,
                "y": IKKUNAN_KORKEUS - 100,
                "x_nopeus": 0,
                "y_nopeus": 0,
                "lennossa": False,
                "raahataan": False,
                "ammuttu": False
            })
        peli["sorsia_jaljella"] = sorsa_maara

    sorsat[0]["x"] = SORSA_X
    sorsat[0]["y"] = SORSA_Y
    haravasto.lataa_kuvat("spritet")
    haravasto.lataa_sorsa("spritet")
    haravasto.luo_ikkuna(leveys=IKKUNAN_LEVEYS, korkeus=IKKUNAN_KORKEUS)
    haravasto.aseta_piirto_kasittelija(piirra)
    haravasto.aseta_toistuva_kasittelija(paivita, 1/60)
    haravasto.aseta_hiiri_kasittelija(kasittele_klikkaus)
    haravasto.aseta_raahaus_kasittelija(kasittele_raahaus)
    haravasto.aseta_vapautus_kasittelija(kasittele_vapautus)
    haravasto.aloita()

if __name__ == "__main__":
    main(sys.argv[1:])
