import requests, time, base64, sys, json

#('-----------------------------------------------------')
#('--- PureCloud Python Conversation Detail Record -----')
#('-----------------------------------------------------')

#Funcion para generar el token
def generarToken():
    # Prepare post token request
    client_auth = config['client_id'] + ":" + config['client_secret']

    tokenHeader = {
        'Authorization': 'Basic ' + base64.b64encode(client_auth.encode()).decode(),
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    tokenBody = {'grant_type': 'client_credentials'}

    token = requests.post('https://login.' + config['environment'] + '/token', data=tokenBody, headers=tokenHeader)

    # Check response
    if token.status_code == 200:
        print('Token success! ' + str(token.status_code) + ' ' + str(token.reason) + ' ' + tiempo.strftime(format))
    else:
        print('Error al generar token ' + str(token.status_code) + ' ' + str(token.reason) + ' ' + tiempo.strftime(format))
        sys.exit()

    # Get JSON response body
    tokenJson = token.json()
    return tokenJson

#Funcion para conseguir el nombre de las colas
def GetQueueIdMap():
    queue_id_map = {}
    done = False
    page_number = 1
    while not done:
        queues = requests.get(
            'https://api.' + config['environment'] + '/api/v2/routing/queues?pageSize=100&pageNumber=' + str(page_number),headers=requestHeaders)
        print('Got queues page {0} of {1}'.format(page_number, queues.json()['pageCount']))
        for q in queues.json()['entities']:
            queue_id_map[q['id']] = q
        done = (page_number >= queues.json()['pageCount'])
        page_number += 1
    print('Queues found:', len(queue_id_map))
    return queue_id_map

#Abrir y guardar el Json de configuracion
with open('configuration.json') as config_file:
    config = json.load(config_file)

# Formato fecha y guardo variable de fecha y hora actual
format = "%Y-%m-%dT%H:%M:%S"
tiempo = time

#Generar el token
tokenHeader = generarToken()

requestHeaders = {
    'Content-Type': 'application/json',
    'Authorization': tokenHeader['token_type'] + ' ' + tokenHeader['access_token']
}

queue_id_map = GetQueueIdMap()

#Abrir y guardar el Json de configuracion
with open('query.json') as query_file:
    query = json.load(query_file)



detailsTotal = {}
listConversations = []
done = False
query['paging']['pageNumber'] = 1
count = 1
while not done:
    details = requests.post('https://api.' + config['environment'] + '/api/v2/analytics/conversations/details/query',json=query, headers=requestHeaders)
    # Check response
    if details.status_code == 200:
        if details.json() != {}:
            print('Got {} conversations of page {}'.format(len(details.json()['conversations']), query['paging']['pageNumber']))
            for c in details.json()['conversations']:
                listConversations.append(c)
            query['paging']['pageNumber'] += 1
            if len(details.json()['conversations']) < query['paging']['pageSize']:
                done = True
        else:
            done = True
    elif details.status_code == 504:
        if count >= 10:
            print('Query details 10s timeout! ' + tiempo.strftime(format))
            sys.exit()
        else:
            count += 1
    else:
        print('Query details error ' + str(details.status_code) + ' ' + str(details.reason) + ' ' + tiempo.strftime(format))
        sys.exit()

print(len(listConversations))



