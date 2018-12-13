import hashlib


def get_md5(url):
    if isinstance(url,str):#python3已经没有unicode，需要转为utf-8
        url=url.encode("utf-8")
    m=hashlib.md5()
    m.update(url)
    return m.hexdigest()

if __name__ == '__main__':
    print(get_md5("http://jobbole.com"))