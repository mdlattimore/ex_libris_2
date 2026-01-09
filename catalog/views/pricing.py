# catalog/views.py
from django.shortcuts import render
from catalog.forms import PricingForm
from catalog.services.pricing import net_proceeds, listing_price
from django.contrib.auth.decorators import login_required

@login_required(login_url="account_login")
def pricing_view(request):
    result = None
    result_label = None
    error = None

    if request.method == "POST":
        form = PricingForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                if cd["mode"] == PricingForm.MODE_NET:
                    result = net_proceeds(
                        price=cd["input_number"],
                        tax_rate=cd["tax_rate"],
                        shipping=cd["shipping"],
                        ebay_comm=cd["ebay_comm"],
                        xaction_fee=cd["xaction_fee"],
                    )
                    result_label = "Net proceeds"
                else:
                    result = listing_price(
                        target_net=cd["input_number"],
                        tax_rate=cd["tax_rate"],
                        shipping=cd["shipping"],
                        ebay_comm=cd["ebay_comm"],
                        xaction_fee=cd["xaction_fee"],
                    )
                    result_label = "Listing price"
            except ValueError as e:
                error = str(e)
    else:
        form = PricingForm()

    context = {
        "form": form,
        "result": round(result, 2) if result is not None else None,
        "result_label": result_label,
        "error": error,
    }
    return render(request, "catalog/pricing_calculator.html", context)
