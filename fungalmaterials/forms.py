from django import forms
from fungalmaterials.models import Material, Species, Substrate


class DOISearchForm(forms.Form):
    doi = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter DOI'})
    )


class DOIImportForm(forms.Form):
    doi = forms.CharField(widget=forms.HiddenInput, label='Enter DOI', max_length=100)
    CHOICES = [("article", "Article"), ("review", "Review")]
    import_type = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES)

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(MaterialForm, self).__init__(*args, **kwargs)
        
        # If an article is selected, filter the species and substrate querysets
        if 'article' in self.data:
            try:
                article_id = int(self.data.get('article'))
                
                # Filter species related to the selected article
                self.fields['species'].queryset = Species.objects.filter(article__id=article_id)
                
                # Filter substrate related to the selected article
                self.fields['substrate'].queryset = Substrate.objects.filter(article__id=article_id)
                
            except (ValueError, TypeError):
                # No valid article selected, empty species and substrate querysets
                self.fields['species'].queryset = Species.objects.none()
                self.fields['substrate'].queryset = Substrate.objects.none()
        
        elif self.instance.pk:
            # When editing an existing MaterialProperty instance,
            # restrict species and substrate to those related to the associated article
            self.fields['species'].queryset = self.instance.article.species.all()
            self.fields['substrate'].queryset = self.instance.article.substrate.all()
