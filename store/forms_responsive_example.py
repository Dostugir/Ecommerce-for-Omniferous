from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

class MySampleForm(forms.Form):
    first_name = forms.CharField(label="First Name")
    last_name = forms.CharField(label="Last Name")
    email = forms.EmailField(label="Email")
    address = forms.CharField(label="Address", widget=forms.Textarea)
    city = forms.CharField(label="City")
    postal_code = forms.CharField(label="Postal Code")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('email', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'address',
            Row(
                Column('city', css_class='form-group col-md-6 mb-0'),
                Column('postal_code', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Submit', css_class='btn btn-primary')
        )
