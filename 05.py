import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

# ========== 读取 API Key（本地 .env → 云端 st.secrets）==========
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    api_key = st.secrets.get("DEEPSEEK_API_KEY", "")

# 只创建一次 client
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# ========== 页面配置 ==========
st.set_page_config(
    page_title="AI聊天",
    page_icon="😜",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)

st.title("AI聊天")

# ========== 系统提示词 ==========
system_prompt = """
你叫%s，现在是用户的真实伴侣，请完全代入伴侣角色。

规则：
    1. 每次只回1条消息
    2. 禁止任何场景或状态描述性文字
    3. 匹配用户的语言
    4. 回复简短，像微信聊天一样
    5. 有需要的话可以用❤️🌸等emoji表情
    6. 用符合伴侣性格的方式对话
    7. 回复的内容，要充分体现伴侣的性格特征

伴侣性格：
    - %s
你必须严格遵守上述规则来回复用户。
"""

# ========== 初始化状态 ==========
if "messages" not in st.session_state:
    st.session_state.messages = []

if "nick_name" not in st.session_state:
    st.session_state.nick_name = "小甜甜"

if "personality" not in st.session_state:
    st.session_state.personality = "温柔可爱的软妹子"

# ========== 展示历史消息 ==========
for message in st.session_state.messages:
    if message["role"] == "user":
        st.chat_message("user").write(message["content"])
    elif message["role"] == "assistant":
        st.chat_message("assistant").write(message["content"])

# ========== 用户输入 & AI 回复 ==========
prompt = st.chat_input("请输入您的问题：")
if prompt:
    st.chat_message("user").write(prompt)
    print("-----------> 调用AI大模型，提示词：", prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt % (st.session_state.nick_name, st.session_state.personality)},
            *st.session_state.messages
        ],
        stream=True
    )

    response_message = st.empty()
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            full_response += content
            response_message.chat_message("assistant").write(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

# ========== 左侧边栏 ==========
with st.sidebar:
    st.subheader("好友信息")
    st.sidebar.image("https://img.alicdn.com/imgextra/i4/O1CN01Xf9p9j1D01Xf9p9p9j.png")

    nick_name = st.text_input("昵称", placeholder="请输入昵称")
    if nick_name:
        st.session_state.nick_name = nick_name

    personality = st.text_area("性格", placeholder="请输入性格")
    if personality:
        st.session_state.personality = personality