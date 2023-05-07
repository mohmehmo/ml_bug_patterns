import pandas as pd
from git.repo.base import Repo
from pydriller import Repository
import ntpath
from io import BytesIO
import pycurl
import requests
import json


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


def check_repo_availability(repo_full_name):
    url = f"https://api.github.com/repos/{repo_full_name}"
    body = github_api_v3_call(url)

    if body.get("message")== 'Not Found' or body.get("message") == 'Moved Permanently' or body.get("message") == "The history or contributor list is too large to list contributors for this repository via the API.":
        return False

    return True


def check_commit_text(text):
    keywords = ["refactor"]

    lower_text = text.lower()
    for keyword in keywords:
        if lower_text.find(keyword) != -1:
            return True

    return False


def get_refactoring_commits(repo_full_name):

    col_names = ["repo_full_name", "commit_url", "commit_html_url"]
    commits = pd.DataFrame(columns=col_names)

    if not check_repo_availability(repo_full_name):
        return commits

    page_number = 1
    while True:
        url = f"https://api.github.com/repos/{repo_full_name}/commits?per_page=100&page={page_number}"
        body = github_api_v3_call(url)
        page_number += 1
        if body == []:
            break
        print(f"{page_number}-th is processing...", end="\r")

        for commit in body:
            # counter += 1
            commit_message = commit["commit"]["message"]
            if check_commit_text(commit_message):
                commits.loc[-1] = [repo_full_name, commit["url"], commit["html_url"]]

    print("", end="\r")
    return commits


def main():
    # all_repos = pd.read_csv("data/ml_based_repos.csv", low_memory=False)

    keras_repos = pd.read_csv("data/keras/keras_repo_100.csv", low_memory=False)
    pytorch_repos = pd.read_csv("data/pyTorch/pytorch_repo_100.csv", low_memory=False)
    tensorflow_repos = pd.read_csv("data/tensorflow/tensorflow_repo_100.csv", low_memory=False)

    all_repos = pd.concat([keras_repos, pytorch_repos]).drop_duplicates().reset_index(drop=True)
    all_repos = pd.concat([all_repos, tensorflow_repos]).drop_duplicates().reset_index(drop=True)

    col_names = ["repo_full_name", "commit_url", "commit_html_url"]
    refactoring_commits = pd.DataFrame(columns=col_names)

    counter = 1

    for index, row in all_repos.iterrows():
        repo_full_name = row["full_name"]
        print(f"{counter}-th repository ({repo_full_name}) is started to review....")
        counter += 1
        repo_refactoring_commits = get_refactoring_commits(repo_full_name)
        if repo_refactoring_commits.empty:
            continue
        else:
            refactoring_commits = pd.concat([refactoring_commits, repo_refactoring_commits]).drop_duplicates().reset_index(drop=True)

    refactoring_commits.to_csv("data/all_repos_refactoring_commits.csv", index=False)

if __name__ == '__main__':
    main()
