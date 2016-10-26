# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from orchestra.expressions import jinja
from orchestra.tests.unit import base
from orchestra.utils import plugin


class JinjaValidationTest(base.ExpressionEvaluatorTest):

    @classmethod
    def setUpClass(cls):
        cls.language = 'jinja'
        super(JinjaValidationTest, cls).setUpClass()

    def test_get_evaluator(self):
        self.assertEqual(
            plugin.get_module(
                'orchestra.expressions.evaluators',
                self.language
            ),
            jinja.JinjaEvaluator
        )

    def test_basic_validate(self):
        self.assertListEqual([], self.evaluator.validate('{{ 1 }}'))
        self.assertListEqual([], self.evaluator.validate('{{ abc }}'))
        self.assertListEqual([], self.evaluator.validate('{{ 1 + 2 }}'))
        self.assertListEqual([], self.evaluator.validate('{{ _.foo }}'))
        self.assertListEqual([], self.evaluator.validate('{{ _.a1 + _.a2 }}'))

    def test_parse_error(self):
        expr = '{{ {{ _.foo }} }}'
        errors = self.evaluator.validate(expr)

        self.assertEqual(1, len(errors))
        self.assertIn('unexpected end of template', errors[0]['message'])

    def test_multiple_errors(self):
        expr = '{{ 1 +/ 2 }} and {{ * }}'
        errors = self.evaluator.validate(expr)

        self.assertEqual(2, len(errors))
        self.assertIn('unexpected', errors[0]['message'])
        self.assertIn('unexpected', errors[1]['message'])
