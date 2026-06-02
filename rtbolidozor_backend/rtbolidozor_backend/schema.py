from .models import Observatory, Station

# Definování typu pro Observatory
class ObservatoryType(DjangoObjectType):
    class Meta:
        model = Observatory

    stations = graphene.List(lambda: StationType)

    def resolve_stations(self, info):
        return self.stations.all()

# Definování typu pro Station
class StationType(DjangoObjectType):
    class Meta:
        model = Station

# Definování dotazů
class Query(graphene.ObjectType):
    observatory = graphene.Field(ObservatoryType, identifier=graphene.String())
    all_observatories = graphene.List(ObservatoryType)
    station = graphene.Field(StationType, identifier=graphene.String())
    all_stations = graphene.List(StationType)

    # Resolver pro jednu observatoř podle identifikátoru
    def resolve_observatory(self, info, identifier):
        try:
            return Observatory.objects.get(identifier=identifier)
        except Observatory.DoesNotExist:
            return None

    # Resolver pro všechny observatoře
    def resolve_all_observatories(self, info):
        return Observatory.objects.all()

    # Resolver pro jednu stanici podle identifikátoru
    def resolve_station(self, info, identifier):
        try:
            return Station.objects.get(identifier=identifier)
        except Station.DoesNotExist:
            return None

    # Resolver pro všechny stanice
    def resolve_all_stations(self, info):
        return Station.objects.all()

schema = graphene.Schema(query=Query)