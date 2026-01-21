import streamlit as st
from pathlib import Path
import json
import io
import zipfile
from datetime import datetime

# ---------------------------------
# Page config
# ---------------------------------
st.set_page_config(
    page_title="برنامج كابتن سعيد محمود",
    page_icon="💪",
    layout="wide"
)

BASE_DIR = Path(__file__).parent
IMG_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
VID_EXTS = {".mp4", ".webm", ".mov"}

# 👇 عدّل ده حسب اسم ملفك الحقيقي
RUN_FILE_NAME = Path(__file__).name  # يطبع اسم الملف الحالي تلقائيًا

# ---------------------------------
# Theme: Black + Yellow (Fitness)
# ---------------------------------
BRAND_CSS = """
<style>
.stApp {
  background: radial-gradient(900px 600px at 20% 0%, rgba(255,193,7,0.10), transparent 60%),
              radial-gradient(900px 600px at 100% 10%, rgba(255,193,7,0.08), transparent 55%),
              #070a0f;
  color: #e8eef6;
}
[data-testid="stSidebar"] {
  background: #0b0f14;
  border-right: 1px solid rgba(255,255,255,0.06);
}
h1,h2,h3 { color:#ffffff !important; letter-spacing: 0.2px; }

.hero {
  background: linear-gradient(135deg, rgba(255,193,7,0.18), rgba(255,193,7,0.07));
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 22px;
  padding: 18px 18px 14px 18px;
  margin: 10px 0 18px 0;
  box-shadow: 0 10px 28px rgba(0,0,0,0.35);
}
.card {
  background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 18px;
  padding: 18px;
  margin: 16px 0;
  box-shadow: 0 8px 24px rgba(0,0,0,0.30);
}
.badge {
  display:inline-block;
  padding:6px 10px;
  border-radius:999px;
  background: rgba(255,193,7,0.16);
  border:1px solid rgba(255,193,7,0.35);
  font-size:12px;
  margin-right:8px;
  margin-top:8px;
}
.badge2 {
  display:inline-block;
  padding:6px 10px;
  border-radius:999px;
  background: rgba(0,200,120,0.14);
  border:1px solid rgba(0,200,120,0.30);
  font-size:12px;
  margin-right:8px;
  margin-top:8px;
}
.mini { color: rgba(232,238,246,0.78); font-size:14px; }
.small { color: rgba(232,238,246,0.62); font-size:13px; }
hr { border: 0; height: 1px; background: rgba(255,255,255,0.12); margin: 18px 0; }
a, a:visited { color: #ffd54a; }
</style>
"""
st.markdown(BRAND_CSS, unsafe_allow_html=True)

# ---------------------------------
# Coach Config
# ---------------------------------
COACH = {
    "name": "كابتن سعيد محمود",
    "subtitle": "برنامج تمارين + نظام غذائي — شرح تفصيلي لكل صورة + أخطاء شائعة",
    "tagline": "BLACK • YELLOW • FITNESS",
    "image": "images/coach/captain_saeed.jpg",
    "facebook": "https://www.facebook.com/share/14W2zkEeTCh/?mibextid=wwXIfr",
    "instagram": "https://www.instagram.com/sa3ed.ma7moudd?igsh=MWsyaDVkYnVvdXQxMA==",
}

# ترتيب الأقسام المطلوب
SECTIONS = [
    ("تمارين البنش 💛", "images/bench"),
    ("تمارين الظهر 🧱", "images/back"),
    ("تمارين الكتف 🏋️", "images/shoulders"),
]

ARMS = [
    ("تمارين الباي 💥", "images/biceps"),
    ("تمارين التراي 🔥", "images/triceps"),
]

# ---------------------------------
# Helpers (Cached)
# ---------------------------------
@st.cache_data(show_spinner=False)
def safe_read_json_cached(p_str: str) -> dict:
    p = Path(p_str)
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}

def list_images(folder: Path):
    if not folder.exists():
        return []
    imgs = [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in IMG_EXTS]
    return sorted(imgs, key=lambda x: x.name.lower())

def list_videos(folder: Path):
    if not folder.exists():
        return []
    vids = [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in VID_EXTS]
    return sorted(vids, key=lambda x: x.name.lower())

def list_exercise_dirs(section_folder: Path, query: str = ""):
    if not section_folder.exists():
        return []
    dirs = [d for d in section_folder.iterdir() if d.is_dir()]
    dirs = sorted(dirs, key=lambda x: x.name.lower())
    if query:
        q = query.strip().lower()
        dirs = [d for d in dirs if q in d.name.lower()]
    return dirs

def render_list(title: str, items):
    if not items:
        return
    st.markdown(f"**{title}:**")
    for x in items:
        st.write(f"- {x}")

@st.cache_data(show_spinner=True)
def zip_project_cached(base_dir_str: str) -> bytes:
    base_dir = Path(base_dir_str)
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, "w", zipfile.ZIP_DEFLATED) as z:
        skip_dirs = {".git", "__pycache__", ".venv", "venv", ".mypy_cache", ".pytest_cache"}
        for f in base_dir.rglob("*"):
            if f.is_dir() and f.name in skip_dirs:
                continue
            if f.is_file():
                parts = set(f.parts)
                if parts & skip_dirs:
                    continue
                z.write(f, f.relative_to(base_dir).as_posix())
    return bio.getvalue()

def get_per_image_info(info: dict, filename: str, idx: int) -> dict:
    per_map = info.get("per_image", {})
    if isinstance(per_map, dict) and filename in per_map:
        return per_map[filename]
    per_list = info.get("per_image_list", [])
    if isinstance(per_list, list) and idx < len(per_list):
        return per_list[idx]
    return {}

# Fallback أذكى شوية لما مفيش info.json
def smart_fallback(ex_name: str, section_title: str):
    name = ex_name.replace("_", " ").replace("-", " ").strip().title()
    # targets بسيطة حسب القسم
    if "بنش" in section_title:
        targets = ["صدر", "ترايسبس", "كتف أمامي"]
    elif "ظهر" in section_title:
        targets = ["لاتس", "ميد باك", "بايسبس مساعد"]
    elif "كتف" in section_title:
        targets = ["كتف جانبي/أمامي", "ترايسبس مساعد"]
    elif "باي" in section_title:
        targets = ["بايسبس", "ساعد"]
    elif "تراي" in section_title:
        targets = ["ترايسبس"]
    else:
        targets = ["عضلات مساعدة"]

    return {
        "display_name": name,
        "targets": targets,
        "sets_reps": "3–4 مجموعات × 8–12 تكرار (حسب مستواك)",
        "why": ["يبني قوة وتحكم ويُحسن الشكل العضلي."],
        "how": ["حافظ على ثبات الجسم، واشتغل بمدى حركة مريح وتحكم كامل."],
        "mistakes": ["استخدام وزن أكبر من اللازم", "سرعة زائدة بدون تحكم", "وضعية كتف/ظهر غير ثابتة"],
    }

def exercise_card_from_folder(ex_dir: Path, section_title: str):
    info_path = ex_dir / "info.json"
    info = safe_read_json_cached(str(info_path)) if info_path.exists() else smart_fallback(ex_dir.name, section_title)

    display_name = info.get("display_name") or ex_dir.name.replace("_", " ").title()
    targets = info.get("targets", [])
    sets_reps = info.get("sets_reps", "3–4 مجموعات × 8–12 تكرار (حسب مستواك)")

    imgs = list_images(ex_dir)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"### {display_name}")

    if targets:
        st.markdown(f"<span class='badge'>🎯 {', '.join(targets)}</span>", unsafe_allow_html=True)
    if sets_reps:
        st.markdown(f"<span class='badge2'>📌 {sets_reps}</span>", unsafe_allow_html=True)

    st.markdown("<hr/>", unsafe_allow_html=True)

    render_list("✅ ليه التمرين مهم", info.get("why", []))
    render_list("🧠 طريقة الأداء الصحيحة", info.get("how", []))
    with st.expander("⚠️ أخطاء شائعة لازم تتجنبها (للتمرين ككل)"):
        mistakes = info.get("mistakes", [])
        if mistakes:
            for m in mistakes:
                st.write(f"- {m}")
        else:
            st.write("- ثبّت جسمك وتحكم في الحركة بدون ترجيح.")

    if not imgs:
        st.warning(f"⚠️ مفيش صور داخل: {ex_dir.as_posix()}")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    st.markdown("#### 📸 صور التمرين (شرح لكل صورة)")
    for i, im in enumerate(imgs):
        per = get_per_image_info(info, im.name, i)
        title = per.get("title") or f"صورة {i+1}"
        st.image(str(im), use_container_width=True, caption=title)

        img_targets = per.get("targets", [])
        img_how = per.get("how", [])
        img_mistakes = per.get("mistakes", [])
        img_note = per.get("note")

        if img_targets:
            st.markdown(f"<span class='badge'>🎯 تستهدف: {', '.join(img_targets)}</span>", unsafe_allow_html=True)
        else:
            # fallback بسيط للصورة
            st.markdown(f"<span class='badge'>🎯 تستهدف: {', '.join(targets) if targets else 'عضلات مساعدة'}</span>", unsafe_allow_html=True)

        if img_how:
            render_list("🧩 شرح الصورة (الطريقة)", img_how)
        else:
            st.write("**🧩 شرح الصورة:**")
            st.write("- ثبّت جسمك وتحكم في الحركة. ركّز على الإحساس بالعضلة المستهدفة.")

        if img_mistakes:
            with st.expander("❌ أخطاء تتجنبها (لهذه الصورة)"):
                for m in img_mistakes:
                    st.write(f"- {m}")

        if img_note:
            st.info(img_note)

        st.divider()

    st.markdown("</div>", unsafe_allow_html=True)

def section_page(title: str, folder: str, query: str = ""):
    section_dir = BASE_DIR / folder

    st.markdown(
        f"""
        <div class="hero">
          <div style="display:flex; gap:12px; align-items:center; flex-wrap:wrap;">
            <div style="font-size:34px;">💪</div>
            <div>
              <h2 style="margin:0;">{title}</h2>
              <div class="mini">كل تمرين فولدر → جوّاه صور بأي أسماء + (اختياري) ملف info.json لشرح كل صورة</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    ex_dirs = list_exercise_dirs(section_dir, query=query)
    if not ex_dirs:
        st.warning(f"⚠️ مفيش تمارين مطابقة داخل: {folder}")
        return

    for ex_dir in ex_dirs:
        exercise_card_from_folder(ex_dir, title)

def page_home():
    st.markdown("<div class='hero'>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1.8], vertical_alignment="center")
    with c1:
        coach_img = BASE_DIR / COACH["image"]
        if coach_img.exists():
            st.image(str(coach_img), use_container_width=True)
        else:
            st.warning(f"⚠️ صورة الكابتن غير موجودة: {COACH['image']}")

    with c2:
        st.markdown(f"# {COACH['name']}")
        st.markdown(f"<div class='mini'>{COACH['subtitle']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='small'>{COACH['tagline']}</div>", unsafe_allow_html=True)

        st.markdown("<hr/>", unsafe_allow_html=True)
        colA, colB = st.columns(2)
        with colA:
            st.link_button("📘 Facebook", COACH["facebook"])
        with colB:
            st.link_button("📸 Instagram", COACH["instagram"])

        st.markdown("<hr/>", unsafe_allow_html=True)
        st.write("✅ ترتيب الأقسام: بنش → ضهر → كتف → ذراع")
        st.write("✅ شرح لكل صورة داخل كل تمرين (من info.json) + fallback ذكي لو مش موجود")
        st.write("✅ إمكانية تحميل المشروع ZIP من السايدبار (Cached)")

    st.markdown("</div>", unsafe_allow_html=True)

    coach_dir = BASE_DIR / "images/coach"
    hero_imgs = [p for p in list_images(coach_dir) if p.name.lower() not in {"captain_saeed.jpg"}]
    vids = list_videos(coach_dir)

    if hero_imgs or vids:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 🎬 معرض الكابتن (صور / فيديو)")
        for v in vids:
            st.video(str(v))
        for im in hero_imgs:
            st.image(str(im), use_container_width=True, caption=im.stem.replace("_", " "))
        st.markdown("</div>", unsafe_allow_html=True)

def page_nutrition():
    st.markdown("<div class='hero'>", unsafe_allow_html=True)
    st.markdown("## النظام الغذائي 🍽️")
    st.markdown("<div class='mini'>اكتب هنا خطة الكابتن: تنشيف / تثبيت / تضخيم</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### مثال يوم متوازن")
    st.write("**الإفطار:** بيض + شوفان + فاكهة")
    st.write("**الغداء:** بروتين (دجاج/لحم/تونة) + كارب (رز/بطاطس) + سلطة")
    st.write("**العشاء:** بروتين خفيف + خضار")
    st.write("**سناك:** فاكهة / مكسرات / زبادي")
    st.markdown("### قواعد ذهبية")
    st.write("- اشرب 2–3 لتر مياه")
    st.write("- بروتين عالي حسب الوزن")
    st.write("- نوم 7–8 ساعات")
    st.write("- قلل السكر والمقليات")
    st.markdown("</div>", unsafe_allow_html=True)

def page_arms(query: str = ""):
    st.markdown(
        """
        <div class="hero">
          <h2 style="margin:0;">تمارين الذراع 💪 (باي + تراي)</h2>
          <div class="mini">باي + تراي في صفحة واحدة — وكل تمرين يشرح كل صورة</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    tab1, tab2 = st.tabs(["💥 الباي", "🔥 التراي"])
    with tab1:
        section_page("تمارين الباي 💥", "images/biceps", query=query)
    with tab2:
        section_page("تمارين التراي 🔥", "images/triceps", query=query)

def page_covers():
    covers_dir = BASE_DIR / "images/covers"
    st.markdown("<div class='hero'>", unsafe_allow_html=True)
    st.markdown("## Covers / Branding 🟡⚫")
    st.markdown("<div class='mini'>صور الواجهة/بوسترات/Brand assets</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    imgs = list_images(covers_dir)
    if not imgs:
        st.info("مفيش صور داخل images/covers")
        return

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    for im in imgs:
        st.image(str(im), use_container_width=True, caption=im.stem.replace("_", " "))
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------
# Sidebar
# ---------------------------------
st.sidebar.markdown("## 🟡 Coach Saeed Fitness")
st.sidebar.markdown(f"**{COACH['name']}**")
st.sidebar.caption("Black & Yellow Theme • Fitness")

search_q = st.sidebar.text_input("🔎 ابحث عن تمرين", placeholder="مثال: row / press / curl ...")

page = st.sidebar.radio(
    "اختر القسم",
    [
        "الرئيسية",
        "النظام الغذائي",
        "تمارين البنش",
        "تمارين الظهر",
        "تمارين الكتف",
        "تمارين الذراع (باي + تراي)",
        "Covers / Branding",
    ],
    index=0
)

st.sidebar.markdown("---")

zip_bytes = zip_project_cached(str(BASE_DIR))
st.sidebar.download_button(
    label="⬇️ تحميل المشروع كامل (ZIP)",
    data=zip_bytes,
    file_name=f"Coach_Saeed_Program_{datetime.now().strftime('%Y-%m-%d')}.zip",
    mime="application/zip"
)

st.sidebar.markdown(
    f"<div class='mini'>تشغيل محلي: <code>streamlit run {RUN_FILE_NAME}</code></div>",
    unsafe_allow_html=True
)

# ---------------------------------
# Router
# ---------------------------------
if page == "الرئيسية":
    page_home()
elif page == "النظام الغذائي":
    page_nutrition()
elif page == "تمارين البنش":
    section_page("تمارين البنش 💛", "images/bench", query=search_q)
elif page == "تمارين الظهر":
    section_page("تمارين الظهر 🧱", "images/back", query=search_q)
elif page == "تمارين الكتف":
    section_page("تمارين الكتف 🏋️", "images/shoulders", query=search_q)
elif page == "تمارين الذراع (باي + تراي)":
    page_arms(query=search_q)
elif page == "Covers / Branding":
    page_covers()
