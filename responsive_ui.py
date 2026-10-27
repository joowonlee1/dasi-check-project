"""Shared layout only: no quiz, scoring or authentication changes."""
from html import escape
import streamlit as st

def apply_layout():
    st.markdown("<style>" + CSS + "</style>", unsafe_allow_html=True)

CSS = """
[data-testid="stMainBlockContainer"] {min-width:0;}
[data-testid="stMainBlockContainer"] h2,
[data-testid="stMainBlockContainer"] h3 {padding:0!important;margin:16px 0 12px!important;line-height:1.45;}
[data-testid="stMainBlockContainer"] h4 {padding:0!important;margin:12px 0 10px!important;line-height:1.45;}
[data-testid="stMarkdownContainer"] p {line-height:1.65;overflow-wrap:anywhere;}
[data-testid="stAlert"] {padding:16px 18px!important;line-height:1.65;}
[data-testid="stAlert"] p {margin:0!important;}
[data-testid="stButton"] button,[data-testid="stPageLink"] a,
[data-testid="stFormSubmitButton"] button {min-height:48px;box-sizing:border-box;white-space:normal;height:auto;line-height:1.45;}
[data-testid="stButton"] button p,[data-testid="stPageLink"] a p {white-space:normal!important;overflow-wrap:anywhere;line-height:1.45!important;}
.st-key-citizen_top .st-key-side_actions [data-testid="stHorizontalBlock"] {align-items:stretch!important;gap:8px;}
.st-key-citizen_top .st-key-side_actions [data-testid="stColumn"] {min-width:0!important;}
.st-key-citizen_top .st-key-side_actions button,.st-key-citizen_top .st-key-side_actions [data-testid="stPageLink"] a {height:52px!important;min-height:52px!important;width:100%!important;margin:0!important;padding:8px!important;display:flex!important;align-items:center!important;justify-content:center!important;border-radius:14px!important;}
.st-key-citizen_top .st-key-side_actions p {margin:0!important;font-size:.95rem!important;}
.st-key-home_start [data-testid="stPageLink"] a {background:#35685b!important;color:#fff!important;padding:12px 18px!important;border-radius:14px;max-width:520px;}
.st-key-home_start [data-testid="stPageLink"] a p {color:white!important;font-weight:800!important;}
.home-hero {display:flex!important;gap:24px!important;max-width:900px;margin:0 auto;align-items:center;}
.home-hero .txt {flex:1 1 380px!important;min-width:0!important;}
.home-hero .pic {flex:0 0 150px!important;margin:0!important;}
.home-hero .pic img {max-width:150px!important;height:auto!important;}
.st-key-gate_guest {margin-top:16px;}
.stpgrid {margin-bottom:20px!important;overflow:visible;align-items:stretch;}
.stp small,.stp b {overflow-wrap:anywhere;}
[data-testid="stCaptionContainer"] {line-height:1.65;clear:both;}
.jk-hero,.chat-legend {line-height:1.65;}
.st-key-chat_screen {margin-top:8px!important;padding:18px!important;}
.jk-chat-label {margin:0 0 12px!important;line-height:1.6;}
@media(max-width:640px){
 .home-hero {gap:16px!important;flex-wrap:wrap;}
 .home-hero .txt {flex-basis:100%!important;}
 .home-hero .pic {margin:0 auto!important;}
 .jk-tiles {grid-template-columns:1fr!important;}
 .stpgrid {grid-template-columns:repeat(3,minmax(0,1fr))!important;}
 .st-key-citizen_top .st-key-side_actions [data-testid="stHorizontalBlock"] {flex-direction:row!important;}
 .st-key-citizen_top .st-key-side_actions [data-testid="stColumn"] {flex:1 1 0!important;width:calc(50% - 4px)!important;}
}
@media(max-width:380px){.stpgrid{grid-template-columns:repeat(2,minmax(0,1fr))!important;}}
"""

POSITIONS = {
 "01":(30,90), "09":(360,90), "10":(690,90), "04":(865,260),
 "03":(30,315), "14":(30,450), "06":(350,310), "07":(350,440),
 "12":(350,590), "02":(640,385), "05":(640,490), "08":(875,490),
 "11":(640,610), "13":(875,610),
}

def map_html(places, got):
    pins=[]
    for number,(icon,town,place,_) in places.items():
        x,y=POSITIONS[number]
        awarded=number in got
        pins.append(
            f'<div class="city-location{ " visited" if awarded else ""}" style="left:{x}px;top:{y}px" '
            f'aria-label="{escape(town+" "+place+(" 도장 획득" if awarded else ""),quote=True)}">'
            f'<span class="city-marker">{icon}</span><span class="city-name">{escape(place)}</span>'
            + ('<span aria-label="도장 획득">🏅</span>' if awarded else "") + '</div>')
    background = """<svg viewBox="0 0 1120 735" width="1120" height="735" aria-hidden="true">
<rect width="1120" height="735" rx="22" fill="#ecf1df"/>
<path d="M0 208 Q260 135 530 230 T1120 205" fill="none" stroke="#8ac8d4" stroke-width="72"/>
<path d="M0 208 Q260 135 530 230 T1120 205" fill="none" stroke="#b8e0e7" stroke-width="3" stroke-dasharray="20 18"/>
<path d="M280 0V735 M610 0V735 M0 570H1120 M0 370H1120" stroke="#d3c7ad" stroke-width="34"/>
<path d="M280 0V735 M610 0V735 M0 570H1120 M0 370H1120" stroke="#fff9e8" stroke-width="23"/>
<path d="M280 0V735 M610 0V735 M0 570H1120 M0 370H1120" stroke="#dccca8" stroke-width="2" stroke-dasharray="12 12"/>
<path d="M990 0V350" stroke="#8b8277" stroke-width="15"/>
<path d="M990 0V350" stroke="#eee8dc" stroke-width="9" stroke-dasharray="5 9"/>
<circle cx="450" cy="280" r="38" fill="#dfcbb0"/><circle cx="450" cy="280" r="27" fill="#77c3df"/>
<circle cx="450" cy="280" r="12" fill="#d8f3ff"/>
<path d="M438 278Q450 236 462 278" fill="none" stroke="white" stroke-width="4"/>
<g fill="#597749" font-family="sans-serif" font-size="19" font-weight="700">
<text x="40" y="54">🌳 상수리동</text><text x="365" y="54">🍂 떡갈나무동</text>
<text x="710" y="54">🌰 개암골</text><text x="875" y="245">🚉 도토리역 앞</text>
<text x="40" y="290">🐿️ 다람쥐동</text><text x="365" y="415">⛲ 중앙동</text>
<text x="680" y="350">🏛️ 시청로</text></g>
<g font-size="32"><text x="80" y="670">🌳 🌳 🏡</text><text x="740" y="710">🌳 🌲 🌳</text><text x="1030" y="85">🚉</text></g>
</svg>"""
    return """<style>
.city-scroll{width:100%;overflow-x:auto;border:2px solid #ded3b3;border-radius:22px;background:#ecf1df;margin:12px 0 20px;overscroll-behavior-x:contain;}
.city-art{position:relative;width:1120px;height:735px;}
.city-art>svg{position:absolute;inset:0;max-width:none;}
.city-location{position:absolute;display:flex;align-items:center;gap:7px;box-sizing:border-box;width:215px;min-height:64px;padding:10px 12px;border:2px solid #c6d5bd;border-radius:14px;background:#fffefa;box-shadow:0 4px 0 #0000000b;color:#24443b;line-height:1.5;font-size:15px;font-weight:750;}
.city-location::after{content:"";position:absolute;bottom:-10px;left:20px;width:16px;height:16px;background:inherit;border-right:2px solid #c6d5bd;border-bottom:2px solid #c6d5bd;transform:rotate(45deg);}
.city-location.visited,.city-location.visited::after{border-color:#b42318;}
.city-location.visited{background:#fff3dc;}
.city-name{min-width:0;overflow-wrap:anywhere;word-break:keep-all;}
.city-marker{font-size:24px;flex-shrink:0;}
</style><div class="city-scroll" tabindex="0" role="region" aria-label="도토리시 지도. 좁은 화면에서는 좌우로 스크롤하세요."><div class="city-art">""" + background + "".join(pins) + "</div></div>"

def show_city_map(places, got):
    st.markdown(map_html(places,got).replace("\n",""),unsafe_allow_html=True)
    st.caption("↔ 좁은 화면에서는 지도를 좌우로 밀어 모든 장소를 볼 수 있어요.")
