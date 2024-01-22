import re, json, os
from splunk_forwarder import sendEvent


def search_keyword(dataleak_line):
    """
    This function will return two value:
        - The Bolean which show the the data leak is found or not
        - Company name that has leak data
    """
    if os.path.exists("monitored_wordlist.txt"):
        with open("monitored_wordlist.txt", "r") as keyword_list:
            MONITORED_KEYWORD_LIST = keyword_list.read().splitlines()
            print(MONITORED_KEYWORD_LIST)
    else:
        print(f"Please create monitored_wordlist.txt first before running this script")
        exit()
    
    for monitored_key in MONITORED_KEYWORD_LIST: 
        if monitored_key in dataleak_line:
            if monitored_key in ["momo.vn","mservice.com.vn","cvs.vn","mservice.io","momocdn.net","momoapp.vn"]:
                company_name = "Momo"
                print(f"[*] Keyword detected {monitored_key}")
        return True, company_name
    return False, None


class Parsing(object):
    def __init__(self, text) -> None:
        self.url = self.get_url(text)[0] if self.get_url(text) else "NotFound"
        temp = self.get_userpass(text)
        self.username = temp[0]
        self.password = temp[1]
        self.raw = text

    def __getattr__(self, attr):
        return self[attr]
    
    def __iter__(self):
        return iter(self)

    def get_url(self, text):
        def boolCheck(p, t):
            if a:= re.search(p, t):
                return True
            return False
        def isPort(text):
            pattern = r'\:\d{2,5}(?:/|\s|\t|$|\|)'
            return boolCheck(pattern, text)
        def isHttp(text):
            pattern = r'https?://'
            return boolCheck(pattern, text)
        if isPort(text):
            if isHttp(text):
                pattern = r"(?P<url>https?://[^\:]+:\d{2,5}[^\:\s\|]+)"
                return re.search(pattern, text)
            else:
                pattern = r'(?P<url>(?:[a-zA-Z]+\.)+(?:com|net|org|edu|gov|int|mil|biz|info|name|pro|aero|coop|museum|[a-z]{2})\:\d{2,5}[^\|\s\r\n\:]+)'
                return re.search(pattern, text)
        else:
            if isHttp(text):
                pattern = r'(?P<url>https?://[^\:\s\|]+)'
                return re.search(pattern, text)
            else:
                pattern = r'(?P<url>(?:[a-zA-Z]+\.)+(?:com|net|org|edu|gov|int|mil|biz|info|name|pro|aero|coop|museum|[a-z]{2})[^\|\s\r\n\:]+)'
                return re.search(pattern, text)
        return False
    
    def get_userpass(self, text):
        def isMailAddress(s):
            pattern = r'\S+@\S+'
            if re.match(pattern, s):
                return True
            return False
        try:
            url = False if isMailAddress(self.url) else self.url
            pattern = r'(?P<user>[^\s\|\:]+)(?:\s|\||:){1}(?P<pass>\S+)'
            if url:
                if text.find(url) == 0:
                    userpass =  text[len(url)+1:]
                    user, passwd = re.search(pattern, userpass).groups()
                    return user, passwd
                else:
                    userpass = text[0:len(text)-len(url)-2]
                    user, passwd = re.search(pattern, userpass).groups()
                    return user, passwd
            else:
                self.url = None
                user, passwd = re.search(r'(?P<user>\S+)(?:\s|\||:){1}(?P<pass>\S+)', text).groups()
                return user, passwd
        except:
            return None, None
        
def verifySend(filepath):
    try:
        with open(filepath,'r', encoding='utf-8') as f:
            for line in f:
                found_dataleak, company_name = search_keyword(line)
                if found_dataleak and company_name is not None:
                    a = Parsing(line.strip())
                    sendEvent(a.__dict__, filepath)
                else:
                    continue
        os.remove(filepath)
    except UnicodeDecodeError:
        with open(filepath,'r', encoding='latin-1') as f:
            for line in f:
                found_dataleak, company_name = search_keyword(line)
                if found_dataleak and company_name is not None:
                    a = Parsing(line.strip())
                    sendEvent(a.__dict__, filepath)
                else:
                    continue
        os.remove(filepath)
    except Exception as e:
        print(f'[!]Error in VerifySend: {e}')

def readFolder(mainfolder):
    for subdir, dirs, files in os.walk(mainfolder):
        for file in files:
            # Define the path to the current file
            file_path = os.path.join(subdir, file)
            # Open the current file for reading
            verifySend(file_path)

# readFolder('/home/namle/telegram-infostealer-monitoring/downloadedData')