from flask import Flask, request, jsonify
import re
from typing import List, Union

class ExpressionElement:
    def __init__(self, value: str, element_type: str):
        self.value = value
        self.type = element_type

class ExpressionSplitter:
    def __init__(self, expression: str):
        self.expression = expression.replace(" ", "")

    def split_into_elements(self) -> List[ExpressionElement]:
        elements = []
        element_pattern = re.compile(r'\d+(\.\d+)?|[+\-*/()]')
        previous_element = None

        for match in element_pattern.finditer(self.expression):
            element_value = match.group(0)
            if element_value.isdigit() or re.match(r'\d+\.\d+', element_value):
                element_type = 'NUMBER'
            elif element_value == '-' and (previous_element is None or previous_element.type != 'NUMBER' and previous_element.value != ')'):
                element_type = 'NEGATIVE_SIGN'
            else:
                element_type = 'OPERATOR'

            element = ExpressionElement(element_value, element_type)
            elements.append(element)
            previous_element = element

        return elements

class PostfixConverter:
    def __init__(self, elements: List[ExpressionElement]):
        self.elements = elements
        self.postfix_queue = []
        self.operator_stack = []
        self.operation_priority = {'+': 1, '-': 1, '*': 2, '/': 2, 'NEGATIVE_SIGN': 3}
        self.is_right_associative = {'^': True, 'NEGATIVE_SIGN': True}

    def to_postfix(self) -> List[ExpressionElement]:
        for element in self.elements:
            if element.type == 'NUMBER':
                self.postfix_queue.append(element)
            elif element.type in ['OPERATOR', 'NEGATIVE_SIGN']:
                if element.value == '(':
                    self.operator_stack.append(element)
                elif element.value == ')':
                    while self.operator_stack and self.operator_stack[-1].value != '(':
                        self.postfix_queue.append(self.operator_stack.pop())
                    self.operator_stack.pop()  # Remove ( from stack
                else:
                    while (self.operator_stack and
                           self.operator_stack[-1].value in self.operation_priority and
                           ((self.operation_priority[element.value] < self.operation_priority[self.operator_stack[-1].value]) or
                           (self.operation_priority[element.value] == self.operation_priority[self.operator_stack[-1].value] and
                            element.value not in self.is_right_associative))):
                        self.postfix_queue.append(self.operator_stack.pop())
                    self.operator_stack.append(element)

        while self.operator_stack:
            self.postfix_queue.append(self.operator_stack.pop())

        return self.postfix_queue

class PostfixEvaluator:
    def __init__(self, postfix_expression: List[ExpressionElement]):
        self.postfix_expression = postfix_expression

    def evaluate(self) -> Union[float, str]:
        calculation_stack = []
        for element in self.postfix_expression:
            if element.type == 'NUMBER':
                calculation_stack.append(float(element.value))
            elif element.type == 'OPERATOR':
                if len(calculation_stack) < 2:
                    return "Error: Insufficient values in expression"
                second_operand, first_operand = calculation_stack.pop(), calculation_stack.pop()
                if element.value == '+':
                    calculation_stack.append(first_operand + second_operand)
                elif element.value == '-':
                    calculation_stack.append(first_operand - second_operand)
                elif element.value == '*':
                    calculation_stack.append(first_operand * second_operand)
                elif element.value == '/':
                    if second_operand == 0:
                        return "Error: Division by zero"
                    calculation_stack.append(first_operand / second_operand)
            elif element.type == 'NEGATIVE_SIGN':
                if len(calculation_stack) < 1:
                    return "Error: Insufficient values for unary operation"
                operand = calculation_stack.pop()
                calculation_stack.append(-operand)

        return calculation_stack[0] if calculation_stack else "Error: Invalid expression"
        
        
app = Flask(__name__)

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    expression = data.get("expression")
    if not expression:
        return jsonify({"error": "No expression provided"}), 400

    try:
        splitter = ExpressionSplitter(expression)
        elements = splitter.split_into_elements()
        converter = PostfixConverter(elements)
        postfix_expression = converter.to_postfix()
        evaluator = PostfixEvaluator(postfix_expression)
        result = evaluator.evaluate()
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)