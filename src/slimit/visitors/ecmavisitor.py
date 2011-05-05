###############################################################################
#
# Copyright (c) 2011 Ruslan Spivak
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

__author__ = 'Ruslan Spivak <ruslan.spivak@gmail.com>'

from slimit import ast


class ECMAVisitor(object):

    def __init__(self):
        self.indent_level = 0

    def _make_indent(self):
        return ' ' * self.indent_level

    def visit(self, node):
        method = 'visit_%s' % node.__class__.__name__
        return getattr(self, method, self.generic_visit)(node)

    def generic_visit(self, node):
        return 'GEN: %r' % node

    def visit_Program(self, node):
        return '\n'.join(self.visit(child) for child in node.children)

    def visit_Block(self, node):
        s = self._make_indent() + '{\n'
        self.indent_level += 2
        s += '\n'.join(
            self.visit(child) for child in node.children)
        self.indent_level -= 2
        s += self._make_indent() + '\n}'
        return s

    def visit_VarStatement(self, node):
        s = self._make_indent()
        s += 'var %s;' % ', '.join(
            self.visit(child) for child in node.children)
        return s

    def visit_VarDecl(self, node):
        output = []
        output.append(self.visit(node.identifier))
        if node.initializer is not None:
            output.append(' = %s' % self.visit(node.initializer))
        return ''.join(output)

    def visit_Identifier(self, node):
        return node.value

    def visit_Assign(self, node):
        s = self._make_indent()
        return s + '%s %s %s' % (
            self.visit(node.left), node.op, self.visit(node.right))

    def visit_Number(self, node):
        return node.value

    def visit_Comma(self, node):
        return '%s, %s' % (self.visit(node.left), self.visit(node.right))

    def visit_EmptyStatement(self, node):
        return self._make_indent() + node.value

    def visit_If(self, node):
        s = 'if ('
        if node.predicate is not None:
            s += self.visit(node.predicate)
        s += ') '
        s += self.visit(node.consequent)
        if node.alternative is not None:
            s += ' else '
            s += self.visit(node.alternative)
        return s

    def visit_Boolean(self, node):
        return node.value

    def visit_For(self, node):
        s = 'for ('
        s += self.visit(node.init)
        if isinstance(node.init, (ast.Assign, ast.Comma)):
            s += '; '
        else:
            s += ' '
        if node.cond is not None:
            s += self.visit(node.cond)
        s += '; '
        if node.count is not None:
            s += self.visit(node.count)
        s += ') ' + self.visit(node.statement)
        return s

    def visit_ForIn(self, node):
        if isinstance(node.item, ast.VarDecl):
            template = 'for (var %s in %s) '
        else:
            template = 'for (%s in %s) '
        s = template % (self.visit(node.item), self.visit(node.iterable))
        s += self.visit(node.statement)
        return s

    def visit_BinOp(self, node):
        return '%s %s %s' % (
            self.visit(node.left), node.op, self.visit(node.right))

    def visit_UnaryOp(self, node):
        s = self.visit(node.value)
        if node.postfix:
            s += node.op
        else:
            s = node.op + s
        return s

    def visit_ExprStatement(self, node):
        return '%s;' % self.visit(node.expr)

    def visit_DoWhile(self, node):
        s = 'do '
        s += self.visit(node.statement)
        s += ' while (%s);' % self.visit(node.predicate)
        return s

    def visit_While(self, node):
        s = 'while (%s) ' % self.visit(node.predicate)
        s += self.visit(node.statement)
        return s

    def visit_Null(self, node):
        return 'null'

    def visit_String(self, node):
        return node.value

    def visit_Continue(self, node):
        s = self._make_indent()
        if node.identifier is not None:
            s += 'continue %s;' % self.visit_Identifier(node.identifier)
        else:
            s += 'continue;'
        return s

    def visit_Break(self, node):
        s = self._make_indent()
        if node.identifier is not None:
            s += 'break %s;' % self.visit_Identifier(node.identifier)
        else:
            s += 'break;'
        return s

    def visit_Return(self, node):
        s = self._make_indent()
        if node.expr is None:
            return s + 'return;'
        else:
            return '%sreturn %s;' % (s, self.visit(node.expr))

    def visit_With(self, node):
        s = self._make_indent()
        s += 'with (%s) ' % self.visit(node.expr)
        s += self.visit(node.statement)
        return s

    def visit_Label(self, node):
        s = '%s%s: %s' % (
            self._make_indent(),
            self.visit(node.identifier), self.visit(node.statement))
        return s

    def visit_Switch(self, node):
        s = self._make_indent()
        s += 'switch (%s) {\n' % self.visit(node.expr)
        self.indent_level += 2
        for case in node.cases:
            s += self.visit_Case(case)
        if node.default is not None:
            s += self.visit_Default(node.default)
        self.indent_level -= 2
        s += '\n}'
        return s

    def visit_Case(self, node):
        s = self._make_indent()
        s += 'case %s:\n' % self.visit(node.expr)
        self.indent_level += 2
        elements = '\n'.join(self.visit(element) for element in node.elements)
        if elements:
            s += elements + '\n'
        self.indent_level -= 2
        return s

    def visit_Default(self, node):
        s = self._make_indent() + 'default:\n'
        self.indent_level += 2
        s += '\n'.join(self.visit(element) for element in node.elements)
        self.indent_level -= 2
        return s

    def visit_Throw(self, node):
        s = '%sthrow %s;' % (self._make_indent(), self.visit(node.expr))
        return s

    def visit_Debugger(self, node):
        return '%s;' % node.value

    def visit_Try(self, node):
        s = self._make_indent() + 'try '
        s += self.visit(node.statements)
        if node.catch is not None:
            s += ' ' + self.visit(node.catch)
        if node.fin is not None:
            s += ' ' + self.visit(node.fin)
        return s

    def visit_Catch(self, node):
        s = self._make_indent()
        s += 'catch (%s) %s' % (
            self.visit(node.identifier), self.visit(node.elements))
        return s

    def visit_Finally(self, node):
        s = self._make_indent()
        s += 'finally %s' % self.visit(node.elements)
        return s


