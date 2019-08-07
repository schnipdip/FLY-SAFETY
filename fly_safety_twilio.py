from flask import Flask, request, render_template, url_for
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from bs4 import BeautifulSoup
import urllib2
import emoji
import os

# DO NOT USE FOR FLIGHT
# FOR SIMULATOR AND EDUCATIONAL PURPOSES ONLY

# 8/7/2019, Update: Added a donation feature. Also, simplified some code.

app = Flask(__name__)

def data_gather(usr_input):
    url = 'https://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&stationString=' + usr_input + '&hoursBeforeNow=1'
    data = urllib2.urlopen(url)
    read_data = data.read()
    data.close()
    soup = BeautifulSoup(read_data, features='lxml')

    return soup

def data_parse(soup):
    # <raw_text>
    # <dewpoint_c>
    # <wind_dir_degrees>
    # <wind_speed_kt>
    # <visibility_statute_mi>
    # <sea_level_pressure_mb>
    rawText = soup.find('raw_text').string
    dewPointC = soup.find('dewpoint_c').string
    windDir = soup.find('wind_dir_degrees').string
    windSpeedKt = soup.find('wind_speed_kt').string
    visMi = soup.find('visibility_statute_mi').string
    pressureMb = soup.find('sea_level_pressure_mb').string
    tempC = soup.find('temp_c').string
    elevation = soup.find('elevation_m').string

    return rawText, dewPointC, windDir, windSpeedKt, visMi, pressureMb, tempC, elevation

def data_score(rawText, dewPointC, windDir, windSpeedKt, visMi, pressureMb, tempC, elevation):
    print rawText
    print "dew point: " + dewPointC
    print "wind direction: " + windDir
    print "wind speed: " + windSpeedKt
    print "visibility: " + visMi
    print "pressure: " + pressureMb
    print "Temp C: " + tempC
    print "elevation: " + elevation
    #calculate density altitude with temp + pressure
    # Density Altitude = pressure + [120*(OAT-ISA Temp)

    # calculate ISA Temp first
    isaT = ((2 * float(elevation)) - 15)

    # calculate Density Altitude - converted to feet
    DA = int(round((3.28084 *((float(pressureMb) + (120*(float(tempC)-isaT)))))))
    print "Density Altitude (ft): ", DA

    # calulate Relative Humidity
    # DewPointC/TempC
    RH = round(100 * (float(dewPointC)/float(tempC)))
    print "Relative Humidity (C): ", RH

    
    # Start SCORING DATA 1 - 10
    score = 0
    
    # if the temperature falls below the RH, high chance of storm
    tempF = (float(tempC) * 1.8) + 32
    
    if float(tempF) < RH:
        score += 7
    elif float(tempF) > RH:
        score += 2

    # wind speed
    if int(windSpeedKt) >= 11:
        score += 10
    elif int(windSpeedKt) < 11 and int(windSpeedKt) >= 7:
        score += 5
    else:
        score += 1 


    # Visibility
    if float(visMi) == 3:
        score += 3
    elif float(visMi) == 2:
        score += 4
    elif float(visMi) == 1:
        score += 5
    elif float(visMi) > 3:
        score += 1

    # Pressure
    if float(pressureMb) >= 1009 and float(pressureMb) <= 1015:
        score += 3
    elif float(pressureMb)> 1015:
        score += 1

    # A low score can be a total of 5
    # A high score can be a total of 25

    # An acceptable score for safe flying range: 5 -> 12
    # A cautious score can be flying range: 13 - 17
    # A no fly will be 18+

    if score >= 5 and score <= 12:
        fly_answer = (emoji.emojize(':green_heart:'))
        return fly_answer
    elif score >= 13 and score <= 17:
        fly_answer = (emoji.emojize(':yellow_heart:'))
        return fly_answer
    elif score >= 18:
        fly_answer = (emoji.emojize(':red_heart:'))
        return fly_answer

def metar_create(rawText, dewPointC, windDir, windSpeedKt, visMi, pressureMb, tempC, elevation):
    # calculate ISA Temp first
    isaT = ((2 * float(elevation)) - 15)
    
    # calculate Density Altitude - converted to feet
    DA = int(round((3.28084 *((float(pressureMb) + (120*(float(tempC)-isaT)))))))

    # calulate Relative Humidity
    # DewPointC/TempC
    RH = round(100 * (float(dewPointC)/float(tempC)))

    # calculate Temp F
    tempF = (float(tempC) * 1.8) + 32


    metar_string = (rawText, "\n\n",
                    "Dew Point(c): ",dewPointC, "\n",
                    "Relative Humidity: ", RH, "\n",
                    "Temperature(F): ", tempF, "\n",
                    "Wind Speed(kt): ", windSpeedKt, "\n",
                    "Wind Direction: ", windDir, "\n",
                    "Visibility(mi): ", visMi, "\n",
                    "Pressure(mb): ", pressureMb, "\n",
                    "Density Altitude: ", DA, "\n")

    return metar_string
    

@app.route("/sms", methods=['GET', 'POST'])
def twilio_receive():
    #Replies to incoming messages
    """Respond to incoming messages with a friendly SMS."""

    # get the message the user sent
    usr_input = request.values.get('Body',None)

    # Start our response
    resp = MessagingResponse()

    usr_input = usr_input.lower()
    
    # IF METAR IS RECEIVED
    if "metar" in usr_input:
        # parse sring, pull ICAO code
        icao_code = usr_input.replace("metar", '').strip()     
        
        soup = data_gather(icao_code)
        rawText, dewPointC, windDir, windSpeedKt, visMi, pressureMb, tempC, elevation = data_parse(soup)
        metar_string = metar_create(rawText, dewPointC, windDir, windSpeedKt, visMi, pressureMb, tempC, elevation)
        metar_string = ' '.join(map(str, (metar_string)))

        # Add a message - can send variables of strings.
        #metar_string = str(metar_string)
        resp.message(metar_string)

        return str(resp)
    elif "donate" == usr_input:
        donate_message = ("Thank you for wanting to donate to Fly Safety (Paypal)\n\n",
                          "Send a text message to 729725\n\n",
                          "example: send 10 to 17175038265\n\n",
                          "Thank you for your donation! It will help keep this app running")
        donate_message = ' '.join(map(str,(donate_message))) 
        resp.message(donate_message)

        return str(resp)
    elif "help me" == usr_input:
        help_message = ("To get METAR data from an ICAO code:\n",
                        "  exmaple: metar kjfk\n\n",
                        "To get flight safety quick check\n",
                        "  example: kjfk\n\n",
                        "To donate to Flight Safety\n",
                        "  example: donate")
        help_message = ' '.join(map(str,(help_message)))
        resp.message(help_message)

        return str(resp)
    else: 
        soup = data_gather(usr_input)
        rawText, dewPointC, windDir, windSpeedKt, visMi, pressureMb, tempC, elevation = data_parse(soup)
        fly_answer = data_score(rawText, dewPointC, windDir, windSpeedKt, visMi, pressureMb, tempC, elevation)

        # Add a message - can send variables of strings.
        resp.message(fly_answer)

        return str(resp)
    
if __name__ == '__main__':
    app.run(debug=True)
    
