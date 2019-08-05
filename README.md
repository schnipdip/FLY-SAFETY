# FLY-SAFETY
Checks METAR data and gives an estimated return of 'weather' it's safe to fly. 

# Information:
Mostly for major airports that report the following METAR Data:
- <raw_text>
- <dewpoint_c>
- <wind_dir_degrees>
- <wind_speed_kt>
- <visibility_statute_mi>
- <sea_level_pressure_mb>
# Requirements: 
- localtunnel.exe 
  `lt-win.exe --p 5000` (exposes the application to the Internet)
- Twilio:
  - pip install twilio
  - Twilio phone number
- pip install emoji
- pip install flask
- pip install bs4

# Example:
Input ICAO Airport Code

Text Message: `kphl`
