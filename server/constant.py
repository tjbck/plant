from enum import Enum


class PLANT_EVENTS(str, Enum):
    HOT_TEMP = "The temperature exceeds the optimal range for the plant."
    COLD_TEMP = "The temperature falls below the optimal range for the plant."
    LOW_HUMIDITY = "Humidity levels are too low for the plant."
    HIGH_HUMIDITY = "Humidity levels are too high for the plant."
    OVERWATERING = "The plant is receiving too much water."
    UNDERWATERING = "The plant is not receiving enough water."
    LIGHT_INTENSITY_LOW = "The plant is not receiving sufficient light."
    LIGHT_INTENSITY_HIGH = "The plant is receiving too much direct light."
