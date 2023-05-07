import pandas as pd
import pycurl
from io import BytesIO
import json
import time


access_token = [
                # "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", # Ahura
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

def get_repo_info(repo_full_name):
    url = f"https://api.github.com/repos/{repo_full_name}"
    print(url)
    body = github_api_v3_call(url)

    repo_forked_stats = True
    repo_last_activity = '2010-02-27T18:00:57Z'

    # check availability of the repository
    if body.get("message")== 'Not Found':
        return repo_forked_stats, time.strptime(repo_last_activity, '%Y-%m-%dT%H:%M:%SZ')
    if body.get("message") == 'Moved Permanently':
        url = body.get('url')
        body = github_api_v3_call(url)
    if body['disabled'] == True or body['private'] == True:
        return repo_forked_stats, time.strptime(repo_last_activity, '%Y-%m-%dT%H:%M:%SZ')


    # extract repository information
    repo_forked_stats = body['fork']
    repo_last_activity = body['pushed_at']
    repo_last_activity_time = time.strptime(repo_last_activity, '%Y-%m-%dT%H:%M:%SZ')

    return repo_forked_stats, repo_last_activity_time


def main():
    repos_forked_stats = []
    repos_last_activity = []
    repos = pd.read_csv("data/keras/repos_keras_code_filtered(fork_star).csv")
    repos = pd.read_csv("data/pyTorch/py")
    for index, row in repos.iterrows():
        repo_full_name = row["full_name"]
        repo_forked_stats, repo_last_activity = get_repo_info(repo_full_name)
        repos_forked_stats.append(repo_forked_stats)
        repos_last_activity.append(repo_last_activity)

    repos["forked"] = repos_forked_stats
    repos["activity"] = repos_last_activity

    repos.to_csv("data/keras/repos_keras_code_filtered(fork_star)_activity.csv")

if __name__ == '__main__':
    main()