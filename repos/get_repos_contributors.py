import pandas as pd
from git.repo.base import Repo
from pydriller import Repository
import ntpath
from io import BytesIO
import pycurl
import requests
import json
import csv




# access_token = [
#                 "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", # Mehdi
#                 "a6abc85a10eb7681b2b4fa58324680fcb8e19eae", # Kopol
#                 "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", # Dima
#                 "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", # Ahura
#                 "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",
#                 "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",
#                 "4911fb3cb9c359b10a19d427c7d0726dc9d641fc",
#                 "149c667147dfb79d75c448355b7f031f856df65e"
#                 ]

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


def get_num_of_collaborators(repo_full_name):

    num_of_collaborators = 0

    global access_token_counter
    page_number = 1
    while True:
        url = f"https://api.github.com/repos/{repo_full_name}/contributors?per_page=100&page={page_number}"
        body = github_api_v3_call(url)
        if body == []:
            break
        num_of_collaborators += len(body)
        page_number += 1
    return num_of_collaborators

def main():
    repos = pd.read_csv("data/keras/repos_keras_code_filtered(fork_star_activity_commit).csv", low_memory=False)
    collaborators = []
    counter = 0
    for index, row in repos.iterrows():
        counter += 1
        print(f"{counter}-th repository {row['full_name']} is started processing....")
        # checking the availability of the GitHub repository and ignore it if it is not available by API at present
        if not check_repo_availability(row["full_name"]):
            collaborators.append(0)
            continue
        collaborators.append(get_num_of_collaborators(row["full_name"]))

    repos["collaborators"] = collaborators
    repos.to_csv('data/keras/repos_keras_code_filtered(fork_star_activity_commit)_contributors.csv', index=False)



if __name__ == '__main__':
    main()
    print("everything is done....")