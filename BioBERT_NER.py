import requests

def query_raw(text, url="https://bern.korea.ac.kr/plain"):
return requests.post(url, data={'sample_text': text}).json()

if __name__ == '__main__':
print(query_raw("YOUR TEXT HERE"))
