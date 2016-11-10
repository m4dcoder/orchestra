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

from functools import partial
import inspect
import logging
import re
import six

import jinja2

from orchestra import exceptions as exc
from orchestra.expressions import base
from orchestra.expressions.functions import base as functions


LOG = logging.getLogger(__name__)


def register_functions(env):
    catalog = functions.load()

    for name, func in six.iteritems(catalog):
        env.filters[name] = func

    return catalog


class JinjaEvaluator(base.Evaluator):
    _delimiter = '{{}}'
    _regex_pattern = '{{.*?}}'
    _regex_parser = re.compile(_regex_pattern)

    _block_delimiter = '{%}'
    _regex_block_pattern = '{%.*?%}'
    _regex_block_parser = re.compile(_regex_block_pattern)

    _jinja_env = jinja2.Environment(
        undefined=jinja2.StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True
    )

    _custom_functions = register_functions(_jinja_env)

    @classmethod
    def contextualize(cls, data):
        ctx = {'_': data}

        for name, func in six.iteritems(cls._custom_functions):
            ctx[name] = partial(func, ctx['_'])

        if isinstance(data, dict):
            ctx['__task_states'] = data.get('__task_states')

        return ctx

    @classmethod
    def validate(cls, text):
        if not isinstance(text, six.string_types):
            raise ValueError('Text to be evaluated is not typeof string.')

        errors = []

        def append_error(expr, exc):
            error = {
                'message': str(getattr(exc, 'message', exc)),
                'expression': expr
            }

            errors.append(error)

        # Validate the entire text to cover malformed delimiters and blocks.
        try:
            cls._jinja_env.parse(text)
        except jinja2.exceptions.TemplateError as e:
            append_error(text, e)

        # Validate individual inline expressions.
        for expr in cls._regex_parser.findall(text):
            try:
                parser = jinja2.parser.Parser(
                    cls._jinja_env.overlay(),
                    cls.strip_delimiter(expr),
                    state='variable'
                )

                parser.parse_expression()
            except jinja2.exceptions.TemplateError as e:
                append_error(cls.strip_delimiter(expr), e)

        return errors

    @classmethod
    def _traverse_and_evaluate(cls, text, data=None):
        output = text
        exprs = cls._regex_parser.findall(text)
        block_exprs = cls._regex_block_parser.findall(text)
        ctx = cls.contextualize(data)
        opts = {'undefined_to_none': False}

        try:
            # Evaluate inline jinja expressions first.
            for expr in exprs:
                stripped = cls.strip_delimiter(expr)
                compiled = cls._jinja_env.compile_expression(stripped, **opts)
                result = compiled(**ctx)

                if inspect.isgenerator(result):
                    result = list(result)

                if isinstance(result, six.string_types):
                    result = cls._traverse_and_evaluate(result, data)

                # For StrictUndefined values, UndefinedError only gets raised
                # when the value is accessed, not when it gets created. The
                # simplest way to access it is to try and cast it to string.
                # When StrictUndefined is cast to str below, this will raise
                # an exception with error description.
                if not isinstance(result, jinja2.runtime.StrictUndefined):
                    output = (
                        output.replace(expr, str(result))
                        if len(exprs) > 1 or block_exprs
                        else result
                    )

            # Evaluate jinja block(s) after inline expressions are evaluated.
            if block_exprs and isinstance(output, six.string_types):
                output = cls._jinja_env.from_string(output).render(ctx)

                # Traverse and evaulate again in case additional inline
                # epxressions are introduced after the jinja block is evaluated.
                output = cls._traverse_and_evaluate(output, data)

        except jinja2.exceptions.UndefinedError as e:
            raise exc.JinjaEvaluationException(str(getattr(e, 'message', e)))

        return output

    @classmethod
    def evaluate(cls, text, data=None):
        if not isinstance(text, six.string_types):
            raise ValueError('Text to be evaluated is not typeof string.')

        if data and not isinstance(data, dict):
            raise ValueError('Provided data is not typeof dict.')

        output = cls._traverse_and_evaluate(text, data=data)

        if isinstance(output, six.string_types):
            exprs = [
                cls.strip_delimiter(expr)
                for expr in cls._regex_parser.findall(output)
            ]

            if exprs:
                raise exc.JinjaEvaluationException(
                    'There are unresolved variables: %s' % ', '.join(exprs)
                )

        return output
