import streamlit as st
import ast
import re

def analyze_time_complexity(code):
    try:
        # Parse the code into an AST
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
                if isinstance(node.iter, ast.Call) and node.iter.func.id == "range":
                    args = node.iter.args
                    if len(args) == 3:
                        step = args[2]
                        if isinstance(step, ast.Num) and step.n > 1:
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
                for body_node in node.body:
                    if (isinstance(body_node, ast.Assign) and 
                        isinstance(body_node.value, ast.Dict)):
                        return True
                return False
        
        # Analyze the AST
        visitor = ComplexityVisitor()
        visitor.visit(tree)
        
        # Estimate time complexity
        if visitor.has_recursion:
            if visitor.current_function in visitor.memoized:
                complexity = "O(n)"
                note = "Memoized recursion detected (e.g., dynamic programming)."
            else:
                complexity = "O(2^n) or O(n) depending on recursion depth"
                note = "Recursion detected. Complexity varies with call pattern."
        elif visitor.logarithmic:
            complexity = "O(log n)"
            note = "Logarithmic pattern detected (e.g., division by 2 or step > 1)."
        elif visitor.max_loop_depth == 0:
            complexity = "O(1)"
            note = "No significant loops or recursion detected."
        elif visitor.max_loop_depth == 1:
            complexity = "O(n)"
            note = "Single loop detected."
        elif visitor.max_loop_depth == 2:
            complexity = "O(n^2)"
            note = "Nested loops (2 levels) detected."
        else:
            complexity = f"O(n^{visitor.max_loop_depth})"
            note = f"Nested loops ({visitor.max_loop_depth} levels) detected."
        
        return f"**Estimated Time Complexity:** {complexity}  \n**Note:** {note}"
    
    except SyntaxError:
        return "Error: Invalid Python code syntax."
    except Exception as e:
        return f"Error analyzing code: {str(e)}"

# Streamlit UI
def main():
    st.title("Time Complexity Analyzer")
    st.write("Enter your Python code below to analyze its time complexity.")
    
    # Text area for code input
    code_input = st.text_area("Your Python Code", height=200, placeholder="e.g., def example(n):\n    for i in range(n):\n        print(i)")
    
    # Button to analyze
    if st.button("Analyze"):
        if code_input.strip():
            result = analyze_time_complexity(code_input)
            st.markdown("### Analysis Result")
            st.markdown(result)
        else:
            st.warning("Please enter some code to analyze.")

if __name__ == "__main__":
    main()