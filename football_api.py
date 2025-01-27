import requests
from datetime import datetime
import json


API_KEY = '3f66fc3d1b2e46cea12968d0def3b713'
BASE_URL = 'https://api.football-data.org/v4'



headers = {
    'X-Auth-Token': API_KEY
}

def get_champions_matches():
    response = requests.get(f'{BASE_URL}/competitions/CL/matches', headers=headers)
    return response.json()

def get_team_stats(team_id):
    response = requests.get(f'{BASE_URL}/teams/{team_id}', headers=headers)
    return response.json()

def get_formatted_matches():
    matches = get_champions_matches()
    formatted_matches = []
    for match in matches['matches']:
        formatted_matches.append({
            'id': match['id'],
            'homeTeam': match['homeTeam']['name'],
            'awayTeam': match['awayTeam']['name'],
            'date': match['utcDate'],
            'status': match['status'],
            'score': match.get('score', {})
        })
    return formatted_matches

def get_upcoming_matches():
    matches = get_champions_matches()
    now = datetime.utcnow()
    
    future_matches = [
        match for match in matches.get('matches', [])
        if match['status'] in ['SCHEDULED', 'TIMED']
    ]
    
    return [{
        'date': match['utcDate'],
        'homeTeam': {
            'name': match['homeTeam'].get('name', '-')
        },
        'awayTeam': {
            'name': match['awayTeam'].get('name', '-')
        }
    } for match in future_matches[:5]]

def get_team_matches(search_team):
    try:
        matches = get_champions_matches()
        team_matches = []
        
        for match in matches.get('matches', []):
            home_team = match.get('homeTeam', {}).get('name', '')
            away_team = match.get('awayTeam', {}).get('name', '')
            
            if (home_team and away_team and 
                (search_team.lower() in home_team.lower() or 
                 search_team.lower() in away_team.lower())):
                
                team_matches.append({
                    'date': match.get('utcDate'),
                    'homeTeam': home_team,
                    'awayTeam': away_team,
                    'status': match.get('status'),
                    'competition': match.get('competition', {}).get('name', ''),
                    'score': match.get('score', {}).get('fullTime', {})
                })
        
        return team_matches
    except Exception as e:
        print(f"Error: {e}")
        return []
    
def get_available_teams():
    matches = get_champions_matches()
    teams = set()
    
    for match in matches.get('matches', []):
        home = match.get('homeTeam', {}).get('name')
        away = match.get('awayTeam', {}).get('name')
        if home: teams.add(home)
        if away: teams.add(away)
    
    # Obtener puntos desde la API de standings
    standings_url = f'{BASE_URL}/competitions/CL/standings'
    response = requests.get(standings_url, headers=headers)
    
    team_points = {}
    if response.status_code == 200:
        standings = response.json()
        team_points = {
            team['team']['name']: team['points'] 
            for team in standings['standings'][0]['table']
        }
    
    return [
        {
            "name": team,
            "points": team_points.get(team, 0)
        } for team in teams
    ]

# def get_match_prediction(home_team, away_team):
#     try:
#         print(f"Calculando predicción para {home_team} vs {away_team}")
#         stats = get_team_detailed_stats(home_team)
#         away_stats = get_team_detailed_stats(away_team)
        
#         model = genai.GenerativeModel('gemini-1.0-pro')
#         prompt = f"""
#         {home_team}: Jugados:{stats['played']}, Victorias:{stats['wins']}, GF:{stats['goals_scored']}, GC:{stats['goals_against']}, Forma:{' '.join(stats['form'])}
#         {away_team}: Jugados:{away_stats['played']}, Victorias:{away_stats['wins']}, GF:{away_stats['goals_scored']}, GC:{away_stats['goals_against']}, Forma:{' '.join(away_stats['form'])}
        
#         Analiza estos datos y devuelve un JSON con: probabilidad victoria local (%), probabilidad victoria visitante (%), resultado más probable
#         """
        
#         response = model.generate_content(prompt)
#         prediction_data = response.text  # Asegúrate de que esto sea un JSON válido
        
#         # Validar que prediction_data sea un JSON
#         try:
#             prediction_json = json.loads(prediction_data)
#             return prediction_json
#         except json.JSONDecodeError:
#             return {"error": "La respuesta del modelo no es un JSON válido."}
        
#     except Exception as e:
#         return {"error": f"Ocurrió un error: {str(e)}"}

def predict_match(home_team, away_team):
    home_stats = get_team_detailed_stats(home_team)
    away_stats = get_team_detailed_stats(away_team)

    # Calcular la probabilidad de victoria
    home_win_probability = (home_stats['wins'] / max(home_stats['played'], 1)) * 100
    away_win_probability = (away_stats['wins'] / max(away_stats['played'], 1)) * 100

    # Ajustar las probabilidades según los goles anotados y recibidos
    home_goal_difference = home_stats['goals_scored'] - home_stats['goals_against']
    away_goal_difference = away_stats['goals_scored'] - away_stats['goals_against']

    # Sumar las diferencias de goles a las probabilidades
    home_win_probability += home_goal_difference
    away_win_probability += away_goal_difference

    # Normalizar las probabilidades
    total_probability = home_win_probability + away_win_probability
    if total_probability > 0:
        home_win_probability = max(0, (home_win_probability / total_probability) * 100)
        away_win_probability = max(0, (away_win_probability / total_probability) * 100)
    else:
        home_win_probability = 50
        away_win_probability = 50

    # Resultado más probable
    predicted_result = "Empate"
    if home_win_probability > away_win_probability:
        predicted_result = "Victoria local"
    elif away_win_probability > home_win_probability:
        predicted_result = "Victoria visitante"

    return {
        "probabilidad_victoria_local": round(home_win_probability, 2),
        "probabilidad_victoria_visitante": round(away_win_probability, 2),
        "resultado_predicho": predicted_result
    }


def get_future_matches():
    matches = get_champions_matches()
    now = datetime.utcnow()
    
    future_matches = [
        match for match in matches.get('matches', [])
        if datetime.fromisoformat(match['utcDate'].replace('Z', '+00:00')) > now
    ]
    
    return [{
        'date': match['utcDate'],
        'homeTeam': match['homeTeam']['name'],
        'awayTeam': match['awayTeam']['name'],
        'competition': match['competition']['name']
    } for match in future_matches]

def get_team_standings(league_code='CL'):  # Por defecto Premier League
    standings_url = f'{BASE_URL}/competitions/{league_code}/standings'
    response = requests.get(standings_url, headers=headers)
    
    if response.status_code == 200:
        standings = response.json()
        return [
            {
                "id": team['team']['id'],
                "name": team['team']['name'],
                "points": team['points'],
                "position": team['position']
            } for team in standings['standings'][0]['table']
        ]
    return []

def get_team_detailed_stats(team_name):
    matches = get_champions_matches()
    stats = {
        'played': 0,
        'wins': 0,
        'draws': 0,
        'losses': 0,
        'goals_scored': 0,
        'goals_against': 0,
        'form': []
    }

    for match in matches.get('matches', []):
        if match['status'] != 'FINISHED':
            continue
            
        score = match.get('score', {}).get('fullTime', {})
        is_home = match.get('homeTeam', {}).get('name', '').strip() == team_name.strip()
        is_away = match.get('awayTeam', {}).get('name', '').strip() == team_name.strip()
        
        if not (is_home or is_away) or not score:
            continue

        stats['played'] += 1
        home_score = score.get('home', 0)
        away_score = score.get('away', 0)

        # Agregar logs para verificar los datos
        print(f"Partido: {match['homeTeam']['name']} vs {match['awayTeam']['name']}, Score: {home_score}-{away_score}")

        if is_home:
            stats['goals_scored'] += home_score
            stats['goals_against'] += away_score
            if home_score > away_score:
                stats['wins'] += 1
                stats['form'].append('W')
            elif home_score < away_score:
                stats['losses'] += 1
                stats['form'].append('L')
            else:
                stats['draws'] += 1
                stats['form'].append('D')
        else:
            stats['goals_scored'] += away_score
            stats['goals_against'] += home_score
            if away_score > home_score:
                stats['wins'] += 1
                stats['form'].append('W')
            elif away_score < home_score:
                stats['losses'] += 1
                stats['form'].append('L')
            else:
                stats['draws'] += 1
                stats['form'].append('D')

    stats['form'] = stats['form'][-5:]  # últimos 5 partidos
    stats['win_rate'] = round((stats['wins'] / max(stats['played'], 1)) * 100, 2)
    
    return stats
