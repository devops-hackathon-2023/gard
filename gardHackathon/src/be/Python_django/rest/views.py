import pandas as pd
from datetime import datetime
import aiohttp
import asyncio
from django.http import JsonResponse
from rest_framework.decorators import api_view

def parseTime(time):
    if time is not None:
        if '.' in time:
            time = time.split('.')[0]
        time = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S")
        return time
    return None


async def getDataPage(session, base_url, page, size, headers):
    params = {'page': page, 'size': size}
    async with session.get(base_url, params=params, headers=headers) as response:
        if response.status == 200:
            return await response.json()
        return None


async def getAllData(base_url, params={}, max_workers=30):
    headers = {'Authorization': 'Basic ZG9wbzpEZXZPcHMyMDIz'}

    params['pageSize'] = 100
    data = []

    async with aiohttp.ClientSession() as session:
        response = await session.get(base_url, params=params, headers=headers)

        if response.status != 200:
            print(f'Ошибка при запросе данных: {response.status}')
            return data

        response_data = await response.json()
        pageCount = response_data['pageCount']

        tasks = []

        for page in range(pageCount + 1):
            tasks.append(getDataPage(session, base_url, page, params['pageSize'], headers))

        responses = await asyncio.gather(*tasks)

        for response_data in responses:
            if response_data:
                if 'page' in response_data:
                    data.extend(response_data['page'])

                if response_data['nextPage'] is None:
                    break
    return data

async def get_deployment_unit_versions(ids):
    data = []
    tasks = []

    async with aiohttp.ClientSession() as session:
        for unitId in ids:
            task = asyncio.ensure_future(getDataPage(session,
                                                     'https://dopo.fly.dev/api/v1/dopo/deployment-units/{}/deployment-unit-versions'.format(
                                                         unitId), 0, 100,
                                                     {'Authorization': 'Basic ZG9wbzpEZXZPcHMyMDIz'}))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)

        for response_data in responses:
            if response_data:
                if 'page' in response_data:
                    data.extend(response_data['page'])
    return data


async def processData(params = {
        'sasName': '',
        'appModuleName': '',
        'platform': '',
        'deploymentUnitName': '',
        'environment': '',
        'startDate': '',
        'endDate': ''
    }):
    data = await getAllData('https://dopo.fly.dev/api/v1/dopo/sases')
    df_sases = pd.DataFrame(data)
    if params['sasName'] != 'None':
        df_sases = df_sases[df_sases['name'] == params['sasName']]

    df_appModules = []
    for sasId in df_sases['id'].unique():
        data = await getAllData('https://dopo.fly.dev/api/v1/dopo/sases/{}/app-modules'.format(sasId))
        df_appModules.extend(data)
    df_appModules = pd.DataFrame(df_appModules)
    if params['appModuleName'] != 'None':
        df_appModules = df_appModules[df_appModules['name'] == params['appModuleName']]

    df_deploymentUnits = []
    data = await getAllData('https://dopo.fly.dev/api/v1/dopo/deployment-units')
    df_deploymentUnits.extend(data)
    df_deploymentUnits = pd.DataFrame(df_deploymentUnits)
    df_deploymentUnits = df_deploymentUnits[df_deploymentUnits['appModuleId'].isin(df_appModules['id'].unique())]

    if params['deploymentUnitName'] != 'None':
        df_deploymentUnits = df_deploymentUnits[
            df_deploymentUnits['deploymentUnitName'] == params['deploymentUnitName']]

    data = await get_deployment_unit_versions(df_deploymentUnits['id'].unique())
    df_deploymentUnitVersions = pd.DataFrame(data)

    # df_deploymentUnitVersions = []
    # for unitId in df_deploymentUnits['id']:
    #     data = await getAllData(
    #         'https://dopo.fly.dev/api/v1/dopo/deployment-units/{}/deployment-unit-versions'.format(unitId))
    #     df_deploymentUnitVersions.extend(data)
    # df_deploymentUnitVersions = pd.DataFrame(df_deploymentUnitVersions)

    df_qualityGates = []
    data = await getAllData('https://dopo.fly.dev/api/v1/dopo/quality-gates')
    df_qualityGates.extend(data)
    df_qualityGates = pd.DataFrame(df_qualityGates)
    df_qualityGates = df_qualityGates[df_qualityGates['versionId'].isin(df_deploymentUnitVersions['id'].unique())]
    df_qualityGates = df_qualityGates.merge(df_deploymentUnitVersions, left_on='appModuleId', right_on='id', how='left')

    df_deployments = []
    data = await getAllData('https://dopo.fly.dev/api/v1/dopo/deployments')
    df_deployments.extend(data)
    df_deployments = pd.DataFrame(df_deployments)
    df_deployments = df_deployments[df_deployments['versionId'].isin(df_deploymentUnitVersions['id'].unique())]

    if params['platform'] != 'None':
        df_deployments = df_deployments[df_deployments['platform'] == params['platform']]

    if params['environment'] != 'None':
        df_deployments = df_deployments[df_deployments['environment'] == params['environment']]

    df_deployments['finishedAt'] = df_deployments['finishedAt'].apply(lambda x: parseTime(x))
    df_deployments['startedAt'] = df_deployments['startedAt'].apply(lambda x: parseTime(x))
    df_deployments['deployDate'] = df_deployments['finishedAt'].apply(lambda x: x.date())
    df_deployments['deployDate'] = pd.to_datetime(df_deployments['deployDate'])

    if params['startDate'] != 'None':
        df_deployments = df_deployments[(df_deployments['deployDate'] >= pd.to_datetime(params['startDate']))]

    if params['endDate'] != 'None':
        df_deployments = df_deployments[(df_deployments['deployDate'] <= pd.to_datetime(params['endDate']))]

    df_deployments = df_deployments.merge(df_deploymentUnits[['id', 'language']], left_on='deploymentUnitId',
                                          right_on='id', how='left')

    return df_deployments, df_qualityGates


def sucessRateGraph(df_deployments):

    df_deployments['successful_attempt'] = df_deployments['status'] == 'SUCCESS'
    date_success = df_deployments.groupby('deployDate')['successful_attempt'].mean().reset_index()
    date_success.sort_values(by='deployDate', inplace=True)

    if date_success.isna().sum().sum() > 0:
        date_success.dropna(inplace=True)

    return date_success['deployDate'].apply(lambda x: x.date()).tolist(), date_success['successful_attempt'].tolist()

def barPlotSuccessByLang(df_deployments):
    df_deployments['successful_attempt'] = df_deployments['status'] == 'SUCCESS'
    language_success = df_deployments.groupby('language')['successful_attempt'].mean().reset_index()
    language_success.sort_values(by='successful_attempt', inplace=True)

    if language_success.isna().sum().sum() > 0:
        language_success.dropna(inplace=True)

    return language_success['language'].tolist(), language_success['successful_attempt'].tolist()

def barPlotSuccessByType(df_qualityGates):

    df_qualityGates['successful_attempt'] = df_qualityGates['result'] == 'PASSED'
    type_success = df_qualityGates.groupby('type')['successful_attempt'].mean().reset_index()
    type_success.sort_values(by='successful_attempt', inplace=True)

    if type_success.isna().sum().sum() > 0:
        type_success.dropna(inplace=True)

    return type_success['type'].tolist(), type_success['successful_attempt'].tolist()

def pieChartLang(df_deployments):

    lang_count = df_deployments.groupby('language')['environment'].count().reset_index()
    if lang_count.isna().sum().sum() > 0:
        lang_count.dropna(inplace=True)

    return lang_count['language'].tolist(), lang_count['environment'].tolist()

def histDuration(df_deployments):

    duration = df_deployments['duration'].dropna().tolist()

    return duration

def calculateMetrics(df_deployments, df_qualityGates):
    totalDeploys = df_deployments.shape[0]

    passedPercentage = df_qualityGates['result'] == 'PASSED'
    passedPercentage = passedPercentage.mean()

    successDeplPrecentage = df_deployments['status'] == 'SUCCESS'
    successDeplPrecentage = df_deployments.mean()

    durationMean = df_deployments['duration'].mean()

    meanPrecentRate = df_qualityGates['percent'].mean()

    meanRating = df_qualityGates['rating'].mode()

    return totalDeploys, passedPercentage, successDeplPrecentage, durationMean, meanPrecentRate, meanRating

async def versionHistory(deploymentUnitVersionId):
    deployments = await getAllData(base_url='https://dopo.fly.dev/api/v1/dopo/deployments', params={'versionId': deploymentUnitVersionId})
    deployments = pd.DataFrame(deployments)

    qualityGates = await getAllData(base_url='https://dopo.fly.dev/api/v1/dopo/quality-gates', params={ 'versionId': deploymentUnitVersionId})
    qualityGates = pd.DataFrame(qualityGates)

    sas = await getAllData(base_url='https://dopo.fly.dev/api/v1/dopo/sases', params={'id': deployments['sasId'][0]})
    sas = pd.DataFrame(sas)
    sasMapping= {sas['id'][0]: sas['name'][0]}

    appModules = await getAllData(base_url='https://dopo.fly.dev/api/v1/dopo/sases/{}/app-modules', params={'sasId': sas['id`'][0]})
    appModules = pd.DataFrame(appModules)

    appModuleNameMapping = dict(zip(appModules['id'], appModules['name']))

    deployments['sasId'] = deployments['sasId'].map(sasMapping)
    deployments['appModuleId'] = deployments['appModuleId'].map(appModuleNameMapping)

    deployments['finishedAt'] = deployments['finishedAt'].apply(lambda x: parseTime(x))
    deployments['startedAt'] = deployments['startedAt'].apply(lambda x: parseTime(x))

    qualityGates['sasId'] = qualityGates['sasId'].map(sasMapping)
    qualityGates['appModuleId'] = qualityGates['appModuleId'].map(appModuleNameMapping)

    qualityGates['finishedAt'] = qualityGates['finishedAt'].apply(lambda x: parseTime(x))
    qualityGates['startedAt'] = qualityGates['startedAt'].apply(lambda x: parseTime(x))

    deployments.sort_values(by='startedAt', inplace=True)
    qualityGates.sort_values(by='startedAt', inplace=True)

    return deployments.to_json(orient='records'), qualityGates.to_json(orient='records')


@api_view(['GET'])
def get_success_rate_graph(request):

    params = {
        'sasName': request.GET.get('sasName'),
        'appModuleName': request.GET.get('appModuleName'),
        'platform': request.GET.get('platformName'),
        'deploymentUnitName': request.GET.get('dUnitName'),
        'environment': request.GET.get('envName'),
        'startDate': request.GET.get('startDateName'),
        'endDate': request.GET.get('endDateName')
    }

    depl, gate = asyncio.run(processData(params))

    x_successRateGraph, y_successRateGraph = sucessRateGraph(depl)
    x_barPlotSuccessByLang , Y_barPlotSuccessByLang = barPlotSuccessByLang(depl)
    x_barPlotSuccessByType, Y_barPlotSuccessByType = barPlotSuccessByType(gate)
    labels_pieChartLang, counts_pieChartLang = pieChartLang(depl)
    hist_data = histDuration(depl)

    totalDeploys, passedPercentage, successDeplPrecentage, durationMean, meanPrecentRate, meanRating = calculateMetrics(depl, gate)

    response_data = {
        "successRateGraph": {
            "x": x_successRateGraph,
            "y": y_successRateGraph
        },
        "barPlotSuccessByLang": {
            "x": x_barPlotSuccessByLang,
            "y": Y_barPlotSuccessByLang
        },
        "barPlotSuccessByType": {
            "x": x_barPlotSuccessByType,
            "y": Y_barPlotSuccessByType
        },
        "pieChartLang": {
            "labels": labels_pieChartLang,
            "counts": counts_pieChartLang
        },
        "metrics": {
            "totalDeploys": totalDeploys,
            "passedPercentage": passedPercentage,
            "successDeplPrecentage": successDeplPrecentage,
            "durationMean": durationMean,
            "meanPrecentRate": meanPrecentRate,
            "meanRating": meanRating
        }
    }

    print(response_data)
    return JsonResponse(response_data)



@api_view(['GET'])
def getDeploymentHistory(request):
    id = request.GET.get('deploymentUnitVersionId')

    deployments, qualityGates = asyncio.run(versionHistory(id))

    response_data = {
        "deployents" : deployments,
        "qualityGates" : qualityGates
    }

    return JsonResponse(response_data)