from django.shortcuts import render

from django.http import HttpResponse
from rango.models import Category
from rango.models import Page 
from rango.forms import CategoryForm
from django.shortcuts import redirect
from rango.forms import PageForm 
from django.urls import reverse

def index(request): 
    
    # Query the database for a list of ALL categories currently stored.
    # Order the categories by the number of likes in descending order.
    # Retrieve the top 5 only-- or all if less than 5.
    # Place the list in our context_dict dictionary (with our boldmessage!)
    # that will be passed to the template engine.
    category_list = Category.objects.order_by('-likes')[:5]

    context_dict = {}

    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list 

    #render returns http response, applies the info given that we wanna fill in template and renders it to the user

    # page stuff 

    page_list = Page.objects.order_by('-views')[:5]
    context_dict['pages'] = page_list

    return render(request, 'rango/index.html', context=context_dict)



def show_category(request, category_name_slug):
    #Create a context dictionary which we can pass to template rendering engine
    context_dict = {}

    try: 
        #can we find a category name slug with given name?
        #if we can't, the .get() method reaises a DoesNotExist exception
        # The .get() method returns one model instance or raises and exception. 
        category = Category.objects.get(slug=category_name_slug)

        #retrieve all of the associated pages. 
        # the filter() will return a list of page objects or an empty list
        pages = Page.objects.filter(category=category)

        #add our results list to template context under name pages
        context_dict['pages'] = pages
        #we can also add the category object from databse to the context dictionary
        #We'll use this in the template to verify that category exists 
        context_dict['category'] = category 
    except Category.DoesNotExist: 
        #We get here if we didn't find the specified category. Don't do anything, the template will display the no category message for us
        context_dict['category'] = None
        context_dict['pages'] = None
    # Go render the response and return it to the client 
    return render(request, 'rango/category.html', context=context_dict)


def add_category(request):
    form = CategoryForm()

    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        
        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)
            # Now that the category is saved, we could confirm this.
            # For now, just redirect the user back to the index view.
            return redirect('/rango/')
        else:
            # The supplied form contained errors
            # just print them to the terminal.
            print(form.errors)
    # Will handle the bad form, new form, or no form supplied cases.

    # Render the form with error messages (if any).
    return render(request, 'rango/add_category.html', {'form': form})


def add_page(request, category_name_slug): 
    try: 
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist: 
        category = None 

    # you can't add a page to nonexistent Category
    if category is None: 
        return redirect('/rango/')
    
    form = PageForm()

    if request.method == 'POST': 
        form = PageForm(request.POST)

        if form.is_valid(): 
            if category: 
                page = form.save(commit=False) 
                page.category = category
                page.views = 0 
                page.save() 
            
            return redirect(reverse('rango:show_category', kwargs={'category_name_slug': category_name_slug}))
        else: 
            print(form.errors)
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)



def about(request): 
    return render(request,'rango/about.html')
    

