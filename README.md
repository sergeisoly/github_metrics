# github_metrics
Collecting and managing github metrics for opencv repositories

1. github_metrics.py collects data from Github for given repository
2. run_for_all_repos.sh runs github_metrics.py for opencv repositories
3. files_to_google_drive.py uploads csv files to Google Drive 
   (needs some work to get access to Google Drive)
4. Github_stats_view.ipynb shows in Jupyter Notebook DataFrames of metrics 
   for opencv repositories
5. files_drive_links.txt  - file with links to tables on Google Drive 
   uploaded by files_to_google_drive.py
   
   Futher improvements:
 - Github API does not provide access to traffic and views data for more then last 2 weeks
     but somehow it can be done
 - Forks metric was made but in case of some bug removed at the last moment
   Soon it can be added
