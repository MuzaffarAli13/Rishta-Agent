import pandas as pd
import requests
from io import StringIO
from agents import function_tool

@function_tool
def get_user_data_from_sheet(user_age: str, user_gender: str) -> list:
    """
    Fetches user profile data from a public Google Sheet (CSV format) and returns a list of users 
    whose age is greater than or equal to the specified minimum age 
    and whose gender is opposite to the specified gender.
    """    
    
    sheet_url = "https://docs.google.com/spreadsheets/d/1Rr3EQZa8iUZ11Z_j-GW0Qui3WE-FRXj_GaoUxnB_35o/export?format=csv&gid=66214557"    
    response = requests.get(sheet_url)
    if response.status_code != 200:
        return []    
    
    df = pd.read_csv(StringIO(response.text))

    opposite_gender = "female" if user_gender.lower() == "male" else "Male"

    # Filter age & gender
    matched = df[
        (df["age"] >= int(user_age)) & 
        (df["gender"].str.lower() == opposite_gender.lower())
    ].to_dict(orient="records")
    
    return matched
