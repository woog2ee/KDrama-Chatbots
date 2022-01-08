import re
import pandas as pd
import sys
from tqdm.notebook import tqdm
from pykospacing import spacing



# 데이터프레임에서 대사 추출
def extract_dialog(dataframe, continuous=False):
    '''
        dataframe: 드라마 대본 데이터프레임, Subtitle 컬럼에 다음과 같은 대사가 포함됨
                   ex) (서진) 그렇게 행복했던 사람이?
        continuous: Subtitle 컬럼에서 등장인물 정보가 없는 대사를 합치는지 여부
    '''
    global charname        # 등장인물 이름
    name = None            # 등장인물 탐색 전 상태
    
    for i in range(len(dataframe)):
        sent = dataframe['Subtitle'][i]
        
        # 등장인물 괄호 찾아냄
        start_idx = 0
        matchs = re.finditer(r'\)', sent)
        for match in matchs:
            start_idx = match.span()[1]
            break
        
        # 대사에 등장인물이 없고, 대본을 연속해서 모을 경우
        if start_idx == 0 and continuous:
            if name == None: continue
            sent = sent[start_idx:]
            sent = modify_sent(sent)
            globals()[f'dialog_{name}'].append(sent)
        
        # 대사에 등장인물이 없는 경우
        elif start_idx == 0 and not continuous:
            continue
            
        # 대사에 등장인물이 있는 경우
        else:
            name = sent[:start_idx]
            name = modify_name(name)
            if name not in charname:
                charname.append(name)
                globals()[f'dialog_{name}'] = []  
            
            sent = sent[start_idx:]
            sent = modify_sent(sent)
            globals()[f'dialog_{name}'].append(sent)
            
            
# 등장인물 텍스트 전처리
def modify_name(text):
    matchs = re.finditer(r'\(', text)
    for match in matchs:
        start_idx = match.span()[1]
        text = text[start_idx:]
        break
    text = re.sub(r'\)', '', text)
    text = re.sub(r' ', '', text)
    text = re.sub(r'-', '', text)
    text = re.sub(r'\n', '', text)
    text = re.sub(r'\[[^]]*\]', '', text)
    return text


# 대사 텍스트 전처리
def modify_sent(text):
    matchs = re.finditer(r'\(', text)
    for match in matchs:
        start_idx = match.span()[1]
        text = text[:start_idx-1]
        break
    text = re.sub(r'-', '', text)
    text = re.sub(r'- ', '', text)
    text = re.sub(r'\n', '', text)
    text = re.sub(r'\[[^]]*\]', '', text)
    text = re.sub(r'\'', '', text)
    return spacing(text)



if __name__ == '__main__':
    # 드라마 제목, 회차
    dramaname = sys.argv[1]
    dramanum  = int(sys.argv[2])
    
    
    charname  = []     # 등장인물 목록
    for i in range(1, dramanum+1, 1):
        data = pd.read_excel(f'./dataset/{dramaname}/{dramaname}_{i}화.xlsx')
        print(f' {dramaname} {i}화 추출 및 전처리 진행...')
        extract_dialog(data, True)
    
    
    charlen   = []     # 등장인물당 대사 개수 
    for name in charname:
        charlen.append(len(globals()[f'dialog_{name}']))
    charlen.sort(reverse=True)
    charlen = charlen[:10]
    
    
    topname   = []     # 대사 개수 많은 등장인물 10명
    for name in charname:
        if len(globals()[f'dialog_{name}']) in charlen:
            topname.append(name)
    
    
    # 대본 데이터프레임 저장
    drama_dialog = pd.DataFrame.from_dict({ f'{topname[0]}': globals()[f'dialog_{topname[0]}'],
                                            f'{topname[1]}': globals()[f'dialog_{topname[1]}'],
                                            f'{topname[2]}': globals()[f'dialog_{topname[2]}'],
                                            f'{topname[3]}': globals()[f'dialog_{topname[3]}'],
                                            f'{topname[4]}': globals()[f'dialog_{topname[4]}'],
                                            f'{topname[5]}': globals()[f'dialog_{topname[5]}'],
                                            f'{topname[6]}': globals()[f'dialog_{topname[6]}'],
                                            f'{topname[7]}': globals()[f'dialog_{topname[7]}'],
                                            f'{topname[8]}': globals()[f'dialog_{topname[8]}'],
                                            f'{topname[9]}': globals()[f'dialog_{topname[9]}'] }, orient='index')
    drama_dialog = drama_dialog.transpose()
    drama_dialog.to_csv(f'{dramaname}_인물별 대본.csv', index=False, encoding='utf-8-sig')
    print(f' {dramaname} 인물별 대본 추출 완료!')