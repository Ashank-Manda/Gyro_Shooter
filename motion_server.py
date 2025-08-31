import socket
import json
import threading

playerRotation = {"p1": 0, "p2": 0}
playerStart = {"p1": 0, "p2": 0}
playerConnected = {"p1": False, "p2": False}
shootButtonPressedDict = {'p1': False, 'p2': False}
prevShootButtonStates = {'p1': False, 'p2': False}
specialAttackButtonPressedDict = {'p1': False, 'p2': False}
prevSpecialAttackButtonStates = {'p1': False, 'p2': False}   

def getInfoFromClient(clientSocket):
    #Lines 15 to 25 are from ChatGPT, although I understand how the code works
    buffer = ""
    try:
        while True:
            data = clientSocket.recv(1024)
            if not data:
                break
            buffer += data.decode('utf-8')
            while True:
                try:
                    motionData, index = json.JSONDecoder().raw_decode(buffer)
                    buffer = buffer[index:].lstrip()
                    playerID = motionData.get("id", "")
                    #Function to extract data from Motion Dictionary
                    gettingInfoFromData(motionData)
                #Lines 30 to 34
                except json.JSONDecodeError:
                    break
    except Exception as e:
        print(f"[ERROR] Motion server error: {e}")
    finally:
        if playerID in playerConnected:
            playerConnected[playerID] = False
        clientSocket.close()
        print("[INFO] Client disconnected.")

def gettingInfoFromData(motionData):
    #Sending Data of Player ID and Phone Rotation
    playerID = motionData.get("id", "")
    rotation = motionData.get("rotation", 0)
    startRotation = motionData.get("startRotation", 0)

    #Sending Data of Shooting Buttons
    shootButtonPressed = motionData.get('shootButtonPressed', False)
    specialAttackButtonPressed = motionData.get('specialAttackPressed', False)

    if playerID in playerRotation:
        playerRotation[playerID] = rotation
        playerConnected[playerID] = True
        playerStart[playerID] = startRotation

        #Shooting Button Press Logic
        if (shootButtonPressed and 
            not prevShootButtonStates[playerID]):
            shootButtonPressedDict[playerID] = True
        else:
            shootButtonPressedDict[playerID] = False
        prevShootButtonStates[playerID] = shootButtonPressed

        if (specialAttackButtonPressed and 
            not prevSpecialAttackButtonStates[playerID]):
            specialAttackButtonPressedDict[playerID] = True
        else:
            specialAttackButtonPressedDict[playerID] = False
        prevSpecialAttackButtonStates[playerID] = specialAttackButtonPressed
    
    #Lines 56 to 62 and line 66 are from ChatGPT   
    else:
        print(f"[WARN] Unknown player ID received: {playerID}") 

# TCP Server to Receive Data from Phone (Entire Function is from ChatGPT)
def startMotionServer():
    ipAddress = '0.0.0.0'
    port = 12345

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((ipAddress, port))
    serverSocket.listen(2)  # Expecting up to 2 clients
    print(f"[INFO] Server listening on {ipAddress}:{port}...")

    def acceptClients():
        while True:
            clientSocket, clientAddress = serverSocket.accept()
            print(f"[INFO] Connected to {clientAddress}")
            threading.Thread(target=getInfoFromClient, 
                             args=(clientSocket,), daemon=True).start()

    threading.Thread(target=acceptClients, daemon=True).start()
