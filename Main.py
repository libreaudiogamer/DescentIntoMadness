#*******************************************************************************************************************
# Eden Kung and Matt Clark
# Comp 190 - Enabling Technologies
# Myst/Resident Evil for people with visual impairments
#*******************************************************************************************************************
# go to the program directory before importing my files
import os, sys
if sys.version_info[0] < 3:
    print("Python 2 is not supported. You must run this with Python 3")
    sys.exit()
mydir = os.path.dirname(sys.argv[0])
if mydir:
    os.chdir(mydir)
  
from collections import UserDict
import pickle         #for loading and saving data
import sys            #for sys.exit()
from threading import Timer


#global currentRoom, roomDict
currentRoom = None
roomDict = None
operatingRoom = None
freezer= None
basementHallway = None
pianoRoom= None
elevator = None
study= None
upperHallway = None
bedroom = None
bathroom= None
closet = None
bathroomHallway= None
balcony = None
westHallway= None
lobby= None
library = None
masterBedroom= None
masterBathroom= None
masterElevator= None
eleanorsRoom = None
sittingRoom = None
basement = None
kitchen= None
lab = None
garage = None
trappedHallway = None
outside = None
barn = None
barnLoft= None
inventory= None
#******** PYGAME INITIALIZATION ********************************************************************
import pygame
from pygame.locals import *
#Initialize the mixer before pygame itself because it causes less lag.
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.mixer.init()
pygame.init()
screen = pygame.display.set_mode((750, 550))
pygame.display.set_caption('Descent Into Madness')
pygame.mouse.set_visible(0)

titleScreen = pygame.image.load('images/Descent Into Madness.jpg')
tSrect = titleScreen.get_rect()

screen.blit(titleScreen, tSrect)
pygame.display.flip()


#************* CLASS TYPES *************************************************************************
class Room(UserDict):
    "Room"
    def __init__(self):
        UserDict.__init__(self)

    def construct(self, stringName, soundName, soundDescription, connectingRooms, examineItems):
        self["name"]=stringName
        self["sName"]=soundName
        self["sDescription"]=soundDescription
        self["rooms"]=connectingRooms
        self["items"]=examineItems
        
class Item(UserDict):
    "Items"
    def __init__(self):
        UserDict.__init__(self)

    def construct(self, stringName, soundName, soundDescription, canYouTakeIt):
        self["name"]=stringName
        self["sName"]=soundName
        self["sDescription"]=soundDescription
        #takable: 0 = not takable, 1 = takable
        self["takable"]=canYouTakeIt

class DeadException(Exception):
    "Thrown when player dies"
    def __init__(self):
        pass


#*************** ACTIONS **************************************************************************
def useItem():
    "When an item is used"
    global currentRoom, roomDict
    #prints will have to be replaced by sound files
    #print "What item will you use?"
    playSound("whatItemWillYouUse.ogg")
    #select will return the item selected
    #itemUsed = select(items that are in the inventory room)
    itemUsed = select([elem for elem in roomDict["inventory"]["items"]])
    if itemUsed == "esc":
        return 0
    #if itemUsed == 0:   #this should never happen assuming you can use player
    #    print "No items in inventory"
    #    return 0

    #print "Use this on what?"
    playSound("useThisOnWhat.ogg")
    #select amongst items still not picked up or used
    usedOn = select([elem for elem in roomDict[currentRoom]["items"]])
    if usedOn == 0:
        #print "No examinable items in this room"
        playSound("noItems.ogg")
        return 0
    elif usedOn == "esc":
        return 0

    successfulUse = 0
    #itemUses[itemUsed["name]] is the list of usedOn and function for a given itemUsed
    #e.g. itemUses[player] is returns [["journal", save], ["painting", punch]]
    for elem in itemUses[itemUsed["name"]]:      #elem is a single usedOn, function combination 
#        if itemUses[itemUsed["name"]][0] == usedOn["name"]:
#            itemUses[itemUsed["name"]][1]() 
        if elem[0] == usedOn["name"]:
            elem[1]()   #elem[1] is the function to call upon successful use
            successfulUse = 1
            
    if successfulUse == 0:
        #print "Nothing happened"
        playSound("nothingHappened.ogg")

def examine():
    "Examine objects in room"
    global currentRoom, roomDict
    if len(roomDict[currentRoom]["items"]) == 0:
        #print "There are no items in this room"
        playSound("noItems.ogg")
    else:            
        #print "The following items in this room seem suspicious"
        soundInterrupt = playSound("itemsSeemSuspicious.ogg")
        if soundInterrupt:
            pass
        else:
            for item in roomDict[currentRoom]["items"]:              
                #print item["name"]
                soundInterrupt = playSound(item["sName"])
                if soundInterrupt:
                    break
                else:
                    pass
    while 1:
        #print "What would you like to examine?"
        playSound("whatToExamine.ogg")
        examined = select([elem for elem in roomDict[currentRoom]["items"]] + [roomDict[currentRoom]])
        if examined == "esc":
            return 0
        
        #print examined["sDescription"]
        playSound(examined["sDescription"])
  
        #rooms can't be takable, so break if it's a room
        if examined.__doc__ == "Room":
            pass
        elif examined["takable"]==1:
            #print "Would you like to take this item?"
            soundInterrupt = playSound("takeItem.ogg")
            yesOrNo = selectOption(yesNoList)
            if (yesOrNo == "yes"):
                roomDict["inventory"]["items"].append(examined)
                roomDict[currentRoom]["items"].remove(examined)
                #print "You have taken the " + examined["name"]
                soundInterrupt = playSound("youHaveTakenThe.ogg")
                if soundInterrupt:
                    pass
                else:
                    playSound(examined["sName"])
    
        playSound("continueExamine.ogg")
        yesOrNo = selectOption(yesNoList)
        if yesOrNo == "no":
            break
        else:
            pass
    
def move():
    "When player wants to move"
    global currentRoom, roomDict

    if len(roomDict[currentRoom]["rooms"]) == 0:
        #print "You can't move anywhere"
        playSound("cantMoveAnywhere.ogg")
        return 0
      
    #print "Where do you want to move?"
    playSound("whereToMove.ogg")
    moveTo = select(roomDict[currentRoom]["rooms"])
    if moveTo == "esc":
        return 0
    currentRoom = moveTo["name"]
    #print "You are now in the " + currentRoom["name"]
    soundInterrupt = playSound("youAreNowInThe.ogg")
    if soundInterrupt:
        return 0
    playSound(roomDict[currentRoom]["sName"])
    if soundInterrupt:
        return 0
    playSound(roomDict[currentRoom]["sDescription"])
    

#************** MENU FUNCTIONS **************************************************************************
def menu():
    "Menu"
    while 1 == 1:        
        #print "Welcome to the game, use the spacebar to select, the esc key to cancel, and any other key to scroll"
        pygame.mixer.music.load("sounds/menumusic.ogg")
        pygame.mixer.music.set_volume(.80)
        pygame.mixer.music.play(-1)
        playSound("descentIntoMadness.ogg")
        playSound("menuInstructions.ogg")
        #print "Choose a menu option"
        playSound("menu.ogg")
        menuOption = selectOption(menuList)

        #to prevent accidental quits
        if menuOption == "esc":
            pass
        else: 
            menuOption()

def newGame():
    "New Game"
    pygame.mixer.music.load("sounds/music1.ogg")
    pygame.mixer.music.set_volume(.15)
    pygame.mixer.music.play(-1)
    constructRoomsItems()
    global currentRoom
    currentRoom = operatingRoom["name"]

    #print "You awaken to find yourself strapped to a operating table"
    playSound("intro.ogg")
    #playSound("instructions.ogg")
    gameLoop()
    
def loadGame():
    "Load Game"
    pygame.mixer.music.load("sounds/music1.ogg")
    pygame.mixer.music.set_volume(.15)
    pygame.mixer.music.play(-1)
    global inventory, operatingRoom, freezer, basementHallway, pianoRoom, elevator, study, upperHallway, bedroom, bathroom, closet, bathroomHallway, balcony, westHallway, lobby, library, masterBedroom,  masterBathroom, masterElevator, eleanorsRoom, sittingRoom, basement, kitchen, lab, garage, trappedHallway, outside, barn, barnLoft, currentRoom, roomDict
    #retrieve currentRoom and roomDict
    #print "Please select a save slot to load"
    playSound("selectLoad.ogg")
    try:
        slot = selectOption(saveList)
#        print slot
        fileHandle = open ( slot,'rb')
        [inventory, operatingRoom, freezer, basementHallway, pianoRoom, elevator, study, upperHallway, bedroom, bathroom, closet, bathroomHallway, balcony, westHallway, lobby, library, masterBedroom,  masterBathroom, masterElevator, eleanorsRoom, sittingRoom, basement, kitchen, lab, garage, trappedHallway, outside, barn, barnLoft, currentRoom, roomDict] = pickle.load ( fileHandle )
        fileHandle.close()
    except IOError:
        #print "That file is empty or doesn't exist. You will now be returned to the main menu"
        playSound("loadError.ogg")
        return 0
  
    gameLoop()

def save():
    "Save"
    global currentRoom, roomDict
    #write out roomDict and currentRoom to the file
    #print "Choose a slot to save your game"
    playSound("saveSlot.ogg")
    try:
        slot = selectOption(saveList)
        fileHandle = open ( slot, 'wb' )
        pickle.dump ( [inventory, operatingRoom, freezer, basementHallway, pianoRoom, elevator, study, upperHallway, bedroom, bathroom, closet, bathroomHallway, balcony, westHallway, lobby, library, masterBedroom,  masterBathroom, masterElevator, eleanorsRoom, sittingRoom, basement, kitchen, lab, garage, trappedHallway, outside, barn, barnLoft, currentRoom, roomDict], fileHandle ) #hopefully this works
        fileHandle.close()
        #print "Your game was successfully saved"
        playSound("saveSuccessful.ogg")
    except IOError:
        #print "Error while saving game. Game was not saved."
        playSound("saveError.ogg")    
  
def options():
    "Set the game options"
    #set voice speed
    #print "Choose the speed at which the voices will be spoken. Choosing fast will make the voices faster and higher pitched, and may work better for non-horror games"
    playSound("voiceSpeed1.ogg")
    voiceList = [["normal.ogg", SPEED_NORMAL], ["fast.ogg", SPEED_FAST]]
    global voiceSpeed
    voiceSpeed = selectOption(voiceList)

def quit():
    "Quit"
    pygame.quit()   #closes pygame window
    sys.exit()
    

#************** UTILITY FUNCTIONS ********************************************************************
def select(list):
    "Selecting something, will have to wait for keyboard input and return the item selected. Takes a list as an argument and goes through them via keyboard"
    global currentRoom, roomDict
    #Down or Right arrow goes to next item, Up or Left goes to prev item, Space bar uses elem
    if len(list) == 0:      # return 0 if case the list is empty
        return 0
    index = 0
    
    while 1 == 1:
        soundInterrupt = playSound(list[index]["sName"])
        if soundInterrupt:
            keyboardInput = soundInterrupt
        else:
            keyboardInput = getInput()
            
        if keyboardInput == K_ESCAPE:
            return "esc"
        elif keyboardInput == K_SPACE:
            return list[index]
        elif (keyboardInput == K_DOWN) or (keyboardInput == K_RIGHT):
            if index == len(list)-1:
                index = 0
            else:
                index += 1
        elif (keyboardInput == K_UP) or (keyboardInput == K_LEFT):
            if index == 0:
                index = len(list)-1
            else:
                index -= 1
        else:
            pass      

def selectOption(list):
    "Selecting non-item, non-room options, such as actions, or load files"
    global currentRoom, roomDict
    #Down or Right arrow goes to next item, Up or Left goes to prev item, Space bar uses elem
    index = 0
    
    while 1 == 1:
        soundInterrupt = playSound(list[index][0])
        if soundInterrupt:
            keyboardInput = soundInterrupt
        else:
            keyboardInput = getInput()

        if keyboardInput == K_ESCAPE:
            return "esc"
        elif keyboardInput == K_SPACE:
            return list[index][1]
        elif keyboardInput == K_DOWN or keyboardInput == K_RIGHT:
            if index == len(list)-1:
                index = 0
            else:
                index += 1
        elif keyboardInput == K_UP or keyboardInput == K_LEFT:
            if index == 0:
                index = len(list)-1
            else:
                index -= 1
        else:
            pass

def gameOver():
    "Game Over"
    #print "Game Over"
    playSound("gameOver.ogg")
    raise DeadException
    #menu()  #may have other functions on the stack, don't know what to do about that

def getInput():
    "Waits for keyboard input and returns key that is pressed."
    while 1==1:
        pygame.time.delay(100)
        for event in pygame.event.get():
            if (event.type == KEYUP): # or (event.type == KEYDOWN)
                return event.key
            if (event.type == QUIT):
                pygame.quit()
                sys.exit()
                
def playSound(r,delay=False):
    try:
        chan=pygame.mixer.find_channel()
        ss=pygame.mixer.Sound("sounds/"+r)
    except:    
        print("No sound called "+r+" was found in the game directory.")
        return
    chan.play(ss)
    while chan.get_busy():
        pygame.event.pump()
        pygame.time.delay(100)
        if delay == True:
            continue
        for event in pygame.event.get():
            if (event.type == KEYUP): # or (event.type == KEYDOWN)
                chan.stop()
                return event.key

#************** GAME LOOP *******************************************************************************
def gameLoop():
    #print "You are in the " + currentRoom["name"]
    global currentRoom, roomDict
    for i in range(1):
        soundInterrupt = playSound("youAreNowInThe.ogg")
        if soundInterrupt:
            break
        playSound(roomDict[currentRoom]["sName"])
        if soundInterrupt:
            break
        playSound(roomDict[currentRoom]["sDescription"])

    try:    
        while 1 == 1:
            #print "Choose an option"
            playSound("chooseAnOption.ogg")
            action = selectOption(actionList)              
            if action == "esc": #esc was pressed
                pass #to prevent accidental quits
            else:
                action()
    except DeadException:
        return 0

    
#************** useItem FUNCTIONS ***********************************************************************
def scalpelToOperatingTable():
    #print "You cut the straps on the operating table. You are now free!"
    playSound("cutStraps.ogg")
    playSound("cutStraps2.ogg")
    roomDict["inventory"]["items"].remove(scalpel)
    roomDict["operatingRoom"]["rooms"].append(freezer)
    roomDict["operatingRoom"]["items"].remove(operatingTable)
    roomDict["operatingRoom"]["items"].append(operatingRoomRecording)
    roomDict["operatingRoom"]["items"].append(operatingRoomDoor)

def playerToPainting():
    #print "You move the painting and a tune plays"
    playSound("movePainting.ogg")
    #print "Play tune"
    playSound("pianoC.ogg")
    playSound("pianoE.ogg")
    playSound("pianoG.ogg")

def playerToPiano():
    pianoKeyList = [ ["pianoChooseC.ogg", "pianoC.ogg"], ["pianoChooseD.ogg", "pianoD.ogg"], ["pianoChooseE.ogg", "pianoE.ogg"], ["pianoChooseF.ogg", "pianoF.ogg"], ["pianoChooseG.ogg", "pianoG.ogg"], ["pianoChooseA.ogg", "pianoA.ogg"], ["pianoChooseB.ogg", "pianoB.ogg"], ["cancel.ogg", "Cancel"] ]
    missCount = 0

    while 1 == 1:    
            #print "Press a key"
        playSound("pianoPressKey1.ogg")
        keyPressed1 = selectOption(pianoKeyList)
        if keyPressed1 == "Cancel":
            break
        #print keyPressed1
        playSound(keyPressed1)
        
        #print "Press a 2nd key"
        playSound("pianoPressKey2.ogg")
        keyPressed2 = selectOption(pianoKeyList)
        if keyPressed2 == "Cancel":
            break
        #print keyPressed2
        playSound(keyPressed2)
  
        #print "Press a 3rd key"
        playSound("pianoPressKey3.ogg")
        keyPressed3 = selectOption(pianoKeyList)
        if keyPressed3 == "Cancel":
            break
        #print keyPressed3
        playSound(keyPressed3)
  
        if(keyPressed1 == "pianoC.ogg" and keyPressed2 == "pianoE.ogg" and keyPressed3 == "pianoG.ogg"):
            #print "Ding!"
            playSound("chime.ogg")
            #print "You hear a loud rumble from the hallway that sounds like a wall moving"
            playSound("pianoSolve.ogg")
            roomDict["basementHallway"]["rooms"].insert(0, elevator)
            #basementHallway["rooms"].insert(0, elevator) #added elevator
            break
        else:
            missCount = missCount + 1
            #print "Err!"
            playSound("buzzer.ogg")
            if(missCount == 3):
            #print "You have failed too many times. A trap door opens underneath you, revealing a pit of spikes. You fall to your death."
                playSound("pianoFail.ogg")
                gameOver()
            else:
                playSound("pianoTryAgain.ogg")
      
def operatingRoomKeyToOperatingRoomDoor():
    #print "You unlocked the door to the hallway. You can now move to the hallway."
    playSound("unlockOperatingRoom.ogg")
    roomDict["inventory"]["items"].remove(operatingRoomKey)
    roomDict["operatingRoom"]["rooms"].insert(0, basementHallway)
    roomDict["operatingRoom"]["items"].remove(operatingRoomDoor)

def broomToShelf():
    "Knocks box off of the shelf"
    #print "You hit the box off of the shelf"
    playSound("broomToShelf.ogg")
    roomDict["bathroom"]["items"].insert(0, box)

def playerToBox():
    "Stand on box, can reach star hole"
    #print "You stand on the box. You can now reach the star-shaped hole"
    playSound("playerToBox.ogg")
    roomDict["bathroom"]["items"].insert(0, starHole)
    roomDict["bathroom"]["items"].remove(box)

def starToStarHole():
    "Mirror open, revealing a small dark hallway with a door at the end"
    #print "You put the star in the star-shaped hole. Sound plays. Mirror moves"
    playSound("starToStarHole.ogg")
    roomDict["bathroom"]["rooms"].insert(0, bathroomHallway)

def deskKeyToDesk():
    "Unlock desk, reveals recording"
    #print "The desk opens, revealing a recording"
    playSound("deskKeyToDesk.ogg")
    roomDict["bedroom"]["items"].insert(0, bedroomRecording)
    roomDict["bedroom"]["items"].insert(0, star)
    roomDict["inventory"]["items"].remove(deskKey)

def hammerToMirror():
    "Break mirror, Dr hears the noise and game over"
    #print "You break the mirror with the hammer with a loud crash!, revealing a hallway hidden behind the mirror. Unfortunately, the Dr hears the loud crash and find you in the bathroom. You try to defend yourself with the hammer, but you miss, and he injects you with a tranquilizer, puts you to sleep, and takes you away"
    playSound("hammerToMirror.ogg")
    gameOver()

def playerToBathroomHallwayDoor():
    "Knock on door, talk to friend"
    #print "You knock on the door to get the attention of the person inside."
    playSound("playerToBathroomHallwayDoor.ogg")
    playSound("friend010_cell.ogg")
    
def playerToSafe():
    "Open safe with passcode 2 1 6"
    numberList = [ ["1.ogg", "1"], ["2.ogg", "2"], ["3.ogg", "3"], ["4.ogg", "4"], ["5.ogg", "5"], ["6.ogg", "6"], ["7.ogg", "7"], ["8.ogg", "8"], ["9.ogg", "9"], ["0.ogg", "0"] ]

    #print "Enter the combination"
    playSound("safe1.ogg")
    #print "Choose a number"
    playSound("safeChoose1.ogg")
    numberChosen1 = selectOption(numberList)
    
    #print "Choose a second number"
    playSound("safeChoose2.ogg")
    numberChosen2 = selectOption(numberList)

    #print "Choose a third number"
    playSound("safeChoose3.ogg")
    numberChosen3 = selectOption(numberList)

    if(numberChosen1 == "2" and numberChosen2 == "1" and numberChosen3 == "6"):
        #print "Ding!"
        playSound("chime.ogg")
        #print "The safe opens. Inside you find a recording, a key, and a pass card"
        playSound("safeOpen1.ogg")
        roomDict["study"]["items"].remove(safe)
        roomDict["study"]["items"].insert(0, safeRecording)
        roomDict["study"]["items"].insert(0, cellKey)
        roomDict["study"]["items"].insert(0, passCard)
        #print "phone ring"
        playSound("phoneRing.ogg")
        #print "Strange, the phone suddenly rings. You pick it up"
        playSound("safeOpen2.ogg")
        #print "Professor talks"
        playSound("safeOpen3.ogg")
    else:
        #print "Err!"
        playSound("buzzer.ogg")
  
def cellKeyToBathroomHallwayDoor():
    "Opens the cell"
    roomDict["bathroomHallway"]["items"].remove(bathroomHallwayDoor)
    roomDict["inventory"]["items"].remove(cellKey)
    #print "Let's go to the main hallway and open the strange locked door"
    playSound("cellKeyToBathroomHallwayDoor.ogg")
    global currentRoom
    currentRoom = upperHallway["name"]
    playSound("cellKeyToBathroomHallwayDoor2.ogg")
    
    #condition something = true? for not letting people just open the door with the hammer earlier?
    #or maybe he gives you something to open the door with

def hammerToUpperHallwayDoor():
    "You need to hit the door and it opens. You can now move to the balcony"
    #print "You hit the door and it opens"
    playSound("hammerToUpperHallwayDoor.ogg")
    playSound("hammerToUpperHallwayDoor2.ogg")
    roomDict["upperHallway"]["items"].remove(upperHallwayDoor)
    roomDict["upperHallway"]["rooms"].insert(0, balcony)
    roomDict["inventory"]["items"].remove(hammer)
    #do you still need the hammer?

def passCardToMainEntrance():
    "Open and dogs will eat you"
    #print "You use the pass card and the main entrance opens. Unfortunately, as soon as you open it, you find a pack of growling dogs waiting outside. They look pretty hungry, and apparently, they find you pretty tasty."
    playSound("passCardToMainEntrance.ogg")
    gameOver()

def masterBedroomDeskKeyToMasterBedroomDesk():
    "Open desk"
    #print "You open the desk and find a key and another recording"
    playSound("masterBedroomDeskKeyToMasterBedroomDesk.ogg")
#    roomDict["masterBedroom"]["items"].insert(0, masterBathroomKey)
    roomDict["masterBedroom"]["items"].insert(0, masterBedroomRecording)
    roomDict["masterBedroom"]["items"].remove(masterBedroomDesk)
    roomDict["inventory"]["items"].remove(masterBedroomDeskKey)

def starToMasterBathroomStarHole():
    "Opens mirror"
    #print "The mirror moves, revealing an elevator"
    playSound("starToMasterBathroomStarHole.ogg")    
    roomDict["masterBathroom"]["rooms"].insert(0, masterElevator)
    roomDict["masterBathroom"]["items"].remove(masterBathroomStarHole)
    roomDict["masterBathroom"]["items"].remove(masterBathroomMirror)

def playLeftSound():
    "For the passCardToSittingRoomDoor puzzle. Plays a sound to the left"
    chan=pygame.mixer.find_channel()
    LeftSound = pygame.mixer.Sound("sounds/pianoC.ogg")
    chan.set_volume(1,0)
    chan.play(LeftSound)
    while chan.get_busy():
        pygame.event.pump()
        pygame.time.delay(100)

def playRightSound():
    "For the passCardToSittingRoomDoor puzzle. Plays a sound to the right"
    chan=pygame.mixer.find_channel()
    RightSound = pygame.mixer.Sound("sounds/pianoF.ogg")
    chan.set_volume(0, 1)
    chan.play(RightSound)
    while chan.get_busy():
        pygame.event.pump()
        pygame.time.delay(100)
def passCardToSittingRoomDoor():
    "Puzzle to open Eleanor's room"
    #print "There are 2 speakers in front of you, one on the left, one on the right. Below each speaker is a button. When you insert the pass key, sounds start playing from the left and right speakers.
    playSound("passCardToSittingRoomDoor1.ogg")
    buttonList=[ ["leftButton.ogg", "leftButton"], ["rightButton.ogg", "rightButton"], ["cancel.ogg", "cancel"] ] 
#    #sequence is L, R, L, L
    playLeftSound()
    playRightSound()
    playLeftSound()
    playLeftSound()
#    #print "Press a button"
    playSound("passCardToSittingRoomDoor2.ogg")
    buttonPressed = selectOption(buttonList)
    if buttonPressed == "cancel":
        return 0
    buttonSequence = buttonPressed
    for i in range(3):
#        #print "Press a button"
        playSound("passCardToSittingRoomDoor2.ogg")
        buttonPressed = selectOption(buttonList)
        if buttonPressed == "cancel":
            return 0
        buttonSequence += buttonPressed
    if(buttonSequence != "leftButtonrightButtonleftButtonleftButton"):
#        playSound("buzzer.ogg")
#        #print "Apparently you've inputted the wrong sequence of button presses. A trap door opens underneath you, revealing a pit of spikes. You fall to your death"
        playSound("passCardToSittingRoomDoor3.ogg")
        gameOver()
    playSound("chime.ogg")

#    #second sequence is R, R, R, L, R, L
    playRightSound()
    playRightSound()
    playRightSound()
    playLeftSound()
    playRightSound()
    playLeftSound()
#    #print "Press a button"
    playSound("passCardToSittingRoomDoor2.ogg")
    buttonPressed = selectOption(buttonList)
    if buttonPressed == "cancel":
        return 0
    buttonSequence = buttonPressed
    for i in range(5):
#        #print "Press a button"
        playSound("passCardToSittingRoomDoor2.ogg")
        buttonPressed = selectOption(buttonList)
        if buttonPressed == "cancel":
            return 0
        buttonSequence += buttonPressed
    if(buttonSequence != "rightButtonrightButtonrightButtonleftButtonrightButtonleftButton"):
        playSound("buzzer.ogg")
#        #print "Apparently you've inputted the wrong sequence of button presses. A trap door opens underneath you, revealing a pit of spikes. You fall to your death"
        playSound("passCardToSittingRoomDoor3.ogg")
        gameOver()
    playSound("chime.ogg")
#    #print "The door slides open. You can now move into the dark room ahead"
    playSound("passCardToSittingRoomDoor4.ogg")
    roomDict["sittingRoom"]["rooms"].insert(0, eleanorsRoom)
    roomDict["sittingRoom"]["items"].remove(sittingRoomDoor)

def knifeToEleanor():
    "Cut her bindings"
    #print "Eleanor conversation"
    playSound("knifeToEleanor.ogg")
    roomDict["inventory"]["items"].append(gun)
    roomDict["eleanorsRoom"]["items"].remove(eleanor)
    eleanor["sDescription"]="eleanorDesc2.ogg"
    roomDict["basementHallway"]["rooms"].insert(0, lab)
    roomDict["basementHallway"]["items"].remove(labDoor)
    roomDict["lab"]["items"].insert(0, eleanor)
    roomDict["study"]["rooms"].remove(elevator)

def passCardToMazeDoor():
#    "Starts the maze. Follow the sound to get to the exit"
    playSound("passCardToMazeDoor0.ogg")
#  
#    song.Stop()
#    exitSound = pySonic.Source()
#    exitSound.Sound = pySonic.FileStream("sounds/pianoC.ogg", pySonic.Constants.FSOUND_LOOP_NORMAL)
#    exitSound.Position = (0, 4, 0)
#    exitSound.Velocity = (0, 0, 0)
#    exitSound.Volume = 50
#    exitSound.Play()
#    
#    #maze is 5 x 5 matrix. 0 denotes not movable. 1 denotes movable. 2 denotes monster. 3 denotes end.
#    mazeMatrix = [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]
#    mazeMatrix[0][0]=2
#    mazeMatrix[1][0]=1
#    mazeMatrix[2][0]=1
#    mazeMatrix[3][0]=1
#    mazeMatrix[3][1]=1
#    mazeMatrix[3][2]=1
#    mazeMatrix[2][2]=1
#    mazeMatrix[1][2]=1
#    mazeMatrix[1][3]=1
#    mazeMatrix[1][4]=1
#    mazeMatrix[0][4]=3
#    mazeMatrix[0][2]=2
#    mazeMatrix[3][3]=2
#    mazeMatrix[4][2]=2

#    #start at (3,0)
#    positionX=3
#    positionY=0
#    #w.Listener.Position = (positionX, positionY, 0) 

#    #print "You are now in the maze. Navigate by going north, west, south, or east. There is a sound coming from the exit, and you can assume that you are always facing north "
#    playSound("passCardToMazeDoor1.ogg")

#    while 1:
#        #make the move list
#        mazeMoveList = []
#        #north
#        if (positionY + 1 <= 4) and (mazeMatrix[positionX][positionY+1] != 0):
#            mazeMoveList.append(["north.ogg", "north"])
#        #west
#        if (positionX - 1 >= 0) and (mazeMatrix[positionX-1][positionY] != 0):
#            mazeMoveList.append(["west.ogg", "west"])
#        #south
#        if (positionY - 1 >= 0) and (mazeMatrix[positionX][positionY-1] != 0):
#            mazeMoveList.append(["south.ogg", "south"])
#        #east
#        if (positionX + 1 <= 4) and (mazeMatrix[positionX+1][positionY] != 0):
#            mazeMoveList.append(["east.ogg", "east"])             
#        
#        #move
#        #print "The following paths are open:"
#        playSound("passCardToMazeDoor2.ogg")
#        for elem in mazeMoveList:
#            playSound(elem[0])
#        #print "Select a direction to move."
#        playSound("passCardToMazeDoor3.ogg")
#        mazeMove = selectOption(mazeMoveList)
#        
#        #update position
#        if mazeMove == "north":
#            positionY += 1
#        elif mazeMove == "south":
#            positionY -= 1
#        elif mazeMove == "east":
#            positionX += 1
#        elif mazeMove == "west":
#            positionX -= 1
#        exitSound.Position = (0-positionX, 4-positionY, 0)
#        exitSound.Play()
      
#            
#        if(mazeMatrix[positionX][positionY] == 2):
            #print "ROAR! It's a monster."
#            playSound("passCardToMazeDoor4.ogg")
#            playSound("whatItemWillYouUse.ogg")
#            itemUsed = select([elem for elem in roomDict["inventory"]["items"]])
#            if itemUsed["name"] == "gun":
#                #print "The monster lunges at you, but you side step and fire your gun! BANG! And the monster falls dead"
#                playSound("passCardToMazeDoor5.ogg")
#            else:
#                #print "The monster is not phased, and lunges straight for your neck, ripping out your throat"
#                playSound("passCardToMazeDoor6.ogg")
#                song.Play()
#                gameOver()
#        elif(mazeMatrix[positionX][positionY]==3):
#            #print "You've reached the end of the maze. After rummaging through stacks of chemicals, you find the ingredients that Eleanor told you about. You make your way back to the entrance of the maze, and are now back in the basement"
    playSound("passCardToMazeDoor7.ogg")
    roomDict["inventory"]["items"].append(ingredients)
#            exitSound.Stop()
#            song.Play()
#            return 0
  
def playerToComputer():
    "Attempt to logon to computer. Need passkey from notebook, which is 9 3 1"
    numberList = [ ["1.ogg", "1"], ["2.ogg", "2"], ["3.ogg", "3"], ["4.ogg", "4"], ["5.ogg", "5"], ["6.ogg", "6"], ["7.ogg", "7"], ["8.ogg", "8"], ["9.ogg", "9"], ["0.ogg", "0"] ]
    #print "You attempt to use the computer and it starts to speak
    #playTTS("Please enter the pass key to unlock the basement lab")
    #print "Choose a number"
    playSound("safeChoose1.ogg")
    numberChosen1 = selectOption(numberList)
    
    #print "Choose a second number"
    playSound("safeChoose2.ogg")
    numberChosen2 = selectOption(numberList)
    #print "Choose a third number"
    playSound("safeChoose3.ogg")
    numberChosen3 = selectOption(numberList)

    if(numberChosen1 == "9" and numberChosen2 == "3" and numberChosen3 == "1"):
        #print "Ding!"
        playSound("chime.ogg")
        #print "The basement lab is now unlocked. You can access the lab by going down the elevator in this room"
        playSound("computerActivateElevator.ogg")
        roomDict["study"]["rooms"].insert(0, elevator)
    else:
        #print "Err!"
        playSound("buzzer.ogg")
  
def ingredientsToEleanor():
    "Give ingredients to Eleanor"
    #print "Eleanor conversation"
    playSound("ingredientsToEleanor.ogg")
    playSound("ingredientsToEleanor2.ogg")
    roomDict["inventory"]["items"].append(garageKey)
    roomDict["inventory"]["items"].remove(ingredients)
    eleanor["sDescription"]="eleanorDesc3.ogg"
    
def garageKeyToGarageDoor():
    "Doesn't work"
    #print "You try the key to the door, but the lock seems to be rusted shut. Maybe you can just shoot it out"
    playSound("garageKeyToGarageDoor.ogg")
    
def gunToGarageDoor():
    "Shoot open lock"
    #print "You shoot the lock on the door and it shatters. You can now move to the garage"
    playSound("gunToGarageDoor.ogg")
    roomDict["inventory"]["items"].remove(garageKey)
    roomDict["kitchen"]["items"].remove(garageDoor)
    roomDict["kitchen"]["rooms"].insert(0, garage)
    
def dieInTrappedHallway():
    "For use in trappedHallwayDoorKeyToTrappedHallwayDoor()"
    #print "You fail to act fast enough, and a large blade cuts in you half"
    playSound("dieInTrappedHallway.ogg")
    gameOver()
    
def trappedHallwayReact(direction):
    if direction == "up":
        soundFile = "jump.ogg"
        expectedInput = K_UP
    elif direction == "down":
        soundFile = "duck.ogg"
        expectedInput = K_DOWN
    elif direction == "left":
        soundFile = "left.ogg"
        expectedInput = K_LEFT
    elif direction == "right":
        soundFile = "right.ogg"
        expectedInput = K_RIGHT
    elif direction == "shoot":
        soundFile = "shoot.ogg"
        expectedInput = K_SPACE
    else:
         print("Error in trappedHallwayReact()")
    t = Timer(2.0, dieInTrappedHallway)
    playSound(soundFile)
    t.start() # after 2 seconds, player dies if he hasn't inputted correct key
    while 1:
        keyboardInput = getInput()
        if keyboardInput == expectedInput:
            t.cancel()
            return 0
        else:
            #print "You act as fast you can, but you did the wrong thing and a blade cuts you in half"
            t.cancel()
            playSound("dieInTrappedHallway2.ogg")
            gameOver()
  
def trappedHallwayDoorKeyToTrappedHallwayDoor():
    "Use key on door, triggers cut scene"
    roomDict["inventory"]["items"].remove(trappedHallwayDoorKey)
    #print "Conversation"
    playSound("trappedHallwayDoorKeyToDoor0.ogg")
    playSound("trappedHallwayDoorKeyToDoor1.ogg")
    playSound("trappedHallwayDoorKeyToDoor2.ogg")

    #sequence up, down, left, right, up, up, down, down, right, down
    trappedHallwayReact("up")
    trappedHallwayReact("down")
    trappedHallwayReact("left")
    trappedHallwayReact("right")
    trappedHallwayReact("up")
    trappedHallwayReact("up")
    trappedHallwayReact("down")
    trappedHallwayReact("down")
    trappedHallwayReact("right")
    trappedHallwayReact("down")
    #print "conversation"
    playSound("friend070_road.ogg")

    global currentRoom
    currentRoom = outside["name"]
    soundInterrupt = playSound("youAreNowInThe.ogg")
    if soundInterrupt:
        return 0
    playSound(roomDict[currentRoom]["sName"])
    if soundInterrupt:
        return 0
    playSound(roomDict[currentRoom]["sDescription"])

def passCardToBarnDoor():
    "Unlock barn"
    #print "You have unlocked the barn door. You can now move into the barn"
    playSound("passCardToBarnDoor.ogg")
    roomDict["outside"]["rooms"].insert(0, barn)
    
def playerToBarnSwitch():
    "Unlocks cages, monsters kill you"
    #print "You hit the switch, and all of the cages open. You've freed all of the monsters, and they show their thanks by eating you alive."
    playSound("playerToBarnSwitch.ogg")
    gameOver()
    
def knifeToEleanor2():
    "Cut her bindings"
    #print "conversation"
    playSound("knifeToEleanor2.ogg")
    playSound("eleanor050_barn.ogg")
    
def dieInBarn():
    "Killed by doctor"
    #print "You try to pull out your gun, but you aren't fast enough. The doctor bounds up the stairs with surprising speed, steals your gun right out of your hand and shoots you with it"
    playSound("dieInBarn.ogg")
    gameOver()
    
def gasolineToEleanor2():
    "Give her the gas"
    #print "conversation"
    playSound("doc140_barn.ogg")
    playSound("friend080_shoot_the_doctor.ogg")
    
    t = Timer(2.0, dieInBarn) 
    t.start() # after 2 seconds, player dies if he hasn't inputted correct key 
    while 1:
        keyboardInput = getInput()
        if keyboardInput == K_SPACE:
            t.cancel()
            break
        else:
            pass

    playSound("doc150_barn_hit.ogg")
    
    #print "ending"
    playSound("narrator_before_final_scene.ogg")
    playSound("final_scene.ogg")
def constructRoomsItems():
    #construct the rooms and items
    operatingRoom.construct("operatingRoom", "operatingRoom.ogg", "operatingRoomDesc.ogg", [], [operatingTable, scalpel])   #freezer, operatingRoomDoor accessible after scalpelToOperatingTable, locked door to basementHallway
    freezer.construct("freezer", "freezer.ogg", "freezerDesc.ogg", [operatingRoom], [freezerBodies, operatingRoomKey])
    basementHallway.construct("basementHallway", "basementHallway.ogg", "basementHallwayDesc.ogg", [operatingRoom, pianoRoom], [journal, labDoor]) #hidden door to elevator
    pianoRoom.construct("pianoRoom", "pianoRoom.ogg", "pianoRoomDesc.ogg", [basementHallway], [painting, piano])
    elevator.construct("elevator", "elevator.ogg", "elevatorDesc.ogg", [basementHallway, study], [])
    study.construct("study", "study.ogg", "studyDesc.ogg", [upperHallway], [deskKey, studyRecording, computer, phone, safe])
    upperHallway.construct("upperHallway", "upperHallway.ogg", "upperHallwayDesc.ogg", [study, bedroom, closet], [upperHallwayDoor, journal])
    bedroom.construct("bedroom", "bedroom.ogg", "bedroomDesc.ogg", [upperHallway, bathroom], [desk, bed])
    bathroom.construct("bathroom", "bathroom.ogg", "bathroomDesc.ogg", [bedroom], [journal, mirror, bathtub, shelf])
    closet.construct("closet", "closet.ogg", "closetDesc.ogg", [upperHallway], [broom, hammer])
    bathroomHallway.construct("bathroomHallway", "bathroomHallway.ogg", "bathroomHallwayDesc.ogg", [bathroom], [bathroomHallwayDoor])
    balcony.construct("balcony", "balcony.ogg", "balconyDesc.ogg", [upperHallway, westHallway, lobby], [])
    westHallway.construct("westHallway", "westHallway.ogg", "westHallwayDesc.ogg", [balcony, masterBedroom, library], [journal])
    lobby.construct("lobby", "lobby.ogg", "lobbyDesc.ogg", [balcony, kitchen], [journal, mainEntrance, trappedHallwayDoor])
    library.construct("library", "library.ogg", "libraryDesc.ogg", [westHallway], [notebook, masterBedroomDeskKey, libraryRecording])
    masterBedroom.construct("masterBedroom", "masterBedroom.ogg", "masterBedroomDesc.ogg", [westHallway, masterBathroom], [masterBedroomDesk, masterBedroomBed])
    masterBathroom.construct("masterBathroom", "masterBathroom.ogg", "masterBathroomDesc.ogg", [masterBedroom], [masterBathroomMirror, masterBathroomStarHole])
    masterElevator.construct("masterElevator", "masterElevator.ogg", "masterElevatorDesc.ogg", [masterBathroom, sittingRoom, basement], [])
    eleanorsRoom.construct("eleanorsRoom", "eleanorsRoom.ogg", "eleanorsRoomDesc.ogg", [sittingRoom], [eleanor])
    sittingRoom.construct("sittingRoom", "sittingRoom.ogg", "sittingRoomDesc.ogg", [masterElevator], [journal, sittingRoomDoor])
    basement.construct("basement", "basement.ogg", "basementDesc.ogg", [masterElevator], [journal, mazeDoor])
    kitchen.construct("kitchen", "kitchen.ogg", "kitchenDesc.ogg", [lobby], [knife, garageDoor])
    lab.construct("lab", "lab.ogg", "labDesc.ogg", [basementHallway], [])
    garage.construct("garage", "garage.ogg", "garageDesc.ogg", [kitchen], [journal, gasoline, trappedHallwayDoorKey])
    trappedHallway.construct("trappedHallway", "trappedHallway.ogg", "trappedHallwayDesc.ogg", [lobby, outside], []) #Desc, traps have been deactivated
    outside.construct("outside", "outside.ogg", "outsideDesc.ogg", [trappedHallway], [journal, barnDoor])
    barn.construct("barn", "barn.ogg", "barnDesc.ogg", [outside, barnLoft], [barnSwitch])
    barnLoft.construct("barnLoft", "barnLoft.ogg", "barnLoftDesc.ogg", [barn], [eleanor2])
   
    inventory.construct("inventory", "inventory.ogg", "inventory.ogg", [], [player])

#************** MAIN METHOD *****************************************************************************
if __name__ == "__main__":
    try:
    #player, journal, and inventory are part of the game engine, so separate them out
        player = Item()
        journal = Item()
        player.construct("player", "self.ogg", "selfDesc.ogg", 0)
        journal.construct("journal", "journal.ogg", "journalDesc.ogg", 0)
        #inventory isn't really a room, but it's easier to treat it as one. All of the player's inventory is in the "items" list of the inventory room
        inventory = Room()

        
        #initialize the rooms and items
        operatingRoom = Room()
        freezer = Room()
        basementHallway = Room()
        pianoRoom = Room()
        elevator = Room()
        study = Room()
        upperHallway = Room()
        bedroom = Room()
        bathroom = Room()
        closet = Room()
        bathroomHallway = Room()
        balcony = Room()
        westHallway = Room()
        lobby = Room()
        library = Room()
        masterBedroom = Room()
        masterBathroom = Room()
        masterElevator = Room()
        eleanorsRoom = Room()
        sittingRoom = Room()
        basement = Room()
        kitchen = Room()
        lab = Room()
        garage = Room()
        trappedHallway = Room()
        outside = Room()
        barn = Room()
        barnLoft = Room()
        
        operatingTable = Item()
        scalpel = Item()
        operatingRoomRecording = Item()
        operatingRoomDoor = Item()
        operatingRoomKey = Item()
        freezerBodies = Item()
        piano = Item()
        painting = Item()
        deskKey = Item()
        studyRecording = Item()
        computer = Item()
        phone = Item()
        safe = Item()
        desk = Item()
        bedroomRecording = Item()
        bed = Item()
        mirror = Item()
        bathtub = Item()
        shelf = Item()
        box = Item()
        broom = Item()
        hammer = Item()
        star = Item()
        starHole = Item()
        bathroomHallwayDoor = Item()
        safeRecording = Item()
        cellKey = Item()
        passCard = Item()
        upperHallwayDoor = Item()
        notebook = Item()
        mainEntrance = Item()
        masterBedroomDeskKey = Item()
        masterBedroomDesk = Item()
        masterBedroomBed = Item()
        libraryRecording = Item()
        masterBedroomRecording = Item()
        masterBathroomStarHole = Item()
        masterBathroomMirror = Item()
        sittingRoomDoor = Item()
        knife = Item()
        trappedHallwayDoorKey = Item()
        eleanor = Item()
        gun = Item()
        labDoor = Item()
        ingredients = Item()
        mazeDoor = Item()
        garageDoor = Item()
        garageKey = Item()
        gasoline = Item()
        trappedHallwayDoor = Item()
        barnDoor = Item()
        barnSwitch = Item()
        eleanor2 = Item()

        operatingTable.construct("operatingTable", "operatingTable.ogg", "operatingTableDesc.ogg", 0)
        scalpel.construct("scalpel", "scalpel.ogg", "scalpelDesc.ogg", 1)
        operatingRoomRecording.construct("operatingRoomRecording", "recording.ogg", "operatingRoomRecordingDesc.ogg", 0)
        operatingRoomDoor.construct("operatingRoomDoor", "operatingRoomDoor.ogg", "operatingRoomDoorDesc.ogg", 0)
        operatingRoomKey.construct("operatingRoomKey", "operatingRoomKey.ogg", "operatingRoomKeyDesc.ogg", 1)
        freezerBodies.construct("freezerBodies", "freezerBodies.ogg", "freezerBodiesDesc.ogg", 0)
        piano.construct("piano", "piano.ogg", "pianoDesc.ogg", 0)
        painting.construct("painting", "painting.ogg", "paintingDesc.ogg", 0)
        deskKey.construct("deskKey", "deskKey.ogg", "deskKeyDesc.ogg", 1)
        studyRecording.construct("studyRecording", "recording.ogg", "studyRecordingDesc.ogg", 0)
        computer.construct("computer", "computer.ogg", "computerDesc.ogg", 0)
        phone.construct("phone", "phone.ogg", "phoneDesc.ogg", 0)
        safe.construct("safe", "safe.ogg", "safeDesc.ogg", 0)
        desk.construct("desk", "desk.ogg", "deskDesc.ogg", 0)
        bedroomRecording.construct("bedroomRecording", "recording.ogg", "bedroomRecordingDesc.ogg", 0)
        bed.construct("bed", "bed.ogg", "bedDesc.ogg", 0)
        mirror.construct("mirror", "mirror.ogg", "mirrorDesc.ogg", 0)
        bathtub.construct("bathtub", "bathtub.ogg", "bathtubDesc.ogg", 0)
        shelf.construct("shelf", "shelf.ogg", "shelfDesc.ogg", 0)
        box.construct("box", "box.ogg", "boxDesc.ogg", 0)
        broom.construct("broom", "broom.ogg", "broomDesc.ogg", 1)
        hammer.construct("hammer", "hammer.ogg", "hammerDesc.ogg", 1)
        star.construct("star", "star.ogg", "starDesc.ogg", 1)
        starHole.construct("starHole", "starHole.ogg", "starHoleDesc.ogg", 0)
        bathroomHallwayDoor.construct("bathroomHallwayDoor", "bathroomHallwayDoor.ogg", "bathroomHallwayDoorDesc.ogg", 0)
        safeRecording.construct("safeRecording", "safeRecording.ogg", "safeRecordingDesc.ogg", 0)
        cellKey.construct("cellKey", "cellKey.ogg", "cellKeyDesc.ogg", 1)
        passCard.construct("passCard", "passCard.ogg", "passCardDesc.ogg", 1)
        upperHallwayDoor.construct("upperHallwayDoor", "upperHallwayDoor.ogg", "upperHallwayDoorDesc.ogg", 0)
        notebook.construct("notebook", "notebook.ogg", "notebookDesc.ogg", 0)
        mainEntrance.construct("mainEntrance", "mainEntrance.ogg", "mainEntranceDesc.ogg", 0)
        masterBedroomDeskKey.construct("masterBedroomDeskKey", "masterBedroomDeskKey.ogg", "masterBedroomDeskKeyDesc.ogg", 1)
        masterBedroomBed.construct("masterBedroomBed", "bed.ogg", "masterBedroomBedDesc.ogg", 0)

        masterBedroomDesk.construct("masterBedroomDesk", "desk.ogg", "masterBedroomDeskDesc.ogg", 0)
        libraryRecording.construct("libraryRecording", "recording.ogg", "libraryRecordingDesc.ogg", 0)
        masterBedroomRecording.construct("masterBedroomRecording", "recording.ogg", "masterBedroomRecordingDesc.ogg", 0)
        masterBathroomStarHole.construct("masterBathroomStarHole", "starHole.ogg", "starHoleDesc.ogg", 0)    
        masterBathroomMirror.construct("masterBathroomMirror", "mirror.ogg", "mirrorDesc.ogg", 0)
        knife.construct("knife", "knife.ogg", "knifeDesc.ogg", 1)
        trappedHallwayDoorKey.construct("trappedHallwayDoorKey", "trappedHallwayDoorKey.ogg", "trappedHallwayDoorKeyDesc.ogg", 1)
        sittingRoomDoor.construct("sittingRoomDoor", "sittingRoomDoor.ogg", "sittingRoomDoorDesc.ogg", 0)
        eleanor.construct("eleanor", "eleanor.ogg", "eleanorDesc.ogg", 0)
        gun.construct("gun", "gun.ogg", "gunDesc.ogg", 1)
        labDoor.construct("labDoor", "labDoor.ogg", "labDoorDesc.ogg", 0)
        ingredients.construct("ingredients", "ingredients.ogg", "ingredientsDesc.ogg", 1)
        mazeDoor.construct("mazeDoor", "mazeDoor.ogg", "mazeDoorDesc.ogg", 0)
        garageDoor.construct("garageDoor", "garageDoor.ogg", "garageDoorDesc.ogg", 0)
        garageKey.construct("garageKey", "garageKey.ogg", "garageKeyDesc.ogg", 1)
        gasoline.construct("gasoline", "gasoline.ogg", "gasolineDesc.ogg", 1)
        trappedHallwayDoor.construct("trappedHallwayDoor", "trappedHallwayDoor.ogg", "trappedHallwayDoorDesc.ogg", 0)
        barnDoor.construct("barnDoor", "barnDoor.ogg", "barnDoorDesc.ogg", 0)
        barnSwitch.construct("barnSwitch", "barnSwitch.ogg", "barnSwitchDesc.ogg", 0)
        eleanor2.construct("eleanor2", "eleanor.ogg", "eleanorDesc4.ogg", 0)

       
       
        #itemUses stores all the possible item use combinations
        #"itemUsed": [ ["usedOn", function], ["usedOn", function] ]
        itemUses = {"player":[["journal", save], ["painting", playerToPainting], ["piano", playerToPiano], ["box", playerToBox], ["bathroomHallwayDoor", playerToBathroomHallwayDoor], ["computer", playerToComputer], ["safe", playerToSafe], ["barnSwitch", playerToBarnSwitch]],
                    "scalpel":[["operatingTable", scalpelToOperatingTable]],
                    "operatingRoomKey":[["operatingRoomDoor", operatingRoomKeyToOperatingRoomDoor]],
                    "broom":[["shelf", broomToShelf]],
                    "star":[["starHole", starToStarHole], ["masterBathroomStarHole", starToMasterBathroomStarHole]],
                    "deskKey":[["desk", deskKeyToDesk]],
                    "hammer":[["mirror", hammerToMirror], ["upperHallwayDoor", hammerToUpperHallwayDoor]],
                    "cellKey":[["bathroomHallwayDoor", cellKeyToBathroomHallwayDoor]],
                    "passCard":[["mainEntrance", passCardToMainEntrance], ["sittingRoomDoor", passCardToSittingRoomDoor], ["mazeDoor", passCardToMazeDoor], ["barnDoor", passCardToBarnDoor]],
                    "masterBedroomDeskKey":[["masterBedroomDesk", masterBedroomDeskKeyToMasterBedroomDesk]],
                    "knife":[["eleanor", knifeToEleanor], ["eleanor2", knifeToEleanor2]],
                    "ingredients":[["eleanor", ingredientsToEleanor]],
                    "garageKey":[["garageDoor", garageKeyToGarageDoor]],
                    "gun":[["garageDoor", gunToGarageDoor]],
                    "trappedHallwayDoorKey":[["trappedHallwayDoor", trappedHallwayDoorKeyToTrappedHallwayDoor]],
                    "gasoline":[["eleanor2", gasolineToEleanor2]]}
        roomDict = {"inventory":inventory,
                    "operatingRoom":operatingRoom,
                    "freezer":freezer,
                    "basementHallway":basementHallway,
                    "pianoRoom":pianoRoom,
                    "elevator":elevator,
                    "study":study,
                    "upperHallway":upperHallway,
                    "bedroom":bedroom,
                    "bathroom":bathroom,
                    "closet":closet,
                    "bathroomHallway":bathroomHallway,
                    "balcony":balcony,
                    "westHallway":westHallway,
                    "lobby":lobby,
                    "library":library,
                    "masterBedroom":masterBedroom,
                    "masterBathroom":masterBathroom,
                    "masterElevator":masterElevator,
                    "eleanorsRoom":eleanorsRoom,
                    "sittingRoom":sittingRoom,
                    "basement":basement,
                    "kitchen":kitchen,
                    "lab":lab,
                    "garage":garage,
                    "trappedHallway":trappedHallway,
                    "outside":outside,
                    "barn":barn,
                    "barnLoft":barnLoft}
        actionList = [["move.ogg", move], ["useItem.ogg", useItem], ["examine.ogg", examine], ["quit.ogg", quit]]
        yesNoList = [["yes.ogg", "yes"], ["no.ogg", "no"]]
        menuList = [["newGame.ogg", newGame], ["loadGame.ogg", loadGame], ["options.ogg", options], ["quit.ogg", quit]]
        saveList = [["slot1.ogg", "save1.txt"], ["slot2.ogg", "save2.txt"], ["slot3.ogg", "save3.txt"], ["slot4.ogg", "save4.txt"], ["slot5.ogg", "save5.txt"]]
    
        SPEED_NORMAL = 45000
        SPEED_FAST = 65000
        voiceSpeed = SPEED_NORMAL
        menu()    
    finally:        
        pygame.quit()
