import streamlit as st
import json
import difflib

from optimizer import optimize_prompt, evaluate_prompt, iterative_optimize
from explanation import generate_explanation

st.set_page_config(page_title="Prompt Optimizer", layout="wide")

st.title("🧠 Prompt Optimizer")
st.caption("Improve your prompts with structured optimization using local LLM")

# -----------------------------
# 🧠 SESSION STATE
# -----------------------------
if "optimized" not in st.session_state:
    st.session_state.optimized = None

if "original" not in st.session_state:
    st.session_state.original = None

# -----------------------------
# INPUT
# -----------------------------
user_input = st.text_area("✍️ Enter your prompt:", height=150)

col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    optimize_btn = st.button("⚡ Optimize")

with col_btn2:
    deep_optimize_btn = st.button("🔥 Deep Optimize")

# OPTIONS
show_explanation = st.toggle("🧠 Show Explanation Mode")

# -----------------------------
# 🔍 DIFF VIEW
# -----------------------------
def show_diff(original, optimized):
    original_words = original.split()
    optimized_words = optimized.split()

    diff = difflib.ndiff(original_words, optimized_words)

    removed, added = [], []

    for token in diff:
        if token.startswith("- "):
            removed.append(token[2:])
        elif token.startswith("+ "):
            added.append(token[2:])

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔴 Removed / Changed")
        st.write(" ".join(removed) if removed else "No removals")

    with col2:
        st.markdown("### 🟢 Added / Improved")
        st.write(" ".join(added) if added else "No additions")


# -----------------------------
# 📊 DISPLAY RESULTS
# -----------------------------
def display_results(original, optimized):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔹 Original Prompt")
        st.text_area("", original, height=250)
        original_score = evaluate_prompt(original)
        st.markdown("**📊 Original Score**")
        st.code(original_score)

    with col2:
        st.subheader("✅ Optimized Prompt")
        st.text_area("", optimized, height=250)
        optimized_score = evaluate_prompt(optimized)
        st.markdown("**📊 Optimized Score**")
        st.code(optimized_score)

    # --- Improvement ---
    try:
        orig_val = int(original_score.split("/")[0].split(":")[1].strip())
        opt_val = int(optimized_score.split("/")[0].split(":")[1].strip())
        diff_score = opt_val - orig_val

        st.markdown("---")
        if diff_score > 0:
            st.success(f"🚀 Improvement: +{diff_score} points")
        elif diff_score == 0:
            st.info("⚖️ No improvement detected")
        else:
            st.warning(f"⚠️ Score decreased: {diff_score}")
    except:
        st.info("Could not calculate improvement")

    # --- Diff View ---
    st.markdown("---")
    st.subheader("🔍 Diff View")
    show_diff(original, optimized)

    # --- Explanation ---
    if show_explanation:
        st.markdown("---")
        with st.expander("🔍 Explanation Mode"):
            with st.spinner("Generating explanation..."):
                explanation = generate_explanation(original, optimized)
                st.markdown(explanation)

    # --- Actions ---
    st.markdown("---")
    st.markdown("### 📋 Actions")

    col_copy, col_download = st.columns(2)

    with col_copy:
        st.code(optimized)

    with col_download:
        export_data = {
            "original_prompt": original,
            "optimized_prompt": optimized,
            "original_score": original_score,
            "optimized_score": optimized_score
        }

        st.download_button(
            label="⬇️ Download",
            data=json.dumps(export_data, indent=2),
            file_name="prompt_result.json",
            mime="application/json"
        )


# -----------------------------
# ⚡ OPTIMIZE
# -----------------------------
if optimize_btn and user_input:
    with st.spinner("Optimizing..."):
        st.session_state.original = user_input
        st.session_state.optimized = optimize_prompt(user_input)

# -----------------------------
# 🔥 DEEP OPTIMIZE
# -----------------------------
if deep_optimize_btn and user_input:
    with st.spinner("Deep optimizing..."):
        st.session_state.original = user_input
        st.session_state.optimized = iterative_optimize(user_input, iterations=2)

# -----------------------------
# 📊 SHOW RESULTS IF AVAILABLE
# -----------------------------
if st.session_state.optimized:
    if "❌" in st.session_state.optimized:
        st.error("❌ Optimization failed.")
    else:
        display_results(
            st.session_state.original,
            st.session_state.optimized
        )

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.caption("⚡ Built with Streamlit + Ollama | Local LLM Prompt Engineering Tool")