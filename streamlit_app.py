import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

import streamlit as st

DB_PATH = Path(__file__).with_name("estate_command_center.db")


def ensure_database_schema(db_path: str | Path | None = None) -> Path:
    db_file = Path(db_path or DB_PATH)
    conn = sqlite3.connect(db_file)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS properties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_name TEXT NOT NULL,
                owner_name TEXT,
                deed_data TEXT,
                deed_fingerprint TEXT
            )
            """
        )
        cols = {row[1] for row in conn.execute("PRAGMA table_info(properties)")}
        if "deed_fingerprint" not in cols:
            conn.execute("ALTER TABLE properties ADD COLUMN deed_fingerprint TEXT")
        conn.commit()
    finally:
        conn.close()
    return db_file


def add_property(db_path: str | Path | None = None, property_name: str = "", owner_name: str = "", deed_data: str = "", deed_fingerprint: str | None = None) -> None:
    db_file = ensure_database_schema(db_path)
    conn = sqlite3.connect(db_file)
    try:
        fingerprint = deed_fingerprint or hashlib.sha256((property_name + owner_name + deed_data).encode("utf-8")).hexdigest()
        conn.execute(
            "INSERT INTO properties (property_name, owner_name, deed_data, deed_fingerprint) VALUES (?, ?, ?, ?)",
            (property_name, owner_name, deed_data, fingerprint),
        )
        conn.commit()
    finally:
        conn.close()


def get_properties(db_path: str | Path | None = None) -> list[dict[str, Any]]:
    db_file = ensure_database_schema(db_path)
    conn = sqlite3.connect(db_file)
    try:
        rows = conn.execute(
            "SELECT id, property_name, owner_name, deed_data, deed_fingerprint FROM properties ORDER BY property_name"
        ).fetchall()
    finally:
        conn.close()
    return [
        {
            "id": row[0],
            "property_name": row[1],
            "owner_name": row[2],
            "deed_data": row[3],
            "deed_fingerprint": row[4],
        }
        for row in rows
    ]


def build_pdf_payload(properties: list[dict[str, Any]], display_name: str) -> str:
    return json.dumps(
        {
            "title": "Deed Packet",
            "display_name": display_name,
            "properties": properties,
        },
        indent=2,
    )


def build_share_text(properties: list[dict[str, Any]], display_name: str) -> str:
    lines = [
        "Digital Receipt Deed",
        f"Prepared by: {display_name or 'Not provided'}",
        "",
        "Property summary:",
    ]
    for item in properties:
        lines.append(f"- {item.get('property_name', 'Unnamed')} | Owner: {item.get('owner_name', 'Unknown')} | Fingerprint: {item.get('deed_fingerprint', 'N/A')}")
    return "\n".join(lines)


def build_registry_payload(properties: list[dict[str, Any]], display_name: str) -> dict[str, Any]:
    return {
        "documentType": "digital_receipt_deed",
        "preparedBy": display_name or "Not provided",
        "properties": [
            {
                "propertyName": item.get("property_name", "Unnamed"),
                "ownerName": item.get("owner_name", "Unknown"),
                "deedFingerprint": item.get("deed_fingerprint", "N/A"),
                "deedDetails": item.get("deed_data", ""),
            }
            for item in properties
        ],
    }


def build_ledger_csv(properties: list[dict[str, Any]], display_name: str) -> str:
    header = "prepared_by,property_name,owner_name,deed_fingerprint,deed_details"
    rows = [header]
    for item in properties:
        rows.append(
            ",".join(
                [
                    str(display_name or "Not provided"),
                    str(item.get("property_name", "Unnamed")),
                    str(item.get("owner_name", "Unknown")),
                    str(item.get("deed_fingerprint", "N/A")),
                    str(item.get("deed_data", "")),
                ]
            )
        )
    return "\n".join(rows)


def build_business_delivery_ledger(properties: list[dict[str, Any]], display_name: str) -> list[dict[str, Any]]:
    return [
        {
            "businessName": display_name or "Not provided",
            "deliveryType": "Digital Receipt Deed",
            "propertyName": item.get("property_name", "Unnamed"),
            "ownerName": item.get("owner_name", "Unknown"),
            "fingerprint": item.get("deed_fingerprint", "N/A"),
            "status": "Delivered to city ledger",
        }
        for item in properties
    ]


def build_faire_delivery_record() -> dict[str, Any]:
    return {
        "source": "Faire",
        "businessName": "Susanna Marie's Creations",
        "contactName": "Susanna Marie Cole",
        "address": "11051B County Road C, Bryan, Ohio",
        "status": "Ordered and coming",
        "deliveryNote": "Faire order for city ledger / business delivery record",
    }


def build_walmart_delivery_record() -> dict[str, Any]:
    return {
        "source": "Walmart",
        "businessName": "Susanna Marie's Creations",
        "contactName": "Susanna Marie Cole",
        "address": "11051B County Road C, Bryan, Ohio",
        "status": "Ordered and coming",
        "deliveryNote": "Walmart order for city ledger / business delivery record",
    }


def build_pdf_bytes(properties: list[dict[str, Any]], display_name: str) -> bytes:
    def escape_text(value: str) -> str:
        return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    lines = [
        "DIGITAL RECEIPT DEED",
        f"Fingerprint identifier: {display_name or 'Not provided'}",
        "",
        "Property Summary",
    ]
    for item in properties:
        lines.extend(
            [
                f"- Property: {item.get('property_name', 'Unnamed')}",
                f"  Owner: {item.get('owner_name', 'Unknown')}",
                f"  Fingerprint: {item.get('deed_fingerprint', 'N/A')}",
            ]
        )
        if item.get("deed_data"):
            lines.append(f"  Deed Details: {item['deed_data']}")
        lines.append("")

    content = "\n".join(lines)
    body = "\n".join(f"({escape_text(line)})" for line in content.splitlines())
    pdf_lines = [
        "%PDF-1.4",
        "1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj",
        "2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj",
        "3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>endobj",
        "4 0 obj<< /Length 0 >>stream",
        "BT /F1 12 Tf 50 750 Td",
        f"({escape_text('DIGITAL RECEIPT DEED')}) Tj",
        "0 -18 Td",
        f"({escape_text('Fingerprint identifier: ' + (display_name or 'Not provided'))}) Tj",
        "0 -18 Td",
        f"({escape_text('Property Summary')}) Tj",
    ]
    for line in content.splitlines()[3:]:
        pdf_lines.append("0 -14 Td")
        pdf_lines.append(f"({escape_text(line)}) Tj")
    pdf_lines.extend([
        "ET",
        "endstream",
        "endobj",
        "5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj",
        "xref",
        "0 6",
        "0000000000 65535 f ",
        "0000000010 00000 n ",
        "0000000062 00000 n ",
        "0000000119 00000 n ",
        "0000000203 00000 n ",
        "0000000300 00000 n ",
        "trailer<< /Size 6 /Root 1 0 R >>",
        "startxref",
        "0",
        "%%EOF",
    ])
    return "\n".join(pdf_lines).encode("latin-1", errors="ignore")


st.set_page_config(page_title="Estate Command Center", page_icon="🏠")
st.title("🏠 Estate Command Center")
st.caption("Manage deed data for properties with a fingerprint.")

ensure_database_schema()

with st.sidebar:
    st.header("Add deed")
    property_name = st.text_input("Property name")
    owner_name = st.text_input("Owner name")
    deed_data = st.text_area("Deed details")
    fingerprint = st.text_input("Fingerprint (optional)")
    display_name = st.text_input("Name to show on the packet")
    if st.button("Save property"):
        if not property_name:
            st.warning("Please enter a property name.")
        else:
            add_property(DB_PATH, property_name, owner_name, deed_data, fingerprint or None)
            st.success("Property saved.")

st.subheader("Properties with deed fingerprints")
properties = get_properties(DB_PATH)
filtered = [item for item in properties if item.get("deed_fingerprint")]

if not filtered:
    st.info("No deed fingerprints have been recorded yet.")
else:
    st.dataframe(filtered, use_container_width=True)
    st.download_button(
        label="Download deed packet PDF",
        data=build_pdf_bytes(filtered, display_name),
        file_name="deed_packet.pdf",
        mime="application/pdf",
    )

    share_text = build_share_text(filtered, display_name)
    st.text_area("Shareable notice", share_text, height=220)
    st.download_button(
        label="Download registry payload JSON",
        data=json.dumps(build_registry_payload(filtered, display_name), indent=2),
        file_name="registry_payload.json",
        mime="application/json",
    )
    st.download_button(
        label="Download municipal ledger CSV",
        data=build_ledger_csv(filtered, display_name),
        file_name="municipal_ledger.csv",
        mime="text/csv",
    )
    st.download_button(
        label="Download business delivery ledger JSON",
        data=json.dumps(build_business_delivery_ledger(filtered, display_name), indent=2),
        file_name="business_delivery_ledger.json",
        mime="application/json",
    )
    st.link_button(
        "Send notice by email",
        f"mailto:municipal@city.gov?subject=Digital%20Receipt%20Deed%20Notice&body={share_text}",
    )
