"""The definition of the crime schema."""
from marshmallow import Schema, fields, post_load, EXCLUDE, pre_load
from models.crime import Crime


class CrimeSchema(Schema):
    _model = Crime
    class Meta:
        unknown = EXCLUDE
    category = fields.Str()
    date = fields.Date(data_key='month')

    @pre_load
    def correct_date(self, data, **kwargs):
        """Adds a day to the date string."""
        data['month'] += '-15'
        return data

    @post_load
    def load_crime(self, data, **kwargs):
        """Loads the model."""
        return self._model(**data)