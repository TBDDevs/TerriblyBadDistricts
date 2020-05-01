from census import Census
from us import states

c = Census("e4fcede59883bbb963ce978868f5f2507b572d7f") # this is the key we use to access the API (its connected to my account so dont get me in trouble)

c.acs5.get(("NAME", "B25034_010E"),
            {"for": "state:{}".format(states.MD.fips)})

print(c.acs5.state(('NAME', 'B25034_010E'), states.MD.fips))

