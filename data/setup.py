import requests
from random import random, choice
from string import ascii_letters
from random import randrange
from datetime import datetime, timedelta
from passlib.hash import sha256_crypt


# Denna fil består bara av fulhack.


URL_TO_ENGLISH_WORDS = 'https://raw.githubusercontent.com/dwyl/english-words/master/words.txt'



def random_date(start, end):
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)


if __name__ == '__main__':


    FILE_PATH = 'data/'


    names = [
        'transportwildcat', 'wrapteal', 'listenseagull', 'peerswallow', 'admireowl', 'shrugbuzzard', 'orderoxbird',
        'requestlion', 'operatewildebeest', 'yodelplover', 'hidechamois', 'minehamster', 'scrapegoldfinch',
        'volunteersheldrake', 'entertainsnail', 'severblackbird', 'causekookaburra', 'commenttuna', 'bleachraven',
        'wishptarmigan', 'fearpheasant', 'avowlemur', 'borroweland', 'tossdoves'
    ]

    domain = ['@hotmail.com', '@kth.se', '@gmail.com', '@msn.com']


    words = requests.get(URL_TO_ENGLISH_WORDS).content.decode('utf-8').split()


    with open(FILE_PATH + 'users_data.txt', 'w') as datafile:
        for i, name in enumerate(names):
            username = name

            email = ''
            for _ in range(1, int(random() * 4) + 2):
                email += words[int(random() * (len(words) - 1))]
            email += choice(domain)

            age = int(random() * 100) + 1

            datafile.write('{},{},{}\n'.format(username, email, age))

    with open(FILE_PATH + 'tweets_data.txt', 'w') as datafile:

        d1 = datetime.strptime('2008-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
        d2 = datetime.now()

        posterID = 1
        for i in range(len(names) * 10):

            content = ' '.join(words[int(random() * (len(words) - 1))] for _ in range(1, int(random() * 30) + 5))
            content += choice(['!', '.', '...', '?', ''])
            if len(content) > 144:
                content = content[0:144]

            time_posted = random_date(d1, d2)

            datafile.write('{},{},{}\n'.format(posterID, content, time_posted))

            if random() < 0.08:
                posterID += 1
                if posterID > len(names):
                    break



    with open(FILE_PATH + 'followers_data.txt', 'w') as datafile:

        followers = set()

        for i in range((len(names) ** 2)):

            a, b = int(random() * (len(names) - 1) + 1),  int(random() * (len(names) - 1) + 1)

            if (a, b) in followers or a == b:
                continue
            else:
                followers.add((a, b))
                datafile.write('{},{}\n'.format(a, b))


    with open(FILE_PATH + 'passwords_data.txt', 'w') as datafile:

        for i, name in enumerate(names, start=1):
            password = sha256_crypt.hash(name[0:4])
            datafile.write('{},{}\n'.format(i, password))
