from django.core.management.base import BaseCommand

# USAGE: go to manage.py directory and open command prompt there
# type 'python manage.py modeltune' in command prompt
# your code inside handle() gets executed in django environment
# calling your_object.save() applies changes to the database

class Command(BaseCommand):
    def handle(self, **options):
        from DataVortex.models import Game, MyGame, Highscore
        from django.contrib.auth.models import User, Group
        from django.core.exceptions import ObjectDoesNotExist 
        import json
        from random import randint

        """
        other_games = Game.objects.all()
        for game in other_games:
            print(game.name)
        other_games.delete()
        """
        
        """
        # create test users
        pasi = User.objects.create_user("Meemimestari", "123", "juuhelikkas@gaymail.com") 
        lassi = User.objects.create_user("leHomo", "123", "asdfasd@gaymail.com")

        # create two test games
        worms = Game(id=9001, name="Worms", buycount=0, url="https://wormsxdxdd.com")
        worms.save()
        tetris = Game(id=9002, name="Tetris", buycount=3, url="https://tetrissxdxdd.com")
        tetris.save()

        # create user spesific game objects
        pasinworms = MyGame(game=worms, player=pasi, gamestate="")
        pasinworms.save()
        pasintetris = MyGame(game=tetris, player=pasi, gamestate="")
        pasintetris.save()

        lassinworms = MyGame(game=worms, player=lassi, gamestate="")
        lassinworms.save()
        lassintetris = MyGame(game=tetris, player=lassi, gamestate="")
        lassintetris.save()

        # create a bunch of highscores which have relation both to the Game and MyGame objects
        
        highscore1 = Highscore(value=9001, game=worms, mygame=pasinworms)
        highscore1.save()
        highscore2 = Highscore(value=101, game=worms, mygame=pasinworms)
        highscore2.save()
        highscore3 = Highscore(value=5001, game=worms, mygame=pasinworms)
        highscore3.save()

        highscore4 = Highscore(value=10001, game=tetris, mygame=pasintetris)
        highscore4.save()
        highscore5 = Highscore(value=621, game=tetris, mygame=pasintetris)
        highscore5.save()
        highscore6 = Highscore(value=501, game=tetris, mygame=pasintetris)
        highscore6.save()
        

        highscore7 = Highscore(value=1231, game=worms, mygame=lassinworms)
        highscore7.save()
        highscore8 = Highscore(value=1401, game=worms, mygame=lassinworms)
        highscore8.save()
        highscore9 = Highscore(value=542, game=worms, mygame=lassinworms)
        highscore9.save()

        highscore10 = Highscore(value=151, game=tetris, mygame=lassintetris)
        highscore10.save()
        highscore11 = Highscore(value=681, game=tetris, mygame=lassintetris)
        highscore11.save()
        highscore12 = Highscore(value=5531, game=tetris, mygame=lassintetris)
        highscore12.save()

        print("")
        print("Starting model testing...")
        print("=========================")
        print("")

        print("Current registered users: ")
        for user in User.objects.all():
            print(user.username)
        print("")
        
        # perform your model tests here:

        print("Meemimestari's Worms Highscores:")
        for hs in pasinworms.highscore_set.all():
            print(hs.value)
        print("")

        print("LeHomo's Worms Highscores:")
        for hs in lassinworms.highscore_set.all():
            print(hs.value)
        print("")

        print("Tetris Global Highscores:")
        for ghs in tetris.highscore_set.all():
            print(ghs.mygame.player.username)
            print(ghs.value)
        print("")
        
        print("Meemimestari's All Highscores:")
        pasigames = MyGame.objects.filter(player=pasi)
        for mgame in pasigames:
            print(mgame.game.name)
            for hs in mgame.highscore_set.all():
                print(hs.value)
        print("")

        dev = User.objects.get(username="devjäbä")
        print("")
        print("devjaba's games: ")
        for mg in dev.mygame_set.all():
            print(mg.game.name)
        print("")

        print("All games:")
        for g in Game.objects.all():
             print(g.name)
        print("")

        # end of tests

        print("")
        print("====================")
        print("All tests completed!")
        print("")



        # Clear old test objects from database
        try:
            worms = Game.objects.get(name="Worms")
            myworms = MyGame.objects.filter(game=worms)
            wormscores = Highscore.objects.filter(game=worms)
            worms.delete()
            myworms.delete()
            wormscores.delete()
            tetris = Game.objects.get(name="Tetris")
            mytetris = MyGame.objects.filter(game=tetris)
            tetrisscores = Highscore.objects.filter(game=tetris)
            tetris.delete()
            mytetris.delete()
            tetrisscores.delete()
            pasi = User.objects.get(username="Meemimestari")
            pasi.delete()
            lassi = User.objects.get(username="leHomo")
            lassi.delete()
            
        except ObjectDoesNotExist:
            print("Some objects might not have been deleted...")
            print("")
               
        """
        # I used the following code to add 'Children's Rock Game' game to pasi's own games in the database...
        # do not use it unless you know what you're doing :^)
        """
        pasi = User.objects.get(username="pasi")
        test = Game.objects.get(id=1)
        #test.delete()
        testgame = MyGame(game=test, player=pasi, gamestate="")
        testgame.save()
        pasi.mygame_set.add(testgame)
        """ 
        lassi = User.objects.get(username="lassi")
        print(lassi.password)
       # usergames = MyGame.objects.filter(player=devjaba)
       # userhighscores = [[0 for x in range(10)] for x in range(usergames.count())]

        #for player in User.objects.get(username):
        
        
        #for game in Game.objects.all():
           # MyGame.objects.create(player=lassi, game=game)
        """
        usergames = MyGame.objects.filter(player=lassi)
        

        for mgame in usergames:
            for x in range(10):
                Highscore.objects.create(value=randint(10,10000), game=mgame.game, mygame=mgame)
              

        print(lassi.username)
        for mgame in usergames:
            print(mgame.game.name)
            for hs in mgame.highscore_set.all():
               # hs.delete()
                print(hs.value)
        print("")
        """

        """           
        userhighscores = [[] for x in range(usergames.count())]

        userhighscores[1] = [1,2,3,4,5]
        userhighscores[1][4] = 9
        print(userhighscores[1])
        print(userhighscores[1][4])
        print(json.dumps(userhighscores))
        """

        #new_game = pasi.mygame_set.get(game=test)

        #print(new_game.game.name)
        
        
        



