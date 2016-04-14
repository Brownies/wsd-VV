# views.py for VidyaVortex project 2015-2016

import json
import uuid
from hashlib import md5
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.core import mail
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Min
from django.http import HttpResponse, Http404, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.utils.datastructures import MultiValueDictKeyError

from DataVortex.forms import RegisterForm, UploadForm, PurchaseForm, BoolForm, EditForm
from DataVortex.models import Game, MyGame, Highscore, Purchase, Verification
from VidyaVortex.settings import SELLER_ID, SELLER_KEY, LOCATION_URL


# function to check whether request.user is developer
# return value of this function is often passed as a context variable to templates in order to render it correctly
def isdev(request):
    try:
        return request.user.groups.filter(name='developers').exists()
    except ObjectDoesNotExist:
        return False


# function to check whether request.user is owner of the game spesified by game_id
def isowner(request, game_id):
    try:
        game = Game.objects.get(id=game_id)
        return MyGame.objects.filter(player=request.user).filter(game=game).exists()
    except ObjectDoesNotExist:
        return False


# function to check whether request.user is both developer and the owner of the game
# in other words, whether he has the right to delete this game
def can_delete(request, game_id):
    return isowner(request, game_id) == isdev(request) == True


# display homepage template
def home(request):
    if request.method == 'GET':
        return render(request, 'DataVortex/homepage.html', {'isDev': isdev(request)})


# display browse.html template
def browse(request):
    if request.method == 'GET':
        return render(request, 'DataVortex/browse.html', {'isDev': isdev(request)})


# display highscores.html template
def highscores(request):
    if request.method == 'GET':
        return render(request, 'DataVortex/highscores.html', {'isDev': isdev(request)})


# display faqpage template
def faq(request):
    if request.method == 'GET':
        return render(request, 'DataVortex/faq.html', {'isDev': isdev(request)})


# register a new user with data submitted with form
def register(request):
    # Handle sent form data
    if request.method == 'POST':

        # store post data to 'form' object
        form = RegisterForm(request.POST)

        # check if form data is valid
        if form.is_valid():
            data = form.cleaned_data

            # check if password was typed correctly
            if data['password'] == data['password2']:

                # check if the input username already exists in database
                if User.objects.filter(username=data['username']).count() == 0:

                    # check if the input email address already exists in database
                    if User.objects.filter(email=data['email']).count() == 0:

                        # All ok! --> create new user
                        user = User.objects.create_user(data['username'], data['email'], data['password'])

                        # set the new user to the right user group
                        if data['developer'] == 'dev':
                            group, created = Group.objects.get_or_create(name='developers')
                        # add the registered user to developers' group

                        else:
                            group, created = Group.objects.get_or_create(name='players')
                        # add the registered user to players' group

                        user.groups.add(group.pk)
                        user.save()

                        # generate email verification token
                        ver_str = data["email"] + "VidyaVortex" + data["username"]
                        ver_token = md5(ver_str.encode("utf-8")).hexdigest()

                        apikey = uuid.uuid4().hex
                        ver = Verification.objects.create(user=user, apikey=apikey)
                        ver.save()

                        # send email verification link to user's email address (or in this demo case, to Django console)
                        with mail.get_connection() as connection:
                            subject = "VidyaVortex account verification"
                            body = "Click this link to verify your account:\nhttp://" + LOCATION_URL +\
                                   "/verify?token=" + ver_token + "&username=" + data["username"] +\
                                   "\nYour apikey is. " + apikey

                            mail.EmailMessage(subject, body, "verify@vidyavortex", [data["email"]],
                                              connection=connection).send()

                        state = 1  # registration successful
                    else:
                        state = 5  # email address already taken
                else:
                    state = 4  # username already taken
            else:
                state = 3  # password confirmation failed
        else:
            state = 2  # form data invalid

    # initialize new empty form
    elif request.method == 'GET':
        form = RegisterForm()  # new empty form
        state = 0  # do not display registration information

    # render the register page according to dict variables and send HttpResponse
    return render(request, 'DataVortex/register.html', {'form': form, 'state': state, 'isDev': isdev(request)})


# view to verify user's email
# email has been sent to user containing link with valid token to this view
def verify(request):
    data = request.GET
    if "token" not in data or "username" not in data:
        return HttpResponseBadRequest()
    if not User.objects.filter(username=data["username"]).exists():
        raise Http404("No such user")

    token = data["token"]
    u = User.objects.get(username=data["username"])

    ver_str = u.email + "VidyaVortex" + u.get_username()
    ver_token = md5(ver_str.encode("utf-8")).hexdigest()
    if token != ver_token:
        raise Http404("Invalid token")
    u.verification.verified = True
    u.verification.save()
    return HttpResponse("<h1>Verification succesful!</h1>")


# game service view, returns playgame.html with context variables
@login_required(login_url="login")
def playgame(request, game_id):
    if request.method == 'GET':

        try:
            game = Game.objects.get(id=game_id)

        except Game.DoesNotExist:
            raise Http404()

        context = {'game_url': game.url,
                   'game_name': game.name,
                   'game_id': game_id,
                   'isDev': isdev(request)}
        try:
            my_games = MyGame.objects.filter(player=request.user)
            my_games.get(game=game)
        except ObjectDoesNotExist:
            # user needs to purchase this game first
            if not isdev(request):  # devs can't purchase games
                return redirect("purchase", game_id)
            else: 
                return redirect("homepage")

        # most of game service functionality is implemented in the template (JavaScript)
        # and ajax view with JSON communication
        return render(request, 'DataVortex/playgame.html', context)

    return redirect("homepage")


# view to handle ajax requests, a lot of this website's functionality is based on this view
def ajax(request):

    # make sure XmlHttpRequest header is included in the request
    if request.is_ajax():

        # only accept post method
        if request.method == 'POST':

            # extract the payload from the HTTP request in JSON format
            jsondata = json.loads(request.body.decode('utf-8'))
            game_id = jsondata['game_id']
            jsondata = jsondata['data']

            # check message type
            try: 
                mtype = jsondata['messageType']
            except KeyError:
                return HttpResponse(json.dumps({'messageType': 'ERROR', 'info': 'Unidentified request!'}),
                                    content_type="application/json")

            # the request associated to spesific game
            if game_id > 0:

                # user must be logged in
                if request.user.is_authenticated():

                    # access current user's game collection and find active game
                    try:
                        my_games = MyGame.objects.filter(player=request.user)
                        current_game = Game.objects.get(id=game_id)
                        my_game = my_games.get(game=current_game)
                    except ObjectDoesNotExist:
                        return HttpResponse(json.dumps({'messageType': 'ERROR', 'info': 'Game data not found!'}),
                                            content_type="application/json")

                    # request to save score to the server was sent
                    if mtype == 'SCORE':
                        try:
                            score = jsondata['score']
                        except KeyError:
                            return HttpResponse(json.dumps({'messageType': 'ERROR',
                                                            'info': 'Failed to save highscore!'}),
                                                content_type="application/json")

                        scores = []

                        # only save relevant scores, i.e. ones that are higher than zero
                        if score > 0:
                            # create new highscore object
                            highscores = my_game.highscore_set
                            lowest_score_value = highscores.aggregate(Min('value'))
                            newhighscore = Highscore(value=score, game=current_game, mygame=my_game)
                            newhighscore.save()

                            # we want to keep max 10 highscores per game for one user
                            if highscores.count() <= 10:
                                highscores.add(newhighscore)

                            # there are already 10 highscores in database,
                            # check if they are all bigger than the submitted one
                            # if not, remove the lowest existing highscore to keep the count at 10
                            elif score > lowest_score_value['value__min']:     
                                lowest_scores = highscores.filter(value=lowest_score_value['value__min'])

                                # delete only one even if there are duplicate highscores
                                for item in lowest_scores:
                                    highscores.remove(item)
                                    item.delete()
                                    break

                                highscores.add(newhighscore)

                            # they were all bigger, we won't bother to add this one...
                            else: 
                                newhighscore.delete()

                            # save highscores in scores array
                            for hscore in highscores.all():
                                scores.append(hscore.value)

                            # all good, message frontend of successful save operation
                            return HttpResponse(json.dumps({'messageType': 'SCORE_SAVED', 'highScores': scores}),
                                                content_type="application/json")

                        # special score value that indicates the client has requested highscores data
                        elif score == -1:
                            highscores = my_game.highscore_set
                            for hscore in highscores.all():
                                scores.append(hscore.value)
                            return HttpResponse(json.dumps({'messageType': 'SCORES_REQUESTED', 'highScores': scores}),
                                                content_type="application/json")

                        # tell user to try harder before posting highscores
                        else:
                            return HttpResponse(json.dumps({'messageType': 'ERROR',
                                                            'info': 'Score needs to be greater than zero!'}),
                                                content_type="application/json")

                    # request to save game state to the server was sent  
                    elif mtype == 'SAVE':

                        # extract gamestate data from request
                        try:
                            gamestate = jsondata['gameState']
                        except KeyError:
                            return HttpResponse(json.dumps({'messageType': 'ERROR', 'info': 'Failed to save game!'}),
                                                content_type="application/json")

                        if gamestate:
                            # Save game state to the database
                            my_game.gamestate = gamestate
                            my_game.save()
                        else:
                            return HttpResponse(json.dumps({'messageType': 'ERROR', 'info': 'Failed to save game!'}),
                                                content_type="application/json")

                        return HttpResponse(json.dumps({'messageType': 'GAME_SAVED',
                                                        'gameState': gamestate['playerItems']}),
                                            content_type="application/json")

                    # request to load previous game state from the server was sent
                    elif mtype == 'LOAD_REQUEST':

                        # load game state from the database
                        # replace single quotes with double ones so json.loads() works
                        jsonstr = my_game.gamestate.replace("'", "\"")
                        gamestate = json.loads(jsonstr)

                        if gamestate:
                            return HttpResponse(json.dumps({'messageType': 'GAME_LOADED', 'gameState': gamestate}),
                                                content_type="application/json")
                        else: 
                            return HttpResponse(json.dumps({'messageType': 'ERROR', 'info': 'Failed to load game!'}),
                                                content_type="application/json")

                    # request to save rating given by user was sent
                    elif mtype == 'RATE':

                        # developer can't rank his own game
                        if not isdev(request):

                            # extract rating data from request
                            try:
                                rate = jsondata['rate']
                            except KeyError:
                                return HttpResponse(json.dumps({'messageType': 'ERROR',
                                                                'info': 'Failed to rate game!'}),
                                                    content_type="application/json")

                            # user can rate each game only once
                            if not my_game.rated:

                                # rating change can only be 1 or -1
                                if abs(rate) == 1:

                                    # change rating
                                    current_game.rating += rate
                                    current_game.save()

                                    # make sure one can rate each game only once
                                    my_game.rated = True
                                    my_game.save()

                                else:    
                                    return HttpResponse(json.dumps({'messageType': 'INVALID_RATING'}),
                                                        content_type="application/json")

                            else:
                                return HttpResponse(json.dumps({'messageType': 'ALREADY_RATED'}),
                                                    content_type="application/json")

                            return HttpResponse(json.dumps({'messageType': 'GAME_RATED'}),
                                                content_type="application/json")

                        else:
                            return HttpResponse(json.dumps({'messageType': 'ERROR',
                                                            'info': 'Developer cannot rank his own game!'}),
                                                content_type="application/json")

                    # message type unidentified    
                    else:
                        return HttpResponse(json.dumps({'messageType': 'ERROR', 'info': 'Unidentified request!'}),
                                            content_type="application/json")

            else:
                # request info about all games visible to current user
                if mtype == 'GLOBAL_GAME_LIST':
                    ordering = ""

                    # extract ordering preference from request
                    try:
                        ordering = jsondata['ordering']
                    except KeyError:
                        pass

                    # get all game objects in prefered order
                    if ordering == "RELEASE_DATE":
                        games = Game.objects.all().order_by('-time')
                    elif ordering == "RATING":
                        games = Game.objects.all().order_by('-rating')
                    else:
                        games = Game.objects.all()

                    # initialize response data structure
                    allgames = [None]*games.count()

                    # user is logged in --> give all info
                    if request.user.is_authenticated():

                        # populate response with data from database
                        for index, game in enumerate(games):

                            # parse time, leave milliseconds out
                            time = str(game.time).split('.')[0]
                            try:
                                allgames[index] = {
                                                'id': game.id, 
                                                'name': game.name,  
                                                'description': game.description,
                                                'isyourgame': isowner(request, game.id),
                                                'time': time, 
                                                'rating': game.rating,
                                                'candelete': can_delete(request, game.id),
                                                'buycount': game.buycount,
                                                'price': str(game.price),
                                                'thumbnail': game.thumbnail
                                }
                            except ValueError:
                                allgames[index] = {
                                                'id': game.id,
                                                'name': game.name,  
                                                'description': game.description,
                                                'isyourgame': isowner(request, game.id),
                                                'time': time, 
                                                'rating': game.rating,
                                                'candelete': can_delete(request, game.id),
                                                'buycount': game.buycount,
                                                'price': str(game.price)
                                }

                    # user is not logged in --> restrict given info
                    else:

                        # populate response with data from database
                        for index, game in enumerate(games):  

                            # parse time, leave milliseconds out
                            time = str(game.time).split('.')[0]
                            try:
                                allgames[index] = {
                                                'id': game.id, 
                                                'name': game.name,  
                                                'description': game.description,
                                                'time': time, 
                                                'rating': game.rating, 
                                                'thumbnail': game.thumbnail
                                }
                            except ValueError:
                                allgames[index] = {
                                                'id': game.id, 
                                                'name': game.name,  
                                                'description': game.description,
                                                'time': time, 
                                                'rating': game.rating 
                                }

                    return HttpResponse(json.dumps(allgames), content_type="application/json")

                # request info about all highscores visible to current user
                elif mtype == 'GLOBAL_HIGHSCORE_LIST':

                    # fetch all highscore objects, if there are any
                    try:
                        Highscore.objects.all()
                    except Highscore.DoesNotExist:
                        return HttpResponse(json.dumps({'messageType': 'ERROR', 'info': 'No Highscores exist!'}),
                                            content_type="application/json")

                    # try to get global highscore data
                    try:
                        gamenames = [] 

                        all_games = Game.objects.all()
                        # initialize arrays
                        # 2D array for all players with highscores for each game
                        all_players = [[] for x in range(all_games.count())]  # 2D array for all hiscores for each game
                        all_highscores = [[] for x in range(all_games.count())]  # indices match in both arrays

                        for i, agame in enumerate(all_games):

                            gamenames.append([agame.name, agame.thumbnail])

                            for j, hs in enumerate(agame.highscore_set.all()):

                                if len(all_highscores[i]) >= 10:
                                    break
                                else:
                                    all_players[i].append(hs.mygame.player.username)
                                    all_highscores[i].append(hs.value)

                        globalhighscoredata = {
                            'games': gamenames,
                            'players': all_players,
                            'scores': all_highscores
                        }

                    # some object was not found
                    except ObjectDoesNotExist:
                        return HttpResponse(json.dumps({'messageType': 'ERROR',
                                                        'info': 'Can\'t find global highscores!'}),
                                            content_type="application/json")

                    # if user is logged in --> try to get personal highscore data
                    # same process as with global highscore data except there is no player name array
                    if request.user.is_authenticated():
                        try:
                            # get all games owned by user
                            usergames = MyGame.objects.filter(player=request.user)
                            usergamenames = []
                            userhighscores = [[] for x in range(usergames.count())]

                            for i, ugame in enumerate(usergames):
                                usergamenames.append([ugame.game.name, ugame.game.thumbnail])
                                for j, hs in enumerate(ugame.highscore_set.all()):
                                    userhighscores[i].append(hs.value)

                            yourhighscoredata = {
                                'games': usergamenames,
                                'scores': userhighscores
                            }

                        # some object was not found
                        except ObjectDoesNotExist:
                            return HttpResponse(json.dumps({'messageType': 'ERROR',
                                                            'info': 'Can\'t find personal highscores!'}),
                                                content_type="application/json")

                    # user was not logged in, initialize empty dict for personal data
                    else:
                        yourhighscoredata = {}

                    # combine global and personal highscore data and return them in json format
                    return HttpResponse(json.dumps({'global': globalhighscoredata, 'user': yourhighscoredata}),
                                        content_type="application/json")

                # message type unidentified
                else:
                    return HttpResponse(json.dumps({'messageType': 'ERROR', 'info': 'Unidentified request!'}),
                                        content_type="application/json")

    # the HTTP request was not ajax or sent with POST-method --> Redirect to homepage   
    return redirect("homepage")


# view for developers to add new game to server database
@login_required(login_url="login")
def addgame(request):
    index = 0  # needed to determine new game's id
    state = 0  # condition variable for success message

    if not request.user.verification.verified:
            return HttpResponseForbidden("You are not verified yet. Verify your email to add games.")

    # user needs to be developer
    if isdev(request):

        # post method was used --> handle sent form data
        if request.method == 'POST':

            # extract form data
            form = UploadForm(request.POST)

            # validate form
            if form.is_valid():

                data = form.cleaned_data

                # find lowest free positive integer for new game id
                for i in range(1, Game.objects.all().count()+2):
                    try:  
                        Game.objects.get(id=i)
                    except Game.DoesNotExist:
                        index = i
                        break

                # create new game object with form data
                newgame = Game(id=index, name=data['name'], url=data['url'],
                               description=data['description'], price=data['price'],
                               thumbnail=data['thumbnail'])

                # save it to database
                newgame.save()

                # create MyGame object for the user. This object links the Game and User object together 
                # this means the user now owns this game
                MyGame.objects.create(player=request.user, game=newgame)

                # tell template that success message should be displayed
                state = 1

        # get method was used, initialize an empty form
        else: 
            form = UploadForm()

        return render(request, 'DataVortex/addgame.html', {'form': form, 'state': state, 'isDev': isdev(request),
                                                           'edit': False})

    return redirect("homepage")    


# enables player users to purchase games
@login_required(login_url="login")
def purchase(request, game_id):

    # only allow get method
    if request.method == 'GET':

        if not request.user.verification.verified:
            return HttpResponseForbidden("You are not verified yet. Verify your email to purchase games.")

        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            raise Http404("Game doesn't exist")

        # user has already purchased this game --> redirect to playgame view
        if isowner(request, game_id):
            return redirect("playgame", game_id)

        # devs can't buy games 
        if isdev(request):
            return redirect("browse")

        user = request.user
        game_name = game.name
        price = str(game.price)

        # create new Purchase object
        p = Purchase.objects.create(amount=price, buyer=user, game=game)
        purchase_id = p.id

        # generate checksum for payment service
        checksumstr = "pid={}&sid={}&amount={}&token={}".format(purchase_id, SELLER_ID, price, SELLER_KEY)
        m = md5(checksumstr.encode("ascii"))
        checksum = m.hexdigest()

        """
        print("str:" + checksumstr)
        print("checksum:" + checksum)
        print(LOCATION_URL + "/purchase_succesful")
        """

        # create a bound form to be sent to the payment service
        formdata = {
            "pid": purchase_id,
            "sid": SELLER_ID,
            "amount": price,
            "success_url": "http://" + LOCATION_URL + "/purchase_successful",
            "cancel_url": "http://" + LOCATION_URL + "/purchase_failed",
            "error_url": "http://" + LOCATION_URL + "/purchase_failed",
            "checksum": checksum
        }
        form = PurchaseForm(formdata)

        # define render context variables
        context = {
            "form": form, 
            "price": price, 
            "game_name": game_name, 
            "game_id": game_id, 
            "isDev": isdev(request), 
            "state": 1,
            "rating": game.rating,
            "img_url": game.thumbnail
        }
        return render(request, "DataVortex/purchase.html", context)


# a view to handle failed purchases, displays error messages
@login_required(login_url="login")
def purchase_failed(request):
    if request.method == "GET":
        data = request.GET
        try:
            p = Purchase.objects.get(id=data["pid"])
        except MultiValueDictKeyError:  # someone probably just typed ourdomain.com/purchase_failed/ in url bar
            return redirect("homepage")

        # purchase failed so delete the now obsolete Purchase model created in purchase view
        p.delete()
        s = ""
        if data["result"] == "cancel":
            s = "User cancelled payment"
        elif data["result"] == "error":
            s = "Payment service error"

        context = {
            'isDev': isdev(request),
            'state': 2,
            'errmsg': s
        }

        return render(request, "DataVortex/purchase.html", context)


# a view to handle successful purchases, displays success messages
@login_required(login_url="login")
def purchase_successful(request):
    if request.method == "GET":
        data = request.GET
        try:
            p = Purchase.objects.get(id=data["pid"])
        except MultiValueDictKeyError:  # someone probably just typed ourdomain.com/purchase_successful/ in url bar
            return redirect("homepage")

        # make the purchase valid so it is displayed in sales statistics 
        # and is not deleted by the 'python manage.py purchase_cleanup' command
        p.valid = True
        p.save()
        buyer = p.buyer
        game = p.game
        game.buycount += 1  # increase game buycount
        game.save()
        MyGame.objects.create(player=buyer, game=game)  # add the game to buyer's inventory

        context = {
            'isDev': isdev(request), 
            'state': 3
        }

        return render(request, "DataVortex/purchase.html", context)


# completely delete a game from database
@login_required(login_url="login")
def delete(request, game_id):
    # only devs can delete games
    if isdev(request):
        
        if request.method == "POST":

            form = BoolForm(request.POST)

            # check if form data is valid
            if form.is_valid():

                if form.cleaned_data['accept']:

                    try:
                        game = Game.objects.get(id=game_id)
                    except Game.DoesNotExist:
                        raise Http404("Game doesn't exist")

                    try:
                        mygames = MyGame.objects.filter(game=game)
                        mygames.get(player=request.user)
                    except ObjectDoesNotExist:
                        # current user doesn't own this game, so he cannot delete it
                        return redirect("browse")

                    try:
                        # delete all highscores related to this game, if there are any
                        highscores = game.highscore_set.all()
                        highscores.delete()
                    except highscores.DoesNotExist:
                        pass

                    try:
                        # delete all purchases related to this game, if there are any
                        purchases = Purchase.objects.filter(game=game)
                    except ObjectDoesNotExist:
                        pass

                    mygames.delete()  # delete all ownerships related to this game
                    purchases.delete()  # delete all purchases related to this game

                    """
                    try:
                        os.remove(os.path.join(MEDIA_ROOT, game.thumbnail.name))  # delete uploaded screenshot
                    except FileNotFoundError:
                        pass 
                    """
                    game.delete()  # delete game object
        
        else:
            form = BoolForm({'accept': True})
            return render(request, 'DataVortex/delete.html', {'game_id': game_id, 'form': form,
                                                              'isDev': isdev(request)})
            
    # redirect back to browsing page
    return redirect("browse")


# developer feature to modify their already uploaded game
@login_required(login_url="login")
def editgame(request, game_id):
    state = 0
    error = 0
    
    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        raise Http404("Game doesn't exist")

    # only developer who owns this game can edit it
    if can_delete(request, game_id):

        # post method was used --> handle form data and edit game
        if request.method == 'POST':

            # get data from form
            form = EditForm(request.POST)

            # check if form data is valid
            if form.is_valid():

                data = form.cleaned_data

                if data['url'].split('://')[0] != 'https' and data['url'] != "":
                    error = 1  # not valid https url
                elif game.name != data['name'] and Game.objects.filter(name=data['name']).count() > 0:
                    error = 2  # trying to give existing game name that is not this game's old name
                elif game.url != data['url'] and Game.objects.filter(name=data['url']).count() > 0:
                    error = 3  # trying to give existing url that is not this game's old url
                else:
                    # ignore name field if its blank or the name did not change
                    if game.name != data['name'] and data['name'] != "":
                        game.name = data['name'] 

                    # ignore url field if its blank or the url did not change
                    if game.url != data['url'] and data['url'] != "":
                        game.url = data['url']      
                              
                    # try to delete old thumbnail  
                    """
                    try:
                        os.remove(os.path.join(MEDIA_ROOT, game.thumbnail.name))
                    except FileNotFoundError:
                        pass
                    """

                    # update rest of the game model
                    game.description = data['description']
                    game.price = data['price']
                    game.thumbnail = data['thumbnail']
                    
                    # and save it
                    game.save()

                    state = 2

        # get method was used --> initialise empty form and render template
        else: 
            form = EditForm()

        # set context variables for template
        context = {
            'form': form, 
            'state': state, 
            'isDev': isdev(request), 
            'edit': True, 
            'game_name': game.name, 
            'game_id': game.id,
            'error': error
        }

        return render(request, 'DataVortex/addgame.html', context)

    # user was not dev nor own the game --> he'll be on his way to homepage
    return redirect("homepage")


# this view displays sales statistics for certain game for its owner dev only
@login_required(login_url="login")
def salesinfo(request, game_id):
    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        raise Http404("Game doesn't exist")

    # only developer who owns this game can see the sales statistics for it
    if can_delete(request, game_id):

        # initialize total income variable
        totalsum = Decimal('0.00') 

        if request.method == 'GET':

            # try to get purchases for this game and count total income
            try:
                purchases = Purchase.objects.filter(game=game).order_by('-time')
                for p in purchases:
                    if p.valid:
                        totalsum += p.amount
            except Purchase.DoesNotExist:
                purchases = None

            # purchases exists --> set context accordingly
            if purchases:
                context = {
                    'purchases': purchases, 
                    'empty': False, 
                    'game': game, 
                    'totalsum': totalsum,
                    'isDev': isdev(request)
                }

            # no purchases exist --> purchase history will be left empty 
            else:
                context = {
                    'empty': True, 
                    'game': game, 
                    'totalsum': totalsum,
                    'isDev': isdev(request)
                }

            return render(request, 'DataVortex/salesinfo.html', context)

    # send non-devs and non-owners to homepage
    return redirect("homepage")


def api(request):
    if request.method != "GET":
        return HttpResponseBadRequest("Invalid request method. The api only supports GET methods")
    data = request.GET

    if "type" not in data:
        return HttpResponseBadRequest("request type missing")

    r = {}
    if data["type"] == "games":
        i = 0
        games = Game.objects.all()
        for game in games:
            i += 1
            g = {
                "sold": game.buycount,
                "description": game.description,
                "rating": game.rating,
                "price": str(game.price)
            }
            r[game.name] = g
            r["total_games"] = i

    elif data["type"] == "highscores":
        games = Game.objects.all()
        for game in games:
            hs = Highscore.objects.all().filter(game=game).first()
            g = {
                "highscore": hs.value,
                "user": hs.mygame.player.username
            }
            r[game.name] = g

    # requires api key
    elif data["type"] == "sales":
        if "id" not in data or "apikey" not in data:
            return HttpResponseBadRequest("missing game id or apikey")

        apikey = data["apikey"]
        game_id = data["id"]
        if not Game.objects.filter(id=game_id).exists():
            return HttpResponseNotFound("invalid id")
        game = Game.objects.get(id=game_id)

        if not User.objects.filter(groups="developer", verification__apikey=apikey).exists():
            return HttpResponseNotFound("invalid apikey")
        dev = User.objects.get(groups="developers", verification__apikey=apikey)

        if not MyGame.objects.filter(game=game, player=dev).exists():
            return HttpResponseForbidden("not your game")

        purchases = Purchase.objects.filter(game=game, valid=True).order_by('-time')
        total_sum = Decimal("0.00")
        if purchases.exists():
            for p in purchases:
                if p.valid:
                    total_sum += p.amount

        r["id"] = game_id
        r["total_sum"] = total_sum
        r["purchases"] = game.buycount
        r["current_price"] = game.price
        r["rating"] = game.rating

    r_json = json.dumps(r)
    response = HttpResponse(r_json, content_type="application/json")
    return response
