#!/usr/bin/env python3

"""
Utility for creating a table of statistics for given repository on Github

Snapshot metrics:
- Open PR
- Open Issues
- Stars

Delta metrics:
- PR opened
- PR merged
- PR closed
- Issue opened
- Issue closed
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


def snapshot_metric(items_list, date, item_type):
    """
    Evaluates snapshot metric on given date
    """
    num = 0
    if datetime.today() < date:
        return None
    for item in items_list:
        if state_func_at(item, "created") <= date:
            if item_type == "pulls":
                if state_func_at(item, "closed") is None or state_func_at(item, "closed") > date:
                    if state_func_at(item, "merged") is None or state_func_at(item, "merged") > date:
                        num += 1
            elif item_type == "issues":
                if state_func_at(item, "closed") is None or state_func_at(item, "closed") > date:
                    num += 1
                  
            else: print("Now it possible only for pull and issues")
        else:
            continue
    return num


def add_stars(data, position, dates, items_list, state):
    """
    Function for evaluation Stars
    and adding to data dictionary
    :returns data
    """
    total = items_list.totalCount
    dates = dates[1:]
    length = len(dates)
    date = dates.pop()
    i, j = 0, 0
    for item in items_list.reversed:
        if state_func_at(item, state) < date:
            data[length-j][position] = total-i
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
        '-repo', '--repo',
        type=str,
        help='Url of repository to collect statistics in format: "OWNER/REPOSITORY_NAME"')
    parser.add_argument(
        '-start', '--start_date',
        dest='start_date',
        type=str,
        default="2019-01-01",
        help='The date from which to start collecting statistics in format: "YYYY-MM-DD". default="2019-01-01"')
    parser.add_argument(
        '-end', '--end_date',
        type=str,
        default="2019-12-01",
        help='The end date of collecting statistics in format: "YYYY-MM-DD". default="2019-12-01"')
    parser.add_argument(
        '-p', '--print_table',
        type=bool,
        default=True,
        help='Flag to print result DataFrame in console. default = True')
    parser.add_argument(
        '-csv', '--save_to_csv',
        type=bool,
        default=True,
        help='Flag to save resulting DataFrame in csv format. default = True')
    parser.add_argument(
        '-path', '--csv_path',
        type=str,
        default=dir_path,
        help='Path to save result DataFrame in csv format. default is script directory')
    args = parser.parse_args()

    start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
    dates = create_dates_range(start_date, end_date)

    print("You should provide access to your Github user account because of Github API constraints")
    login = getpass.getpass("Login:")
    passwd = getpass.getpass("Password:")

    # start point for evaluating time of running the script
    start_time = time.time()

    print("Getting access to GitHub...")
    try:
        g = Github(login, passwd)
    except:
        print("Authentification error!")

    repo = g.get_repo(args.repo)
    repo_name = repo.name

    # Getting pull_requests and issues then
    # to increase efficiency cutting such of them
    # that do not belong to needed dates range

    print(f"Getting pull requests from {repo_name} ... ")
    pulls = repo.get_pulls(state='all')
    pulls = [pr for pr in pulls if pr.closed_at is None or pr.closed_at >= start_date - month]

    print(f"Getting issues from {repo_name} ...")

    # Only issues that suit dates range and not pull request issues added
    issues = repo.get_issues(state='all')
    issues = [issue for issue in issues if issue.pull_request is None
              and (issue.closed_at is None or issue.closed_at >= start_date - month)]

    print(f"Getting stargazers of {repo_name} ... ")
    stargazers = repo.get_stargazers_with_dates()

    print(f"Creating DataFrame of {repo_name} statistics... ", end="\n\n")

    # Delta metrics evaluated to month period
    # that was before current date in dates list
    # so the range starts whith 1 not 0

    data = {i:  # cuttind dates for better visibility
               [dates[i].replace(hour=0, minute=0, second=0, microsecond=0),
                snapshot_metric(pulls, dates[i], item_type='pulls'),
                snapshot_metric(issues, dates[i], item_type='issues'),
                0,  # place for Stars metric
                delta_metric(pulls, dates[i-1], dates[i], 'created'),
                delta_metric(pulls, dates[i-1], dates[i], 'merged'),
                delta_metric(pulls, dates[i-1], dates[i], 'closed'),
                delta_metric(issues, dates[i-1], dates[i], 'created'),
                delta_metric(issues, dates[i-1], dates[i], 'closed')]
            for i in range(1, len(dates))}

    # Counting Stars
    data = add_stars(data, 3, dates, stargazers, 'starred')

    columns = ["Period", "Open PR", "Open issues", "Stars", "PR opened",
               "PR merged", "PR closed", "Issue opened", "Issue closed"]
    df = pd.DataFrame.from_dict(data, orient='index', columns=columns)

    if args.print_table is True:
        print(df.to_string(), end="\n\n")

    if args.save_to_csv is True:
        file_name = f"{args.csv_path}/Github_stats_{repo_name}.csv"
        print(f"Saving DataFrame to csv file {file_name} ")
        df.to_csv(file_name, index=False)

    print(f"Script execution took {(time.time()-start_time)/60:.2f} minutes ", end="\n\n")

if __name__ == "__main__":
    main()
