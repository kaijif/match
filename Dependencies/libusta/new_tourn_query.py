import requests
import pandas as pd


def query_tourn(site):
    id = site.split('/')[-1]
    post_json = '{"operationName":"GetTournament","variables":{"id":"' + id + '","previewMode":false},"query":"query GetTournament($id: UUID!, $previewMode: Boolean) {\n  publishedTournament(id: $id, previewMode: $previewMode) {\n    id\n    sanctionStatus\n    name\n    isPublished\n    selectionsPublished\n    tournamentFee\n    identificationCode\n    finalisedAndCharged\n    tournamentFeePayment {\n      status\n      tournamentFee\n      latestChargeTimestamp\n      __typename\n    }\n    organisation {\n      id\n      name\n      __typename\n    }\n    registrationRestrictions {\n      entriesCloseDate\n      entriesOpenDate\n      entriesCloseTime\n      entriesOpenTime\n      timeZone\n      entriesCloseDateTime\n      entriesOpenDateTime\n      secondsUntilEntriesClose\n      secondsUntilEntriesOpen\n      maxEventEntriesPerUser\n      maxSinglesEntriesPerUser\n      maxDoublesEntriesPerUser\n      singleAgeGroupPerPlayer\n      __typename\n    }\n    director {\n      id\n      firstName\n      lastName\n      emailAddress\n      phoneNumber\n      mobileNumber\n      __typename\n    }\n    websiteContent {\n      logoPath\n      photoPath\n      tournamentDetails\n      aboutTheOrganiser\n      entryInformation\n      hideDraws\n      hidePlayerList\n      __typename\n    }\n    lastSanctionStatusChange(sanctionStatus: SUBMITTED) {\n      createdAt\n      createdByFirstName\n      createdByLastName\n      __typename\n    }\n    primaryLocation {\n      id\n      name\n      address1\n      address2\n      address3\n      country\n      county\n      latitude\n      longitude\n      postcode\n      town\n      __typename\n    }\n    timings {\n      startDate\n      endDate\n      timeZone\n      startDateTime\n      __typename\n    }\n    level {\n      __typename\n      id\n      name\n      category\n      orderIndex\n      shortName\n    }\n    events {\n      id\n      sanctionStatus\n      courtLocation\n      sanctionStatus\n      isPublished\n      formatConfiguration {\n        entriesLimit\n        ballColour\n        drawSize\n        eventFormat\n        scoreFormat\n        selectionProcess\n        __typename\n      }\n      level {\n        id\n        name\n        category\n        orderIndex\n        shortName\n        __typename\n      }\n      division {\n        __typename\n        ballColour\n        ageCategory {\n          __typename\n          minimumAge\n          maximumAge\n          todsCode\n          type\n        }\n        eventType\n        gender\n        wheelchairRating\n        familyType\n        ratingCategory {\n          __typename\n          ratingCategoryType\n          ratingType\n          value\n        }\n      }\n      pricing {\n        entryFee {\n          amount\n          currency\n          __typename\n        }\n        __typename\n      }\n      registrations {\n        id\n        player {\n          customId {\n            key\n            value\n            __typename\n          }\n          firstName\n          lastName\n          name\n          gender\n          __typename\n        }\n        registrationDate\n        selectionIndex\n        selectionStatus\n        __typename\n      }\n      surface\n      withdrawals {\n        player {\n          customId {\n            key\n            value\n            __typename\n          }\n          firstName\n          lastName\n          name\n          gender\n          __typename\n        }\n        registrationDate\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"}'
    r = requests.post('https://playtennis.usta.com/swift?cs:prod-us-kube/usta/tournaments/api/graphql', data=post_json)
    out = pd.DataFrame()
    tourn_name = r.json()['data']['publishedTournament']['name']
    for event in r.json()['data']['publishedTournament']['events']:
        division_dict = event['division']
        division = division_dict['gender'].capitalize() + '\' ' + str(
            division_dict['ageCategory']['maximumAge']) + ' & Under ' + division_dict['eventType'].capitalize()
        for player in event['registrations']:
            name = player['player']['name']
            gender = player['player']['gender'][0]
            player_info = pd.DataFrame([name, division, gender]).transpose()
            out = out.append(player_info)
    out.columns = ['Player name', 'Events', 'Gender']
    out = out[out['Events'].str.endswith('Singles')]
    out['index'] = [num for num in range(1, len(out.index) + 1)]
    out = out.set_index('index')
    return out, tourn_name


if __name__ == '__main__':
    print(query_tourn(input('ID here:')))
