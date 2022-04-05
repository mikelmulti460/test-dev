from datetime import date
from django.db import models


# Create your models here.

class VehicleType(models.Model):
    name = models.CharField(max_length=32)
    max_capacity = models.PositiveIntegerField()

    def __str__(self) -> str:
        return self.name


class Vehicle(models.Model):
    name = models.CharField(max_length=32)
    passengers = models.PositiveIntegerField()
    vehicle_type = models.ForeignKey(VehicleType, null=True, on_delete=models.SET_NULL)
    number_plate = models.CharField(max_length=10)

    def __str__(self) -> str:
        return self.name

    def can_start(self) -> bool:
        return self.vehicle_type.max_capacity >= self.passengers
    
    def get_distribution(self) -> list:
        distribution = [[False,False] for _ in range((self.passengers//2)+1)]
        print(distribution)
        for i in range(self.passengers):
            distribution[i//2][i%2] = True
        return distribution


class Journey(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT)
    start = models.DateField()
    end = models.DateField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.vehicle.name} ({self.start} - {self.end})"
    
    def stop(self, end: date):
        if self.is_finished():
            raise ValueError("Journey is already finished")
        self.end = end
        #self.save()
        

    def is_finished(self) -> bool:
        return self.end is not None

def validate_number_plate(number_plate: str) -> bool:
    first_two_caracters = number_plate[:2].isalpha()
    two_middle_digits = number_plate[3:5].isdigit()
    last_four_digits = number_plate[6:].isdigit()
    separator = number_plate[2] == '-' and number_plate[5] == '-'
    return first_two_caracters and two_middle_digits and last_four_digits \
        and separator and len(number_plate) == 8