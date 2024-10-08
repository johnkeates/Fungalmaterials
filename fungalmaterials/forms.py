from django import forms
from fungalmaterials.models import MaterialProperty, Species, Substrate


class DOILookupForm(forms.Form):
    doi = forms.CharField(label='Enter DOI', max_length=100)


class DOIImportForm(forms.Form):
    doi = forms.CharField(label='Enter DOI', max_length=100)

class MaterialPropertyForm(forms.ModelForm):
    class Meta:
        model = MaterialProperty
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(MaterialPropertyForm, self).__init__(*args, **kwargs)
        
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
