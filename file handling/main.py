import filehandling as f


while True:
    print("1.read data \n2.write data\n3.exit data")
    x=int(input("Enter choice :"))

    if x==2:
        
        name=input("Enter a Name :")
        age=input("Enter a Age :")
        number=input("Enter a phone number :")
        email=input("Enter a Email :")

        f.save_data(name,age,number,email)
        print("Data saved succesfully")
    elif x==1:
        data=f.read_data()
        print(data)
    elif x==3:
        break
    else:
        print("Invalid input !!")














