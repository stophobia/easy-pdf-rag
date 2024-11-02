import streamlit as st
from langchain_core.messages.chat import ChatMessage
from dotenv import load_dotenv
from assistant_builder import setup_openai_assistant, setup_anthropic_assistant
from langchain_teddynote.models import AnthropicPDFAssistant
import os

# API KEY 정보로드
load_dotenv()

# 캐시 디렉토리 생성
if not os.path.exists(".cache"):
    os.mkdir(".cache")

# 파일 업로드 전용 폴더
if not os.path.exists(".cache/files"):
    os.mkdir(".cache/files")

st.title("PDF 기반 RAG💬")

# 처음 1번만 실행하기 위한 코드
if "messages" not in st.session_state:
    # 대화기록을 저장하기 위한 용도로 생성한다.
    st.session_state["messages"] = []

if "mode" not in st.session_state:
    st.session_state["mode"] = None

if "assistant" not in st.session_state:
    st.session_state["assistant"] = None

# 사이드바 생성
with st.sidebar:
    # 초기화 버튼 생성
    clear_btn = st.button("대화 초기화", type="primary")

    # 파일 업로드
    uploaded_file = st.file_uploader("파일 업로드", type=["pdf"])

    # 모델 선택 메뉴
    selected_model = st.selectbox(
        "Provider 선택", ["OpenAI Assistant V2", "Anthropic PDF"], index=0
    )

    system_prompt = st.text_area(
        "RAG 프롬프트(지시사항)",
        """You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. 
Answer in Korean.""",
        height=200,
    )

    show_token = st.toggle(
        "토큰 정보 출력(Anthropic 만 지원)", value=False, key="show_token"
    )
    apply_btn = st.button("설정 완료", use_container_width=True, type="primary")


# 이전 대화를 출력
def print_messages():
    for chat_message in st.session_state["messages"]:
        st.chat_message(chat_message.role).write(chat_message.content)


# 새로운 메시지를 추가
def add_message(role, message):
    st.session_state["messages"].append(ChatMessage(role=role, content=message))


# 파일을 캐시 저장(시간이 오래 걸리는 작업을 처리할 예정)
@st.cache_resource(show_spinner="업로드한 파일을 처리 중입니다...")
def embed_file(file):
    # 업로드한 파일을 캐시 디렉토리에 저장합니다.
    file_content = file.read()
    file_path = f"./.cache/files/{file.name}"
    with open(file_path, "wb") as f:
        f.write(file_content)
    return file_path


# OpenAI Assistant V2 생성
def create_openai_assistant(
    openai_api_key: str, data_path: str, system_prompt: str = None
):
    return setup_openai_assistant(
        openai_api_key=openai_api_key, data_path=data_path, system_prompt=system_prompt
    )


# Anthropic PDF 생성
def create_anthropic_assistant(
    anthropic_api_key: str, data_path: str, system_prompt: str = None
):
    return setup_anthropic_assistant(
        anthropic_api_key=anthropic_api_key,
        data_path=data_path,
        system_prompt=system_prompt,
    )


# 설정 완료 버튼이 눌리면...
if apply_btn:
    # 파일이 업로드 되었을 때
    if uploaded_file:
        # 파일 업로드 후 retriever 생성 (작업시간이 오래 걸릴 예정...)
        file_path = embed_file(uploaded_file)
        if selected_model == "OpenAI Assistant V2":
            assistant = create_openai_assistant(
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                data_path=file_path,
                system_prompt=system_prompt,
            )
            st.session_state["mode"] = "openai"
            st.session_state["assistant"] = assistant
        elif selected_model == "Anthropic PDF":
            assistant = create_anthropic_assistant(
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
                data_path=file_path,
                system_prompt=system_prompt,
            )
            st.session_state["mode"] = "anthropic"
            st.session_state["assistant"] = assistant

# 초기화 버튼이 눌리면...
if clear_btn:
    st.session_state["messages"] = []
    if st.session_state["assistant"] is not None:
        st.session_state["assistant"].clear_chat_history()

if st.session_state["mode"] is not None:
    st.subheader(f"`{st.session_state['mode']}` 모드로 설정되었습니다.")

# 이전 대화 기록 출력
print_messages()

# 사용자의 입력
user_input = st.chat_input("궁금한 내용을 물어보세요!")

# 경고 메시지를 띄우기 위한 빈 영역
warning_msg = st.empty()

# 만약에 사용자 입력이 들어오면...
if user_input:
    # assistant 생성
    assistant = st.session_state["assistant"]
    mode = st.session_state["mode"]
    show_token = st.session_state["show_token"]

    if assistant is not None:
        # 사용자의 입력
        st.chat_message("user").write(user_input)
        # 스트리밍 호출
        if mode == "anthropic" and show_token:
            response = assistant.stream(user_input, token_info=True)
        else:
            response = assistant.stream(user_input)

        with st.chat_message("assistant"):
            # 빈 공간(컨테이너)을 만들어서, 여기에 토큰을 스트리밍 출력한다.
            container = st.empty()
            token_usage = []

            ai_answer = ""
            for token in response:
                if mode == "openai":
                    ai_answer += token
                    container.markdown(ai_answer)
                elif mode == "anthropic":
                    if token["type"] == "token":
                        ai_answer += token["content"]
                    elif token["type"] == "usage":
                        token_usage.append(token["content"])
                    container.markdown(ai_answer)

            if show_token:
                token_usage_str = "**토큰 사용량**\n\n"

                for usage in token_usage:
                    # BetaUsage 객체인 경우
                    if "cache_creation_input_tokens" in str(usage):
                        # 문자열을 딕셔너리로 파싱
                        usage_str = str(usage).split("BetaUsage")[-1].strip("()")
                        usage_parts = usage_str.split(", ")
                        usage_dict = {}
                        for part in usage_parts:
                            key, value = part.split("=")
                            usage_dict[key] = int(value)

                        token_usage_str += "| 토큰 유형 | 사용량 |\n"
                        token_usage_str += "|---|---:|\n"
                        token_usage_str += f"| 캐시 생성 입력 토큰 | {usage_dict['cache_creation_input_tokens']} |\n"
                        token_usage_str += f"| 캐시 읽기 입력 토큰 | {usage_dict['cache_read_input_tokens']} |\n"
                        token_usage_str += (
                            f"| 입력 토큰 | {usage_dict['input_tokens']} |\n"
                        )
                        token_usage_str += (
                            f"| 출력 토큰 | {usage_dict['output_tokens']} |\n"
                        )

                    # BetaMessageDeltaUsage 객체인 경우
                    elif "output_tokens" in str(usage):
                        # 문자열을 딕셔너리로 파싱
                        usage_str = (
                            str(usage).split("BetaMessageDeltaUsage")[-1].strip("()")
                        )
                        usage_parts = usage_str.split(", ")
                        usage_dict = {}
                        for part in usage_parts:
                            key, value = part.split("=")
                            usage_dict[key] = int(value)

                        token_usage_str += "| 토큰 유형 | 사용량 |\n"
                        token_usage_str += "|---|---:|\n"
                        token_usage_str += (
                            f"| 출력 토큰 | {usage_dict['output_tokens']} |\n"
                        )
                    token_usage_str += "\n"
                container.markdown(ai_answer + token_usage_str)

        # 대화기록을 저장한다.
        add_message("user", user_input)
        add_message("assistant", ai_answer)
    else:
        # 파일을 업로드 하라는 경고 메시지 출력
        warning_msg.warning("**파일을 업로드**하고, **설정 완료** 버튼을 눌러주세요.")
