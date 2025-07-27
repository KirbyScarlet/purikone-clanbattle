#合刀计算

from nonebot.internal.adapter import Bot, Event, Message

HEDAO_HELP = """\
使用说明：
=========================
合刀 血量1 血量2 血量3
自动识别首领剩余血量
计算补偿秒数，并计算满补需垫刀伤
=========================
合刀 血量1 血量2
自动识别首领剩余血量
尽可能计算满补所需垫刀
=========================
合刀 血量
计算合刀满补线"""

async def hedao_parser(msg: Message) -> list["int", "int", "int"]:
    msg = msg.extract_plain_text().split()
    try:
        num = list(map(int, msg))
    except ValueError:
        return None, None, None
    num.sort()
    if 1 == len(msg):
        return num[0], None, None
    if 2 == len(msg):
        return num[0], num[1], None
    elif 3 == len(msg):
        return num
    return None, None, None
        
def comp(h1, maxhp) -> float:
    # 尾刀剩余秒数
    h1persecond = h1/90
    h1realsecond = maxhp/h1persecond
    return 110-h1realsecond

def rebate(h1, h2, maxhp) -> float:
    # 合刀剩余秒数
    return comp(h1, maxhp-h2)

def decomp(h1, maxhp):
    # 计算垫刀
    return maxhp-7*h1/30

async def hedao(a: int, b: int, c: int) -> list[dict]:
    res = [{"text":"\n"}]
    if c:
        if a+b<c:
            res.append({"text":f"不够，还差{c-a-b+1}，进一刀{int((c-a-b)*30/7)+1}吃满补"})
        elif a+b==c:
            res.append({"text":f"正好收了"})
        else:
            res.append({"text":f"{a}先出，"})
            if (r:=rebate(b,a,c))>89:
                res.append({"text":f"{b}返{r:.2f}秒\n"})
            else:
                res.append({"text":f"{b}返{r:.2f}秒，再垫{int(decomp(b,c-a))+1}满补\n"})
            res.append({"text":f"{b}先出，"})
            if (r:=rebate(a,b,c))>89:
                res.append({"text":f"{a}返{r:.2f}秒"})
            else:
                res.append({"text":f"{a}返{r:.2f}秒，再垫{int(decomp(a,c-b))+1}满补"})
    elif b:
        if comp(b,a)>89:
            res.append({"text":f"剩余血量{a}，刀伤{b}，补偿{comp(b,a):.2f}秒。"})
        else:
            res.append({"text":f"剩余血量{a}，刀伤{b}，补偿{comp(b,a):.2f}秒，再垫{int(decomp(b,a))+1}满补\n"})
        res.append({"text":"==========\n"})
        res.append({"text":f"剩余血量{b}，刀伤{a}，还差{b-a}\n"})
        # if decomp(a,b-a)+a>b:
        #     pass
        # else:
        #     res.append({"text":f"刀伤{a}先出，第二刀满补需要打{decomp(a,b-a)+a}\n"})
        res.append({"text":f"第二刀砍{int(decomp(a,b)+1)}，刀伤{a}吃满补"})
        if (b-a)*30/7+1<b:
            res.append({"text":f"\n刀伤{a}先出，第二刀超过{int((b-a)*30/7)+1}可满补"})
    elif a:
        res.append({"text":f"剩余血量{a}，两刀{int(a*30/37)+1}满补\n"})
        res.append({"text":f"刀伤{a}，剩余血量小于{int(a*7/30)}可满补"})
    return res

