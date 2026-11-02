def save_data(name, age, number, email):
    file = open("data.txt", "a")

    file.write(name + "," + age + "," + number + "," + email + "\n")

    file.close()


def read_data():
    file = open("data.txt", "r")

    data = file.read()

    file.close()

    return data