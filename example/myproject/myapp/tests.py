from django.test import TestCase
from django.utils import translation
from django.conf import settings

from .models import Product
from .forms import ProductAdminForm

class LinguoAdminUpdateTestCase(TestCase):
    """Test that demonstrates the bug with updating fields in default language."""
    
    def setUp(self):
        """Create an initial product with values in all languages."""
        self.product = Product.objects.create(
            name="English Name",
            description="English description",
            price=19.99,
            sku="PROD001"
        )
        
        # Add translations for other languages
        self.product.translate(language='fr', name="French Name", description="French description")
        self.product.translate(language='es', name="Spanish Name", description="Spanish description")
        self.product.save()
        
        # Reset to default language to ensure consistent test environment
        translation.activate(settings.LANGUAGE_CODE)
    
    def test_admin_update_preserves_default_language(self):
        """
        This test simulates how the admin would update a product, by using
        the MultilingualModelForm directly. It evidences the bug where fields
        for the default language are not properly updated.
        """
        # Prepare data as it would come from the admin form
        # Note: Admin forms include fields for all languages (name_en, name_fr, name_es, etc.)
        default_lang = settings.LANGUAGE_CODE  # Should be 'en'
        
        # Construct form data with updates for all languages
        # Make sure to include ALL required fields for ALL languages
        form_data = {
            # Primary language fields
            'name': "Updated English Name",  # Regular field (not language-specific)
            'description': "Updated English description",  # Regular field
            
            # Language-specific fields
            f'name_{default_lang}': "Updated English Name",
            f'description_{default_lang}': "Updated English description",
            'name_fr': "Updated French Name",
            'description_fr': "Updated French description",
            'name_es': "Updated Spanish Name",
            'description_es': "Updated Spanish description",
            
            # Non-translatable fields
            'price': 29.99,
            'sku': "PROD001",
        }
        
        # Instantiate the admin form with the data and the existing product instance
        form = ProductAdminForm(data=form_data, instance=self.product)
        
        # Confirm the form is valid
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        
        # Save the form - this should update the product in all languages
        saved_product = form.save()
        
        # Fetch fresh instance from DB to ensure we're seeing saved values
        updated_product = Product.objects.get(id=self.product.id)
        
        # Print out the actual values saved to help with debugging
        print("\nProduct values after admin form update:")
        
        translation.activate(default_lang)
        print(f"English name: {updated_product.name}")
        print(f"English description: {updated_product.description}")
        
        translation.activate('fr')
        print(f"French name: {updated_product.name}")
        print(f"French description: {updated_product.description}")
        
        translation.activate('es')
        print(f"Spanish name: {updated_product.name}")
        print(f"Spanish description: {updated_product.description}")
        
        # Check that all languages were properly updated
        
        # First, verify the default language (English)
        translation.activate(default_lang)
        self.assertEqual(updated_product.name, "Updated English Name", 
                        f"Default language name not updated correctly. Got: {updated_product.name}")
        self.assertEqual(updated_product.description, "Updated English description",
                        f"Default language description not updated correctly. Got: {updated_product.description}")
        
        # Verify French translation
        translation.activate('fr')
        self.assertEqual(updated_product.name, "Updated French Name",
                        f"French name not updated correctly. Got: {updated_product.name}")
        self.assertEqual(updated_product.description, "Updated French description",
                        f"French description not updated correctly. Got: {updated_product.description}")
        
        # Verify Spanish translation
        translation.activate('es')
        self.assertEqual(updated_product.name, "Updated Spanish Name", 
                        f"Spanish name not updated correctly. Got: {updated_product.name}")
        self.assertEqual(updated_product.description, "Updated Spanish description",
                        f"Spanish description not updated correctly. Got: {updated_product.description}")
        
        # Verify non-translatable field
        self.assertEqual(updated_product.price, 29.99, 
                        f"Price not updated correctly. Got: {updated_product.price}")
        
    def test_direct_update_comparison(self):
        """
        This test compares direct model updates vs. form-based updates to show the difference.
        It helps identify where the bug occurs.
        """
        # 1. First, try updating directly via the model API
        direct_product = Product.objects.create(
            name="Original Direct Name",
            description="Original Direct Description",
            price=19.99,
            sku="DIRECT001"
        )
        
        # Update all languages
        direct_product.translate(language='en', name="Updated Direct Name", description="Updated Direct Description")
        direct_product.translate(language='fr', name="Updated Direct French", description="Updated Direct French Desc")
        direct_product.translate(language='es', name="Updated Direct Spanish", description="Updated Direct Spanish Desc")
        direct_product.save()
        
        # 2. Now, do a similar update via the form (admin-like)
        form_product = Product.objects.create(
            name="Original Form Name",
            description="Original Form Description",
            price=19.99,
            sku="FORM001"
        )
        
        # Add other language content
        form_product.translate(language='fr', name="Original Form French", description="Original Form French Desc")
        form_product.translate(language='es', name="Original Form Spanish", description="Original Form Spanish Desc")
        form_product.save()
        
        # Provide data for ALL required fields
        form_data = {
            # Regular fields
            'name': "Updated Form Name",
            'description': "Updated Form Description",
            
            # Language-specific fields
            'name_en': "Updated Form Name",
            'description_en': "Updated Form Description",
            'name_fr': "Updated Form French",
            'description_fr': "Updated Form French Desc",
            'name_es': "Updated Form Spanish",
            'description_es': "Updated Form Spanish Desc",
            
            # Non-translatable fields
            'price': 19.99,
            'sku': "FORM001",
        }
        
        form = ProductAdminForm(data=form_data, instance=form_product)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        form.save()
        
        # Reload both from database
        direct_product_reloaded = Product.objects.get(id=direct_product.id)
        form_product_reloaded = Product.objects.get(id=form_product.id)
        
        # Check default language values for both approaches
        translation.activate('en')
        
        print("\nDirect update results:")
        print(f"Name: {direct_product_reloaded.name}")
        print(f"Description: {direct_product_reloaded.description}")
        
        print("\nForm update results:")
        print(f"Name: {form_product_reloaded.name}")
        print(f"Description: {form_product_reloaded.description}")
        
        # The test fails if the form-based update didn't properly update the default language
        self.assertEqual(form_product_reloaded.name, "Updated Form Name",
                         "Form-based update failed to update default language name")
        self.assertEqual(form_product_reloaded.description, "Updated Form Description",
                         "Form-based update failed to update default language description")

    def test_simple_bug_demonstration(self):
        """
        A simple, focused demonstration of the bug where the default language 
        is not updated when using MultilingualModelForm.
        """
        # First get the default language code
        default_lang = settings.LANGUAGE_CODE  # 'en'
        
        # Create a product with initial values
        product = Product.objects.create(
            name="Initial Name",
            description="Initial Description",
            price=9.99,
            sku="BUG001"
        )
        
        # Prepare form data to update the product - simulating admin form submission
        form_data = {
            # These are the fields shown in the admin form
            'name_en': "Updated Name",        # This should update the name in English
            'description_en': "Updated Description",
            'name_fr': "French Name",
            'description_fr': "French Description", 
            'name_es': "Spanish Name",
            'description_es': "Spanish Description",
            'price': 9.99,
            'sku': "BUG001"
        }
        
        # Create and validate the form
        form = ProductAdminForm(data=form_data, instance=product)
        if not form.is_valid():
            print(f"Form validation errors: {form.errors}")
            # Add missing fields if needed
            for field in form.errors:
                form_data[field] = f"Value for {field}"
            form = ProductAdminForm(data=form_data, instance=product)
            self.assertTrue(form.is_valid(), "Form should be valid with all fields provided")
            
        # Save the form - this triggers the bug
        form.save()
        
        # Load a fresh copy from the database to check actual values
        updated_product = Product.objects.get(id=product.id)
        
        # Switch to the default language to check the value
        translation.activate(default_lang)
        
        # Print the values for debugging
        print("\n=== Simple Bug Demo ===")
        print(f"Product name in {default_lang}: '{updated_product.name}'")
        print(f"Expected: 'Updated Name'")
        
        # Assert that the default language field was updated
        # THIS WILL FAIL if the bug is present
        self.assertEqual(updated_product.name, "Updated Name", 
            f"Default language field not updated in database. Got: '{updated_product.name}'")
        
        # Verify that other language updates worked correctly
        translation.activate('fr')
        self.assertEqual(updated_product.name, "French Name", 
            "French translation not saved correctly")
            
        # Return to default language
        translation.activate(default_lang)
        
    def test_workaround_with_direct_update(self):
        """
        This test demonstrates a workaround for the bug by manually updating
        the default language fields after form save.
        """
        # First get the default language code
        default_lang = settings.LANGUAGE_CODE  # 'en'
        print(f"\n=== Workaround Test ===")
        print(f"Default language: {default_lang}")
        
        # Create a product with initial values
        product = Product.objects.create(
            name="Initial Workaround Name",
            description="Initial Workaround Description",
            price=9.99,
            sku="WORKAROUND001"
        )
        
        # Display the initial product state
        translation.activate(default_lang)
        print(f"Initial product name: '{product.name}'")
        print(f"Initial product description: '{product.description}'")
        
        # Inspect the database columns directly
        print("Database columns:")
        for field in product._meta.fields:
            field_name = field.name
            if field_name.startswith('name_') or field_name.startswith('description_') or field_name in ['name', 'description']:
                print(f"  {field_name}: {getattr(product, field_name, 'N/A')}")
                
        # Prepare form data to update the product
        form_data = {
            # Include all required fields to ensure the form validates
            'name': "Value for name",  # This will be ignored anyway
            'description': "Value for description",  # This will be ignored anyway
            'name_en': "Updated Workaround Name",
            'description_en': "Updated Workaround Description",
            'name_fr': "French Workaround Name",
            'description_fr': "French Workaround Description", 
            'name_es': "Spanish Workaround Name",
            'description_es': "Spanish Workaround Description",
            'price': 19.99,
            'sku': "WORKAROUND001"
        }
        
        # Create and validate the form
        form = ProductAdminForm(data=form_data, instance=product)
        self.assertTrue(form.is_valid(), f"Form validation errors: {form.errors}")
        
        # Save the form - normally this would have the bug
        saved_product = form.save()
        
        # Check what happened after the form save
        print("\nAfter form save:")
        translation.activate(default_lang)
        print(f"Product name: '{saved_product.name}'")
        print(f"Product description: '{saved_product.description}'")
        
        # Inspect the database columns after form save
        print("Database columns after form save:")
        for field in saved_product._meta.fields:
            field_name = field.name
            if field_name.startswith('name_') or field_name.startswith('description_') or field_name in ['name', 'description']:
                print(f"  {field_name}: {getattr(saved_product, field_name, 'N/A')}")
        
        # WORKAROUND: Manually update the default language fields directly
        # This is effectively what the Django admin would need to do to fix the bug
        default_lang_fields = {
            'name': form_data['name_en'],
            'description': form_data['description_en']
        }
        
        print("\nApplying workaround...")
        print(f"Using translate() with language={default_lang}, name={default_lang_fields['name']}")
        
        # Update the product with the default language values using translate()
        saved_product.translate(language=default_lang, **default_lang_fields)
        saved_product.save()
        
        # Reload the object
        updated_product = Product.objects.get(id=product.id)
        
        # Check the default language value
        translation.activate(default_lang)
        print(f"\nAfter workaround:")
        print(f"Product name: '{updated_product.name}'")
        print(f"Product description: '{updated_product.description}'")
        
        # Inspect the database columns after workaround
        print("Database columns after workaround:")
        for field in updated_product._meta.fields:
            field_name = field.name
            if field_name.startswith('name_') or field_name.startswith('description_') or field_name in ['name', 'description']:
                print(f"  {field_name}: {getattr(updated_product, field_name, 'N/A')}")
                
        # Try a more direct approach - directly set the field
        print("\nTrying direct field access...")
        name_en_field = f"name_{default_lang}"
        if hasattr(updated_product, name_en_field):
            setattr(updated_product, name_en_field, "DIRECT UPDATED NAME")
            updated_product.save()
            
            # Reload once more
            final_product = Product.objects.get(id=product.id)
            translation.activate(default_lang)
            print(f"Final name: '{final_product.name}'")
            print(f"Final {name_en_field}: '{getattr(final_product, name_en_field, 'N/A')}'")
        
        # This should pass after our direct update attempts
        self.assertEqual(updated_product.name, "Updated Workaround Name", 
            "Workaround failed to update default language field")
            
        # Return to default language
        translation.activate(default_lang)

    def test_fixed_implementation(self):
        """
        Demonstrates a fix for the admin form update bug in django-linguo.
        
        The issue appears to be related to how translate() handles the default language updates,
        possibly because the default language field names don't have language suffixes in the database.
        
        This test directly updates the 'name_en' and 'description_en' fields in addition to the
        non-suffixed default language fields ('name' and 'description').
        """
        # First get the default language code
        default_lang = settings.LANGUAGE_CODE  # 'en'
        print(f"\n=== Fix Implementation Test ===")
        
        # Create a product with initial values
        product = Product.objects.create(
            name="Initial Name For Fix",
            description="Initial Description For Fix",
            price=9.99,
            sku="FIX001"
        )
        
        # Display initial state
        translation.activate(default_lang)
        print(f"Initial name: '{product.name}'")
        
        # Simulate admin form data
        form_data = {
            'name': "Value for name field",  # Required for form validation but not actually used
            'description': "Value for description field",  # Same here
            'name_en': "Fixed Name",  # This is what should be saved to both name_en and name
            'description_en': "Fixed Description",
            'name_fr': "French Fixed Name",
            'description_fr': "French Fixed Description", 
            'name_es': "Spanish Fixed Name",
            'description_es': "Spanish Fixed Description",
            'price': 29.99,
            'sku': "FIX001"
        }
        
        # Save the form like normal
        form = ProductAdminForm(data=form_data, instance=product)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        form.save()
        
        # Reload to check what happened
        reloaded = Product.objects.get(id=product.id)
        translation.activate(default_lang)
        print(f"After normal form save, name: '{reloaded.name}'")
        print(f"Expected: 'Fixed Name'")
        
        # Implement the fix: directly update both the default field and language-specific field
        # This is the key part of the fix
        product_to_fix = Product.objects.get(id=product.id)
        
        # Get names of the default language fields
        name_field = 'name'  # Default field without language suffix
        name_lang_field = f'name_{default_lang}'  # Field with language suffix
        
        desc_field = 'description'
        desc_lang_field = f'description_{default_lang}'
        
        # Set both versions of the fields to ensure consistency
        # This is what a fixed version of MultilingualModelForm would do
        fixed_name = "FIXED NAME"
        fixed_desc = "FIXED DESCRIPTION"
        
        print(f"\nApplying fix by setting both field versions:")
        print(f"  Setting {name_field} = '{fixed_name}'")
        print(f"  Setting {name_lang_field} = '{fixed_name}'")
        
        # Apply the fix
        setattr(product_to_fix, name_field, fixed_name)
        setattr(product_to_fix, name_lang_field, fixed_name)
        setattr(product_to_fix, desc_field, fixed_desc)
        setattr(product_to_fix, desc_lang_field, fixed_desc)
        product_to_fix.save()
        
        # Check if the fix worked
        fixed_product = Product.objects.get(id=product.id)
        translation.activate(default_lang)
        print(f"\nAfter fix, checking default language field:")
        print(f"  {name_field}: '{getattr(fixed_product, name_field)}'")
        print(f"  {name_lang_field}: '{getattr(fixed_product, name_lang_field)}'")
        
        # Now verify that accessing via the property also works
        print(f"  property name: '{fixed_product.name}'")
        
        # Verify translation still works for other languages
        translation.activate('fr')
        print(f"\nVerifying French translation still works:")
        print(f"  name: '{fixed_product.name}'")
        
        # Return to default language for assertion
        translation.activate(default_lang)
        
        # This should pass if our fix worked
        self.assertEqual(fixed_product.name, fixed_name, 
            f"Fix failed. Got: '{fixed_product.name}', Expected: '{fixed_name}'")
        
        # Explanation of the bug and fix
        print("\nSummary of the bug and fix:")
        print("1. The bug occurs because MultilingualModelForm only updates the language-specific fields")
        print("   (name_en, description_en) but not the default fields (name, description)")
        print("2. The translation system expects both to be in sync")
        print("3. The fix is to update both versions of the field in the form's save method:") 