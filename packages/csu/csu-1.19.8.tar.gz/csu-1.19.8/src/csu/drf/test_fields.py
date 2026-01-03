from datetime import date
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
import time_machine
from django import forms
from django.db import models
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SkipField

from ..timezones import today
from .fields import AsciiCharField
from .fields import ChassisNumberField
from .fields import EnumField
from .fields import LocalizedDateField
from .fields import LocalizedTimeField
from .fields import RegistrationNumberField
from .fields import RomanianRegistrationNumberField
from .forms import formfield_for_drf_field


def test_localized_date_field_unbound():
    pytest.raises(TypeError, LocalizedDateField, default_timezone=123)
    pytest.raises(TypeError, LocalizedDateField, timezone=123, default_timezone=123)
    field = LocalizedDateField()
    with pytest.raises(KeyError) as exc:
        assert field.to_representation(date(2025, 1, 1))
    assert exc.value.args == ("timezone",)


def test_localized_date_field_default():
    field = LocalizedDateField(timezone="Europe/Bucharest")
    assert field.run_validation("2025-01-01") == date(2025, 1, 1)
    with pytest.raises(ValidationError) as exc:
        assert field.run_validation("2025-01-01T00:00:00+12:34")
    assert exc.value.detail == ["Date has wrong format. Use one of these formats instead: YYYY-MM-DD."]


def test_localized_date_field_repr():
    field = LocalizedDateField(timezone="Europe/Bucharest")
    assert field.to_representation(date(2025, 1, 1)) == "2025-01-01T00:00:00+02:00"


def test_localized_datetime_field_serializer():
    class LocalizedDateSerializer(serializers.Serializer):
        ltf_field = LocalizedTimeField()
        ldf_field = LocalizedDateField()

    serializer = LocalizedDateSerializer(
        data={
            "ltf_field": "2025-01-01",
            "ldf_field": "2025-01-01",
        }
    )
    with pytest.raises(KeyError) as exc:
        serializer.is_valid(raise_exception=True)
    assert exc.value.args == ("timezone",)

    serializer = LocalizedDateSerializer(
        data={
            "ltf_field": "2025-01-01T00:00:00Z",
            "ldf_field": "2025-01-01T00:00:00Z",
        },
        context={"timezone": ZoneInfo("Europe/Bucharest")},
    )
    serializer.is_valid()
    assert serializer.errors == {"ldf_field": ["Date has wrong format. Use one of these formats instead: YYYY-MM-DD."]}

    serializer = LocalizedDateSerializer(
        data={
            "ltf_field": "2025-01-01",
            "ldf_field": "2025-01-01",
        },
        context={"timezone": ZoneInfo("Europe/Bucharest")},
    )
    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data == {"ldf_field": date(2025, 1, 1), "ltf_field": datetime(2025, 1, 1, 0, tzinfo=ZoneInfo("Europe/Bucharest"))}
    assert serializer.data == {
        "ldf_field": "2025-01-01T00:00:00+02:00",
        "ltf_field": "2025-01-01T00:00:00+02:00",
    }


def test_localized_time_field_unbound():
    pytest.raises(TypeError, LocalizedTimeField, default_timezone=123)
    pytest.raises(TypeError, LocalizedTimeField, timezone=123, default_timezone=123)
    field = LocalizedTimeField()
    with pytest.raises(KeyError) as exc:
        assert field.run_validation("2025-01-01") == 123
    assert exc.value.args == ("timezone",)


def test_localized_time_field_default():
    field = LocalizedTimeField(timezone="Europe/Bucharest")
    assert field.run_validation("2025-01-01") == datetime(2025, 1, 1, tzinfo=ZoneInfo("Europe/Bucharest"))
    assert field.run_validation("2025-01-01T00:00:00+12:34") == datetime(2024, 12, 31, 13, 26, tzinfo=ZoneInfo("Europe/Bucharest"))


def test_localized_time_field_serializer():
    class LocalizedTimeSerializer(serializers.Serializer):
        field = LocalizedTimeField()

    serializer = LocalizedTimeSerializer(data={"field": "2025-01-01"})
    with pytest.raises(KeyError) as exc:
        serializer.is_valid(raise_exception=True)
    assert exc.value.args == ("timezone",)

    serializer = LocalizedTimeSerializer(data={"field": "2025-01-01T00:00:00Z"}, context={"timezone": ZoneInfo("Europe/Bucharest")})
    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data == {"field": datetime(2025, 1, 1, 2, tzinfo=ZoneInfo("Europe/Bucharest"))}

    serializer = LocalizedTimeSerializer(data={"field": "2025-01-01"}, context={"timezone": ZoneInfo("Europe/Bucharest")})
    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data == {"field": datetime(2025, 1, 1, tzinfo=ZoneInfo("Europe/Bucharest"))}


def test_localized_time_field_serializer_default():
    class LocalizedTimeSerializer(serializers.Serializer):
        field = LocalizedTimeField(timezone="Europe/Bucharest")

    serializer = LocalizedTimeSerializer(data={"field": "2025-01-01"})
    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data == {"field": datetime(2025, 1, 1, tzinfo=ZoneInfo("Europe/Bucharest"))}


def test_registration_number_field():
    field = RomanianRegistrationNumberField()
    assert field.run_validation("\t cj 12 ТУХ ") == "CJ12TYX"
    with pytest.raises(ValidationError) as exc:
        field.run_validation("\t cj 123 ТУХ ")
    assert exc.value.args == (["Invalid registration number."],)


def test_registration_number_field_io():
    field = RomanianRegistrationNumberField()
    assert field.run_validation("\t cj 12 aio ") == "CJ12AIO"


def test_registration_number_field_q():
    field = RomanianRegistrationNumberField()
    with pytest.raises(ValidationError) as exc:
        field.run_validation("\t cj 12 ТУQ ")
    assert exc.value.args == (["Cannot contain the letter Q."],)


def test_registration_number_field_i():
    field = RomanianRegistrationNumberField()
    with pytest.raises(ValidationError) as exc:
        field.run_validation("\t cj 12 IBO ")
    assert exc.value.args == (["Letters sequence cannot start with I."],)


def test_registration_number_field_o():
    field = RomanianRegistrationNumberField()
    with pytest.raises(ValidationError) as exc:
        field.run_validation("\t cj 12 OBI ")
    assert exc.value.args == (["Letters sequence cannot start with O."],)


def test_romanian_registration_number_field():
    field = RomanianRegistrationNumberField()
    with pytest.raises(ValidationError) as exc:
        field.run_validation("CJ 1234")
    assert exc.value.args == ("Leasing registration number must include expiry date (YY/MM).",)

    with pytest.raises(ValidationError) as exc:
        field.run_validation("CJ 12345")
    assert exc.value.args == ("Leasing registration number has invalid month: 45.",)

    with pytest.raises(ValidationError) as exc:
        field.run_validation("CJ 1234567")
    assert exc.value.args == ("Leasing registration number has invalid year: 45.",)

    now = today()
    with pytest.raises(ValidationError) as exc:
        field.run_validation(f"CJ 1234-{now.year - 1}/00")
    assert exc.value.args == ("Leasing registration number has invalid month: 00.",)

    with time_machine.travel(date(2025, 2, 28)):
        with pytest.raises(ValidationError) as exc:
            field.run_validation(f"CJ 1234-{now.year - 1}/01")
    assert exc.value.args == ("Leasing registration number is expired: 2024/01 is less than 2025/02.",)


class MultiEnum(models.IntegerChoices):
    first = 0, "1st"
    second = 1, "2nd"
    third = 2, "3rd"


class SoloEnum(models.IntegerChoices):
    single = 0, "1st"


@pytest.mark.parametrize(
    ("enum_class", "value", "error", "result"),
    [
        (MultiEnum, "first", None, 0),
        (MultiEnum, "second", None, 1),
        (MultiEnum, "third", None, 2),
        (MultiEnum, "junk", "'junk' is not a valid choice. Must be one of: 'first', 'second' or 'third'.", None),
        (MultiEnum, 2, "'2' is not a valid choice. Must be one of: 'first', 'second' or 'third'.", None),
        (SoloEnum, "single", None, 0),
        (SoloEnum, "junk", "'junk' is not a valid choice. Must be one of: 'single'.", None),
        (SoloEnum, 0, "'0' is not a valid choice. Must be one of: 'single'.", None),
    ],
)
def test_enum_field_multi(enum_class, value, error, result):
    assert not (error and result)
    field = EnumField(enum=enum_class)
    if error:
        with pytest.raises(ValidationError) as exc_info:
            field.run_validation(value)

        (detail,) = exc_info.value.detail
        assert str(detail) == error
    else:
        assert field.run_validation(value) == result


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (" \t 1a\t b,.-=;\"_'c\t  ", "1ABC"),
        ("АВЕКМНОРСТ", "ABEKMHOPCT"),
        ("УХавекмнор", "YXABEKMHOP"),
        ("стухo0q0q0", "CTYXO0Q0Q0"),
    ],
)
def test_registration_number_valid(value, expected):
    assert expected.encode("ascii")
    assert RegistrationNumberField().run_validation(value) == expected
    assert formfield_for_drf_field(RegistrationNumberField())().clean(value) == expected
    assert AsciiCharField(only_alphanumerics=True, uppercase=True).run_validation(value) == expected
    assert formfield_for_drf_field(AsciiCharField(only_alphanumerics=True, uppercase=True))().clean(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2S3DA417576128786", "2S3DA417576128786"),
        ("JH4KA4530LC018693", "JH4KA4530LC018693"),
        ("km8jn72dx7u587496", "KM8JN72DX7U587496"),
        ("sca664s5xaux48670", "SCA664S5XAUX48670"),
        ("5tfhw5f13ax136128", "5TFHW5F13AX136128"),
        ("1M8GDM9AXKP042788", "1M8GDM9AXKP042788"),
        ("АВЕКМНzРСТУХавекм", "ABEKMHZPCTYXABEKM"),
        ("нZрстухZ0z0z0z0z0", "HZPCTYXZ0Z0Z0Z0Z0"),
    ],
)
def test_chassis_number_valid(value, expected):
    assert expected.encode("ascii")
    assert ChassisNumberField().run_validation(value) == expected
    assert formfield_for_drf_field(ChassisNumberField())().clean(value) == expected


def test_chassis_number_not_required():
    pytest.raises(SkipField, ChassisNumberField(required=False).run_validation)
    assert ChassisNumberField(required=False, allow_blank=True).run_validation("") == ""

    with pytest.raises(forms.ValidationError) as exc_info:
        formfield_for_drf_field(ChassisNumberField(required=False, allow_blank=True))().clean("")
    assert exc_info.value.args == ("This field is required.", "required", None)
    assert formfield_for_drf_field(ChassisNumberField(required=False, allow_blank=True))(required=False).clean("") == ""


def test_chassis_number_required():
    field = formfield_for_drf_field(ChassisNumberField())()
    exc_info = pytest.raises(forms.ValidationError, field.clean, "")
    assert exc_info.value.args == ("This field may not be blank.", "blank", None)
    field = formfield_for_drf_field(ChassisNumberField(allow_blank=True))()
    exc_info = pytest.raises(forms.ValidationError, field.clean, "")
    assert exc_info.value.args == ("This field is required.", "required", None)


def test_invalid_length():
    field = formfield_for_drf_field(ChassisNumberField())()
    exc_info = pytest.raises(forms.ValidationError, field.clean, "123")
    assert exc_info.value.args == ("Chassis number must have 17 characters (3 given).", "length", None)


def test_invalid_no_length_required():
    field = formfield_for_drf_field(ChassisNumberField(required_length=None))()
    assert field.clean("123abc") == "123ABC"


def test_formfield_for_drf_field_no_options():
    field = formfield_for_drf_field(
        ChassisNumberField,
    )()
    exc_info = pytest.raises(forms.ValidationError, field.clean, "")
    assert str(exc_info.value) == "['This field may not be blank.']"
    exc_info = pytest.raises(forms.ValidationError, field.clean, "a- ." * 18)
    assert str(exc_info.value) == "['Chassis number must have 17 characters (18 given).']"
    assert field.clean("a" * 17) == "A" * 17


def test_formfield_for_drf_field():
    drffield = formfield_for_drf_field(
        ChassisNumberField,
        required=False,
        required_length=None,
        allow_blank=True,
    )(
        max_length=32,
        required=False,
    )

    assert drffield.clean("") == ""
    assert drffield.clean("a") == "A"
    assert drffield.clean("a" * 32) == "A" * 32
    assert drffield.clean("a- ." * 32) == "A" * 32

    djfield = forms.CharField(
        required=False,
        max_length=32,
    )
    for field in (drffield, djfield):
        exc_info = pytest.raises(forms.ValidationError, field.clean, "a" * 33)
        assert str(exc_info.value) == "['Ensure this value has at most 32 characters (it has 33).']"
        assert repr(exc_info.value) == "ValidationError(['Ensure this value has at most 32 characters (it has 33).'])"
        assert repr(exc_info.value.args) == "([ValidationError(['Ensure this value has at most 32 characters (it has 33).'])], None, None)"
