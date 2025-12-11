from django.contrib import admin
from .models import Donation, Location, Claim
from django.db.models import Count, Sum
from django.http import HttpResponse
import csv

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'donor',
        'available_quantity_display',
        'claimed_quantity',
        'deleted_quantity_display',
         'expiry_date_display',
        'created_at',
        'is_deleted',
        'deleted_at',
    )
    list_filter = ('is_deleted', 'status', 'donation_type', 'location')
    search_fields = ('title', 'donor__username', 'address')
    readonly_fields = ('deleted_at', 'deleted_by', 'created_at', 'updated_at', 'deleted_quantity')

    def has_add_permission(self, request):
            return False  # Remove "Add Donation"

    def available_quantity_display(self, obj):
        """Show 0 if deleted, otherwise actual available quantity"""
        return 0 if obj.is_deleted else obj.available_quantity
    available_quantity_display.short_description = 'Available Quantity'

    def claimed_quantity(self, obj):
        """Sum of claimed quantities"""
        claimed_sum = obj.claims.aggregate(total=Sum('quantity'))['total'] or 0
        return claimed_sum
    claimed_quantity.short_description = 'Claimed Quantity'

    def expiry_date_display(self, obj):
        return obj.expiry_date or "-"
    expiry_date_display.short_description = "Expiry Date"
    
    def deleted_quantity_display(self, obj):
        """Show deleted quantity if deleted"""
        return obj.deleted_quantity if obj.is_deleted else 0
    deleted_quantity_display.short_description = 'Deleted Quantity'

    actions = ['export_selected_as_csv', 'export_summary_as_csv']

    def export_selected_as_csv(self, request, queryset):
        """
        Export selected Donation rows as CSV with sensible columns.
        """
        meta = self.model._meta
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=donations_selected.csv'
        writer = csv.writer(response)
        # header
        writer.writerow(['id','title','donor_username','donor_email','status','donation_type',
                         'initial_quantity','available_quantity','location','created_at','expiry_date'])
        for obj in queryset.select_related('donor','location'):
            writer.writerow([
                obj.pk,
                obj.title,
                getattr(obj.donor, 'username', ''),
                getattr(obj.donor, 'email', ''),
                obj.status,
                obj.donation_type,
                obj.initial_quantity,
                obj.available_quantity,
                getattr(obj.location, 'name', ''),
                obj.created_at.isoformat() if obj.created_at else '',
                obj.expiry_date.isoformat() if obj.expiry_date else '',
            ])
        return response
    export_selected_as_csv.short_description = "Export selected donations to CSV"

    def export_summary_as_csv(self, request, queryset):
        """
        Export aggregated summary: counts by status and counts by location,
        plus totals for selected set (or all if nothing selected).
        """
        # If no rows selected, base on all filtered results shown in changelist.
        qs = queryset if queryset.exists() else Donation.objects.all()

        # Aggregations
        from django.db.models import Count, Sum
        status_counts = qs.values('status').annotate(count=Count('id')).order_by('-count')
        loc_counts = qs.values('location__name').annotate(count=Count('id')).order_by('-count')
        totals = qs.aggregate(total_donations=Count('id'), total_initial=Sum('initial_quantity'), total_available=Sum('available_quantity'))

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=donations_summary.csv'
        writer = csv.writer(response)

        writer.writerow(['Report for selected donations' if queryset.exists() else 'Report for ALL donations'])
        writer.writerow([])
        writer.writerow(['Totals'])
        writer.writerow(['total_donations', totals.get('total_donations') or 0])
        writer.writerow(['total_initial_quantity', totals.get('total_initial') or 0])
        writer.writerow(['total_available_quantity', totals.get('total_available') or 0])
        writer.writerow([])

        writer.writerow(['Counts by status'])
        writer.writerow(['status','count'])
        for row in status_counts:
            writer.writerow([row['status'], row['count']])
        writer.writerow([])

        writer.writerow(['Counts by location'])
        writer.writerow(['location_name','count'])
        for row in loc_counts:
            writer.writerow([row['location__name'] or 'Unknown', row['count']])

        return response
    export_summary_as_csv.short_description = "Export summary CSV (counts & totals)"

@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = (
        'claimer',
        'donation_title',
        'quantity',
        'claimed_from',
        'claimed_location',
        'claimed_address',
        'expiration_date',       # <-- Added here
        'created_at'
    )
    search_fields = ('donation__title', 'claimer__username', 'donation__donor__username')

    def has_add_permission(self, request):
        return False  # hides "Add claim"
    
    def donation_title(self, obj):
        return obj.donation.title
    donation_title.short_description = 'Donation'

    def claimed_from(self, obj):
        return obj.donation.donor.username
    claimed_from.short_description = 'Claimed From'

    def claimed_location(self, obj):
        return obj.donation.location.name if obj.donation.location else '-'
    claimed_location.short_description = 'Claimed Location'

    def claimed_address(self, obj):
        return obj.donation.address
    claimed_address.short_description = 'Claimed Address'

    # NEW: Expiration date display column
    def expiration_date(self, obj):
        return obj.donation.expiry_date
    expiration_date.short_description = "Expirey Date"

    actions = ["export_selected_as_csv", "export_summary_as_csv"]

    def export_selected_as_csv(self, request, queryset):
        """
        Export selected Claim rows as CSV with sensible columns.
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=claims_selected.csv'
        writer = csv.writer(response)

        # Header
        writer.writerow(['Claimer', 'Donation', 'Quantity', 'Location', 'Address', 'Expiration Date', 'Claimed At'])

        # Rows
        for obj in queryset.select_related('claimer', 'donation', 'donation__location'):
            writer.writerow([
                obj.claimer.username if obj.claimer else '',
                obj.donation.title if obj.donation else '',
                obj.quantity,
                obj.donation.location.name if obj.donation and obj.donation.location else '',
                obj.donation.address if obj.donation else '',
                obj.donation.expiration_date if obj.donation else '',
                obj.created_at.isoformat() if obj.created_at else '',
            ])
        return response
    export_selected_as_csv.short_description = "Export selected claims to CSV"

    def export_summary_as_csv(self, request, queryset):
        """
        Export aggregated summary: counts by donation and totals for selected claims.
        """
        qs = queryset if queryset.exists() else Claim.objects.all()

        # Aggregations
        donation_counts = qs.values('donation__title').annotate(total_claims=Count('id')).order_by('-total_claims')
        total_quantity = qs.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=claims_summary.csv'
        writer = csv.writer(response)

        writer.writerow(['Summary of Claims'])
        writer.writerow([])
        writer.writerow(['Total Quantity Claimed', total_quantity])
        writer.writerow([])
        writer.writerow(['Counts by Donation'])
        writer.writerow(['Donation', 'Number of Claims'])

        for row in donation_counts:
            writer.writerow([row['donation__title'] or 'Unknown', row['total_claims']])

        return response
    export_summary_as_csv.short_description = "Export summary CSV (counts & totals)"
