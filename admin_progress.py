
"""관리자 인증 후에만 접근하는 공용 도장 저장소. 시민 기록과 분리합니다."""
import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import urlencode
KEY="admin_progress_stamps"
PENDING="admin_progress_pending"
ERROR="admin_progress_error"

def active():
    import dotori_data as dd
    return bool(st.session_state.get("admin_open")) and not dd.citizen()

def load(force=False):
    if not active():return {}
    if st.session_state.get("admin_progress_loaded") and not force:
        return st.session_state.setdefault(KEY,{})
    import dotori_data as dd
    from admin_tools import _token
    from firebase_support import request, ConnectionProblem
    local=st.session_state.setdefault(KEY,{})
    try:
        try:doc=request(dd._url("admin_progress/shared"),token=_token())
        except ConnectionProblem as exc:
            if exc.status!=404:raise
            doc={}
        fields=doc.get("fields",{}).get("stamps",{}).get("mapValue",{}).get("fields",{})
        saved={k:v["stringValue"] for k,v in fields.items() if k in dd.STAMP_PLACES and isinstance(v.get("stringValue"),str)}
        saved.update(local)
        st.session_state[KEY]=saved
        st.session_state["admin_progress_loaded"]=True
        st.session_state.pop(ERROR,None)
    except Exception:
        st.session_state[ERROR]="관리자 도장을 서버에서 읽지 못했어요. firebase_admin 설정과 연결을 확인하세요."
    return st.session_state[KEY]

def sync():
    if not active():return False
    pending=dict(st.session_state.get(PENDING,{}))
    if not pending:return True
    import dotori_data as dd
    from admin_tools import _token
    from firebase_support import request
    try:
        fields={k:{"stringValue":v} for k,v in pending.items() if k in dd.STAMP_PLACES}
        query=urlencode([("updateMask.fieldPaths","stamps."+chr(96)+k+chr(96)) for k in fields])
        request(dd._url("admin_progress/shared")+"?"+query,"PATCH",{"fields":{"stamps":{"mapValue":{"fields":fields}}}},_token())
        current=st.session_state.setdefault(PENDING,{})
        for k,v in pending.items():
            if current.get(k)==v:current.pop(k,None)
        st.session_state.pop(ERROR,None)
        return True
    except Exception:
        st.session_state[ERROR]="관리자 도장이 아직 저장되지 않았어요. 새로고침 전에 다시 저장해 주세요."
        return False

def award(code,quiet=False):
    if not active():return False
    import dotori_data as dd
    if code not in dd.STAMP_PLACES:return False
    got=load()
    if code in got:return False
    got[code]=datetime.now(ZoneInfo("Asia/Seoul")).strftime("%m/%d %H:%M")
    st.session_state.setdefault(PENDING,{})[code]=got[code]
    sync()
    if not quiet:st.session_state["stamp_popup"]=(code,len(got))
    return True

def status(prefix="sidebar"):
    if not active():return
    load()
    st.caption("관리자 공용 도장판 · 같은 관리자 코드로 이용하는 사람끼리 공유해요.")
    if st.session_state.get(ERROR):st.warning(st.session_state[ERROR])
    if st.session_state.get(PENDING) or st.session_state.get(ERROR):
        if st.button("관리자 도장 불러오기·저장 재시도",key="admin_progress_retry_"+prefix):
            load(force=True)
            sync()
            st.rerun()
    if st.session_state.get("stamp_logout_blocked"):
        st.warning("미저장 도장이 있어 로그아웃을 멈췄어요.")
        if st.button("미저장 관리자 도장을 버리고 로그아웃",key="admin_discard_"+prefix):
            import dotori_data as dd
            dd.logout(discard=True)
            st.rerun()
