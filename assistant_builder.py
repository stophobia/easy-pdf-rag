from langchain_teddynote.models import OpenAIAssistant
from langchain_teddynote.models import AnthropicPDFAssistant
import os
import json


def setup_openai_assistant(
    openai_api_key: str,
    data_path: str = None,
    assistant_id: str = None,
    vector_id: str = None,
    system_prompt: str = None,
):
    """OpenAI Assistant를 설정하고 초기화하는 함수

    Args:
        openai_api_key (str): OpenAI API 키
        data_path (str, optional): 업로드할 PDF 파일 경로. 기존 어시스턴트를 로드할 때는 불필요
        assistant_id (str, optional): 기존 어시스턴트 ID. 새로 생성할 때는 불필요
        vector_id (str, optional): 기존 벡터스토어 ID. 새로 생성할 때는 불필요
        system_prompt (str, optional): 시스템 프롬프트. 기본값은 None

    Returns:
        OpenAIAssistant: 설정된 어시스턴트 인스턴스
    """
    # RAG 시스템 프롬프트 입력
    _DEFAULT_RAG_INSTRUCTIONS = """You are an assistant for question-answering tasks. 
    Use the following pieces of retrieved context to answer the question. 
    If you don't know the answer, just say that you don't know. 
    Answer in Korean."""

    # 설정(configs)
    configs = {
        "OPENAI_API_KEY": openai_api_key,  # OpenAI API 키
        "instructions": (
            system_prompt if system_prompt is not None else _DEFAULT_RAG_INSTRUCTIONS
        ),  # RAG 시스템 프롬프트
        "PROJECT_NAME": "PDF-RAG-TEST",  # 프로젝트 이름(자유롭게 설정)
        "model_name": "gpt-4o",  # 사용할 OpenAI 모델 이름(gpt-4o, gpt-4o-mini, ...)
        "chunk_size": 1000,  # 청크 크기
        "chunk_overlap": 100,  # 청크 중복 크기
    }

    # 인스턴스 생성
    assistant = OpenAIAssistant(configs)

    # 기존 어시스턴트 로드
    if assistant_id and vector_id:
        assistant.setup_assistant(assistant_id)
        assistant.setup_vectorstore(vector_id)
        return assistant

    if not data_path:
        raise ValueError("새로운 어시스턴트를 생성하려면 data_path가 필요합니다.")

    # .cache/openai_file_db 디렉토리 생성
    db_dir = ".cache/openai_file_db"

    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    # 파일명으로 저장된 정보가 있는지 확인
    file_info_path = os.path.join(db_dir, os.path.basename(data_path) + ".json")

    if os.path.exists(file_info_path):
        print("기존 정보가 있습니다.")
        print(file_info_path)
        # 기존 정보가 있으면 로드
        with open(file_info_path, "r") as f:
            saved_info = json.load(f)

        return setup_openai_assistant(
            openai_api_key,
            data_path,
            assistant_id=saved_info["assistant_id"],
            vector_id=saved_info["vector_id"],
            system_prompt=system_prompt,
        )

    # 파일 업로드 후 file_id 받기
    file_id = assistant.upload_file(data_path)

    # 업로드한 파일의 ID 리스트 생성
    file_ids = [file_id]

    # 새로운 어시스턴트 생성 및 ID 받기
    assistant_id, vector_id = assistant.create_new_assistant(file_ids)

    # 정보를 파일로 저장
    with open(file_info_path, "w") as f:
        json.dump({"assistant_id": assistant_id, "vector_id": vector_id}, f)

    # 어시스턴트 설정
    assistant.setup_assistant(assistant_id)

    # 벡터 스토어 설정
    assistant.setup_vectorstore(vector_id)

    return assistant


def setup_anthropic_assistant(
    anthropic_api_key: str,
    data_path: str = None,
    system_prompt: str = None,
):
    """Anthropic Assistant를 설정하고 초기화하는 함수

    Args:
        anthropic_api_key (str): Anthropic API 키
        data_path (str, optional): 업로드할 PDF 파일 경로
        system_prompt (str, optional): 시스템 프롬프트. 기본값은 None

    Returns:
        AnthropicPDFAssistant: 설정된 어시스턴트 인스턴스
    """

    # 설정(configs)
    configs = {
        "ANTHROPIC_API_KEY": anthropic_api_key,  # Anthropic API 키
        "model": "claude-3-5-sonnet-20241022",  # 사용할 Anthropic 모델
    }

    if not data_path:
        raise ValueError("PDF 파일 경로가 필요합니다.")

    # 인스턴스 생성 및 반환
    assistant = AnthropicPDFAssistant(
        configs, data_path, use_prompt_cache=True, system_prompt=system_prompt
    )
    return assistant
