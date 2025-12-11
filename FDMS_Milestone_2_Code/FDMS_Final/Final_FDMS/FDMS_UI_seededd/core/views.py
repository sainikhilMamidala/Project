from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout as django_logout
from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect
from django.db.models import Sum
from django.db import models
from django.db.models import Sum
from django.db.models import Sum
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone

import csv

from .models import Donation, Location, Claim
from .forms import DonationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

from django.contrib.auth import login
from django.contrib.auth.models import Group
from .forms import DonorSignupForm, ReceiverSignupForm


def landing(request):
    return render(request, 'landing.html')

def is_donor(user):
    return user.groups.filter(name='Donor').exists()

def is_receiver(user):
    return user.groups.filter(name='Receiver').exists()

def donor_signup_view(request):
    if request.method == 'POST':
        form = DonorSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Save first_name and last_name
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            
            # Add to Donor group
            donor_group, _ = Group.objects.get_or_create(name='Donor')
            user.groups.add(donor_group)
            
            login(request, user)
            return redirect('donor_dashboard')
    else:
        form = DonorSignupForm()
    return render(request, 'donor_signup.html', {'form': form})


def receiver_signup_view(request):
    if request.method == 'POST':
        form = ReceiverSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Save first_name and last_name
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            
            # Add to Receiver group
            receiver_group, _ = Group.objects.get_or_create(name='Receiver')
            user.groups.add(receiver_group)
            
            login(request, user)
            return redirect('receiver_dashboard')
    else:
        form = ReceiverSignupForm()
    return render(request, 'receiver_signup.html', {'form': form})

def donor_login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('donor_dashboard')

    return render(request, 'donor_login.html', {'form': form})



def receiver_login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('receiver_dashboard')
    return render(request, 'receiver_login.html', {'form': form})


def logout_view(request):
    django_logout(request)
    return redirect('landing')

from django.db.models import Sum, F, Value, Case, When
from django.db.models import F, Case, When, BooleanField
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
@login_required
@user_passes_test(is_donor, login_url='/donor/login/')

def donor_dashboard(request):
    user = request.user

    # Annotate donations with claimed quantity
    donations_qs = Donation.objects.annotate(
        claimed_qty=Coalesce(Sum('claims__quantity'),0)
    )

    # -----------------------
    # Your Donations
    # Include donations not claimed OR partially claimed, even if remaining quantity deleted
    # -----------------------
    your_donations = (
    donations_qs.filter(donor=user)
    .annotate(
        fully_claimed=Case(
            When(claimed_qty__gte=F('initial_quantity'), then=True),
            default=False,
            output_field=BooleanField()
        )
    )
    .order_by('-created_at')
)

# Pagination
    from django.core.paginator import Paginator

    paginator = Paginator(your_donations, 20)
    page = request.GET.get('page', 1)
    donations = paginator.get_page(page)

    # -----------------------
    # Recycle Bin
    # Include donations that are partially or fully deleted
    # -----------------------
    deleted_donations = donations_qs.filter(
        donor=user,
        is_deleted=True
    ).order_by('-deleted_at')

    # -----------------------
    # Handle donation creation
    # -----------------------
    if request.method == 'POST':
        form = DonationForm(request.POST, user=user)
        if form.is_valid():
            d = form.save(commit=False)
            d.donor = user
            if not getattr(d, 'available_quantity', None):
                d.available_quantity = getattr(d, 'initial_quantity', None) or getattr(d, 'quantity', None)
            d.save()
            messages.success(request, "Donation created.")
            return redirect('donor_dashboard')
        else:
            for field, errs in form.errors.items():
                messages.error(request, f"{field}: {errs.as_text()}")
    else:
        form = DonationForm(user=user)

    today_iso = timezone.now().date().isoformat()
    return render(request, 'donor_dashboard.html', {
        'donations': donations,
        'deleted_items': deleted_donations,
        'form': form,
        'today_iso': today_iso
    })


@login_required
@user_passes_test(is_receiver, login_url='/receiver/login/')

@login_required
@user_passes_test(is_receiver, login_url='/receiver/login/')
def receiver_dashboard(request):
    selected_location_id = request.GET.get('location')
    locations = Location.objects.all()

    # Donations available to claim
    qs = Donation.objects.filter(
        status='available',
        expiry_date__gt=timezone.now(),
        is_deleted=False
    )

    if selected_location_id:
        try:
            qs = qs.filter(location_id=int(selected_location_id))
        except ValueError:
            pass

    nearby = qs.select_related('donor', 'location').order_by('-created_at')[:50]

    # Donations this user has claimed
    assigned = Donation.objects.filter(
        claims__claimer=request.user,
    ).prefetch_related('claims', 'claims__claimer').order_by('-created_at')

    return render(request, 'receiver_dashboard.html', {
        'locations': locations,
        'nearby': nearby,
        'assigned': assigned,
        'selected_location_id': int(selected_location_id) if selected_location_id else None,
    })


@login_required
@login_required
@login_required
def claim_donation(request, pk):
    donation = get_object_or_404(Donation, pk=pk, is_deleted=False)

    if donation.status != 'available' or (hasattr(donation, 'is_expired') and donation.is_expired()):
        messages.error(request, "Cannot claim this donation (expired or unavailable).")
        return redirect('receiver_dashboard')

    # Determine claim quantity
    if request.method == 'POST':
        qty_raw = request.POST.get('claim_qty', '0')
    else:
        qty_raw = request.GET.get('claim_qty', '1')  # fallback to 1

    try:
        claim_qty = int(qty_raw)
    except ValueError:
        messages.error(request, "Invalid claim quantity.")
        return redirect('receiver_dashboard')

    if claim_qty <= 0 or claim_qty > donation.available_quantity:
        messages.error(request, f"Cannot claim {claim_qty} units. Available: {donation.available_quantity}")
        return redirect('receiver_dashboard')

    # Record the claim and adjust available quantity atomically
    try:
        with transaction.atomic():
            d = Donation.objects.select_for_update().get(pk=donation.pk)
            Claim.objects.create(donation=d, claimer=request.user, quantity=claim_qty)

            d.available_quantity -= claim_qty
            if d.available_quantity == 0:
                d.status = 'claimed'
            d.save(update_fields=['available_quantity', 'status', 'updated_at'])

    except Exception as e:
        messages.error(request, f"Failed to claim donation: {e}")
        return redirect('receiver_dashboard')

    messages.success(request, f"Successfully claimed {claim_qty} unit(s).")
    return redirect('receiver_dashboard')

@login_required
def reject_donation(request, pk):
    d = get_object_or_404(Donation, pk=pk, is_deleted=False)
    if request.user != d.claimed_by and not request.user.is_staff:
        return HttpResponseForbidden('Not allowed')

    d.status = 'rejected'
    d.save()
    messages.success(request, 'Donation rejected.')
    if request.user == d.claimed_by:
        return redirect('receiver_dashboard')
    return redirect('donor_dashboard')


@login_required
def donor_delete_donation(request, pk):
    if request.method != "POST":
        return redirect('donor_dashboard')

    donation = get_object_or_404(Donation, pk=pk, donor=request.user, is_deleted=False)
    donation.soft_delete(user=request.user)
    messages.success(request, "Donation removed from your dashboard.")
    return redirect('donor_dashboard')

@login_required
@login_required
def delete_donation(request, pk):
    donation = get_object_or_404(Donation, pk=pk, donor=request.user, is_deleted=False)

    if request.method == "POST":
        # Soft delete the donation
        donation.soft_delete(user=request.user)
        messages.success(request, f"Donation '{donation.title}' has been deleted and moved to Recycle Bin.")
        return redirect("donor_dashboard")

    return render(request, "confirm_delete.html", {"donation": donation})

def soft_delete(self, user=None):
    if self.available_quantity is None:
        self.available_quantity = 0
    else:
        self.available_quantity = 0  # full deletion

    self.is_deleted = True
    self.deleted_at = timezone.now()
    if user is not None and hasattr(user, "pk"):
        self.deleted_by = user
    self.save(update_fields=["available_quantity", "is_deleted", "deleted_at", "deleted_by"])



@login_required
def donor_restore_donation(request, pk):
    if request.method != "POST":
        return redirect('donor_dashboard')

    donation = get_object_or_404(Donation, pk=pk, donor=request.user, is_deleted=True)
    donation.is_deleted = False
    donation.deleted_at = None
    donation.deleted_by = None
    donation.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by', 'updated_at'])
    messages.success(request, "Donation restored and visible in your dashboard.")
    return redirect('donor_dashboard')


@login_required
def reports(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Reports are available to admin only.")

    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="donations_report.csv"'
        writer = csv.writer(response)
        for d in Donation.objects.all().order_by('-created_at'):
            writer.writerow([d.pk, d.title, getattr(d.donor, 'username', ''), d.status, d.created_at])
        return response

    return render(request, 'reports.html')


def home(request):
    if request.user.is_authenticated:
        try:
            if request.user.groups.filter(name='Donor').exists():
                return redirect('donor_dashboard')
            if request.user.groups.filter(name='Receiver').exists():
                return redirect('receiver_dashboard')
        except Exception:
            pass
        if request.user.is_staff:
            return redirect('/admin/')
    return redirect('landing')
