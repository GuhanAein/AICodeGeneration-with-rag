import streamlit as st
import time_complexity_analyzer
import stack_overflow_debugger
import stack_overflow_gemini
import code_debugger_optimizer
import competitive_solver

def main():
    st.title("Developer Tools Suite")
    tool = st.sidebar.selectbox("Select Tool", [
        "Time Complexity Analyzer",
        "Stack Overflow Error Debugger",
        "Stack Overflow with Gemini AI",
        "AI Code Debugger & Optimizer",
        "Competitive Programming Solver"
    ])

    if tool == "Time Complexity Analyzer":
        time_complexity_analyzer.run()
    elif tool == "Stack Overflow Error Debugger":
        stack_overflow_debugger.run()
    elif tool == "Stack Overflow with Gemini AI":
        stack_overflow_gemini.run()
    elif tool == "AI Code Debugger & Optimizer":
        code_debugger_optimizer.run()
    elif tool == "Competitive Programming Solver":
        competitive_solver.run()

if __name__ == "__main__":
    main()

TypeError: Cannot read properties of undefined (reading 'length')