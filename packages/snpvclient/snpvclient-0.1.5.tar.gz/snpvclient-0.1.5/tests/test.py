import snpvclient as sn
import os

snclient = sn.SNPClient('https://sn.example.com')
snclient.login('name@example.com', 'password')

if __name__ == '__main__':

    sn.actions.list_folder(snclient)