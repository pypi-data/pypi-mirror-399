from typing import Final

class Weekday:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    MONDAY: Final["Weekday"] | None = None
    TUESDAY: Final["Weekday"] | None = None
    WEDNESDAY: Final["Weekday"] | None = None
    THURSDAY: Final["Weekday"] | None = None
    FRIDAY: Final["Weekday"] | None = None
    SATURDAY: Final["Weekday"] | None = None
    SUNDAY: Final["Weekday"] | None = None

Weekday.MONDAY = Weekday(0, "Monday")
Weekday.TUESDAY = Weekday(1, "Tuesday")
Weekday.WEDNESDAY = Weekday(2, "Wednesday")
Weekday.THURSDAY = Weekday(3, "Thursday")
Weekday.FRIDAY = Weekday(4, "Friday")
Weekday.SATURDAY = Weekday(5, "Saturday")
Weekday.SUNDAY = Weekday(6, "Sunday")