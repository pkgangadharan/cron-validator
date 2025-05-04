
import streamlit as st
import re

st.set_page_config(page_title="Cron Expression Validator", layout="centered")

st.title("🕒 Cron Expression Validator")
st.markdown("""
Validate Unix (5-segment), Quartz 6-segment, and Quartz 7-segment cron expressions.

Examples:
- `0 12 * * 1-5` (Unix)
- `0 0/5 14 * * ?` (Quartz 6)
- `0 15 10 ? * MON#2 2025` (Quartz 7)
""")

def is_valid_cron_segment(field, segment_type):
    ranges = {
        "second": (0, 59),
        "minute": (0, 59),
        "hour": (0, 23),
        "day_of_month": (1, 31),
        "month": (1, 12),
        "day_of_week": (0, 7),
        "year": (1970, 2099),
    }

    if field in ["*", "?"]:
        return True

    for part in field.split(','):
        if segment_type in ["day_of_month", "day_of_week"]:
            if re.fullmatch(r"L", part): return True
            if re.fullmatch(r"\d+W", part): return True
            if part == "LW": return True
            if re.fullmatch(r"\d+#\d+", part): return True

        if "/" in part:
            base, step = part.split('/')
            if not step.isdigit(): return False
            part = base

        if "-" in part:
            start, end = part.split('-')
            if start.isdigit() and end.isdigit():
                if ranges[segment_type][0] <= int(start) <= int(end) <= ranges[segment_type][1]:
                    continue
                else:
                    return False
            else:
                return False

        if part.isdigit():
            val = int(part)
            if not (ranges[segment_type][0] <= val <= ranges[segment_type][1]):
                return False
        elif part not in ['L', 'W', '?']:
            return False

    return True

def validate_cron_expression(expr):
    parts = expr.strip().split()
    segment_count = len(parts)

    if segment_count == 5:
        cron_type = "Unix"
        segment_names = ["minute", "hour", "day_of_month", "month", "day_of_week"]
    elif segment_count == 6:
        cron_type = "Quartz (6-segment)"
        segment_names = ["second", "minute", "hour", "day_of_month", "month", "day_of_week"]
    elif segment_count == 7:
        cron_type = "Quartz (7-segment)"
        segment_names = ["second", "minute", "hour", "day_of_month", "month", "day_of_week", "year"]
    else:
        return False, f"❌ Invalid segment count: {segment_count}.", None

    for i, field in enumerate(parts):
        segment = segment_names[i]
        if not is_valid_cron_segment(field, segment):
            return False, f"❌ Invalid field `{field}` in segment `{segment}`.", cron_type

    return True, f"✅ Valid {cron_type} cron expression.", cron_type

cron_input = st.text_input("Enter cron expression", "")

if cron_input:
    valid, message, cron_type = validate_cron_expression(cron_input)
    if valid:
        st.success(message)
    else:
        st.error(message)
