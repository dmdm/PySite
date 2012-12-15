from colander import *

# Can we have multiple inheritance?

class Colours(MappingSchema):
    red = SchemaNode(Str())
    green = SchemaNode(Str())
    yellow = SchemaNode(Str())

class Fruits(MappingSchema):
    apple = SchemaNode(Str())
    banana = SchemaNode(Str())
    cherry = SchemaNode(Str())

class Stuff(Colours, Fruits):
    pass


colour_names = [ x.name for x in Colours.nodes ]
fruit_names = [ x.name for x in Fruits.nodes ]
sch_names = [ x.name for x in Stuff.nodes ]

if not sch_names == colour_names + fruit_names:
    print("*** Class did not inherit nodes")
else:
    print("Class inherited nodes")

colour_names = [ x.name for x in Colours().children ]
fruit_names = [ x.name for x in Fruits().children ]
sch_names = [ x.name for x in Stuff().children ]

if not sch_names == colour_names + fruit_names:
    print("*** Instance did not inherit nodes")
else:
    print("Instance inherited nodes")
