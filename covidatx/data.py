from requests import get
from json import dumps
import pandas as pd
from http import HTTPStatus
from typing import Dict, Union, List


class CovidData:
    """Class for fetching data from gov.uk API
       https://api.coronavirus.data.gov.uk. This code was adapted from
       code provided in the developer's guide for the api
       https://coronavirus.data.gov.uk/details/developers-guide/main-api
    """

    _nations = ['england', 'scotland', 'wales', 'northern ireland']
    _regions = ['East Midlands', 'East of England', 'London', 'North East',
                'North West', 'South East', 'South West', 'West Midlands',
                'Yorkshire and The Humber']
    _ENDPOINT = "https://api.coronavirus.data.gov.uk/v1/data"

    def __init__(self, nation='england'):
        """
        Create a CovidData object. This will read data from the
        gov.uk covid data API.

        Parameters:
            - nation: This specifies for which nation to collect data.
              it is one of 'scotland', 'england', 'wales' or 'northern
              ireland'.

        Returns:
            A `CovidData` object.
        """

        self.nation = nation
        if not isinstance(self.nation, str):
            raise TypeError('`nation` must be a string')
        if self.nation not in self._nations:
            raise ValueError('`nation` must be either england, scotland, \
                                or wales or northern ireland')
        self.nation = nation.lower()

    @property
    def nation_list(self):
        """Return list of available nations"""
        return self._nations

    @property
    def region_list(self):
        """Return list of available nations"""
        return self._regions

    def get_national_data(self):
        """ Retrieve national data from the API_data.

        Parameters:
                - uses self.nation to determine which nation's data to
                retrieve.

        Returns:
             A pandas DataFrame of covid data. Date, name of area, new cases,
             change in new cases, percentage change in new cases, new case
             rate, cumulative cases, daily deaths, new death rate, cumulative
             death, cumulative death rate, death demographics, vaccine first
             dose uptake,vaccine second dose uptake, vaccine total percentage
             uptake, vaccine demographics, hospital cases, hospital new
             admissions, hospital new admission change and hosp mechanical
             ventilator occupancy are returnedas panda DataFrame columns.
             The date range is the most recently updated data, (this is
             updated in the afternoon UK time) going back to the start
             of the pandemic UK data collection in March 2020.
        """

        area_type = 'nation'
        filters = [
                f"areaType={ area_type }",
                f"areaName={ self.nation }"
                ]

        structure = {
            "date": "date",
            "name": "areaName",
            "case_newCases": "newCasesByPublishDate",
            "case_newCasesChange": "newCasesByPublishDateChange",
            "case_newCasesPercChange": "newCasesByPublishDateChangePercentage",
            "case_rate": "newCasesBySpecimenDateRollingRate",
            "case_cumulativeCases": "cumCasesByPublishDate",
            "death_dailyDeaths": "newDeaths28DaysByPublishDate",
            "death_newDeathRate": "newDeaths28DaysByDeathDateRate",
            "death_cumulativeDeaths": "cumDeaths28DaysByDeathDate",
            "death_cumulativeDeathsRate": "cumDeaths28DaysByDeathDateRate",
            "death_Demographics": "newDeaths28DaysByDeathDateAgeDemographics",
            "vac_first_dose": "cumPeopleVaccinatedFirstDoseByVaccinationDate",
            "vac_second_dose": "cumPeopleVaccinatedSecondDoseByPublishDate",
            "vac_total_perc":
            "cumVaccinationCompleteCoverageByVaccinationDatePercentage",
            "vac_demographics": "vaccinationsAgeDemographics",
            "hosp_hospitalCases": "hospitalCases",
            "hosp_newAdmissions": "newAdmissions",
            "hosp_newAdmissionsChange": "newAdmissionsChange",
            "hosp_covidOccupiedMVBeds": "covidOccupiedMVBeds"

        }
        StructureType = Dict[str, Union[dict, str]]
        api_params = {
            "filters": str.join(";", filters),
            "structure": dumps(structure, separators=(",", ":"))
        }

        # response = get(self._ENDPOINT, params=api_params, timeout=10)

        # if response.status_code >= 400:
        #     raise RuntimeError(f'Request failed: { response.text }')

        # data_json = response.json()
        # df = pd.DataFrame(data_json['data'])
        # return df

        data = list()

        page_number = 1

        while True:
            # Adding page number to query params
            api_params["page"] = page_number

            response = get(self._ENDPOINT, params=api_params, timeout=30)

            if response.status_code >= HTTPStatus.BAD_REQUEST:
                raise RuntimeError(f'Request failed: {response.text}')
            elif response.status_code == HTTPStatus.NO_CONTENT:
                break

            current_data = response.json()
            page_data: List[StructureType] = current_data['data']

            data.extend(page_data)

            # The "next" attribute in "pagination" will be `None`
            # when we reach the end.
            if current_data["pagination"]["next"] is None:
                break

            page_number += 1
        df = pd.DataFrame(data)
        return df

    def get_regional_data(self):
        """Retrieve regional data for 9 English regions. Regional data is not
        available for other UK countries.

        Parameters:
                - uses self.nation to assert that data for england is being
                  collected.

        Returns:
            A pandas DataFrame consisting of Date, region name, regional new
            daily cases, regional cumulative cases, regional case demographics,
            vaccine first dose and vaccine second dose uptake. Data is updated
            in the afternoon UK time (actual time can vary). Date range
            includes most recent available data, going back to the start
            of UK pandemic data collection in March 2020.
        """

        assert self.nation == 'england', 'Regional data only available for'\
                                   +' `england`. Set nation to `england`.'
        area_type = 'region'

        StructureType = Dict[str, Union[dict, str]]
        filters = [
                f"areaType={ area_type }"
                ]

        structure = {
            "date": "date",
            "name": "areaName",
            "cases_newDaily": "newCasesBySpecimenDate",
            "cases_cumulative": "cumCasesBySpecimenDate",
            "case_rate": "newCasesBySpecimenDateRollingRate",
            "cases_demographics": "newCasesBySpecimenDateAgeDemographics",
            "death_newDeathRate": "newDeaths28DaysByDeathDateRate",
            "death_cumulativeDeaths": "cumDeaths28DaysByDeathDate",
            "death_cumulativeDeathsRate": "cumDeaths28DaysByDeathDateRate",
            "death_Demographics": "newDeaths28DaysByDeathDateAgeDemographics",
            "vac_firstDose":
            "cumVaccinationFirstDoseUptakeByVaccinationDatePercentage",
            "vac_secondDose":
            "cumVaccinationSecondDoseUptakeByVaccinationDatePercentage",
            "vac_demographics": "vaccinationsAgeDemographics"
            }

        api_params = {
            "filters": str.join(";", filters),
            "structure": dumps(structure, separators=(",", ":"))
        }

        data = list()

        page_number = 1

        while True:
            # Adding page number to query params
            api_params["page"] = page_number

            response = get(self._ENDPOINT, params=api_params, timeout=30)

            if response.status_code >= HTTPStatus.BAD_REQUEST:
                raise RuntimeError(f'Request failed: {response.text}')
            elif response.status_code == HTTPStatus.NO_CONTENT:
                break

            current_data = response.json()
            page_data: List[StructureType] = current_data['data']

            data.extend(page_data)

            # The "next" attribute in "pagination" will be `None`
            # when we reach the end.
            if current_data["pagination"]["next"] is None:
                break

            page_number += 1
        df = pd.DataFrame(data)
        return df

    def get_local_data(self, date='date'):
        """Retrieve all the local authority data across the UK.
           Return it as a pandas DataFrame.

            Parameters:
                - No parameters required. It will connect to the gov.uk API
                  using pre selected criteria.

            Returns:
                - A pandas DataFrame containing all the data available since
                  the start of the pandemic. The features are 'date',
                  'name'- this is the local authority name, 'case_newDaily'
                  - this is the daily, number of new cases for the
                  local authority, 'case_cumulative' - the cumulative
                  case numbers for each authority and 'case_rate',
                  which is the number of cases per 100,000 people.
        """

        AREA_TYPE = "ltla"
        StructureType = Dict[str, Union[dict, str]]
        # this is local authority data
        filters = [
            f"areaType={ AREA_TYPE }",
            f"date={ date }"

        ]

        structure = {
            "date": "date",
            "name": "areaName",
            "case_newDaily": "newCasesByPublishDate",
            "case_cumulative": "cumCasesBySpecimenDate",
            "case_rate": "newCasesBySpecimenDateRollingRate"
            }

        api_params = {
            "filters": str.join(";", filters),
            "structure": dumps(structure, separators=(",", ":"))
        }
        data = list()

        page_number = 1

        while True:
            # Adding page number to query params
            api_params["page"] = page_number

            response = get(self._ENDPOINT, params=api_params, timeout=30)

            if response.status_code >= HTTPStatus.BAD_REQUEST:
                raise RuntimeError(f'Request failed: {response.text}')
            elif response.status_code == HTTPStatus.NO_CONTENT:
                break

            current_data = response.json()
            page_data: List[StructureType] = current_data['data']

            data.extend(page_data)

            # The "next" attribute in "pagination" will be `None`
            # when we reach the end.
            if current_data["pagination"]["next"] is None:
                break

            page_number += 1
        df = pd.DataFrame(data)
        return df

    def get_uk_data(self):
        """Retrieve and combine all national data.
           Provide United Kingdom data.

        Parameters:
                -No parameters needed.

        Returns:
                A dataframe combining all of the nation data. DataFrame
                contains date column, daily new cases, cumulative cases
                daily death data, cumulative death data, hospital cases,
                hospital new admissions, occupied mechanical ventilators.
        """
        df = self.get_national_data()
        self.nation = self._nations[2]
        df_wales = self.get_national_data()
        self.nation = self._nations[1]
        df_scot = self.get_national_data()
        self.nation = self._nations[3]
        df_ni = self.get_national_data()

        # If time I'll implement this. More efficient but requires
        # reworking of plotting funtions.
        # df_list = [df, df_wales, df_scot, df_ni]
        # to_drop = ['death_Demographics', 'vac_demographics']

        # for frame in df_list:
        #     frame['date'] = pd.to_datetime(frame['date'])
        #     frame.set_index('date', inplace=True)
        #     frame.drop(columns=to_drop, inplace=True)

        # df_total = df_ni.add(df_wales.add(df.add(df_scot)))

        df_total = pd.DataFrame()
        df_total = df_total.assign(date=df['date'])
        df_total['date'] = pd.to_datetime(df_total['date'])
        df_total = df_total.assign(nation=('United Kingdom'))
        df_total = df_total.assign(case_newCases=(df_wales['case_newCases']
                                   + df_ni['case_newCases']
                                   + df_scot['case_newCases']
                                   + df['case_newCases']))
        df_total = df_total.assign(case_cumulativeCases=(
                                   df_wales['case_cumulativeCases']
                                   + df_ni['case_cumulativeCases']
                                   + df_scot['case_cumulativeCases']
                                   + df['case_cumulativeCases']))
        df_total = df_total.assign(death_dailyDeaths=(
                                   df_wales['death_dailyDeaths']
                                   + df_ni['death_dailyDeaths']
                                   + df_scot['death_dailyDeaths']
                                   + df['death_dailyDeaths']))
        df_total = df_total.assign(death_cumulativeDeaths=(
                                   df_wales['death_cumulativeDeaths']
                                   + df_ni['death_cumulativeDeaths']
                                   + df_scot['death_cumulativeDeaths']
                                   + df['death_cumulativeDeaths']))
        df_total = df_total.assign(hosp_hospitalCases=(
                                   df_wales['hosp_hospitalCases']
                                   + df_ni['hosp_hospitalCases']
                                   + df_scot['hosp_hospitalCases']
                                   + df['hosp_hospitalCases']))
        df_total = df_total.assign(hosp_newAdmissions=(
                                   df_wales['hosp_newAdmissions']
                                   + df_ni['hosp_newAdmissions']
                                   + df_scot['hosp_newAdmissions']
                                   + df['hosp_newAdmissions']))
        df_total = df_total.assign(hosp_covidOccupiedMVBeds=(
                                   df_wales['hosp_covidOccupiedMVBeds']
                                   + df_ni['hosp_covidOccupiedMVBeds']
                                   + df_scot['hosp_covidOccupiedMVBeds']
                                   + df['hosp_covidOccupiedMVBeds']))
        df_total = df_total.assign(hosp_newAdmissionsChange=(
                                   df_wales['hosp_newAdmissionsChange']
                                   + df_ni['hosp_newAdmissionsChange']
                                   + df_scot['hosp_newAdmissionsChange']
                                   + df['hosp_newAdmissionsChange']))
        df_total = df_total.assign(vac_first_dose=(
                                   df_wales['vac_first_dose']
                                   + df_ni['vac_first_dose']
                                   + df_scot['vac_first_dose']
                                   + df['vac_first_dose']))
        df_total = df_total.assign(vac_second_dose=(
                                   df_wales['vac_second_dose']
                                   + df_ni['vac_second_dose']
                                   + df_scot['vac_second_dose']
                                   + df['vac_second_dose']))
        df_total = df_total.assign(vac_total_perc=(
                                   df_wales['vac_total_perc']
                                   + df_ni['vac_total_perc']
                                   + df_scot['vac_total_perc']
                                   + df['vac_total_perc']))

        return df_total
