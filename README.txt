Author: Christopher Herzog
Date: 7/28/2019
Purpose: Determine if the weather is good enough to fly on based on pulled data.

Requirements:
- Serverless Application -> AWS Lambda
- Must be written in Python
- Return data: [Green|Red|Yellow], weather data decoded, wind direction
- Input: Location -> ex. King of Pussia or Area Code or Airport

Data to GET:
- TFR's, if TFR is in effect, displaying warning with TFR.
- Pressure - High/Low, Cold Front/Warm Front.
- Visibility 
- Wind Gradient (usairnet)
- METAR

Process:
- Client types in Airport code in html input box.
- Return data

Links:
https://www.aviationweather.gov/dataserver
https://docs.python-guide.org/scenarios/scrape/