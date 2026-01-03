# liasdfiosql

샌드박스 디렉터리에서 안전하게 파일을 둘러보고, 고정된 웹훅으로 결과를 전송할 수 있는 경량 CLI입니다.

- 실행: `liasdfio ...` 또는 `python -m liasdfiosql ...`
- 기본 루트: `./workspace` (존재하지 않으면 생성)

## 설치
```bash
pip install liasdfiosql
```

## 사용법
```bash
liasdfio --help
liasdfio ls                     # 루트 목록
liasdfio cat path/to/file.txt   # 파일 출력
liasdfio find --name "*.py"     # 이름 패턴으로 찾기
liasdfio grep "TODO" --glob "*.py" -i
liasdfio sleep 2                # 최대 300초 대기
# 고정된 웹훅으로 요청 보내기 (응답 최대 1MB 출력)
liasdfio curl
# 다른 명령어 결과를 쿼리스트링(result=...)으로 전송
liasdfio curl --query-cmd ls
liasdfio curl --query-cmd grep TODO --glob "*.py"
```

## 동작 제한
- 루트 밖으로 나가는 경로는 거부
- 읽기/응답은 1MB 초과 시 차단
- `curl`은 http/https만 허용, URL은 고정됨
- `sleep`은 300초 이내만 허용

## 개발
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[test]"
pytest
```
