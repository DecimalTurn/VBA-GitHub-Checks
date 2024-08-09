import requests

def search_github_repos(query, sort='updated', order='desc', per_page=10):
    url = f"https://api.github.com/search/repositories"
    headers = {'Accept': 'application/vnd.github.v3+json'}
    params = {
        'q': query,
        'sort': sort,
        'order': order,
        'per_page': per_page
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data from GitHub API. Status code: {response.status_code}")
        return None

def main():
    query = 'VBA'
    repos = search_github_repos(query)
    
    if repos:
        print(f"Found {repos['total_count']} repositories:")
        for repo in repos['items']:
            print(f"Name: {repo['name']}")
            print(f"Description: {repo['description']}")
            print(f"Language: {repo['language']}")
            print(f"URL: {repo['html_url']}")
            print(f"Updated at: {repo['updated_at']}")
            print('-' * 40)
    else:
        print("No repositories found.")

if __name__ == "__main__":
    main()