"""
Work Assistant MCP Server

프로세스 조회, 회사 정보 질의, 프로세스 실행을 위한 MCP 도구 모음.
Agent가 사용자 요청을 분석하고 필요한 도구를 선택해서 호출합니다.

★ 사용자 요청 유형별 처리 흐름:
1. 프로세스 생성 요청 → generate_process 도구 호출 후 즉시 종료 (프론트엔드에서 실제 처리)
2. 프로세스 실행 요청 → get_process_list → get_process_detail → get_form_fields → execute_process
3. 질문/조회 요청 → get_process_list → get_instance_list → get_todolist 또는 get_organization
"""

import os
import json
import uuid
import logging
import httpx
from typing import Optional, List, Dict, Any
from fastmcp import FastMCP

# 파일 로깅 설정 (즉시 flush)
log_file = os.path.join(os.path.dirname(__file__), 'mcp_debug.log')

# 핸들러에 즉시 flush 설정
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# Supabase 설정
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

# 백엔드 API 설정 (프로세스 실행용)
# API_BASE_URL은 tenant_id를 기반으로 동적 생성: https://{tenant_id}.process-gpt.io
def get_api_base_url(tenant_id: str) -> str:
    """테넌트 ID를 기반으로 API Base URL을 동적으로 생성"""
    return f"https://{tenant_id}.process-gpt.io"

# FastMCP 서버 생성
mcp = FastMCP(
    "work-assistant",
    instructions="""
    이 서버는 업무 지원을 위한 도구들을 제공합니다.
    
    ★★★ 도구 호출 흐름 가이드 (매우 중요) ★★★
    
    【프로세스 생성 요청 시】 예: "휴가신청 프로세스 만들어줘", "새로운 업무 프로세스 생성"
    → generate_process 도구만 호출하고 즉시 종료
    → 다른 도구를 호출하지 말 것! 프론트엔드에서 실제 생성 처리함
    
    【프로세스 실행 요청 시】 예: "12월 26일 휴가 1일 신청", "날씨 검색해줘"
    1. get_process_list → 프로세스 목록에서 관련 프로세스 ID 확인
    2. get_process_detail → 프로세스 상세에서 첫 번째 액티비티와 폼 키 확인
    3. get_form_fields → 폼 필드 정보 조회하여 어떤 값을 입력해야 하는지 확인
    4. execute_process → 사용자 요청에서 추출한 값으로 폼을 채워 프로세스 실행
    
    【프로세스 실행 결과 조회 시】 예: "나라장터 검색 결과 알려줘", "진행 중인 업무"
    1. get_process_list → 프로세스 목록에서 관련 프로세스 ID 확인
    2. get_instance_list → 해당 프로세스의 인스턴스 목록 조회
    3. get_todolist → 인스턴스의 실행 결과(output) 조회
    
    【조직도 조회 시】 예: "조직도 보여줘", "개발팀 누구야?"
    → get_organization 직접 호출
    
    【프로세스 상세 정보 조회 시】 예: "휴가신청 프로세스 단계가 뭐야?"
    1. get_process_list → 프로세스 ID 확인
    2. get_process_detail → 상세 정보 조회
    
    ★ 중요: 프로세스 실행 시 사용자 메시지에서 폼 필드에 맞는 값을 추출하세요.
    예: "12월 26일 휴가 1일 신청" → start_date: "2024-12-26", days: 1
    """
)


def get_supabase_headers() -> dict:
    """Supabase API 호출용 헤더 생성"""
    return {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }


def generate_uuid() -> str:
    """UUID 생성"""
    return str(uuid.uuid4())


# =============================================================================
# 도구 1: 프로세스 생성 (프론트엔드 위임)
# =============================================================================
@mcp.tool()
async def generate_process(user_message: str) -> str:
    """
    프로세스 생성 요청을 처리합니다.
    
    ★★★ 매우 중요 ★★★
    - 사용자가 프로세스 생성/만들기를 요청한 경우 이 도구만 호출하고 즉시 종료하세요.
    - 이 도구 호출 후 다른 도구를 호출하지 마세요!
    - 실제 프로세스 생성은 프론트엔드에서 처리됩니다.
    
    ★ 사용 예시 (이런 요청이 오면 이 도구를 호출):
    - "휴가신청 프로세스 만들어줘"
    - "새로운 업무 프로세스 생성해줘"
    - "출장신청 워크플로우 만들어줘"
    - "프로세스 하나 만들고 싶어"
    - "업무 자동화 프로세스 생성"
    
    ★ 동작 방식:
    1. 이 도구 호출 (사용자의 원본 메시지를 user_message 파라미터로 전달)
    2. 고정된 JSON 응답 반환 (user_message 포함)
    3. 에이전트 동작 종료 (추가 도구 호출 금지)
    4. 프론트엔드가 응답을 받아 프로세스 생성 UI로 전환
    
    Args:
        user_message: 사용자가 입력한 원본 메시지 (프론트엔드에서 프로세스 생성 시 활용)
    
    Returns:
        항상 {"user_request_type": "generate_process", "user_message": "사용자가 입력한 원본 메시지"} 반환
    """
    return json.dumps({"user_request_type": "generate_process", "user_message": user_message}, ensure_ascii=False)


# =============================================================================
# 도구 2: 프로세스 목록 조회
# =============================================================================
@mcp.tool()
async def get_process_list(tenant_id: str) -> str:
    """
    프로세스 정의 목록을 조회합니다.
    
    ★ 호출 시점 (매우 중요):
    - 프로세스 관련 모든 요청의 첫 번째 단계
    - 사용자가 어떤 프로세스를 실행/조회하려는지 파악하기 위해 반드시 먼저 호출
    
    ★ 사용 예시:
    - "휴가신청 해줘" → 먼저 이 도구로 "휴가신청" 프로세스 ID 확인
    - "나라장터 검색 결과" → 먼저 이 도구로 "나라장터" 프로세스 ID 확인
    - "어떤 프로세스가 있어?" → 이 도구로 전체 목록 조회
    
    Args:
        tenant_id: 테넌트 ID (서브도메인, 예: "uengine")
    
    Returns:
        프로세스 목록 JSON. 각 프로세스는 id, name을 포함합니다.
        예: [{"id": "vacation_request", "name": "휴가신청"}, ...]
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/proc_def",
                headers=get_supabase_headers(),
                params={
                    "tenant_id": f"eq.{tenant_id}",
                    "select": "id,name"
                }
            )
            response.raise_for_status()
            data = response.json()
            return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# =============================================================================
# 도구 3: 프로세스 상세 조회
# =============================================================================
@mcp.tool()
async def get_process_detail(tenant_id: str, process_id: str) -> str:
    """
    특정 프로세스의 상세 정보를 조회합니다.
    
    ★ 호출 시점:
    - get_process_list 이후, 프로세스 실행 전 반드시 호출
    - 첫 번째 액티비티 ID와 폼 키(tool 필드)를 확인하기 위해 필수
    
    ★ 반환값에서 확인할 것:
    - definition.sequences: source가 "start_event"인 시퀀스의 target이 첫 번째 액티비티 ID
    - definition.activities: 첫 번째 액티비티의 tool 필드에서 "formHandler:" 뒤의 값이 폼 키
    - definition.roles: 역할 목록 (프로세스 실행 시 role_mappings에 사용)
    
    ★ 사용 예시:
    - "휴가신청" 실행 시 → 이 도구로 첫 번째 액티비티와 폼 키 확인
    - "이 프로세스 어떻게 진행돼?" → 이 도구로 단계별 흐름 확인
    
    Args:
        tenant_id: 테넌트 ID (서브도메인)
        process_id: 프로세스 정의 ID (get_process_list에서 얻은 id 값)
    
    Returns:
        프로세스 상세 정보 JSON. definition 필드에 activities(단계), roles(역할), 
        events(시작/종료 이벤트), sequences(흐름) 등이 포함됩니다.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/proc_def",
                headers=get_supabase_headers(),
                params={
                    "tenant_id": f"eq.{tenant_id}",
                    "id": f"eq.{process_id}",
                    "select": "id,name,definition"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                return json.dumps(data[0], ensure_ascii=False, indent=2)
            else:
                return json.dumps({"error": "프로세스를 찾을 수 없습니다."}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# =============================================================================
# 도구 4: 폼 필드 조회
# =============================================================================
@mcp.tool()
async def get_form_fields(tenant_id: str, form_key: str) -> str:
    """
    폼의 입력 필드 정보를 조회합니다.
    
    ★ 호출 시점:
    - get_process_detail 이후, execute_process 전에 호출
    - 프로세스 실행에 필요한 입력 필드 정보를 얻기 위해 필수
    
    ★ form_key 찾는 방법:
    get_process_detail 결과에서:
    1. sequences에서 source가 "start_event"인 항목 찾기 → target이 첫 번째 액티비티 ID
    2. activities에서 해당 ID의 액티비티 찾기
    3. 해당 액티비티의 tool 필드에서 "formHandler:" 뒤의 값이 form_key
       예: tool이 "formHandler:vacation_request_activity_001_form"이면
           form_key는 "vacation_request_activity_001_form"
    
    ★ 반환값 활용:
    - fields_json: 각 필드의 이름, 타입, 필수 여부 등 확인
    - 사용자 메시지에서 이 필드들에 맞는 값을 추출하여 execute_process에 전달
    
    Args:
        tenant_id: 테넌트 ID (서브도메인)
        form_key: 폼 키 (예: "vacation_request_activity_001_form")
    
    Returns:
        폼 필드 정보 JSON. fields_json에 각 필드의 상세 정보가 포함됩니다.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/form_def",
                headers=get_supabase_headers(),
                params={
                    "tenant_id": f"eq.{tenant_id}",
                    "id": f"eq.{form_key}"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                return json.dumps(data[0], ensure_ascii=False, indent=2)
            else:
                return json.dumps({"error": "폼을 찾을 수 없습니다."}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# =============================================================================
# 도구 5: 프로세스 실행
# =============================================================================
@mcp.tool()
async def execute_process(
    tenant_id: str,
    user_uid: str,
    user_email: str,
    process_definition_id: str,
    activity_id: str,
    form_key: str,
    form_values: Dict[str, Any],
    username: Optional[str] = None
) -> str:
    """
    프로세스를 실행합니다.
    
    ★ 호출 시점:
    - 반드시 get_process_list → get_process_detail → get_form_fields 순서로 호출한 후 마지막에 호출
    - 이전 단계에서 얻은 정보로 파라미터를 채워서 호출
    
    ★ 파라미터 설정 방법:
    1. process_definition_id: get_process_list에서 얻은 프로세스 id
    2. activity_id: get_process_detail에서 찾은 첫 번째 액티비티 id
       - sequences에서 source가 "start_event"인 항목의 target 값
    3. form_key: get_process_detail에서 찾은 폼 키
       - 첫 번째 액티비티의 tool 필드에서 "formHandler:" 뒤의 값
    4. form_values: get_form_fields에서 얻은 필드 정보를 기반으로 사용자 요청에서 추출한 값
       - 예: {"start_date": "2024-12-26", "days": 1, "reason": "개인 사유"}
    
    ★ 역할 매핑 (role_mappings)은 서버에서 자동 생성되므로 전달하지 않아도 됩니다.
    
    ★ 사용 예시:
    사용자: "12월 26일 휴가 1일 신청"
    → form_values: {"start_date": "2024-12-26", "days": 1}
    
    사용자: "날씨 검색 - 서울"
    → form_values: {"location": "서울"}
    
    Args:
        tenant_id: 테넌트 ID (서브도메인)
        user_uid: 실행하는 사용자의 UID (UUID 형식, 예: "550e8400-e29b-41d4-a716-446655440000")
        user_email: 실행하는 사용자의 이메일 (예: "user@example.com")
        process_definition_id: 프로세스 정의 ID
        activity_id: 첫 번째 액티비티 ID
        form_key: 폼 키
        form_values: 폼에 입력할 값들 (dict)
        username: 사용자 이름 (선택, 미제공 시 user_email 사용)
    
    Returns:
        프로세스 실행 결과 JSON. 성공 시 process_instance_id 포함.
    """
    
    try:
        # process_instance_id 생성
        process_instance_id = f"{process_definition_id}.{generate_uuid()}"
        
        # username 기본값 처리 (없으면 email 사용)
        effective_username = username if username else user_email
        
        # role_mappings 초기화 (항상 서버에서 자동 생성)
        role_mappings = None
        
        # role_mappings가 비어있으면 프로세스 정의에서 자동 생성
        if not role_mappings:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    # 프로세스 정의 조회
                    response = await client.get(
                        f"{SUPABASE_URL}/rest/v1/proc_def",
                        headers=get_supabase_headers(),
                        params={
                            "tenant_id": f"eq.{tenant_id}",
                            "id": f"eq.{process_definition_id}",
                            "select": "definition"
                        }
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    if data and len(data) > 0:
                        definition = data[0].get("definition", {})
                        roles = definition.get("roles", [])
                        activities = definition.get("activities", [])
                        logger.info(f"roles: {roles}")
                        logger.info(f"activities 개수: {len(activities)}")
                        
                        # 첫 번째 액티비티의 role 찾기
                        first_activity = None
                        for act in activities:
                            if act.get("id") == activity_id:
                                first_activity = act
                                break
                        
                        first_activity_role = first_activity.get("role") if first_activity else None
                        
                        # 역할 매핑 생성 (ProcessGPTExecute.vue 참고)
                        role_mappings = []
                        for role in roles:
                            role_name = role.get("name")
                            role_default = role.get("default", [])
                            role_endpoint = role.get("endpoint", [])
                            
                            # endpoint 값 결정
                            if role_name == first_activity_role:
                                # 첫 번째 액티비티의 role에 현재 사용자 매핑
                                endpoint_value = user_uid
                            elif role_default:
                                # default 값이 있으면 사용
                                endpoint_value = role_default if isinstance(role_default, list) else [role_default]
                            elif role_endpoint:
                                # endpoint 값이 있으면 사용
                                endpoint_value = role_endpoint if isinstance(role_endpoint, list) else [role_endpoint]
                            else:
                                endpoint_value = ""
                            
                            role_mapping = {
                                "name": role_name,
                                "endpoint": endpoint_value,
                                "resolutionRule": role.get("resolutionRule"),
                                "default": role_default if role_default else ""
                            }
                            role_mappings.append(role_mapping)                        
                    else:
                        logger.warning("프로세스 정의를 찾을 수 없음")
            except Exception as e:
                # 역할 매핑 조회 실패 시 빈 배열로 진행
                logger.error(f"역할 매핑 생성 오류: {e}")
                role_mappings = []
        
        logger.info(f"최종 role_mappings: {role_mappings}")
        
        # 입력 데이터 구성
        input_data = {
            "process_definition_id": process_definition_id.lower(),
            "process_instance_id": process_instance_id,
            "activity_id": activity_id,
            "form_values": {
                form_key: form_values
            },
            "role_mappings": role_mappings,
            "answer": "",
            "user_id": user_uid,
            "username": effective_username,
            "email": user_email,
            "tenant_id": tenant_id,
            "version_tag": "major",
            "version": None,
            "source_list": []
        }
        
        api_base_url = get_api_base_url(tenant_id)
        logger.info(f"API 호출 URL: {api_base_url}/completion/complete")
        logger.info(f"API 호출 input_data: {json.dumps(input_data, ensure_ascii=False, default=str)}")
        
        # API 호출
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{api_base_url}/completion/complete",
                headers={
                    "Content-Type": "application/json"
                },
                json={"input": input_data}
            )
            logger.info(f"API 응답 status_code: {response.status_code}")
            logger.info(f"API 응답 body: {response.text[:500] if response.text else 'empty'}")
            
            response.raise_for_status()
            result = response.json()
            
            # 성공 응답에 process_instance_id 추가
            if isinstance(result, dict):
                result["process_instance_id"] = process_instance_id
                result["message"] = f"프로세스 '{process_definition_id}'가 성공적으로 실행되었습니다."
            
            logger.info(f"========== execute_process 성공 ==========")
            return json.dumps(result, ensure_ascii=False, indent=2)
            
    except httpx.HTTPStatusError as e:
        logger.error(f"API 호출 실패: {e.response.status_code}")
        logger.error(f"API 에러 응답: {e.response.text}")
        return json.dumps({
            "error": f"API 호출 실패: {e.response.status_code}",
            "detail": e.response.text
        }, ensure_ascii=False)
    except Exception as e:
        logger.error(f"execute_process 예외 발생: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# =============================================================================
# 도구 6: 인스턴스 목록 조회
# =============================================================================
@mcp.tool()
async def get_instance_list(tenant_id: str, user_uid: str, process_id: Optional[str] = None) -> str:
    """
    진행 중인 프로세스 인스턴스(업무) 목록을 조회합니다.
    
    ★ 호출 시점:
    - 프로세스 실행 결과를 조회할 때 사용
    - get_process_list 이후에 호출하여 특정 프로세스의 인스턴스 확인
    
    ★ 사용 예시:
    - "내 진행 중인 업무" → process_id 없이 호출
    - "휴가신청 현황" → get_process_list로 휴가신청 ID 확인 후 process_id로 필터링
    - "나라장터 실행 결과" → get_process_list로 나라장터 ID 확인 후 process_id로 필터링
    
    ★ 다음 단계:
    - 이 도구로 얻은 proc_inst_id를 get_todolist에 전달하여 실행 결과 확인
    
    Args:
        tenant_id: 테넌트 ID (서브도메인)
        user_uid: 사용자 UID (참여자로 필터링)
        process_id: (선택) 특정 프로세스로 필터링할 경우 프로세스 ID
    
    Returns:
        인스턴스 목록 JSON. 각 인스턴스는 proc_inst_id, proc_def_id, status, 
        start_date, participants, current_activity_ids 등을 포함합니다.
    """
    try:
        params = {
            "tenant_id": f"eq.{tenant_id}",
            "participants": f"cs.{{{user_uid}}}"  # contains user_uid
        }
        
        if process_id:
            params["proc_def_id"] = f"eq.{process_id}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/bpm_proc_inst",
                headers=get_supabase_headers(),
                params=params
            )
            response.raise_for_status()
            data = response.json()
            return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# =============================================================================
# 도구 7: 할 일 목록 조회 (실행 결과 포함)
# =============================================================================
@mcp.tool()
async def get_todolist(tenant_id: str, instance_ids: List[str]) -> str:
    """
    특정 인스턴스들의 할 일(activity) 목록과 실행 결과를 조회합니다.
    
    ★ 호출 시점:
    - 프로세스 실행 결과를 확인할 때 마지막 단계로 호출
    - get_process_list → get_instance_list → get_todolist 순서로 호출
    
    ★ 중요: 실행 결과는 각 activity의 output 필드에 저장됩니다.
    - 에이전트가 실행한 작업의 결과물이 output에 포함
    - 예: 검색 결과, API 호출 결과 등
    
    ★ 사용 예시:
    - "나라장터 검색 결과 알려줘" → output 필드에서 검색 결과 확인
    - "휴가신청 진행 상황" → status와 output으로 진행 상황 확인
    
    Args:
        tenant_id: 테넌트 ID (서브도메인)
        instance_ids: 조회할 인스턴스 ID 목록 (get_instance_list에서 얻은 proc_inst_id 값들)
    
    Returns:
        할 일 목록 JSON. 프로세스별, 인스턴스별로 그룹화된 activity 정보.
        각 activity에는 activityId, activityName, status, output(실행 결과) 등이 포함됩니다.
    """
    try:
        if not instance_ids:
            return json.dumps({"error": "instance_ids가 비어있습니다."}, ensure_ascii=False)
        
        # instance_ids를 쉼표로 구분된 문자열로 변환
        ids_filter = ",".join([f'"{id}"' for id in instance_ids])
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/todolist",
                headers=get_supabase_headers(),
                params={
                    "tenant_id": f"eq.{tenant_id}",
                    "proc_inst_id": f"in.({ids_filter})",
                    "order": "start_date.asc"
                }
            )
            response.raise_for_status()
            todos = response.json()
            
            # 프로세스별, 인스턴스별로 그룹화
            result = {}
            for todo in todos:
                def_id = todo.get("proc_def_id", "unknown")
                inst_id = todo.get("proc_inst_id", "unknown")
                
                if def_id not in result:
                    result[def_id] = {"processDefinitionId": def_id, "instances": {}}
                
                if inst_id not in result[def_id]["instances"]:
                    result[def_id]["instances"][inst_id] = {"instanceId": inst_id, "activities": []}
                
                result[def_id]["instances"][inst_id]["activities"].append({
                    "activityId": todo.get("activity_id"),
                    "activityName": todo.get("activity_name"),
                    "status": todo.get("status"),
                    "startDate": todo.get("start_date"),
                    "endDate": todo.get("end_date"),
                    "userId": todo.get("user_id"),
                    "output": todo.get("output")  # 실행 결과
                })
            
            return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# =============================================================================
# 도구 8: 조직도 조회
# =============================================================================
@mcp.tool()
async def get_organization(tenant_id: str) -> str:
    """
    회사 조직도를 조회합니다.
    
    ★ 호출 시점:
    - 조직도에 대한 질문에만 사용
    - 다른 도구 호출 없이 바로 사용 가능
    
    ★ 사용 예시:
    - "조직도 보여줘"
    - "우리 회사 구조가 어떻게 돼?"
    - "개발팀에 누가 있어?"
    - "팀원 누구야?"
    
    Args:
        tenant_id: 테넌트 ID (서브도메인)
    
    Returns:
        조직도 정보 JSON. 부서, 팀, 직원 계층 구조를 포함합니다.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/configuration",
                headers=get_supabase_headers(),
                params={
                    "tenant_id": f"eq.{tenant_id}",
                    "key": "eq.organization"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                value = data[0].get("value", {})
                chart = value.get("chart", value) if isinstance(value, dict) else value
                return json.dumps(chart, ensure_ascii=False, indent=2)
            else:
                return json.dumps({"error": "조직도 정보를 찾을 수 없습니다."}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# =============================================================================
# 메인 진입점
# =============================================================================
def main():
    """MCP 서버 실행"""
    mcp.run()


if __name__ == "__main__":
    main()
