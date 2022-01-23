import re
import pandas as pd
import sys
from tqdm.notebook import tqdm
from hanspell import spell_checker



# 데이터프레임에서 대사 추출
def extract_dialog(dataframe):
    '''
        dataframe: 드라마 대본 데이터프레임, Subtitle 컬럼에 다음과 같은 대사가 포함됨
                   ex) (서진) 그렇게 행복했던 사람이?
    '''
    pair = []            # 등장인물 대사 QA 쌍
    dialog_qa = []       # 최종 형태
    
    for i in range(len(dataframe)):
        sent = dataframe['Subtitle'][i]
                
        # 등장인물 괄호 찾아냄
        start_idx = 0
        matchs = re.finditer(r'\)', sent)
        for match in matchs:
            start_idx = match.span()[1]
            break
        
        # 짝수 번째 대사 0, 2, 4...
        if i%2 == 0:
            sent = sent[start_idx:]
            sent = modify_sent(sent)
            pair.append(sent)
            
        # 홀수 번째 대사 1, 3, 5...
        else:
            sent = sent[start_idx:]
            sent = modify_sent(sent)
            pair.append(sent)
            
            dialog_qa.append(pair)
            pair = []
                            
    return dialog_qa
            

# 대사 텍스트 전처리
def modify_sent(text):
    if '&' in text:
        return text
    
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
    return spell_checker.check(text).checked



if __name__ == '__main__':
    # 드라마 제목, 회차
    dramaname = sys.argv[1]
    dramanum  = int(sys.argv[2])
    
    
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
    
    dropidx = drama_dialog[drama_dialog['A'].str.contains('&' or '♪' or '자막')].index
    drama_dialog = drama_dialog.drop(dropidx)
    dropidx = drama_dialog[drama_dialog['B'].str.contains('&' or '♪' or '자막')].index
    drama_dialog = drama_dialog.drop(dropidx)
    drama_dialog.reset_index(drop=True)
        
    
    # 대본 데이터프레임 저장
    drama_dialog.to_csv(f'{dramaname}_질의별 대본2.csv', index=False, encoding='utf-8-sig')
    print(f' {dramaname} 질의별 대본2 추출 완료!')