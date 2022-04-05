from django.utils import timezone
from django.http import Http404

from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView


from adventure import models, notifiers, repositories, serializers, usecases


class CreateVehicleAPIView(APIView):
    def post(self, request: Request) -> Response:
        payload = request.data
        vehicle_type = models.VehicleType.objects.get(name=payload["vehicle_type"])
        vehicle = models.Vehicle.objects.create(
            name=payload["name"],
            passengers=payload["passengers"],
            vehicle_type=vehicle_type,
        )
        return Response(
            {
                "id": vehicle.id,
                "name": vehicle.name,
                "passengers": vehicle.passengers,
                "vehicle_type": vehicle.vehicle_type.name,
            },
            status=201,
        )


class StartJourneyAPIView(generics.CreateAPIView):
    serializer_class = serializers.JourneySerializer

    def perform_create(self, serializer) -> None:
        repo = self.get_repository()
        notifier = notifiers.Notifier()
        usecase = usecases.StartJourney(repo, notifier).set_params(
            serializer.validated_data
        )
        try:
            usecase.execute()
        except usecases.StartJourney.CantStart as e:
            raise ValidationError({"detail": str(e)})

    def get_repository(self) -> repositories.JourneyRepository:
        return repositories.JourneyRepository()

class StopJourneyAPIView(APIView):
    def get_object(self, pk: int) -> models.Journey:
        try:
            return models.Journey.objects.get(pk=pk)
        except models.Journey.DoesNotExist:
            raise Http404

    def post(self, request: Request, *args, **kwargs) -> Response:
        print(kwargs["pk"])
        journey = self.get_object(kwargs["pk"])
        journey.stop(timezone.now().date())
        journey.save()
        return Response(
            {
                "id": journey.id,
                "start": journey.start,
                "end": journey.end,
            },
            status=status.HTTP_200_OK,
        )


# class StopJourneyAPIView(generics.UpdateAPIView):
    
#     serializer_class = serializers.JourneySerializer

#     def get_object(self) -> models.Journey:
#         return models.Journey.objects.get(id=self.kwargs["pk"])

#     def get_repository(self) -> repositories.JourneyRepository:
#         return repositories.JourneyRepository()
    
#     def perform_update(self, serializer) -> None:
#         repo = self.get_repository()
#         notifier = notifiers.Notifier()
#         usecase = usecases.StopJourney(repo, notifier).set_params(
#             self.get_object()
#         )
#         try:
#             usecase.execute()
#         except Exception as e:
#             raise ValidationError({"detail": str(e)})




       
