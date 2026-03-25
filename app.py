import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# -------------- Google Sheets Setup -------------- #

SHEET_URL = "https://docs.google.com/spreadsheets/d/1n146nX5EWZD7EHscSBvODaD6bYIsNBB2pTGhcFXTltU/edit?usp=sharing"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def connect_sheet():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_url(SHEET_URL).sheet1
    return sheet

sheet = connect_sheet()

HEADERS = ["First Name", "Last Name", "Birth Place", "Gender", "Phone", "Emergency Contact", "Emergency Phone"]

# เช็คว่ามี Header แล้วหรือยัง
if sheet.row_count < 1 or sheet.row_values(1) != HEADERS:
    sheet.insert_row(HEADERS, 1)

# ----------- Functions ----------- #
def load_students():
    values = sheet.get_all_values()
    return values[1:] if len(values) > 1 else []

def add_student(data):
    sheet.append_row(data)

def update_student(index, data):
    row = index + 2
    sheet.update(f"A{row}:G{row}", [data])

def delete_student(index):
    row = index + 2
    sheet.delete_rows(row)

# -------------- Streamlit UI -------------- #

st.title("📘 ระบบจัดการข้อมูลนักเรียน (Streamlit + Google Sheets)")
menu = st.sidebar.radio("เมนูหลัก", ["เพิ่มนักเรียน", "ค้นหา/แก้ไข/ลบ", "รายชื่อทั้งหมด"])

# ----------- หน้าเพิ่มนักเรียน ----------- #
if menu == "เพิ่มนักเรียน":
    st.header("➕ เพิ่มข้อมูลนักเรียน")

    with st.form("add_form"):
        first = st.text_input("ชื่อ")
        last = st.text_input("นามสกุล")
        birth = st.text_input("สถานที่เกิด")
        gender = st.selectbox("เพศ", ["ชาย", "หญิง", "อื่น ๆ"])
        phone = st.text_input("เบอร์โทรศัพท์")
        emer = st.text_input("ผู้ติดต่อฉุกเฉิน")
        emer_phone = st.text_input("เบอร์โทรฉุกเฉิน")

        submitted = st.form_submit_button("บันทึกข้อมูล")

        if submitted:
            add_student([first, last, birth, gender, phone, emer, emer_phone])
            st.success("บันทึกข้อมูลเรียบร้อย!")

# ----------- หน้า ค้นหา / แก้ไข / ลบ ----------- #
elif menu == "ค้นหา/แก้ไข/ลบ":
    st.header("🔍 ค้นหานักเรียน")

    students = load_students()

    query = st.text_input("พิมพ์คำค้นหา (ชื่อ / นามสกุล / เพศ)")
    results = []

    if query:
        for i, s in enumerate(students):
            if query.lower() in " ".join(s).lower():
                results.append((i, s))

    for idx, (index, s) in enumerate(results):
        st.write(f"### [{idx}] {s[0]} {s[1]}")
        st.write(f"- สถานที่เกิด: {s[2]}")
        st.write(f"- เพศ: {s[3]}")
        st.write(f"- โทร: {s[4]}")
        st.write(f"- ผู้ติดต่อฉุกเฉิน: {s[5]} ({s[6]})")

        col1, col2 = st.columns(2)

        if col1.button("แก้ไขข้อมูล", key=f"edit_{index}"):
            st.session_state["edit_index"] = index

        if col2.button("ลบข้อมูล", key=f"delete_{index}"):
            delete_student(index)
            st.success("ลบข้อมูลเรียบร้อย!")
            st.experimental_rerun()

    # แก้ไขข้อมูล
    if "edit_index" in st.session_state:
        st.subheader("✏️ แก้ไขข้อมูล")
        idx = st.session_state["edit_index"]
        data = students[idx]

        with st.form("edit_form"):
            first = st.text_input("ชื่อ", data[0])
            last = st.text_input("นามสกุล", data[1])
            birth = st.text_input("สถานที่เกิด", data[2])
            gender = st.text_input("เพศ", data[3])
            phone = st.text_input("โทรศัพท์", data[4])
            emer = st.text_input("ผู้ติดต่อฉุกเฉิน", data[5])
            emer_phone = st.text_input("เบอร์ฉุกเฉิน", data[6])

            save = st.form_submit_button("บันทึกการแก้ไข")

            if save:
                update_student(idx, [first, last, birth, gender, phone, emer, emer_phone])
                st.success("อัปเดตข้อมูลสำเร็จ!")
                st.session_state.pop("edit_index")
                st.experimental_rerun()

# ----------- หน้าแสดงรายชื่อทั้งหมด ----------- #
elif menu == "รายชื่อทั้งหมด":
    st.header("📋 รายชื่อนักเรียนทั้งหมด")

    students = load_students()
    st.write(f"พบทั้งหมด {len(students)} คน")

    st.table(students)
