try:
        
    from base.models import EmployeeShiftDay
    if len(EmployeeShiftDay.objects.all()) == 0:
        days = (
            ("monday", "Monday"),
            ("tuesday", "Tuesday"),
            ("wednesday", "Wednesday"),
            ("thursday", "Thursday"),
            ("friday", "Friday"),
            ("saturday", "Saturday"),
            ("sunday", "Sunday"),
        )
        for day in days:
            shift_day = EmployeeShiftDay()
            shift_day.day = day[0]
            shift_day.save()
except :
    pass