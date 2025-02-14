from django.shortcuts import render

from django.http import HttpResponse
from rango.models import Category
from rango.models import Page 
from rango.forms import CategoryForm
from django.shortcuts import redirect
from rango.forms import PageForm 
from django.urls import reverse
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required 
from datetime import datetime 


def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    
    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list
    
    visitor_cookie_handler(request)
    
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

@login_required 
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

@login_required
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
    
    context_dict = {}
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']

    return render(request, 'rango/about.html', context=context_dict)
    
def register(request): 
    #A boolean value for telling the template whether registration was successful
    # set to false at first. code changes value to true when registration is sucessful 
    registered = False 

    #If an HTTP Post, we're interested in processing form data 
    if request.method =='POST': 
        #attempt to grab info from raw form information
        # note that we make use of both UserForm and UserProfileForm
        user_form = UserForm(request.POST) 
        profile_form = UserProfileForm(request.POST) 

        #if two forms are valid...
        if user_form.is_valid() and profile_form.is_valid(): 
            #save user's form data to the database
            user = user_form.save() 

            #now hash password with set_password method 
            #once hashed, we can update user object 
            user.set_password(user.password) 
            user.save() 
            
            #now sort out the userprofile instance, since we need to set user attribute to ourselves, we commit_false, this delays 
            # saving the model until we're ready to avoid integrity problems
            profile = profile_form.save(commit=False) 
            profile.user = user
            #Did the user provide a profile picture? 
            #if so , we need to get it from input form and put in the UserProfile model 
            if 'picture' in request.FILES: 
                profile.picture = request.FILES['picture']

            #Now we save UserProfile model instance 
            profile.save() 

            #update our variable to indicate that template registartion was successful 
            registered = True 

        else: 
            print(user_form.errors, profile_form.errors)


    else: 
        #not an HTTP Post, so we render our form using two ModelForm instances. these forms will be blank and ready for user input 
        user_form = UserForm() 
        profile_form = UserProfileForm() 

    #render thhe template depending on the context 
    return render(request, 'rango/register.html', context = {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})


def user_login(request):
    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        # We use request.POST.get('<variable>') as opposed
        # to request.POST['<variable>'], because the
        # request.POST.get('<variable>') returns None if the
        # value does not exist, while request.POST['<variable>']
        # will raise a KeyError exception.
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid- a User object is returned if it is.
        user = authenticate(username=username, password=password)
        
        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                # An inactive account was used- no logging in!
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    
    # The request is not a HTTP POST, so display the login form.          
    # this scenario would most likely be a HTTP GET 
    else: 
        #No context variables to pass to template system, so the blank dic object 
        return render(request, 'rango/login.html') 
    

@login_required 
def user_logout(request): 
    #since we know user logged in, we can now just log them out
    logout(request)
    # Take the user back to the homepage. 
    return redirect(reverse('rango:index'))



@login_required
def restricted(request): 
    return render(request,'rango/restricted.html')


# A helper method
def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request,'last_visit', str(datetime.now()))
    
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')
    
    # If it's been more than a day since the last visit...
    if (datetime.now()- last_visit_time).days > 0:
        visits = visits + 1
        # Update the last visit cookie now that we have updated the count
        request.session['last_visit'] = str(datetime.now())
    else:
        # Set the last visit cookie
        request.session['last_visit'] = last_visit_cookie
    # Update/set the visits cookie
    request.session['visits'] = visits