import re
import pandas as pd
import sys
from tqdm.notebook import tqdm
from pykospacing import spacing



# 데이터프레임에서 대사 추출
def extract_dialog(dataframe):
    '''
        dataframe: 드라마 대본 데이터프레임, Subtitle 컬럼에 다음과 같은 대사가 포함됨
                   ex) (서진) 그렇게 행복했던 사람이?
    '''
    dialog_temp = ''     # 등장인물 탐색 전 상태
    pair = []            # 등장인물 대사 QA 쌍
    cnt = 0
    dialog_qa = [] 
    
    for i in range(len(dataframe)):
        sent = dataframe['Subtitle'][i]
        
        # 등장인물 괄호 찾아냄
        start_idx = 0
        matchs = re.finditer(r'\)', sent)
        for match in matchs:
            start_idx = match.span()[1]
            break
        
        # 대사에 등장인물이 없는 경우
        if start_idx == 0:
            if len(dialog_temp) == 0: continue
            sent = sent[start_idx:]
            sent = modify_sent(sent) + ' ' 
            dialog_temp += sent
            
        # 대사에 등장인물이 있는 경우
        else:
            cnt += 1
            if len(dialog_temp) > 0:
                pair.append(dialog_temp)
            
            # 인물 대화가 쌍을 이루도록 함
            if cnt >= 2 and len(pair) == 2:
                dialog_qa.append(pair)
                dialog_before = pair[1]
            
                pair = []
                pair.append(dialog_before)
                cnt = 1
                
            dialog_temp = ''
            sent = sent[start_idx:]
            sent = modify_sent(sent) + ' '
            dialog_temp += sent
    return dialog_qa
            

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
    
    
    charname  = []                    # 등장인물 목록
    drama_dialog = pd.DataFrame()     # 대본 데이터프레임
    for i in range(1, dramanum+1, 1):
        data = pd.read_excel(f'./dataset/{dramaname}/{dramaname}_{i}화.xlsx')
        print(f' {dramaname} {i}화 추출 및 전처리 진행...')
        
        dialog_qa = extract_dialog(data)
        dialog_qa = pd.DataFrame(dialog_qa)
        drama_dialog = pd.concat([drama_dialog, dialog_qa], ignore_index=True)
        
       
    # 추가 전처리
    drama_dialog.columns = ['A', 'B']
    drama_dialog['A'] = drama_dialog['A'].apply(lambda x: x.strip())
    drama_dialog['B'] = drama_dialog['B'].apply(lambda x: x.strip())
    
    dropidx = drama_dialog[drama_dialog['A'].str.contains('♪')].index
    drama_dialog = drama_dialog.drop(dropidx)
    dropidx = drama_dialog[drama_dialog['B'].str.contains('♪')].index
    drama_dialog = drama_dialog.drop(dropidx)
    drama_dialog.reset_index(drop=True)
        
    
    # 대본 데이터프레임 저장
    drama_dialog.to_csv(f'{dramaname}_질의별 대본.csv', index=False, encoding='utf-8-sig')
    print(f' {dramaname} 질의별 대본 추출 완료!')