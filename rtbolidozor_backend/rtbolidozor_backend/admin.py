from django.contrib import admin
from django.contrib import messages
from .models import Station, Observatory, BolidozorUser, Event, File, MultiStationEvent, Snapshot, CachedStats

from import_export.admin import ExportMixin, ImportExportModelAdmin
from import_export import resources



# Resource třídy pro Import-Export
class ObservatoryResource(resources.ModelResource):
    class Meta:
        model = Observatory
        fields = ('identifier', 'name', 'location', 'latitude', 'longitude')


from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import Observatory, Station

class StationResource(resources.ModelResource):
    observatory_identifier = fields.Field(
        column_name='observatory_identifier',
        attribute='observatory',
        widget=ForeignKeyWidget(Observatory, 'identifier')
    )
    observatory_name = fields.Field(
        column_name='observatory_name',
        attribute='observatory__name'
    )
    observatory_location = fields.Field(
        column_name='observatory_location',
        attribute='observatory__location'
    )
    observatory_latitude = fields.Field(
        column_name='observatory_latitude',
        attribute='observatory__latitude'
    )
    observatory_longitude = fields.Field(
        column_name='observatory_longitude',
        attribute='observatory__longitude'
    )

    class Meta:
        model = Station
        fields = ('identifier', 'name', 'location', 'status', 'last_active',
                  'observatory_identifier', 'observatory_name', 'observatory_location', 
                  'observatory_latitude', 'observatory_longitude')



@admin.register(Observatory)
class ObservatoryAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = ObservatoryResource
    search_help_text = ""
    list_display = ('identifier', 'name', 'location', 'latitude', 'longitude', 'station_count')
    search_fields = ('identifier', 'name', 'location')
    list_filter = ('location',)
    ordering = ('identifier',)

    def station_count(self, obj):
        return obj.stations.count()
    station_count.short_description = "Number of Stations"


@admin.register(Station)
class StationAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = StationResource
    list_display = ('identifier', 'name', 'observatory', 'status', 'last_active')
    search_help_text = ""
    search_fields = ('identifier', 'name', 'location', 'observatory__name')
    list_filter = ('status', 'observatory')
    ordering = ('identifier',)
    autocomplete_fields = ('observatory',)


#admin.site.register(Station)
#admin.site.register(Observatory)
admin.site.register(BolidozorUser)

admin.site.register(Event)
admin.site.register(MultiStationEvent)
admin.site.register(Snapshot)
#admin.site.register(EventMetadata)

admin.site.register(File)


@admin.register(CachedStats)
class CachedStatsAdmin(admin.ModelAdmin):
    list_display = ('key', 'generated_at')
    actions = ['regenerate']

    @admin.action(description='Regenerate statistics')
    def regenerate(self, request, queryset):
        from .tasks import generate_statistics
        result = generate_statistics()
        self.message_user(request, result, messages.SUCCESS)
