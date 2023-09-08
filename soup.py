from requests import get as requests_get
from bs4 import BeautifulSoup


def get_nbw_message():
    """
    获取公文通消息
    :return 消息列表[[来源部门，标题，链接]]
    """

    main_url = "https://nbw.sztu.edu.cn/"

    summuny_url = main_url + "list.jsp?urltype=tree.TreeTempUrl&wbtreeid=1029"

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                '(KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36'}

    response = requests_get(summuny_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    res_list = soup.find_all(name='li', class_ = 'clearfix')

    message_list = []
    for block in res_list:
        message = []

        source = block.find_all(name='a', attrs = {'style':'font-size: 14px;'})[0].string
        message.append(source)

        title = block.find_all(name='span')[2].string
        message.append(title)

        message_url = block.find_all(name='a', attrs = {'title':title})[0].get('href')
        message_url = main_url + message_url
        message.append(message_url)


        message_list.append(message)

    return message_list


if __name__ == "__main__":
    get_nbw_message()

