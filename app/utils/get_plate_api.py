import requests

def get_plate(plate_number):
    url = "https://wdapi2.com.br/consulta/" + plate_number + "asdunuddfbf"

    response = requests.get(url)

    if response.status_code == 200:
        dados = response.json() 

        return dados

    else:
        return
    