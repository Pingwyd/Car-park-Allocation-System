from random import choice
import sqlite3
import qrcode
import datetime
from pyzbar.pyzbar import decode
import cv2
import uuid


def databaseLogSetup():
    conn = sqlite3.connect("parkingdblogs.db")
    cursor = conn.cursor()

    conn.execute(''' CREATE TABLE IF NOT EXISTS parklogs(
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 entryID TEXT NOT NULL UNIQUE,
                 Name TEXT NOT NULL,
                 PhoneNumber TEXT NOT NULL,
                 PlateNumber TEXT NOT NULL,
                 SlotID INTEGER,
                 timeIN TEXT,
                 timeOut TEXT)
                 ''')
    
    conn.commit
    conn.close

def databaseSetup():
    conn = sqlite3.connect("parkingdb.db")
    cursor = conn.cursor()

    conn.execute('''CREATE TABLE IF NOT EXISTS slots(
                 id INTEGER PRIMARY KEY AUTOINCREMENT,        
                 isFREE BOOLEAN DEFAULT TRUE
                 )
''')
    
    conn.execute(''' CREATE TABLE IF NOT EXISTS park(
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 Name TEXT NOT NULL,
                 PhoneNumber TEXT NOT NULL,
                 PlateNumber TEXT NOT NULL,
                 SlotID INTEGER,
                 FOREIGN KEY (SlotID) REFERENCES SLOTS(id)
                 )
                 
 ''')    
    
    conn.commit
    conn.close

def logs(name, PhoneNumber, PlateNumber, freeSlotID):

    conn = sqlite3.connect("parkingdblogs.db")
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM parklogs WHERE Name= ? AND timeOut IS NULL",(name,))
        existingEntry = cursor.fetchone()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    

        if existingEntry:
            cursor.execute("UPDATE parklogs SET timeOUT =? WHERE id = ?", (now,existingEntry[0]))
            print(f"{name} Logged out... Slot is now free....")
            return "SignOut", existingEntry[5]

        else:   
            entry_id = str(uuid.uuid4())
            cursor.execute('''INSERT INTO parklogs (entryID, Name, PhoneNumber, PlateNumber, timeIN, SlotID) VALUES(?,?,?,?,?,?)''', (entry_id, name, PhoneNumber, PlateNumber,
now,freeSlotID))
        print(f"{name} Logged in... Slot {freeSlotID} is now occupied ...")
        return "SignIN",freeSlotID

    except sqlite3.Error as e:
        print(f"Error: {e}")
        
    finally:
        conn.commit()
        conn.close()    

def freeSpaces(name, PhoneNumber, PlateNumber):
    conn = sqlite3.connect("parkingdb.db")
    cursor = conn.cursor()
    
    # numParkingSlots()
    #To check for free spaces in the parking slots
    cursor.execute("SELECT id FROM slots WHERE isFree == 1 ")
    freeSlots = cursor.fetchall()
    
    if not freeSlots:
        print("No Available Slots")
        return None
    
    freeSlotID = choice(freeSlots)[0]

    cursor.execute("INSERT INTO park (Name, PhoneNumber, PlateNumber, SlotID) VALUES (?, ?, ?, ?)",
                   (name, PhoneNumber, PlateNumber, freeSlotID))

    cursor.execute("UPDATE slots SET isFREE = 0 WHERE id =?",(freeSlotID,))
    
    conn.commit()
    conn.close()

    return freeSlotID

def emptySlot(slotID):
    conn = sqlite3.connect("parkingdb.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE slots SET isFREE = 1 WHERE id = ?", (slotID,))
    conn.commit()
    conn.close()

def scanning(): 
    qr_data = read_qr_from_camera()
    return qr_data

def read_qr_from_camera():

    cap = cv2.VideoCapture(0)
    print("Showing camera... Scan your QR code.")
    while True:
        success, frame = cap.read()
        for code in decode(frame):
            qr_data = code.data.decode('utf-8').split(',')
            print(f"Scanned QR: {qr_data}")
            cap.release()
            cv2.destroyAllWindows()
            return qr_data
        cv2.imshow('QR Scanner', frame)
        if cv2.waitKey(1) == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    return None

def view_logs():
        
        conn = sqlite3.connect("parkingdblogs.db")
        cursor = conn.cursor()
        cursor.execute("SELECT Name,PhoneNumber, PlateNumber, SlotID, timeIN, timeOUT FROM parklogs")
        rows = cursor.fetchall()
        conn.close()

        print("=== Parking Logs ===")
        print("  Name \t| PhoneNumber | PlateNumber | SlotNumber |\tTimeIn\t|\t TimeOut")
        for row in rows:
            print(row)

def run():
    databaseLogSetup()
    databaseSetup()
    data = scanning()

    if data:
        name, PhoneNumber, PlateNumber = data
        slotID = freeSpaces(name, PhoneNumber, PlateNumber)

    if slotID == None:
        return
    result = logs(name, PhoneNumber,PlateNumber,slotID)

    if result:
        action, slotUsed = result
        if action =="SignOut":
            emptySlot(slotUsed)

def main():
    print("Welcome")
    while True:

        print("\nPlease choose an option:")
        print("1. Get/Release a Parking Slot")
        print("2. View Logs")
        print("3. Exit")

        answer = input("> ").strip()

        if answer == "1":
            run()    
        elif answer == "2":
            view_logs()
        elif answer =="3":
            print("Goodbye!!")
            break
        else:
            print("Enter a valid option (1,2,3).....")

if __name__ =="__main__":
    main()
    

