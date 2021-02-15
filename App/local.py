# Times are represented internally as the number of minutes since midnight. 480 and 1200 are representative
# of 8:00 am and 8:00 pm respectively.
SHIFT_START_TIME = 480
SHIFT_END_TIME = 1200
global_time = 0

# The overall status of the day's scheduled deliveries.
global_status_msg = ""

# Zones are used to group nearby zip codes and get a general idea of their location relative to the HUB.
# This information can be used to more efficiently load trucks and avoid having packages destined for
# opposite sides of the city on the same truck at the same time.
zones = {}
zones.update(dict.fromkeys(["84104", "84103", "84111", "84102"], "North"))
zones.update(dict.fromkeys(["84124", "84117", "84107", "84121"], "South"))
zones.update(dict.fromkeys(["84115", "84106", "84105"], "East"))
zones.update(dict.fromkeys(["84119", "84129", "84123", "84118"], "West"))
