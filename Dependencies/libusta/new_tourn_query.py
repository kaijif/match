import requests
import pandas as pd


def query_tourn(site):
    id = site.split('/')[-1]
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:108.0) Gecko/20100101 Firefox/108.0",
        "Accept" : "*/*",
        "Accept-Language": "en-US,en.q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://playtennis.usta.com/",
        "content-type": "application/json",
        "Content-Length": "513",
        "Origin": "https://playtennis.usta.com",
        "DNT": "1",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "TE": "trailers",
        }
    player_post_json = '{"operationName":"TournamentPlayers","variables":{"tournamentId":"' + id + '"},"query":"query TournamentPlayers($tournamentId: ID!) {  tournamentParticipants(tournamentId: $tournamentId)}"}'
    player_request = requests.post('https://prd-usta-kube-tournamentdesk-public-api.clubspark.pro/', data=player_post_json, headers=headers)
    name_post_json = '{"operationName":"GetTournament","variables":{"id":"' + id + '","previewMode":false},"query":"query GetTournament($id: UUID!, $previewMode: Boolean) {\n  publishedTournament(id: $id, previewMode: $previewMode) {\n    id\n    featureSettings {\n      enabled\n      featureId\n      overridable\n      __typename\n    }\n    commsSettings {\n      emailReplyTo\n      phoneNumber\n      __typename\n    }\n    sanctionStatus\n    name\n    isPublished\n    selectionsPublished\n    tournamentFee\n    identificationCode\n    finalisedAndCharged\n    tournamentFeePayment {\n      status\n      tournamentFee\n      latestChargeTimestamp\n      __typename\n    }\n    organisation {\n      id\n      name\n      __typename\n    }\n    registrationRestrictions {\n      entriesCloseDate\n      entriesOpenDate\n      entriesCloseTime\n      entriesOpenTime\n      timeZone\n      entriesCloseDateTime\n      entriesOpenDateTime\n      secondsUntilEntriesClose\n      secondsUntilEntriesOpen\n      maxEventEntriesPerUser\n      maxSinglesEntriesPerUser\n      maxDoublesEntriesPerUser\n      singleAgeGroupPerPlayer\n      __typename\n    }\n    director {\n      id\n      firstName\n      lastName\n      __typename\n    }\n    officials(officialType: REFEREE) {\n      officialType\n      status\n      commsSettings {\n        emailReplyTo\n        __typename\n      }\n      contact {\n        id\n        firstName\n        lastName\n        userId\n        __typename\n      }\n      __typename\n    }\n    websiteContent {\n      logoPath\n      photoPath\n      tournamentDetails\n      aboutTheOrganiser\n      entryInformation\n      hideDraws\n      hidePlayerList\n      __typename\n    }\n    lastSanctionStatusChange(sanctionStatus: SUBMITTED) {\n      createdAt\n      createdByFirstName\n      createdByLastName\n      __typename\n    }\n    primaryLocation {\n      id\n      name\n      address1\n      address2\n      address3\n      country\n      county\n      latitude\n      longitude\n      postcode\n      town\n      __typename\n    }\n    timings {\n      startDate\n      endDate\n      timeZone\n      startDateTime\n      __typename\n    }\n    level {\n      __typename\n      branding\n      id\n      name\n      category\n      orderIndex\n      shortName\n    }\n    onlineRegistrationEnabled\n    publishedEvents(previewMode: $previewMode) {\n      id\n      sanctionStatus\n      courtLocation\n      sanctionStatus\n      isPublished\n      formatConfiguration {\n        entriesLimit\n        ballColour\n        drawSize\n        eventFormat\n        scoreFormat\n        selectionProcess\n        __typename\n      }\n      level {\n        __typename\n        id\n        name\n        category\n        orderIndex\n        shortName\n      }\n      division {\n        __typename\n        ballColour\n        ageCategory {\n          __typename\n          minimumAge\n          maximumAge\n          todsCode\n          type\n        }\n        eventType\n        gender\n        wheelchairRating\n        familyType\n        ratingCategory {\n          __typename\n          ratingCategoryType\n          ratingType\n          value\n          minimumValue\n          maximumValue\n        }\n      }\n      pricing {\n        entryFee {\n          amount\n          currency\n          __typename\n        }\n        __typename\n      }\n      registrations {\n        id\n        player {\n          customId {\n            key\n            value\n            __typename\n          }\n          firstName\n          lastName\n          name\n          gender\n          __typename\n        }\n        registrationDate\n        selectionIndex\n        selectionStatus\n        __typename\n      }\n      surface\n      timings {\n        startDateTime\n        __typename\n      }\n      tournament {\n        id\n        registrationRestrictions {\n          entriesCloseDateTime\n          __typename\n        }\n        levelConfiguration {\n          skillLevel\n          __typename\n        }\n        __typename\n      }\n      withdrawals {\n        player {\n          customId {\n            key\n            value\n            __typename\n          }\n          customIds {\n            key\n            value\n            __typename\n          }\n          firstName\n          lastName\n          name\n          gender\n          __typename\n        }\n        registrationDate\n        __typename\n      }\n      teamEventConfiguration {\n        isDominantDuo\n        maximumTeams\n        eventFormat\n        selectionProcess\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"}'
    name_request = requests.post('https://prd-usta-kube-tournaments.clubspark.pro/', data=name_post_json, headers=headers)
    out = pd.DataFrame()
    tourn_name = name_request.json()['data']['publishedTournament']['name']
    #pass 1, get events
    event_ids = []
    for participant in player_request.json()['data']['tournamentParticipants']:
        for event in participant['events']:
            event_ids.append(event['eventId']) 
    event_ids = list(set(event_ids))
    event_map = {}
    for event_id in event_ids:
        event_data_json = '{"operationName":"TournamentPublicEventData","variables":{"eventId":"' + event_id + '","tournamentId":"CE657375-B3DD-4381-B216-E8AC84F1C6CD"},"query":"query TournamentPublicEventData($eventId: ID!, $tournamentId: ID!) {  tournamentPublicEventData(eventId: $eventId, tournamentId: $tournamentId)}"}'
        r = requests.post('https://prd-usta-kube-tournamentdesk-public-api.clubspark.pro/', data=event_data_json, headers=headers)
        event_map.update({ r.json()['data']['tournamentPublicEventData']['eventData']['eventInfo']['eventName']: event_id})
    for division in event_map.keys():
        for player in player_request.json()['data']['tournamentParticipants']:
            for event in player['events']:
                    if event_map[division] == event['eventId']:
                        name = player['person']['standardGivenName'] + ' ' + player['person']['standardFamilyName']
                        gender =  player['person']['sex']
                        player_info = pd.DataFrame([name, division, gender]).transpose()
                        out = pd.concat([out, player_info])
    out.columns = ['Player name', 'Events', 'Gender']
    out['index'] = [num for num in range(1, len(out.index) + 1)]
    out = out.set_index('index')
    return out, tourn_name


if __name__ == '__main__':
    print(query_tourn("https://playtennis.usta.com/Competitions/virginiabeachtennisandcountryclub/Tournaments/draws/CE657375-B3DD-4381-B216-E8AC84F1C6CD"))
