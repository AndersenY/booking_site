from django.db import models


class Booking(models.Model):
    # Заменяем ForeignKey на CharField
    apartment = models.CharField(max_length=255, null=True)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    guests = models.PositiveIntegerField()

    def __str__(self):
        return f"Booking for {self.apartment} from {self.check_in_date} to {self.check_out_date} for {self.guests} guests"


class Calendar(models.Model):
    # Хранит список забронированных дат
    booked_dates = models.JSONField(default=list)

    def __str__(self):
        return f"Calendar with booked dates: {self.booked_dates}"

    def add_booked_date(self, date):
        if date not in self.booked_dates:
            self.booked_dates.append(date)
            self.save()

    def remove_booked_date(self, date):
        if date in self.booked_dates:
            self.booked_dates.remove(date)
            self.save()


class Apartment(models.Model):
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    # Поле для хранения URL изображения
    image = models.URLField(max_length=200, null=True, blank=True)
    # Поле для хранения ссылки на полную информацию
    link = models.URLField(max_length=200, null=True, blank=True)
    # Поле для связи с календарем
    calendar = models.OneToOneField(
        Calendar, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Apartment at ${self.price_per_night} per night"
