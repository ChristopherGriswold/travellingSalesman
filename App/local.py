# Zones are used to group nearby zip codes and get a general idea of their location relative to the HUB.
# This information can be used to more efficiently load trucks and avoid having packages destined for
# opposite sides of the city on the same truck at the same time.
zones = {}
zones.update(dict.fromkeys(["84104", "84103", "84111", "84102"], "North"))
zones.update(dict.fromkeys(["84124", "84117", "84107", "84121"], "South"))
zones.update(dict.fromkeys(["84115", "84106", "84105"], "East"))
zones.update(dict.fromkeys(["84119", "84129", "84123", "84118"], "West"))

# Times are represented internally as the number of minutes since midnight. 480 is representative of 08:00.
SHIFT_START_TIME = 480
