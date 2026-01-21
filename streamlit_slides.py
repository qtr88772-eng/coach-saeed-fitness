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

# ---------------------------------
# Branding / Styling (BLACK x YELLOW Fitness)
# ---------------------------------
BRAND_CSS = """
<style>
.stApp{
  background: radial-gradient(1000px 650px at 10% 0%, rgba(255,193,7,0.10), transparent 60%),
              radial-gradient(900px 600px at 95% 10%, rgba(255,193,7,0.08), transparent 55%),
              #0b0f14;
  color:#e8eef6;
  font-family: "Segoe UI", sans-serif;
}
[data-testid="stSidebar"]{
  background:#0e1117;
  border-right:2px solid rgba(255,193,7,0.55);
}

h1,h2,h3{ color:#ffc107 !important; letter-spacing:.2px; font-weight:800; }

.hero{
  background: linear-gradient(135deg, rgba(255,193,7,0.18), rgba(0,0,0,0.25));
  border:1px solid rgba(255,193,7,0.35);
  border-radius:22px;
  padding:18px 18px 14px 18px;
  margin:10px 0 18px 0;
  box-shadow:0 10px 30px rgba(0,0,0,0.55);
}
.card{
  background:#111827;
  border:1px solid rgba(255,193,7,0.28);
  border-radius:18px;
  padding:18px;
  margin:16px 0;
  box-shadow:0 8px 26px rgba(0,0,0,0.6);
}
.badge{
  display:inline-block;
  padding:6px 10px;
  border-radius:999px;
  background:#ffc107;
  color:#000;
  font-size:12px;
  font-weight:800;
  margin-right:8px;
  margin-top:8px;
}
.badge2{
  display:inline-block;
  padding:6px 10px;
  border-radius:999px;
  background:rgba(255,193,7,0.16);
  border:1px solid rgba(255,193,7,0.45);
  color:#ffc107;
  font-size:12px;
  font-weight:700;
  margin-right:8px;
  margin-top:8px;
}
.mini{ color:rgba(232,238,246,0.78); font-size:14px; }
.small{ color:rgba(232,238,246,0.66); font-size:13px; }

hr{ border:0; height:1px; background:rgba(255,193,7,0.22); margin:18px 0; }

a.social-btn{
  display:inline-block;
  padding:10px 14px;
  border-radius:999px;
  background:#ffc107;
  color:#000 !important;
  font-weight:900;
  text-decoration:none;
  margin-right:10px;
  margin-top:8px;
}
a.social-btn:hover{ background:#ffdb4d; }

.footer{
  margin-top:22px;
  padding:14px;
  border-radius:16px;
  border:1px solid rgba(255,193,7,0.28);
  background:rgba(255,255,255,0.03);
  text-align:center;
}
</style>
"""
st.markdown(BRAND_CSS, unsafe_allow_html=True)

# ---------------------------------
# Coach + Social
# ---------------------------------
COACH = {
    "name": "كابتن سعيد محمود",
    "subtitle": "برنامج تمارين احترافي + نظام غذائي (بدون أيام) — صور + شرح تفصيلي + أخطاء شائعة",
    "image": "images/coach/captain_saeed.jpg",
    "tagline": "Train Smart • Eat Right • Build Better",
    "facebook": "https://www.facebook.com/share/14W2zkEeTCh/?mibextid=wwXIfr",
    "instagram": "https://www.instagram.com/sa3ed.ma7moudd",
}

SECTIONS = [
    ("تمارين البنش 💪", "images/bench"),
    ("تمارين الظهر 🧱", "images/back"),
    ("تمارين الكتف 🏋️", "images/shoulders"),
    ("تمارين الباي 💥", "images/biceps"),
    ("تمارين التراي 🔥", "images/triceps"),
]

# ---------------------------------
# Default Smart Explanations (when no info.json)
# ---------------------------------
DEFAULTS = {
    "bench": {
        "targets": ["الصدر (أساسي)", "الترايسبس (مساعد)", "الكتف الأمامي (مساعد)"],
        "why": [
            "يبني كتلة وقوة في الصدر.",
            "يحسن شكل الجزء العلوي وتناسق الدفع.",
            "ينقل القوة لتمارين كتير (Push).",
        ],
        "how": [
            "ثبّت لوح الكتف لورا وتحت وافتح صدرك.",
            "انزل بتحكم 2–3 ثواني لمدى مريح.",
            "اطلع مع عصر الصدر بدون قفل عنيف للكوع.",
        ],
        "mistakes": [
            "رفع الكتف لفوق أثناء الدفع (بيحمل على الكتف).",
            "نزول سريع بدون تحكم.",
            "تقويس/تسييب الظهر وعدم تثبيت لوح الكتف.",
        ],
        "cues": ["صدر مفتوح", "لوح كتف ثابت", "نزول بطيء", "اطلع بقوة وتحكم"],
        "sets_reps": "3–4 مجموعات × 8–12 تكرار",
    },
    "back": {
        "targets": ["اللاتس (جناب الظهر)", "منتصف الظهر", "الترابيز/أسفل الظهر حسب التمرين"],
        "why": [
            "يزود عرض الظهر (V-shape).",
            "يحسن وضعية الجسم ويقلل انحناء الكتف للأمام.",
            "يدعم القوة في السحب ويوازن تمارين الدفع.",
        ],
        "how": [
            "اسحب بالكوع مش باليد.",
            "حافظ على صدر مرفوع وظهر محايد.",
            "اعصر لوح الكتف ثانية في آخر الحركة.",
        ],
        "mistakes": [
            "الترجيح بالجسم بدل السحب بالعضلة.",
            "تقويس الظهر في الرو/الديدليفت.",
            "سحب بالرقبة ورفع الكتف لفوق.",
        ],
        "cues": ["اسحب بالكوع", "كتف لتحت", "اعصر لوح الكتف", "تحكم في النزول"],
        "sets_reps": "3–4 مجموعات × 8–12 تكرار",
    },
    "shoulders": {
        "targets": ["كتف جانبي", "كتف خلفي", "كتف أمامي (حسب التمرين)"],
        "why": [
            "يزود عرض الكتف وبيعمل شكل رياضي قوي.",
            "تحسين ثبات الكتف وتقليل إصابات الدفع.",
            "تفصيل أعلى الجسم مع الصدر والظهر.",
        ],
        "how": [
            "وزن متوسط/خفيف وتحكم أعلى.",
            "ارفع لمستوى الكتف فقط (في الرفرفة).",
            "حافظ على الكوع ثابت بثني بسيط.",
        ],
        "mistakes": [
            "استخدام وزن تقيل مع هز الجسم.",
            "رفع الكتف لفوق بدل تشغيل الدلت.",
            "مدى حركة أكبر من اللازم يوجع مفصل الكتف.",
        ],
        "cues": ["وزن خفيف", "تحكم", "كتف لتحت", "ارفع للجانب"],
        "sets_reps": "3–5 مجموعات × 12–20 تكرار (للعزل)",
    },
    "biceps": {
        "targets": ["البايسبس", "البراكيالس", "الساعد (خاصة الهامر)"],
        "why": [
            "يزود حجم الذراع ويقوي السحب.",
            "يحسن شكل الذراع مع التراي.",
            "يساعد في تمارين الظهر (سحب/رو).",
        ],
        "how": [
            "الكوع جنب الجسم ثابت.",
            "اطلع بتحكم وانزل ببطء 2–3 ثواني.",
            "متكسرش المعصم وخليه مستقيم.",
        ],
        "mistakes": [
            "الغش بالظهر والتأرجح.",
            "تحريك الكوع للأمام أثناء الرفع.",
            "تقصير المدى وعدم النزول الكامل.",
        ],
        "cues": ["كوع ثابت", "نزول بطيء", "معصم مستقيم"],
        "sets_reps": "3–4 مجموعات × 10–15 تكرار",
    },
    "triceps": {
        "targets": ["الترايسبس (خصوصًا Long head في فوق الرأس)"],
        "why": [
            "التراي هو أكبر جزء من الذراع (حجم).",
            "يزود قوة الدفع (بنش/شولدر برس).",
            "يحسن شكل الذراع من الخلف.",
        ],
        "how": [
            "الكوع ثابت جنب الجسم في pushdown.",
            "في فوق الرأس: خلي الكوعين قريبين.",
            "مدى مريح + تحكم في الرجوع.",
        ],
        "mistakes": [
            "فتح الكوعين للبره (يقلل العزل).",
            "استخدام وزن تقيل مع كتف بيتحرك.",
            "نص تكرار بدون تمديد كامل.",
        ],
        "cues": ["كوع ثابت", "فرد كامل", "تحكم في الرجوع"],
        "sets_reps": "3–4 مجموعات × 10–15 تكرار",
    },
}

# ---------------------------------
# Helpers
# ---------------------------------
def safe_read_json(p: Path) -> dict:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}

def list_images(folder: Path):
    if not folder.exists():
        return []
    imgs = [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in IMG_EXTS]
    return sorted(imgs, key=lambda x: x.name.lower())

def list_exercise_dirs(section_folder: Path):
    if not section_folder.exists():
        return []
    dirs = [d for d in section_folder.iterdir() if d.is_dir()]
    return sorted(dirs, key=lambda x: x.name.lower())

def section_key_from_path(folder: str) -> str:
    # folder like "images/bench" -> "bench"
    return Path(folder).name.lower()

def merge_info_with_defaults(section_key: str, info: dict) -> dict:
    d = DEFAULTS.get(section_key, {})
    merged = {
        "targets": info.get("targets", d.get("targets", [])),
        "why": info.get("why", d.get("why", [])),
        "how": info.get("how", d.get("how", [])),
        "mistakes": info.get("mistakes", d.get("mistakes", [])),
        "cues": info.get("cues", d.get("cues", [])),
        "sets_reps": info.get("sets_reps", d.get("sets_reps")),
        "note": info.get("note"),
        "display_name": info.get("display_name"),
    }
    return merged

def zip_project_images() -> bytes:
    images_dir = BASE_DIR / "images"
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, "w", zipfile.ZIP_DEFLATED) as z:
        if images_dir.exists():
            for f in images_dir.rglob("*"):
                if f.is_file():
                    z.write(f, f.relative_to(BASE_DIR).as_posix())

        readme = (
            "Coach Saeed Mahmoud Program\n"
            "Files:\n"
            "- streamlit_slides.py\n"
            "- images/\n\n"
            "To add custom explanation per exercise:\n"
            "Place info.json inside each exercise folder.\n"
            "Example keys: display_name, targets, why, how, mistakes, cues, sets_reps, note\n"
        )
        z.writestr("README_PROGRAM.txt", readme)
    return bio.getvalue()

def render_list(title: str, items):
    if not items:
        return
    st.markdown(f"**{title}:**")
    for x in items:
        st.write(f"- {x}")

def exercise_card_from_folder(section_key: str, ex_dir: Path):
    """
    images/bench/dumbbell_bench_press/
        info.json (optional)
        any images with any names...
    """
    info_path = ex_dir / "info.json"
    info = safe_read_json(info_path) if info_path.exists() else {}
    info = merge_info_with_defaults(section_key, info)

    display_name = info.get("display_name") or ex_dir.name.replace("_", " ").replace("-", " ").title()
    targets = info.get("targets", [])
    sets_reps = info.get("sets_reps")
    note = info.get("note")

    imgs = list_images(ex_dir)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"### {display_name}")

    # badges
    if targets:
        st.markdown(f"<span class='badge'>🎯 العضلات المستهدفة</span>", unsafe_allow_html=True)
    if sets_reps:
        st.markdown(f"<span class='badge2'>📌 {sets_reps}</span>", unsafe_allow_html=True)

    st.markdown("<hr/>", unsafe_allow_html=True)

    # images (any names)
    if imgs:
        # عرض الصور في صفوف (اختياري)
        for im in imgs:
            st.image(str(im), use_container_width=True, caption=im.stem.replace("_", " ").replace("-", " "))
    else:
        st.warning(f"⚠️ مفيش صور داخل: {ex_dir.as_posix()}")

    st.markdown("<hr/>", unsafe_allow_html=True)

    # detailed text
    render_list("🎯 بيستهدف", targets)
    render_list("✅ ليه التمرين مهم", info.get("why", []))
    render_list("🧠 طريقة الأداء الصحيحة", info.get("how", []))

    with st.expander("⚠️ أخطاء شائعة لازم تتجنبها"):
        mistakes = info.get("mistakes", [])
        if mistakes:
            for m in mistakes:
                st.write(f"- {m}")
        else:
            st.write("- حافظ على تكنيك ثابت وتحكم في الحركة.")

    cues = info.get("cues", [])
    if cues:
        st.markdown("**🎯 Cue سريع (ركز على):**")
        st.write(" • ".join(cues))

    if note:
        st.info(f"ملاحظة: {note}")

    st.markdown("</div>", unsafe_allow_html=True)

def section_page(title: str, folder: str):
    section_dir = BASE_DIR / folder
    s_key = section_key_from_path(folder)

    st.markdown(
        f"""
        <div class="hero">
          <div style="display:flex; gap:14px; align-items:center; flex-wrap:wrap;">
            <div style="font-size:34px;">🔥</div>
            <div>
              <h2 style="margin:0;">{title}</h2>
              <div class="mini">صور بأي أسماء + شرح تفصيلي + أخطاء شائعة (تلقائي) + ويمكن تخصيصه من info.json</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    ex_dirs = list_exercise_dirs(section_dir)

    # subfolder per exercise (recommended)
    if ex_dirs:
        for ex_dir in ex_dirs:
            exercise_card_from_folder(s_key, ex_dir)
        return

    # fallback: images directly inside section folder (no subfolders)
    imgs = list_images(section_dir)
    if not imgs:
        st.warning(f"⚠️ مفيش صور في: {folder}")
        st.info("💡 الأفضل تعمل فولدر لكل تمرين داخل القسم (زي الصور اللي انت عاملها).")
        return

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### صور القسم (بدون تقسيم تمارين)")
    for im in imgs:
        st.image(str(im), use_container_width=True, caption=im.stem.replace("_", " ").replace("-", " "))
        st.markdown("**شرح عام:**")
        st.write("- نفّذ التمرين بتحكم كامل.")
        st.write("- ركّز على العضلة المستهدفة.")
        st.write("- تحكّم في النزول وازفر أثناء الرفع.")
        st.divider()
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------
# Pages
# ---------------------------------
def page_home():
    st.markdown("<div class='hero'>", unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1.7], vertical_alignment="center")
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

        st.markdown(
            f"""
            <a class="social-btn" href="{COACH['facebook']}" target="_blank">📘 Facebook</a>
            <a class="social-btn" href="{COACH['instagram']}" target="_blank">📸 Instagram</a>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<hr/>", unsafe_allow_html=True)
        st.write("✅ تمارين مصنفة حسب العضلة")
        st.write("✅ تحت كل تمرين: صور + شرح (بيستهدف/ليه/طريقة/أخطاء)")
        st.write("✅ زر تحميل البرنامج كامل (صور + تنظيم الفولدرات)")
        st.write("✅ الثيم: Black × Yellow (Fitness)")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="footer">
          <div class="mini">© برنامج كابتن سعيد محمود — نسخة خاصة</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def page_nutrition():
    st.markdown("<div class='hero'>", unsafe_allow_html=True)
    st.markdown("## النظام الغذائي 🍽️")
    st.markdown("<div class='mini'>ممكن تكتب هنا: تنشيف / تثبيت / تضخيم + بدائل للوجبات</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### مثال يوم متوازن")
    st.write("**الإفطار:** بيض + شوفان + فاكهة")
    st.write("**الغداء:** صدر دجاج/لحم + رز/بطاطس + سلطة")
    st.write("**العشاء:** زبادي/تونة + خضار")
    st.write("**سناك:** فاكهة / مكسرات")

    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown("### قواعد ذهبية")
    st.write("- اشرب 2–3 لتر مياه يوميًا")
    st.write("- بروتين عالي (حسب وزنك)")
    st.write("- نوم 7–8 ساعات")
    st.write("- قلل السكر والمقليات")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------
# Sidebar
# ---------------------------------
st.sidebar.markdown("## 🏋️ برنامج الكابتن")
st.sidebar.markdown(f"**{COACH['name']}**")
st.sidebar.caption("القائمة + التحميل + السوشيال")

page = st.sidebar.radio(
    "اختر القسم",
    ["الرئيسية", "النظام الغذائي"] + [x[0] for x in SECTIONS],
    index=0
)

st.sidebar.markdown("---")

# Download button (ZIP)
zip_bytes = zip_project_images()
st.sidebar.download_button(
    label="⬇️ تحميل البرنامج كامل (ZIP)",
    data=zip_bytes,
    file_name=f"Coach_Saeed_Program_{datetime.now().strftime('%Y-%m-%d')}.zip",
    mime="application/zip"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📲 تواصل مع الكابتن")
st.sidebar.markdown(
    f"""
    <a class="social-btn" href="{COACH['facebook']}" target="_blank">Facebook</a><br><br>
    <a class="social-btn" href="{COACH['instagram']}" target="_blank">Instagram</a>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("<div class='mini'>تشغيل: <code>streamlit run streamlit_slides.py</code></div>", unsafe_allow_html=True)

# ---------------------------------
# Router
# ---------------------------------
if page == "الرئيسية":
    page_home()
elif page == "النظام الغذائي":
    page_nutrition()
else:
    for title, folder in SECTIONS:
        if page == title:
            section_page(title, folder)
            break
