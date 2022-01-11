from .data import CovidData
import datetime as dt
from matplotlib.offsetbox import AnchoredText
import pandas as pd
import seaborn as sns


import geopandas as gpd
import matplotlib.pyplot as plt
plt.style.use('ggplot')


def pan_duration(date):
    """Return the duration in days of the pandemic.

    As calculated from the gov.uk API. It subtracts the first date entry
    in the API data from the most recent date entry.

    Args:
        date (datetime): DataFrame column (i.e Series) containing date
        field as downloaded from the gov.uk API by get_national_data()
        method from CovidData Class.

    Returns:
        datetime: Duration of pandemic in days as datetime object.
    """
    return (date[0] - date[-1]).days


def validate_input(df):
    """Check that input into the plotting functions is of the correct type.

    Args:
        df (Pandas DataFrame): this is intended to be the plotting parameter

    Raises:
        TypeError: if parameter is not a DataFrame
    """
    # if for_function == 'deaths' or for_function == 'cases':
    #     expected_cols = {'cases_cumulative', 'cases_demographics',
    #                      'cases_newDaily', 'case_rate', 'date',
    #                      'death_Demographics', 'name', 'vac_firstDose',
    #                      'vac_secondDose'}
    if not isinstance(df, pd.DataFrame):
        raise TypeError('Parameter must be DataFrame, use get_regional_data'
                        + ' method from CovidData class.')

    # if set(df.columns) != expected_cols:
    #     raise ValueError('Incorrect features. Expecting output from'
    #                      + ' get_regional_data method from CovidData class')


def my_path():
    """Find correct path at module level for geo_data files.

    Returns:
        [type]: [description]
    """
    from pathlib import Path
    base = Path(__file__).resolve().parent / 'geo_data'
    return base


def daily_case_plot(df, pan_duration=pan_duration, save=False):
    """Create a matplotlib plot of case numbers in the UK.

    Calculated over the duration of the pandemic.Display text information
    giving the most recent daily number, the highest daily number and the
    date recorded, the total cumulative
    number of cases and the duration of the pandemic in days.

    Args:
        df (DataFrame): containing covid data retrieved from CovidData
            class using get_national_data() or get_UK_data() method.
        pan_duration (function, optional): Defaults to pan_duration.
        save (bool, optional): set True to save plot. Defaults to False.
    Returns:
            - Matplotlib plot, styled using matplotlib template 'ggplot'
    """
    # Create Variables we wish to plot
    cases = df['case_newCases'].to_list()
    date = df['date'].to_list()
    cumulative = df['case_cumulativeCases'].to_list()

    # Find date of highest number of daily cases
    high, arg_high = max(cases), cases.index(max(cases))
    high_date = date[arg_high].strftime('%d %b %Y')

    duration = pan_duration(date=date)
    # Create matplotlib figure and specify size
    fig = plt.figure(figsize=(12, 10))
    plt.style.use('ggplot')
    ax = fig.add_subplot()
    # Plot varibles
    ax.plot(date, cases)
    # Style and label plot
    ax.set_xlabel('Date')
    ax.set_ylabel('Cases')
    ax.fill_between(date, cases,
                    alpha=0.3)
    ax.set_title('Number of people who tested positive for Covid-19 (UK)',
                 fontsize=18)
    at = AnchoredText(f"Most recent new cases\n{cases[0]:,.0f}\
                      \nMax new cases\n{high:,.0f}: {high_date}\
                      \nCumulative cases\n{cumulative[0]:,.0f}\
                      \nPandemic duration\n{duration} days",
                      prop=dict(size=16), frameon=True, loc='upper left')
    at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
    ax.add_artist(at)
    ax.annotate('Source: gov.uk https://api.coronavirus.data.gov.uk/v1/data',
                xy=(0.25, 0.0175), xycoords='figure fraction',
                fontsize=12, color='#555555')

    plt.style.use('ggplot')
    if save:
        plt.savefig(f"{date[0].strftime('%Y-%m-%d')}-case_numbers_plot");
    plt.show()


def regional_plot_cases(save=False):
    """Plot regional case numbers on a map of the UK.

        Function collects data using CovidData get_regional_data method.

    Args:
        save (bool, optional): If true will save plot. Defaults to False.
    Returns:
        Plot of regional case numbers on map of UK
    """
    # Collect data
    regions = CovidData().get_regional_data()
    scotland = CovidData(nation='scotland').get_national_data()
    wales = CovidData(nation='wales').get_national_data()
    ni = CovidData(nation='northern ireland').get_national_data()
    regions = regions.assign(case_newCases=regions['cases_newDaily'])
    # Set date to plot
    date_selector = regions['date'][0]
    regions_date = regions.loc[regions['date'] == date_selector]
    scotland_date = \
        scotland.loc[scotland['date'] == date_selector,
                     ['date', 'name', 'case_newCases']]
    wales_date = wales.loc[wales['date'] == date_selector,
                           ['date', 'name', 'case_newCases']]
    ni_date = ni.loc[ni['date'] == date_selector,
                     ['date', 'name', 'case_newCases']]
    # Combine regional data into single dataframe
    final_df = pd.concat([regions_date, scotland_date, wales_date, ni_date],
                         axis=0)
    file_path = my_path() / 'NUTS_Level_1_(January_2018)_Boundaries.shp'
    # Check required file exists
    try:
        # Read shape file
        geo_df = gpd.read_file(file_path)
    except: # bare except is not good practice, this should be changed
        print('Ensure you have imported geo_data sub-folder')

    geo_df['nuts118nm'] = \
        geo_df['nuts118nm'].replace(['North East (England)',
                                     'North West (England)',
                                     'East Midlands (England)',
                                     'West Midlands (England)',
                                     'South East (England)',
                                     'South West (England)'],
                                    ['North East', 'North West',
                                     'East Midlands', 'West Midlands',
                                     'South East', 'South West'])
    merged = geo_df.merge(final_df, how='left', left_on="nuts118nm",
                          right_on="name")

    # Column to plot
    feature = 'case_newCases'
    # Plot range
    feature_min, feature_max = merged['case_newCases'].min(), \
        merged['case_newCases'].max()
    # Create plot
    fig, ax = plt.subplots(1, figsize=(12, 10))
    # Set style and labels
    ax.axis('off')
    ax.set_title(f'Number of new cases per region {date_selector}',
                 fontdict={'fontsize': '18', 'fontweight': '3'})
    ax.annotate('Source: gov.uk'
                + ' https://api.coronavirus.data.gov.uk/v1/data',
                xy=(0.25, .05), xycoords='figure fraction',
                fontsize=12, color='#555555')
    # Create colorbar
    sm = plt.cm.ScalarMappable(cmap='Reds',
                               norm=plt.Normalize(vmin=feature_min,
                                                  vmax=feature_max))
    fig.colorbar(sm)
    # Create map
    merged.plot(column=feature, cmap='Reds', linewidth=0.8, ax=ax,
                edgecolor='0.8');
    plt.show()
    if save:
        image = merged.plot(column=feature, cmap='Reds', linewidth=0.8,
                            ax=ax, edgecolor='0.8');
        image.figure.savefig(f'{date_selector}-regional_cases_plot')


def regional_plot_rate(save=False):
    """Plot regional case rate per 100,000 on a map of the UK.

       Function collects data using CovidData get_regional_data method.
    Args:
        save (bool, optional): If true will save plot. Defaults to False.
    Returns:
        Plot of regional case rate on map of UK.
    """
    # Collect data
    regions = CovidData().get_regional_data()
    scotland = CovidData(nation='scotland').get_national_data()
    wales = CovidData(nation='wales').get_national_data()
    ni = CovidData(nation='northern ireland').get_national_data()

    # Set date to plot
    date_selector = regions['date'][5]
    regions_date = regions.loc[regions['date'] == date_selector]
    scotland_date = scotland.loc[scotland['date'] == date_selector,
                                 ['date', 'name', 'case_rate']]
    wales_date = wales.loc[wales['date'] == date_selector,
                           ['date', 'name', 'case_rate']]
    ni_date = ni.loc[ni['date'] == date_selector,
                     ['date', 'name', 'case_rate']]
    # Combine regional data into single dataframe
    final_df = pd.concat([regions_date, scotland_date, wales_date, ni_date],
                         axis=0)
    file_path = my_path() / 'NUTS_Level_1_(January_2018)_Boundaries.shp'
    # Check required file exists
    try:
        # Read shape file
        geo_df = gpd.read_file(file_path)
    except:  # bare except should be changed, will do so in later interation
        print('Ensure you have imported geo_data sub-folder')

    geo_df['nuts118nm'] = \
        geo_df['nuts118nm'].replace(['North East (England)',
                                     'North West (England)',
                                     'East Midlands (England)',
                                     'West Midlands (England)',
                                     'South East (England)',
                                     'South West (England)'],
                                    ['North East', 'North West',
                                     'East Midlands', 'West Midlands',
                                     'South East', 'South West'])
    merged = geo_df.merge(final_df, how='left', left_on="nuts118nm",
                          right_on="name")
    # Column to plot
    feature = 'case_rate'
    # Plot range
    feature_min, feature_max = merged['case_rate'].min(),\
        merged['case_rate'].max()
    # Create plot
    fig, ax = plt.subplots(1, figsize=(12, 10))
    # Set style and labels
    ax.axis('off')
    ax.set_title('Regional rate per 100,000 (new cases)',
                 fontdict={'fontsize': '20', 'fontweight': '3'})
    ax.annotate('Source: gov.uk'
                + ' https://api.coronavirus.data.gov.uk/v1/data',
                xy=(0.25, .05), xycoords='figure fraction',
                fontsize=12, color='#555555')
    # Create colorbar
    sm = plt.cm.ScalarMappable(cmap='Reds',
                               norm=plt.Normalize(vmin=feature_min,
                                                  vmax=feature_max))
    fig.colorbar(sm)
    # Create map
    merged.plot(column=feature, cmap='Reds', linewidth=0.8, ax=ax,
                edgecolor='0.8');
    plt.show()
    if save:
        image = merged.plot(column=feature, cmap='Reds', linewidth=0.8,
                            ax=ax, edgecolor='0.8');
        image.figure.savefig(f'{date_selector}-regional_rate_plot')


def heatmap_cases(df):
    """Create heatmap of case numbers for duration of pandemic.

    Args:
        df (DataFrame): Covid case data retrieved by calling CovidData
                        class method.
    Returns:
        Seaborn heatmap plot of case numbers for each day of the pandemic.
    """
    # Variables to plot
    cases = df['case_newCases'].to_list()
    date = df['date'].to_list()

    # Create new DataFrame containing two columns: date and case numbers
    heat_df = pd.DataFrame({'date': date, 'cases': cases}, index=date)

    # Separate out date into year month and day
    heat_df['year'] = heat_df.index.year
    heat_df["month"] = heat_df.index.month
    heat_df['day'] = heat_df.index.day

    # Use groupby to convert data to wide format for heatmap plot
    x = heat_df.groupby(["year", "month", "day"])["cases"].sum()
    df_wide = x.unstack()

    # Plot data
    sns.set(rc={"figure.figsize": (12, 10)})
    # Reverse colormap so that dark colours represent higher numbers
    cmap = sns.cm.rocket_r
    ax = sns.heatmap(df_wide, cmap=cmap)

    ax.set_title('Heatmap of daily cases since start of pandemic',
                 fontsize=20)
    ax.annotate('Source: gov.uk https://api.coronavirus.data.gov.uk/v1/data',
                xy=(0.25, 0.01), xycoords='figure fraction',
                fontsize=12, color='#555555')
    plt.show()


def local_rate_plot(save=False):
    """Plot local case rate per 100,000 on a map of the UK.

    Function collects data using CovidData get_regional_data method.

    Args:
        save (bool, optional): If true will save plot. Defaults to False.
    Returns:
        Plot of local case rate on map of UK
    """
    # Find latest data
    recent_date = CovidData().get_regional_data()
    recent_date = recent_date['date'][5]
    # Select latest data from local data
    local = CovidData().get_local_data(date=recent_date)
    date_selector = recent_date
    local_date = local.loc[local['date'] == date_selector,
                           ['date', 'name', 'case_rate']]
    file_path = my_path() / "Local_Authority_Districts.shp"
    # Check required file exists
    try:
        # Read shape file
        geo_df = gpd.read_file(file_path)
    except:  # bare except should be changed, will do so in later interation
        print('Ensure you have imported geo_data sub-folder')

    local_date['name'] = \
        local_date['name'].replace(['Cornwall and Isles of Scilly'],
                                   ['Cornwall'])
    merged = geo_df.merge(local_date, how='outer',
                          left_on="lad19nm", right_on="name")
    # Column to plot
    feature = 'case_rate'
    # Plot range
    vmin, vmax = merged['case_rate'].min(), merged['case_rate'].max()
    # Create plot
    fig, ax = plt.subplots(1, figsize=(12, 10))
    # Set style and labels
    ax.axis('off')
    ax.set_title(f'Local rate per 100,000 {recent_date}',
                 fontdict={'fontsize': '20', 'fontweight': '3'})
    ax.annotate('Source: gov.uk'
                + ' https://api.coronavirus.data.gov.uk/v1/data',
                xy=(0.25, .05), xycoords='figure fraction',
                fontsize=12, color='#555555')
    # Create colorbar
    sm = plt.cm.ScalarMappable(cmap='Reds',
                               norm=plt.Normalize(vmin=vmin, vmax=vmax))
    fig.colorbar(sm)
    # Create map
    merged.plot(column=feature, cmap='Reds', linewidth=0.2, ax=ax,
                edgecolor='0.8')
    plt.show()
    if save:
        image = merged.plot(column=feature, cmap='Reds', linewidth=0.2,
                            ax=ax, edgecolor='0.8');
        image.figure.savefig(f'{date_selector}-local_rate_plot')


def local_cases_plot(save=False):
    """Plot local case numbers on a map of the UK.

    Function collects data using CovidData get_regional_data method.

    Args:
        save (bool, optional): If true will save plot. Defaults to False.
    """
    # Find latest data
    recent_date = CovidData().get_regional_data()
    recent_date = recent_date['date'][0]
    # Select latest data from local data
    local = CovidData().get_local_data(date=recent_date)
    date_selector = recent_date
    local_date = local.loc[local['date'] == date_selector,
                           ['date', 'name', 'case_newDaily']]
    file_path = my_path() / "Local_Authority_Districts.shp"
    # Check required file exists
    try:
        # Read shape file
        geo_df = gpd.read_file(file_path)

    except:  # bare except should be changed, will do so in later interation
        print('Ensure you have imported geo_data sub-folder')
    local_date['name'] = \
        local_date['name'].replace(['Cornwall and Isles of Scilly'],
                                   ['Cornwall'])
    merged = geo_df.merge(local_date, how='outer',
                          left_on="lad19nm", right_on="name")
    # Column to plot
    feature = 'case_newDaily'
    # Plot range
    vmin, vmax = merged['case_newDaily'].min(), \
        merged['case_newDaily'].max()
    # Create plot
    fig, ax = plt.subplots(1, figsize=(12, 10))
    # Set style and labels
    ax.axis('off')
    ax.set_title(f'Number of new cases by local authority {recent_date}',
                 fontdict={'fontsize': '20', 'fontweight': '3'})
    ax.annotate('Source: gov.uk'
                + ' https://api.coronavirus.data.gov.uk/v1/data',
                xy=(0.25, .05), xycoords='figure fraction',
                fontsize=12, color='#555555')
    # Create colorbar
    sm = plt.cm.ScalarMappable(cmap='Reds',
                               norm=plt.Normalize(vmin=vmin, vmax=vmax))
    fig.colorbar(sm)
    # Create map
    merged.plot(column=feature, cmap='Reds', linewidth=0.2, ax=ax,
                edgecolor='0.8')
    plt.show()
    if save:
        image = merged.plot(column=feature, cmap='Reds', linewidth=0.2,
                            ax=ax, edgecolor='0.8');
        image.figure.savefig(f'{date_selector}-local_cases_plot')


def case_demographics(df):
    """Produce a plot of the age demographics of cases across England.

    Args:
        df (DataFrame): this must be the dataframe produced by the
                        get_regional_data method from the CovidData class
    Returns:
        Plot of case numbers broken down by age
    """
    validate_input(df)
    df_list = df.loc[:, ['cases_demographics', 'date']]
    age_df = []
    for i in range(df_list.shape[0]):
        if df_list.iloc[i, 0]:
            temp_df = pd.DataFrame(df_list.iloc[i, 0])
            temp_df['date'] = df_list.iloc[i, 1]
            temp_df = temp_df.pivot(values='rollingRate',
                                    columns='age', index='date')
            age_df.append(temp_df)
    data = pd.concat(age_df)
    data.index = pd.to_datetime(data.index)
    data = \
        data.assign(under_15=(data['00_04']+data['05_09']+data['10_14'])/3,
                    age_15_29=(data['15_19']+data['20_24']+data['25_29'])/3,
                    age_30_39=(data['30_34']+data['35_39'])/2,
                    age_40_49=(data['40_44']+data['45_49'])/2,
                    age_50_59=(data['50_54']+data['55_59'])/2)
    data.drop(columns=['00_04', '00_59', '05_09', '10_14', '15_19', '20_24',
                       '25_29', '30_34', '35_39', '40_44', '45_49', '50_54',
                       '55_59', '60_64', '65_69', '70_74', '75_79', '80_84',
                       '85_89', '90+', 'unassigned'], inplace=True)
    date = data.index[0].strftime('%d-%b-%y')
    ready_df = data.resample('W').mean()
    ready_df.plot(figsize=(15, 10), subplots=True, layout=(3, 3),
                  title=f'{date} - England case rate per 100,000 by age'
                  + ' (weekly)')
    plt.style.use('ggplot')
    plt.show()


def vaccine_demographics(df):
    """Plot of the age demographics of third vaccine uptake across England.

    Args:
        df ([DataFrame]): this must be the dataframe produced by the
                          get_regional_data method from the CovidData class
    Returns:
        Plot of cumulative third vaccination numbers broken down by age.
    """
    validate_input(df)
    df_list = df.loc[:, ['vac_demographics', 'date']]
    age_df = []
    for i in range(df_list.shape[0]):
        if df_list.iloc[i, 0]:
            temp_df = pd.DataFrame(df_list.iloc[i, 0])
            temp_df['date'] = df_list.iloc[i, 1]
            temp_df =\
                temp_df.pivot(values=
            'cumVaccinationThirdInjectionUptakeByVaccinationDatePercentage',
                              columns='age', index='date')
            age_df.append(temp_df)
    data = pd.concat(age_df)
    data.index = pd.to_datetime(data.index)
    date = data.index[0].strftime('%d-%b-%y')
    ready_df = data.resample('W').mean()
    ready_df.plot(figsize=(15, 10), subplots=True, layout=(6, 3),
                  title=f'{date} - England vaccine booster uptake (%) by age'
                  + ' (weekly)')
    plt.style.use('ggplot')
    plt.show()


def death_demographics(df):
    """Plot of the age demographics of rate of deaths across England.

    Args:
        df (DataFrame): this must be the dataframe produced by the
                        get_regional_data method from the CovidData class
    Returns:
        Plot of death rate per 100,000 broken down by age.
    """
    validate_input(df)
    df_list = df.loc[:, ['death_Demographics', 'date']]
    age_df = []
    for i in range(df_list.shape[0]):
        if df_list.iloc[i, 0]:
            temp_df = pd.DataFrame(df_list.iloc[i, 0])
            temp_df['date'] = df_list.iloc[i, 1]
            temp_df = temp_df.pivot(values='rollingRate',
                                    columns='age', index='date')
            age_df.append(temp_df)
    data = pd.concat(age_df)
    data.index = pd.to_datetime(data.index)
    data = \
        data.assign(under_15=(data['00_04']+data['05_09']+data['10_14'])/3,
                    age_15_29=(data['15_19']+data['20_24']+data['25_29'])/3,
                    age_30_39=(data['30_34']+data['35_39'])/2,
                    age_40_49=(data['40_44']+data['45_49'])/2,
                    age_50_59=(data['50_54']+data['55_59'])/2)
    data.drop(columns=['00_04', '00_59', '05_09', '10_14', '15_19', '20_24',
                       '25_29', '30_34', '35_39', '40_44', '45_49', '50_54',
                       '55_59', '60_64', '65_69', '70_74', '75_79', '80_84',
                       '85_89', '90+'], inplace=True)

    date = data.index[0].strftime('%d-%b-%y')
    ready_df = data.resample('W').mean()
    ready_df.plot(figsize=(15, 10), subplots=True, layout=(3, 3),
                  title=f'{date} - England death rate per 100,000 by age'
                  + ' (weekly)')
    plt.style.use('ggplot')
    plt.show()


def daily_deaths(df, pan_duration=pan_duration, save=False):
    """Plot number of people died per day within 28 days of 1st +ve test.

       COVID-19 deaths over time, from the start of the pandemic March 2020.

    Args:
        df (DataFrame): requires data from get_uk_data method
        pan_duration (function, optional): use pre specified pan_duration.
        Defaults to pan_duration.
        save (bool, optional): [description]. Defaults to False.
    Returns:
        Matplotlib plot, styled using matplotlib template 'ggplot'
    """
    daily_deaths = df['death_dailyDeaths'].to_list()
    date = df['date'].to_list()
    # cumulative = df['case_cumulativeCases'].to_list()
    # Find date of highest number of daily cases
    high, arg_high = max(daily_deaths), daily_deaths.index(max(daily_deaths))
    # daily = df['death_dailyDeaths'][0]
    high_date = date[arg_high].strftime('%d %b %Y')
    # added the number of death for the last seven days
    duration = pan_duration(date=date)
    # Create matplotlib figure and specify size
    fig = plt.figure(figsize=(12, 10))
    plt.style.use('ggplot')
    ax = fig.add_subplot()
    # Plot varibles
    ax.plot(date, daily_deaths)

    # Style and label plot
    ax.set_xlabel('Date')
    ax.set_ylabel('Daily deaths')
    ax.fill_between(date, daily_deaths,
                    alpha=0.3)
    ax.set_title('Deaths within 28 days of positive test (UK)',
                 fontsize=18)

    at = AnchoredText(f"Most recent daily deaths\n{daily_deaths[0]:,.0f}\
                      \nMax daily deaths\n{high:,.0f}: {high_date}\
                      \nPandemic duration\n{duration} days",
                      prop=dict(size=16), frameon=True, loc='upper left')

    # \nCumulative cases\n{cumulative[0]:,.0f}\
    at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
    ax.add_artist(at)
    ax.annotate('Source: gov.uk https://api.coronavirus.data.gov.uk/v1/data',
                xy=(0.25, 0.0175), xycoords='figure fraction',
                fontsize=12, color='#555555')

    if save:
        plt.savefig(f"casenumbers{date[0].strftime('%Y-%m-%d')}")
    plt.show()


def cumulative_deaths(df, pan_duration=pan_duration, save=False):
    """Plot cum number of people who died within 28 days of +ve test.

        Total COVID-19 deaths over time, from the start of the
        pandemic March 2020.

    Args:
        df (DataFrame): containing covid data retrieved from CovidData
        pan_duration ([function], optional): Defaults to pan_duration.
        save (bool, optional): True to save plot. Defaults to False.
    Returns:
        Matplotlib plot, styled using matplotlib template 'ggplot'
    """
    df = df.fillna(0)
    cum_deaths = df["death_cumulativeDeaths"].to_list()
    date = df['date'].to_list()
    # cumulative = df['death_cumulativeDeaths'].to_list()
    # Find date of highest number of daily cases
    high, arg_high = max(cum_deaths), cum_deaths.index(max(cum_deaths))
    # daily = df["death_cumulativeDeaths"][0]
    high_date = date[arg_high].strftime('%d %b %Y')
    # added the number of death for the last seven days
    duration = pan_duration(date=date)
    # Create matplotlib figure and specify size
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot()
    # Plot varibles
    ax.plot(date, cum_deaths)
    # Style and label plot
    ax.set_xlabel('Date')
    ax.set_ylabel('Cumulative deaths')
    ax.fill_between(date, cum_deaths,
                    alpha=0.3)
    ax.set_title('Cumulative deaths within 28 days of positive test (UK)',
                 fontsize=18)
    at = AnchoredText(f"Last cumulative deaths\n{high:,.0f}: {high_date}\
                      \nPandemic duration\n{duration} days",
                      prop=dict(size=16), frameon=True, loc='upper left')
    # \nCumulative cases\n{cumulative[0]:,.0f}\
    at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
    ax.add_artist(at)
    ax.annotate('Source: gov.uk https://api.coronavirus.data.gov.uk/v1/data',
                xy=(0.25, 0.0175), xycoords='figure fraction',
                fontsize=12, color='#555555')
    plt.style.use('ggplot')
    if save:
        plt.savefig(f"casenumbers{date[0].strftime('%Y-%m-%d')}")
    plt.show()


def regional_plot_death_rate(save=False):
    """Plot regional deaths rate per 100,000 on a map of the UK.

    Function collects data using CovidData get_regional_data method.

    Args:
        save (bool, optional): True will save plot. Defaults to False.
    Returns:
        Plot of regional case rate on map of UK
    """
    # Collect data
    regions = CovidData().get_regional_data()
    scotland = CovidData(nation='scotland').get_national_data()
    wales = CovidData(nation='wales').get_national_data()
    ni = CovidData(nation='northern ireland').get_national_data()

    # Set date to plot
    date_selector = regions['date'][7]
    regions_date = regions.loc[regions['date'] == date_selector]
    scotland_date = scotland.loc[scotland['date'] == date_selector,
                                 ['date', 'name', 'death_newDeathRate']]
    wales_date = wales.loc[wales['date'] == date_selector,
                           ['date', 'name', 'death_newDeathRate']]
    ni_date = ni.loc[ni['date'] == date_selector,
                     ['date', 'name', 'death_newDeathRate']]
    # Combine regional data into single dataframe
    final_df = pd.concat([regions_date, scotland_date, wales_date, ni_date],
                         axis=0)
    file_path = my_path() / 'NUTS_Level_1_(January_2018)_Boundaries.shp'
    # Check required file exists
    try:
        # Read shape file
        geo_df = gpd.read_file(file_path)
    except:  # bare except should be changed, will do so in later interation
        print('Ensure you have imported geo_data sub-folder')
    geo_df['nuts118nm'] = \
        geo_df['nuts118nm'].replace(['North East (England)',
                                     'North West (England)',
                                     'East Midlands (England)',
                                     'West Midlands (England)',
                                     'South East (England)',
                                     'South West (England)'],
                                    ['North East', 'North West',
                                     'East Midlands', 'West Midlands',
                                     'South East', 'South West'])
    merged = geo_df.merge(final_df, how='left', left_on="nuts118nm",
                          right_on="name")
    # Column to plot
    feature = 'death_newDeathRate'
    # Plot range
    feature_min, feature_max = merged['death_newDeathRate'].min(),\
        merged['death_newDeathRate'].max()
    # Create plot
    fig, ax = plt.subplots(1, figsize=(12, 10))
    # Set style and labels
    ax.axis('off')
    ax.set_title('Regional rate per 100,000 (new deaths)',
                 fontdict={'fontsize': '20', 'fontweight': '3'})
    ax.annotate('Source: gov.uk \
                https://api.coronavirus.data.gov.uk/v1/data',
                xy=(0.25, .05), xycoords='figure fraction',
                fontsize=12, color='#555555')
    # Create colorbar
    sm = plt.cm.ScalarMappable(cmap='Reds',
                               norm=plt.Normalize(vmin=feature_min,
                                                  vmax=feature_max))
    fig.colorbar(sm)
    # Create map
    merged.plot(column=feature, cmap='Reds', linewidth=0.8, ax=ax,
                edgecolor='0.8')
    plt.show()
    if save:
        image = merged.plot(column=feature, cmap='Reds', linewidth=0.8,
                            ax=ax, edgecolor='0.8')
        image.figure.savefig(f'caserates{date_selector}')


def regional_deaths_demo(save=False):
    """Plot number of deaths in the UK.

       Plot by age category (>60 , <60). Function collects data using
       CovidData get_regional_data method.

    Args:
        save (bool, optional): True will save plot. Defaults to False.
    Returns:
        Plot of regional deaths by age category (UK)
    """
    CovidDataE = CovidData("england")
    regional = CovidDataE.get_regional_data()
    regional = \
        regional.drop(regional.columns.difference(["date",
                                                   "death_Demographics"]), 1)

    regional
    # remove empty lists in 'death_Demographcs column'
    regional = regional[regional["death_Demographics"].astype(bool)]

    # transform the regional dataframe to have 'age_categories' as columns
    # with 'deaths' values and 'date' as rows
    age_df = []
    for i in range(regional.shape[0]):
        if regional.iloc[i, 1]:
            temp_df = pd.DataFrame(regional.iloc[i, 1])
            temp_df['date'] = regional.iloc[i, 0]
            temp_df = temp_df.pivot(values='deaths', columns=['age'],
                                    index='date')
            age_df.append(temp_df)
    final_death_data = pd.concat(age_df)
    # create a dataframe with columns 'age category' and 'number of deaths'
    age_cat = ['00_04', '00_59', '05_09', '10_14', '15_19', '20_24', '25_29',
               '30_34', '35_39', '40_44', '45_49', '50_54', '55_59', '60+',
               '60_64', '65_69', '70_74', '75_79', '80_84', '85_89', '90+']
    deaths = []
    for ele in age_cat:
        x = final_death_data[ele].sum()
        deaths.append(x)

    deaths_df = pd.DataFrame(list(zip(age_cat, deaths)),
                             columns=['age category', 'number of deaths'])

    # group age categories to have only <60 old years and 60+
    cat_1 = deaths_df.loc[deaths_df['age category'] == '00_59']
    cat_2 = deaths_df.loc[deaths_df['age category'] == '60+']
    below_60 = cat_1['number of deaths'].sum()
    above_60 = cat_2['number of deaths'].sum()
    lst1 = ['<60', '60+']
    lst2 = [below_60, above_60]
    final_deaths_age_cat = pd.DataFrame(list(zip(lst1, lst2)),
                                        columns=['age category',
                                                 'number of deaths'])
    # getting highest number of deaths for each age category

    # PLOTTING A BAR PLOT OF NUMBER OF DEATHS vs AGE CATEGORY
    fig = plt.figure(figsize=(12, 10))

    ax = fig.add_subplot()
    # Plot varibles
    ax.bar(final_deaths_age_cat['age category'],
           final_deaths_age_cat['number of deaths'])
    # plot(date, cum_deaths)

    # Style and label plot
    ax.set_xlabel('Age category')
    ax.set_ylabel('Number of deaths')
    ax.fill_between(final_deaths_age_cat['age category'],
                    final_deaths_age_cat['number of deaths'],
                    alpha=0.3)
    ax.set_title('Number of deaths per age category (England)',
                 fontsize=18)

    at = AnchoredText(f"Number of deaths:\
                      \nAge <60: {below_60}\
                      \nAge >60: {above_60}",
                      prop=dict(size=16), frameon=True, loc='upper left')

    # \nCumulative cases\n{cumulative[0]:,.0f}\
    at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
    ax.add_artist(at)
    ax.annotate('Source: gov.uk https://api.coronavirus.data.gov.uk/v1/data',
                xy=(0.25, 0.0175), xycoords='figure fraction',
                fontsize=12, color='#555555')

    plt.style.use('ggplot')
    plt.show()
    if save:
        date = dt.now()
        plt.savefig(f"casenumbers{date.strftime('%Y-%m-%d')}")


def collect_hosp_data(country='england'):
    """Collect data for hosp and vac functions.

    Args:
        country (str, optional): Select country data. Defaults to 'england'.

    Returns:
        DataFrame: data in correct format for hosp and vac functions
    """
    if country == 'england':
        hosp_data = CovidData("england").get_national_data()
        hosp_data["date"] = hosp_data["date"].astype('datetime64[ns]')
        hosp_data = hosp_data.fillna(0)
        return hosp_data
    else:
        hosp_uk = CovidData("england").get_uk_data()
        hosp_uk["date"] = hosp_uk["date"].astype('datetime64[ns]')
        hosp_uk = hosp_uk.fillna(0)
        return hosp_uk


def hosp_cases_plot():
    """Heatmap for the the daily number of hospital cases (England).

    Args:
        No args required, collects own data.
    Returns :
      Seaborn heatmap plot for the number of hospital cases
      per day of the pandemic.
    """
    hosp_data = collect_hosp_data()
    hosp_cases_col = ["date", "hosp_hospitalCases"]
    hosp_data1 = hosp_data.loc[:, hosp_cases_col]
    hosp_data1.loc[:, ["Day"]] = hosp_data1["date"].apply(lambda x: x.day)
    hosp_data1["date"] = hosp_data1.date.dt.strftime("%Y-%m")
    newpivot = hosp_data1.pivot_table("hosp_hospitalCases", index="date",
                                      columns="Day")
    cmap = sns.cm.rocket_r
    plt.figure(figsize=(16, 9))
    hm2 = sns.heatmap(newpivot, cmap=cmap)
    hm2.set_title("Heatmap of the daily number of hospital cases (England)",
                  fontsize=14)
    hm2.set_xlabel("Day", fontsize=12)
    hm2.set_ylabel("Month and Year", fontsize=12)


def hosp_newadmissions_plot():
    """Heatmap for the the daily number of new hospital admissions (England).

    Args:
        No args required, collects own data.
    Returns :
        Seaborn heatmap plot for the number of new hospital admissions per day
        of the pandemic.
    """
    hosp_data = collect_hosp_data()
    hosp_cases_col = ["date", "hosp_newAdmissions"]
    hosp_data2 = hosp_data.loc[:, hosp_cases_col]
    hosp_data2["Day"] = hosp_data2.date.apply(lambda x: x.day)
    hosp_data2["date"] = hosp_data2.date.dt.strftime("%Y-%m")
    newpivot = hosp_data2.pivot_table("hosp_newAdmissions", index="date",
                                      columns="Day")
    cmap = sns.cm.rocket_r
    plt.figure(figsize=(16, 9))
    hm1 = sns.heatmap(newpivot, cmap=cmap)
    hm1.set_title("Heatmap of the daily number of new hospital admissions"
                  + " (England)", fontsize=14)
    hm1.set_xlabel("Day", fontsize=12)
    hm1.set_ylabel("Month and Year", fontsize=12)


def hosp_newadmissionschange_plot():
    """Change in hospital admissions (England).

       Plot difference between the number of new hospital admissions
       during the latest 7-day period and the previous non-overlapping week.

    Args:
        No args required, collects own data.
    Returns :
        Lineplot of this difference over the months.
    """
    hosp_data = collect_hosp_data()
    hosp_cases_col = ["date", "hosp_newAdmissionsChange"]
    hosp_data3 = hosp_data.loc[:, hosp_cases_col]
    x = hosp_data3["date"].dt.strftime("%Y-%m")
    y = hosp_data3["hosp_newAdmissionsChange"]
    fig, ax = plt.subplots(1, 1, figsize=(20, 3))
    sns.lineplot(x=x, y=y, color="g")
    ax.set_title("Daily new admissions change (England)", fontsize=14)
    ax.invert_xaxis()
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("New Admissions Change", fontsize=12)


def hosp_occupiedbeds_plot():
    """Plot daily number of COVID-19 patients in mechanical ventilator beds.

    Plots information for England.

    Args:
        No args required, collects own data.
    Returns :
        - Lineplot of this difference over the months.
    """
    hosp_data = collect_hosp_data()
    hosp_cases_col = ["date", "hosp_covidOccupiedMVBeds"]
    hosp_data4 = hosp_data.loc[:, hosp_cases_col]
    fig, ax = plt.subplots(1, 1, figsize=(20, 3))
    sns.lineplot(x=hosp_data4["date"].dt.strftime("%Y-%m"),
                 y=hosp_data4["hosp_covidOccupiedMVBeds"], ax=ax, color="b")
    ax.set_title("Daily number of COVID occupied Mechanical Ventilator beds"
                 + " (England)", fontsize=14)
    ax.invert_xaxis()
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Number of occupied MV beds", fontsize=12)


def hosp_casesuk_plot():
    """Heatmap for the the daily number of hospital cases in UK.

    Args:
        No args required, collects own data.
    Returns :
      Seaborn heatmap plot for the number of hospital cases
      per day of the pandemic.
    """
    hosp_uk = collect_hosp_data(country='uk')
    hosp_cases_col = ["date", "hosp_hospitalCases"]
    hosp_data1 = hosp_uk.loc[:, hosp_cases_col]
    hosp_data1["Day"] = hosp_data1["date"].apply(lambda x: x.day)
    hosp_data1["date"] = hosp_data1.date.dt.strftime("%Y-%m")
    newpivot = hosp_data1.pivot_table("hosp_hospitalCases", index="date",
                                      columns="Day")
    cmap = sns.cm.rocket_r
    plt.figure(figsize=(16, 9))
    hm2 = sns.heatmap(newpivot, cmap=cmap)
    hm2.set_title("Heatmap of the daily number of hospital cases in the UK",
                  fontsize=14)
    hm2.set_xlabel("Day", fontsize=12)
    hm2.set_ylabel("Month and Year", fontsize=12)


def hosp_newadmissionsuk_plot():
    """Heatmap for the the daily number of new hospital admissions (UK).

    Args:
        No args required, collects own data.
    Returns :
        Seaborn heatmap plot for the number of new hospital admissions per day
        of the pandemic (UK).
    """
    hosp_uk = collect_hosp_data(country='uk')
    hosp_cases_col = ["date", "hosp_newAdmissions"]
    hosp_data2 = hosp_uk.loc[:, hosp_cases_col]
    hosp_data2["Day"] = hosp_data2.date.apply(lambda x: x.day)
    hosp_data2["date"] = hosp_data2.date.dt.strftime("%Y-%m")
    newpivot = hosp_data2.pivot_table("hosp_newAdmissions", index="date",
                                      columns="Day")
    cmap = sns.cm.rocket_r
    plt.figure(figsize=(16, 9))
    hm1 = sns.heatmap(newpivot, cmap=cmap)
    hm1.set_title("Heatmap of the daily number of new hospital admissions"
                  + " in the UK", fontsize=14)
    hm1.set_xlabel("Day", fontsize=12)
    hm1.set_ylabel("Month and Year", fontsize=12)


def hosp_occupiedbedsuk_plot():
    """Plot daily number of COVID-19 patients in mechanical ventilator beds.

    Plots information for UK.

    Args:
        No args required, collects own data.
    Returns :
        - Lineplot of this difference over the months.
    """
    hosp_uk = collect_hosp_data(country='uk')
    hosp_cases_col = ["date", "hosp_covidOccupiedMVBeds"]
    hosp_data4 = hosp_uk.loc[:, hosp_cases_col]
    fig, ax = plt.subplots(1, 1, figsize=(20, 3))
    sns.lineplot(x=hosp_data4["date"].dt.strftime("%Y-%m"),
                 y=hosp_data4["hosp_covidOccupiedMVBeds"], ax=ax, color="b")
    ax.set_title("Daily number of COVID occupied Mechanical Ventilator"
                 + " beds in the UK", fontsize=14)
    ax.invert_xaxis()
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Number of occupied MV beds", fontsize=12)


def vaccine_percentage(df):
    """Plot the percentage of the vaccinated population over time.

    Args:
        df (DataFrame): Requires data returned by get_uk_data
        or get_national_data methods
    Retuns:
        Plot of total percentage of population vaccinated
    """
    df['date'] = df['date'].astype('datetime64[ns]')
    plt.figure(figsize=(14, 7))
    plot1 = sns.lineplot(x='date', y='vac_total_perc', data=df)
    plt.ylim(0, 100)
    plot1.set_xlabel("Covid pandemic, up to date", fontsize=12)
    plot1.set_ylabel("Percentage", fontsize=12)
    plot1.set_title('Percentage of the vaccinated population over time',
                    fontsize=14)
    # print(plot1)


def vaccine_doses_plot(df):
    """Pllot both the first and second doses of vaccines.

    Daily information.

    Args:
        df (DataFrame): Requires data returned by get_national_data
    Returns:
        Plots of first and second vaccine doses since start of pandemic
        records
    """
    df['date'] = df['date'].astype('datetime64[ns]')
    keep_col = ['date', 'vac_first_dose', 'vac_second_dose']
    vaccines_melted = df[keep_col]
    vaccines_melted = vaccines_melted.melt('date', var_name="vaccine_doses",
                                           value_name='count')
    plt.figure(figsize=(14, 7))
    plot = sns.lineplot(x='date', y='count', hue='vaccine_doses',
                        data=vaccines_melted)
    plt.grid()
    plt.ylim(0, 50000000)
    plot.set_ylabel("count", fontsize=12)
    plot.set_xlabel("Covid pandemic, up to date", fontsize=12)
    plot.set_title('daily amount of first and second doses' +
                   ' of vaccination administered', fontsize=14)
    # use hue = column to categorise the data
    # print(plot)


def first_vaccination_hm(df):
    """Plot a heatmap of the first vaccine dose (daily).

    Args:
        df (DataFrame): Requires data returned by get_national_data
    Returns:
        Heatmap of first vaccine doses over time
    """
    df['date'] = df['date'].astype('datetime64[ns]')
    df = df.fillna(0)
    keep_col_hm = ['date', 'vac_first_dose']
    vaccines_hm = df.loc[:, keep_col_hm]
    vaccines_hm["Day"] = vaccines_hm.date.apply(lambda x: x.strftime("%d"))
    vaccines_hm.pivot_table(index="Day", columns="date",
                            values="vac_first_dose")
    vaccines_hm.date = vaccines_hm.date.dt.strftime('%Y-%m')

    keep_colu = ['date', 'Day', 'vac_first_dose']
    vaccines_hm = vaccines_hm[keep_colu]

    pivoted = vaccines_hm.pivot(columns='Day',
                                index='date',
                                values='vac_first_dose')

    pivoted = pivoted.fillna(0)

    plt.figure(figsize=(16, 9))
    cmap = sns.cm.rocket_r
    plot_hm1 = sns.heatmap(pivoted, cmap=cmap)
    plot_hm1.set_title('heatmap of the first vaccination dose' +
                       ' administered daily', fontsize=14)
    plot_hm1.set_ylabel('Year and month', fontsize=12)
    # print(plot_hm1)


def second_vaccination_hm(df):
    """Plot a heatmap of the second vaccine dose (daily).

    Args:
        df (DataFrame): Requires data returned by get_national_data
    Returns:
        Heatmap of second vaccine doses over time
    """
    df['date'] = df['date'].astype('datetime64[ns]')
    df = df.fillna(0)
    keep_col_hm = ['date', 'vac_second_dose']
    vaccines_hm = df.loc[:, keep_col_hm]
    vaccines_hm["Day"] = vaccines_hm.date.apply(lambda x: x.strftime("%d"))
    vaccines_hm.pivot_table(index="Day", columns="date",
                            values="vac_second_dose")
    vaccines_hm.date = vaccines_hm.date.dt.strftime('%Y-%m')
    keep_colu = ['date', 'Day', 'vac_second_dose']
    vaccines_hm = vaccines_hm[keep_colu]
    pivoted = vaccines_hm.pivot(columns='Day',
                                index='date',
                                values='vac_second_dose')
    pivoted = pivoted.fillna(0)
    plt.figure(figsize=(16, 9))
    cmap = sns.cm.rocket_r
    plot_hm2 = sns.heatmap(pivoted, cmap=cmap)
    plot_hm2.set_title('heatmap of the second vaccination dose' +
                       ' administered daily', fontsize=14)
    plot_hm2.set_ylabel('Year and month', fontsize=12)
    # print(plot_hm2)


def vaccines_across_regions(vaccines2):
    """Plot graph of the vaccination uptake percentage by English regions.

    Args:
        vaccines2 (DataFrame): data from get_regional_data required

    Returns:
        plot of vaccine uptake by regions in England
    """
    keep_fd = ['date', 'name', 'vac_firstDose']
    vaccines2['date'] = vaccines2['date'].astype('datetime64[ns]')
    vaccines_fd = vaccines2.loc[:, keep_fd]
    vaccines_fd.fillna(0, inplace=True)
    vaccines_fd

    plt.figure(figsize=(16, 9))
    plot_fd = sns.lineplot(x='date', y='vac_firstDose', hue='name',
                           data=vaccines_fd)
    plt.ylim(0, 100)
    plt.grid()
    plot_fd.set_ylabel("percentage", fontsize=12)
    plot_fd.set_xlabel("Covid pandemic, up to date", fontsize=12)
    plot_fd.set_title('Vaccination uptake by region', fontsize=14)
    # print(plot_fd)
