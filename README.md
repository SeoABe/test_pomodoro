# 🍅 포모도로 타이머 (메모리 상주형)

Windows에서 **백그라운드에 상주**하는 가벼운 포모도로 타이머입니다.
항상 위에 뜨는 작은 창과 시스템 트레이 아이콘으로 동시에 동작하며,
창을 닫아도 트레이에 남아 계속 타이머가 흘러갑니다.

> 집중 25분 → 짧은 휴식 5분, 집중 4회마다 긴 휴식 15분. (설정에서 변경 가능)

---

## ✨ 기능

| | 기능 |
|---|---|
| 🪟 | **항상 위 미니 창** + **시스템 트레이** 동시 동작 |
| ⏱️ | 트레이 아이콘에 **원형 진행률 게이지 + 남은 분** 표시 (단계별 색상) |
| ▶️ | 단계 종료 후 **자동으로 다음 단계 시작** (옵션, 끌 수 있음) |
| ⚙️ | **설정 창**에서 시간·주기·자동시작·알림음 변경 → 자동 영구 저장 |
| 🔔 | 단계 종료 시 트레이 풍선 알림 + 알림음 |
| ⬇️ | 창 닫기(X) → 트레이로 최소화 (종료는 트레이 메뉴에서) |
| 📦 | **단일 .exe(약 12MB)** 로 배포 — 파이썬 미설치 PC에서도 실행 |

### 단계별 색상
- 🔴 **집중** (빨강)
- 🟢 **짧은 휴식** (초록)
- 🔵 **긴 휴식** (파랑)

---

## 🚀 사용 방법

### 1) 배포된 exe로 바로 실행 (권장)
[**Releases**](https://github.com/SeoABe/test_pomodoro/releases/latest) 페이지에서 `pomodoro.exe` 하나만 내려받아 실행하면 됩니다.
설치 과정도, 파이썬도 필요 없습니다. 실행하면 화면 우하단에 작은 창과 트레이 아이콘이 나타납니다.

### 2) 소스로 실행 (개발용)
```powershell
pip install -r requirements.txt
python pomodoro.py
```

---

## ⚙️ 설정

실행 중 창의 **⚙ 설정** 버튼 또는 트레이 메뉴 **설정…** 에서 바꿀 수 있습니다.
코드를 고칠 필요가 없습니다.

- 집중 / 짧은 휴식 / 긴 휴식 시간 (분)
- 긴 휴식 주기 (집중 N회마다)
- 단계 종료 후 자동 시작 on/off
- 알림음 on/off

설정은 `%APPDATA%\pomodoro\config.json` 에 자동 저장되어 재시작해도 유지됩니다.

---

## 🔁 부팅 시 자동 시작 (선택)

`Win + R` → `shell:startup` 입력 → 열리는 폴더에
`dist\pomodoro.exe` **바로가기**를 넣으면, 부팅할 때마다 트레이에 자동 상주합니다.

---

## 🛠️ 직접 빌드하기

```powershell
.\build.bat
```
빌드가 끝나면 `dist\pomodoro.exe` 단일 파일이 생성됩니다.

### 용량 최적화 (30MB → 약 12MB)
기본 PyInstaller 빌드는 30MB였지만, 사용하지 않는 의존성을 걷어내고 압축해 60% 줄였습니다.

| 항목 | 절감 |
|---|---|
| `numpy` + OpenBLAS 제거 (Pillow가 자동으로 끌어옴) | 약 12MB |
| `ssl` / `hashlib` → libcrypto·libssl 제거 (네트워크 미사용) | 약 5MB |
| `sqlite3`, PIL AVIF 코덱(`_avif`) 등 미사용 모듈 제거 | 약 1MB |
| UPX 바이너리 압축 | 추가 절감 |

더 줄이려면 [UPX](https://github.com/upx/upx/releases)를 받아
`_tools\upx-4.2.4-win64\upx.exe` 위치에 두면 `build.bat`이 자동으로 사용합니다.

---

## 📂 구성

```
pomodoro.py        # 본체 (단일 파일)
build.bat          # 용량 최적화 빌드 스크립트 (cmd)
build.ps1          # 용량 최적화 빌드 스크립트 (PowerShell)
requirements.txt   # 의존성 (pystray, Pillow)
```
> 빌드 결과물 `dist/pomodoro.exe` 는 저장소에 포함하지 않고 [Releases](https://github.com/SeoABe/test_pomodoro/releases) 로 배포합니다.

## 의존성
- Python 3.8+
- [pystray](https://pypi.org/project/pystray/) (트레이 아이콘)
- [Pillow](https://pypi.org/project/Pillow/) (아이콘 렌더링)
- `tkinter`, `winsound` 은 파이썬 기본 내장

## 라이선스
MIT
