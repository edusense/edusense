# Define Labels
labels = {
    'dog-bark': 0,
    'drill': 1,
    'hazard-alarm': 2,
    'phone-ring': 3,
    'speech': 4,
    'vacuum': 5,
    'baby-cry': 6,
    'chopping': 7,
    'cough': 8,
    'door': 9,
    'water-running': 10,
    'knock': 11,
    'microwave': 12,
    'shaver': 13,
    'toothbrush': 14,
    'blender': 15,
    'dishwasher': 16,
    'doorbell': 17,
    'flush': 18,
    'hair-dryer': 19,
    'laugh': 20,
    'snore': 21,
    'typing': 22,
    'hammer': 23,
    'car-horn': 24,
    'engine': 25,
    'saw': 26,
    'cat-meow': 27,
    'alarm-clock': 28,
    'cooking': 29,
    'dribble': 30,
    'whistle': 31,
    'buzzer': 32
}

dummy = ['snore', 'saw']
bathroom = ['water-running', 'flush', 'toothbrush', 'shaver', 'hair-dryer']
kitchen = ['water-running', 'chopping', 'cooking', 'microwave',
           'blender', 'hazard-alarm', 'dishwasher', 'speech']
bedroom = ['alarm-clock', 'snore', 'cough', 'baby-cry', 'speech']
office = ['knock', 'typing', 'phone-ring', 'door', 'cough', 'speech']
entrance = ['knock', 'door', 'doorbell', 'speech', 'laugh']
workshop = ['hammer', 'saw', 'drill', 'vacuum', 'hazard-alarm', 'speech']
outdoor = ['dog-bark', 'cat-meow', 'engine',
           'car-horn', 'speech', 'hazard-alarm']
sports = ['dribble', 'whistle', 'buzzer']
everything = ['dog-bark', 'drill', 'hazard-alarm', 'phone-ring', 'speech', 'vacuum', 'baby-cry', 'chopping', 'cough', 'door', 'water-running', 'knock', 'microwave', 'shaver', 'toothbrush',
              'blender', 'dishwasher', 'doorbell', 'flush', 'hair-dryer', 'laugh', 'snore', 'typing', 'hammer', 'car-horn', 'engine', 'saw', 'cat-meow', 'alarm-clock', 'cooking', 'dribble', 'whistle', 'buzzer']
context_mapping = {'kitchen': kitchen, 'bathroom': bathroom, 'bedroom': bedroom, 'office': office, 'entrance': entrance,
                   'workshop': workshop, 'outdoor': outdoor, 'everything': everything, 'dummy': dummy, 'sports': sports}
