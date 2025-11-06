import qrcode

def generate_qr(name, phone, plate):
    
    data = f"{name},{phone},{plate}"
    qr = qrcode.make(str(data))
    qr.save(f"{name}.png")
    print(f"QR Code saved as {name}.png")
    return qr

def main():
    
    # employeeID = input("Enter your employeeID: ")
    name = input("Enter your name: ")
    phone = input("Enter your phone Number: ")
    plate = input("Enter your plate number: ")

    qrCode  = generate_qr(name,phone,plate)

if __name__ == "__main__":
    main()
