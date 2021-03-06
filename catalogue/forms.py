from django import forms
from .models import Product, ProductStorage, ProductIngredient, ProductClass, Category
from project_settings.models import Storage
from dal.autocomplete import ModelSelect2


class BaseForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class ProductForm(BaseForm, forms.ModelForm):
    product_class = forms.ModelChoiceField(queryset=ProductClass.objects.all(), widget=forms.HiddenInput())
    
    '''
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        widget=autocomplete.ModelSelect2(url='product-autocomplete')
    )
    '''

    class Meta:
        model = Product
        fields = ['active', 'title', 'product_class', 'sku', 'category',
                  'price', 'vendor', 'order_sku', 'price_buy', 'order_discount',
                  'safe_stock', 'unit', 'taxes_modifier',
                  ]


class OurProductFrom(ProductForm):
    class Meta:
        model = Product
        fields = ['active', 'title', 'product_class', 'sku', 'category',
                  'price', 'safe_stock', 'unit', 'taxes_modifier',
                  ]


class ProductServiceForm(ProductForm):

    class Meta:
        model = Product
        fields = ['active', 'title', 'product_class', 'sku', 'category',
                  'price', 'order_sku', 'price',
                  'taxes_modifier',
                  ]


class ProductClassForm(BaseForm, forms.ModelForm):

    class Meta:
        model = ProductClass
        fields = '__all__'


class ProductCreateForm(BaseForm, forms.ModelForm):

    class Meta:
        model = Product
        fields = ['title', 'vendor', 'sku', 'product_class']


class ProductStorageForm(BaseForm, forms.ModelForm):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), required=True, widget=forms.HiddenInput())
    storage = forms.ModelChoiceField(queryset=Storage.objects.filter(active=True), label='Αποθηκη')

    class Meta:
        model = ProductStorage
        fields = ['product', 'storage', 'priority']


class ProductStorageEditForm(ProductStorageForm):
    storage = forms.ModelChoiceField(queryset=Storage.objects.filter(active=True), label='Αποθηκη', widget=forms.HiddenInput())


class ProductIngredientForm(BaseForm, forms.ModelForm):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), required=True, widget=forms.HiddenInput())
    ingredient = forms.ModelChoiceField(queryset=Product.objects.all(),
                                        required=True,
                                        widget=ModelSelect2(url='catalogue:product_autocomplete'),
                                        label='Συστατικο'
                                        )

    class Meta:
        model = ProductIngredient
        fields = '__all__'


class CategoryForm(BaseForm, forms.ModelForm):

    class Meta:
        model = Category
        fields = ['name', 'parent']

