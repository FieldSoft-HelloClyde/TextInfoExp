# coding=utf-8
import json
import os
import traceback
import urllib2

import time
from bs4 import BeautifulSoup

base_url = "http://cpc.people.com.cn"
seed_url = "http://cpc.people.com.cn/GB/67481/412690/414114/index%s.html"


def set_proxy():
    """
    设置代理
    :return:
    """
    pass


def get_page_total_from_seed(seed_html_init):
    """
    获取页码，来自html中的注释
    :param seed_html_init:
    :return:
    """
    soup = BeautifulSoup(seed_html_init, "lxml")
    dom = soup.select_one(".p2j_con02 > .fl").contents[-2]
    return int(str(dom.string).split("=")[-1])


def get_seed_html():
    """
    获取种子页面
    将种子页面写入data/seed/htmls
    :return:
    """
    global seed_url
    # 获取第一页以便获取页数
    seed_html_1 = str(urllib2.urlopen(seed_url % 1).read()).decode("GB18030")
    # 写入第一页
    html_file = open("../data/seed/htmls/0.html", "w")
    html_file.write(seed_html_1.encode("utf-8"))
    html_file.close()
    # 获取页数
    page_total = get_page_total_from_seed(seed_html_1)
    for page in range(1, page_total):
        seed_html = str(urllib2.urlopen(seed_url % (page + 1)).read()).decode("GB18030")
        html_file = open("../data/seed/htmls/%s.html" % page, "w")
        html_file.write(seed_html.encode("utf-8"))
        html_file.close()


def get_links_from_html(seed_html_path):
    """
    从种子页面获取链接
    :param seed_html_path:种子页面地址
    :return:
    """
    global base_url
    seed_html = str(open(seed_html_path, "r").read()).decode("utf-8")
    soup = BeautifulSoup(seed_html, "lxml")
    dom_list = soup.select(".p2j_con02 > .fl > ul > li > a")
    urls = []
    for dom in dom_list:
        url = str(dom["href"])
        if not url.startswith("http"):
            url = base_url + url
        urls.append(url)
    return urls


def get_links_from_seed():
    """
    从种子页面抽取出文章link
    从data/seed/seed.html获取种子页面
    将文章url写入data/seed/links.txt中
    :return:
    """
    base_path = "../data/seed/htmls"
    file_list = os.listdir(base_path)
    url_links = []
    for file_name in file_list:
        links = get_links_from_html(base_path + "/" + file_name)
        url_links.extend(links)
    url_file = open("../data/seed/links.txt", "w")
    for link in url_links:
        url_file.write(link + "\n")
    url_file.close()


def get_html_from_links():
    """
    从data/seed/links.txt获取文章html内容
    存放入data/htmls中
    :return:
    """
    url_file = open("../data/seed/links.txt", "r")
    idx = 0
    for line in url_file.readlines():
        url = line.strip()
        if url == "":
            continue
        print "get html from url:%s" % url
        html = str(urllib2.urlopen(url).read()).decode("GB18030")
        html_file = open("../data/htmls/%s.html" % idx, "w")
        html_file.write(html.encode("utf-8"))
        html_file.close()
        print "ok"
        idx += 1
    url_file.close()


def get_doc_from_html():
    """
    从doc/htmls中获取html，然后解析出想要的doc内容
    doc内容为json格式，存放于data/documents中
    :return:
    """
    base_path = "../data/htmls"
    output_path = "../data/documents"
    file_list = os.listdir(base_path)
    for file_name in file_list:
        try:
            file_path = base_path + "/" + file_name
            html_file = open(file_path, "r")
            html = str(html_file.read()).decode("utf-8")
            html_file.close()
            # 解析html
            print "start parse %s" % file_name
            soup = BeautifulSoup(html, "lxml")
            # 获取标题
            title_doms = soup.select(".text_c > h3, .text_c > h1 , .text_c > h2")
            title = ""
            for title_dom in title_doms:
                if title_dom.string:
                    title += title_dom.string
            print title
            # 获取时间和来源
            source_dom = soup.select_one(".text_c > .sou")
            time_str = source_dom.contents[0].string[0:16]
            publish_time = int(time.mktime(time.strptime(time_str, '%Y年%m月%d日%H:%M'.decode("utf-8"))))
            print publish_time
            try:
                source = source_dom.contents[1].string
            except Exception:
                source = None
            print source
            # 获取文章内容
            content_strs = soup.select_one(".show_text").stripped_strings
            content = ""
            for content_str in content_strs:
                content += content_str
            print content
            output_file = open(output_path + "/" + file_name.split(".")[0] + ".json", "w")
            output_file.write(json.dumps({
                "title": title,
                "publishTime": publish_time,
                "source": source,
                "content": content
            }).encode("utf-8"))
            output_file.close()
            print file_name + " parser ok"
        except Exception:
            traceback.print_exc()
            print file_name + " parser err"


def main():
    """
    程序主要入口
    :return:
    """
    set_proxy()
    get_seed_html()
    get_links_from_seed()
    get_html_from_links()
    get_doc_from_html()


if __name__ == '__main__':
    main()
