# This file is part of Hypothesis, which may be found at
# https://github.com/HypothesisWorks/hypothesis/
#
# Copyright the Hypothesis Authors.
# Individual contributors are listed in AUTHORS.rst and the git log.
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at https://mozilla.org/MPL/2.0/.

import pytest

from hypothesis import given, settings, strategies as st

from tests.common.utils import fails_with


def fails_with_output(expected, error=AssertionError, **kw):
    expected = [expected] if isinstance(expected, str) else expected

    def _inner(f):
        def _new():
            with pytest.raises(error) as err:
                settings(print_blob=False, derandomize=True, **kw)(f)()
            got = "\n".join(err.value.__notes__).strip() + "\n"
            assert any(got == s.strip() + "\n" for s in expected)

        return _new

    return _inner


@fails_with_output(
    """
Falsifying example: test_inquisitor_comments_basic_fail_if_either(
    # The test always failed when commented parts were varied together.
    a=False,  # or any other generated value
    b=True,
    c=[],  # or any other generated value
    d=True,
    e=False,  # or any other generated value
)
"""
)
@given(st.booleans(), st.booleans(), st.lists(st.none()), st.booleans(), st.booleans())
def test_inquisitor_comments_basic_fail_if_either(a, b, c, d, e):
    assert not (b and d)


@fails_with_output(
    """
Falsifying example: test_inquisitor_comments_basic_fail_if_not_all(
    # The test sometimes passed when commented parts were varied together.
    a='',  # or any other generated value
    b='',  # or any other generated value
    c='',  # or any other generated value
)
"""
)
@given(st.text(), st.text(), st.text())
def test_inquisitor_comments_basic_fail_if_not_all(a, b, c):
    condition = a and b and c
    assert condition


@fails_with_output(
    """
Falsifying example: test_inquisitor_no_together_comment_if_single_argument(
    a='',
    b='',  # or any other generated value
)
"""
)
@given(st.text(), st.text())
def test_inquisitor_no_together_comment_if_single_argument(a, b):
    assert a


@fails_with(ZeroDivisionError)
@settings(database=None)
@given(start_date=st.datetimes(), data=st.data())
def test_issue_3755_regression(start_date, data):
    data.draw(st.datetimes(min_value=start_date))
    raise ZeroDivisionError
