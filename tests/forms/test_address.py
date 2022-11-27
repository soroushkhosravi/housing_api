"""Tests related to the AddressFrom."""
from forms.address import AddressForm
from flask import Flask
from werkzeug.datastructures import ImmutableMultiDict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'abc'
app.config['WTF_CSRF_ENABLED'] = False


def test_form_can_be_validated_when_required_fields_provided():
    """Tests we can validate the form."""
    with app.test_request_context():
        form = AddressForm(ImmutableMultiDict([('post_code', 'HP1 2DD')]))

        assert isinstance(form, AddressForm)
        assert form.validate() is True
        assert not form.errors


def test_form_does_not_validate_when_postcode_is_missed():
    """Tests postcode is required for the form submitting."""
    with app.test_request_context():
        form = AddressForm(ImmutableMultiDict([]))

        assert isinstance(form, AddressForm)
        assert form.validate() is False
        assert form.errors == {'post_code': ['This field is required.']}