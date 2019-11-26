#抓入https://pcredivewiki.tw/ 的檔案
from bs4 import BeautifulSoup
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import discord, asyncio, re, time, requests, json, io, colorama


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'}

def home_event():
    try:
        event_link = "https://pcredivewiki.tw/static/data/event.json"
        event_json = requests.get(event_link)
    except:
        print("error from request: {}".format(event_json))

    raw_json = json.loads(event_json.text)
    sorted_json = json.dumps(raw_json, indent=4, sort_keys=True, ensure_ascii=False)

    eventdatafile = open("datafile/event.json", "w",encoding='utf-8')
    eventdatafile.write(json.dumps(json.loads(sorted_json), indent=4, sort_keys=True, ensure_ascii=False))
    eventdatafile.close()
    
def character():
    chrome_options = Options()
    chrome_options.add_argument("")#--headless
    browser = webdriver.Chrome(chrome_options=chrome_options)
    browser.get("https://pcredivewiki.tw/Character")
    html = browser.page_source
    htmlbs4 = BeautifulSoup(html, "lxml")

    #find name
    character_name = []
    for name in htmlbs4.find_all('small'):
        character_name.append(name.get_text())
    
    #find link
    character_link = []
    for link in htmlbs4.find_all('a'):
        if "/Character/Detial/" in link.get('href'):
            character_link.append(link.get('href'))
    
    #find picture path
    character_imgpath = []
    for path in htmlbs4.find_all('img', src=True, class_=True):
        if "/static/images/unit/" in path.get('src'):
            character_imgpath.append(path.get('src'))

    if len(character_imgpath) == len(character_link) == len(character_name):
        print("compare done!")
    else:
        print("error! character info not complete!")
    
    data = {}
    index = 0
    for name in character_name:
        data[name] = ["{}".format(character_imgpath[index]),"{}".format(character_link[index])]
        index+=1

    character_nav = open("datafile/character_nav.json", "w", encoding='utf8')
    character_nav.write(json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False))
    character_nav.close()

def character_info(character_link):
    """
    The output shoud be:
    {
        "document":{
            "name": none,
            "birthday": none,
            "age": none,
            "height": none,
            "weight": none,
            "bloodtype": none,
            "raise": none,
            "hobby": none,
            "CV": none,
            "intro": none
        },
        "skill": {
            "name": [
                "ぷうきちサンタ・ストーム",
                "ぷうきちエール",
                "ぷうきちラッシュ",
                "ホーリーナイトスラッガー",
                "ホーリーナイトスラッガー+"
            ],
            "startup": [
                "/static/images/skill/icon_skill_ap01.png",
                "/static/images/skill/icon_skill_ap02.png"
            ],
            "loop": [
                "/static/images/skill/icon_skill_attack.png",
                "/static/images/skill/icon_skill_ap01.png",
                "/static/images/skill/icon_skill_ap02.png"
            ],
            "info": [
                "敵単体に【80.0 + 80.0*技能等級 + 7.4 *atk】の物理ダメージ",
                "自分の物理攻撃力を【22.0 + 22.0*技能等級 】アップ\n\n持續時間: 10.0 秒",
                "敵単体に【12.0 + 12.0*技能等級 + 1.0 *atk】の物理ダメージ",
                "自分の物理攻撃力を【15.0 + 15.0*技能等級 】アップ",
                "自分の物理攻撃力を【240.0 + 15.0*技能等級 】アップ"
            ]
        },
        "specialitem": {
            "name": null
            "intro": null
            "status": null
        }
    }
    """
    #for loop
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    browser = webdriver.Chrome(chrome_options=chrome_options)
    browser.get(character_link)
    html = browser.page_source
    htmlbs4 = BeautifulSoup(html, "lxml")
    #個人資料
    character_doc = [text.get_text() for text in htmlbs4.find_all('td')]
    character_key = ["name", "birthday", "age", "hight", "weight", "bloodtype", "raise", "hobby", "CV"]
    character_dict = dict(zip(character_key, character_doc))
    #special item:
    item_ = [item for item in htmlbs4.find_all('div', class_="prod-info-box unique mb-3")]
    if item_:
        specialitem_name = {"name":[name.find('h2').get_text() for name in item_][0]}
        specialitem_intro = {"intro":[intro.find('p').get_text() for intro in item_][0]}
        specialiteminfo = []
        for item in item_:
            for info in item.find_all('span', class_=True):
                specialiteminfo.append(info.get_text().strip())
        specialitem_status = {"status":specialiteminfo}

        skinfo = htmlbs4.find_all('div', class_="skill-box my-3")
        skillinfo = []
        skill_name = {"name":[info.find('h3').get_text() for info in skinfo]}
        for info in skinfo:
            info.find('h3').decompose()
            info.find('div', class_=re.compile(r"skill-type\smb-1\s\w+")).decompose()
            skillinfo.append(info.get_text().replace("\t", ""))
        skill_info = {"info":skillinfo}
    
    else:
        skinfo = htmlbs4.find_all('div', class_="skill-box my-3")
        skill_info = {"info":[info.find('div', class_="mb-3").get_text().strip().replace("\t", "").replace("\r", "") for info in skinfo]}
        skill_name = {"name":[info.find('h3').get_text() for info in skinfo]}
        specialitem_name = {"name":None}
        specialitem_intro = {"intro":None}
        specialitem_status = {"status":None}

    #intro:
    character_dict['intro'] = [htmlbs4.find('span', class_="my-3 d-block").get_text().replace("簡介", "").strip()][0]
    #document:
    document = {"document":character_dict}

    startup_skill = {"startup":[path.get('src') for path in htmlbs4.find('div', class_="d-flex flex-wrap").find_all('img')]}
    
    loop_ = [path for path in htmlbs4.find_all('div', class_="d-flex flex-wrap")][1]
    loop_skill = {"loop":[path.get('src') for path in loop_.find_all('img')]}
    #skill
    #skill = {"skill":{skill_name, startup_skill, loop_skill, skill_info}}
    skill_name.update(startup_skill)
    skill_name.update(loop_skill)
    skill_name.update(skill_info)
    skill = {"skill": skill_name} 
    #specialitem
    specialitem_name.update(specialitem_intro)
    specialitem_name.update(specialitem_status)
    specialitem = {"specialitem": specialitem_name}
    #combine document skill specialitem
    #output = {f'{character_doc[0]}':dict(zip(document, skill, specialitem))}
    document.update(skill)
    document.update(specialitem)
    output = {f'{character_doc[0]}': document}
    
    #convert dict into json
    #print(json.dumps(output, indent=4, sort_keys=True, ensure_ascii=False))
    return output

def writedatafile():
    """read character name, link"""

    #name, character and picture link
    with open("datafile/character_nav.json", "r", encoding='utf-8') as f:
        character_load = json.load(f)
    link = "https://pcredivewiki.tw/Character/Detial/"
    home = "https://pcredivewiki.tw"
    character_list = list(character_load.keys())
    character_detaillink = [f'{link}{name}' for name in character_list]

    index = 0
    for name in character_list:
        character_dict = character_info(character_detaillink[index])
        #character_datafile io
        with open("datafile/character_datafile.json", "r", encoding='utf-8') as f:
            character_prev = json.load(f)
        character_link = {"link": f'{home}{character_load[name][1]}'}
        character_icon = {"icon": f'{home}{character_load[name][0]}'}
        character_dict[name].update(character_icon)
        character_dict[name].update(character_link)
        print(json.dumps(character_dict, indent=4, sort_keys=True, ensure_ascii=False))

        with open("datafile/character_datafile.json", "w+", encoding='utf-8') as f:
            character_prev.update(character_dict)
            json.dump(character_prev, f, indent=4, sort_keys=True, ensure_ascii=False)
        print(colorama.Fore.RED + f'INFO: 已經完成{name}的腳色檔案\n')
        index +=1

writedatafile()
