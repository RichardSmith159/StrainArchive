# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from archive.models import Strain, Family, Genus, Species
from . forms import SearchParameterForm
import cart.utils
import json



def results(request, page_number):

    basket = cart.utils.get_basket(request)
    
    paginator = Paginator(request.session["search_results"], 25)

    page = request.GET.get("page")

    try:

        strains = paginator.page(page)
    
    except PageNotAnInteger:

        strains = paginator.page(page_number)

    except EmptyPage:

        strains = paginator.page(paginator.num_pages)


    return render(
        request,
        "search/results.html",
        {
            "strains": strains,
            "num_pages": range(paginator.num_pages),
            "basket": basket
        }
    )



def search(request):

    if request.method == "POST":

        searchParameterForm = SearchParameterForm(request.POST)

        if searchParameterForm.is_valid():

            searchParameterForm.process(request)

            return redirect("search:results", 1)

        
        else:

            searchParameterForm.process_errors(request)
    
    else:

        searchParameterForm = SearchParameterForm()



    if Family.objects.all().count() > 0:
        
        data = {"data": []}

        for family in Family.objects.all():

            data["data"].append(family.to_dict())
    
    else: 

        data = {"data": "EMPTY"}

    return render(
        request,
        "search/search.html",
        {
            "searchParameterForm": searchParameterForm,
            "data": json.dumps(data)
        }
    )





def details(request, strain_pk):

    try:

        selected_strain = Strain.objects.get(pk = strain_pk)
    
    except Strain.DoesNotExist:

        raise Http404("Can't find the strain with id %d." % strain_pk)
    
    else:
        
        return render(
            request,
            "search/details.html",
            {
                "selected_strain": selected_strain
            }
        )