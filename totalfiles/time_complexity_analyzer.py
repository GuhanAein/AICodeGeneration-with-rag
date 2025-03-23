import streamlit as st
import ast
import re

def analyze_time_complexity(code):
    try:
        tree = ast.parse(code)
        class ComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.loop_depth = 0
                self.max_loop_depth = 0
                self.logarithmic = False
                self.function_defs = {}
                self.function_calls = []
                self.current_function = None
                self.memoized = set()
                self.has_recursion = False
                
            def visit_For(self, node):
                if self._is_logarithmic_loop(node):
                    self.logarithmic = True
                else:
                    self.loop_depth += 1
                    self.max_loop_depth = max(self.max_loop_depth, self.loop_depth)
                self.generic_visit(node)
                if not self.logarithmic:
                    self.loop_depth -= 1
                
            def visit_While(self, node):
                if self._is_logarithmic_while(node):
                    self.logarithmic = True
                else:
                    self.loop_depth += 1
                    self.max_loop_depth = max(self.max_loop_depth, self.loop_depth)
                self.generic_visit(node)
                if not self.logarithmic:
                    self.loop_depth -= 1
                
            def visit_FunctionDef(self, node):
                self.current_function = node.name
                self.function_defs[node.name] = node
                if self._has_memoization(node):
                    self.memoized.add(node.name)
                self.generic_visit(node)
                self.current_function = None
                
            def visit_Call(self, node):
                if isinstance(node.func, ast.Name):
                    call_name = node.func.id
                    self.function_calls.append((call_name, self.current_function))
                    if call_name == self.current_function:
                        self.has_recursion = True
                self.generic_visit(node)
                
            def _is_logarithmic_loop(self, node):
                if isinstance(node.iter, ast.Call) and getattr(node.iter.func, 'id', '') == "range":
                    args = node.iter.args
                    if len(args) == 3 and isinstance(args[2], ast.Num) and args[2].n > 1:
                        return True
                return False
                
            def _is_logarithmic_while(self, node):
                for child in ast.walk(node):
                    if (isinstance(child, ast.Assign) and 
                        isinstance(child.value, ast.BinOp) and 
                        isinstance(child.value.op, (ast.FloorDiv, ast.Div))):
                        return True
                return False
                
            def _has_memoization(self, node):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.id == "lru_cache":
                        return True
                return any(isinstance(body_node, ast.Assign) and isinstance(body_node.value, ast.Dict) for body_node in node.body)
        
        visitor = ComplexityVisitor()
        visitor.visit(tree)
        
        if visitor.has_recursion:
            if visitor.current_function in visitor.memoized:
                complexity, note = "O(n)", "Memoized recursion detected."
            else:
                complexity, note = "O(2^n) or O(n)", "Recursion detected."
        elif visitor.logarithmic:
            complexity, note = "O(log n)", "Logarithmic pattern detected."
        elif visitor.max_loop_depth == 0:
            complexity, note = "O(1)", "No significant loops."
        elif visitor.max_loop_depth == 1:
            complexity, note = "O(n)", "Single loop detected."
        elif visitor.max_loop_depth == 2:
            complexity, note = "O(n^2)", "Nested loops (2 levels)."
        else:
            complexity, note = f"O(n^{visitor.max_loop_depth})", f"Nested loops ({visitor.max_loop_depth} levels)."
        
        return f"**Estimated Time Complexity:** {complexity}  \n**Note:** {note}"
    except SyntaxError:
        return "Error: Invalid Python code syntax."
    except Exception as e:
        return f"Error analyzing code: {str(e)}"

def run():
    st.subheader("Time Complexity Analyzer")
    code_input = st.text_area("Your Python Code", height=200, placeholder="e.g., def example(n):\n    for i in range(n):\n        print(i)")
    if st.button("Analyze"):
        if code_input.strip():
            result = analyze_time_complexity(code_input)
            st.markdown("### Analysis Result")
            st.markdown(result)
        else:
            st.warning("Please enter some code.")