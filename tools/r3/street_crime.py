"""The street outside the precinct at 4:52 a.m., the morning Sal Moretti died (Case 5, scene 1): the same set as the
street, in its crime-scene state (street.build(crime=True))."""
import street


def build(hide=()):
    return street.build(hide, crime=True)
