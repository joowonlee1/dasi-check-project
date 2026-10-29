"""같은 탭의 새로고침에서만 로그인 복원. 비밀 숫자/관리자 코드는 저장하지 않습니다."""
import base64
import hashlib
import hmac
import json
import time
import uuid
from pathlib import Path
from urllib.parse import quote
import streamlit as st
import streamlit.components.v1 as components
from cryptography.fernet import Fernet, InvalidToken

PREFIX="_login_resume_"
_component=components.declare_component("dotori_login_resume",path=str(Path(__file__).parent/"login_resume_frontend"))

def _cipher():
    try:
        seed=str(st.secrets.get("login_persistence",{}).get("key",""))
        if not seed:
            seed=str(st.secrets.get("firebase_admin",{}).get("private_key",""))
    except (KeyError,FileNotFoundError):
        seed=""
    if len(seed)<32:
        raise ValueError("로그인 유지용 서버 키가 없습니다.")
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(("dotori-login-v1:"+seed).encode()).digest()))

def _admin_version():
    from admin_tools import _admin_code
    code=_admin_code()
    if not code:raise ValueError("관리자 인증이 비활성화됐습니다.")
    return hashlib.sha256(code.encode()).hexdigest()

def queue(token):
    st.session_state[PREFIX+"op"]={"id":uuid.uuid4().hex,"token":token}

def remember():
    """인증 성공 후에만 호출합니다."""
    import dotori_data as dd
    try:
        payload={"v":1,"exp":time.time()+86400}
        me=dd.citizen()
        if me:
            payload["citizen"]={k:me[k] for k in ("uid","refresh","canonical")}
        if st.session_state.get("admin_open"):
            payload["admin"]=_admin_version()
            payload["exp"]=time.time()+28800
        if "citizen" not in payload and "admin" not in payload:
            queue("");return
        queue(_cipher().encrypt(json.dumps(payload).encode()).decode())
        st.session_state.pop(PREFIX+"warning",None)
    except (ValueError,KeyError):
        st.session_state[PREFIX+"warning"]="로그인은 됐지만 유지 설정이 없어 새로고침하면 다시 로그인해야 해요. firebase_admin 또는 login_persistence.key 설정을 확인하세요."

def clear():
    # logout()의 세션 정리 뒤 호출해야 이전 브라우저 값이 복원되지 않습니다.
    st.session_state[PREFIX+"ready"]=True
    queue("")

def restore(token):
    """서명/만료 확인 후 Firebase에서 시민 토큰과 실제 소유자를 다시 검증."""
    import dotori_data as dd
    from firebase_support import config, request, ConnectionProblem
    try:
        if not isinstance(token,str) or len(token)>16000:return False
        raw=_cipher().decrypt(token.encode(),ttl=86400)
        p=json.loads(raw)
        if p.get("v")!=1 or not isinstance(p.get("exp"),(int,float)) or p["exp"]<=time.time():
            return False
        admin=p.get("admin")
        admin_ok=bool(admin and hmac.compare_digest(admin,_admin_version()))
        account=None;shown=None;saved={}
        if p.get("citizen"):
            c=p["citizen"]
            account={"uid":c["uid"],"refresh":c["refresh"],"token":"","expires":0}
            dd._fresh(account)
            # Firebase の refresh response must belong to the original account.
            key,_=config()
            user=request("https://identitytoolkit.googleapis.com/v1/accounts:lookup?key="+quote(key,safe=""),
                         "POST",{"idToken":account["token"]})
            users=user.get("users",[])
            if not users or users[0].get("localId")!=c["uid"] or users[0].get("disabled"):
                return False
            doc=request(dd._url("citizens/"+quote(c["canonical"],safe="")),token=account["token"])
            f=doc.get("fields",{})
            if f.get("uid",{}).get("stringValue")!=c["uid"]:return False
            shown=f.get("nickname",{}).get("stringValue",c["canonical"])
            saved={k:dd._value(v) for k,v in f.get("stamps",{}).get("mapValue",{}).get("fields",{}).items() if k in dd.STAMP_PLACES}
            account.update(nickname=shown,canonical=c["canonical"])
        if not account and not admin_ok:return False
        if account:
            st.session_state[dd.CITIZEN]=account
            st.session_state[dd.ANON]=account
            st.session_state[dd.STAMPS]=saved
            st.session_state[dd.PENDING_STAMPS]={}
        if admin_ok:st.session_state["admin_open"]=True
        st.session_state[PREFIX+"expires"]=p["exp"]
        return True
    except ConnectionProblem as exc:
        if exc.status in (400,401,403,404):return False
        raise
    except (InvalidToken,ValueError,KeyError,TypeError,AttributeError):
        return False

def bootstrap():
    """app.py의 set_page_config 직후, 로그인 여부로 분기하기 전에 호출."""
    op=st.session_state.get(PREFIX+"op",{"id":"read","token":None})
    result=_component(operation=op,key="login_resume_bridge",default=None)
    if op["id"]!="read":
        if not isinstance(result,dict) or result.get("id")!=op["id"]:
            st.caption("로그인 유지 정보를 반영하고 있어요…")
            st.stop()
        st.session_state.pop(PREFIX+"op",None)
        st.session_state[PREFIX+"ready"]=True
        if result.get("error"):
            st.session_state[PREFIX+"warning"]="브라우저가 저장을 막아 로그인 유지를 적용하지 못했어요."
    if not st.session_state.get(PREFIX+"ready"):
        if not isinstance(result,dict) or result.get("id")!="read":
            st.caption("로그인 상태를 확인하고 있어요…")
            if st.button("로그인 복원 없이 계속",key="resume_skip"):
                st.session_state[PREFIX+"ready"]=True
                queue("")
                st.rerun()
            st.stop()
        token=result.get("token","")
        if token:
            try:ok=restore(token)
            except Exception:
                st.warning("연결 문제로 로그인을 복원하지 못했어요. 저장된 로그인은 아직 지우지 않았어요.")
                if st.button("다시 확인",key="resume_retry"):st.rerun()
                if st.button("기존 로그인 지우고 다시 로그인",key="resume_forget"):
                    clear();st.rerun()
                st.stop()
            if not ok:
                clear();st.rerun()
        st.session_state[PREFIX+"ready"]=True
        if result.get("error"):
            st.session_state[PREFIX+"warning"]="이 브라우저에서는 로그인 유지 저장소를 사용할 수 없어요."
    warning=st.session_state.get(PREFIX+"warning")
    if warning:st.warning(warning)
