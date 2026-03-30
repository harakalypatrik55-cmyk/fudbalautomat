import requests
from datetime import datetime, timedelta

# ==========================================
# 1. NASTAVENIA (Tvoj PRO kľúč)
# ==========================================
API_KEY = "e89867ce51msh51fbf753f35e2f0p171553jsn43cabb7c76b4"

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com"
}

URL_MATCHES = "https://free-api-live-football-data.p.rapidapi.com/football-get-matches-by-date"
URL_H2H = "https://free-api-live-football-data.p.rapidapi.com/football-get-h2h"

# ==========================================
# 2. ANALÝZA (Góly, Rohy, Karty) - Len pre DNES
# ==========================================
def analyzuj_dnesny_zapas(home_id, away_id):
    try:
        res = requests.get(URL_H2H, headers=HEADERS, params={
            "home_team_id": home_id,
            "away_team_id": away_id
        }, timeout=10)
        data = res.json().get('response', {}).get('h2h', [])

        if not data:
            return {"over25": 50, "rohy": "7.5+", "karty": "3.5+"}

        t_goals, t_corners, t_cards = 0, 0, 0
        pocet = len(data)

        for g in data:
            t_goals += (g.get('home_score', 0) + g.get('away_score', 0))
            t_corners += g.get('corners', 8.5)
            t_cards += g.get('yellow_cards', 3.5)

        avg_g = t_goals / pocet
        # Pravdepodobnosť Over 2.5
        prob = 85 if avg_g >= 3 else 70 if avg_g >= 2.5 else 55

        return {
            "over25": prob,
            "rohy": round(t_corners / pocet, 1),
            "karty": round(t_cards / pocet, 1)
        }
    except:
        return {"over25": 50, "rohy": "7.5+", "karty": "3.5+"}

# ==========================================
# 3. HLAVNÝ ENGINE (4 dni program, 1 deň analýza)
# ==========================================
def spustit_system():
    print("🤖 PATOV PRO ROBOT - FINÁLNA VERZIA")
    print("------------------------------------")
    
    for i in range(4):
        den = datetime.now() + timedelta(days=i)
        datum_api = den.strftime("%Y%m%d")
        datum_pekne = den.strftime("%d.%m.%Y")
        je_dnes = (i == 0)

        print(f"\n📅 Dátum: {datum_pekne} {'[ANALYZUJEM...]' if je_dnes else '[LEN PROGRAM]'}")

        try:
            res = requests.get(URL_MATCHES, headers=HEADERS, params={"date": datum_api})
            zápasy = res.json().get('response', {}).get('matches', [])[:10]

            if not zápasy:
                print("   Žiadne zápasy v ponuke.")
                continue

            for z in zápasy:
                tymy = f"{z['home']['name']} vs {z['away']['name']}"
                
                if je_dnes:
                    # DNES robíme plnú robotu
                    st = analyzuj_dnesny_zapas(z['home']['id'], z['away']['id'])
                    print(f"✅ {tymy} | G: {st['over25']}% | R: {st['rohy']} | K: {st['karty']}")
                else:
                    # Ostatné dni len stiahneme zoznam
                    cas = z.get('time', 'Neznámy čas')
                    print(f"⏳ {cas} - {tymy}")

        except Exception as e:
            print(f"❌ Chyba pri dni {datum_pekne}: {e}")

if __name__ == "__main__":
    spustit_system()
