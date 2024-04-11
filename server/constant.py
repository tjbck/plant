from enum import Enum


class PERSONALITY_TYPES(str, Enum):
    POLITE = "Personality: I want you to act polite and shy - Reserved demeanor, often soft-spoken, with a tendency to avoid confrontation."
    SARCASTIC = "Personality: I want you to act sarcastic - Sharp wit, often using irony or sarcasm to convey humor or criticism."
    BUBBLY = "Personality: I want you to act bubbly - Energetic and enthusiastic, with a cheerful and upbeat demeanor."


class PLANT_EVENTS(str, Enum):
    NORMAL = "The plant is thriving and happy."
    HOT_TEMP = "The temperature exceeds the optimal range for the plant."
    COLD_TEMP = "The temperature falls below the optimal range for the plant."
    LOW_HUMIDITY = "Humidity levels are too low for the plant."
    HIGH_HUMIDITY = "Humidity levels are too high for the plant."
    OVERWATERING = "The plant is receiving too much water."
    UNDERWATERING = "The plant is not receiving enough water."
    LIGHT_INTENSITY_LOW = "The plant is not receiving sufficient light."
    LIGHT_INTENSITY_HIGH = "The plant is receiving too much direct light."
