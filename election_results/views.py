from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum
from django.contrib import messages
from django.utils import timezone
from .models import PollingUnit, LGA, Ward, AnnouncedPuResults, Party

def index(request):
    return render(request, 'election_results/index.html')

def polling_unit_result(request):
    lgas = LGA.objects.all().order_by('lga_name')
    results = []
    selected_pu = None
    
    pu_uniqueid = request.GET.get('pu_uniqueid')
    if pu_uniqueid:
        selected_pu = get_object_or_404(PollingUnit, uniqueid=pu_uniqueid)
        results = AnnouncedPuResults.objects.filter(polling_unit_uniqueid=pu_uniqueid)
    
    context = {
        'lgas': lgas,
        'results': results,
        'selected_pu': selected_pu,
    }
    return render(request, 'election_results/polling_unit.html', context)

def lga_summed_result(request):
    lgas = LGA.objects.all().order_by('lga_name')
    results = []
    selected_lga = None
    
    lga_id = request.GET.get('lga_id')
    if lga_id:
        selected_lga = get_object_or_404(LGA, lga_id=lga_id)
        
        # Get all polling units in this LGA
        # Note: PollingUnit has lga_id field.
        # We need to sum AnnouncedPuResults for these polling units.
        # AnnouncedPuResults links to PollingUnit via polling_unit_uniqueid (which matches PollingUnit.uniqueid)
        
        # Filter PUs by LGA
        pus = PollingUnit.objects.filter(lga_id=lga_id)
        pu_uniqueids = list(pus.values_list('uniqueid', flat=True))
        # Cast to strings because AnnouncedPuResults.polling_unit_uniqueid is CharField
        pu_uniqueids = [str(uid) for uid in pu_uniqueids]
        
        # Sum results
        # We want to group by party and sum score
        results = AnnouncedPuResults.objects.filter(
            polling_unit_uniqueid__in=pu_uniqueids
        ).values('party_abbreviation').annotate(
            party_score__sum=Sum('party_score')
        ).order_by('party_abbreviation')
        
    context = {
        'lgas': lgas,
        'results': results,
        'selected_lga': selected_lga,
    }
    return render(request, 'election_results/lga_result.html', context)

def add_polling_unit_result(request):
    lgas = LGA.objects.all().order_by('lga_name')
    parties = Party.objects.all()
    
    if request.method == 'POST':
        pu_uniqueid = request.POST.get('polling_unit_uniqueid')
        entered_by = request.POST.get('entered_by_user')
        user_ip = request.META.get('REMOTE_ADDR')
        
        if pu_uniqueid:
            # Check if results already exist for this PU?
            # The prompt says "store results ... for a new polling unit".
            # It doesn't explicitly say forbid if exists, but usually we add new.
            # I'll just add new rows.
            
            for party in parties:
                score = request.POST.get(f'party_{party.partyname}')
                if score:
                    AnnouncedPuResults.objects.create(
                        polling_unit_uniqueid=pu_uniqueid,
                        party_abbreviation=party.partyname[:4], # Truncate to 4 chars to fit model field
                        party_score=score,
                        entered_by_user=entered_by,
                        date_entered=timezone.now(),
                        user_ip_address=user_ip
                    )
            
            messages.success(request, 'Results added successfully!')
            return redirect('polling_unit_result') # Redirect to view it
        else:
            messages.error(request, 'Please select a polling unit.')

    context = {
        'lgas': lgas,
        'parties': parties,
    }
    return render(request, 'election_results/add_result.html', context)

def get_wards(request, lga_id):
    wards = Ward.objects.filter(lga_id=lga_id).values('ward_id', 'ward_name').order_by('ward_name')
    return JsonResponse(list(wards), safe=False)

def get_polling_units(request, ward_id):
    # PollingUnit has ward_id
    pus = PollingUnit.objects.filter(ward_id=ward_id).values('uniqueid', 'polling_unit_name', 'polling_unit_number').order_by('polling_unit_name')
    return JsonResponse(list(pus), safe=False)
