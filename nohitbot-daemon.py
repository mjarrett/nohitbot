#!/usr/bin/env python3

import mlbgame
import os
import time
import datetime
import sys
from daemoner import Daemon, log
import twitterer as twitter
from tweepy.error import TweepError

def g():
    twitter.warning("@jaysnohit is shutting down")

def get_game(year,month,day,team):
    
    try:
        games = mlbgame.day(year,month,day,home=team)
    except:
        return None,None
    
    if len(games) > 0:
        return games[0],True
    
    try:
        games = mlbgame.day(year,month,day,away=team)
    except:
        return None,None
    if len(games) > 0:
        return games[0],False
        
    return None,None

def toint(x):
    try:
        return int(x)
    except:
        return 0


def get_hits(game,home):
    if home:
        hits = game.home_team_hits
    else:
        hits = game.away_team_hits  
    return hits
        
def get_last_game_id():
    try:
        with open('/var/run/nohitbot/lastgame.txt','r') as f:
            last_game_id = f.read().strip()  
    except Exception:
        last_game_id = None
    return last_game_id
        
def finish_game(game):
    with open('/var/run/nohitbot/lastgame.txt','w') as f:
        f.write(game.game_id)  
    
def nohit(team='Blue Jays'):
    
    
    while True:
        
        sleep = 60
        log(f"{datetime.datetime.now()}")
        now  = datetime.datetime.now()
        game,home = get_game(now.year,now.month,now.day,team)
        
        
        last_game_id = get_last_game_id()
        
            
        
        if game == None:
            sleep = 60*60
            log("No games today")
            
        elif game.game_id == last_game_id:
            sleep = 60*60
            log("Today's game is finished")
        
        else:
            log(game)
            sleep = 10
            game_id = game.game_id
            
            try:
                data = mlbgame.game.box_score(game_id)
            except Exception:
                sleep = 60
                continue
                
            #if 1 not in data.keys():
            #    current_inning = 1
            #else:
            #    current_inning = sorted([x for x in data.keys() if type(x)==int])[-1]

            if home:
                ha = 'home'
            else:
                ha = 'away'





            if game.game_status == 'PRE_GAME':
                log(game.game_status)
                current_inning = 1
                sleep = 60*5

            if game.game_status == 'IN_PROGRESS':        
                data = mlbgame.game.box_score(game.game_id) 
                hits = get_hits(game,home)
                try:
                    current_inning
                except NameError:
                    current_inning = max([toint(x) for x in data.keys()])
                log(game)
                log(data)
                log(f"inning: {current_inning}")
                log(f"hits  : {hits}")

                try:
                    int(data[current_inning][ha])
                    inning_over = True
                except ValueError:
                    inning_over = False
                except KeyError:
                    continue

                if hits > 0:
                    try:
                        twitter.tweet('JaysNoHit',"Not this time!")
                        log("Not this time!")
                    except TweepError as e:
                        log(e)
                        twitter.tweet('JaysNoHit',"The Jays got a hit!")
                        log("The Jays got a hit!")
                    except Exception as e:
                        log(e)
                        twitter.tweet('1710_13',"@mikejarrett_ @jaynohit raised the following error: {}".format(e))
                    finish_game(game)
                    current_inning = 0


                if current_inning + 1 in data.keys() or inning_over:

                    if hits == 0:
                        try:
                            twitter.tweet('JaysNoHit',f"The #bluejays are being no-hit through {current_inning}")
                            log(f"The #bluejays are being no-hit through {current_inning}")
                        except TweepError as e:
                            log(e)
                            twitter.tweet('JaysNoHit',f"The #bluejays don't have a hit through {current_inning}")
                            log(f"The #bluejays don't have a hit through {current_inning}")
                        except Exception as e:
                            log(e)
                            twitter.tweet('1710_13',"@mikejarrett_ @jaysnohit raised the following error: {}".format(e))
                        current_inning += 1




            if game.game_status == 'FINAL':
                data = mlbgame.game.box_score(game.game_id) 
                hits = get_hits(game,home)
                if hits == 0:
                    log("Yes, the #bluejays have been no-hit",game)
                    twitter.tweet('JaysNoHit',"The #bluejays have been no-hit")
                finish_game(game)
                current_inning = 0
        
        time.sleep(sleep)
        
fkwargs = {'team':'Blue Jays'}
d = Daemon(f=nohit,fkwargs=fkwargs,pidfilename='/home/msj/bluejays/daemon.pid',g=g)
d.run()        