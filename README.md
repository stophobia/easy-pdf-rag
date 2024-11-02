## EASY PDF RAG

OpenAI Assistant V2 와 Anthropic 의 PDF 기능을 기반으로 RAG 기능을 구현한 예제입니다.

- made by[테디노트](https://www.youtube.com/c/teddynote)

> Anthropic PDF 기능 예시

![anthropic-pdf](./assets/anthropic.png)

> OpenAI Assistant V2 예시

![openai-assistant](./assets/openai.png)

### YouTube 튜토리얼

아래의 영상을 시청하시면서 따라서 진행하세요.

[![설명 영상](https://img.youtube.com/vi/JVBXekOaKJw/0.jpg)](https://youtu.be/JVBXekOaKJw)

### 설치

> poetry 사용(권장)
```bash
poetry shell
poetry update
```

> conda 사용
```bash
conda create -n easy-pdf-rag python=3.11
conda activate easy-pdf-rag
pip install -r requirements.txt
```

### 실습파일

**Jupyter Notebook**
- [OpenAI-Assistant-V2](https://github.com/teddylee777/easy-pdf-rag/blob/main/01-OpenAI-Assistant-V2.ipynb)
- [Anthropic-PDF](https://github.com/teddylee777/easy-pdf-rag/blob/main/02-Anthropic-PDF-Parsing.ipynb)

**Google Colab**
- [OpenAI-Assistant-V2](https://colab.research.google.com/github/teddylee777/easy-pdf-rag/blob/main/01-OpenAI-Assistant-V2.ipynb)
- [Anthropic-PDF](https://colab.research.google.com/github/teddylee777/easy-pdf-rag/blob/main/02-Anthropic-PDF-Parsing.ipynb)

### Streamlit 실행

```bash
streamlit run main.py
```
