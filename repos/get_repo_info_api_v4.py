import pandas as pd
from git.repo.base import Repo
from pydriller import Repository
import ntpath
from io import BytesIO
import pycurl
import requests
import json
import csv

access_token = [
                "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", #roozbeh
                "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",
                "149c667147dfb79d75c448355b7f031f856df65e"
                ]

access_token_counter = 0

def github_api_v3_call(url):

    global access_token_counter
    output = BytesIO()
    request = pycurl.Curl()
    request.setopt(pycurl.HTTPHEADER, [f'Authorization: token {access_token[access_token_counter % 3]}'])
    request.setopt(request.URL, url)
    request.setopt(request.WRITEDATA, output)
    request.perform()
    access_token_counter += 1

    get_body = output.getvalue().decode()
    body = json.loads(get_body)

    return body

def check_repo_contributors(repo_full_name):
    url = f"https://api.github.com/repos/{repo_full_name}/collaborators"
    body = github_api_v3_call(url)



def check_repo_availability(repo_full_name):
    url = f"https://api.github.com/repos/{repo_full_name}"
    body = github_api_v3_call(url)

    if body.get("message")== 'Not Found' or body.get("message") == 'Moved Permanently':
        return False

    return True

def run_query(query,token): # A simple function to use requests.post to make the API call. Note the json= section.
    headers = {'Authorization': 'token %s' % token}
    request = requests.post('https://api.github.com/graphql', json={'query': query} , headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))



def main():
    global access_token_counter

    data_file_name = "data/pyTorch/repos_pytorch_code_filtered(fork_star_activity).csv"
    repos = pd.read_csv(data_file_name, low_memory=False)


    # Backup output
    csvfile = open('data/temp/repos_pytorch_code_filtered(fork_star_activity)_commit_backup.csv', mode='w')
    writer = csv.writer(csvfile)
    writer.writerow(["id", "full_name", "url", "stars", "forks", "commit", "openIssue", "closedIssue"])

    repos_commits = []
    repos_openIssues = []
    repos_closedIssues = []

    counter = 1
    unavailable_repos = 0
    for index, row in repos.iterrows():
        if not check_repo_availability(row["full_name"]):
            repos_commits.append(0)
            repos_openIssues.append(0)
            repos_closedIssues.append(0)
            unavailable_repos += 1
            continue
        repo_owner, repo_name = ntpath.split(row["full_name"])

        query = """
            query {
                repository(owner:"%s", name:"%s") {
                openIssue:issues(states: OPEN) {
                totalCount
            }
            closedIssues:issues(states:CLOSED){
                totalCount
            }
            defaultBranchRef {
                target {
                    ... on Commit {
                        history(first: 0) {
                          totalCount
                        }
                    }
                }
            }
        }
    }
    """%(repo_owner, repo_name)

        token = access_token[access_token_counter%3]
        access_token_counter += 1
        result = run_query(query, token)
        openIssues = result['data']['repository']['openIssue']['totalCount']
        closedIssues = result['data']['repository']['closedIssues']['totalCount']
        totalCommits = result['data']['repository']['defaultBranchRef']['target']['history']['totalCount']

        repos_commits.append(totalCommits)
        repos_openIssues.append(openIssues)
        repos_closedIssues.append(closedIssues)

        print(f"{counter} repository  {row['full_name']} is processed....")
        counter += 1

        writer.writerow([row['id'],row["full_name"],row['url'], row['stars'], row['forks'],
                         totalCommits, openIssues, closedIssues])

    repos["commits"] = repos_commits
    repos["open_issue"] = repos_openIssues
    repos["closed_issue"] = repos_closedIssues

    repos.to_csv('data/pyTorch/repos_pytorch_code_filtered(fork_star_activity)_commit.csv', index=False)
    csvfile.close()
    print(f"Number of unavailable repos is  {unavailable_repos}")


if __name__ == '__main__':
    main()