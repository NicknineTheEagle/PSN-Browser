import requests
import argparse
import json

interactive=False

# Sony server does not like the default user agent for some reason.
httpHeaders = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0"
}

def parseContent(contentId,language,region,age):
    url="https://store.playstation.com/store/api/chihiro/00_09_000/container/%s/%s/%d/%s" % (region,language,age,contentId)
    req=requests.get(url,headers=httpHeaders)
    if req.status_code!=200:
        print("%s failed - %d!" % (url,req.status_code))
        return None

    data=json.loads(req.content)

    print(data.get("id"))
    print(data.get("name"))
    print(data.get("game_contentType","-"))
    print(data.get("provider_name","-"))
    print(data.get("release_date","-"))
    if "default_sku" in data:
        print(data["default_sku"]["display_price"])
        print(" "+data["default_sku"]["name"])
        for elem in data["default_sku"]["entitlements"]:
            print(" "+elem["id"])
    print("")
    print(data.get("long_desc").replace("<br>","\n"))
    print("")

    contentIds=list()
    print("Additional content:")
    if "relationships" in data:
        for rel in data["relationships"]:
            print(" "*2+rel["name"]+":")
            url=rel["url"]
            req=requests.get(url,headers=httpHeaders)
            if req.status_code!=200:
                print("%s failed - %d!" % (url,req.status_code))
                continue

            data2=json.loads(req.content)
            for elem in data2["links"]:
                if interactive: print(" "*4+"%d)" % (len(contentIds)+1))
                print(" "*4+elem.get("id"))
                print(" "*4+elem.get("name"))
                print(" "*4+elem.get("game_contentType","-"))
                if "default_sku" in elem:
                    print(" "*4+elem["default_sku"]["display_price"])
                print("")
                contentIds.append(elem.get("id"))

##    for elem in data["links"]:
##        print("\t"+elem.get("game_contentType","-"))
##        print("\t"+elem.get("id"))
##        print("\t"+elem.get("name"))
##        if "default_sku" in elem:
##            print("\t"+elem["default_sku"]["display_price"])
##        print("")

    parentIds=list()
    print("Parents:")
    if "parent_links" in data:
        for elem in data["parent_links"]:
            if interactive: print(" "*2+"%s)" % (chr(len(parentIds)+ord("A"))))
            print(" "*2+elem.get("id"))
            print(" "*2+elem.get("name"))
            print("")
            parentIds.append(elem["id"])

    return parentIds, contentIds

def searchStore(searchStr,language,region,age,platform):
    url="https://store.playstation.com/store/api/chihiro/00_09_000/tumbler/%s/%s/%d/%s?platform=%s&size=100" % (region,language,age,searchStr,platform)
    req=requests.get(url,headers=httpHeaders)
    if req.status_code!=200:
        print("%s failed - %d!" % (url,req.status_code))
        return None

    data=json.loads(req.content)
    contentIds=list()

    for elem in data["links"]:
        if interactive: print("%d)" % (len(contentIds)+1))
        print(elem.get("id"))
        print(elem.get("name"))
        print(elem.get("game_contentType","-"))
        print(elem.get("provider_name","-"))
        if "default_sku" in elem:
            print(elem["default_sku"]["display_price"])
        print("")
        contentIds.append(elem.get("id"))

    return contentIds

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--content",type=str,default=None)
    parser.add_argument("--search",type=str,default=None)
    parser.add_argument("--platform",type=str,default="ps3")
    parser.add_argument("--language",type=str,default="en")
    parser.add_argument("--region",type=str,default="GB")
    parser.add_argument("--age",type=int,default=999)
    args=parser.parse_args()


    if args.content:
        parseContent(args.content,args.language,args.region,args.age)
    elif args.search:
        searchStore(args.search,args.language,args.region,args.age,args.platform)
    else:
        # Interactive mode.
        interactive=True
        state=0
        while True:
            if state==0:
                searchStr=input("Search: ")
                contentIds=searchStore(searchStr,args.language,args.region,args.age,args.platform)
                if not contentIds:
                    print("No results")
                else:
                    parentIds=None
                    state=1
            elif state==1:
                choice=input("Select content or Q to go back: ")
                if choice.upper()=="Q":
                    state=0
                elif choice.isdecimal() and (int(choice)-1)<len(contentIds):
                    idx=int(choice)-1
                    parentIds,contentIds=parseContent(contentIds[idx],args.language,args.region,args.age)
                    state=1
                elif choice.isalpha() and parentIds and len(choice)==1 and (ord(choice.upper())-ord("A"))<len(parentIds):
                    idx=(ord(choice.upper())-ord("A"))
                    parentIds,contentIds=parseContent(parentIds[idx],args.language,args.region,args.age)
                    state=1
