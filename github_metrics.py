#!/usr/bin/env python

"""
Utility for creating a table of statistics for given repository on Github

Snapshot metrics:
- Open PR
- Open Issues
- Stars
- Forks

Delta metrics:
- PR opened
- PR merged
- PR closed
- Issue opened
- Issue closed
- Starred
"""

from datetime import datetime
import time
import dateutil.relativedelta
import getpass
import os
import argparse
from github import Github
import pandas as pd

dir_path = os.path.dirname(os.path.realpath(__file__))
month = dateutil.relativedelta.relativedelta(months=1)


def create_dates_range(start_date, end_date):
    """
    Defining a list of dates whith month interval
    if end_date is later then today then list will end with today's date
    """
    today = datetime.today()
    if end_date > today:
        end_date = today
        today_last = True

    dates = []
    date = start_date - month
    while date < end_date:
        dates.append(date)
        date += month
    if today_last:
        dates.append(today)
    return dates


def state_func_at(item, state):
    """
    Returns functions of the item based on its state
    """
    if state == "created":
        return item.created_at
    elif state == "closed":
        return item.closed_at
    elif state == "merged":
        return item.merged_at
    elif state == "starred":
        return item.starred_at
    else:
        raise ValueError("Only 4 values allowed :'created', 'closed', 'merged', 'starred")


def snapshot_metric(items_list, date):
    """
    Evaluates snapshot metric on given date
    """
    num = 0
    if datetime.today() < date:
        return None
    for item in items_list:
        if state_func_at(item, "created") <= date:
            if state_func_at(item, "closed") is None or state_func_at(item, "closed") > date:
                num += 1
        else:
            continue
    return num


def add_count_metric(data, position, dates, items_list, state):
    """
    Function for evaluation Stars and Forks 
    and adding to data dictionary
    :returns data
    """
    total = items_list.totalCount
    dates = dates[1:]
    date = dates.pop()
    i, j = 0, 0
    for item in items_list.reversed:
        if state_func_at(item, state) < date:
            data[len(dates)-j+1][position] = total-i
            if not dates:
                break
            else:
                date = dates.pop()
            j += 1
        i += 1
    return data


def delta_metric(items_list, date1, date2, state):
    """
    Evaluates delta metric in given interval of dates
    """
    num = 0
    if datetime.today() < date1:
        return None
    for item in items_list:
        if state_func_at(item, state) is not None and \
            state_func_at(item, state) >= date1 and state_func_at(item, state) < date2:
            num += 1
        else:
            continue
    return num


def main():

    parser = argparse.ArgumentParser(
        description='Collecting statistics for repository on Github')

    parser.add_argument(
        '--repo_url',
        '-repo',
        dest='repo_url',
        type=str,
        default="opencv/opencv",
        help='Url of repository to collect statistics in format: "OWNER/REPOSITORY_NAME"')
    parser.add_argument(
        '-print',
        dest='console',
        type=bool,
        default=True,
        help='Flag to print result DataFrame in console')
    parser.add_argument(
        '-login',
        dest='login',
        type=str,
        default='sergeisoly',
        help='Login to access Github statistics of traffic and clones of repository')
    parser.add_argument(
        '-password',
        dest='password',
        type=str,
        default='nepisu72',
        help='Password from Github login')
    parser.add_argument(
        '-csv',
        dest='save_to_csv',
        type=bool,
        default=True,
        help='Flag to save resulting DataFrame in csv format')
    parser.add_argument(
        '-path',
        dest='csv_path',
        type=str,
        default=dir_path,
        help='Path to save result DataFrame in csv format. default is script directory')
    parser.add_argument(
        '-start_date',
        dest='start_date',
        type=str,
        default="2019-01-01",
        help='The date from which to start collecting statistics in format: "YYYY-MM-DD". default="2019-01-01"')
    parser.add_argument(
        '-end_date',
        dest='end_date',
        type=str,
        default="2019-12-01",
        help='The end date of collecting statistics in format: "YYYY-MM-DD". default="2019-12-01"')
    args = parser.parse_args()

    start_date = datetime.strptime(args.start_date, "%Y-%m-%d")   
    end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
    dates = create_dates_range(start_date, end_date)

    print(f"You should provide access to your Github user account \nbecause of Github API constraints")
    login = getpass.getpass("Login:")
    passwd = getpass.getpass("Password:")

    start_time = time.time() # start point for evaluating time of running the script

    print("Getting access to GitHub...")
    try:
        g = Github(login, passwd)
    except:
        print("Authentification error!")
    repo = g.get_repo(args.repo_url)
    repo_name = repo.name

    # Getting pull_requests and issues then
    # to increase efficiency cutting such of them
    # that do not belong to needed dates range

    # TODO find more efficient way to exctract pulls and issues.
    # now it takes too much time
    print(f"Getting pull requests from {repo_name} ...")
    pulls = repo.get_pulls(state='all', base='master')
    pulls = [pr for pr in pulls if pr.closed_at is None or pr.closed_at >= start_date - month]

    print(f"Getting issues from {repo_name} ...")
    issues = repo.get_issues(state='all')
    issues = [issue for issue in issues if issue.closed_at is None or issue.closed_at >= start_date - month]

    print(f"Getting stargazers of {repo_name} ...")
    stargazers = repo.get_stargazers_with_dates()

    print(f"Getting forks of {repo_name} ...")
    forks = repo.get_forks()

    print(f"Creating DataFrame of {repo_name} statistics...")

    # Delta metrics evaluated to month period
    # that was before current date in dates list
    # so the range starts whith 1 not 0

    data = {i:  # cuttind dates for better visibility
               [dates[i].replace(hour=0, minute=0, second=0, microsecond=0),
                snapshot_metric(pulls, dates[i]),
                snapshot_metric(issues, dates[i]),
                0,  # place for Stars metric
                0,  # place for Forks metric
                delta_metric(pulls, dates[i-1], dates[i], 'created'),
                delta_metric(pulls, dates[i-1], dates[i], 'merged'),
                delta_metric(pulls, dates[i-1], dates[i], 'closed'),
                delta_metric(issues, dates[i-1], dates[i], 'created'),
                delta_metric(issues, dates[i-1], dates[i], 'closed')]
            for i in range(1, len(dates))}

    # Counting Stars
    data = add_count_metric(data, 3, dates, stargazers, 'starred')
    # Counting Forks
    data = add_count_metric(data, 4, dates, forks, 'created')

    columns = ["Period", "Open PR", "Open issues", "Stars", "Forks", "PR opened",
               "PR merged", "PR closed", "Issue opened", "Issue closed"]
    df = pd.DataFrame.from_dict(data, orient='index', columns=columns)

    if args.console is True:
        print(df.to_string())

    if args.save_to_csv is True:
        file_name = f"{args.csv_path}/Github_stats_{repo_name}.csv"
        print(f"Saving DataFrame to csv file {file_name}")
        df.to_csv(file_name, index=True)

    print(f"Script execution took {(time.time()-start_time)/60:.2f} minutes")

if __name__ == "__main__":
    main()
