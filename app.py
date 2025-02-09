import streamlit as st
import requests
import urllib.parse
import firebase_admin
from firebase_admin import credentials, firestore
import os

# -----------------------
# 1. Setup Google OAuth
# -----------------------
CLIENT_ID = os.getenv("CLIENT_ID") 
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
AUTHORIZATION_URL = os.getenv("AUTHORIZATION_URL")
TOKEN_URL = os.getenv("TOKEN_URL")
USERINFO_URL = os.getenv("USERINFO_URL")

def get_google_auth_url():
    """Return the Google OAuth 2.0 authorization URL."""
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "prompt": "consent",
        "access_type": "offline",
    }
    return AUTHORIZATION_URL + "?" + urllib.parse.urlencode(params)

def exchange_code_for_token(code):
    """Exchange authorization code for an access token and ID token."""
    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    r = requests.post(TOKEN_URL, data=data)
    return r.json()

def get_user_info(access_token):
    """Use the access token to get user info from Google."""
    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.get(USERINFO_URL, headers=headers)
    return r.json()

# -----------------------
# 2. Setup Firebase (if needed)
# -----------------------
# Comment out if you're not storing user data in Firebase
try:
    if not firebase_admin._apps:  # If there's no previously initialized app
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"Error connecting to Firebase: {e}")
    db = None

# -----------------------
# 3. Streamlit App
# -----------------------
def main():
    st.title("이기릿 채널 증정 이벤트!")

    # Keep track of user session
    if "user" not in st.session_state:
        st.session_state.user = None

    # Check if we got "code" from Google in URL
    query_params = st.query_params
    if "code" in query_params:
        code = query_params["code"]  # Get the code param
        token_data = exchange_code_for_token(code)
        if "access_token" in token_data:
            user_info = get_user_info(token_data["access_token"])
            # Store user info in session
            st.session_state.user = user_info
            # Clear the query params so the URL is clean
            st.query_params.clear()

            # Optionally store user info in Firebase
            if db:
                # Use user_info["sub"] as a unique user ID
                db.collection("users").document(user_info["sub"]).set({
                    "email": user_info.get("email"),
                    "name": user_info.get("name"),
                    "picture": user_info.get("picture"),
                }, merge=True)

    # If user is logged in, show a form or any restricted content
    if st.session_state.user:
        st.write("이벤트 응모를 위해 아래 구글 폼을 작성해주세요:")
        
        google_form_url = "https://forms.gle/KWozoHo9bLEamgsR7"
        
        st.markdown(f"""
            <a href="{google_form_url}" target="_blank">
                <div style="
                    background-color: #34A853;
                    color: white;
                    padding: 10px 20px;
                    text-align: center;
                    border-radius: 5px;
                    cursor: pointer;
                    width: fit-content;
                    text-decoration: none;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    margin: 20px 0;
                ">
                    🎲 구글 폼으로 응모하기
                </div>
            </a>
        """, unsafe_allow_html=True)

    # If user is not logged in, show a login link
    else:
        st.write("이벤트 참여를 위해 구글 계정으로 로그인해주세요! 👋")
        auth_url = get_google_auth_url()
        st.markdown(
            f"""
            <a href="{auth_url}" target="_self">
                <div style="
                    background-color: #fb8c00;
                    color: white;
                    padding: 10px 20px;
                    text-align: center;
                    border-radius: 5px;
                    cursor: pointer;
                    width: fit-content;
                    text-decoration: none;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                ">
                    🙋🏻‍♀️ Youtube 계정으로 로그인
                </div>
            </a>
            """,
            unsafe_allow_html=True
        )




    st.markdown("---", unsafe_allow_html=True)

    # 유투브 영상 임베딩
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 증정 제품 소개 영상!")
        st.markdown("""
            <iframe
                width="100%"
                height="315"
                src="https://www.youtube.com/embed/Hq2a2Rqllsw"
                frameborder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen>
            </iframe>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("### 갤럭시 리뷰 영상!")
        st.video("https://youtu.be/5TomH-UUZGQ")

    
    # go to vote
    st.markdown("---")
    st.markdown("### 갤럭시 vs 아이폰 블라인드 테스트 하러 가기!")
    st.markdown(
        """
        <a href="https://vote.eegirit.com" target="_self">
            <div style="
                background-color: #fb8c00;
                color: white;
                padding: 10px 20px;
                text-align: center;
                border-radius: 5px;
                cursor: pointer;
                width: fit-content;
                text-decoration: none;
                display: flex;
                align-items: center;
                gap: 10px;
                margin-top: 10px;
            ">
                🎮 블라인드 테스트 참여하기
            </div>
        </a>
        """,
        unsafe_allow_html=True
    )




if __name__ == "__main__":
    main()
