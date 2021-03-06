from django import forms
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
import json
import urllib
from archive.models import Strain
import blaster.search
import blaster.searchUtils


class BlastSearchForm(forms.Form):

    query_string = forms.CharField(required = True)
    blast_type = forms.CharField(max_length = 2, required = True)
    blast_parameters = forms.CharField(required = False)

    def process(self, request):

        cleaned_query_string = self.cleaned_data["query_string"]
        cleaned_blast_type = self.cleaned_data["blast_type"]
        cleaned_blast_parameters = self.cleaned_data["blast_parameters"]
        
        blast_success = False
        blast_output = None
        
        if cleaned_blast_type == "N":

            try:

                blast_output = blaster.search.ncbi_blast_n("nt", cleaned_query_string)
            
            except ValueError as e:

                if "Message ID#24" in str(e):

                    messages.error(request, "Protein FASTA provided for nucleotide sequence.")
            
            else:

                blast_success = True
        
        elif cleaned_blast_type == "P":
            
            try:

                blast_output = blaster.search.ncbi_blast_p("nt", cleaned_query_string)
        
            except ValueError as e:

                if "Message ID#24" in str(e):

                    messages.error(request, "Nucleutide FASTA provided for protein sequence.")
            
            else:

                blast_success = True

        else:

            messages.error(request, "Unknown BLAST Type.")
        
        return blast_output
    
    def process_errors(self, request):

        error_dict = json.loads(self.errors.as_json())
        for key in error_dict:
            for error in error_dict[key]:
                messages.error(request, "Error: %s - %s" % (key, error["message"]))



class SearchParameterForm(forms.Form):

    selected_family_ids = forms.CharField(max_length = None, required = False)
    selected_genus_ids = forms.CharField(max_length = None, required = False)
    selected_species_ids = forms.CharField(max_length = None, required = False)

    def process(self, request):

        cleaned_family_ids = self.cleaned_data["selected_family_ids"]
        cleaned_genus_ids = self.cleaned_data["selected_genus_ids"]
        cleaned_species_ids = self.cleaned_data["selected_species_ids"]
        
        families_list = []
        genera_list = []
        species_list = []

        # for family in cleaned_family_ids.split(","):

        #     try:

        #         selected_family = Family.objects.get(pk = family)
            
        #     except Famiy.DoesNotExist:

        #         pass
            
        #     else:

        #         families_list.append(selected_family)

        # for genus in cleaned_genus_ids.split(","):

        #     try:

        #         selected_genus = Genus.objects.get(pk = genus)
            
        #     except Genus.DoesNotExist:

        #         pass
            
        #     else:

        #         genera_list.append(selected_genus)
        
        # for species in cleaned_species_ids.split(","):

        #     try:

        #         selected_species = Species.objects.get(pk = species)

        #     except Species.DoesNotExist:

        #         pass
            
        #     else:

        #         species_list.append(selected_species)

        
        strains = []

        # for strain in Strain.objects.all():

        #     if strain.family in families_list and strain.genus in genera_list and strain.species in species_list:

        #         strains.append({"name": strain.name, "pk": strain.pk})
        
        request.session["search_results"] = None
        request.session["search_results"] = strains
        
    
    def process_errors(self, request):

        error_dict = json.loads(self.errors.as_json())
        for key in error_dict:
            for error in error_dict[key]:
                messages.error(request, "Error: %s - %s" % (key, error["message"]))