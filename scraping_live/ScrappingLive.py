import bs4
import requests
import traceback

response = requests.get('https://www.ncbi.nlm.nih.gov/books/NBK547852/')
response = response.text
data = bs4.BeautifulSoup(response, "lxml")
a_nodes = data.select(".simple-list.toc .half_rhythm .toc-item")

for a_node in a_nodes:
    link = 'https://www.ncbi.nlm.nih.gov' + a_node['href']
    print(f'fetching link: {link}, ', end='')

    link_response = requests.head(link)
    if link_response.status_code == 303:
        link = link_response.headers['Location']

    link_response = requests.get(link).text

    with open('files/' + a_node.text + '.html', mode='w', encoding='utf-8') as f:
        f.write(link_response)

    try:
        r = requests.get(link)
        print(f'url: {r.url}')
    except ConnectionError as e:
        traceback.print_exc()
        break
