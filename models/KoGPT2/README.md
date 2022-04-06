# KDrama-Bot
CUAI 4th Winter Conference Project

## Summary
드라마 대본 데이터와 pre-trained KoGPT2를 이용한 Fine-Tuning 챗봇

## Preview
* 스카이 캐슬  
![스카이 캐슬](./imgs/skycastle.png)

* 이태원 클라스  
![이태원 클라스](./imgs/itaewon.png)


## Install
```bash
pip install -r requirements.txt
```

## How to Train
```bash
CUDA_VISIBLE_DEVICES=0 python train_torch.py --gpus 1 --train --max_epochs 50
```

## How to Chat
```bash
CUDA_VISIBLE_DEVICES=0 python train_torch.py --gpus 1 --chat
```

## References
* [KoGPT2](https://github.com/SKT-AI/KoGPT2)
* [KoGPT2-chatbot](https://github.com/haven-jeon/KoGPT2-chatbot/blob/master/README.md)
